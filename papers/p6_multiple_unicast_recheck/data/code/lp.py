"""A11: undirected unit-capacity max concurrent flow LP on G with the 157 sessions (HiGHS, floating). Tier X."""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction

HERE = "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal6/2026-11-03/AIC-MUC9"
sys.path.insert(0, HERE + "/code")
sys.path.insert(0, "/home/callensxavier_gmail_com/muc9_thirdparty")
from appendixA_transcribed import R  # noqa: E402
from muc9lib import build_T, build_graph  # noqa: E402
from flow import max_concurrent  # noqa: E402

T = build_T()
edges, _ = build_graph(T)
Rs = set(R)
phys = [edges[q] for q in range(910) if q not in Rs]
pairs = json.load(open("/home/callensxavier_gmail_com/muc9_thirdparty/sessions_B_derived.json"))
sessions = [(v[0], v[1], 1.0) for v in pairs.values()]
t0 = time.time()
lam, msg = max_concurrent(182, phys, False, sessions, time_limit=1500.0)
bound = 147 / 157
out = {"edges": len(phys), "sessions": len(sessions), "num_source_groups": len({s for s, _, _ in sessions}),
       "lp_lambda": lam, "lp_status": msg, "bound_147_over_157": bound, "lp_le_bound_plus_1e-7": lam <= bound + 1e-7,
       "ratio_lp_over_bound": lam / bound, "lp_lambda_as_fraction_limit_1000": str(Fraction(lam).limit_denominator(2000)),
       "seconds": time.time() - t0}
print(json.dumps(out, indent=1))
json.dump(out, open(HERE + "/data/lp_result.json", "w"), indent=1)
