"""Search v2 (float heuristic, Tier X): vectorised chain-LP descent + continuation in n.

Untrusted.  Every candidate is rounded to s = a/D and must pass checker 1
(slr_exact.covers_open) and checker 2 (check_cover, C) before a certificate is kept.

Continuation: the best shifts for v of size n-1 are extended by one runner with
velocity n; the new shift is chosen on a grid, then the whole vector is
re-optimised by chain-LP descent with diversified chains and iterated kicks.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"

import argparse
import json
import math
import random
import subprocess
import sys
import time
from fractions import Fraction
from typing import Sequence

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from slr_exact import covers_open  # noqa: E402

C_CHECKER = os.path.join(HERE, "check_cover")


class Arcs:
    """Arc index structure for velocity vector v (all lifts with centres in a 3-period window)."""

    def __init__(self, v: np.ndarray):
        self.v = v
        idx, ks = [], []
        for i, vi in enumerate(v):
            k = np.arange(-int(vi) - 1, 2 * int(vi) + 2)
            idx.append(np.full(len(k), i))
            ks.append(k)
        self.i = np.concatenate(idx)
        self.k = np.concatenate(ks).astype(float)
        self.vi = v[self.i]

    def bounds(self, s: np.ndarray, delta: float):
        c = (self.k - s[self.i]) / self.vi
        h = delta / self.vi
        return c - h, c + h


def covers(A: Arcs, s: np.ndarray, delta: float) -> bool:
    lo, hi = A.bounds(s, delta)
    m = (hi > -0.5) & (lo < 1.5)
    lo, hi = lo[m], hi[m]
    o = np.argsort(lo, kind="stable")
    lo, hi = lo[o], hi[o]
    cm = np.maximum.accumulate(hi)
    # need coverage of [0, 1]: first arc with lo < 0 ... ; check no gap inside [0,1]
    # gaps occur where lo[j+1] >= cm[j]
    j0 = np.searchsorted(lo, 0.0, side="left")  # arcs with lo < 0 are indices < j0
    if j0 == 0 or cm[j0 - 1] <= 0.0:
        return False
    gaps = lo[1:] >= cm[:-1]
    # positions of gaps that lie within [0, 1]
    gpos = cm[:-1][gaps]
    return not np.any((gpos >= 0.0) & (gpos <= 1.0)) and cm[-1] > 1.0


def gap(A: Arcs, s: np.ndarray, lo_d: float = 0.0, hi_d: float = 0.5, tol: float = 1e-12) -> float:
    lo, hi = lo_d, hi_d
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if covers(A, s, mid):
            hi = mid
        else:
            lo = mid
    return hi


def chain(A: Arcs, s: np.ndarray, delta: float, t0: float = 0.0):
    lo, hi = A.bounds(s, delta)
    m = (hi > t0 - 1.0) & (lo < t0 + 2.0)
    sel = np.nonzero(m)[0]
    lo, hi = lo[sel], hi[sel]
    o = np.argsort(lo, kind="stable")
    lo, hi, sel = lo[o], hi[o], sel[o]
    cm = np.maximum.accumulate(hi)
    am = np.zeros(len(hi), dtype=int)
    best = -1
    bv = -np.inf
    for j in range(len(hi)):  # argmax prefix
        if hi[j] > bv:
            bv = hi[j]
            best = j
        am[j] = best
    out = []
    cur = t0
    end = None
    for _ in range(10 * len(A.v) + 200):
        j = np.searchsorted(lo, cur, side="left") - 1  # lo < cur strictly
        if j < 0:
            return None
        if cm[j] <= cur:
            return None
        b = am[j]
        out.append((int(A.i[sel[b]]), int(A.k[sel[b]])))
        if end is None:
            end = lo[b] + 1.0
        cur = cm[j]
        if cur > end:
            return out
    return None


def lp_on_chain(v: np.ndarray, ch, fix: int = 0):
    n = len(v)
    m = len(ch)
    nv = n + 1
    ii = np.array([c[0] for c in ch])
    kk = np.array([c[1] for c in ch], dtype=float)
    inv = 1.0 / v[ii]
    # lo_j = (k_j - s_ij - d)/v ; hi_j = (k_j - s_ij + d)/v
    rows = []
    rhs = []
    for j in range(m):
        jn = (j + 1) % m
        wrap = 1.0 if jn == 0 else 0.0
        r = np.zeros(nv)
        # lo_{jn} + wrap <= hi_j :  (k_n - s_n - d)/v_n + wrap <= (k_j - s_j + d)/v_j
        r[ii[jn]] += -inv[jn]
        r[n] += -inv[jn]
        r[ii[j]] += inv[j]
        r[n] += -inv[j]
        rows.append(r)
        rhs.append(kk[j] * inv[j] - kk[jn] * inv[jn] - wrap)
        if jn != 0:
            r2 = np.zeros(nv)
            # lo_j <= lo_{jn}
            r2[ii[j]] += -inv[j]
            r2[n] += -inv[j]
            r2[ii[jn]] += inv[jn]
            r2[n] += inv[jn]
            rows.append(r2)
            rhs.append(kk[jn] * inv[jn] - kk[j] * inv[j])
    c = np.zeros(nv)
    c[n] = 1.0
    bnds = [(-3.0, 3.0)] * n + [(0.0, 0.5)]
    bnds[fix] = (0.0, 0.0)
    res = linprog(c, A_ub=np.array(rows), b_ub=np.array(rhs), bounds=bnds, method="highs")
    if res.status != 0:
        return None, None
    return res.x[:n], float(res.x[n])


def descend(A: Arcs, s: np.ndarray, rng: random.Random, patience: int = 10, d: float | None = None):
    if d is None:
        d = gap(A, s)
    fails = 0
    while fails <= patience:
        if fails == 0:
            alpha, t0 = 1e-9, 0.0
        else:
            alpha = rng.choice([1e-6, 0.01, 0.03, 0.07, 0.15, 0.3])
            t0 = rng.random()
        ch = chain(A, s, d * (1 + alpha) + 1e-13, t0=t0)
        if ch is None:
            fails += 1
            continue
        s2, _ = lp_on_chain(A.v, ch)
        if s2 is None:
            fails += 1
            continue
        s2 = np.mod(s2, 1.0)
        d2 = gap(A, s2, 0.0, min(0.5, d * 1.5))
        if d2 < d - 1e-12:
            s, d = s2, d2
            fails = 0
        else:
            fails += 1
    return s, d


def ils(A: Arcs, s: np.ndarray, d: float, rng: random.Random, budget: float, stop_below: float | None):
    t0 = time.process_time()
    n = len(A.v)
    best_s, best_d = s.copy(), d
    while time.process_time() - t0 < budget:
        if stop_below is not None and best_d < stop_below:
            break
        c = best_s.copy()
        r = rng.random()
        if r < 0.4:
            for _ in range(rng.randint(1, max(1, n // 8))):
                c[rng.randrange(n)] = rng.random()
        elif r < 0.8:
            c = np.mod(c + np.array([rng.gauss(0, rng.choice([0.002, 0.01, 0.03]) ) for _ in range(n)]), 1.0)
        else:
            j = rng.randrange(n)
            c[j] = np.mod(c[j] + rng.gauss(0, 0.05), 1.0)
        s2, d2 = descend(A, c, rng)
        if d2 < best_d - 1e-12:
            best_s, best_d = s2, d2
    return best_s, best_d


def extend(A: Arcs, s_prev: np.ndarray, rng: random.Random, grid: int, keep: int):
    """Append a runner (last velocity of A.v) to s_prev; choose its shift on a grid; descend the best few."""
    cands = []
    for g in range(grid):
        sn = (g + rng.random()) / grid
        s = np.append(s_prev, sn)
        cands.append((gap(A, s, tol=1e-9), sn))
    cands.sort()
    best = None
    for dd, sn in cands[:keep]:
        s, d = descend(A, np.append(s_prev, sn), rng)
        if best is None or d < best[1]:
            best = (s, d)
    return best


def c_check(path: str) -> tuple[bool, str]:
    r = subprocess.run([C_CHECKER, path], capture_output=True, text=True)
    return r.returncode == 0, r.stdout.strip()


def certify(v: Sequence[int], s: np.ndarray, dp: int, dq: int, path: str, fgap: float, meta: dict):
    margin = dp / dq - fgap
    if margin <= 0:
        return False, {"reason": "no float margin"}
    D0 = max(8, int(math.ceil(2.0 / margin)))
    for D in (D0, 4 * D0, 64 * D0, 4096 * D0):
        a = [int(round(float(x) * D)) % D for x in s]
        if not covers_open(list(v), a, D, dp, dq)[0]:
            continue
        cert = {"n": len(v), "v": [int(x) for x in v], "a": a, "D": D,
                "s": [str(Fraction(x, D)) for x in a], "delta_num": dp, "delta_den": dq,
                "delta": f"{dp}/{dq}", "float_gamma_estimate": fgap, "meta": meta}
        with open(path, "w") as fh:
            json.dump(cert, fh, indent=1)
        ok2, msg = c_check(path)
        if not ok2:
            os.replace(path, path + ".DISAGREE")
            return False, {"reason": "checker disagreement", "c": msg}
        cert["checker1"] = "COVERED"
        cert["checker2"] = msg
        with open(path, "w") as fh:
            json.dump(cert, fh, indent=1)
        return True, cert
    return False, {"reason": "rounding failed checker 1"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmin", type=int, required=True)
    ap.add_argument("--nmax", type=int, required=True)
    ap.add_argument("--start", default=None, help="JSON file with float shifts for size nmin-1")
    ap.add_argument("--budget", type=float, default=120.0)
    ap.add_argument("--extra", type=float, default=30.0, help="ILS CPU seconds after success, to deepen margin")
    ap.add_argument("--grid", type=int, default=200)
    ap.add_argument("--keep", type=int, default=6)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--state", required=True, help="JSON file with float shifts per n (appended)")
    ap.add_argument("--log", required=True)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    logf = open(args.log, "a")

    def log(m: str) -> None:
        logf.write(m + "\n")
        logf.flush()

    state = {}
    if os.path.exists(args.state):
        state = json.load(open(args.state))
    if args.start:
        s_prev = np.array(json.load(open(args.start))[str(args.nmin - 1)]["s"])
    elif str(args.nmin - 1) in state:
        s_prev = np.array(state[str(args.nmin - 1)]["s"])
    else:
        s_prev = np.array([0.0])
    for n in range(args.nmin, args.nmax + 1):
        t0 = time.process_time()
        v = np.arange(1, n + 1, dtype=float)
        A = Arcs(v)
        target = 1.0 / (n + 1)
        if len(s_prev) != n - 1:
            raise SystemExit("state size mismatch")
        s, d = extend(A, s_prev, rng, args.grid, args.keep)
        log(f"n={n} after-extend gap={d:.10f} 1/gap={1/d:.4f} target_inv={n+1} cpu={time.process_time()-t0:.1f}")
        s, d = ils(A, s, d, rng, args.budget, stop_below=target * (1 - 1e-3))
        if d < target and args.extra > 0:
            s, d = ils(A, s, d, rng, args.extra, stop_below=None)
        cpu = time.process_time() - t0
        log(f"n={n} final gap={d:.10f} 1/gap={1/d:.4f} E={1/d-(n+1):.4f} cpu={cpu:.1f}")
        state[str(n)] = {"s": [float(x) for x in s], "gap": d, "cpu": cpu}
        json.dump(state, open(args.state, "w"))
        if d < target:
            path = os.path.join(args.outdir, f"cert_n{n:03d}.json")
            ok, info = certify(list(range(1, n + 1)), s, 1, n + 1, path, d,
                               {"method": "search2 continuation chain-LP ILS, v=[n]", "seed": args.seed, "cpu_s": cpu})
            log(f"n={n} certify={'OK' if ok else 'FAIL'} D={info.get('D')} {info.get('checker2', info.get('reason'))}")
        else:
            log(f"n={n} NO certificate")
        s_prev = s
    logf.close()


if __name__ == "__main__":
    main()
