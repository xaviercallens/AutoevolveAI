"""Exact Python mirror of `lookup` (with the tail branch), `G`, and the inner loops of `bdsup`, `global_grid`,
`inside_hess` (grids.hpp, core.hpp:277-286), over the full table of dump2.txt. UNTRUSTED: it produces intermediate
states and lookup windows for the Lean chunks; its states at the C++ checkpoints are required to equal dump2.
"""
from __future__ import annotations

import bisect
import math

from l1common import ONE, Q, ZERO, add, div, inv, mul, neg, ofint, pow_, rat, sub

IV = tuple[int, int]


def hull(a: IV, b: IV) -> IV:
    return (min(a[0], b[0]), max(a[1], b[1]))


def sqrtI(a: IV) -> IV:
    assert a[0] > 0
    return (math.isqrt(a[0] * Q), math.isqrt(a[1] * Q) + 1)


def absI(a: IV) -> IV:
    if a[0] >= 0:
        return a
    if a[1] <= 0:
        return neg(a)
    return (0, max(-a[0], a[1]))


class Grid:
    def __init__(self, d) -> None:
        n = len(d.node)
        self.ts = [d.node[i][1] for i in range(n)]
        self.pts = [d.node[i][2] for i in range(n)]
        self.cels = [d.cell[i] for i in range(n - 1)]
        self.UIL = [t[0] for t in self.ts]
        self.VIL = [t[1] for t in self.ts]
        sc = d.sc
        self.lam, self.mu, self.eps, self.l = sc["lambda"], sc["mu"], sc["eps"], sc["l"]
        self.pi, self.bcons, self.K = sc["pi"], sc["bcons"], sc["K"]

    def rng(self, T: IV) -> tuple[int, int]:
        im = max(0, bisect.bisect_left(self.VIL, T[0]) - 1)
        ix = min(len(self.cels), bisect.bisect_right(self.UIL, T[1]))
        return im, ix

    def tail(self, T: IV) -> list[IV]:
        pb = mul(self.pi, self.bcons)
        return [sub(add(self.pts[-1][0], self.eps), mul(pb, sub(mul(T, T), mul(self.l, self.l)))),
                mul(mul(mul(ofint(-2), self.pi), self.bcons), T), mul(mul(ofint(-2), self.pi), self.bcons), ZERO, ZERO, ZERO]

    def lookup(self, T: IV, full: bool) -> list[IV]:
        out: list[IV] | None = None

        def addv(nx: list[IV]) -> None:
            nonlocal out
            out = nx if out is None else [hull(a, b) for a, b in zip(out, nx)]
        if T[1] >= self.l[0]:
            z = self.tail(T)
            addv(z if full else [z[0], z[3]])
        im, ix = self.rng(T)
        eps = self.eps
        for i in range(im, ix):
            if full:
                addv([add(c, eps) for c in self.cels[i]])
                continue
            H = sub(self.ts[i + 1], self.ts[i])
            aa = div(sub(T, self.ts[i]), H)
            xu, xv = max(0, aa[0]), min(Q, aa[1])
            if xu > xv:
                continue
            X = (xu, xv)
            fv = add(self.pts[i][0], mul(X, sub(self.pts[i + 1][0], self.pts[i][0])))
            ev = add(self.pts[i][3], mul(X, sub(self.pts[i + 1][3], self.pts[i][3])))
            er = div(mul(H, H), ofint(8))
            err = mul(absI(self.cels[i][2]), er)
            fv = add(fv, (-err[1], err[1]))
            err = mul(absI(self.cels[i][5]), er)
            ev = add(ev, (-err[1], err[1]))
            addv([add(fv, eps), add(ev, eps)])
        assert out is not None, "empty lookup"
        return out

    def T_of(self, d: IV, s: IV) -> IV:
        return sqrtI(add(mul(d, d), mul(s, s)))

    def Gs(self, d: IV, s: IV) -> IV:
        t2 = add(mul(d, d), mul(s, s))
        t = sqrtI(t2)
        f, e = self.lookup(t, False)
        A = div(d, t2)
        B = div(mul(neg(s), s), mul(d, t2))
        f = sub(sub(f, div(mul(self.lam, t2), ofint(2))), self.mu)
        return add(mul(A, f), mul(B, e))

    def Gf(self, d: IV, s: IV) -> list[IV]:
        lam, mu = self.lam, self.mu
        t2 = add(mul(d, d), mul(s, s))
        t = sqrtI(t2)
        f, fr, frr, e, er, err = self.lookup(t, True)
        A = div(d, t2)
        B = div(mul(neg(s), s), mul(d, t2))
        f = sub(sub(f, div(mul(lam, t2), ofint(2))), mu)
        fr = sub(fr, mul(lam, t))
        frr = sub(frr, lam)
        rdt, rst = div(d, t), div(s, t)
        rtdd = div(sub(ONE, mul(rdt, rdt)), t)
        rtss = div(sub(ONE, mul(rst, rst)), t)
        Ad = div(sub(ONE, div(mul(mul(ofint(2), d), d), t2)), t2)
        Bd = add(Ad, div(ONE, mul(d, d)))
        As = div(mul(mul(ofint(-2), A), s), t2)
        Bs = As
        t2c = pow_(t2, 3)
        Add = div(mul(mul(ofint(2), d), sub(mul(d, d), mul(mul(ofint(3), s), s))), t2c)
        Bdd = sub(Add, div(ofint(2), pow_(d, 3)))
        Ass = add(div(mul(ofint(-2), d), pow_(t2, 2)), div(mul(mul(mul(ofint(8), d), s), s), t2c))
        Bss = Ass
        g0 = add(mul(A, f), mul(B, e))
        g1 = add(add(add(mul(Ad, f), mul(mul(A, fr), rdt)), mul(Bd, e)), mul(mul(B, er), rdt))
        g2 = add(add(add(mul(As, f), mul(mul(A, fr), rst)), mul(Bs, e)), mul(mul(B, er), rst))
        g3 = add(add(add(add(add(mul(Add, f), mul(mul(mul(ofint(2), Ad), fr), rdt)),
                             mul(A, add(mul(mul(frr, rdt), rdt), mul(fr, rtdd)))), mul(Bdd, e)),
                     mul(mul(mul(ofint(2), Bd), er), rdt)), mul(B, add(mul(mul(err, rdt), rdt), mul(er, rtdd))))
        g4 = add(add(add(add(add(mul(Ass, f), mul(mul(mul(ofint(2), As), fr), rst)),
                             mul(A, add(mul(mul(frr, rst), rst), mul(fr, rtss)))), mul(Bss, e)),
                     mul(mul(mul(ofint(2), Bs), er), rst)), mul(B, add(mul(mul(err, rst), rst), mul(er, rtss))))
        return [g0, g1, g2, g3, g4]


