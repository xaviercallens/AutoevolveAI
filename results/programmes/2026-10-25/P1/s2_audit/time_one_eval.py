"""Time one f0_e evaluation of the constants re-implementation (helper, no claims)."""
import sys
import time

sys.path.insert(0, "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/programmes/2026-10-25/P1/s2_audit")
import mpmath as mp  # noqa: E402
import constants_reimpl as cr  # noqa: E402

t0 = time.time()
m = cr.Model()
t1 = time.time()
v = m.f0_e(m.p + mp.mpf("0.03"))
t2 = time.time()
print({"model_init_s": round(t1 - t0, 2), "one_eval_s": round(t2 - t1, 3), "f0": mp.nstr(v[0], 12), "e": mp.nstr(v[1], 12)})
