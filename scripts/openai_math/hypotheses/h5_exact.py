#!/usr/bin/env python3
"""Exact rational evaluation of the dyadic triangular Hilbert ratio for +-1 inputs.

For inputs with entries in {+1, -1} on the 2^-N grid of [0,1)^2, each ||F_v||_3 = 1 exactly
and every L_I is an integer times a power of two, so the ratio is an exact dyadic rational.
A witness evaluated here is a rigorous lower bound for the best constant C* (H5), not a
floating-point estimate. Also provides a sign-flip local search (autoresearch iteration 2).

Usage:
    python3 scripts/openai_math/hypotheses/h5_exact.py verify results/openai_math/hypotheses/H5/best_inputs_N4.npz
    python3 scripts/openai_math/hypotheses/h5_exact.py search --n-res 5 --budget-s 600 --seed 1
"""

from __future__ import annotations

import argparse
import json
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
OUT_DIR = REPO / "results" / "openai_math" / "hypotheses" / "H5"


def exact_ratio(signs: list[np.ndarray]) -> tuple[Fraction, dict[str, str]]:
    """Exact ratio for +-1 integer matrices of size 2^N (norms are exactly 1)."""
    size = signs[0].shape[0]
    n_res = size.bit_length() - 1
    assert 2**n_res == size
    a = [np.asarray(x, dtype=np.int64) for x in signs]
    assert all(set(np.unique(x)) <= {-1, 1} for x in a), "entries must be +-1"
    w3 = Fraction(1, size**3)
    parts: dict[str, Fraction] = {}
    parts["T"] = abs(int(np.einsum("ij,jk,ki->", a[0], a[1], a[2]))) * w3
    for k in range(-n_res + 1, 1):
        m = 2 ** (-k)
        b = size // m
        s = np.concatenate([np.ones(b // 2, dtype=np.int64), -np.ones(b // 2, dtype=np.int64)])
        blocks = [x.reshape(m, b, m, b).transpose(0, 2, 1, 3) for x in a]
        n0 = np.arange(m)[:, None]
        n1 = np.arange(m)[None, :]
        n2 = n0 ^ n1
        x0 = blocks[0][n0, n1] * s[:, None] * s[None, :]
        x1 = blocks[1][n1, n2] * s[None, :]
        x2 = blocks[2][n2, n0]
        ints = np.einsum("pqij,pqjk,pqki->pq", x0, x1, x2)  # exact int64
        parts[str(k)] = Fraction(int(np.abs(ints).sum()) * m) * w3
    total = sum(parts.values(), Fraction(0))
    return total, {k: str(v) for k, v in parts.items()}


def verify(npz: Path) -> dict[str, object]:
    z = np.load(npz)
    signs = [np.where(z[f] >= 0, 1, -1) for f in z.files]
    total, parts = exact_ratio(signs)
    return {"witness": str(npz.relative_to(REPO)), "exact_ratio": str(total), "float": float(total), "parts": parts}


def local_search(n_res: int, budget_s: float, seed: int, start: list[np.ndarray] | None) -> tuple[Fraction, list[np.ndarray]]:
    """Single-entry sign flips, accept if the exact ratio does not decrease (plateau moves allowed)."""
    rng = np.random.default_rng(seed)
    size = 2**n_res
    cur = start if start is not None else [rng.choice([-1, 1], size=(size, size)) for _ in range(3)]
    cur_val, _ = exact_ratio(cur)
    best_val, best = cur_val, [c.copy() for c in cur]
    t0 = time.time()
    while time.time() - t0 < budget_s:
        v = int(rng.integers(3))
        i, j = (int(x) for x in rng.integers(size, size=2))
        cur[v][i, j] *= -1
        val, _ = exact_ratio(cur)
        if val >= cur_val:
            cur_val = val
            if val > best_val:
                best_val, best = val, [c.copy() for c in cur]
        else:
            cur[v][i, j] *= -1
    return best_val, best


def main() -> int:
    p = argparse.ArgumentParser(description="exact H5 evaluation and sign-flip search")
    sub = p.add_subparsers(dest="cmd", required=True)
    pv = sub.add_parser("verify")
    pv.add_argument("npz", type=Path)
    ps = sub.add_parser("search")
    ps.add_argument("--n-res", type=int, required=True)
    ps.add_argument("--budget-s", type=float, default=600.0)
    ps.add_argument("--seed", type=int, default=1)
    ps.add_argument("--start", type=Path, default=None, help="npz witness to start from (signs taken)")
    args = p.parse_args()
    if args.cmd == "verify":
        out = verify(args.npz.resolve())
        print(json.dumps(out))
        return 0
    start = None
    if args.start is not None:
        z = np.load(args.start)
        start = [np.where(z[f] >= 0, 1, -1).astype(np.int64) for f in z.files]
    val, best = local_search(args.n_res, args.budget_s, args.seed, start)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"signsearch_N{args.n_res}_seed{args.seed}.npz"
    np.savez_compressed(path, *best)
    print(json.dumps({"n_res": args.n_res, "seed": args.seed, "budget_s": args.budget_s, "exact_ratio": str(val), "float": float(val), "witness": str(path.relative_to(REPO))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
