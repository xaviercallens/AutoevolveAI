"""Exact analysis of a numeric (rational) member of the family: all positive equilibria with sink/saddle classification."""
from __future__ import annotations
from fractions import Fraction as Fr
import sympy as sp
from bistab import *


class Iv:
    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi=None):
        self.lo = Fr(lo)
        self.hi = Fr(lo if hi is None else hi)

    def __add__(s, o):
        o = o if isinstance(o, Iv) else Iv(o)
        return Iv(s.lo + o.lo, s.hi + o.hi)

    __radd__ = __add__

    def __neg__(s):
        return Iv(-s.hi, -s.lo)

    def __sub__(s, o):
        o = o if isinstance(o, Iv) else Iv(o)
        return s + (-o)

    def __mul__(s, o):
        o = o if isinstance(o, Iv) else Iv(o)
        c = [s.lo * o.lo, s.lo * o.hi, s.hi * o.lo, s.hi * o.hi]
        return Iv(min(c), max(c))

    __rmul__ = __mul__

    def sign(s):
        if s.lo > 0:
            return 1
        if s.hi < 0:
            return -1
        return 0  # undecided


def horner(coeffs, X):  # coeffs high->low, sympy rationals
    r = Iv(0)
    for c in coeffs:
        r = r * X + Iv(Fr(int(c.p), int(c.q)))
    return r


def analyse(es, ks, a_, b_, rho_=Fr(1), eps=Fr(1, 10 ** 40)):
    """Return dict with positive equilibria: list of (x-interval, y-interval, sign trace, sign det)."""
    R = lambda v: sp.Rational(v.numerator, v.denominator)
    f, g = fields(es, [R(k) for k in ks], R(a_), R(b_), R(rho_))
    gb = sp.groebner([f, g], y, x, order="lex", domain="QQ")
    polys = list(gb.exprs)
    Px = [p for p in polys if not p.has(y)]
    if len(Px) != 1:
        return dict(status="no_elimination_poly", gb=[str(p) for p in polys])
    P = sp.Poly(Px[0], x)
    P = sp.Poly(sp.quo(P, sp.gcd(P, P.diff(x))), x)  # squarefree (gb already radical-agnostic)
    ys = [p for p in polys if p.has(y)]
    if len(ys) != 1 or sp.Poly(ys[0], y).degree() != 1:
        return dict(status="not_shape_position", P=str(P.as_expr()), gb=[str(p) for p in polys])
    py = sp.Poly(ys[0], y)
    lc = sp.Poly(py.coeff_monomial(y), x)
    c0 = sp.Poly(py.coeff_monomial(1), x)
    if lc.degree() != 0:
        return dict(status="y_not_monic", P=str(P.as_expr()))
    Q = sp.Poly(-c0.as_expr() / lc.as_expr(), x)  # y = Q(x)
    n_pos = P.count_roots(0, None)  # roots in [0, inf)
    atzero = P.eval(0) == 0
    ivs = P.intervals(inf=0, eps=R(eps), sqf=True) if n_pos else []
    Jf = sp.Matrix([f, g]).jacobian([x, y])
    Jy = Jf.subs(y, Q.as_expr())
    T = sp.Poly(sp.expand(Jy.trace()), x)
    D = sp.Poly(sp.expand(Jy.det()), x)
    eqs = []
    for (lo, hi) in ivs:
        X = Iv(Fr(int(lo.p), int(lo.q)), Fr(int(hi.p), int(hi.q)))
        yq = horner(Q.all_coeffs(), X)
        tr = horner(T.all_coeffs(), X).sign()
        de = horner(D.all_coeffs(), X).sign()
        eqs.append(dict(x_lo=str(X.lo)[:60], x_hi=str(X.hi)[:60], x_approx=float(X.lo), y_approx=float((yq.lo + yq.hi) / 2),
                        y_sign=yq.sign(), tr=tr, det=de))
    pos = [e for e in eqs if e["y_sign"] == 1]
    undecided = [e for e in eqs if e["y_sign"] == 0 or e["tr"] == 0 or e["det"] == 0]
    sinks = [e for e in pos if e["tr"] == -1 and e["det"] == 1]
    saddles = [e for e in pos if e["det"] == -1]
    return dict(status="ok", degP=P.degree(), n_roots_x_ge0=n_pos, root_at_zero=atzero, n_positive_equilibria=len(pos),
                n_sinks=len(sinks), n_saddles=len(saddles), n_other=len(pos) - len(sinks) - len(saddles),
                undecided=len(undecided), equilibria=pos)
