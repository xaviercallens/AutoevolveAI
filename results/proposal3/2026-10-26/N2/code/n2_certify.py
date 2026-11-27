"""N2: rigorous ball-arithmetic (Arb, python-flint 0.6.0) certificate that the triangular lattice is not a local minimum
of the harmonic zero-point energy E_zp, for exponentially decaying completely monotone pair potentials
(Yukawa exp(-kappa r)/r, Gaussian exp(-pi a r^2)), along the symmetric shear P_t = [[1, t], [t, 1 + t^2]] (B2 setting).

usage: python -I n2_certify.py POT PARAM N T0 QMAX OUT.json
  POT   yukawa | gauss          PARAM rational string (kappa or a)
  N     initial Duffy grid N x N per triangle; cells bisected adaptively (N2_REFINE_TOL, N2_MAX_DEPTH)
  T0    half-width of the t window (rational string)
  QMAX  exact lattice sum over n = (m, l) != 0 with m^2 + m l + l^2 <= QMAX; the rest is a rigorous tail ball

What is new against B2 (b2_certify.py): the comparison matrix depends on t.
  E(t) = (1/2) int tr D_t^{1/2},   X_t = X + t Y,  X = D_0^{1/2},  X Y + Y X = D_0' (Sylvester; Y = d/dt D_t^{1/2} at 0).
  f_kappa(t) = tr X_t + tr(X_t^{-1} D_t) >= 2 tr D_t^{1/2}   whenever X_t > 0  (Lean two_trace_le_of_inverse),
  with equality at t = 0.  U2(t) = (1/4) int f_kappa(t) dkappa >= E(t),  U2(0) = E(0),  U2''(0) = E''(0) exactly.
  f'' = 2 tr(X^-1 Y X^-1 Y X^-1 D) - 2 tr(X^-1 Y X^-1 D') + tr(X^-1 D'')   (all at t, X = X_t).
  Window, per kappa: f(t) + f(-t) - 2 f(0) = int_0^t (t - u)(f''(u) + f''(-u)) du <= t^2 sup_{|u| <= T0} f''(u).
  Duffy scaling (B2): D_t = s^2 B_t, D_t' = s^2 B1_t, D_t'' = s^2 B2_t, X = s Q, Q = B_0^{1/2}, Y = s Yt with
  Q Yt + Yt Q = B1_0;  f'' = s phi,  phi = 2 tr(Qi Yt Qi Yt Qi B) - 2 tr(Qi Yt Qi B1) + tr(Qi B2), Qi = (Q + u Yt)^-1.
  integrand of M := (1/4) int f''  is  s^2 phi / 8  on (s, t') with Jacobian s/2 already included.
  So for 0 < t <= T0:  U2(t) + U2(-t) - 2 U2(0) <= t^2 M_hi.  Certified iff M_hi < 0 and the positivity checks pass.
Positivity checks on every cell, for every |u| <= T0: det B_u > 0, tr B_u > 0 (strained lattice dynamically stable),
det(Q + u Yt) > 0, tr(Q + u Yt) > 0 (X_t positive definite).
Every number is an arb ball (outward rounded); NOT kernel-checked (Tier C-ball).
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
from fractions import Fraction

sys.path.insert(0, "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/.scratchpad/b2_pylib")
import flint  # noqa: E402
import sympy as sp  # noqa: E402
from flint import arb, arb_mat, ctx  # noqa: E402

ctx.prec = 80
PI = arb.pi()
SQ3 = arb(3).sqrt()
C2 = 2 / SQ3
C = C2.sqrt()
HALF = arb(1) / 2
RHO_V = C / SQ3  # circumradius of the Voronoi hexagon of L_rho (= c / sqrt3 < 0.621)


def q_arb(s: str) -> arb:
    f = Fraction(s)
    return arb(f.numerator) / arb(f.denominator)


# ---------------------------------------------------------------- potentials g(q), q = |R|^2, and derivatives

class Potential:
    """V(R) = g(|R|^2); g completely monotone in q (so |g^(j)| is decreasing in q, used for the tails)."""

    def __init__(self, pot: str, par: str) -> None:
        self.pot, self.par = pot, par
        q = sp.symbols("q", positive=True)
        p = sp.Rational(Fraction(par).numerator, Fraction(par).denominator)
        if pot == "yukawa":
            g = sp.exp(-p * sp.sqrt(q)) / sp.sqrt(q)
        elif pot == "gauss":
            g = sp.exp(-sp.pi * p * q)
        else:
            raise ValueError(pot)
        self.sym = [sp.simplify(sp.diff(g, q, j)) for j in range(5)]
        mods = [{"exp": lambda x: x.exp(), "sqrt": lambda x: x.sqrt(), "pi": PI}]
        self.fn = [sp.lambdify(q, e, modules=mods) for e in self.sym]
        self.p = q_arb(par)
        # explicit majorants for the far tail (r >= 1, i.e. q >= 1): |g^(j)(q)| <= Cj * decay(q)
        self.Cj = []
        if pot == "yukawa":
            for e in self.sym:
                poly = sp.expand(sp.simplify(e * sp.exp(p * sp.sqrt(q))))
                terms = sp.Add.make_args(poly)
                bound = sp.Integer(0)
                for term in terms:
                    cf, rest = term.as_coeff_Mul()
                    # every term is c * q^(-e) with e > 0, so |term| <= |c| for q >= 1
                    pw = sp.powsimp(rest).as_base_exp()
                    assert pw[0] == q and pw[1] < 0, (term, pw)
                    bound += abs(cf)
                self.Cj.append(q_arb(str(sp.Rational(bound))))
        else:
            for j in range(5):
                self.Cj.append((PI * self.p) ** j)

    def g(self, j: int, qv: arb) -> arb:
        return self.fn[j](qv)

    def decay(self, r: arb, smin: arb) -> arb:
        """decay factor of the majorant at |R0| = r (|R| >= smin r)."""
        if self.pot == "yukawa":
            return (-self.p * smin * r).exp()
        return (-PI * self.p * smin * smin * r * r).exp()

    def decay_rate(self, rK: arb, smin: arb) -> arb:
        """beta with decay(r + delta) <= exp(-beta delta) decay(r) for r >= rK."""
        if self.pot == "yukawa":
            return self.p * smin
        return 2 * PI * self.p * smin * smin * rK


# ---------------------------------------------------------------- path and Hessian derivatives

def path_R(X0: arb, Y0: arb, t: arb) -> tuple[arb, ...]:
    """shear P_t = [[1, t], [t, 1 + t^2]]: R(t), R'(t), R''(t)."""
    return (X0 + t * Y0, t * X0 + (1 + t * t) * Y0, Y0, X0 + 2 * t * Y0, arb(0), 2 * Y0)


