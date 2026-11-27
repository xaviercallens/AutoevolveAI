import json
import sys
import time

sys.path.insert(0, "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/scripts/openai_math/lt_matrix")
import torch

torch.set_num_threads(2)
from kinetic_dual import PI2_4, run_search

t = time.time()
j, _ = run_search(3, 4, 96, 20.0, 2048, 2901)
out = "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/openai_math/hypotheses/night_2026-10-08/LT_C/timing_m3N4.json"
json.dump({"seed": 2901, "m": 3, "N": 4, "J": j, "excess": j / PI2_4 - 1, "seconds": time.time() - t}, open(out, "w"))
