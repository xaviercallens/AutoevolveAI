"""M1 development probe (supports nothing): widths and timing of single cells of the second-order cell rule.

usage: python -I m1_cellprobe.py POT PARAM QMAX ALPHA H_DENOM
"""
from __future__ import annotations

import sys
import time
from fractions import Fraction

sys.path.insert(0, "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal4/2026-10-27/M1/code")
import m1_certify as M  # noqa: E402


def main() -> None:
    pot, par, qmax, alpha, hd = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
    t_build = time.time()
    model, info = M.build(pot, par, M.N2.q_arb("1/100000"), qmax, M.N2.q_arb(alpha))
    print("build", round(time.time() - t_build, 1), "s pairs", len(model.ns), info, flush=True)
    h = Fraction(1, hd)
    for tri, s0, t0 in ((0, Fraction(0), Fraction(1, 2)), (0, Fraction(1, 8), Fraction(1, 2)), (0, Fraction(1, 2), Fraction(1, 2)),
                        (0, Fraction(7, 8), Fraction(0)), (1, Fraction(15, 16), Fraction(1, 2)), (1, Fraction(1, 2), Fraction(1, 4))):
        t1 = time.time()
        r = model.cell2(tri, s0, t0, h)
        dt = time.time() - t1
        if r["ok"]:
            print(tri, s0, t0, "width/area", float(r["width"]) / float(h * h), "g/area", float(r["g"].mid()) / float(h * h),
                  "lmin", float(r["lmin"].lower()), f"{dt:.2f}s", flush=True)
        else:
            print(tri, s0, t0, "FAIL", r.get("why"), f"{dt:.2f}s", flush=True)


if __name__ == "__main__":
    main()