def path_norms(t0: arb) -> tuple[arb, arb, arb, arb]:
    """(sigma_min, sigma_max, sup||P'||, sup||P''||) over |t| <= t0 (B2 path_norms, shear)."""
    e = t0 + t0 * t0
    return (1 - e, 1 + e, 1 + 2 * t0, arb(2))


def hess_derivs(V: Potential, R: tuple[arb, ...]) -> tuple[list[arb], list[arb], list[arb]]:
    """H = Hess V(R(t)) = 2 g'(q) I + 4 g''(q) R R^T and its first two t-derivatives (entries 11, 12, 22)."""
    Rx, Ry, dx, dy, ddx, ddy = R
    qv = Rx * Rx + Ry * Ry
    q1 = 2 * (Rx * dx + Ry * dy)
    q2 = 2 * (dx * dx + dy * dy + Rx * ddx + Ry * ddy)
    g1, g2, g3, g4 = (V.g(j, qv) for j in (1, 2, 3, 4))
    H, H1, H2 = [], [], []
    for (Ri, Rj, di, dj, ddi, ddj, dl) in ((Rx, Rx, dx, dx, ddx, ddx, 1), (Rx, Ry, dx, dy, ddx, ddy, 0),
                                          (Ry, Ry, dy, dy, ddy, ddy, 1)):
        P = Ri * Rj
        P1 = di * Rj + Ri * dj
        P2 = ddi * Rj + 2 * di * dj + Ri * ddj
        H.append(2 * g1 * dl + 4 * g2 * P)
        H1.append(2 * g2 * q1 * dl + 4 * g3 * q1 * P + 4 * g2 * P1)
        H2.append(2 * (g3 * q1 * q1 + g2 * q2) * dl + 4 * (g4 * q1 * q1 + g3 * q2) * P + 8 * g3 * q1 * P1 + 4 * g2 * P2)
    return H, H1, H2


# ---------------------------------------------------------------- forward-mode duals over arb: value, d/ds, d/dt'

class Dl:
    __slots__ = ("v", "s", "t")

    def __init__(self, v: arb, s: arb | int = 0, t: arb | int = 0) -> None:
        self.v, self.s, self.t = v, s, t

    def __add__(self, o: "Dl | arb | int") -> "Dl":
        if isinstance(o, Dl):
            return Dl(self.v + o.v, self.s + o.s, self.t + o.t)
        return Dl(self.v + o, self.s, self.t)

    __radd__ = __add__

    def __neg__(self) -> "Dl":
        return Dl(-self.v, -self.s, -self.t)

    def __sub__(self, o: "Dl | arb | int") -> "Dl":
        return self + (-o)

    def __rsub__(self, o: "arb | int") -> "Dl":
        return (-self) + o

    def __mul__(self, o: "Dl | arb | int") -> "Dl":
        if isinstance(o, Dl):
            return Dl(self.v * o.v, self.s * o.v + self.v * o.s, self.t * o.v + self.v * o.t)
        return Dl(self.v * o, self.s * o, self.t * o)

    __rmul__ = __mul__

    def inv(self) -> "Dl":
        iv = 1 / self.v
        return Dl(iv, -self.s * iv * iv, -self.t * iv * iv)

    def __truediv__(self, o: "Dl | arb | int") -> "Dl":
        if isinstance(o, Dl):
            return self * o.inv()
        return Dl(self.v / o, self.s / o, self.t / o)

    def sqrt(self) -> "Dl":
        r = self.v.sqrt()
        return Dl(r, self.s / (2 * r), self.t / (2 * r))


