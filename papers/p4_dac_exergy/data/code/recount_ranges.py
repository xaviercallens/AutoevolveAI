"""Paper-side recount of ranges quoted in the text from the K1 logs (read-only; writes data/recount_ranges.json).
Usage: python -I recount_ranges.py <logs_dir> <out.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    logs = Path(sys.argv[1])
    s = json.loads((logs / "scan_joint.json").read_text())["rows"]
    w = json.loads((logs / "warm_best.json").read_text())["rows"]
    e = json.loads((logs / "exergy_table2.json").read_text())["rows"]
    out: dict[str, object] = {}
    t1_all: list[float] = []
    for part in ("unconstrained", "constrained"):
        for row in s:
            for k, v in row[part].items():
                if k != "fv":
                    t1_all.append(v["T1"])
    out["T1_star_exergy_min_max_all_18_variants_14_rows"] = [min(t1_all), max(t1_all)]
    out["n_variants_checked"] = len({(p, k) for p in ("unconstrained", "constrained") for k in s[0][p] if k != "fv"})
    fv_te = [r["unconstrained"]["fv"]["Tend"] for r in s]
    r0_te = [r["unconstrained"]["ex_298.15_0.0"]["Tend"] for r in s]
    out["Tend_fv_unconstrained_min_max"] = [min(fv_te), max(fv_te)]
    out["Tend_ex298_r0_unconstrained_min_max"] = [min(r0_te), max(r0_te)]
    out["fv_T1_star_max"] = max(r["unconstrained"]["fv"]["T1"] for r in s)
    for key in ("fv", "ex_298.15_0.0", "ex_298.15_0.5", "ex_298.15_1.0"):
        rs = [x[key]["benefit_ratio_cold_over_warm"] for x in w]
        out["ratio_" + key] = [min(rs), max(rs)]
    out["rows_P1_below_101325"] = sum(1 for r in e if float(r["row"][4]) < 101325)
    out["rows_P1_below_101325_range"] = [min(float(r["row"][4]) for r in e if float(r["row"][4]) < 101325),
                                         max(float(r["row"][4]) for r in e if float(r["row"][4]) < 101325)]
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
