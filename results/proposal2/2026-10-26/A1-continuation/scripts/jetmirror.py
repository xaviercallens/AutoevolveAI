"""Exact Python mirror of the certificate's jet type `J` and of `basis()` / `core_test` / `init_after_co`
(core.hpp:94-200, 268-298). UNTRUSTED: used to produce literals and to localise transcription errors; every value
that enters a Lean theorem is recomputed by the kernel, and the mirror itself is checked against dump2.txt.

Association order follows the C++ overloads exactly (left-associative `*` and `/`; `IV*J` is `J*IV`; `x/y` is
`x * y.inv()`; additions are exact, so their order is irrelevant).
"""
from __future__ import annotations

from math import comb as comb_c

from l1common import (ONE, ZERO, add, inv, mul, neg, ofint, pow_, rat, sub)

IV = tuple[int, int]
Jet = tuple[IV, IV, IV, IV]
M = 38
KS = [6] + [6 * m for m in range(1, M + 1)]


def iszero(a: IV) -> bool:
    return a[0] == 0 and a[1] == 0


def absI(a: IV) -> IV:
    if a[0] >= 0:
        return a
    if a[1] <= 0:
        return neg(a)
    return (0, max(-a[0], a[1]))


def mid(a: IV) -> IV:
    s = a[0] + a[1]
    return (s // 2, -((-s) // 2))


def sqrtI(a: IV) -> IV:
    import math
    from l1common import Q
    assert a[0] > 0
    return (math.isqrt(a[0] * Q), math.isqrt(a[1] * Q) + 1)


class Ctx:
    """Constants of the run (C++ globals): ln2, pi, p, R, co[1..38]."""

    def __init__(self, sc: dict[str, IV]):
        self.ln2, self.pi, self.p, self.R, self.a = sc["ln2"], sc["pi"], sc["p"], sc["R"], sc["a"]
        self.co = [ZERO] + [sc[f"co{m}"] for m in range(1, M + 1)]
        self.v = rat(75, 1000)
        self.cut = rat(6, 100)
        self.small = sub(self.p, self.cut)
        R = self.R
        self.breaks = [rat(28209, 100000), self.small, self.p, R, add(R, rat(1, 1000)), add(R, self.v), add(R, rat(76, 1000))]
        self.init_after_co()

    # IV log (core.hpp:85-93)
    def logI(self, a: IV) -> IV:
        from l1common import Q
        assert a[0] > 0
        x, n = a, 0
        while x[0] < Q // 4:
            x = mul(x, ofint(2))
            n -= 1
        while x[1] > Q:
            x = mul(x, inv(ofint(2)))
            n += 1
        assert not (x[0] < Q // 4 or x[1] > Q)
        z = mul(sub(x, ONE), inv(add(x, ONE)))
        out, z2, vv = ZERO, mul(z, z), z
        for i in range(200):
            out = add(out, mul(vv, inv(ofint(2 * i + 1))))
            vv = mul(vv, z2)
        return add(add(mul(ofint(2), out), (-1, 1)), mul(ofint(n), self.ln2))

    def init_after_co(self) -> None:
        p, R, co = self.p, self.R, self.co
        self.uR = sub(mul(R, R), mul(p, p))
        self.alp, self.beta, self.VR, self.edge, self.Tp0, self.Tp1, self.Tp2 = [], [], [], [], [], [], []
        for i in range(1, M + 1):
            c, k = co[i], KS[i]
            vals, qc, sc, edge = [], [], [], []
            for j in range(k // 2 + 1):
                z = mul(rat((-1 if j % 2 else 1) * comb_c(k, 2 * j)), pow_(p, k - 2 * j))
                vals.append(z)
                edge.append(mul(c, z))
                if j >= 1:
                    qc.append(mul(ofint(j), z))
                if j >= 2:
                    sc.append(mul(ofint(j * (j - 1)), z))
            xx, qq, ss = horI(self.uR, vals), horI(self.uR, qc), horI(self.uR, sc)
            self.VR.append(mul(c, xx))
            self.alp.append(mul(mul(mul(c, ofint(2)), R), qq))
            self.beta.append(mul(c, add(mul(mul(mul(ofint(4), R), R), ss), mul(ofint(2), qq))))
            self.edge.append(edge)
            t0 = mul(c, pow_(p, k))
            self.Tp0.append(t0)
            self.Tp1.append(mul(mul(t0, ofint(-k * (k - 1))), inv(p)))
            self.Tp2.append(mul(mul(mul(mul(t0, ofint(k)), ofint(k - 1)), sub(rat((k - 2) * (k - 3), 6), rat(1, 2))), inv(mul(p, p))))
        pi = self.pi
        lr = self.logI(R)
        self.b0c = add(neg(lr), mul(mul(mul(pi, inv(ofint(2))), R), R))       # -R.log()+pi/2*R*R
        self.cR1 = add(mul(ofint(-1), inv(R)), mul(pi, R))                    # -1/R+pi*R
        self.cR2 = add(mul(ofint(1), inv(mul(R, R))), pi)                     # 1/(R*R)+pi
        self.pi2 = mul(pi, inv(ofint(2)))                                     # pi/2

    # ---------------- jets ----------------
    def jlog(self, a: Jet) -> Jet:
        iz = jinv(a)
        y = [self.logI(a[0]), ZERO, ZERO, ZERO]
        for n in range(1, 4):
            s = ZERO
            for k in range(1, n + 1):
                s = add(s, mul(mul(ofint(k), a[k]), iz[n - k]))
            y[n] = mul(s, inv(ofint(n)))
        return tuple(y)

    def basis(self, t: Jet, seg: int) -> tuple[Jet, list[Jet]]:
        pi, R, p = self.pi, self.R, self.p
        g = jadd(jneg(self.jlog(t)), jmul(jmuli(t, self.pi2), t))
        Pr = Qr = None
        if seg < 3:
            b0 = g
        elif seg < 5:
            Pr, Qr = self.PQt(jaddi(t, neg(R)))
            b0 = jadd(jaddi(jmuli(Pr, self.cR1), self.b0c), jmuli(Qr, self.cR2))
        else:
            b0 = jc(self.b0c)
        bm = [JZ] * M
        if seg < 1:
            pass
        elif seg == 1:
            h = jaddi(t, neg(p))
            bm = [jadd(jaddi(jmuli(h, self.Tp1[i]), self.Tp0[i]), jmul(jmuli(h, self.Tp2[i]), h)) for i in range(M)]
        elif seg == 2:
            z = jaddi(jmul(t, t), neg(mul(p, p)))
            bm = [horJ(z, self.edge[i]) for i in range(M)]
        elif seg < 5:
            bm = [jadd(jaddi(jmuli(Pr, self.alp[i]), self.VR[i]), jmuli(Qr, self.beta[i])) for i in range(M)]
        else:
            bm = [jc(self.VR[i]) for i in range(M)]
        cu = sm(jmuli(jaddi(t, neg(self.small)), inv(self.cut)), 0 if seg == 1 else (-1 if seg < 1 else 1))
        gc = sm(jmuli(jaddi(t, neg(R)), inv(rat(10, 100))), 0 if 3 <= seg <= 6 else (-1 if seg < 3 else 1))
        cer = sm(jmuli(jaddi(jaddi(t, neg(R)), neg(rat(1, 1000))), inv(rat(75, 1000))), 0 if seg in (4, 5) else (-1 if seg < 4 else 1))
        one_gc = jaddi(jneg(gc), ONE)
        mm = []
        for i in range(M):
            bm[i] = jmul(cu, bm[i])
            sgn = -1 if (i + 1) % 2 else 1
            mm.append(jmul(jmuli(jpow(t, KS[i + 1]), mul(self.co[i + 1], ofint(sgn))), one_gc))
        smm, sbm = JZ, JZ
        for i in range(M):
            smm = jadd(smm, mm[i])
            sbm = jadd(sbm, bm[i])
        D = [JZ] * (M + 1)
        if seg < 4:
            if seg >= 3:
                D[0] = jsub(b0, g)
            for i in range(M):
                D[i + 1] = jsub(bm[i], mm[i])
            return jadd(g, smm), D
        if seg >= 6:
            return jadd(b0, sbm), D
        D[0] = jsub(b0, g)
        sd = D[0]
        for i in range(M):
            D[i + 1] = jsub(bm[i], mm[i])
            sd = jadd(sd, D[i + 1])
        one_cer = jaddi(jneg(cer), ONE)
        D = [jmul(one_cer, d) for d in D]
        return jadd(jadd(g, smm), jmul(cer, sd)), D

    def PQt(self, t: Jet) -> tuple[Jet, Jet]:
        v = self.v
        h = jmuli(t, inv(v))
        P = jmuli(cpol(h, [ZERO, ONE, ZERO, rat(-6), rat(8), rat(-3)]), v)
        Qc = mul(mul(v, v), inv(ofint(2)))
        Qq = jmuli(cpol(h, [ZERO, ZERO, ONE, rat(-3), rat(3), neg(ONE)]), Qc)
        return P, Qq

    def tt_z(self, seg: int, j: int, n: int) -> tuple[Jet, Jet]:
        aa, bb = self.breaks[seg], self.breaks[seg + 1]
        w = sub(bb, aa)
        lo = add(aa, mul(mul(w, ofint(j)), inv(ofint(n))))
        hi = add(aa, mul(mul(w, ofint(j + 1)), inv(ofint(n))))
        tt = ((lo[0], hi[1]), ONE, ZERO, ZERO)
        return tt, jaddi(jmul(tt, tt), neg(mul(self.p, self.p)))

    def hor_modes(self, z: Jet) -> list[Jet]:
        return [horJ(z, self.edge[i]) for i in range(M)]

    def core_cell(self, seg: int, j: int, n: int) -> tuple[IV, IV, IV]:
        aa, bb = self.breaks[seg], self.breaks[seg + 1]
        w = sub(bb, aa)
        lo = add(aa, mul(mul(w, ofint(j)), inv(ofint(n))))
        hi = add(aa, mul(mul(w, ofint(j + 1)), inv(ofint(n))))
        tt = ((lo[0], hi[1]), ONE, ZERO, ZERO)
        b, D = self.basis(tt, seg)
        bi = jadd(jder(b), jmuli(jinv(tt), ONE))
        norm = add(add(absI(bi[0]), absI(bi[1])), absI(bi[2]))
        dsm, sm2 = ZERO, ZERO
        for i in range(M + 1):
            v1 = ZERO
            for x in D[i]:
                v1 = add(v1, absI(x))
            dsm = add(dsm, mul(pow_(ofint(KS[i] + 1), 3), v1))
            sm2 = add(sm2, mul(pow_(ofint(KS[i] + 1), 2), v1))
        return norm, dsm, sm2


JZ: Jet = (ZERO, ZERO, ZERO, ZERO)


def jc(a: IV) -> Jet:
    return (a, ZERO, ZERO, ZERO)


def jneg(a: Jet) -> Jet:
    return tuple(neg(x) for x in a)


def jadd(a: Jet, b: Jet) -> Jet:
    return tuple(add(x, y) for x, y in zip(a, b))


def jsub(a: Jet, b: Jet) -> Jet:
    return jadd(a, jneg(b))


def jaddi(a: Jet, b: IV) -> Jet:
    return (add(a[0], b), a[1], a[2], a[3])


def jmul(a: Jet, b: Jet) -> Jet:
    z = []
    for k in range(4):
        s = ZERO
        for j in range(k + 1):
            s = add(s, mul(a[j], b[k - j]))
        z.append(s)
    return tuple(z)


def jmuli(a: Jet, b: IV) -> Jet:
    return tuple(mul(x, b) for x in a)


def jinv(a: Jet) -> Jet:
    h = inv(a[0])
    z = [h, ZERO, ZERO, ZERO]
    for i in range(1, 4):
        ss = ZERO
        for j in range(1, i + 1):
            ss = add(ss, mul(a[j], z[i - j]))
        z[i] = mul(neg(ss), h)
    return tuple(z)


def jpow(a: Jet, k: int) -> Jet:
    if k < 0:
        return jinv(jpow(a, -k))
    if iszero(a[2]) and iszero(a[3]):
        z = [ZERO] * 4
        for j in range(4):
            if j > k:
                break
            c = 1
            for i in range(j):
                c = c * (k - i) // (i + 1)
            z[j] = mul(mul(pow_(a[0], k - j), pow_(a[1], j)), rat(c))
        return tuple(z)
    v, x = jc(ONE), a
    while k:
        if k & 1:
            v = jmul(v, x)
        k >>= 1
        if k:
            x = jmul(x, x)
    return v


def jsqrt(a: Jet) -> Jet:
    y = [sqrtI(a[0]), ZERO, ZERO, ZERO]
    for j in range(1, 4):
        ss = ZERO
        for t in range(1, j):
            ss = add(ss, mul(y[t], y[j - t]))
        y[j] = mul(sub(a[j], ss), inv(mul(ofint(2), y[0])))
    return tuple(y)


def jder(a: Jet) -> Jet:
    return (a[1], mul(ofint(2), a[2]), mul(ofint(3), a[3]), ZERO)


def horI(x: IV, coeff: list[IV]) -> IV:
    z = ZERO
    for c in reversed(coeff):
        z = add(mul(z, x), c)
    return z


def horJ(x: Jet, coeff: list[IV]) -> Jet:
    z = JZ
    for c in reversed(coeff):
        z = jaddi(jmul(z, x), c)
    return z


def cpol(t: Jet, coeff: list[IV]) -> Jet:
    m = mid(t[0])
    h = jaddi(t, neg(m))
    cc = [ZERO] * len(coeff)
    for j in range(len(coeff)):
        for ll in range(j, len(coeff)):
            cc[j] = add(cc[j], mul(mul(rat(comb_c(ll, j)), coeff[ll]), pow_(m, ll - j)))
    z = jc(ZERO)
    for c in reversed(cc):
        z = jaddi(jmul(z, h), c)
    return z


def sm(t: Jet, seg: int) -> Jet:
    if seg < 0:
        return jc(ZERO)
    if seg > 0:
        return jc(ONE)
    return cpol(t, [ZERO, ZERO, ZERO, rat(10), rat(-15), rat(6)])


# ---------------- table stage: dels, propagation step, solve, fh (core.hpp:144, 223-266) ----------------

def integ(H: IV, y: Jet, yc: Jet) -> IV:
    err = mul(mul(pow_(H, 3), absI(yc[2])), inv(ofint(12)))
    return add(mul(H, y[0]), (-err[1], err[1]))


def tdels(ctx: "Ctx", t: Jet, seg: int, b: Jet | None = None) -> tuple[Jet, Jet, Jet]:
    if b is None:
        b = ctx.basis(t, seg)[0]
    bp = jadd(jder(b), jmuli(jinv(t), ONE))
    return jmul(t, b), jadd(jmuli(bp, ofint(-2)), jmul(jpow(bp, 2), t)), bp


KEYS = [6 * m for m in range(1, M + 1)]


def prop_step(ctx: "Ctx", old: IV, x: IV, S: tuple, sgprev: int, bm: Jet | None = None, bc: Jet | None = None) -> tuple[tuple, tuple]:
    """(ns, bs) of core.hpp:254-259; S = (s1, s2, [ps_k for k in KEYS]). bm, bc: optional basis values at tm, tc."""
    s1, s2, ps = S
    H = sub(x, old)
    md = mul(add(old, x), inv(ofint(2)))
    tc = ((old[0], x[1]), ONE, ZERO, ZERO)
    tm = (md, ONE, ZERO, ZERO)
    zm = tdels(ctx, tm, sgprev, bm)
    zc = tdels(ctx, tc, sgprev, bc)
    ns1 = add(s1, integ(H, zm[0], zc[0]))
    ns2 = add(s2, integ(H, zm[1], zc[1]))
    ix = inv(x)
    nps = []
    for k, v in zip(KEYS, ps):
        nps.append(add(mul(pow_(mul(old, ix), k), v), integ(H, jmul(jpow(jmuli(tm, ix), k), zm[2]), jmul(jpow(jmuli(tc, ix), k), zc[2]))))
    a0 = zc[2][0]
    bb = max(abs(a0[0]), abs(a0[1]))
    err = mul(H, (-bb, bb))
    bs1 = add(s1, mul((0, H[1]), zc[0][0]))
    bs2 = add(s2, mul((0, H[1]), zc[1][0]))
    itc = inv(tc[0])
    bps = [add(mul(pow_(mul(old, itc), k), v), err) for k, v in zip(KEYS, ps)]
    return (ns1, ns2, nps), (bs1, bs2, bps)


def solve(val: IV, der) -> Jet:
    z = [val, ZERO, ZERO, ZERO]
    for i in range(3):
        z[i + 1] = mul(der(tuple(z))[i], inv(ofint(i + 1)))
    return tuple(z)


def fh_solve(ctx: "Ctx", t: Jet, B: Jet, S: tuple) -> tuple[Jet, Jet, list[Jet]]:
    B1 = jadd(jder(B), jmuli(jinv(t), ONE))
    tB = jmul(t, B)
    s1 = solve(S[0], lambda _z: tB)
    d2 = jadd(jmuli(B1, ofint(-2)), jmul(jpow(B1, 2), t))
    s2 = solve(S[1], lambda _z: d2)
    it = jinv(t)
    ps = []
    for k, v in zip(KEYS, S[2]):
        ps.append(solve(v, lambda F, k=k: jsub(B1, jmul(jmuli(F, ofint(k)), it))))
    return s1, s2, ps


def qj_list(t: Jet, D: list[Jet]) -> list[Jet]:
    return [jsub(jmul(t, jder(D[i])), jmuli(D[i], ofint(KS[i]))) for i in range(M + 1)]


def qe_rows(t: Jet, D: list[Jet], i0: int, i1: int) -> tuple[Jet, Jet]:
    """Σ over pairs (i, j), i0 <= i < i1, i <= j of the quad and e summands (fh, core.hpp:234)."""
    Qj = qj_list(t, D)
    quad, e = JZ, JZ
    for i in range(i0, i1):
        for j in range(i, M + 1):
            mult = 1 if i == j else 2
            ki, kj = KS[i], KS[j]
            quad = jadd(quad, jmuli(jmul(jmuli(D[i], ofint(mult * ki * kj)), D[j]), inv(ofint(ki + kj))))
            e = jadd(e, jmuli(jmul(jmuli(Qj[i], ofint(mult)), Qj[j]), inv(ofint(ki + kj))))
    return quad, e


def fh_final(ctx: "Ctx", t: Jet, D: list[Jet], ss: tuple, quad: Jet, e: Jet) -> list[IV]:
    s1, s2, ps = ss
    psd = {k: v for k, v in zip(KEYS, ps)}
    dsum, lin = JZ, JZ
    for i in range(M + 1):
        dsum = jadd(dsum, jmuli(D[i], inv(ofint(KS[i] + 2))))
        lin = jadd(lin, jadd(jmuli(D[i], ofint(-2)), jmul(jmuli(D[i], ofint(2 * KS[i])), psd[KS[i]])))
    f = jsub(jmuli(jadd(s1, jmul(jmul(t, t), dsum)), mul(ofint(-2), ctx.pi)),
             jmuli(jadd(jadd(jadd(ctx.jlog(t), s2), lin), quad), rat(1, 2)))
    e = jmuli(e, rat(1, 2))
    return [f[0], f[1], mul(ofint(2), f[2]), e[0], e[1], mul(ofint(2), e[2])]


def fh0(ctx: "Ctx", t: Jet) -> list[IV]:
    f = jsub(jmul(jaddi(jmul(jmuli(t, ctx.pi), t), neg(rat(1, 2))), ctx.jlog(t)),
             jmuli(jpow(t, 4), mul(mul(rat(3, 8), ctx.pi), ctx.pi)))
    return [f[0], f[1], mul(ofint(2), f[2]), ZERO, ZERO, ZERO]


def fh(ctx: "Ctx", t: Jet, seg: int, S: tuple | None) -> list[IV]:
    if seg == 0 and S is None:
        return fh0(ctx, t)
    B, D = ctx.basis(t, seg)
    ss = fh_solve(ctx, t, B, S)
    quad, e = qe_rows(t, D, 0, M + 1)
    return fh_final(ctx, t, D, ss, quad, e)


def ss0_A0(ctx: "Ctx", t: IV) -> tuple:
    """Order-0 coefficients of ss0(J(t)) (core.hpp:206-222) computed with intervals."""
    ek = [2] + KS[1:]
    bv = [ctx.pi] + [mul(mul(ofint(-1 if i % 2 else 1), ctx.co[i]), ofint(KS[i])) for i in range(1, M + 1)]
    s2c: dict[int, IV] = {}
    for i in range(len(ek)):
        s2c[ek[i]] = add(s2c.get(ek[i], ZERO), mul(mul(ofint(-2), bv[i]), inv(ofint(ek[i]))))
        for j in range(len(ek)):
            e = ek[i] + ek[j]
            s2c[e] = add(s2c.get(e, ZERO), mul(mul(bv[i], bv[j]), inv(ofint(e))))
    P = [ONE]
    for _ in range(1, 12 * M + 1):
        P.append(mul(P[-1], t))
    s1 = add(mul(mul(mul(t, t), inv(ofint(2))), add(neg(ctx.logI(t)), rat(1, 2))), mul(P[4], mul(ctx.pi, inv(ofint(8)))))
    for i in range(1, M + 1):
        s1 = add(s1, mul(P[KS[i] + 2], mul(mul(ofint(-1 if i % 2 else 1), ctx.co[i]), inv(ofint(KS[i] + 2)))))
    s2 = ZERO
    for e in sorted(s2c):
        s2 = add(s2, mul(P[e], s2c[e]))
    ps = []
    for k in KEYS:
        v = ZERO
        for i in range(len(ek)):
            v = add(v, mul(P[ek[i]], mul(bv[i], inv(ofint(ek[i] + k)))))
        ps.append(v)
    return s1, s2, ps