class Dl2:
    """Second-order forward-mode jets over arb in (s, t'): value, first partials (s, t), second partials (ss, st, tt)."""
    __slots__ = ("v", "s", "t", "ss", "st", "tt")

    def __init__(self, v: arb, s: arb | int = 0, t: arb | int = 0, ss: arb | int = 0, st: arb | int = 0,
                 tt: arb | int = 0) -> None:
        self.v, self.s, self.t, self.ss, self.st, self.tt = v, s, t, ss, st, tt

    def __add__(self, o: "Dl2 | arb | int") -> "Dl2":
        if isinstance(o, Dl2):
            return Dl2(self.v + o.v, self.s + o.s, self.t + o.t, self.ss + o.ss, self.st + o.st, self.tt + o.tt)
        return Dl2(self.v + o, self.s, self.t, self.ss, self.st, self.tt)

    __radd__ = __add__

    def __neg__(self) -> "Dl2":
        return Dl2(-self.v, -self.s, -self.t, -self.ss, -self.st, -self.tt)

    def __sub__(self, o: "Dl2 | arb | int") -> "Dl2":
        return self + (-o)

    def __rsub__(self, o: "arb | int") -> "Dl2":
        return (-self) + o

    def __mul__(self, o: "Dl2 | arb | int") -> "Dl2":
        if isinstance(o, Dl2):
            a, b = self, o
            return Dl2(a.v * b.v, a.s * b.v + a.v * b.s, a.t * b.v + a.v * b.t,
                       a.ss * b.v + 2 * a.s * b.s + a.v * b.ss,
                       a.st * b.v + a.s * b.t + a.t * b.s + a.v * b.st,
                       a.tt * b.v + 2 * a.t * b.t + a.v * b.tt)
        return Dl2(self.v * o, self.s * o, self.t * o, self.ss * o, self.st * o, self.tt * o)

    __rmul__ = __mul__

    def compose(self, f0: arb, f1: arb, f2: arb) -> "Dl2":
        """F(self) given F, F', F'' evaluated at (an enclosure of) self.v."""
        return Dl2(f0, f1 * self.s, f1 * self.t, f2 * self.s * self.s + f1 * self.ss,
                   f2 * self.s * self.t + f1 * self.st, f2 * self.t * self.t + f1 * self.tt)

    def inv(self) -> "Dl2":
        iv = 1 / self.v
        return self.compose(iv, -iv * iv, 2 * iv * iv * iv)

    def __truediv__(self, o: "Dl2 | arb | int") -> "Dl2":
        if isinstance(o, Dl2):
            return self * o.inv()
        return self * (1 / arb(o) if isinstance(o, int) else 1 / o)

    def sqrt(self) -> "Dl2":
        r = self.v.sqrt()
        return self.compose(r, 1 / (2 * r), -1 / (4 * r * r * r))


def m_mul(A: tuple, B: tuple) -> tuple:
    """symmetric-entry 2x2 (a11, a12, a21, a22) general product; inputs as 4-tuples."""
    return (A[0] * B[0] + A[1] * B[2], A[0] * B[1] + A[1] * B[3], A[2] * B[0] + A[3] * B[2], A[2] * B[1] + A[3] * B[3])


def m_tr(A: tuple) -> "Dl":
    return A[0] + A[3]


def sym4(e: list) -> tuple:
    return (e[0], e[1], e[1], e[2])


def m_inv(A: tuple) -> tuple[tuple, "Dl"]:
    det = A[0] * A[3] - A[1] * A[2]
    idet = det.inv()
    return (A[3] * idet, -A[1] * idet, -A[2] * idet, A[0] * idet), det


def det3(a: list) -> "Dl":
    return (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1]) - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
            + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))


def sylvester(Q: list, M: list) -> list:
    """Solve Q Y + Y Q = M for symmetric 2x2 Y (entries 11, 12, 22) by Cramer's rule."""
    q11, q12, q22 = Q
    z = q11 * 0
    A = [[2 * q11, 2 * q12, z], [q12, q11 + q22, q12], [z, 2 * q12, 2 * q22]]
    d = det3(A)
    out = []
    for k in range(3):
        Ak = [[M[i] if j == k else A[i][j] for j in range(3)] for i in range(3)]
        out.append(det3(Ak) / d)
    return out


# ---------------------------------------------------------------- f(x) = (1 - cos x)/x^2 and f'

FACT = [arb(math.factorial(k)) for k in range(40)]


TWO_PI = 2 * PI


def abs_lo(x: arb) -> arb:
    """exact lower bound of |x| over the ball (full precision, unlike abs_lower which is a 30-bit mag)."""
    if bool(x > 0):
        return x.lower()
    if bool(x < 0):
        return -x.upper()
    return arb(0)


def abs_hi(x: arb) -> arb:
    return x.upper().max(-x.lower())


def f_series(x: arb) -> arb:
    """f(x) = sum_k (-1)^k x^(2k)/(2k+2)!, valid for |x| <= 2 (alternating, terms decreasing in modulus)."""
    tot = arb(0)
    x2 = x * x
    pw = arb(1)
    for k in range(0, 8):
        tot += (-1) ** k * pw / FACT[2 * k + 2]
        pw = pw * x2
    return tot + arb(0, 1) * x.abs_upper() ** 16 / FACT[18]


def f_point(y: arb) -> arb:
    """f at a thin point y >= 0."""
    if bool(y <= 2):
        return f_series(y)
    return (1 - y.cos()) / (y * y)


