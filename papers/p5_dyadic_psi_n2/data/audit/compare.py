import json
import sys
from pathlib import Path

L = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal5/2026-10-27/DH-Psi2")
summ = json.loads((L / "data/summary.json").read_text())["modes"]
mapping = {"gauge_haar.json": {"wT=1": "R", "wT=3": "PSI", "wT=4": "PLANT4"},
           "gauge_haarfree.json": {"wT=1": "HF_R", "wT=3": "HF_PSI"}}
for fn, mm in mapping.items():
    p = Path("/tmp/dhaudit") / fn
    if not p.exists() or p.stat().st_size == 0:
        print(fn, "not ready")
        continue
    g = json.loads(p.read_text())
    for key, mode in mm.items():
        mine = g["modes"][key]
        prod = summ[mode]["c_int_enumeration"]["hist"]
        prodp = summ[mode]["python_kernel"]["hist"]
        scaled = {k: v * 512 for k, v in mine["hist"].items()}
        print(mode, "pairs", g["pairs"], "max_S", mine["max_S"], "recheck", mine["argmax_recheck"],
              "pairs_gt192", mine["pairs_gt192"], "x512", mine["pairs_gt192"] * 512,
              "pairs_at_max", mine["pairs_at_max"], "x512", mine["pairs_at_max"] * 512,
              "F2max_sum", mine["F2_maximisers_summed_over_max_pairs"],
              "full_F_at_max(x2^11)", mine["F2_maximisers_summed_over_max_pairs"] * 2048,
              "hist_x512==C", scaled == {k: int(v) for k, v in prod.items()},
              "hist_x512==py", scaled == {k: int(v) for k, v in prodp.items()})
