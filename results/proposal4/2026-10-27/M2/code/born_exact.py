"""Exact rational Born-stability (positive-definiteness) tools for 6x6 elastic tensors.

All verdict functions take Fraction matrices and use no floating point.
"""
from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from math import isqrt, lcm
from typing import Optional

Matrix = list[list[Fraction]]


def frac_from_float(x: float) -> Fraction:
    """Exact rational of the shortest round-trip decimal repr of x (the 'printed decimal')."""
    return Fraction(Decimal(repr(float(x))))


def printed_places(x: float) -> int:
    """Number of printed decimal places of the shortest repr (>= 0)."""
    exp = Decimal(repr(float(x))).as_tuple().exponent
    assert isinstance(exp, int)
    return max(0, -exp)


def to_matrix(rows: list[list[float]]) -> Matrix:
    return [[frac_from_float(v) for v in r] for r in rows]


def half_widths(rows: list[list[float]]) -> Matrix:
    """h_ij = 1/2 * 10^(-p_ij), p_ij = printed decimal places of entry (i,j)."""
    return [[Fraction(1, 2 * 10 ** printed_places(v)) for v in r] for r in rows]


def is_symmetric(m: Matrix) -> bool:
    n = len(m)
    return all(m[i][j] == m[j][i] for i in range(n) for j in range(i))


def symmetrize(m: Matrix) -> Matrix:
    n = len(m)
    return [[(m[i][j] + m[j][i]) / 2 for j in range(n)] for i in range(n)]


def quad_form(m: Matrix, x: list[Fraction]) -> Fraction:
    n = len(m)
    return sum((x[i] * m[i][j] * x[j] for i in range(n) for j in range(n)), Fraction(0))


def ldl_verdict(s: Matrix) -> tuple[bool, int, Fraction, Optional[list[Fraction]]]:
    """LDL^T without pivoting. Returns (is_pd, k, d_k, witness).

    If PD: (True, n, smallest pivot, None).
    Else: k = first index with pivot <= 0 (0-based), d_k that pivot, witness x with x^T S x = d_k.
    """
    n = len(s)
    L = [[Fraction(0)] * n for _ in range(n)]
    d = [Fraction(0)] * n
    for j in range(n):
        dj = s[j][j] - sum((L[j][k] ** 2 * d[k] for k in range(j)), Fraction(0))
        d[j] = dj
        if dj <= 0:
            x = [Fraction(0)] * n
            x[j] = Fraction(1)
            for i in range(j - 1, -1, -1):
                x[i] = -sum((L[t][i] * x[t] for t in range(i + 1, j + 1)), Fraction(0))
            return False, j, dj, x
        L[j][j] = Fraction(1)
        for i in range(j + 1, n):
            L[i][j] = (s[i][j] - sum((L[i][k] * L[j][k] * d[k] for k in range(j)), Fraction(0))) / dj
    return True, n, min(d), None


def is_pd(s: Matrix) -> bool:
    return ldl_verdict(s)[0]


def shifted(s: Matrix, t: Fraction) -> Matrix:
    n = len(s)
    return [[s[i][j] - (t if i == j else 0) for j in range(n)] for i in range(n)]


def bareiss_minors(s: Matrix) -> list[int]:
    """Independent implementation: signs-bearing leading principal minors via integer
    fraction-free Bareiss elimination on D*S (D = common denominator > 0).
    Returns the list of leading-minor values of D*S (each = D^k * true minor, same sign)."""
    n = len(s)
    D = 1
    for r in s:
        for v in r:
            D = lcm(D, v.denominator)
    a = [[int(v * D) for v in r] for r in s]
    minors: list[int] = []
    prev = 1
    for k in range(n):
        piv = a[k][k]
        minors.append(piv)
        if piv == 0:
            # remaining minors not obtainable by plain Bareiss; stop (verdict already non-PD)
            return minors
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                a[i][j] = (a[i][j] * piv - a[i][k] * a[k][j]) // prev
        prev = piv
    return minors


def minors_pd(s: Matrix) -> bool:
    """Sylvester via the independent Bareiss implementation."""
    m = bareiss_minors(s)
    return len(m) == len(s) and all(v > 0 for v in m)


def sqrt_upper(q: Fraction, scale: int = 10**6) -> Fraction:
    """Rational upper bound of sqrt(q), q >= 0."""
    return Fraction(isqrt(int(q * scale * scale)) + 1, scale)


def frob_upper_of_halfwidths(h: Matrix) -> Fraction:
    return sqrt_upper(sum((v * v for r in h for v in r), Fraction(0)))


def frob_upper(m: Matrix) -> Fraction:
    return sqrt_upper(sum((v * v for r in m for v in r), Fraction(0)))


