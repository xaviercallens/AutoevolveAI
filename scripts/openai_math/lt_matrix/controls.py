#!/usr/bin/env python3
"""Frozen control suite for the matrix Lieb-Thirring instrument (run before every campaign; a failed control voids the run).

Positive controls (the instrument must reproduce known facts):
  C1  exact equality potential: R/L1 - 1 within 2e-6 (one-sided: <= 1e-9), exactly one bound state at E = -1.
  C2  invariance: embedding a scalar in m = 2, 3 and rotating by a constant unitary leaves R unchanged (1e-12).
  C3  decoupled direct sum: numerator is additive (1e-10).
  C4  scalar search from random starts reaches L1 (within 1e-4) and never exceeds it (gamma = 1.0, 1.25).
  C6  gamma = 3/2: sup is 3/16 (Laptev-Weidl, proved for operator-valued W): the matrix search reaches it from below
      and must not exceed it.
Negative controls (the search must be able to find a violation where one exists):
  C5  scalar gamma = 3: the one-bound-state constant is NOT the sup, many-state potentials beat it.
  C7  matrix m = 2, gamma = 3: same.
Usage: python3 controls.py --out results/openai_math/hypotheses/lt_matrix/controls.json
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from instrument import (Grid, equality_potential, numerator_denominator, optimise, ratio, semiclassical_constant,  # noqa: E402
                        sharp_constant)

GRID = dict(L=24.0, M=160, Q=1200)


def _init() -> None:
    torch.set_num_threads(2)


def c1() -> dict:
    out = {}
    for gamma, g in ((1.0, Grid(**GRID)), (1.25, Grid(**GRID)), (1.4, Grid(**GRID)), (0.75, Grid(24.0, 320, 2400))):
        W = equality_potential(gamma, g)
        num, den, neg = numerator_denominator(W, gamma, g)
        excess = float(num / den) / sharp_constant(gamma) - 1.0
        out[str(gamma)] = {"excess": excess, "n_neg": int(neg.numel()), "E_min": -float(neg.max()),
                           "pass": abs(excess) < 2e-6 and excess < 1e-9 and neg.numel() == 1 and abs(float(neg.max()) - 1) < 1e-5}
    return {"id": "C1", "results": out, "pass": all(v["pass"] for v in out.values())}


def c2_c3() -> dict:
    g = Grid(**GRID)
    gamma = 1.0
    base = equality_potential(gamma, g)
    res = {}
    for m in (2, 3):
        W = torch.zeros(g.Q, m, m, dtype=torch.complex128)
        W[:, 0, 0] = base[:, 0, 0]
        U = torch.linalg.qr(torch.randn(m, m, dtype=torch.complex128, generator=torch.Generator().manual_seed(m)))[0]
        r0, r1 = ratio(W, gamma, g), ratio(U @ W @ U.conj().T, gamma, g)
        r_scalar = ratio(base, gamma, g)
        res[f"m{m}"] = {"embed_minus_scalar": r0 - r_scalar, "dressed_minus_embed": r1 - r0, "pass": abs(r0 - r_scalar) < 1e-12 and abs(r1 - r0) < 1e-12}
    # C3: decoupled sum of two different scalars
    w1 = equality_potential(1.0, g)[:, 0, 0]
    x2 = g.x - 3.0
    w2 = (1.7 * 2.0 / torch.cosh(1.3 * (g.x + 4.0)) ** 2).to(torch.complex128)
    W = torch.zeros(g.Q, 2, 2, dtype=torch.complex128)
    W[:, 0, 0], W[:, 1, 1] = w1, w2
    n12, d12, _ = numerator_denominator(W, gamma, g)
    n1, d1, _ = numerator_denominator(w1.reshape(-1, 1, 1), gamma, g)
    n2, d2, _ = numerator_denominator(w2.reshape(-1, 1, 1), gamma, g)
    c3 = {"num_diff": float(n12 - n1 - n2), "den_diff": float(d12 - d1 - d2)}
    c3["pass"] = abs(c3["num_diff"]) < 1e-10 and abs(c3["den_diff"]) < 1e-10
    return {"id": "C2_C3", "invariance": res, "additivity": c3, "pass": all(v["pass"] for v in res.values()) and c3["pass"]}


def search(args: tuple[float, int, int, int, int]) -> dict:
    gamma, m, seed, K, P = args
    g = Grid(**GRID)
    t0 = time.time()
    r, _ = optimise(gamma, m, g, seed, K=K, P=P)
    return {"gamma": gamma, "m": m, "seed": seed, "K": K, "P": P, "R": r, "L1": sharp_constant(gamma),
            "Lcl": semiclassical_constant(gamma), "excess": r / sharp_constant(gamma) - 1.0, "seconds": round(time.time() - t0, 1)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    torch.set_num_threads(2)
    results: dict = {"grid": GRID, "controls": {}}
    results["controls"]["C1"] = c1()
    results["controls"]["C2_C3"] = c2_c3()
    jobs = ([(1.0, 1, s, 2, 8) for s in range(3)] + [(1.25, 1, s, 2, 8) for s in range(3)] + [(1.5, 2, s, 2, 8) for s in range(3)] +
            [(3.0, 1, s, 3, 14) for s in range(4)] + [(3.0, 2, s, 3, 14) for s in range(4)])
    # spawn, not fork: the parent has already used torch's thread pool, and forked workers deadlock on it
    with ProcessPoolExecutor(max_workers=3, initializer=_init, mp_context=multiprocessing.get_context("spawn")) as ex:
        runs = list(ex.map(search, jobs))
    results["runs"] = runs

    def pick(gamma: float, m: int) -> list[dict]:
        return [r for r in runs if r["gamma"] == gamma and r["m"] == m]

    c4 = {str(g): {"best_excess": max(r["excess"] for r in pick(g, 1))} for g in (1.0, 1.25)}
    for v in c4.values():
        v["pass"] = -1e-4 <= v["best_excess"] <= 1e-6
    c6 = {"best_excess": max(r["excess"] for r in pick(1.5, 2))}
    c6["pass"] = -1e-3 <= c6["best_excess"] <= 1e-6
    c5 = {"best_excess": max(r["excess"] for r in pick(3.0, 1))}
    c5["pass"] = c5["best_excess"] > 1e-3
    c7 = {"best_excess": max(r["excess"] for r in pick(3.0, 2))}
    c7["pass"] = c7["best_excess"] > 1e-3
    results["controls"].update({"C4": {"results": c4, "pass": all(v["pass"] for v in c4.values())}, "C5": c5, "C6": c6, "C7": c7})
    results["all_pass"] = all(c["pass"] for c in results["controls"].values())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({k: v["pass"] for k, v in results["controls"].items()}), "all_pass", results["all_pass"])
    for r in runs:
        print(f"gamma={r['gamma']} m={r['m']} seed={r['seed']}: R/L1-1={r['excess']:+.3e}  R/Lcl={r['R']/r['Lcl']:.4f}  {r['seconds']}s")
    return 0 if results["all_pass"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
