"""Revision 2026-10-27 (audit items B1 and N5): (i) drift of the Table 1 exergy numbers on the 14 stored Table 2
paths between the v1 step-3 trapezoid and the revised right-point rule (run_exergy_table2.py run twice), and
(ii) the share of each face-value term in the published E_total on the 14 stored paths (own code, stored terms).

Usage: python -I rev_table1_compare.py <DAC_data dir> <positive_control.json> <exergy_table2 v1.json>
       <exergy_table2 right.json> <out.json>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_data import Dataset  # noqa: E402
from stored import terms_from_stored  # noqa: E402


def main() -> int:
    ds = Dataset(Path(sys.argv[1]))
    pc = json.loads(Path(sys.argv[2]).read_text())
    old = json.loads(Path(sys.argv[3]).read_text())
    new = json.loads(Path(sys.argv[4]).read_text())
    outp = Path(sys.argv[5])
    drift = []
    worst = 0.0
    for a, b in zip(old["rows"], new["rows"]):
        d = {"row": a["row"][:2]}
        for T0 in ("298.15", "273.15", "313.15"):
            ea, eb = a["eval"][f"T0={T0}"], b["eval"][f"T0={T0}"]
            for r in ("r=0.0", "r=0.5", "r=1.0"):
                xa, xb = ea[r]["xi_umol_per_J"], eb[r]["xi_umol_per_J"]
                rel = abs(xb - xa) / abs(xa)
                worst = max(worst, rel)
                if T0 == "298.15":
                    d[f"xi_{r}_v1"] = xa
                    d[f"xi_{r}_v2"] = xb
                    d[f"rel_{r}"] = rel
            if T0 == "298.15":
                d["refr_share_v1"] = ea["refrigeration_share_of_B_NC"]
                d["refr_share_v2"] = eb["refrigeration_share_of_B_NC"]
                d["B_rev_kJ_v2"] = eb["r=1.0"]["B_per_mol_kJ"]
                d["W_min_P0_kJ"] = eb["W_min_P0_kJ_per_mol"]
        d["gate_v2_ok"] = b["gate_T0_298"]["ok"]
        d["G2_closure_v2"] = b["gate_T0_298"]["numbers"]["sorb_closure_rel"]
        drift.append(d)
    shares = []
    for row in pc["rows"]:
        name = row["row"][0].replace(" ", "_")
        t = terms_from_stored(ds.optimized(name), row["solution_index"])
        E = t.E
        s = {"row": row["row"][:2],
             "Q_ads_step1": (t.Q_ads_co2 + t.Q_ads_n2) / E, "W_ads_step1": (t.W_ads_co2 + t.W_ads_n2) / E,
             "Q_des_step2": float(np.nansum(t.Q_des_co2 + t.Q_des_n2)) / E,
             "W_des_step2": float(np.nansum(t.W_des_co2 + t.W_des_n2)) / E,
             "E_heat_gas": float(np.nansum(t.E_heat_co2 + t.E_heat_n2)) / E,
             "E_heat_sorb": float(np.nansum(t.E_heat_sorb)) / E, "E_P": float(np.nansum(t.E_P)) / E}
        s["ads_plus_des_heats"] = s["Q_ads_step1"] + s["Q_des_step2"]
        shares.append(s)
    summ = {"max_rel_xi_drift_all_T0_r_rows": worst,
            "refr_share_v2_range": [min(d["refr_share_v2"] for d in drift), max(d["refr_share_v2"] for d in drift)],
            "xi_nc_v2_range": [min(d["xi_r=0.0_v2"] for d in drift), max(d["xi_r=0.0_v2"] for d in drift)],
            "xi_rev_v2_range": [min(d["xi_r=1.0_v2"] for d in drift), max(d["xi_r=1.0_v2"] for d in drift)],
            "B_rev_v2_range_kJ": [min(d["B_rev_kJ_v2"] for d in drift), max(d["B_rev_kJ_v2"] for d in drift)],
            "gate_v2_pass_rows": sum(1 for d in drift if d["gate_v2_ok"]),
            "G2_closure_v2_max": max(d["G2_closure_v2"] for d in drift),
            "share_sorb_heat_range": [min(s["E_heat_sorb"] for s in shares), max(s["E_heat_sorb"] for s in shares)],
            "share_ads_plus_des_range": [min(s["ads_plus_des_heats"] for s in shares),
                                         max(s["ads_plus_des_heats"] for s in shares)]}
    outp.write_text(json.dumps({"summary": summ, "drift": drift, "shares": shares}, indent=1, default=float))
    print(json.dumps(summ, indent=1, default=float))
    for s in shares:
        print(s["row"][0], s["row"][1], {k: round(v, 3) for k, v in s.items() if k != "row"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
