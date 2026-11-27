"""Assemble ../result.json from the logs (numbers read from files, not retyped) and the sha256 table."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
L = ROOT / "logs"


def load(name: str) -> dict:
    return json.loads((L / name).read_text())


def main() -> None:
    g = load("certify.json")  # final clean end-to-end run of the hashed e1_certify.py
    pb = g
    ns = g["pB11"]
    wm = load("certify_wang_mix.json")
    lean = load("lean_runner_core.json")
    lc = load("lean_controls.json")
    sha = load("sha256.json")
    out = {
        "id": "E1",
        "status": "PARTIAL",
        "status_reason": ("certified-numeric gate PASS and both negative controls rejected; but BH/NS coefficients pinned from the "
                          "preregistered fallback (W-H public code), not primary papers; enclosures are Tier C (Arb, not Lean-replayed); "
                          "updated fit = Wang 2026 (deviation); no independent verifier yet"),
        "tiers": {"enclosures": "C", "lean_lemmas": "A pending independent verification", "fits": "L (secondary: author code; Wang 2026 primary)",
                  "float_checks": "X"},
        "E1a_positive_control": {"gate": g["gate_positive"], "authors_code_model": {k: g["positive"][k] for k in ("T_ign", "TP_Tmin", "TP_min", "LP_Tmin", "LP_min")},
                                 "constant_hull": {k: g["positive"]["hull"][k] for k in ("T_ign", "TP_min", "LP_min")},
                                 "dt_variants": pb["dt_variants"]},
        "negative_controls": {"NC1_reactivity_x0.5": g["gate_NC1"], "NC2_no_bremsstrahlung": g["gate_NC2"],
                              "lean_controls_rc": lc["rc"]},
        "E1b_theta_star": {"NS_box": ns["NS_theta_star_box"], "NS_WHmix": ns["NS_theta_star_WHmix"],
                           "Wang_box": pb["pB11"]["Wang2026_theta_star_box"],
                           "Wang_WHmix_scan": {k: {kk: v[kk] for kk in ("L", "U", "certified_below_1", "witness_above_1")} for k, v in wm.items() if k != "grid_nodes"},
                           "box": {"T_i_keV": [50, 500], "x_nB_over_ni": [0.05, 0.5]}},
        "E1c_TeEqTi": {"NS_box_maxR": [ns["NS_theta1_box"]["L"], ns["NS_theta1_box"]["U"]],
                       "NS_WHmix_maxR": [ns["NS_theta1_WHmix"]["L"], ns["NS_theta1_WHmix"]["U"]],
                       "Wang_box_maxR": [pb["pB11"]["Wang2026_theta1_box"]["L"], pb["pB11"]["Wang2026_theta1_box"]["U"]],
                       "Wang_WHmix_maxR": [pb["pB11"]["Wang2026_theta1_WHmix"]["L"], pb["pB11"]["Wang2026_theta1_WHmix"]["U"]],
                       "m_star_NS": [1 / ns["NS_theta1_box"]["U"], 1 / ns["NS_theta1_box"]["L"]],
                       "m_star_Wang": pb["pB11"]["Wang2026_m_star"],
                       "Wang_over_NS_points": pb["pB11"]["Wang_over_NS_points"],
                       "conclusion": "no ideal-ignition window at T_e = T_i on the box under either fit (certified)"},
        "lean": [{k: r[k] for k in ("theorem_name", "compiled_successfully", "axioms", "has_sorry")} for r in lean],
        "papers_read": ["Wurzel-Hsu 2105.10954 (partial: physics sections + App. C/D; data tables not read)",
                        "Ochs-Fisch 2310.18508 (full)", "Sikora-Weller 2016 JFE 35:538 (full, CC-BY)",
                        "Wang-Li-Wu-Cui 2601.00241 (full)"],
        "not_obtained": ["Bosch-Hale 1992 (closed)", "Nevins-Swain 2000 (abstract only)", "Putvinski 2019 (OCR summaries only)",
                         "Tentori-Belloni 2023 (bot-blocked)"],
        "sha256": sha,
    }
    (ROOT / "result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print("result.json written;", len(sha), "hashed files")


if __name__ == "__main__":
    main()