def f_enc(x: arb) -> arb:
    """Enclosure of f(x) = (1 - cos x)/x^2 over the ball x. f is even, decreasing on [0, 2 pi] (f' < 0 there:
    x sin x - 2(1 - cos x) = 2 sin(x/2)(x cos(x/2) - 2 sin(x/2)) < 0), 0 <= f <= min(1/2, 2/x^2)."""
    if bool(x.rad() < arb(10) ** -12):
        return f_point(abs(x)) + arb(0, 1) * x.rad()  # |f'| <= 1/4 < 1 (F1 = 0.138)
    xl, xu = abs_lo(x), abs_hi(x)
    if bool(xu <= TWO_PI):
        return f_point(xu).union(f_point(xl))
    if bool(x.rad() < arb(1) / 20):
        return (1 - x.cos()) / (x * x)
    if bool(xl > 2):
        hi = 2 / (xl * xl)
    else:
        hi = arb(1) / 2
    return arb(0).union(hi)


def fprime_sup() -> arb:
    """sup_x |f'(x)| (B2: (|x| + 4)/|x|^3 <= 1/8 beyond 4, ball evaluation on [0, 4])."""
    F1 = arb(1) / 8
    for i in range(256):
        F1 = F1.max(fprime_series(arb((i + 0.5) / 64, 0.5 / 64)).abs_upper() if (i + 1) / 64 <= 2
                    else fprime_closed(arb((i + 0.5) / 64, 0.5 / 64)).abs_upper())
    return F1


def fprime_closed(x: arb) -> arb:
    sn, cs = x.sin(), x.cos()
    return (x * sn - 2 * (1 - cs)) / (x * x * x)


def fprime_series(x: arb) -> arb:
    """valid for |x| <= 2 (alternating series, terms decreasing; remainder bounded by the first omitted term)."""
    tot = arb(0)
    x2 = x * x
    pw = x  # x^(2k-1), by repeated multiplication (arb ** int is not used on balls containing 0)
    for k in range(1, 8):
        tot += (-1) ** k * (2 * k) * pw / FACT[2 * k + 2]
        pw = pw * x2
    K = 8
    rem = (2 * K) * x.abs_upper() ** (2 * K - 1) / FACT[2 * K + 2]
    return tot + arb(0, 1) * rem


def fprime_enc(x: arb, F1: arb) -> arb:
    """Enclosure of f'(x) over the ball x: series (|x| <= 2) or closed form (|x| >= 1) on narrow balls, otherwise the
    bound |f'| <= min(F1, (|x| + 4)/|x|^3)."""
    xl, xu = x.abs_lower(), x.abs_upper()
    if bool(xu <= 2) and bool(x.rad() < arb(1) / 4):
        return fprime_series(x)
    if bool(xl >= 1) and bool(x.rad() < xl / 20):
        return fprime_closed(x)
    b = F1
    if bool(xl >= 1):
        b2 = (xu + 4) / (xl * xl * xl)
        if bool(b2 < b):
            b = b2
    return arb(0, 1) * b


def fsecond_series(x: arb) -> arb:
    """f''(x) = sum_{k>=1} (-1)^k (2k)(2k-1) x^(2k-2)/(2k+2)!, valid for |x| <= 2 (alternating, terms decreasing:
    ratio <= x^2/5 < 1)."""
    tot = arb(0)
    x2 = x * x
    pw = arb(1)
    for k in range(1, 9):
        tot += (-1) ** k * (2 * k) * (2 * k - 1) * pw / FACT[2 * k + 2]
        pw = pw * x2
    K = 9
    return tot + arb(0, 1) * (2 * K) * (2 * K - 1) * abs_hi(x) ** (2 * K - 2) / FACT[2 * K + 2]


def fsecond_closed(x: arb) -> arb:
    x2 = x * x
    return x.cos() / x2 - 4 * x.sin() / (x2 * x) + 6 * (1 - x.cos()) / (x2 * x2)


def fsecond_sup() -> arb:
    """sup |f''|: ball evaluation on [0, 4] (series on [0, 2], closed form on [2, 4]); for |x| >= 4,
    |f''| <= 1/x^2 + 4/|x|^3 + 12/x^4 <= 0.171875."""
    F2 = arb(11) / 64
    for i in range(256):
        b = arb((i + 0.5) / 64, 0.5 / 64)
        v = fsecond_series(b) if (i + 1) / 64 <= 2 else fsecond_closed(b)
        F2 = F2.max(abs_hi(v))
    return F2


def fsecond_enc(x: arb, F2: arb) -> arb:
    xl, xu = abs_lo(x), abs_hi(x)
    if bool(xu <= 2) and bool(x.rad() < arb(1) / 4):
        return fsecond_series(x)
    if bool(xl >= 1) and bool(x.rad() < xl / 20):
        return fsecond_closed(x)
    b = F2
    if bool(xl >= 4):
        b2 = 1 / (xl * xl) + 4 / (xl * xl * xl) + 12 / (xl * xl * xl * xl)
        if bool(b2 < b):
            b = b2
    return arb(0, 1) * b


# ---------------------------------------------------------------- lattice and tails

def lattice_half(qmax: int) -> list[tuple[int, int]]:
    out = []
    lim = int(math.isqrt(4 * qmax)) + 2
    for m in range(-lim, lim + 1):
        for l in range(-lim, lim + 1):
            if (m, l) == (0, 0) or m * m + m * l + l * l > qmax:
                continue
            if m > 0 or (m == 0 and l > 0):
                out.append((m, l))
    return out


