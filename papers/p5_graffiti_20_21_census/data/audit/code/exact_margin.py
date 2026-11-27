"""Exact margins for listed graph6 strings: integer charpoly (sympy), exact inertia (Descartes),
S+ enclosed by sympy real-root isolation of the squarefree part (width 1e-25), with multiplicities.
Prints certified enclosures of S+ - n_+ (conj 20) and S+ - n_- (conj 21)."""
import sys
import sympy as sp
from fractions import Fraction
sys.path.insert(0, '/tmp/gr11audit/code')
from exact_c29 import g6, inertia  # noqa: E402  (module body only runs over argv file if __main__ guard absent)

x = sp.symbols('x')


def splus(A: list[list[int]]) -> tuple[Fraction, Fraction]:
    p = sp.Poly(sp.Matrix(A).charpoly(x).as_expr(), x)
    lo = hi = Fraction(0)
    for (a, b), m in p.intervals(eps=sp.Rational(1, 10 ** 25)):
        a = Fraction(int(a.p), int(a.q)); b = Fraction(int(b.p), int(b.q))
        if a > 0:
            lo += m * a; hi += m * b
        elif b > 0:
            hi += m * b
    return lo, hi


for s in [l.strip() for l in open(sys.argv[1]) if l.strip()]:
    A = g6(s)
    np_, nn, nz = inertia(A)
    lo, hi = splus(A)
    print(s, 'inertia', (np_, nn, nz), 'S+ in [%.15f, %.15f]' % (float(lo), float(hi)),
          'm20 in [%.12f, %.12f]' % (float(lo - np_), float(hi - np_)),
          'm21 in [%.12f, %.12f]' % (float(lo - nn), float(hi - nn)),
          'c20', 'HOLDS' if lo >= np_ else ('VIOL' if hi < np_ else 'TIE?'),
          'c21', 'HOLDS' if lo >= nn else ('VIOL' if hi < nn else 'TIE?'))
