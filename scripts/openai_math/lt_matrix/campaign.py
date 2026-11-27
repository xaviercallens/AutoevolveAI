#!/usr/bin/env python3
"""Adversarial campaign against the matrix Lieb-Thirring claim (one lane = one (gamma, m, family) cell).

Maieutics rules (Elenchus docs/MAIEUTICS.md): fixed budget in restarts, immutable evaluator (instrument.py, sha256 recorded),
mechanical keep/discard, every row logged, a winner is a setting not a finding.  The only edits a lane may make are the
INIT FAMILY and the BASIS SIZES, below; the metric and the verdict rule are frozen.

Families (initialisations of the potential, all parametrised through Blobs so that W = B^dagger B >= 0):
  random      random coefficients, kappa ~ 1.5 e^{0.5 N}, centres ~ N(0, 3)
  embed       exact scalar optimiser in channel 1, small random matrix perturbation (tests local optimality)
  rotpair     two rank-one solitons with different orientation angle theta and separation d (non-commuting at overlap)
  twist       one rank-one soliton whose direction rotates slowly with x (non-abelian twist)
Refinement of every candidate whose lower bound exceeds L1 (1 + 1e-7): (a) grid doubled in M and Q, (b) independent finite
differences with Richardson extrapolation.  Verdict is CERTIFIED only if both agree and the excess survives.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
from scipy.sparse import coo_matrix, diags, identity, kron
from scipy.sparse.linalg import eigsh

sys.path.insert(0, str(Path(__file__).resolve().parent))
from instrument import (Blobs, Grid, numerator_denominator, optimise, ratio, semiclassical_constant, sharp_constant,  # noqa: E402
                        verdict)

HERE = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_init(family: str, gamma: float, m: int, seed: int, K: int, P: int) -> Blobs:
    rng = np.random.default_rng(seed)
    mdl = Blobs(m, K, P, seed)
    with torch.no_grad():
        if family == "random":
            return mdl
        r = 1.0 / (gamma - 0.5)
        mdl.cr.zero_(); mdl.ci.zero_()
        mdl.logk.fill_(math.log(r)); mdl.x0.zero_()
        mdl.cr[0, 0, 0, 0] = math.sqrt(r + 1)
        if family == "embed":
            mdl.cr.add_(0.05 * torch.randn_like(mdl.cr)); mdl.ci.add_(0.05 * torch.randn_like(mdl.ci))
            mdl.logk.add_(0.05 * torch.randn_like(mdl.logk))
        elif family == "rotpair" and K >= 2:
            theta = float(rng.uniform(0.2, 1.4)); d = float(rng.uniform(0.3, 3.0)) / r
            u2 = torch.tensor([math.cos(theta), math.sin(theta)] + [0.0] * (m - 2))
            mdl.x0[0], mdl.x0[1] = -d / 2, d / 2
            mdl.logk[1] = math.log(r)
            for a in range(m):  # B2 = sqrt(r+1) sech(.) e_{1} u2^T  (rank one with direction u2)
                mdl.cr[1, 0, a, 0] = math.sqrt(r + 1) * float(u2[a])
            mdl.cr[0, 0, 0, 0] = math.sqrt(r + 1)
        elif family == "twist":
            theta1 = float(rng.uniform(0.1, 1.0))
            mdl.cr[0, 0, 0, 0] = math.sqrt(r + 1) * math.cos(0.5 * theta1)
            if m >= 2:
                mdl.cr[0, 0, 1, 0] = math.sqrt(r + 1) * math.sin(0.5 * theta1)
                mdl.cr[0, 0, 1, 1] = float(rng.normal(0, 0.3))
                mdl.cr[0, 0, 0, 1] = float(rng.normal(0, 0.3))
        mdl.cr.add_(0.01 * torch.randn_like(mdl.cr))
    return mdl


def fd_ratio(model: Blobs, gamma: float, L: float, n: int) -> float:
    """Independent second-order finite-difference Dirichlet solver with Richardson extrapolation (not one-sided)."""
    m = model.m

    def eigs(nn: int) -> np.ndarray:
        h = 2 * L / (nn + 1)
        x = torch.tensor(-L + h * np.arange(1, nn + 1))
        with torch.no_grad():
            W = model.W(x).numpy()  # (nn, m, m)
        lap = diags([np.ones(nn - 1), -2 * np.ones(nn), np.ones(nn - 1)], [-1, 0, 1]) / h**2
        Hs = kron(-lap, identity(m)).tocsr()  # index (i, a) -> i * m + a, grid point major
        idx = np.arange(nn)
        rows = np.concatenate([idx * m + a for a in range(m) for b in range(m)])
        cols = np.concatenate([idx * m + b for a in range(m) for b in range(m)])
        vals = np.concatenate([W[:, a, b] for a in range(m) for b in range(m)])
        V = coo_matrix((vals, (rows, cols)), shape=(nn * m, nn * m)).tocsr()
        H = (Hs - V).tocsc()
        shift = -float(np.abs(W).max()) * m - 1.0
        k = 24
        while True:
            vals_k = np.sort(eigsh(H, k=k, sigma=shift, which="LM", return_eigenvectors=False))
            if vals_k[-1] > 0 or k >= 160:
                break
            k *= 2
        return vals_k[vals_k < 0]

    e1, e2 = eigs(n), eigs(2 * n)
    kk = min(len(e1), len(e2))
    extrap = (4 * e2[:kk] - e1[:kk]) / 3.0
    num = float(np.sum((-extrap) ** gamma))
    xq, wq = np.polynomial.legendre.leggauss(6000)
    x = torch.tensor(L * xq)
    with torch.no_grad():
        lam = torch.linalg.eigvalsh(model.W(x)).clamp(min=0.0).numpy()
    den = float(np.sum(L * wq[:, None] * lam ** (gamma + 0.5)))
    return num / den


def refine(model: Blobs, gamma: float, grid: Grid) -> dict:
    with torch.no_grad():
        r_base = ratio(model.W(grid.x), gamma, grid)
        g2 = grid.refined()
        r_fine = ratio(model.W(g2.x), gamma, g2)
    try:
        r_fd = fd_ratio(model, gamma, grid.L, 6000)
    except Exception as exc:  # recorded, never silently dropped
        r_fd = float("nan")
        err = str(exc)[:200]
    else:
        err = ""
    return {"R_base": r_base, "R_refined_grid": r_fine, "R_fd_richardson": r_fd, "fd_error": err}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gamma", type=float, required=True)
    ap.add_argument("--m", type=int, required=True)
    ap.add_argument("--family", default="random", choices=["random", "embed", "rotpair", "twist"])
    ap.add_argument("--K", type=int, default=2)
    ap.add_argument("--P", type=int, default=8)
    ap.add_argument("--seed0", type=int, default=0)
    ap.add_argument("--restarts", type=int, default=20)
    ap.add_argument("--budget-s", type=float, default=1500.0)
    ap.add_argument("--M", type=int, default=160)
    ap.add_argument("--L", type=float, default=24.0)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--threads", type=int, default=2)
    args = ap.parse_args()
    torch.set_num_threads(args.threads)
    grid = Grid(args.L, args.M, 1200 if args.M <= 200 else 2400)
    L1, Lcl = sharp_constant(args.gamma), semiclassical_constant(args.gamma)
    rows, best, t0 = [], None, time.time()
    for i in range(args.restarts):
        if time.time() - t0 > args.budget_s:
            break
        seed = args.seed0 + i
        init = make_init(args.family, args.gamma, args.m, seed, args.K, args.P)
        r, model = optimise(args.gamma, args.m, grid, seed, K=args.K, P=args.P, init=init)
        excess = r / L1 - 1.0
        row = {"seed": seed, "family": args.family, "R": r, "excess": excess, "verdict": verdict(r, L1)}
        if excess > 1e-7:
            row["refinement"] = refine(model, args.gamma, grid)
        rows.append(row)
        if best is None or r > best["R"]:
            best = {"R": r, "seed": seed, "excess": excess}
            torch.save({k: v.detach() for k, v in model.state_dict().items()}, args.out.with_suffix(f".best_seed{seed}.pt"))
    flagged = [r for r in rows if r["excess"] > 1e-7]
    result = {
        "gamma": args.gamma, "m": args.m, "family": args.family, "K": args.K, "P": args.P, "grid": {"L": args.L, "M": args.M},
        "L1": L1, "Lcl": Lcl, "restarts_done": len(rows), "best": best, "n_flagged_above_1e-7": len(flagged),
        "instrument_sha256": sha(HERE / "instrument.py"), "campaign_sha256": sha(HERE / "campaign.py"),
        "elapsed_s": round(time.time() - t0, 1), "rows": rows,
        "summary_verdict": ("CANDIDATE_VIOLATION_NEEDS_REFINEMENT_REVIEW" if flagged else "NO_VIOLATION_FOUND"),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("gamma", "m", "family", "restarts_done", "best", "n_flagged_above_1e-7", "summary_verdict", "elapsed_s")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
