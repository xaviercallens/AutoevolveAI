"""Build C1b/result.json: status, key numbers, sha256 of every code/data/log file (and of the compiled binary + geng sample files).
Usage: make_result_json.py <census_fast binary>"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WT = HERE.parents[4]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(name: str) -> dict | None:
    p = ROOT / "data" / name
    return json.load(open(p)) if p.exists() else None


def main() -> None:
    binary = Path(sys.argv[1])
    agg = load("census_n11_final.json")
    thr = load("throughput_sample11_1e7.json")
    val = load("validation_fast_vs_C1.json")
    ctl = load("controls_c1b.json")
    ctl1 = load("controls.json")
    rep = load("reproduce_c1.json")
    controls_ok = bool(val and val["all_ok"] and ctl and ctl["all_passed"] and ctl1 is not None and rep and rep["all_ok"])
    if ctl1 is not None:
        controls_ok = controls_ok and len(ctl1) == 14 and all(c["expected_outcome_met"] for c in ctl1)
    if agg is None:
        status = "RUNNING"
    elif agg["partial"] or not agg["count_equals_A001349"]:
        status = "PARTIAL"
    elif controls_ok:
        status = "KEEP"
    else:
        status = "DISCARD"
    key = {}
    if agg:
        key = {k: agg[k] for k in ("graphs", "count_equals_A001349", "excluded_certified_lt", "candidates", "near_graphs", "regular_graphs",
                                   "regular_equals_A005177", "count_gt_total", "count_eq_total", "count_lt_total",
                                   "exact_candidates_eq_nonregular", "guard_fail", "chol_fail", "max_eps", "only_richter",
                                   "richter_among_amplifiers", "amplifier_canonical_classes", "parts_done", "parts_missing")}
        key["amplifiers"] = [{k: a[k] for k in ("graph6", "N_eff", "N_eff_float", "degrees", "edges", "canonical_labelg")}
                             for a in agg["amplifiers"]]
        key["nearest_nonamplifiers_exact"] = [{k: a[k] for k in ("graph6", "N_eff", "N_eff_float", "source")}
                                              for a in agg["nearest_nonamplifiers_exact"][:5]]
    files = {}
    for sub in ("code", "data", "logs"):
        for p in sorted((ROOT / sub).rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                files[str(p.relative_to(ROOT))] = sha(p)
    if (ROOT / "RESULT.md").exists():
        files["RESULT.md"] = sha(ROOT / "RESULT.md")
    out = {
        "id": "C1b", "status": status, "preregistration": "docs/proposals/PROPOSAL_4_ADDENDUM_2_C1B_2026-10-27.md",
        "preregistration_sha256": sha(WT / "docs/proposals/PROPOSAL_4_ADDENDUM_2_C1B_2026-10-27.md"),
        "preregistration_sha256_recorded": json.load(open(WT / "results/proposal4/2026-10-27/addendum_2_C1b.json"))["sha256"],
        "controls_all_passed": controls_ok,
        "validation_fast_vs_C1_all_ok": bool(val and val["all_ok"]),
        "throughput": thr and {"python_projected_h_2cores": thr["python_C1_code"]["projected_total_h_on_2_cores"],
                               "fast_projected_h_2cores": thr["census_fast"]["projected_total_h_on_2_cores"],
                               "fast_graphs_per_s_core": thr["census_fast"]["graphs_per_s_one_core_wall"],
                               "python_graphs_per_s_core": thr["python_C1_code"]["graphs_per_s_one_core"],
                               "kill_triggered": thr["kill_triggered_for_fast_code"]},
        "key_numbers": key,
        "binary": {"path": str(binary.relative_to(WT)) if binary.is_relative_to(WT) else str(binary), "sha256": sha(binary),
                   "build": "gcc 11.4.0: gcc -O3 -march=native -Wall -Wextra -o census_fast code/census_fast.c -lm"},
        "scratch_sha256": {p.name: sha(p) for p in sorted((WT / ".scratchpad" / "C1b").glob("geng11_p*.g6"))}
        | {"sample11_1e7.g6": sha(WT / ".scratchpad" / "C1b" / "sample11_1e7.g6")},
        "files_sha256": files,
        "lean": {
            "theorems": ["AmplifierCensus.A1_amplifier", "AmplifierCensus.A2_amplifier", "AmplifierCensus.A3_amplifier",
                         "AmplifierCensus.R11_amplifier (C1)"],
            "compile_rc": {m: json.load(open(ROOT / "logs" / f"lean_{m}.json"))["rc"]
                           for m in ("DataA1", "DataA2", "DataA3", "Amplifiers11", "ControlsC1b")},
            "axioms_Amplifiers11": [ln for ln in json.load(open(ROOT / "logs" / "lean_Amplifiers11.json"))["output"].splitlines()
                                    if "depends on axioms" in ln],
            "leanchecker_rc": {e["module"]: e["rc"] for e in json.load(open(ROOT / "logs" / "leanchecker_replay.json"))},
            "files_sha256": {p.name: sha(p) for p in sorted((WT / "formal_cert/Programmes/AmplifierCensus").glob("*.lean"))},
            "producer_ne_verifier": "pending", "statement_lock": "none",
        },
        "literature_match": "the 4 classes equal Richter arXiv 2204.12861v1 p. 8 Fig. 1 (N_eff 11.0008, 11.0128, 11.0056, 11.0952)",
    }
    json.dump(out, open(ROOT / "result.json", "w"), indent=1)
    print(status, json.dumps(key)[:3000])


if __name__ == "__main__":
    main()