def nsamp(aa: IV, bb: IV, h: IV) -> int:
    return max(1, -((-div(sub(bb, aa), h)[1]) // Q))


def gseq(a0: IV, b0: IV, m: int, i: int) -> IV:
    if i < m:
        return add(a0, mul(mul(sub(b0, a0), ofint(i)), inv(ofint(m))))
    return b0


def seq3(a: IV, b: IV, c: IV, e: IV, m1: int, m2: int, m3: int, i: int) -> IV:
    if i < m1:
        return gseq(a, b, m1, i)
    if i < m1 + m2:
        return gseq(b, c, m2, i - m1)
    return gseq(c, e, m3, i - m1 - m2)


DL, DU, SL, SU = rat(52528, 100000), rat(54930, 100000), rat(29420, 100000), rat(32621, 100000)
BD_DLO, BD_DUP, BD_SHI, BD_H = rat(28209, 100000), rat(697, 1000), rat(65, 100), rat(8, 10000)


def bd_d(nd: int, j: int) -> IV:
    hd = div(sub(BD_DUP, BD_DLO), ofint(nd))
    lo = add(BD_DLO, mul(hd, ofint(j)))
    return (lo[0], add(lo, hd)[1])


def bd_s(nsd: int, i: int) -> IV:
    hs = div(BD_SHI, ofint(nsd))
    slo = mul(hs, ofint(i))
    return (slo[0], add(slo, hs)[1])


def gg_step(G: Grid, d: IV, lo: IV, hi: IV, st: tuple[IV, IV, IV]) -> tuple[tuple[IV, IV, IV], IV]:
    g, drop, gmin = st
    h = sub(hi, lo)
    arg = mul(add(lo, hi), inv(ofint(2)))
    gv = mul(h, G.Gs(d, arg))
    g = add(g, gv)
    m = mul(neg(gv), inv(h))
    drop = add(drop, mul(h, (max(0, m[0]), max(0, m[1]))))
    needall = d[0] <= DL[1] or d[1] >= DU[0]
    if needall or hi[1] <= SL[1] or hi[0] >= SU[0]:
        value = sub(mul(ofint(2), g), G.K)
        if value[0] < gmin[0]:
            gmin = value
    return (g, drop, gmin), arg


def ih_step(G: Grid, d: IV, lsx: IV, usx: IV, st: tuple) -> tuple[tuple, IV]:
    init, fails, dd, dgl, glx, glxx, det = st
    sx = (lsx[0], usx[1])
    h = sub(usx, lsx)
    v = G.Gf(d, sx)
    xdi, xxi, sd2 = v[1], v[2], v[3]
    ddcc = add(dd, mul((0, h[1]), sd2))
    dd = add(dd, mul(h, sd2))
    if usx[0] >= SL[0]:
        dt = sub(mul(ddcc, xxi), mul(xdi, xdi))
        if not init:
            dgl, glx, glxx, det, init = ddcc, xdi, xxi, dt, True
        else:
            dgl, glx, glxx, det = hull(dgl, ddcc), hull(glx, xdi), hull(glxx, xxi), hull(det, dt)
        if ddcc[0] <= 0 or xxi[0] <= 0 or dt[0] <= 0:
            fails += 1
    return (init, fails, dd, dgl, glx, glxx, det), sx
