"""N1 engine v2: rigorous (Arb) enclosure of the exact second variation F(a, t) = d^2/dt^2 E_zp along the shear
path through the triangular lattice, for the Gaussian exp(-pi a r^2), valid for EVERY a in an interval
[a_c - delta, a_c + delta] and every |t| <= t0, in the affine form

    F(a, t) in Q + (a - a_c) D + R,

with Q = sum_cells |cell| g(c, a_c)  (a midpoint sum at the exact centre a_c, thin balls),
     D = sum_cells |cell| d_a g(c, a_c)  (the same midpoint sum of the a-derivative, signed),
     R = sum_cells of the second-order Taylor remainder in (s, t', a) over cell x a-interval, bounded with
         second partials enclosed over the cell ball and the whole a-interval (and the t-window):
         R_cell in |cell| [ (h^2/24)(g_ss + g_t't') + (h^2/16)|g_st'|[-1,1] + (delta h/4)(|g_sa| + |g_t'a|)[-1,1]
                            + hull(0, (delta^2/2) g_aa) ].
(Lagrange form of Taylor's theorem in three variables on the convex set cell x [a_c - delta, a_c + delta]; the
first-order terms in s, t' integrate to zero over the square cell, the first-order term in a is (a - a_c) D.)

usage: python -I n1_certify2.py OUT.json N T0 QMAX TOL DEPTH A_LO:A_HI [A_LO:A_HI ...]
  N      initial Duffy grid N x N per triangle; a cell is bisected while rad(R_cell) > TOL |cell| (DEPTH levels)
  T0     window half-width (rational), t ranges over the ball [-T0, T0] in H_n(t)
  QMAX   lattice truncation (0: max(6, ceil(20/a_lo))); the rest is a rigorous tail added to every jet
         component

Integrand (same as n1_certify.py): g = s^2 tau''/4, tau = sqrt(T + 2 delta), T = tr B, delta = sqrt det B,
B = sum_n theta_n^2 f(s theta_n) H_n(t) (Duffy coordinates; see that file and CERTIFIED_CURVATURE.md of B2).
Second-order forward-mode jets in (s, t', a). f = (1 - cos x)/x^2 and its derivatives over balls by centred forms
with |f^{(k)}| <= 1/((k+1)(k+2)) (from f(x) = int_0^1 (1 - u) cos(u x) du).
A cell counts only if det B > 0 and tr B > 0 are certified on the cell ball x a-interval x t-window (dynamical
stability of every L_t, |t| <= T0, for every a in the interval).
Every number is an arb ball (python-flint 0.6.0, 96 bits): rigorous, not kernel-checked (Tier C-ball).
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n1_certify as v1  # noqa: E402
from n1_certify import C, HALF, PI, SQ3, J, arb, f_thin, flint, ctx, hess_derivs, lattice_half, path_R, path_norms  # noqa: E402,F401

IDX = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))  # ss, st, sa, tt, ta, aa


class K:
    """Second-order jet in (s, t', a): value v, gradient g[3], Hessian h[6] in the order IDX."""
    __slots__ = ("v", "g", "h")

    def __init__(self, v: arb, g: list, h: list) -> None:
        self.v, self.g, self.h = v, g, h

    def __add__(self, o: object) -> "K":
        if isinstance(o, K):
            return K(self.v + o.v, [x + y for x, y in zip(self.g, o.g)], [x + y for x, y in zip(self.h, o.h)])
        return K(self.v + o, self.g, self.h)

    __radd__ = __add__

    def __sub__(self, o: object) -> "K":
        if isinstance(o, K):
            return K(self.v - o.v, [x - y for x, y in zip(self.g, o.g)], [x - y for x, y in zip(self.h, o.h)])
        return K(self.v - o, self.g, self.h)

    def __rsub__(self, o: object) -> "K":
        return K(o - self.v, [-x for x in self.g], [-x for x in self.h])

    def __neg__(self) -> "K":
        return K(-self.v, [-x for x in self.g], [-x for x in self.h])

    def __mul__(self, o: object) -> "K":
        if isinstance(o, K):
            u, w = self, o
            g = [u.g[i] * w.v + u.v * w.g[i] for i in range(3)]
            h = [u.h[k] * w.v + u.g[i] * w.g[j] + u.g[j] * w.g[i] + u.v * w.h[k] for k, (i, j) in enumerate(IDX)]
            return K(u.v * w.v, g, h)
        return K(self.v * o, [x * o for x in self.g], [x * o for x in self.h])

    __rmul__ = __mul__

    def unary(self, p0: arb, p1: arb, p2: arb) -> "K":
        g = [p1 * x for x in self.g]
        h = [p2 * self.g[i] * self.g[j] + p1 * self.h[k] for k, (i, j) in enumerate(IDX)]
        return K(p0, g, h)

    def recip(self) -> "K":
        r = 1 / self.v
        return self.unary(r, -r * r, 2 * r * r * r)

    def __truediv__(self, o: object) -> "K":
        if isinstance(o, K):
            return self * o.recip()
        return self * (1 / o)

    def __rtruediv__(self, o: object) -> "K":
        return self.recip() * o

    def sqrt(self) -> "K":
        r = self.v.sqrt()
        return self.unary(r, 1 / (2 * r), -1 / (4 * r * self.v))

    def exp(self) -> "K":
        e = self.v.exp()
        return self.unary(e, e, e)


def vv(x: object) -> arb:
    if isinstance(x, P):
        return x.b.v
    return x.v if isinstance(x, (K, J)) else x


def sq(x: object) -> object:
    if isinstance(x, (K, P)):
        return x.sqrt()
    return v1.sqrt_(x)


HIDX = {(0, 0): 0, (0, 1): 1, (1, 0): 1, (0, 2): 2, (2, 0): 2, (1, 1): 3, (1, 2): 4, (2, 1): 4, (2, 2): 5}


class P:
    """A quantity evaluated twice in lockstep: c = first-order jet at the thin cell centre (s_c, t'_c, a_c), b =
    second-order jet over the cell ball x a-interval. After every operation the ball jet is tightened by mean-value
    forms around the centre: grad in grad(c) + Hess(b) Delta, value in val(c) + grad(b) Delta (each intersected with
    the naive enclosure), Delta = ([-r_s, r_s], [-r_t', r_t'], [-delta, delta]) set in P.D before each cell."""
    __slots__ = ("c", "b")
    D: tuple = (arb(0), arb(0), arb(0))

    def __init__(self, c: J, b: K, tighten: bool = True) -> None:
        self.c = c
        if tighten:
            D = P.D
            cg = (c.s, c.t, c.a)
            g = [(cg[i] + b.h[HIDX[i, 0]] * D[0] + b.h[HIDX[i, 1]] * D[1] + b.h[HIDX[i, 2]] * D[2]).intersection(b.g[i])
                 for i in range(3)]
            v = (c.v + g[0] * D[0] + g[1] * D[1] + g[2] * D[2]).intersection(b.v)
            b = K(v, g, b.h)
        self.b = b

    def __add__(self, o: object) -> "P":
        if isinstance(o, P):
            return P(self.c + o.c, self.b + o.b)
        return P(self.c + o, self.b + o, False)

    __radd__ = __add__

    def __sub__(self, o: object) -> "P":
        if isinstance(o, P):
            return P(self.c - o.c, self.b - o.b)
        return P(self.c - o, self.b - o, False)

    def __rsub__(self, o: object) -> "P":
        return P(o - self.c, o - self.b, False)

    def __neg__(self) -> "P":
        return P(-self.c, -self.b, False)

    def __mul__(self, o: object) -> "P":
        if isinstance(o, P):
            return P(self.c * o.c, self.b * o.b)
        return P(self.c * o, self.b * o, False)

    __rmul__ = __mul__

    def __truediv__(self, o: object) -> "P":
        if isinstance(o, P):
            return P(self.c / o.c, self.b / o.b)
        return P(self.c / o, self.b / o, False)

    def __rtruediv__(self, o: object) -> "P":
        return P(o / self.c, o / self.b)

    def sqrt(self) -> "P":
        return P(v1.sqrt_(self.c), self.b.sqrt())


def g_integrand(B: list, B1: list, B2: list, s: object) -> object | None:
    det = B[0] * B[2] - B[1] * B[1]
    T = B[0] + B[2]
    if not (bool(vv(det) > 0) and bool(vv(T) > 0)):
        return None
    T1 = B1[0] + B1[2]
    T2 = B2[0] + B2[2]
    det1 = B1[0] * B[2] + B[0] * B1[2] - 2 * B[1] * B1[1]
    det2 = B2[0] * B[2] + 2 * B1[0] * B1[2] + B[0] * B2[2] - 2 * (B1[1] * B1[1] + B[1] * B2[1])
    dl = sq(det)
    dl1 = det1 / (2 * dl)
    dl2 = det2 / (2 * dl) - det1 * det1 / (4 * dl * dl * dl)
    tau = sq(T + 2 * dl)
    u = T1 + 2 * dl1
    tau2 = (T2 + 2 * dl2) / (2 * tau) - u * u / (4 * tau * tau * tau)
    return s * s * tau2 / 4


def f3_ball(X: arb) -> tuple[arb, arb, arb]:
    """f, f', f'' over the ball X: centred forms, |f'''| <= 1/20, |f''''| <= 1/30 (|f^{(k)}| <= 1/((k+1)(k+2)))."""
    xc = arb(X.mid())
    r = arb(X.rad())
    f, f1, f2 = f_thin(xc)
    F = (f + arb(0, 1) * (f1.abs_upper() * r + r * r / 24)).intersection(arb(1, 1) / 4)
    F1 = (f1 + arb(0, 1) * (f2.abs_upper() * r + r * r / 40)).intersection(arb(0, 1) / 6)
    F2 = (f2 + arb(0, 1) * (r / 20)).intersection(arb(0, 1) / 12)
    return F, F1, F2


DEG = 16  # polynomial degree in r of a tail term besides the count (weight bound <= r^4, Hessian <= r^6, a-factor r^4)


def tail_bound(a_lo: arb, a_hi: arb, qmax: int, path: str, t0: arb) -> dict:
    """One bound T valid for EVERY jet component (value, 3 first, 6 second partials in (s, t', a)) of every entry of
    B, B', B'' restricted to the lattice tail m^2 + m l + l^2 >= qmax + 1, uniformly in kappa, |t| <= t0, a in
    [a_lo, a_hi]. Per lattice point and per entry: weight bound W (all partials of theta^2 f(s theta) up to order
    2 in (s, t'), using |f|, |f'|, |f''| <= 1/2, 1/6, 1/12, s <= 1, |theta| <= th, |beta| <= be), Hessian bound hb
    (H, H', H'' summed; n1_certify.tail_bounds), a-factor 1 + L + L^2, L = pi q_max + 4/a_lo (each hb term is
    e^{-pi a q} P(a), P of degree <= 4 in a with nonnegative coefficients). Shell sums and the geometric remainder
    as in n1_certify.tail_bounds (polynomials at the outer radius, Gaussians at the inner radius, ratio computed)."""
    smin, smax, d1, d2 = path_norms(path, t0)
    pa_hi = PI * a_hi
    k_hi = 4 * pa_hi * pa_hi
    cg = PI * a_lo * smin * smin
    r_tail = C * arb(qmax + 1).sqrt()
    delta = arb(1) / 4
    sq2 = arb(2).sqrt()
    acc = arb(0)
    K_ = 400
    last = rho = None
    for kk in range(K_ + 1):
        rin = r_tail + kk * delta
        rout = rin + delta
        cnt = PI * (rout + 1) ** 2
        th = 2 * PI * rout / C
        be = sq2 * th
        R, dR, ddR = smax * rout, d1 * rout, d2 * rout
        q1 = 2 * R * dR
        q2 = 2 * dR * dR + 2 * R * ddR
        M = k_hi * R * R + 2 * pa_hi
        M1 = 2 * k_hi * R * dR
        M2 = k_hi * (2 * ddR * R + 2 * dR * dR)
        hb = (-cg * rin * rin).exp() * (M + (pa_hi * q1 * M + M1)
                                        + ((pa_hi * pa_hi * q1 * q1 + pa_hi * q2) * M + 2 * pa_hi * q1 * M1 + M2))
        W = th ** 2 + th ** 3 + th ** 4 + 2 * th * be + th ** 2 * be + 2 * be ** 2 + 2 * th * be ** 2 \
            + th ** 2 * be ** 2 + th ** 2 * be + th ** 3 * be
        L = PI * R * R + 4 / a_lo
        term = cnt * W * hb * (1 + L + L * L)
        if kk < K_:
            acc += term
        else:
            last = term
            rho = ((rout + delta + 1) / (rout + 1)) ** 2 * ((rout + delta) / rout) ** DEG \
                * (-cg * (2 * rin * delta + delta * delta)).exp()
    if not bool(rho < 1):
        raise ValueError("tail ratio not < 1")
    return {"T": acc + last / (1 - rho), "rho_K": rho, "r_tail": r_tail}


class Model2:
    def __init__(self, a_lo: Fraction, a_hi: Fraction, t0: arb, qmax: int) -> None:
        ac = (a_lo + a_hi) / 2
        dl = (a_hi - a_lo) / 2
        self.a_c = arb(ac.numerator) / ac.denominator
        self.delta = arb(dl.numerator) / dl.denominator
        self.dA = arb(0, 1) * self.delta
        aball = v1.frac_ball(a_lo, a_hi)
        self.ns = lattice_half(qmax)
        tball = arb(0, 1) * t0
        z = arb(0)
        aJc = J(self.a_c, z, z, arb(1))
        aK = K(aball, [z, z, arb(1)], [z] * 6)
        self.Hc, self.Hb = [], []  # per n: 3 matrices x 3 entries x (v, a) at a_c / (v, a, aa) over the a-interval
        for (m, l) in self.ns:
            X0 = C * (m + HALF * l)
            Y0 = C * l * SQ3 / 2
            Rr = path_R("shear", X0, Y0, tball)
            hc = [[(x.v, x.a) for x in Hm] for Hm in hess_derivs(aJc, Rr)]
            hb = [[(x.v, x.g[2], x.h[5]) for x in Hm] for Hm in hess_derivs(aK, Rr)]
            # Taylor forms in a around a_c (Lagrange remainder): over the a-interval
            #   H(a) in H(a_c) + H_a(a_c)[-delta, delta] + hull(0, (delta^2/2) H_aa),  H_a(a) in H_a(a_c) + H_aa [-delta, delta]
            ht = []
            for Mc_, Mb_ in zip(hc, hb):
                row = []
                for (cv, ca), (bv, ba, baa) in zip(Mc_, Mb_):
                    tv = (cv + ca * self.dA + arb(0).union(self.delta * self.delta / 2 * baa)).intersection(bv)
                    ta = (ca + baa * self.dA).intersection(ba)
                    row.append((tv, ta, baa))
                ht.append(row)
            self.Hc.append(hc)
            self.Hb.append(ht)
        self.th = {0: [(PI * (m - l), 2 * PI * l) for (m, l) in self.ns],
                   1: [(PI * (l - m), 2 * PI * m) for (m, l) in self.ns]}
        a_lo_b = arb(a_lo.numerator) / a_lo.denominator
        a_hi_b = arb(a_hi.numerator) / a_hi.denominator
        self.tails = tail_bound(a_lo_b, a_hi_b, qmax, "shear", t0)
        self.T = arb(0, 1) * self.tails["T"]

    def centre(self, tri: int, s: arb, tt: arb) -> tuple[object, list] | None:
        """First-order jet (s, t', a) at the thin centre (s, t', a_c)."""
        acc = [[[arb(0), arb(0), arb(0), arb(0)] for _ in range(3)] for _ in range(3)]
        for (al, be), Hs in zip(self.th[tri], self.Hc):
            th = al + be * tt
            f0, f1, _ = f_thin(s * th)
            th2 = th * th
            wv = 2 * th2 * f0
            ws = 2 * th2 * th * f1
            wt = 4 * th * be * f0 + 2 * th2 * s * be * f1
            for M, Hm in zip(acc, Hs):
                for e, (hv, ha) in zip(M, Hm):
                    e[0] += wv * hv
                    e[1] += ws * hv
                    e[2] += wt * hv
                    e[3] += wv * ha
        mats = [[J(e[0] + self.T, e[1] + self.T, e[2] + self.T, e[3] + self.T) for e in M] for M in acc]
        g = g_integrand(mats[0], mats[1], mats[2], J(s, arb(1), arb(0), arb(0)))
        return (g, mats) if g is not None else None

    def ball(self, tri: int, s: arb, tt: arb, Mc: list) -> object | None:
        """Second-order jet over the cell ball x a-interval; values and gradients tightened by mean-value forms
        around the centre jet Mc (intersected with the naive enclosures)."""
        dS = arb(0, 1) * arb(s.rad())
        dT = arb(0, 1) * arb(tt.rad())
        dA = self.dA
        acc = [[[arb(0) for _ in range(10)] for _ in range(3)] for _ in range(3)]
        for (al, be), Hs in zip(self.th[tri], self.Hb):
            th = al + be * tt
            f0, f1, f2 = f3_ball(s * th)
            th2 = th * th
            wv = 2 * th2 * f0
            ws = 2 * th2 * th * f1
            wss = 2 * th2 * th2 * f2
            wt = 4 * th * be * f0 + 2 * th2 * s * be * f1
            wst = 6 * th2 * be * f1 + 2 * th2 * th * s * be * f2
            be2 = be * be
            wtt = 4 * be2 * f0 + 8 * th * be2 * s * f1 + 2 * th2 * s * s * be2 * f2
            for M, Hm in zip(acc, Hs):
                for e, (hv, ha, haa) in zip(M, Hm):
                    e[0] += wv * hv
                    e[1] += ws * hv
                    e[2] += wt * hv
                    e[3] += wv * ha
                    e[4] += wss * hv
                    e[5] += wst * hv
                    e[6] += ws * ha
                    e[7] += wtt * hv
                    e[8] += wt * ha
                    e[9] += wv * haa
        mats = []
        for M, Mrow in zip(acc, Mc):
            row = []
            for e, jc in zip(M, Mrow):
                e = [x + self.T for x in e]
                hss, hst, hsa, htt, hta, haa = e[4], e[5], e[6], e[7], e[8], e[9]
                gs = (jc.s + hss * dS + hst * dT + hsa * dA).intersection(e[1])
                gt = (jc.t + hst * dS + htt * dT + hta * dA).intersection(e[2])
                ga = (jc.a + hsa * dS + hta * dT + haa * dA).intersection(e[3])
                v = (jc.v + gs * dS + gt * dT + ga * dA).intersection(e[0])
                row.append(P(jc, K(v, [gs, gt, ga], [hss, hst, hsa, htt, hta, haa]), False))
            mats.append(row)
        if getattr(self, "ball_debug", False):
            print("B entries", [(x.b.v, x.b.g, x.b.h) for x in mats[0]])
        z = arb(0)
        P.D = (dS, dT, dA)
        sP = P(J(arb(s.mid()), arb(1), z, z), K(s, [arb(1), z, z], [z] * 6), False)
        return g_integrand(mats[0], mats[1], mats[2], sP)

    def cell(self, tri: int, s0: Fraction, t0_: Fraction, h: Fraction) -> dict:
        sc, tc = s0 + h / 2, t0_ + h / 2
        sca, tca = arb(sc.numerator) / sc.denominator, arb(tc.numerator) / tc.denominator
        ha = arb(h.numerator) / h.denominator
        sb, tb = sca + arb(0, 1) * ha / 2, tca + arb(0, 1) * ha / 2
        try:
            c = self.centre(tri, sca, tca)
            if c is None:
                return {"ok": False}
            gk = self.ball(tri, sb, tb, c[1])
        except (ValueError, ZeroDivisionError):
            return {"ok": False}
        if gk is None:
            return {"ok": False}
        gc = c[0]
        A = ha * ha
        hss, hst, hsa, htt, hta, haa = gk.b.h
        d = self.delta
        rem = (ha * ha / 24) * (hss + htt) + arb(0, 1) * ((ha * ha / 16) * hst.abs_upper()
                                                         + (d * ha / 4) * (hsa.abs_upper() + hta.abs_upper()))
        rem += arb(0).union(d * d / 2 * haa)
        out = {"ok": True, "Q": A * gc.v, "D": A * gc.a, "R": A * rem}
        for k in ("Q", "D", "R"):
            if not out[k].is_finite():
                return {"ok": False}
        return out


def integrate(model: Model2, N: int, tol: float, max_depth: int) -> dict:
    tot = {"Q": arb(0), "D": arb(0), "R": arb(0)}
    st = {"cells": 0, "refined": 0, "failed": 0}
    h0 = Fraction(1, N)
    stack = [(tri, Fraction(i, N), Fraction(j, N), h0, 0) for tri in (0, 1) for i in range(N) for j in range(N)]
    while stack:
        tri, s0, t0_, h, depth = stack.pop()
        r = model.cell(tri, s0, t0_, h)
        wide = (not r["ok"]) or bool(r["R"].rad() > tol * float(h * h))
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
            continue
        for k in tot:
            tot[k] += 2 * r[k]
    return {"tot": tot, "stats": st}


def main() -> None:
    out, N, t0_s, qmax, tol, depth = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), float(sys.argv[5]), \
        int(sys.argv[6])
    t0 = v1.q_arb(t0_s)
    shas = {}
    for fn in (__file__, v1.__file__):
        with open(fn, "rb") as fh:
            shas[os.path.basename(fn)] = hashlib.sha256(fh.read()).hexdigest()
    recs = []
    if os.path.exists(out):
        recs = json.load(open(out))
    specs = []
    for arg in sys.argv[7:]:
        specs += open(arg[1:]).read().split() if arg.startswith("@") else [arg]
    for spec in specs:
        lo_s, hi_s = spec.split(":")
        lo, hi = Fraction(lo_s), Fraction(hi_s)
        t_start = time.time()
        qm = qmax if qmax > 0 else max(6, math.ceil(20 / float(lo)))
        model = Model2(lo, hi, t0, qm)
        res = integrate(model, N, tol, depth)
        tot, st = res["tot"], res["stats"]
        ok = st["failed"] == 0
        F = tot["Q"] + tot["R"] + model.dA * tot["D"]
        sign = "pos" if (ok and bool(F > 0)) else ("neg" if (ok and bool(F < 0)) else "none")
        rec = {"engine": "n1_certify2", "path": "shear", "a_lo": str(lo), "a_hi": str(hi), "a_c": str((lo + hi) / 2),
               "delta": str((hi - lo) / 2), "N": N, "t0": t0_s, "qmax": qm, "tol": tol, "depth": depth,
               "n_lattice_half": len(model.ns), "ok": ok, "sign": sign,
               "Q": v1.ballrec(tot["Q"]) if ok else None, "D": v1.ballrec(tot["D"]) if ok else None,
               "R": v1.ballrec(tot["R"]) if ok else None, "Epp_window": v1.ballrec(F) if ok else None,
               "stats": {k: st[k] for k in ("cells", "refined", "failed")},
               "tail_T": float(model.tails["T"].upper()), "tail_rho_K": float(model.tails["rho_K"].upper()),
               "seconds": round(time.time() - t_start, 1), "python_flint": flint.__version__, "prec": ctx.prec,
               "script_sha256": shas}
        recs.append(rec)
        print(json.dumps({k: rec[k] for k in ("a_lo", "a_hi", "sign", "Q", "D", "R", "Epp_window", "stats", "seconds")}),
              flush=True)
        with open(out, "w") as fh:
            json.dump(recs, fh, indent=1)


if __name__ == "__main__":
    main()
