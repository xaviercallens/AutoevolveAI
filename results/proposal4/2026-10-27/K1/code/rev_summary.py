"""Revision 2026-10-27: compact per-row and aggregate summary of rev_analyse.py output (for the paper tables).

Usage: python -I rev_summary.py <analysis.json> <out_summary.json>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def g(v: float | None, n: int = 3) -> float | None:
    return None if v is None else round(v, n)


def main() -> int:
    d = json.loads(Path(sys.argv[1]).read_text())
    rows = []
    for x in d["rows"]:
        a = x["air"]
        e = x["eps_star"]
        h = x["eta"]
        rows.append({
            "row": f"{x['name']} {x['xi_pub']}", "purity_min": g(x["purity_min"], 4),
            "vacuous_T0": {k: v["vacuous"] for k, v in x["vacuity"].items()},
            "best_warm_purity_298": g(x["vacuity"]["298.15"]["best_warm_purity"], 3),
            "base_T1star_U_298_r0": x["base_T1star"]["U_298.15_0.0"]["T1"],
            "base_T1star_range_18": [min(v["T1"] for v in x["base_T1star"].values() if v),
                                     max(v["T1"] for v in x["base_T1star"].values() if v)],
            "base_ratio_v1": {k: g(x["base_ratio"][f"{k}_v1"]["ratio"], 3) for k in ("fv", "r0", "r05", "r1")},
            "air_eps0": {r: {"T1star": g(a[f"298.15_{r}_0.0"]["T1star"], 2), "outcome": a[f"298.15_{r}_0.0"]["outcome"],
                             "ratio_v1": g(a[f"298.15_{r}_0.0"]["ratio_v1"], 4),
                             "ratio_d10": g(a[f"298.15_{r}_0.0"]["ratio_d10"], 3),
                             "ratio_aud": g(a[f"298.15_{r}_0.0"]["ratio_aud"], 3)} for r in ("0.0", "0.5", "1.0")},
            "eps_star_d10": {r: g(e[f"298.15_{r}_d10"]["p_star"], 3) for r in ("0.0", "0.5", "1.0")},
            "eps_star_aud": {r: g(e[f"298.15_{r}_aud"]["p_star"], 3) for r in ("0.0", "0.5", "1.0")},
            "eps_star_d10_notes": {r: e[f"298.15_{r}_d10"]["note"] for r in ("0.0", "0.5", "1.0")},
            "eps_star_d10_crossings": {r: e[f"298.15_{r}_d10"]["crossings"] for r in ("0.0", "0.5", "1.0")},
            "eta_noair_R_r1_aud": g(h["R_eps1.0_r1.0_aud"]["p_star"], 3),
            "eta_noair_R_r0_aud": g(h["R_eps1.0_r0.0_aud"]["p_star"], 3),
            "eta_noair_R_r1_d10": g(h["R_eps1.0_r1.0_d10"]["p_star"], 3),
            "eta_noair_S_r1_d10": [g(h["S_eps1.0_r1.0_d10"]["p_star"], 3), h["S_eps1.0_r1.0_d10"]["note"],
                                   g(h["S_eps1.0_r1.0_d10"]["ratio_at_lo"], 3), g(h["S_eps1.0_r1.0_d10"]["ratio_at_hi"], 3)],
            "eta_air0_R_r0_d10": [g(h["R_eps0.0_r0.0_d10"]["p_star"], 3), h["R_eps0.0_r0.0_d10"]["note"]],
            "eta_air0_S_r0_d10": [g(h["S_eps0.0_r0.0_d10"]["p_star"], 3), h["S_eps0.0_r0.0_d10"]["note"]],
            "eta_air0_S_r1_d10": [g(h["S_eps0.0_r1.0_d10"]["p_star"], 3), h["S_eps0.0_r1.0_d10"]["note"]],
            "eps_star_eta0.5": {k: g(v["p_star"], 3) for k, v in x["eps_star_eta0.5"].items()},
            "neg": {k: v["detected_warm"] for k, v in x["neg_control"].items()},
        })
    agg = d["aggregate"]
    keep = {k: v for k, v in agg.items() if not k.startswith("air_") or k.split("_")[1] == "298.15"
            or k.endswith("_0.0")}
    out = {"meta": d["meta"], "aggregate": keep, "rows": rows}
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, default=float))
    for r in rows:
        print(json.dumps(r, default=float))
    for k in ("base_T1star_range_all_18", "vacuous_row_T0", "variants_total", "constrained_variants_vacuous",
              "informative_variants", "neg_control_rows_detected", "free_refrigeration_sanity_all_rows"):
        print(k, agg[k])
    for k in sorted(agg):
        if k.startswith("base_ratio_"):
            print(k, agg[k])
    for T0 in ("273.15", "298.15", "313.15"):
        for r in ("0.0", "0.5", "1.0"):
            for eps in ("0.0", "0.8", "0.9", "1.0"):
                a = agg[f"air_{T0}_{r}_{eps}"]
                print("air", T0, r, eps, a["outcomes"], "T1*", [round(v, 2) for v in a["T1star_range"]],
                      "d10", [round(v, 3) for v in a["ratio_d10_range"]], "warm-wins d10", len(a["rows_warm_wins_d10"]))
    print(json.dumps(agg.get("auditor_comparison_[auditor, producer_revision]"), default=float, indent=0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