def point_bounds(V: Potential, r: arb, r_out: arb, t0: arb, gb: list[arb] | None) -> tuple[arb, arb, arb]:
    """Entry bounds for |H|, |H'|, |H''| over |t| <= t0 for a lattice point with r <= |R0| <= r_out.
    gb: values |g^(j)| at q_lo (if None: computed from the decreasing |g^(j)| at q_lo = (smin r)^2)."""
    smin, smax, d1, d2 = path_norms(t0)
    if gb is None:
        qlo = (smin * r) ** 2
        gb = [V.g(j, qlo).abs_upper() for j in range(5)]
    Rm, R1, R2 = smax * r_out, d1 * r_out, d2 * r_out
    q1 = 2 * Rm * R1
    q2 = 2 * (R1 * R1 + Rm * R2)
    P, P1, P2 = Rm * Rm, 2 * Rm * R1, 2 * R2 * Rm + 2 * R1 * R1
    bH = 2 * gb[1] + 4 * gb[2] * P
    bH1 = 2 * gb[2] * q1 + 4 * gb[3] * q1 * P + 4 * gb[2] * P1
    bH2 = 2 * (gb[3] * q1 * q1 + gb[2] * q2) + 4 * (gb[4] * q1 * q1 + gb[3] * q2) * P + 8 * gb[3] * q1 * P1 + 4 * gb[2] * P2
    return bH, bH1, bH2


def tail_bounds(V: Potential, qmax: int, t0: arb, F1: arb, K: int = 400, delta: arb = arb(1) / 2) -> dict:
    """Entrywise bounds on the truncated sums over all n with m^2 + m l + l^2 >= qmax + 1 (|R0| >= r_tail),
    uniform in kappa and |t| <= t0, for B^(k) (k = 0, 1, 2) and their s- and t'-partials.
    Shell [r, r + delta): #points <= pi (r + delta + rho)^2 - pi (r - rho)^2 (Voronoi hexagons of area 1, circumradius
    rho = c/sqrt3); |g^(j)| decreasing in q (complete monotonicity), evaluated at q_lo = (smin r)^2; polynomial factors at
    r + delta. Beyond r_K = r_tail + K delta: explicit majorant |g^(j)(q)| <= C_j decay(q) and a geometric series with
    ratio rho_K = (1 + 2 delta / r_K)^12 exp(-beta delta) (all polynomial degrees <= 1 + 4 + 4 = 9 <= 12), checked < 1."""
    smin = path_norms(t0)[0]
    r_tail = C * arb(qmax + 1).sqrt()
    sq2 = arb(2).sqrt()
    keys = [f"{a}{k}" for a in ("v", "s", "t", "ss", "st", "tt") for k in range(3)]
    F2 = fsecond_sup()
    acc = {k: arb(0) for k in keys}

    def shell(r: arb, gb: list[arb] | None) -> dict:
        ro = r + delta
        cnt = PI * ((ro + RHO_V) ** 2 - (r - RHO_V) ** 2)
        th = 2 * PI * ro / C
        be = sq2 * th
        w = th * th
        ws = 2 * th * th * th * F1
        wt = 2 * th * be + 2 * th * th * F1 * be
        # second partials of theta^2 f(s theta) (x2 for safety, as above), s <= 1, f <= 1/2
        wss = 2 * th ** 4 * F2
        wst = 2 * (6 * th * th * be * F1 + 2 * th ** 3 * be * F2)
        wtt = 2 * (2 * be * be + 8 * th * be * be * F1 + 2 * th * th * be * be * F2)
        bs = point_bounds(V, r, ro, t0, gb)
        out = {}
        for k in range(3):
            out[f"v{k}"] = cnt * w * bs[k]
            out[f"s{k}"] = cnt * ws * bs[k]
            out[f"t{k}"] = cnt * wt * bs[k]
            out[f"ss{k}"] = cnt * wss * bs[k]
            out[f"st{k}"] = cnt * wst * bs[k]
            out[f"tt{k}"] = cnt * wtt * bs[k]
        return out

    for kk in range(K):
        r = r_tail + kk * delta
        sh = shell(r, None)
        for k in keys:
            acc[k] += sh[k]
    rK = r_tail + K * delta
    assert bool(rK >= 1)
    gmaj = [V.Cj[j] * V.decay(rK, smin) for j in range(5)]
    shK = shell(rK, gmaj)
    beta = V.decay_rate(rK, smin)
    ratio = (1 + 2 * delta / rK) ** 12 * (-beta * delta).exp()
    assert bool(ratio < 1), "tail ratio not < 1"
    rem = {k: shK[k] / (1 - ratio) for k in keys}
    res = {k: acc[k] + rem[k] for k in keys}
    res["r_tail"] = r_tail
    res["r_K"] = rK
    res["ratio"] = ratio
    res["remainder_v0"] = rem["v0"]
    return res


# ---------------------------------------------------------------- the model

