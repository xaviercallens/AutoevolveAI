"""Exploratory supplement to H-LT2 (not preregistered): where does the non-commutativity of KILLED rows sit?"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch

REPO = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
sys.path.insert(0, str(REPO / "scripts/openai_math/lt_matrix"))
from instrument import Blobs  # noqa: E402
from structure_lt2 import commutator_statistic, w_on_grid  # noqa: E402

ROOT = REPO / "results/openai_math/hypotheses/night_2026-10-08"
rows = json.loads((ROOT / "LT_C/h_lt2.json").read_text())["rows"]
out = []
for r in rows:
    if r["status"] != "KILLED":
        continue
    cell_path = next(ROOT.glob(f"LT_*/**/{r['cell']}"))
    cell = json.loads(cell_path.read_text())
    model = Blobs(cell["m"], cell["K"], cell["P"], seed=0)
    model.load_state_dict(torch.load(cell_path.with_suffix(f".best_seed{r['seed']}.pt")))
    W = w_on_grid(model, cell["grid"]["L"], 2001)
    rec = {"cell": r["cell"], "gamma": r["gamma"], "family": r["family"], "seed": r["seed"],
           "R_over_L1": r["R_over_L1"], "C_0.001": r["C"]}
    for rel in (1e-2, 1e-1, 5e-1):
        rec[f"C_{rel:g}"] = commutator_statistic(W, rel_region=rel)["C"]
    ev = np.linalg.eigvalsh(W)
    tr = np.trace(W, axis1=1, axis2=2).real
    rec["second_channel_weight"] = float(ev[:, -2].sum() / tr.sum())
    out.append(rec)
(ROOT / "LT_C/h_lt2_explore.json").write_text(json.dumps(out, indent=1))
print(len(out))
