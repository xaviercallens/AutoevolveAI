"""Debug probe: statuses of the two-sided map for van der Pol (instrument check)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
spec = importlib.util.spec_from_file_location("h4_v2", ROOT / "scripts/openai_math/hypotheses/night/h4_v2.py")
h4 = importlib.util.module_from_spec(spec)
sys.modules["h4_v2"] = h4
spec.loader.exec_module(h4)

vdp = h4.van_der_pol()
for y in (0.5, 1.0, 1.5, 2.0, 3.0, 6.0):
    f = h4.land(vdp, y, +1, "DOP853", 1e-12, 1e-14)
    b = h4.land(vdp, y, -1, "DOP853", 1e-12, 1e-14)
    print(y, f, b, h4.two_sided(vdp, y, "DOP853", 1e-12, 1e-14))
