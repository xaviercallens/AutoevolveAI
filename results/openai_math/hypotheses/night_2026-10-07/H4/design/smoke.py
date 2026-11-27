"""Smoke test of h4_v2 on tiny inputs (instrument check, not a lane result)."""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
spec = importlib.util.spec_from_file_location("h4_v2", ROOT / "scripts/openai_math/hypotheses/night/h4_v2.py")
h4 = importlib.util.module_from_spec(spec)
sys.modules["h4_v2"] = h4
spec.loader.exec_module(h4)

out: dict = {}
part = sys.argv[1] if len(sys.argv) > 1 else "basic"
if part == "basic":
    vdp = h4.van_der_pol()
    for m in ("Radau", "DOP853", "LSODA"):
        t = time.monotonic()
        tiny = h4.land(vdp, 2.0, +1, m, deadline_s=1e-4)
        out[f"tiny_deadline_{m}"] = tiny.status
        out[f"vdp_D_{m}"] = [h4.two_sided(vdp, y, m, 1e-10, 1e-12)[0] for y in (0.5, 1.0, 3.0)]
        out[f"secs_{m}"] = round(time.monotonic() - t, 2)
    r = h4.count_cycles(vdp, 1e-2, 20.0, grid=30)
    out["vdp_count_grid30"] = {"confirmed": r.confirmed, "unconf": len(r.unconfirmed), "s": r.seconds}
    c6 = [0.020730676912451174, -0.6971475182556305, -0.1326813907988433, 0.499665853088071]
    out["sdi_deg6_probe_f0"] = h4.sdi_profile(h4.f0_poly(c6))
    out["sdi_even_f0"] = h4.sdi_profile(h4.f0_poly([0.0, -0.7, 0.0, 0.5]))
    out["sdi_design_deg4_seed0_200"] = h4.sdi_design(4, 0, 200)["histogram"]
elif part == "curve":
    c6 = [0.020730676912451174, -0.6971475182556305, -0.1326813907988433, 0.499665853088071]
    f0 = h4.f0_poly(c6)
    eps = float(sys.argv[2])
    ylo, yhi = h4.canard_y_range(f0, eps)
    out["y_range"] = [ylo, yhi]
    import numpy as np
    t = time.monotonic()
    a_grid = np.linspace(-0.2, 0.2, 9)
    y = float(np.sqrt(ylo * yhi))
    vals = [h4.two_sided(h4.classical_coeffs(f0, float(a), eps), y)[0] for a in a_grid]
    out["D_vs_a_mid_y"] = {"y": y, "a": a_grid.tolist(), "D": vals, "s": round(time.monotonic() - t, 2)}
print(json.dumps(out, indent=1, default=float))