def interval_verdict(s: Matrix, hs: Matrix, nominal: tuple[bool, int, Fraction, Optional[list[Fraction]]],
                     extra_witnesses: Optional[list[list[Fraction]]] = None) -> str:
    """Rounding-robust classification of the symmetric part S with entrywise half-widths hs.

    ROBUST_PD: S - b I is PD for b >= Frobenius norm of the maximal perturbation, hence
               every symmetric E with |E_ij| <= hs_ij keeps S+E PD.
    ROBUST_NOT_PD: some rational x has x^T S x + sum |x_i||x_j| hs_ij < 0, hence x^T(S+E)x < 0
                   for every admissible E.
    UNDECIDED_BY_BOUND otherwise (the bounds are sufficient, not necessary).
    """
    n = len(s)
    b = frob_upper_of_halfwidths(hs)
    if is_pd(shifted(s, b)):
        return "ROBUST_PD"
    wits = [] if extra_witnesses is None else list(extra_witnesses)
    if nominal[3] is not None:
        wits.append(nominal[3])
    for x in wits:
        slack = sum((abs(x[i]) * abs(x[j]) * hs[i][j] for i in range(n) for j in range(n)), Fraction(0))
        if quad_form(s, x) + slack < 0:
            return "ROBUST_NOT_PD"
    return "UNDECIDED_BY_BOUND"


def linear_orthorhombic_pass(s: Matrix) -> bool:
    """Eq. 19 of Mouhat-Coudert 2014 (Wu et al. 2007): necessary but not sufficient."""
    ok = all(s[i][i] > 0 for i in range(6))
    ok = ok and all(s[i][i] + s[j][j] - 2 * s[i][j] > 0 for i in range(3) for j in range(i + 1, 3))
    ok = ok and (s[0][0] + s[1][1] + s[2][2] + 2 * (s[0][1] + s[0][2] + s[1][2]) > 0)
    return ok


# ---- Mouhat-Coudert 2014 class-specific conditions (Voigt order: 1..6 = xx,yy,zz,yz,xz,xy) ----

def laue_class(spg: int) -> str:
    if 1 <= spg <= 2:
        return "triclinic"
    if 3 <= spg <= 15:
        return "monoclinic"
    if 16 <= spg <= 74:
        return "orthorhombic"
    if 75 <= spg <= 88:
        return "tetragonal_II"
    if 89 <= spg <= 142:
        return "tetragonal_I"
    if 143 <= spg <= 148:
        return "trigonal_II"
    if 149 <= spg <= 167:
        return "trigonal_I"
    if 168 <= spg <= 194:
        return "hexagonal"
    if 195 <= spg <= 230:
        return "cubic"
    return "unknown"


def born_class_verdict(c: Matrix, cls: str) -> Optional[bool]:
    """Closed-form necessary-and-sufficient conditions for the idealised stiffness form of the Laue
    class, evaluated on the stored entries (c in Voigt order). None where no closed form is used
    (triclinic/monoclinic: generic minors, identical to the full PD test)."""
    C = lambda i, j: c[i - 1][j - 1]  # noqa: E731
    if cls == "cubic":
        return C(1, 1) - C(1, 2) > 0 and C(1, 1) + 2 * C(1, 2) > 0 and C(4, 4) > 0
    base_hex = C(1, 1) > abs(C(1, 2)) and 2 * C(1, 3) ** 2 < C(3, 3) * (C(1, 1) + C(1, 2)) and C(4, 4) > 0
    if cls == "hexagonal":
        return base_hex
    if cls == "tetragonal_I":
        return base_hex and C(6, 6) > 0
    if cls == "tetragonal_II":
        return base_hex and 2 * C(1, 6) ** 2 < C(6, 6) * (C(1, 1) - C(1, 2))
    if cls == "trigonal_I":
        return (C(1, 1) > abs(C(1, 2)) and C(4, 4) > 0
                and C(1, 3) ** 2 < Fraction(1, 2) * C(3, 3) * (C(1, 1) + C(1, 2))
                and C(1, 4) ** 2 < Fraction(1, 2) * C(4, 4) * (C(1, 1) - C(1, 2)))
    if cls == "trigonal_II":
        return (C(1, 1) > abs(C(1, 2)) and C(4, 4) > 0
                and C(1, 3) ** 2 < Fraction(1, 2) * C(3, 3) * (C(1, 1) + C(1, 2))
                and C(1, 4) ** 2 + C(1, 5) ** 2 < Fraction(1, 2) * C(4, 4) * (C(1, 1) - C(1, 2)))
    if cls == "orthorhombic":
        return (C(1, 1) > 0 and C(1, 1) * C(2, 2) > C(1, 2) ** 2
                and C(1, 1) * C(2, 2) * C(3, 3) + 2 * C(1, 2) * C(1, 3) * C(2, 3)
                - C(1, 1) * C(2, 3) ** 2 - C(2, 2) * C(1, 3) ** 2 - C(3, 3) * C(1, 2) ** 2 > 0
                and C(4, 4) > 0 and C(5, 5) > 0 and C(6, 6) > 0)
    return None


VASP_TO_VOIGT = [0, 1, 2, 4, 5, 3]  # VASP order xx,yy,zz,xy,yz,zx -> Voigt xx,yy,zz,yz,xz,xy


def to_voigt(m: Matrix) -> Matrix:
    return [[m[VASP_TO_VOIGT[i]][VASP_TO_VOIGT[j]] for j in range(6)] for i in range(6)]