class Model:
    def __init__(self, V: Potential, t0: arb, qmax: int) -> None:
        self.V, self.t0, self.qmax = V, t0, qmax
        self.ns = lattice_half(qmax)
        self.F1 = fprime_sup()
        zero = arb(0)
        self.ub = arb(0, 1) * t0
        cols = []  # per n: 18 numbers: B0, B1_0, B2_0 (t = 0) and B_u, B1_u, B2_u (u in window), 3 entries each
        for (m, l) in self.ns:
            X0 = C * (m + HALF * l)
            Y0 = C * l * SQ3 / 2
            H0 = hess_derivs(V, path_R(X0, Y0, zero))
            Hu = hess_derivs(V, path_R(X0, Y0, self.ub))
            row = []
            for H in (H0[0], H0[1], H0[2], Hu[0], Hu[1], Hu[2]):
                row += H
            cols.append(row)
        self.Hmat = arb_mat(len(self.ns), 18, [x for row in cols for x in row])
        self.th = {0: [(PI * (m - l), 2 * PI * l) for (m, l) in self.ns], 1: [(PI * (l - m), 2 * PI * m) for (m, l) in self.ns]}
        self.tails = tail_bounds(V, qmax, t0, self.F1)
        tb = self.tails
        self.tvec = {a: [arb(0, 1) * tb[f"{a}{(k // 3) % 3}"] for k in range(18)] for a in ("v", "s", "t", "ss", "st", "tt")}
        self.F2 = fsecond_sup()
        self.order = int(os.environ.get("N2_ORDER", "2"))

    def sums(self, tri: int, s: arb, tt: arb) -> list[Dl]:
        """18 lattice sums sum_n w_n(s, t') H_n^(k) as duals (value, d/ds, d/dt') over the (s, t') ball, tails added."""
        wv, ws, wt = [], [], []
        F1 = self.F1
        for (al, be) in self.th[tri]:
            th = al + be * tt
            x = s * th
            fx = f_enc(x)
            fp = fprime_enc(x, F1)
            wv.append(2 * th * th * fx)
            ws.append(2 * th * th * th * fp)
            wt.append(4 * th * be * fx + 2 * th * th * fp * s * be)
        n = len(self.ns)
        W = arb_mat(3, n, wv + ws + wt)
        P = W * self.Hmat
        out = []
        for k in range(18):
            out.append(Dl(P[0, k] + self.tvec["v"][k], P[1, k] + self.tvec["s"][k], P[2, k] + self.tvec["t"][k]))
        return out

    def sums2(self, tri: int, s: arb, tt: arb) -> list[Dl2]:
        """18 lattice sums as second-order jets in (s, t') over the ball, tails added."""
        rows = {k: [] for k in ("v", "s", "t", "ss", "st", "tt")}
        F1, F2 = self.F1, self.F2
        for (al, be) in self.th[tri]:
            th = al + be * tt
            x = s * th
            fx = f_enc(x)
            f1 = fprime_enc(x, F1)
            f2 = fsecond_enc(x, F2)
            th2 = th * th
            rows["v"].append(2 * th2 * fx)
            rows["s"].append(2 * th2 * th * f1)
            rows["t"].append(4 * th * be * fx + 2 * th2 * f1 * s * be)
            rows["ss"].append(2 * th2 * th2 * f2)
            rows["st"].append(6 * th2 * be * f1 + 2 * th2 * th * f2 * s * be)
            rows["tt"].append(4 * be * be * fx + 8 * th * be * be * s * f1 + 2 * th2 * s * s * be * be * f2)
        n = len(self.ns)
        W = arb_mat(6, n, rows["v"] + rows["s"] + rows["t"] + rows["ss"] + rows["st"] + rows["tt"])
        P = W * self.Hmat
        out = []
        tv = self.tvec
        for k in range(18):
            out.append(Dl2(P[0, k] + tv["v"][k], P[1, k] + tv["s"][k], P[2, k] + tv["t"][k], P[3, k] + tv["ss"][k],
                           P[4, k] + tv["st"][k], P[5, k] + tv["tt"][k]))
        return out

    def cell2(self, tri: int, s0: Fraction, t0_: Fraction, h: Fraction) -> dict:
        """Second-order cell rule: int_cell g = |cell| (g(c) + R), |R| <= h^2/24 (sup|g_ss| + sup|g_tt|) + h^2/16 sup|g_st|
        (Taylor with Lagrange remainder; the linear term integrates to 0 on the square). Box values and first partials
        of the 18 sums are tightened by Taylor forms around the centre, intersected with the naive box enclosures."""
        hs = arb(float(h / 2))
        sc, tc = arb(float(s0 + h / 2)), arb(float(t0_ + h / 2))
        sb, tb = arb(float(s0 + h / 2), float(h / 2)), arb(float(t0_ + h / 2), float(h / 2))
        dS = arb(0, 1) * hs
        Sc = self.sums(tri, sc, tc)
        Sb = self.sums2(tri, sb, tb)
        St = []
        for c, b in zip(Sc, Sb):
            v = (c.v + c.s * dS + c.t * dS + (b.ss * dS * dS + 2 * b.st * dS * dS + b.tt * dS * dS) / 2).intersection(b.v)
            ps = (c.s + b.ss * dS + b.st * dS).intersection(b.s)
            pt = (c.t + b.st * dS + b.tt * dS).intersection(b.t)
            St.append(Dl2(v, ps, pt, b.ss, b.st, b.tt))
        ic = self.integrand([Dl(c.v) for c in Sc], Dl(sc))
        ib = self.integrand(St, Dl2(sb, 1))
        if not (ic["ok"] and ib["ok"]):
            return {"ok": False, "why": ic.get("why", ib.get("why"))}
        A = arb(float(h * h))
        h2 = arb(float(h * h))
        out = {"ok": True, "lmin": ib["lmin"], "lminu": ib["lminu"], "qpd": ib["qpd"]}
        for key in ("g", "lin", "ezp"):
            gc, gb = ic[key], ib[key]
            R = h2 / 24 * (abs_hi(gb.ss) + abs_hi(gb.tt)) + h2 / 16 * abs_hi(gb.st)
            out[key] = A * (gc.v + arb(0, 1) * R)
        out["width"] = out["g"].rad()
        return out

    def integrand(self, S: list[Dl], s: Dl) -> dict:
        """phi and the integrands from the 18 sums (duals)."""
        B0, B10, B20 = S[0:3], S[3:6], S[6:9]
        Bu, B1u, B2u = S[9:12], S[12:15], S[15:18]
        det0 = B0[0] * B0[2] - B0[1] * B0[1]
        tr0 = B0[0] + B0[2]
        detu = Bu[0] * Bu[2] - Bu[1] * Bu[1]
        tru = Bu[0] + Bu[2]
        if not (bool(det0.v > 0) and bool(tr0.v > 0) and bool(detu.v > 0) and bool(tru.v > 0)):
            return {"ok": False, "why": "B not PD"}
        d = det0.sqrt()
        tau = (tr0 + 2 * d).sqrt()
        Q = [(B0[0] + d) / tau, B0[1] / tau, (B0[2] + d) / tau]
        Yt = sylvester(Q, B10)
        Qu = [Q[0] + Yt[0] * self.ub, Q[1] + Yt[1] * self.ub, Q[2] + Yt[2] * self.ub]
        detQu = Qu[0] * Qu[2] - Qu[1] * Qu[1]
        trQu = Qu[0] + Qu[2]
        if not (bool(detQu.v > 0) and bool(trQu.v > 0)):
            return {"ok": False, "why": "X_t not PD"}
        Qi, _ = m_inv(sym4(Qu))
        Y4 = sym4(Yt)
        A = m_mul(Qi, Y4)  # Qi Yt
        AA = m_mul(A, A)  # Qi Yt Qi Yt
        phi = 2 * m_tr(m_mul(m_mul(AA, Qi), sym4(Bu)))
        phi = phi - 2 * m_tr(m_mul(m_mul(A, Qi), sym4(B1u))) + m_tr(m_mul(Qi, sym4(B2u)))
        # linear-response (B2) curvature integrand, tr(Q^-1 B2_0) at t = 0 (comparison only)
        Q0i, _ = m_inv(sym4(Q))
        lin = m_tr(m_mul(Q0i, sym4(B20)))
        g = s * s * phi / 8
        return {"ok": True, "g": g, "lin": s * s * lin / 8, "ezp": s * s * tau / 4, "lmin": det0.v / tr0.v,
                "lminu": detu.v / tru.v, "qpd": detQu.v / trQu.v}

    def cell(self, tri: int, s0: Fraction, t0_: Fraction, h: Fraction) -> dict:
        hs = arb(float(h / 2))
        sc, tc = arb(float(s0 + h / 2)), arb(float(t0_ + h / 2))
        sb, tb = arb(float(s0 + h / 2), float(h / 2)), arb(float(t0_ + h / 2), float(h / 2))
        dS = arb(0, 1) * hs
        Sc = self.sums(tri, sc, tc)
        Sb = self.sums(tri, sb, tb)
        # tighten the box values by the mean-value form (centre + partials * half-width), keep the box partials
        St = [Dl((c.v + b.s * dS + b.t * dS).intersection(b.v), b.s, b.t) for c, b in zip(Sc, Sb)]
        ic = self.integrand([Dl(c.v) for c in Sc], Dl(sc))
        ib = self.integrand(St, Dl(sb, 1, 0))
        if not (ic["ok"] and ib["ok"]):
            return {"ok": False, "why": ic.get("why", ib.get("why"))}
        A = arb(float(h * h))
        q = hs / 2
        out = {"ok": True, "lmin": ib["lmin"], "lminu": ib["lminu"], "qpd": ib["qpd"]}
        for key in ("g", "lin", "ezp"):
            gc, gb = ic[key], ib[key]
            out[key] = A * (gc.v + arb(0, 1) * q * (gb.s.abs_upper() + gb.t.abs_upper()))
        out["width"] = out["g"].rad()
        return out


