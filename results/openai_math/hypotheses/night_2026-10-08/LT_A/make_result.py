import json
from pathlib import Path

lane = Path(__file__).resolve().parent
c = json.loads((lane / "cell_summary.json").read_text())
keys = ("gamma", "family", "K", "P", "M", "restarts", "flagged", "best_excess", "closeness_below_L1", "verdict", "seconds")
cells = {k: {x: v[x] for x in keys} for k, v in c.items()}
res = {
    "lane": "LT_A", "hypothesis": "H-LT1 (m=2)", "date": "2026-10-08",
    "controls_all_pass": json.loads((lane / "controls.json").read_text()).get("all_pass"),
    "lane_verdict": "NO_VIOLATION_FOUND in all cells (not a proof)",
    "total_restarts": sum(v["restarts"] for v in c.values()), "total_flagged": sum(v["flagged"] for v in c.values()),
    "n_cells": len(c),
    "recheck_grid3": "no flagged restart, nothing to recheck (recheck_grid3.json is an empty list)",
    "search_power_note": "twist family best cells stall 2.8e-7..6.4e-7 below L1 after 24-36 restarts, and consecutive extra chunks did not raise them (saturated); the instrument resolution is about 1e-6, so nothing above the 1e-7 flag was ever seen",
    "deviations": "deviations.md D1-D3", "cells": cells,
}
(lane / "result.json").write_text(json.dumps(res, indent=1) + "\n")
print(res["total_restarts"], res["total_flagged"], res["controls_all_pass"], res["n_cells"])
