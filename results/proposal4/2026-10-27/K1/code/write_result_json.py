"""Write K1/result.json: status, key numbers (read from the logs, not typed in), sha256 of every file."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    k1 = Path(sys.argv[1])
    repo = Path(sys.argv[2])
    tar_sha = sys.argv[3]
    L = k1 / "logs"
    pc = json.loads((L / "positive_control.json").read_text())["summary"]
    ex = json.loads((L / "exergy_table2.json").read_text())
    joint = json.loads((L / "scan_joint.json").read_text())["summary"]
    warm = json.loads((L / "warm_best.json").read_text())["rows"]
    h2 = json.loads((L / "h2_all.json").read_text())["summary"]
    viol = json.loads((L / "h2_violators.json").read_text())
    agree = json.loads((L / "surrogate_agreement.json").read_text())
    cert = json.loads((L / "cert_sign.json").read_text())
    lc = json.loads((L / "lean_core.json").read_text())
    lk = json.loads((L / "lean_controls.json").read_text())
    k = "T0=298.15"
    rows = ex["rows"]
    ratio = lambda key: [min(r[key]["benefit_ratio_cold_over_warm"] for r in warm),
                         max(r[key]["benefit_ratio_cold_over_warm"] for r in warm)]
    v298 = [v for v in viol if v["T0"] == 298.15 and v["violates_lowP"]]
    out = {
        "id": "K1", "status": "KEEP", "headline": "negative result: 'start cold' survives exergy accounting (H1 refuted)",
        "kill_criterion_fired": False,
        "paper_read": "arXiv 2501.04825v1 full text (alphaXiv); supplement not obtainable, not read",
        "dataset": {"zenodo": "10.5281/zenodo.14452152", "licence": "CC-BY-4.0", "code_licence": "NIST software",
                    "DAC_data.tar.gz_md5_matches_zenodo": "a2520f520140c60f8a4663d5b403966c",
                    "DAC_data.tar.gz_sha256": tar_sha},
        "positive_control": pc,
        "negative_controls": ex["controls"],
        "exergy_table2_T0_298": {
            "xi_fv_nominal_umol_per_J": [min(r["eval"]["xi_fv_umol_per_J"] for r in rows),
                                         max(r["eval"]["xi_fv_umol_per_J"] for r in rows)],
            "xi_nc_r0_umol_per_J": [min(r["eval"][k]["r=0.0"]["xi_umol_per_J"] for r in rows),
                                    max(r["eval"][k]["r=0.0"]["xi_umol_per_J"] for r in rows)],
            "B_rev_kJ_per_mol": [min(r["eval"][k]["r=1.0"]["B_per_mol_kJ"] for r in rows),
                                 max(r["eval"][k]["r=1.0"]["B_per_mol_kJ"] for r in rows)],
            "W_min_P0_kJ_per_mol": [min(r["eval"][k]["W_min_P0_kJ_per_mol"] for r in rows),
                                    max(r["eval"][k]["W_min_P0_kJ_per_mol"] for r in rows)],
            "refrigeration_share": [min(r["eval"][k]["refrigeration_share_of_B_NC"] for r in rows),
                                    max(r["eval"][k]["refrigeration_share_of_B_NC"] for r in rows)],
            "gate_pass": sum(r["gate_T0_298"]["ok"] for r in rows)},
        "H1_joint_scan_summary": joint,
        "cold_over_warm_ratio_T0_298": {"fv": ratio("fv"), "ex_r0": ratio("ex_298.15_0.0"),
                                         "ex_r0.5": ratio("ex_298.15_0.5"), "ex_r1": ratio("ex_298.15_1.0")},
        "H2": {"n_materials_with_valid_paths": h2["n_materials_with_valid_paths"], "n_paths": h2["n_paths"],
               "max_posterior_xi_umol_per_J": h2["max_posterior_xi_umol_per_J"],
               "n_materials_any_path_xi_gt_10_umol_per_J": len(h2["n_materials_xi_post_gt_10"]),
               "B_rev_below_W_min_lowP_T0_298_pairs": len(v298),
               "B_rev_below_W_min_lowP_T0_298_materials": sorted({v["name"] for v in v298}),
               "gate_failures_by_T0": h2["gate_failures"]},
        "surrogate": {"agreement": agree, "independent_float_check_failures": cert["independent_float_check_failures"],
                      "A_ex_lt_0_certified_volume_fraction (bisected N_ex = -A_ex > 0)": cert["A_ex_negative"]["frac_positive"]},
        "lean": {"core_rc": lc["rc"], "controls_rc": lk["rc"],
                 "core_axioms_lines": [l for l in lc["output"].splitlines() if "depends on axioms" in l],
                 "controls_axioms_lines": [l for l in lk["output"].splitlines() if "depends on axioms" in l],
                 "flag": "LEDGER_UNAUDITED_TIER_A (producer != verifier pending)"},
        "unit_slip": "text 'above 1.0 x 10^5 mol/J' consistent with 1.0 x 10^-5 mol/J (dataset units string 'mol/J', max 1.1259e-5)",
        "sha256": {},
    }
    files = sorted([p for p in k1.rglob("*") if p.is_file() and p.name != "result.json" and "__pycache__" not in p.parts])
    files += [repo / "formal_cert/Programmes/DacExergy/Core.lean", repo / "formal_cert/Programmes/DacExergy/Controls.lean"]
    for p in files:
        out["sha256"][str(p.relative_to(repo))] = sha(p)
    (k1 / "result.json").write_text(json.dumps(out, indent=1, default=float))
    print("files hashed", len(out["sha256"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
