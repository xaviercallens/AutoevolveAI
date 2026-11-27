"""Exact gamma(v;s)=max_t min_i ||s_i+v_i t|| for rational shifts a_i/D.
Bisection with the exact open-cover checker, then exact evaluation of the local crossing near the last uncovered point,
then two exact confirmations: open cover FAILS at radius gamma, COVERS at gamma*(1+1e-9)."""
from __future__ import annotations

import math
import os
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../2026-11-07/SLR-EXT/code"))
from slr_exact import covers_open  # noqa: E402


def dist(x: Fr) -> Fr:
    f = x - math.floor(x)
    return min(f, 1 - f)


def F(v, a, D, t: Fr) -> Fr:
    return min(dist(Fr(ai, D) + vi * t) for vi, ai in zip(v, a))


def gamma_exact(v, a, D, hi: Fr):
    """hi must be a radius at which the open cover holds."""
    n = len(v)
    lo = Fr(0)
    bad_t = None
    assert covers_open(v, a, D, hi.numerator, hi.denominator)[0], "hi not covered"
    for _ in range(80):
        mid = Fr(round((lo + hi) / 2 * 10**15), 10**15)
        if mid <= lo or mid >= hi:
            break
        ok, M, bad = covers_open(v, a, D, mid.numerator, mid.denominator)
        if ok:
            hi = mid
        else:
            lo = mid
            bad_t = Fr(bad, M)
        if hi - lo < Fr(1, 10**13):
            break
    t0 = bad_t
    f0 = F(v, a, D, t0)
    S = [i for i in range(n) if dist(Fr(a[i], D) + v[i] * t0) <= f0 + Fr(1, 10**6)]
    cands = {t0}
    for ii, i in enumerate(S):
        for j in S[ii + 1:]:
            for w, rhs in ((v[i] - v[j], Fr(a[j] - a[i], D)), (v[i] + v[j], -Fr(a[i] + a[j], D))):
                if w == 0:
                    continue
                ww = abs(w)
                r = rhs if w > 0 else -rhs
                kk = round(t0 * ww - r)
                for k in range(kk - 2, kk + 3):
                    for off in (0, Fr(1, 2)):
                        c = (r + k + off) / ww
                        if abs(c - t0) < Fr(1, 10**5):
                            cands.add(c % 1)
    for i in S:
        k = round(t0 * v[i] + Fr(a[i], D) - Fr(1, 2))
        c = (Fr(1, 2) + k - Fr(a[i], D)) / v[i]
        if abs(c - t0) < Fr(1, 10**5):
            cands.add(c % 1)
    g = max(F(v, a, D, c) for c in cands)
    nc = covers_open(v, a, D, g.numerator, g.denominator)[0]
    up = g * (1 + Fr(1, 10**9))
    cv = covers_open(v, a, D, up.numerator, up.denominator)[0]
    return {"gamma": g, "open_cover_at_gamma": nc, "open_cover_above": cv, "bisect_gap": float(hi - lo),
            "ok": (not nc) and cv}


if __name__ == "__main__":
    import json
    c = json.load(open(sys.argv[1]))
    r = gamma_exact([int(x) for x in c["v"]], [int(x) for x in c["a"]], int(c["D"]),
                    Fr(c["delta_num"], c["delta_den"]) * Fr(21, 20))
    print(r["gamma"], float(r["gamma"]), r["ok"], r)
