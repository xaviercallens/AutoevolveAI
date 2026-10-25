#!/usr/bin/env python3
"""Check every quantitative claim in Paper J against the artifact behind it.

The terminal gate before deposit, as for Paper I. Two kinds of claim are checked:

* **Static claims** written into the paper by hand -- the kernel-gate table, the
  exactness counts, the landscape summary -- each traced to the artifact that
  measured it.
* **Generated sections** -- the Rust ladder and the hill-climb comparison -- which
  `fill_paper_j_results.py` renders from artifacts. Here the check is that no
  placeholder remains and that every rate in the artifact appears verbatim in
  the TeX, so a stale fill cannot ship.

Exit nonzero on any mismatch, because the point is to block a deposit.

Usage:
    .venv/bin/python scripts/verify_paper_j_claims.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, List, Tuple

REPO = Path(__file__).resolve().parents[1]
PAPER = (REPO / "sub_projects" / "socrateai_scientific_genetic" / "SocrateAI-Scientific-Genetic"
         / "papers" / "PaperJ_Kernel_Gated_Evolution_Foundation.tex")
RESULTS = REPO / "results"


def load(name: str) -> dict[str, Any]:
    path = RESULTS / f"{name}.json"
    if not path.exists():
        raise RuntimeError(f"artifact missing: {path}")
    return json.loads(path.read_text())


def static_claims(tex: str) -> List[Tuple[str, Any, Any, str]]:
    rows: List[Tuple[str, Any, Any, str]] = []
    atom = load("lean_atomicity_is_the_wrapper")
    # The one-invocation gate table.
    by_false = {r["actually_false"]: r for r in atom["measured"]}
    for k, wall in ((0, "10.38"), (1, "10.21"), (2, "10.88"), (4, "12.73"), (8, "14.19")):
        rows.append((f"gate invocations at {k} false", 1, by_false[k]["invocations"], "atomicity"))
        rows.append((f"gate wall clock at {k} false", wall, f"{by_false[k]['wall_clock_s']:.2f}",
                     "atomicity"))
        rows.append((f"no false accepted at {k}", [], by_false[k]["false_accepted"], "atomicity"))
    rows.append(("single-candidate median s", "6.36",
                 f"{atom['reference_single_candidate_median_s']:.2f}", "atomicity"))
    rows.append(("eight individual proofs s", "50.88",
                 f"{8 * atom['reference_single_candidate_median_s']:.2f}", "atomicity"))
    # Landscape summary.
    cliff = load("gp_landscape_cliff")
    widths = [r["basin_width_in_mutations"] for r in cliff["rungs"]]
    rows.append(("basin width mostly 4", True, sorted(widths).count(4) >= 4, "landscape"))
    neutral = [r["neutrality_at_solution"] for r in cliff["rungs"]]
    rows.append(("neutrality within 5-8%", True,
                 min(neutral) >= 0.045 and max(neutral) <= 0.085, "landscape"))
    k1 = [r["walk_away_from_solution"][0]["ratio_to_random_median"] for r in cliff["rungs"]]
    rows.append(("k=1 ratios within 0.61-0.91", True,
                 round(min(k1), 2) >= 0.60 and round(max(k1), 2) <= 0.92, "landscape"))
    # Exactness counts quoted from the Python prototype's recorded runs.
    wall = load("semantic_backprop_and_the_wall")
    rows.append(("v* verified pairs", "24303 of 24303",
                 wall["the_identity_that_motivated_it"]["verified"].split(" (")[0], "wall"))
    rows.append(("inert fraction", 0.048, wall["the_identity_that_motivated_it"]["inert_pairs"], "wall"))
    pg = REPO / "formal" / "ANSE" / "AlixPopulationGenetics.lean"
    if pg.exists():
        n = sum(1 for line in pg.read_text().splitlines() if line.startswith("#print axioms"))
        rows.append(("H11/H12 Lean declarations", 16, n, "AlixPopulationGenetics.lean"))
        rows.append(("H11/H12 file has no sorry", True, "sorry" not in pg.read_text().split("-/", 1)[1], "AlixPopulationGenetics.lean"))
    return rows


def generated_sections(tex: str) -> List[str]:
    """Strings that must appear verbatim once the sections are filled."""
    must: List[str] = []
    ladder = load("kge_rust_ladder")
    for r in ladder["rungs"]:
        must.append(f"{r['solved']}/{ladder['parameters']['seeds']}")
        must.append(f"{r['solve_rate']:.3f}")
    gate = load("kge_rust_gate")
    t = gate["totals"]
    must.append(f"{t['accepted_by_kernel']}/{t['distinct_candidates_gated']}")
    must.append(f"{t['invocations']} invocations")
    climb_path = RESULTS / "kge_rust_hillclimb.json"
    if climb_path.exists():
        climb = json.loads(climb_path.read_text())
        for r in climb["rungs"]:
            must.append(f"{r['ga_rate']:.3f} & {r['descent_rate']:.3f} & {r['restarts_rate']:.3f}")
    # Hub benchmark: every method's rate per law, and the gate totals.
    sel_path = RESULTS / "kge_hf_selection.json"
    if sel_path.exists():
        sel = json.loads(sel_path.read_text())
        must.append(f"{sel['fitting_grammar']} of {sel['total_problems']}")
        for prob in sel["selected_top"]:
            name = prob["problem"].replace("-", "_").replace(".", "_")
            p = RESULTS / f"kge_hf_{name}.json"
            if p.exists():
                res = json.loads(p.read_text())
                m = {x["method"]: x for x in res["methods"]}
                must.append(f"{m['kge_mutation_selection']['rate']:.2f}")
                must.append(f"{m['hillclimb_with_restarts']['rate']:.2f} & {m['random_search']['rate']:.2f}")
    ll_path = RESULTS / "kge_lifetime_learning.json"
    if ll_path.exists():
        ll = json.loads(ll_path.read_text())
        for r in ll["rungs"]:
            must.append(f"{r['none_rate']:.3f} & {r['baldwin_rate']:.3f} & {r['lamarck_rate']:.3f}")
            must.append(f"{r['baldwin_only']} / {r['none_only']}")
        cm_path = RESULTS / "kge_rust_ladder_costmatched.json"
        if cm_path.exists():
            for r in json.loads(cm_path.read_text())["rungs"]:
                must.append(f"{r['solve_rate']:.3f}")
        bg = RESULTS / "kge_baldwin_gate.json"
        if bg.exists():
            t = json.loads(bg.read_text())["totals"]
            must.append(f"All {t['accepted_by_kernel']} of the {t['distinct_candidates_gated']} distinct")
    vp = RESULTS / "kge_variance_prediction.json"
    if vp.exists():
        for r in json.loads(vp.read_text())["rungs"]:
            hz = r["hazard"]
            must.append(f"{hz['solves_uncollapsed']}/{hz['exposure_uncollapsed']:,}")
            must.append(f"{hz['exact_binomial_p']:.2g}")
            must.append(f"{r['immigration_only']} / {r['baldwin_only']}")
    gate_path = RESULTS / "kge_hf_gate.json"
    if gate_path.exists():
        t = json.loads(gate_path.read_text())["totals"]
        must.append(f"{t['accepted_by_kernel']} of {t['distinct_candidates_gated']} distinct solutions proved")
    return must


def main() -> int:
    tex = PAPER.read_text()
    rows = static_claims(tex)
    mismatches = [r for r in rows if str(r[1]) != str(r[2])]
    print(f"{len(rows)} static claims checked against artifacts")
    print(f"  matched : {len(rows) - len(mismatches)}")
    print(f"  MISMATCH: {len(mismatches)}")
    for label, paper, art, src in mismatches:
        print(f"    {label}: paper={paper!r} artifact={art!r} ({src})")

    failed = bool(mismatches)
    if "pending at the time of drafting" in tex:
        print("\nresults sections NOT YET FILLED (placeholders remain) -> refusing deposit")
        failed = True
    else:
        must = generated_sections(tex)
        absent = [s for s in must if s not in tex]
        print(f"\n{len(must)} generated-section strings checked; absent: {absent or 'none'}")
        failed = failed or bool(absent)

    print("\n" + ("REFUSING DEPOSIT" if failed else "all claims trace to an artifact"))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
