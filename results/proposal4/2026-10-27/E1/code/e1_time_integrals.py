"""Timing probe for the certified Maxwellian integrals (no claims)."""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1_model import arb, wang_reactivity  # noqa: E402


def main() -> None:
    for T in ("50", "250", "500"):
        for goal in (30, 40):
            t0 = time.time()
            v = wang_reactivity(arb(T), prec_goal=goal)
            print(T, goal, v, round(time.time() - t0, 2), "s rel.rad", float(v.rad() / v.mid()))


if __name__ == "__main__":
    main()
