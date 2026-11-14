#!/usr/bin/env python3
"""Control C4 for P2 (untrusted cross-check through the rusty-SUNDIALS MCP server).

1. chi2 at the fit point (Om = 0.29743, h r_d = 101.543) from the MCP tool `bao_distances` (chi2_dr2 = true).
2. Profile chi2_min(Om) = min over h r_d in [50, 200] (golden-section, the tool's allowed range) on an Om grid,
   written to results/certified_numerics/P2_likelihood/mcp_profile.json for comparison with the certified slab bounds.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mcp_sundials_client import Client  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "results" / "certified_numerics" / "P2_likelihood" / "mcp_profile.json"


def chi2(c: Client, om: float, hrd: float) -> float:
    res = c.request("tools/call", {"name": "bao_distances", "arguments": {"model": "lcdm", "Om": om, "h_rd": hrd, "z": [0.51], "chi2_dr2": True}})
    text = res["content"][0]["text"]
    data = json.loads(text)
    return float(data["chi2_dr2"]["value"])


def golden(f, a: float, b: float, tol: float = 1e-4) -> tuple[float, float]:
    g = (math.sqrt(5) - 1) / 2
    c, d = b - g * (b - a), a + g * (b - a)
    fc, fd = f(c), f(d)
    while b - a > tol:
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - g * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + g * (b - a)
            fd = f(d)
    x = (a + b) / 2
    return x, f(x)


def main() -> int:
    c = Client()
    try:
        probe = c.request("tools/call", {"name": "bao_distances", "arguments": {"model": "lcdm", "Om": 0.29743, "h_rd": 101.543, "z": [0.51], "chi2_dr2": True}})
        raw = probe["content"][0]["text"]
        fit = chi2(c, 0.29743, 101.543)
        grid = [round(0.01 * k, 2) for k in range(1, 101)] + [round(0.24 + 0.002 * k, 3) for k in range(61)]
        prof = {}
        for om in sorted(set(grid)):
            hrd, val = golden(lambda h: chi2(c, om, h), 50.0, 200.0)
            prof[str(om)] = {"h_rd_min": hrd, "chi2_min": val, "at_range_edge": hrd < 50.5 or hrd > 199.5}
        OUT.write_text(json.dumps({"tool": "sundials-mcp bao_distances (rusty-SUNDIALS PR #63 worktree, radiation off)",
                                   "raw_probe": raw[:2000], "chi2_fit_point": fit, "profile": prof}, indent=1) + "\n")
        print(json.dumps({"chi2_fit_point": fit, "n_grid": len(prof), "min": min(prof.items(), key=lambda kv: kv[1]["chi2_min"])}))
    finally:
        c.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
