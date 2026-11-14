"""Smooth surrogate seeding (float heuristic, Tier X).

Minimise  J(s) = (1/p) log sum_t exp(p * softmin_beta_i ||s_i + v_i t||)  on a time grid,
with annealed beta, p, by Adam; then polish with the chain-LP descent of search2.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"

import argparse
import json
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from search2 import Arcs, descend, gap  # noqa: E402


def smooth_opt(v: np.ndarray, s0: np.ndarray, steps: int, G: int, rng: np.random.Generator,
               lr: float = 0.01) -> np.ndarray:
    n = len(v)
    s = s0.copy()
    m = np.zeros(n)
    q = np.zeros(n)
    b1, b2 = 0.9, 0.999
    for it in range(1, steps + 1):
        frac = it / steps
        beta = (n + 1) * (10 + 290 * frac)
        p = (n + 1) * (10 + 290 * frac)
        t = (np.arange(G) + rng.random()) / G
        x = s[None, :] + v[None, :] * t[:, None]
        fr = x - np.floor(x)
        d = np.minimum(fr, 1 - fr)
        sg = np.where(fr < 0.5, 1.0, -1.0)
        z = -beta * d
        zm = z.max(axis=1, keepdims=True)
        w = np.exp(z - zm)
        w /= w.sum(axis=1, keepdims=True)
        f = -(np.log(np.exp(z - zm).sum(axis=1)) + zm[:, 0]) / beta
        pf = p * f
        pi = np.exp(pf - pf.max())
        pi /= pi.sum()
        g = (pi[:, None] * w * sg).sum(axis=0)
        g[0] = 0.0
        m = b1 * m + (1 - b1) * g
        q = b2 * q + (1 - b2) * g * g
        mh = m / (1 - b1 ** it)
        qh = q / (1 - b2 ** it)
        step = lr * (1 - 0.9 * frac) / (n + 1)
        s = np.mod(s - step * mh / (np.sqrt(qh) + 1e-12), 1.0)
    return s


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--restarts", type=int, default=20)
    ap.add_argument("--steps", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--log", required=True)
    ap.add_argument("--state", required=True)
    args = ap.parse_args()
    n = args.n
    v = np.arange(1, n + 1, dtype=float)
    A = Arcs(v)
    rng = np.random.default_rng(args.seed)
    prng = random.Random(args.seed)
    G = int(12 * v.sum())
    best = None
    logf = open(args.log, "a")
    t0 = time.process_time()
    for r in range(args.restarts):
        s0 = rng.random(n)
        s0[0] = 0.0
        s1 = smooth_opt(v, s0, args.steps, G, rng)
        d1 = gap(A, s1)
        s2, d2 = descend(A, s1, prng, patience=15, d=d1)
        logf.write(f"n={n} restart={r} smooth_gap={d1:.6f} (1/{1/d1:.3f}) polished={d2:.8f} (1/{1/d2:.4f}) cpu={time.process_time()-t0:.1f}\n")
        logf.flush()
        if best is None or d2 < best[1]:
            best = (s2, d2)
    st = {}
    if os.path.exists(args.state):
        st = json.load(open(args.state))
    if str(n) not in st or st[str(n)]["gap"] > best[1]:
        st[str(n)] = {"s": [float(x) for x in best[0]], "gap": best[1], "cpu": time.process_time() - t0}
        json.dump(st, open(args.state, "w"))
    logf.write(f"n={n} BEST {best[1]:.10f} 1/{1/best[1]:.4f} E={1/best[1]-(n+1):.4f}\n")
    logf.close()


if __name__ == "__main__":
    main()
