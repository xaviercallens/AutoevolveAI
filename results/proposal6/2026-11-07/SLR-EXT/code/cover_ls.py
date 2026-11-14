"""Search v3 (float heuristic, Tier X): exact coordinate moves on the uncovered measure.

Fixed radius delta* slightly below 1/(n+1).  For runner i, the set U_i not covered by the
other runners is folded modulo 1/v_i; runner i's arcs are one window of width 2 delta*/v_i in
the fold, and the best window position (max covered measure of U_i, optionally weighted) is
found exactly among the breakpoints.  Random order, random-walk kicks, breakout weights.
Stop at uncovered measure 0; then round s to a/D and certify with both exact checkers.
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

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from slr_exact import covers_open  # noqa: E402

C_CHECKER = os.path.join(HERE, "check_cover")


def runner_arcs(vi: float, si: float, d: float) -> tuple[np.ndarray, np.ndarray]:
    k = np.arange(int(vi) + 1)
    c = (k - si) / vi
    c = c - np.floor(c)
    h = d / vi
    return c - h, c + h


def union_complement(los: np.ndarray, his: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Uncovered intervals of [0,1) given arcs (lo,hi) with lo in [-h,1) (wrap handled)."""
    lo = np.concatenate([los, los - 1.0, los + 1.0])
    hi = np.concatenate([his, his - 1.0, his + 1.0])
    m = (hi > 0.0) & (lo < 1.0)
    lo, hi = lo[m], hi[m]
    if len(lo) == 0:
        return np.array([0.0]), np.array([1.0])
    o = np.argsort(lo)
    lo, hi = lo[o], hi[o]
    cm = np.maximum.accumulate(hi)
    ga = [] ; gb = []
    if lo[0] > 0.0:
        ga.append(0.0); gb.append(lo[0])
    idx = np.nonzero(lo[1:] > cm[:-1])[0]
    for j in idx:
        a, b = max(cm[j], 0.0), min(lo[j + 1], 1.0)
        if b > a:
            ga.append(a); gb.append(b)
    if cm[-1] < 1.0:
        ga.append(cm[-1]); gb.append(1.0)
    return np.array(ga), np.array(gb)


class State:
    def __init__(self, v: np.ndarray, s: np.ndarray, d: float):
        self.v, self.s, self.d = v, s, d
        self.n = len(v)

    def all_arcs(self, skip: int = -1):
        L, H = [], []
        for j in range(self.n):
            if j == skip:
                continue
            lo, hi = runner_arcs(self.v[j], self.s[j], self.d)
            L.append(lo); H.append(hi)
        return np.concatenate(L), np.concatenate(H)

    def uncovered(self):
        lo, hi = self.all_arcs()
        a, b = union_complement(lo, hi)
        return a, b, float((b - a).sum())


def best_window(a: np.ndarray, b: np.ndarray, w: np.ndarray, P: float, h: float, rng: random.Random):
    """Fold weighted intervals [a,b] mod P; return (best centre c in [0,P), best covered weight)."""
    # split at multiples of P
    fa, fb, fw = [], [], []
    for x, y, ww in zip(a, b, w):
        q = math.floor(x / P)
        x0 = x - q * P
        y0 = y - q * P
        while y0 > P:
            fa.append(x0); fb.append(P); fw.append(ww)
            x0, y0 = 0.0, y0 - P
        fa.append(x0); fb.append(y0); fw.append(ww)
    fa, fb, fw = np.array(fa), np.array(fb), np.array(fw)
    # unroll three copies for periodicity
    A = np.concatenate([fa - P, fa, fa + P])
    B = np.concatenate([fb - P, fb, fb + P])
    W = np.concatenate([fw, fw, fw])
    # G(x) = sum_j W_j * clip(x - A_j, 0, B_j - A_j)  (folded layers may overlap)
    oa = np.argsort(A)
    As, WA = A[oa], W[oa]
    cWA = np.concatenate([[0.0], np.cumsum(WA)])
    cWAA = np.concatenate([[0.0], np.cumsum(WA * As)])
    ob = np.argsort(B)
    Bs, WB = B[ob], W[ob]
    cWB = np.concatenate([[0.0], np.cumsum(WB)])
    cWBB = np.concatenate([[0.0], np.cumsum(WB * Bs)])

    def G(x: np.ndarray) -> np.ndarray:
        ja = np.searchsorted(As, x, side="right")
        jb = np.searchsorted(Bs, x, side="right")
        return (x * cWA[ja] - cWAA[ja]) - (x * cWB[jb] - cWBB[jb])

    cand = np.concatenate([fa + h, fa - h, fb + h, fb - h])
    cand = np.mod(cand, P)
    F = G(cand + h) - G(cand - h)
    mx = F.max()
    ties = np.nonzero(F >= mx - 1e-15)[0]
    j = ties[rng.randrange(len(ties))]
    return float(cand[j]), float(mx)


