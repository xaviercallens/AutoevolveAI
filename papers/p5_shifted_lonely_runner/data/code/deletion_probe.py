"""Probe (Tier X): for v = [N] minus {r} (size n = N-1), start near s = 0 and run chain-LP descent + short ILS.
Report the float gap and whether it reaches <= 1/(N+1) = 1/(n+2) (E >= 1)."""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"

import argparse
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from search2 import Arcs, descend, gap, ils  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, required=True)
    ap.add_argument("--tries", type=int, default=5)
    ap.add_argument("--ils", type=float, default=5.0)
    ap.add_argument("--log", required=True)
    args = ap.parse_args()
    N = args.N
    rng = random.Random(N)
    logf = open(args.log, "a")
    for r in range(1, N + 1):
        v = np.array([x for x in range(1, N + 1) if x != r], dtype=float)
        A = Arcs(v)
        best = 1.0
        t0 = time.process_time()
        for _ in range(args.tries):
            s0 = np.mod(np.array([rng.gauss(0, 0.002) for _ in v]), 1.0)
            s, d = descend(A, s0, rng, patience=15)
            s, d = ils(A, s, d, rng, args.ils, stop_below=None)
            best = min(best, d)
        logf.write(f"N={N} r={r} n={N-1} best_gap={best:.8f} 1/gap={1/best:.4f} E={1/best-N:.4f} cpu={time.process_time()-t0:.1f}\n")
        logf.flush()
    logf.close()


if __name__ == "__main__":
    main()
