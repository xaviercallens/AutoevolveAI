"""Summarise run_scan.py output: per-row optima and H1 counts (T1* >= T0)."""
from __future__ import annotations

import json
import sys

T0S = (273.15, 298.15, 313.15)
RS = (0.0, 0.5, 1.0)


def main() -> int:
    d = json.load(open(sys.argv[1]))
    verbose = len(sys.argv) > 2
    summary = {}
    for part in ("table2", "sample"):
        rows = d.get(part, [])
        if not rows:
            continue
        s = {"n_rows": len(rows)}
        for tag in ("constrained", "unconstrained"):
            fv_ok = 0
            fv_n = 0
            for x in rows:
                b = x[tag]["fv"]
                if b is None:
                    continue
                fv_n += 1
                if abs(b["T1"] - x["T1_stored"]) <= 15.0 or b["T1"] <= 201.0 + 15.0 * 0:
                    fv_ok += 1
            s[f"{tag}_facevalue_control_pass"] = [fv_ok, fv_n]
            s[f"{tag}_facevalue_T1star_below_273"] = sum(1 for x in rows if x[tag]["fv"] and x[tag]["fv"]["T1"] < 273.15)
            for T0 in T0S:
                for r in RS:
                    k = f"ex_{T0}_{r}"
                    vals = [x[tag][k] for x in rows if x[tag].get(k)]
                    s[f"{tag}_{k}_T1star_ge_T0"] = [sum(1 for v in vals if v["T1"] >= T0), len(vals)]
            s[f"{tag}_ratio_xi_ex298r0_over_fv_at_optima"] = None
        summary[part] = s
        if verbose:
            for x in rows:
                c, u = x["constrained"], x["unconstrained"]
                f = lambda b: None if b is None else (round(b["T1"], 1), round(b["xi"], 2), round(b["purity"], 5))
                print(part, x["name"], "T1st", round(x["T1_stored"], 1), "Tend", round(x["Tend"], 1), "| C fv", f(c["fv"]),
                      "ex298r0", f(c["ex_298.15_0.0"]), "ex298r1", f(c["ex_298.15_1.0"]), "| U fv", f(u["fv"]),
                      "ex298r0", f(u["ex_298.15_0.0"]), "ex298r1", f(u["ex_298.15_1.0"]))
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
