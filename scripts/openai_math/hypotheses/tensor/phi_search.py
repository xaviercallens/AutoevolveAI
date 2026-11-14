#!/usr/bin/env python3
"""Search for +-1 seeds with Phi = H / (1 - |T|) > 3, and for non-tensor inputs beating the tensor family.

Phi(g) is the exact limit of R(g^(x)r) as r -> inf (product rule), so sup_g Phi(g) is the best lower
bound the tensor construction can give.  Tensor products of seeds with Phi <= M have Phi <= M (closure
lemma), so only "prime" seeds matter.  Objective values are exact integer ratios:
    Phi = Hnum / (n^3 - |Tint|),  R = (|Tint| + Hnum) / n^3,  Hnum = sum_l 2^l sum_I |Lint_I|.

Moves: single sign flips (and, for --mode R, pair flips) accepted when the objective does not decrease;
restarts from random signs or from a given tensor product.  Everything is recorded; nothing here can
prove an upper bound.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h5_tensor_rigor import OUT_DIR, R_pm1, exact_H, exact_T, kron, level_ints, resolution, t_int  # noqa: E402


def objective_ints(f: list[np.ndarray]) -> tuple[int, int, int]:
    """(Hnum, |Tint|, n^3) as integers."""
    n = f[0].shape[0]
    N = resolution(f[0])
    hnum = 0
    for level in range(N):
        hnum += int(np.abs(level_ints(f, level)).sum()) * 2**level
    return hnum, abs(t_int(f)), n**3


def phi_frac(f: list[np.ndarray]) -> Fraction:
    h, t, n3 = objective_ints(f)
    return Fraction(h, n3 - t) if t < n3 else Fraction(0)


def r_frac(f: list[np.ndarray]) -> Fraction:
    h, t, n3 = objective_ints(f)
    return Fraction(h + t, n3)


def climb(f: list[np.ndarray], obj, rng: np.random.Generator, budget_s: float, pair_moves: bool) -> tuple[list[np.ndarray], Fraction, int]:
    n = f[0].shape[0]
    cur = [x.copy() for x in f]
    cur_val = obj(cur)
    t0 = time.time()
    evals = 0
    stuck = 0
    while time.time() - t0 < budget_s and stuck < 4 * 3 * n * n:
        flips = [(int(rng.integers(3)), int(rng.integers(n)), int(rng.integers(n)))]
        if pair_moves and rng.random() < 0.5:
            flips.append((int(rng.integers(3)), int(rng.integers(n)), int(rng.integers(n))))
        for v, i, j in flips:
            cur[v][i, j] *= -1
        val = obj(cur)
        evals += 1
        if val >= cur_val:
            if val > cur_val:
                stuck = 0
            cur_val = val
        else:
            for v, i, j in flips:
                cur[v][i, j] *= -1
            stuck += 1
    return cur, cur_val, evals


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["phi", "R"], required=True)
    ap.add_argument("--n-res", type=int, required=True)
    ap.add_argument("--restarts", type=int, default=50)
    ap.add_argument("--budget-s", type=float, default=30.0, help="per restart")
    ap.add_argument("--total-s", type=float, default=1500.0)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--start-tensor", type=str, default=None, help="e.g. g2xg2: start from tensor powers of the N=2 seed")
    ap.add_argument("--tag", type=str, default="")
    ap.add_argument("--pair-moves", action="store_true")
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    obj = phi_frac if args.mode == "phi" else r_frac
    n = 2**args.n_res
    z = np.load(Path(__file__).resolve().parents[4] / "results" / "openai_math" / "hypotheses" / "H5" / "best_inputs_N2.npz")
    g2 = [np.where(z[k] >= 0, 1, -1).astype(np.int64) for k in z.files]
    t0 = time.time()
    best_val, best = Fraction(0), None
    runs = []
    for r in range(args.restarts):
        if time.time() - t0 > args.total_s:
            break
        if args.start_tensor and r % 2 == 0:
            start = g2
            while resolution(start[0]) < args.n_res:
                start = kron(start, g2)
            if resolution(start[0]) != args.n_res:
                start = [rng.choice([-1, 1], size=(n, n)).astype(np.int64) for _ in range(3)]
            else:
                # perturb a few entries so the climb does not sit at the tensor point
                for _ in range(int(rng.integers(1, 6))):
                    v, i, j = int(rng.integers(3)), int(rng.integers(n)), int(rng.integers(n))
                    start = [x.copy() for x in start]
                    start[v][i, j] *= -1
            origin = "tensor_perturbed"
        else:
            start = [rng.choice([-1, 1], size=(n, n)).astype(np.int64) for _ in range(3)]
            origin = "random"
        f, val, evals = climb(start, obj, rng, args.budget_s, pair_moves=(args.mode == "R" or args.pair_moves))
        runs.append({"restart": r, "origin": origin, "value": str(val), "float": float(val), "evals": evals})
        if val > best_val:
            best_val, best = val, [x.copy() for x in f]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    name = f"search_{args.mode}_N{args.n_res}_seed{args.seed}{args.tag}"
    np.savez_compressed(OUT_DIR / f"{name}.npz", *best)
    rec = {"mode": args.mode, "n_res": args.n_res, "seed": args.seed, "restarts_done": len(runs), "budget_s": args.budget_s,
           "best": str(best_val), "best_float": float(best_val), "best_H": str(exact_H(best)), "best_T": str(exact_T(best)),
           "best_R": str(R_pm1(best)), "exceeds_3": best_val > 3 if args.mode == "phi" else None,
           "elapsed_s": round(time.time() - t0, 1), "runs": runs}
    (OUT_DIR / f"{name}.json").write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps({k: rec[k] for k in ("mode", "n_res", "restarts_done", "best", "best_H", "best_T", "best_R", "exceeds_3", "elapsed_s")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
