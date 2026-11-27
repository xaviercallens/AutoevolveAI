#!/usr/bin/env python3
"""Evaluate pilot P3 (certified Hubble tension) against results/certified_numerics/P3_h0/preregistration.json."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
R = REPO / "results" / "certified_numerics" / "P3_h0"
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
TMP = Path("/home/callensxavier_gmail_com/.claude/jobs/6ecda88c/tmp")


def main() -> int:
    ax_out = json.loads((R / "compile_Axioms.json").read_text())["output"]
    ax = {l.split("'")[1]: [a.strip() for a in l.split("[")[1].rstrip("]").split(",")] for l in ax_out.splitlines() if "depends on axioms" in l}
    cert = {k: v for k, v in ax.items() if not k.startswith("ctl_")}
    boxes = json.loads((R / "boxes.json").read_text())
    box_rc = {}
    for b in boxes:
        f = R / f"compile_{b['name']}.json"
        box_rc[b["name"]] = json.loads(f.read_text())["rc"] if f.exists() else None
    main_rc = json.loads((R / "compile_Main.json").read_text())["rc"]
    point = json.loads((R / "point.json").read_text())
    c8 = json.loads((R / "c8.json").read_text())
    c9 = json.loads((TMP / "c9" / "plan.json").read_text())
    c10 = json.loads((TMP / "c10" / "plan.json").read_text())
    out = {
        "pilot": "P3",
        "H9": {"certified": "BAOCert.P3.Point.chi2tot_point" in cert, "U_tot": point["U_tot_float"],
               "point": {"Om": point["Om"], "h": point["h_float"], "omega_b": point["omega_b"]},
               "pass": "BAOCert.P3.Point.chi2tot_point" in cert and set(cert["BAOCert.P3.Point.chi2tot_point"]) <= ALLOWED},
        "H10": {"theorem": "BAOCert.P3.H0_ge_73_excluded", "corollary": "BAOCert.P3.H0_ge_73_delta_chi2",
                "statement": f"for all Om in [0,1], all omega_b, all h >= 0.73: chi2_total > {point['U_tot_float']} + 25",
                "main_rc": main_rc, "boxes": len(boxes), "boxes_rc0": sum(1 for v in box_rc.values() if v == 0),
                "axioms_ok": all(set(cert.get(n, ["missing"])) <= ALLOWED for n in ("BAOCert.P3.H0_ge_73_excluded", "BAOCert.P3.H0_ge_73_delta_chi2"))},
        "H11_H0_le_64": {"status": "NOT_ATTEMPTED"},
        "C8_rd_vs_python": {k: c8[k] for k in ("certified_lo", "certified_hi", "common_rd_aubourg16", "rel_width", "pass")},
        "C9_H0_ge_68.6_not_certifiable": {"boxes_tried": len(c9["leaves"]), "passed": sum(l["pass"] for l in c9["leaves"]),
                                         "pass": not all(l["pass"] for l in c9["leaves"]),
                                         "note": "planner stops at a 300-box budget; failures are the vertex condition B >= 0 (K0 above the parabola vertex)"},
        "C10_shifted_bbn_mean_0.0282": {"boxes_tried": len(c10["leaves"]), "passed": sum(l["pass"] for l in c10["leaves"]),
                                        "pass": not all(l["pass"] for l in c10["leaves"])},
        "C11_axiom_audit": {"n": len(cert), "all_whitelisted": all(set(v) <= ALLOWED for v in cert.values()),
                            "sorry_flagged": "sorryAx" in ax.get("ctl_sorry", []), "axiom_flagged": "ctl_cheat" in ax.get("ctl_axiom", [])},
        "scope": ["flat LCDM, radiation off", "Aubourg 2015 eq. 16 r_d fitting formula with fixed omega_nu (not CAMB)",
                  "Gaussian DESI DR2 BAO likelihood and Gaussian BBN prior 0.02218 +- 0.00055",
                  "Delta chi2 = 25 relative to a certified point; a certified version of a known tension, not a new measurement"],
    }
    out["H10"]["pass"] = bool(main_rc == 0 and out["H10"]["boxes_rc0"] == len(boxes) and out["H10"]["axioms_ok"])
    out["C11_axiom_audit"]["pass"] = all(out["C11_axiom_audit"][k] for k in ("all_whitelisted", "sorry_flagged", "axiom_flagged"))
    ctl = all(out[k]["pass"] for k in ("C8_rd_vs_python", "C9_H0_ge_68.6_not_certifiable", "C10_shifted_bbn_mean_0.0282", "C11_axiom_audit"))
    out["verdict"] = "VOID" if not ctl else ("P3_OK" if out["H9"]["pass"] and out["H10"]["pass"] else "P3_PARTIAL")
    (R / "result.json").write_text(json.dumps(out, indent=1) + "\n")
    (R / "c9_plan.json").write_text(json.dumps(c9, indent=1) + "\n")
    (R / "c10_plan.json").write_text(json.dumps(c10, indent=1) + "\n")
    print(json.dumps({k: (v.get("pass", v.get("status")) if isinstance(v, dict) else v) for k, v in out.items() if k != "scope"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
