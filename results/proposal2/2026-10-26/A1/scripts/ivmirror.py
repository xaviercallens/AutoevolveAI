"""Exact Python mirror of the certificate's IV arithmetic (core.hpp) and of stage calcK (grids.hpp).

Used only to produce the per-chunk literals of the Lean calcK port (CalcK*.lean); every literal is re-derived by
the Lean kernel, and the final K is compared with the C++ dump, so this mirror is untrusted.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

Q = 2**144
IV = tuple[int, int]


def fq(a: int) -> int:
    return a // Q


def cq(a: int) -> int:
    return -((-a) // Q)


def ofint(n: int) -> IV:
    return (n * Q, n * Q)


def neg(a: IV) -> IV:
    return (-a[1], -a[0])


def add(a: IV, b: IV) -> IV:
    return (a[0] + b[0], a[1] + b[1])


def sub(a: IV, b: IV) -> IV:
    return add(a, neg(b))


def mul(a: IV, b: IV) -> IV:
    ps = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (fq(min(ps)), cq(max(ps)))


def inv(a: IV) -> IV:
    if a[0] > 0:
        return ((Q * Q) // a[1], -((-(Q * Q)) // a[0]))
    if a[1] < 0:
        return neg(inv(neg(a)))
    raise ZeroDivisionError("interval div0")


def div(a: IV, b: IV) -> IV:
    return mul(a, inv(b))


def rat(n: int, d: int) -> IV:
    return ((n * Q) // d, -((-(n * Q)) // d))


def sqrt(a: IV) -> IV:
    if a[0] <= 0:
        raise ValueError("nonpositive sqrt")
    return (math.isqrt(a[0] * Q), math.isqrt(a[1] * Q) + 1)


def hull(a: IV, b: IV) -> IV:
    return (min(a[0], b[0]), max(a[1], b[1]))


def absI(a: IV) -> IV:
    if a[0] >= 0:
        return a
    if a[1] <= 0:
        return neg(a)
    return (0, max(-a[0], a[1]))


ONE = ofint(1)


def pow_(x: IV, k: int) -> IV:
    z = ONE
    while k:
        if k & 1:
            z = mul(z, x)
        k >>= 1
        if k:
            x = mul(x, x)
    return z


@dataclass
class Table:
    ts: dict[int, IV]
    pts: dict[int, list[IV]]
    cels: dict[int, list[IV]]
    scal: dict[str, IV]


def load(dump: Path) -> Table:
    ts, pts, cels, scal = {}, {}, {}, {}
    for line in dump.read_text().splitlines():
        p = line.split()
        if p[0] == "node":
            nums = list(map(int, p[2:]))
            pr = [(nums[2 * k], nums[2 * k + 1]) for k in range(len(nums) // 2)]
            ts[int(p[1])], pts[int(p[1])] = pr[0], pr[1:]
        elif p[0] == "cell":
            nums = list(map(int, p[2:]))
            cels[int(p[1])] = [(nums[2 * k], nums[2 * k + 1]) for k in range(len(nums) // 2)]
        elif len(p) == 3:
            try:
                scal[p[0]] = (int(p[1]), int(p[2]))
            except ValueError:
                pass
    return Table(ts, pts, cels, scal)


def window_cells(tb: Table, T: IV) -> list[int]:
    """Cells i with ts[i+1].v >= T.u and ts[i].u <= T.v (equivalent to the C++ im..ix range on a sorted table)."""
    lo, hi = min(tb.cels), max(i for i in tb.cels if i + 1 in tb.ts)
    assert tb.ts[lo][1] < T[0] and tb.ts[hi + 1][0] > T[1], "window too small"
    return [i for i in range(lo, hi + 1) if tb.ts[i + 1][1] >= T[0] and tb.ts[i][0] <= T[1]]


def lookup_val(tb: Table, T: IV, cells: list[int]) -> tuple[IV, IV] | None:
    eps = tb.scal["eps"]
    out = None
    for i in cells:
        H = sub(tb.ts[i + 1], tb.ts[i])
        aa = div(sub(T, tb.ts[i]), H)
        xu, xv = max(0, aa[0]), min(Q, aa[1])
        if xu > xv:
            continue
        X = (xu, xv)
        fv = add(tb.pts[i][0], mul(X, sub(tb.pts[i + 1][0], tb.pts[i][0])))
        ev = add(tb.pts[i][3], mul(X, sub(tb.pts[i + 1][3], tb.pts[i][3])))
        er = div(mul(H, H), ofint(8))
        err = mul(absI(tb.cels[i][2]), er)
        fv = add(fv, (-err[1], err[1]))
        err = mul(absI(tb.cels[i][5]), er)
        ev = add(ev, (-err[1], err[1]))
        nxt = (add(fv, eps), add(ev, eps))
        out = nxt if out is None else (hull(out[0], nxt[0]), hull(out[1], nxt[1]))
    return out


def lookup_full(tb: Table, T: IV, cells: list[int]) -> list[IV] | None:
    eps = tb.scal["eps"]
    out = None
    for i in cells:
        z = [add(c, eps) for c in tb.cels[i]]
        out = z if out is None else [hull(a, b) for a, b in zip(out, z)]
    return out


def G_simple(tb: Table, d: IV, s: IV) -> IV:
    lam, mu = tb.scal["lambda"], tb.scal["mu"]
    t2 = add(mul(d, d), mul(s, s))
    t = sqrt(t2)
    fe = lookup_val(tb, t, window_cells(tb, t))
    assert fe is not None
    f = sub(sub(fe[0], div(mul(lam, t2), ofint(2))), mu)
    A = div(d, t2)
    B = div(mul(neg(s), s), mul(d, t2))
    return add(mul(A, f), mul(B, fe[1]))


def G_full(tb: Table, d: IV, s: IV) -> list[IV]:
    lam, mu = tb.scal["lambda"], tb.scal["mu"]
    t2 = add(mul(d, d), mul(s, s))
    t = sqrt(t2)
    v = lookup_full(tb, t, window_cells(tb, t))
    assert v is not None
    f, fr, frr, e, er, err = v
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
    j = -((-div(sub(bb, aa), h)[1]) // Q)
    return max(1, j)


def calcK(tb: Table) -> dict[str, object]:
    p, R = tb.scal["p"], tb.scal["R"]
    R2 = div(R, ofint(2))
    m = nsamp(ofint(0), R2, rat(1, 10000))
    h = div(R2, ofint(m))
    mh = nsamp(ofint(0), R2, rat(2, 10000))
    H = div(R2, ofint(mh))
    ss = ofint(0)
    hulls = []
    for i in range(mh):
        low, up = mul(ofint(i), H), mul(ofint(i + 1), H)
        dv = G_full(tb, p, (low[0], up[1]))[4]
        hulls.append(dv)
        ss = hull(ss, dv)
    terms = []
    kc = ofint(0)
    for i in range(m):
        val = G_simple(tb, p, mul(add(ofint(i), rat(1, 2)), h))
        terms.append(mul(h, val))
        kc = add(kc, terms[-1])
    er = div(mul(mul(pow_(h, 2), R2), absI(ss)), ofint(24))
    K = mul(ofint(2), add(kc, (-er[1], er[1])))
    return {"m": m, "mh": mh, "h": h, "H": H, "terms": terms, "hulls": hulls, "ss": ss, "kc": kc, "K": K}


if __name__ == "__main__":
    import sys
    tb = load(Path(sys.argv[1]))
    for k in range(8):
        h = tb.scal["calcK_h"]
        v = G_simple(tb, tb.scal["p"], mul(add(ofint(k), rat(1, 2)), h))
        assert v == tb.scal[f"Gs_val{k}"], k
    res = calcK(tb)
    print("m", res["m"], "mh", res["mh"], "K_match", res["K"] == tb.scal["K"])
