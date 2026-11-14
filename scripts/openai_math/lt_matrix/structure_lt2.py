"""H-LT2 instrument: commutator statistic and pointwise eigenvalue structure of near-maximisers of the matrix LT search.

Reads cell JSONs written by scripts/openai_math/lt_matrix/campaign.py (m, K, P, grid.L, best seed, L1, best R) and the
matching `<cell>.best_seed<seed>.pt` state dicts (only the best restart of a cell is stored), rebuilds `Blobs`, and
evaluates W(x) on a fine uniform grid. Statistic (frozen before the files are read):

    region S = {x : tr W(x) > 1e-3 * max_x tr W(x)}
    C = max_{x,y in S} ||[W(x), W(y)]||_2 / (||W(x)||_2 ||W(y)||_2)      (operator 2-norms)
    n_eig(x) = #{eigenvalues of W(x) above 1e-6 * max_{x} lambda_max(W(x))}

Every restart row with R >= (1 - 1e-3) L1 is a near-maximiser (analysed iff its .pt file exists); R >= (1 - 1e-4) L1 is strong.
C is the full pairwise maximum over the n_grid-point uniform grid (no subsampling); eigenvalue threshold relative to the global max.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from instrument import Blobs  # noqa: E402


def w_on_grid(model: Blobs, L: float, n: int) -> np.ndarray:
    x = torch.linspace(-L, L, n, dtype=torch.float64)
    with torch.no_grad():
        return model.W(x).numpy()


def commutator_statistic(W: np.ndarray, rel_region: float = 1e-3, max_points: int | None = None) -> dict:
    """W (n, m, m) Hermitian PSD samples. Returns C, the region size, and the pointwise eigenvalue-count profile."""
    tr = np.trace(W, axis1=1, axis2=2).real
    idx = np.where(tr > rel_region * tr.max())[0]
    if max_points is not None and len(idx) > max_points:
        idx = idx[np.linspace(0, len(idx) - 1, max_points).astype(int)]
    S = W[idx]
    norms = np.linalg.norm(S, ord=2, axis=(1, 2))
    best = 0.0
    for a in range(len(idx)):
        comm = S[a][None] @ S - S @ S[a][None]
        c = np.linalg.norm(comm, ord=2, axis=(1, 2)) / (norms[a] * norms)
        best = max(best, float(c.max()))
    ev = np.linalg.eigvalsh(W)
    top = ev.max()
    counts = (ev > 1e-6 * top).sum(axis=1)
    inreg = np.where(tr > rel_region * tr.max())[0]
    return {"C": best, "region_points_used": int(len(idx)), "n_eig_min": int(counts[inreg].min()), "n_eig_max": int(counts[inreg].max()),
            "n_eig_hist": {int(k): int((counts[inreg] == k).sum()) for k in np.unique(counts[inreg])}}


def analyse_cell(cell_json: Path, n_grid: int = 2001) -> list[dict]:
    """One record per restart row with R >= (1 - 1e-3) L1; restarts whose parameters were not stored are listed as such."""
    cell = json.loads(cell_json.read_text())
    outs = []
    for row in cell["rows"]:
        ratio = row["R"] / cell["L1"]
        if ratio < 1 - 1e-3:
            continue
        pt = cell_json.with_suffix(f".best_seed{row['seed']}.pt")
        out = {"cell": cell_json.name, "m": cell["m"], "gamma": cell["gamma"], "family": cell["family"], "seed": row["seed"],
               "R": row["R"], "L1": cell["L1"], "R_over_L1": ratio}
        if not pt.exists():
            out["status"] = "PARAMETERS_NOT_STORED"
            outs.append(out)
            continue
        model = Blobs(cell["m"], cell["K"], cell["P"], seed=0)
        model.load_state_dict(torch.load(pt))
        st = commutator_statistic(w_on_grid(model, cell["grid"]["L"], n_grid))
        strong = ratio >= 1 - 1e-4
        out.update(st)
        out["strong_near_maximiser"] = bool(strong)
        out["status"] = "KILLED" if (strong and st["C"] > 0.05) else ("PREDICTION_HOLDS" if st["C"] < 0.01 else "INTERMEDIATE")
        outs.append(out)
    return outs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    cells = sorted(p for p in a.cells_dir.rglob("*.json") if "best_seed" not in p.name and "rows" in p.read_text()[:100000] and '"summary_verdict"' in p.read_text())
    rows = [r for p in cells for r in analyse_cell(p)]
    a.out.write_text(json.dumps({"n_cells": len(rows), "rows": rows}, indent=2) + "\n")
    print(json.dumps({"n_cells": len(rows), "statuses": [r["status"] for r in rows]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