def integrate(model: Model, N: int, refine_tol: float, max_depth: int, log_every: int = 2000) -> dict:
    tot = {"g": arb(0), "lin": arb(0), "ezp": arb(0)}
    st = {"cells": 0, "refined": 0, "failed": 0, "lmin_lo": math.inf, "lminu_lo": math.inf, "qpd_lo": math.inf}
    h0 = Fraction(1, N)
    stack = [(tri, Fraction(i, N), Fraction(j, N), h0, 0) for tri in (0, 1) for i in range(N) for j in range(N)]
    t_start = time.time()
    while stack:
        tri, s0, t0_, h, depth = stack.pop()
        r = model.cell2(tri, s0, t0_, h) if model.order == 2 else model.cell(tri, s0, t0_, h)
        wide = (not r["ok"]) or bool(r["width"] > refine_tol * float(h * h))
        if wide and depth < max_depth:
            h2 = h / 2
            for ds in (0, 1):
                for dt in (0, 1):
                    stack.append((tri, s0 + ds * h2, t0_ + dt * h2, h2, depth + 1))
            st["refined"] += 1
            continue
        st["cells"] += 1
        if not r["ok"]:
            st["failed"] += 1
            st.setdefault("why", {})
            st["why"][str(r.get("why"))] = st["why"].get(str(r.get("why")), 0) + 1
            continue
        for key in tot:
            tot[key] += 2 * r[key]
        band = f"tri{tri}_s{int(8 * s0)}_t{int(4 * t0_)}"
        st.setdefault("width_by_band", {})
        st["width_by_band"][band] = st["width_by_band"].get(band, 0.0) + 2 * float(r["width"])
        for key in ("lmin", "lminu", "qpd"):
            st[key + "_lo"] = min(st[key + "_lo"], float(lower_frac(r[key])))
        if st["cells"] % log_every == 0:
            print(f"  cells {st['cells']} stack {len(stack)} {time.time() - t_start:.0f}s M={float(tot['g'].mid()):.4f}+-{float(tot['g'].rad()):.4f} failed={st['failed']}", flush=True)
    return {"tot": tot, "stats": st}