def solve(v: np.ndarray, d: float, rng: random.Random, budget: float, s0: np.ndarray | None = None, log=None):
    n = len(v)
    s = np.array([rng.random() for _ in range(n)]) if s0 is None else s0.copy()
    st = State(v, s, d)
    t0 = time.process_time()
    a, b, U = st.uncovered()
    best = (U, s.copy())
    weights: dict = {}  # breakout weights keyed by rounded midpoint
    tabu = {}
    stall = 0
    it = 0
    while time.process_time() - t0 < budget:
        it += 1
        if U <= 1e-12:
            break
        order = list(range(n))
        rng.shuffle(order)
        improved = False
        for i in order:
            if tabu.get(i, -1) >= it:
                continue
            lo, hi = st.all_arcs(skip=i)
            ua, ub = union_complement(lo, hi)
            if len(ua) == 0:
                continue
            mid = 0.5 * (ua + ub)
            w = np.array([1.0 + weights.get(round(m, 6), 0.0) for m in mid])
            P = 1.0 / v[i]
            h = d / v[i]
            c, val = best_window(ua, ub, w, P, h, rng)
            s_new = (-c * v[i]) % 1.0
            old = st.s[i]
            st.s[i] = s_new
            a2, b2, U2 = st.uncovered()
            if U2 < U - 1e-15:
                improved = True
                U, a, b = U2, a2, b2
                if U < best[0]:
                    best = (U, st.s.copy())
                if U <= 1e-12:
                    break
            elif U2 > U + 1e-15 and rng.random() < 0.7:
                st.s[i] = old
            else:
                U, a, b = U2, a2, b2
        if U <= 1e-12:
            break
        if not improved:
            stall += 1
            # breakout: increase weight on current gaps
            for x, y in zip(a, b):
                key = round(0.5 * (x + y), 6)
                weights[key] = weights.get(key, 0.0) + 1.0
            if stall % 3 == 0 and len(a) > 0:
                # random walk: centre a random runner's nearest arc on a random uncovered point
                g = rng.randrange(len(a))
                u = a[g] + rng.random() * (b[g] - a[g])
                i = rng.randrange(n)
                st.s[i] = (-u * v[i]) % 1.0
                tabu[i] = it + 2
                a, b, U = st.uncovered()
            if stall % 40 == 0:
                weights.clear()
        else:
            stall = 0
        if log and it % 50 == 0:
            log(f"   it={it} U={U:.3e} best={best[0]:.3e} gaps={len(a)} cpu={time.process_time()-t0:.1f}")
    return best[1], best[0], time.process_time() - t0, it


def c_check(path: str) -> tuple[bool, str]:
    r = subprocess.run([C_CHECKER, path], capture_output=True, text=True)
    return r.returncode == 0, r.stdout.strip()


def certify(v, s, dp: int, dq: int, path: str, d_star: float, meta: dict):
    margin = dp / dq - d_star
    D0 = max(8, int(math.ceil(2.0 / margin)))
    for D in (D0, 8 * D0, 128 * D0, 4096 * D0):
        a = [int(round(float(x) * D)) % D for x in s]
        if not covers_open(list(v), a, D, dp, dq)[0]:
            continue
        cert = {"n": len(v), "v": [int(x) for x in v], "a": a, "D": D,
                "s": [str(Fraction(x, D)) for x in a], "delta_num": dp, "delta_den": dq,
                "delta": f"{dp}/{dq}", "search_radius_float": d_star, "meta": meta}
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
    ap.add_argument("--ns", required=True, help="comma list or a-b range")
    ap.add_argument("--budget", type=float, default=300.0)
    ap.add_argument("--restarts", type=int, default=3)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--slack", type=float, default=8.0, help="delta* = 1/(n+1) - 1/(slack*(n+1)^2)")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--skip-existing", action="store_true")
    args = ap.parse_args()
    if "-" in args.ns:
        x, y = args.ns.split("-")
        ns = list(range(int(x), int(y) + 1))
    else:
        ns = [int(x) for x in args.ns.split(",")]
    logf = open(args.log, "a")

    def log(m: str) -> None:
        logf.write(m + "\n")
        logf.flush()

    for n in ns:
        path = os.path.join(args.outdir, f"cert_n{n:03d}.json")
        if args.skip_existing and os.path.exists(path):
            log(f"n={n} skip (certificate exists)")
            continue
        v = np.arange(1, n + 1, dtype=float)
        d_star = 1.0 / (n + 1) - 1.0 / (args.slack * (n + 1) ** 2)
        tot = 0.0
        done = False
        for r in range(args.restarts):
            rng = random.Random(args.seed * 1000 + n * 10 + r)
            s, U, cpu, it = solve(v, d_star, rng, args.budget / args.restarts, log=log)
            tot += cpu
            log(f"n={n} restart={r} uncovered={U:.3e} iters={it} cpu={cpu:.1f}")
            if U <= 1e-12:
                ok, info = certify(list(range(1, n + 1)), s, 1, n + 1, path, d_star,
                                   {"method": "cover_ls coordinate fold moves, v=[n]", "seed": args.seed,
                                    "restart": r, "cpu_s_this_n": tot})
                log(f"n={n} certify={'OK' if ok else 'FAIL'} D={info.get('D')} {info.get('checker2', info.get('reason'))}")
                if ok:
                    done = True
                    break
        log(f"n={n} RESULT {'CERTIFIED' if done else 'OPEN'} cpu_total={tot:.1f}")
    logf.close()


if __name__ == "__main__":
    main()
