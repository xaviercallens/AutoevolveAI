"""Tier X: step-size dependence of the central differences used in m1_selfcheck.py (one point, Riesz 3)."""
from __future__ import annotations

import json
import sys

sys.path.insert(0, "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal4/2026-10-27/M1/code")
import m1_selfcheck as S  # noqa: E402


def main() -> None:
    for h in (3e-2, 1e-2, 3e-3, 1e-3, 3e-4):
        Dp, D0, Dm = (S.direct_B("riesz3", 0.0, 300.0, 0, 0.6, 0.4, t) for t in (h, 0.0, -h))
        print(h, ((Dp - Dm) / (2 * h)).round(6), ((Dp - 2 * D0 + Dm) / h ** 2).round(5))
    d = json.load(open(sys.argv[1]))
    r = d["rows"][2]
    print("ball", r["ball_mid"]["B1"], r["ball_mid"]["B2"])


if __name__ == "__main__":
    main()
