"""Joint repair LP (Tier X): at fixed radius d*, take the greedy cyclic chain of arcs of the current
state, allowing gaps, and solve   min sum_j g_j   s.t.  lo_{j+1} <= hi_j + g_j,  lo_j <= lo_{j+1},
lo_1 + 1 <= hi_m + g_m,  g >= 0   over all shifts jointly (velocities fixed).  Iterate.
Usage: gap_lp.py state.txt n rn rd out_state.txt [iters]"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"

import json
import sys

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cover_ls import union_complement  # noqa: E402
from search2 import Arcs  # noqa: E402


def uncovered(v: np.ndarray, s: np.ndarray, d: float) -> float:
    L, H = [], []
    for vi, si in zip(v, s):
        k = np.arange(int(vi))
        c = (k - si) / vi
        c = c - np.floor(c)
        L.append(c - d / vi)
        H.append(c + d / vi)
    a, b = union_complement(np.concatenate(L), np.concatenate(H))
    return float((b - a).sum())


def chain_with_gaps(A: Arcs, s: np.ndarray, d: float):
    lo, hi = A.bounds(s, d)
    m = (hi > -1.0) & (lo < 2.0)
    sel = np.nonzero(m)[0]
    lo, hi = lo[sel], hi[sel]
    o = np.argsort(lo, kind="stable")
    lo, hi, sel = lo[o], hi[o], sel[o]
    out = []
    # start: arc with lo <= 0 maximising hi
    cur = 0.0
    end = None
    j = 0
    best = -1
    while j < len(lo) and lo[j] <= cur:
        if best < 0 or hi[j] > hi[best]:
            best = j
        j += 1
    if best < 0:
        best = 0
    out.append(best)
    end = lo[best] + 1.0
    cur = hi[best]
    while cur < end:
        cand = -1
        jj = j
        while jj < len(lo) and lo[jj] <= cur:
            if hi[jj] > cur and (cand < 0 or hi[jj] > hi[cand]):
                cand = jj
            jj += 1
        j = max(j, jj) if cand >= 0 else j
        if cand < 0:
            # gap: next arc by lo after cur
            k = np.searchsorted(lo, cur, side="right")
            if k >= len(lo):
                break
            cand = int(k)
            # prefer, among arcs starting at the next start point, max hi
        out.append(cand)
        cur = max(cur, hi[cand])
    return [(int(A.i[sel[b]]), int(A.k[sel[b]])) for b in out]


def lp_gaps(v: np.ndarray, ch, d: float):
    n = len(v)
    m = len(ch)
    nv = n + m
    ii = np.array([c[0] for c in ch])
    kk = np.array([c[1] for c in ch], dtype=float)
    inv = 1.0 / v[ii]
    rows, rhs = [], []
    for j in range(m):
        jn = (j + 1) % m
        wrap = 1.0 if jn == 0 else 0.0
        r = np.zeros(nv)
        # (k_n - s_n - d)/v_n + wrap <= (k_j - s_j + d)/v_j + g_j
        r[ii[jn]] += -inv[jn]
        r[ii[j]] += inv[j]
        r[n + j] = -1.0
        rows.append(r)
        rhs.append(kk[j] * inv[j] + d * inv[j] - kk[jn] * inv[jn] + d * inv[jn] - wrap)
        if jn != 0:
            r2 = np.zeros(nv)
            # lo_j <= lo_jn : (k_j - s_j - d)/v_j <= (k_n - s_n - d)/v_n
            r2[ii[j]] += -inv[j]
            r2[ii[jn]] += inv[jn]
            rows.append(r2)
            rhs.append(kk[jn] * inv[jn] - d * inv[jn] - kk[j] * inv[j] + d * inv[j])
    c = np.zeros(nv)
    c[n:] = 1.0
    bnds = [(-3.0, 3.0)] * n + [(0.0, None)] * m
    bnds[0] = (None, None)
    res = linprog(c, A_ub=np.array(rows), b_ub=np.array(rhs), bounds=bnds, method="highs")
    if res.status != 0:
        return None, None
    return res.x[:n], float(res.fun)


def main() -> None:
    st, n, rn, rd, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    iters = int(sys.argv[6]) if len(sys.argv) > 6 else 30
    d = rn / rd
    rows = [ln.split() for ln in open(st).read().splitlines() if ln.strip()]
    v = np.array([float(r[0]) for r in rows])
    s = np.array([float(r[1]) for r in rows])
    A = Arcs(v)
    U = uncovered(v, s, d)
    hist = [U]
    for _ in range(iters):
        ch = chain_with_gaps(A, s, d)
        s2, obj = lp_gaps(v, ch, d)
        if s2 is None:
            break
        s2 = np.mod(s2, 1.0)
        U2 = uncovered(v, s2, d)
        hist.append(U2)
        if U2 < U - 1e-16:
            s, U = s2, U2
        else:
            break
        if U <= 1e-13:
            break
    with open(out, "w") as fh:
        for a, b in zip(v, s):
            fh.write(f"{int(a)} {b:.17g}\n")
    print(json.dumps({"state": os.path.basename(st), "U_history": hist, "final_U": U}))


if __name__ == "__main__":
    main()
