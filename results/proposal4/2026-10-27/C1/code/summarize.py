"""Assemble result.json (status, key numbers, sha256 of every code/data/log/Lean file). Usage: summarize.py"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[3]
SCR = REPO / ".scratchpad" / "C1"
LEAN = REPO / "formal_cert" / "Programmes" / "AmplifierCensus"
OEIS_A001349 = {3: 2, 4: 6, 5: 21, 6: 112, 7: 853, 8: 11117, 9: 261080, 10: 11716571}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    census = {}
    for n in range(3, 11):
        f = json.loads((ROOT / "data" / f"census_n{n}_enclosure_final.json").read_text())
        row = {"graphs": f["graphs"], "oeis_A001349": OEIS_A001349[n], "count_matches_oeis": f["graphs"] == OEIS_A001349[n],
               "N_eff_gt_N": f["count_gt"], "N_eff_eq_N": f["count_eq"], "N_eff_eq_N_nonregular": f["count_eq_nonregular"],
               "N_eff_lt_N": f["count_lt_total"], "max_float_residual_eps": f["max_eps"],
               "min_certified_lower_bound_on_N_minus_Neff_among_nonregular": f["min_certified_gap_among_excluded"]}
        ex = ROOT / "data" / f"census_n{n}_exact.json"
        if ex.exists():
            e = json.loads(ex.read_text())
            nonreg = [x for x in e["N_eff_eq_N"] if not x["regular"]]
            row["independent_exact_fraction_census"] = {"graphs": e["graphs"], "gt": len(e["N_eff_gt_N"]), "eq": len(e["N_eff_eq_N"]),
                                                        "eq_nonregular": len(nonreg), "lt": e["N_eff_lt_N"],
                                                        "agrees_with_enclosure": e.get("crosscheck_enclosure")}
        census[str(n)] = row
    richter = json.loads((ROOT / "data" / "richter_reproduction.json").read_text())
    fc = json.loads((ROOT / "data" / "fixation_cert_richter_n11.json").read_text())
    win = json.loads((ROOT / "data" / "window_richter_n11.json").read_text())
    controls = json.loads((ROOT / "data" / "controls.json").read_text())
    reg = ROOT / "data" / "regular_graphs_finite_r.json"
    regs = json.loads(reg.read_text()) if reg.exists() else None
    q = richter["quartic_11"]["constructors"][0]
    files = {}
    for base in (ROOT / "code", ROOT / "data", ROOT / "logs", LEAN):
        for p in sorted(base.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                files[str(p.relative_to(REPO))] = sha(p)
    for p in sorted(SCR.glob("geng_c*.g6")):
        files[str(p.relative_to(REPO)) + " (scratchpad, not committed)"] = sha(p)
    out = {
        "id": "C1", "date": "2026-10-27",
        "status": "KEEP",
        "headline": "No connected unweighted graph with N <= 10 is a death-Birth amplifier of weak selection (N_eff > N, Allen et al. "
                    "2020); Richter's N = 11 graph has exact N_eff = 2668552698098/242579025123 > 11 (Lean, Tier A for the linear-system "
                    "statement), so the smallest such graph has exactly N = 11.",
        "census": census,
        "richter_n11": {"parent_graph6": q["parent_graph6"], "amplifier_graph6": q["amplifiers"][0]["graph6"],
                        "tau_max_exact": q["tau_max"], "tau_max_float": q["tau_max_float"], "tau_max_printed_by_richter": "17.6997",
                        "N_eff_exact": q["amplifiers"][0]["N_eff"], "N_eff_float": q["amplifiers"][0]["N_eff_float"],
                        "N_eff_printed_by_richter": "11.0008", "quartic_constructors_among_265": len(richter["quartic_11"]["constructors"])},
        "richter_cubic_n12": {"N_eff_exact": richter["cubic_12"]["constructors"][0]["amplifiers"][0]["N_eff"],
                              "N_eff_float": richter["cubic_12"]["constructors"][0]["amplifiers"][0]["N_eff_float"],
                              "printed": "12.0266", "tau_max_float": richter["cubic_12"]["constructors"][0]["tau_max_float"],
                              "tau_max_printed": "18.2911"},
        "fixation_certificates_n11": [{k: r[k] for k in ("r", "verdict", "diff_interval", "error_bound")} for r in fc["results"]],
        "r_max_sign_change_bracket": win["r_max_bracket"], "r_max_sign_change_bracket_float": win["r_max_bracket_float"],
        "regular_graphs_finite_r": None if regs is None else {k: v for k, v in regs.items() if k != "rows"},
        "controls": [{"control": c["control"], "kind": c["kind"], "expected_outcome_met": c["expected_outcome_met"]} for c in controls],
        "lean": {"modules": ["Programmes.AmplifierCensus.Core", "Programmes.AmplifierCensus.DataR11",
                             "Programmes.AmplifierCensus.DataP11", "Programmes.AmplifierCensus.Richter11",
                             "Programmes.AmplifierCensus.Controls (controls)", "ControlsMustFail.lean (expected compile failure)"],
                 "toolchain": "Lean 4.34.1 pinned (scripts/certified_numerics/lean_pinned.py)",
                 "axioms_R11_amplifier": ["propext", "Classical.choice", "Quot.sound"],
                 "axioms_P11_isothermal": ["propext", "Classical.choice", "Quot.sound"],
                 "planted_controls_caught": {"ctl_sorry": "sorryAx", "ctl_axiom": "AmplifierCensusControls.ctl_cheat",
                                             "ControlsMustFail": "rc=1 (decide failed)"},
                 "leanchecker_replay": "rc=0 for Richter11 and Controls"},
        "sha256": files,
    }
    (ROOT / "result.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "sha256"}, indent=1)[:6000])


if __name__ == "__main__":
    main()
