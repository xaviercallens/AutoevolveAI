"""Search for shifts s with gamma(v; s) small (float heuristic, Tier X).

Nothing produced here is trusted: every candidate is rounded to s = a/D and
re-checked exactly by checker 1 (slr_exact.covers_open, Python integers) and by
checker 2 (check_cover, C).  Only then is a certificate written.

Heuristic: chain-LP descent.
  * Given s and a radius, extract greedily a cyclic chain of bad arcs
    (i_1,k_1), ..., (i_m,k_m) that covers the circle.
  * For that fixed combinatorics, min delta over (s, delta) is a linear program:
        lo_j <= lo_{j+1},  lo_{j+1} <= hi_j,  lo_1 + 1 <= hi_m,
    lo = (k - s_i - delta)/v_i, hi = (k - s_i + delta)/v_i.  Solved by HiGHS.
  * Re-extract the chain at the new optimum and repeat; iterated local search
    (random kicks) on top.
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


def float_gap(v: np.ndarray, s: np.ndarray) -> float:
    """Float gamma(v;s) via the smallest radius at which greedy covering succeeds (bisection)."""
    lo, hi = 0.0, 0.5
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if extract_chain(v, s, mid) is not None:
            hi = mid
        else:
            lo = mid
    return hi


def extract_chain(v: np.ndarray, s: np.ndarray, delta: float, rng: random.Random | None = None, slack: float = 0.0, t0: float = 0.0):
    """Greedy cyclic chain of closed arcs of radius delta covering R/Z, or None.

    Returns list of (i, k).  If rng is given, among candidate arcs whose reach is
    within `slack` of the best one, a random one is chosen (diversification).
    """
    reps = []
    for i, vi in enumerate(v):
        ks = np.arange(-int(vi) - 2, 3 * int(vi) + 3)
        c = (ks - s[i]) / vi
        h = delta / vi
        for k, cc in zip(ks, c):
            if cc + h > t0 - 1.0 and cc - h < t0 + 2.0:
                reps.append((cc - h, cc + h, i, int(k)))
    reps.sort()
    los = [r[0] for r in reps]
    # first arc: containing 0 with max hi
    chain = []
    cur = t0
    idx = 0
    n_r = len(reps)
    first_lo = None
    target_end = None
    pool: list = []
    while True:
        while idx < n_r and los[idx] <= cur:
            pool.append(reps[idx])
            idx += 1
        if not pool:
            return None
        bh = max(p[1] for p in pool)
        if bh <= cur + 1e-15:
            return None
        if rng is not None and slack > 0:
            cand = [p for p in pool if p[1] >= bh - slack and p[1] > cur]
            pick = rng.choice(cand)
        else:
            pick = max(pool, key=lambda p: p[1])
        chain.append((pick[2], pick[3]))
        if first_lo is None:
            first_lo = pick[0]
            target_end = first_lo + 1.0
        cur = pick[1]
        pool = [p for p in pool if p[1] > cur]
        if cur >= target_end:
            return chain
        if len(chain) > 20 * len(v) + 100:
            return None


def lp_on_chain(v: np.ndarray, chain, fix: int = 0):
    """Minimise delta for fixed chain. Variables: s_0..s_{n-1}, delta; s_fix = 0."""
    n = len(v)
    nv = n + 1
    rows = []
    rhs = []

    def lo_coef(i, k):
        # lo = (k - s_i - delta)/v_i  -> coef vector, const
        c = np.zeros(nv)
        c[i] -= 1.0 / v[i]
        c[n] -= 1.0 / v[i]
        return c, k / v[i]

    def hi_coef(i, k):
        c = np.zeros(nv)
        c[i] -= 1.0 / v[i]
        c[n] += 1.0 / v[i]
        return c, k / v[i]

    m = len(chain)
    for j in range(m - 1):
        (i1, k1), (i2, k2) = chain[j], chain[j + 1]
        a1, b1 = lo_coef(i1, k1)
        a2, b2 = lo_coef(i2, k2)
        # lo_j <= lo_{j+1}  ->  a1 x + b1 <= a2 x + b2
        rows.append(a1 - a2)
        rhs.append(b2 - b1)
        h1, hb1 = hi_coef(i1, k1)
        # lo_{j+1} <= hi_j
        rows.append(a2 - h1)
        rhs.append(hb1 - b2)
    (i1, k1), (im, km) = chain[0], chain[-1]
    a1, b1 = lo_coef(i1, k1)
    hm, hbm = hi_coef(im, km)
    rows.append(a1 - hm)
    rhs.append(hbm - b1 - 1.0)
    A = np.array(rows)
    b = np.array(rhs)
    cost = np.zeros(nv)
    cost[n] = 1.0
    bounds = [(-5.0, 5.0)] * n + [(0.0, 0.5)]
    bounds[fix] = (0.0, 0.0)
    res = linprog(cost, A_ub=A, b_ub=b, bounds=bounds, method="highs")
    if res.status != 0:
        return None, None
    return res.x[:n], float(res.x[n])


def descend(v: np.ndarray, s: np.ndarray, rng: random.Random, iters: int = 400, patience: int = 12):
    """Chain-LP descent with diversified chains (random inflation alpha, random start t0)."""
    d = float_gap(v, s)
    fails = 0
    for it in range(iters):
        if fails == 0:
            alpha, t0 = 1e-9, 0.0
        else:
            alpha = rng.choice([1e-6, 0.01, 0.03, 0.07, 0.15, 0.3])
            t0 = rng.random()
        ch = extract_chain(v, s, d * (1 + alpha) + 1e-13, t0=t0)
        if ch is None:
            fails += 1
            if fails > patience:
                break
            continue
        s2, d2 = lp_on_chain(v, ch)
        if s2 is None:
            fails += 1
            if fails > patience:
                break
            continue
        s2 = np.mod(s2, 1.0)
        d2r = float_gap(v, s2)
        if d2r < d - 1e-12:
            s, d = s2, d2r
            fails = 0
        else:
            fails += 1
            if fails > patience:
                break
    return s, d


def ils(v: np.ndarray, s0: np.ndarray | None, rng: random.Random, budget_s: float, stop_below: float | None,
        kick: float = 0.02, log=None):
    t0 = time.process_time()
    n = len(v)
    if s0 is None:
        s0 = np.array([rng.random() for _ in range(n)])
    s, d = descend(v, s0, rng)
    best_s, best_d = s.copy(), d
    it = 0
    while time.process_time() - t0 < budget_s:
        it += 1
        if stop_below is not None and best_d < stop_below:
            break
        if it % 25 == 0:
            cand0 = np.array([rng.random() for _ in range(n)])  # restart
        else:
            cand0 = np.mod(best_s + np.array([rng.gauss(0, kick) for _ in range(n)]), 1.0)
            # sparse kick on a few coordinates
            if rng.random() < 0.5:
                cand0 = best_s.copy()
                for _ in range(max(1, n // 10)):
                    j = rng.randrange(n)
                    cand0[j] = rng.random()
        s2, d2 = descend(v, cand0, rng)
        if d2 < best_d - 1e-13:
            best_s, best_d = s2.copy(), d2
            if log:
                log(f"  it={it} best={best_d:.9f} 1/best={1/best_d:.4f} cpu={time.process_time()-t0:.1f}")
    return best_s, best_d


def c_check(path: str) -> tuple[bool, str]:
    r = subprocess.run([C_CHECKER, path], capture_output=True, text=True)
    return r.returncode == 0, r.stdout.strip()


def round_and_certify(v: Sequence[int], s: np.ndarray, dp: int, dq: int, out_path: str, best_float: float,
                      meta: dict) -> tuple[bool, dict]:
    margin = dp / dq - best_float
    if margin <= 0:
        return False, {"reason": "no float margin"}
    D0 = max(8, int(math.ceil(2.0 / margin)))
    for D in (D0, 4 * D0, 64 * D0, 1024 * D0):
        a = [int(round(float(x) * D)) % D for x in s]
        ok1, M, bad = covers_open(list(v), a, D, dp, dq)
        if not ok1:
            continue
        cert = {
            "n": len(v), "v": list(map(int, v)), "a": a, "D": D,
            "s": [str(Fraction(x, D)) for x in a],
            "delta_num": dp, "delta_den": dq, "delta": f"{dp}/{dq}",
            "common_denominator_checker1": str(M),
            "float_gamma_estimate": best_float,
            "meta": meta,
        }
        with open(out_path, "w") as fh:
            json.dump(cert, fh, indent=1)
        ok2, msg = c_check(out_path)
        cert["checker1"] = "COVERED"
        cert["checker2"] = msg
        with open(out_path, "w") as fh:
            json.dump(cert, fh, indent=1)
        if not ok2:
            os.replace(out_path, out_path + ".DISAGREE")
            return False, {"reason": "checker disagreement", "c": msg}
        return True, cert
    return False, {"reason": "rounding failed checker 1"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmin", type=int, required=True)
    ap.add_argument("--nmax", type=int, required=True)
    ap.add_argument("--budget", type=float, default=600.0, help="CPU seconds per n")
    ap.add_argument("--improve", type=float, default=0.0, help="extra CPU seconds after first success")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--continuation", action="store_true")
    args = ap.parse_args()
    rng = random.Random(args.seed)
    logf = open(args.log, "a")

    def log(msg: str) -> None:
        logf.write(msg + "\n")
        logf.flush()

    prev_s = None
    for n in range(args.nmin, args.nmax + 1):
        v = np.arange(1, n + 1, dtype=float)
        t0 = time.process_time()
        s0 = None
        if args.continuation and prev_s is not None and len(prev_s) == n - 1:
            s0 = np.append(prev_s, rng.random())
        target = 1.0 / (n + 1)
        log(f"n={n} start target={target:.9f}")
        s, d = ils(v, s0, rng, args.budget, stop_below=target * (1 - 1e-4), log=log)
        if d < target and args.improve > 0:
            s, d = ils(v, s, rng, args.improve, stop_below=None, log=log)
        cpu = time.process_time() - t0
        log(f"n={n} float_best={d:.10f} 1/best={1/d:.5f} E_float={1/d-(n+1):.4f} cpu={cpu:.1f}")
        if d < target:
            path = os.path.join(args.outdir, f"cert_n{n:03d}.json")
            ok, info = round_and_certify(list(range(1, n + 1)), s, 1, n + 1, path, d,
                                         {"method": "chain-LP ILS, v=[n]", "seed": args.seed, "cpu_s": cpu})
            log(f"n={n} certify={'OK' if ok else 'FAIL'} D={info.get('D')} {info.get('checker2', info.get('reason'))}")
            prev_s = s
        else:
            log(f"n={n} NO certificate within budget")
            prev_s = s
    logf.close()


if __name__ == "__main__":
    main()