def exact_frac(x: arb) -> Fraction:
    m, e = x.man_exp()
    return Fraction(int(m)) * (Fraction(2) ** int(e))


def upper_frac(x: arb) -> Fraction:
    return exact_frac(x.mid()) + exact_frac(x.rad())


def lower_frac(x: arb) -> Fraction:
    return exact_frac(x.mid()) - exact_frac(x.rad())


def to_q_upper(x: arb, den: int = 10**12) -> Fraction:
    return Fraction(math.ceil(upper_frac(x) * den), den)


def to_q_lower(x: arb, den: int = 10**12) -> Fraction:
    return Fraction(math.floor(lower_frac(x) * den), den)


def ball(x: arb) -> dict:
    if not x.is_finite():
        return {"lo": None, "hi": None, "lo_float": None, "hi_float": None, "mid": None, "rad": "inf"}
    return {"lo": str(to_q_lower(x)), "hi": str(to_q_upper(x)), "lo_float": float(lower_frac(x)),
            "hi_float": float(upper_frac(x)), "mid": float(x.mid()), "rad": float(exact_frac(x.rad()))}


P2_EZP = {("yukawa", "1"): "1.7658983", ("yukawa", "2"): "1.4592747", ("gauss", "1"): "1.50335235220736",
          ("gauss", "2"): "0.5419325"}


def main() -> None:
    pot, par, N, t0_s, qmax, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5]), sys.argv[6]
    refine_tol = float(os.environ.get("N2_REFINE_TOL", "0.05"))
    max_depth = int(os.environ.get("N2_MAX_DEPTH", "2"))
    t_start = time.time()
    V = Potential(pot, par)
    t0 = q_arb(t0_s)
    model = Model(V, t0, qmax)
    tl = model.tails
    print(f"{pot}:{par} pairs={len(model.ns)} r_tail={float(tl['r_tail'].mid()):.2f} tail v0={float(tl['v0'].upper()):.3e} "
          f"v2={float(tl['v2'].upper()):.3e} s0={float(tl['s0'].upper()):.3e} t2={float(tl['t2'].upper()):.3e}", flush=True)
    res = integrate(model, N, refine_tol, max_depth)
    tot, st = res["tot"], res["stats"]
    M = tot["g"]
    pd_ok = st["failed"] == 0 and st["lmin_lo"] > 0 and st["lminu_lo"] > 0 and st["qpd_lo"] > 0
    certified = bool(M < 0) and pd_ok
    p2 = P2_EZP.get((pot, par))
    rec = {
        "potential": pot, "param": par, "path": "shear", "N": N, "t0": t0_s, "qmax": qmax, "refine_tol": refine_tol,
        "max_depth": max_depth, "cell_rule_order": model.order, "n_lattice_half": len(model.ns), "python_flint": flint.__version__,
        "arb_prec_bits": ctx.prec, "seconds": round(time.time() - t_start, 1),
        "M_window_curvature_bound": ball(M), "U_lin_pp0_B2_majorant": ball(tot["lin"]), "E0": ball(tot["ezp"]),
        "tails": {k: (float(v.upper()) if isinstance(v, arb) else v) for k, v in tl.items()},
        "stats": st, "positivity_ok": pd_ok, "certified_not_local_min": certified,
        "cert_rationals": {"M_hi": str(to_q_upper(M)) if M.is_finite() else None,
                           "M_lo": str(to_q_lower(M)) if M.is_finite() else None,
                           "lmin_lo": str(Fraction(math.floor(st["lmin_lo"] * 10**12), 10**12)) if math.isfinite(st["lmin_lo"]) else None,
                           "lminu_lo": str(Fraction(math.floor(st["lminu_lo"] * 10**12), 10**12)) if math.isfinite(st["lminu_lo"]) else None,
                           "qpd_lo": str(Fraction(math.floor(st["qpd_lo"] * 10**12), 10**12)) if math.isfinite(st["qpd_lo"]) else None},
        "controls": {"E0_contains_P2": (bool(tot["ezp"].overlaps(arb(p2, 1e-6))) if p2 else None), "P2_E0": p2},
    }
    with open(__file__, "rb") as fh:
        rec["script_sha256"] = hashlib.sha256(fh.read()).hexdigest()
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=1)
    print(json.dumps({k: rec[k] for k in ("potential", "param", "M_window_curvature_bound", "U_lin_pp0_B2_majorant", "E0",
                                          "certified_not_local_min", "positivity_ok", "seconds", "controls")}, indent=1))
    print("stats", st)


if __name__ == "__main__":
    main()
