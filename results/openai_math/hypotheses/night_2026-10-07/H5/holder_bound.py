"""Exploratory (NOT preregistered, see deviations.md item 5): exact Hoelder-marginal upper bound.

For resolution N the dyadic form is S(F) = sum_t w_t |int_t(F)| with int_t = sum_{i,j,k} F0[i,j] F1[j,k]
F2[k,i] g0_t(i) g1_t(j) g2_t(k) (term list from h5_multiscale.term_vectors, T included). Then
S = max_eps sum_{ijk} W_eps(i,j,k) F0[i,j] F1[j,k] F2[k,i] with W_eps = sum_t eps_t w_t g0_t g1_t g2_t,
and Hoelder for the measure |W_eps| on (i,j,k) gives
    |sum W F0 F1 F2| <= prod_v (sum |W| |F_v|^3)^(1/3) <= (M0 M1 M2)^(1/3) prod_v (sum |F_v|^3)^(1/3),
M0 = max_{ij} sum_k |W|, M1 = max_{jk} sum_i |W|, M2 = max_{ki} sum_j |W|. The ratio is
S / (2^N prod_v (sum |F_v|^3)^(1/3)), so ratio <= B_N with B_N^3 = max_eps M0 M1 M2 / 2^(3N), exact.
eps_T is fixed to +1 (eps and -eps give the same bound).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from fractions import Fraction
from pathlib import Path
from types import ModuleType
from typing import Any

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"

import numpy as np  # noqa: E402

LANE = Path(__file__).resolve().parent
REPO = LANE.parents[4]
NIGHT = REPO / "scripts" / "openai_math" / "hypotheses" / "night" / "h5_multiscale.py"
DYADIC = REPO / "scripts" / "openai_math" / "hypotheses" / "h5_dyadic.py"


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ms = _load("h5_multiscale_ro", NIGHT)


def weight_tensor_basis(n_res: int, haar: bool = True) -> np.ndarray:
    """G[t, i, j, k] = w_t g0_t(i) g1_t(j) g2_t(k) (int64); Haar-free replaces g by block indicators."""
    rows = []
    for wt, g0, g1, g2 in ms.term_vectors(n_res):
        if not haar:
            g0, g1, g2 = np.abs(g0), np.abs(g1), np.abs(g2)
        rows.append(wt * np.einsum("i,j,k->ijk", g0, g1, g2))
    return np.stack(rows).astype(np.int64)


def holder_bound(n_res: int, haar: bool = True, batch: int = 2**14, deadline: float | None = None) -> dict[str, Any]:
    """Exact max over eps (eps_T = +1) of M0 M1 M2; returns B^3 as a Fraction string and the argmax."""
    g = weight_tensor_basis(n_res, haar)
    t, size = g.shape[0], 2**n_res
    gf = g.reshape(t, -1).astype(np.float64)  # integer entries, |W| < 2^53: matmul exact in float64
    n_pat = 2 ** (t - 1)
    best, best_idx, best_m = -1, -1, (0, 0, 0)
    done = 0
    bits = np.arange(t - 1, dtype=np.int64)
    for lo in range(0, n_pat, batch):
        if deadline is not None and time.time() > deadline:
            break
        idx = np.arange(lo, min(lo + batch, n_pat), dtype=np.int64)
        eps = np.ones((idx.size, t), dtype=np.float64)
        eps[:, 1:] = 1 - 2 * ((idx[:, None] >> bits[None, :]) & 1)
        w = np.abs(eps @ gf).reshape(idx.size, size, size, size)
        m0 = np.rint(w.sum(axis=3).reshape(idx.size, -1).max(axis=1)).astype(np.int64)
        m1 = np.rint(w.sum(axis=1).reshape(idx.size, -1).max(axis=1)).astype(np.int64)
        m2 = np.rint(w.sum(axis=2).reshape(idx.size, -1).max(axis=1)).astype(np.int64)
        prod = [int(a) * int(b) * int(c) for a, b, c in zip(m0, m1, m2)]
        j = int(np.argmax(np.array(prod, dtype=object)))
        if prod[j] > best:
            best, best_idx, best_m = prod[j], int(idx[j]), (int(m0[j]), int(m1[j]), int(m2[j]))
        done = int(idx[-1]) + 1
    b3 = Fraction(best, size**3)
    return {"n_res": n_res, "haar": haar, "n_terms": t, "patterns_total": n_pat, "patterns_done": done, "complete": done == n_pat, "B_cubed": str(b3), "B_float": float(b3) ** (1.0 / 3.0), "argmax_pattern_index": best_idx, "argmax_M": list(best_m)}


def random_real_check(n_res: int, bound_cubed: Fraction, trials: int, seed: int) -> dict[str, Any]:
    """Validity spot check: h5_dyadic.ratio of random real inputs never exceeds B_N."""
    dy = _load("h5_dyadic_ro", DYADIC)
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(trials):
        a = [rng.standard_normal((2**n_res, 2**n_res)) * rng.exponential(1.0, (2**n_res, 2**n_res)) for _ in range(3)]
        worst = max(worst, float(dy.ratio(a, n_res, True)))
    return {"trials": trials, "seed": seed, "max_ratio": worst, "below_bound": worst <= float(bound_cubed) ** (1.0 / 3.0) + 1e-12}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--n", type=int, nargs="+", required=True)
    p.add_argument("--budget-s", type=float, default=470.0)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    t0 = time.time()
    out: dict[str, Any] = {"exploratory": True, "note": "deviations.md item 5; not part of the preregistered verdict"}
    # controls: N=1 bound must be exactly 1 (hand proof + exhaustive +-1 max 1); Haar-free bound must equal N + 1
    c1 = holder_bound(1)
    hf2 = holder_bound(2, haar=False)
    hf3 = holder_bound(3, haar=False)
    out["controls"] = {"N1_B_cubed": c1["B_cubed"], "haarfree_N2_B_cubed": hf2["B_cubed"], "haarfree_N3_B_cubed": hf3["B_cubed"]}
    out["controls"]["pass"] = c1["B_cubed"] == "1" and hf2["B_cubed"] == "27" and hf3["B_cubed"] == "64"
    results = []
    for n in args.n:
        r = holder_bound(n, deadline=t0 + args.budget_s)
        r["elapsed_s"] = round(time.time() - t0, 2)
        if r["complete"] and n <= 3:
            r["random_real_check"] = random_real_check(n, Fraction(r["B_cubed"]), 2000, 20261008 + n)
        results.append(r)
    out["results"] = results
    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
