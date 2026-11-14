"""Projected remaining compute from measured per-unit compile times.

Per-unit times come from (a) the hand tests (one row / node / cell per stage, compiled while the machine ran at load
average 15-17 on 8 cores with about two Lean processes per core on cores 0-3, so wall time overstates CPU time by up
to about 2x), and (b) the scheduler's finished chunks (wall and user time; user time is recorded since 11:16).
Range: low = measured wall / 2, high = measured wall (core-hours, one core per worker).
Usage: make_projection.py GG_ROW_WALL_S"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dump2io import Dump2  # noqa: E402
from l1common import CONT  # noqa: E402

STATUS = Path("/home/callensxavier_gmail_com/a1l1_oleans/status")


def done_and_left(stage: str) -> tuple[float, float, int, int]:
    wall = user = 0.0
    ok = left = 0
    for f in STATUS.glob(f"{stage}__*.json"):
        st = json.loads(f.read_text())
        if st.get("state") == "ok":
            ok += 1
            wall += float(st.get("wall_s") or 0)
            user += float(st.get("user_s") or 0)
    man = json.loads((CONT / "manifests" / f"{stage}.json").read_text())
    total = len(man["chunks"]) + len(man.get("core", []))
    left = total - ok
    return wall, user, ok, left


def main() -> int:
    gg_row = float(sys.argv[1])
    d = Dump2(want={"node"})
    segs = [d.node[i][0] for i in range(len(d.node))]
    first = 1562
    n_by = {s: sum(1 for i in range(first, len(segs)) if segs[i - 1] == s or (segs[i - 1] == 0 and i == first)) for s in range(0, 7)}
    table_units = {"seg1": sum(1 for i in range(first, len(segs)) if segs[i - 1] in (0, 1)),
                   "seg2": sum(1 for i in range(first, len(segs)) if segs[i - 1] == 2),
                   "seg3_5": sum(1 for i in range(first, len(segs)) if segs[i - 1] >= 3)}
    per = {"bdsup_row": 1210.4, "inside_hess_row": 7784.3, "global_grid_row": gg_row,
           "table_seg1_node": 784.8, "table_seg2_node": 1906.2, "table_seg3_5_node": 2898.0, "table_seg0_file16": 74.9}
    stages = {}
    w, u, ok, left = done_and_left("core_test")
    # remaining core_test: segment-4 cells (3 per file) at the hand-tested 193.6 s per cell, others at the measured mean
    ct_left_s = 0.0
    for f in (CONT / "manifests" / "core_test.json",):
        man = json.loads(f.read_text())
        for c in man["chunks"]:
            st = json.loads((STATUS / (c["id"].replace("/", "__") + ".json")).read_text()) if (STATUS / (c["id"].replace("/", "__") + ".json")).exists() else {}
            if st.get("state") == "ok":
                continue
            name = c["id"].split("/")[1]
            if name.startswith("S4"):
                ct_left_s += 3 * 193.6
            elif name.startswith("S2"):
                ct_left_s += 80.5
            else:
                ct_left_s += 150.0
    stages["cs"] = {"done": True, "measured_wall_core_h": round(done_and_left("cs")[0] / 3600, 2)}
    stages["core_test"] = {"chunks_ok": ok, "chunks_left": left, "done_wall_core_h": round(w / 3600, 2),
                           "left_core_h": [round(ct_left_s / 2 / 3600, 1), round(ct_left_s / 3600, 1)]}
    for st_name, rows, key in (("bdsup", 519, "bdsup_row"), ("inside_hess", 601, "inside_hess_row"), ("global_grid", 2186, "global_grid_row")):
        tot = rows * per[key]
        stages[st_name] = {"rows": rows, "measured_row_wall_s": per[key], "core_h": [round(tot / 2 / 3600), round(tot / 3600)]}
    ttot = (table_units["seg1"] * per["table_seg1_node"] + table_units["seg2"] * per["table_seg2_node"]
            + table_units["seg3_5"] * per["table_seg3_5_node"] + (first // 16 + 1) * per["table_seg0_file16"])
    stages["table"] = {"nodes": table_units, "measured_node_wall_s": {k: v for k, v in per.items() if k.startswith("table")},
                       "core_h": [round(ttot / 2 / 3600), round(ttot / 3600)]}
    lo = sum(s["core_h"][0] for k, s in stages.items() if "core_h" in s) + stages["core_test"]["left_core_h"][0]
    hi = sum(s["core_h"][1] for k, s in stages.items() if "core_h" in s) + stages["core_test"]["left_core_h"][1]
    out = {"method": __doc__.split("Usage")[0].strip(), "per_unit_wall_s": per, "stages": stages,
           "remaining_core_h": [round(lo), round(hi)],
           "days_at_4_workers": [round(lo / 4 / 24, 1), round(hi / 4 / 24, 1)],
           "days_at_5_workers_memory_capped_8_cores": [round(lo / 5 / 24, 1), round(hi / 5 / 24, 1)],
           "days_if_8_workers_fit": [round(lo / 8 / 24, 1), round(hi / 8 / 24, 1)],
           "table_nodes_by_left_segment": n_by}
    (CONT / "projection.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["remaining_core_h"]), json.dumps({k: v.get("core_h", v.get("left_core_h")) for k, v in stages.items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
