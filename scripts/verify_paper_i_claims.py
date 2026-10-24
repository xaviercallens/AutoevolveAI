#!/usr/bin/env python3
"""Check every quantitative claim in Paper I against the artifact behind it.

The terminal gate before deposit. This project has twice published figures that
did not match the artifact they came from -- a mislabelled index that reached two
DOIs, and near-miss figures emitted from a superseded code path -- so a paper is
not deposited until each number in it has been traced back to the file that
produced it. Prose is not checked; numbers are.

A mismatch is a hard failure and exits nonzero, because the point is to block a
deposit rather than to produce a report someone reads afterwards.

Usage:
    .venv/bin/python scripts/verify_paper_i_claims.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Tuple

REPO = Path(__file__).resolve().parents[1]
SUBPROJECT = (
    REPO / "sub_projects" / "socrateai_scientific_genetic" / "SocrateAI-Scientific-Genetic"
)
PAPER = SUBPROJECT / "papers" / "PaperI_Recombination_Does_Not_Help_Lean4.tex"

ARTIFACTS = (
    "lean_gated_recombination",
    "lean_gated_recombination_homology",
    "lean_gated_recombination_contribution",
    "lean_gated_recombination_calibration",
    "lean_atomicity_is_the_wrapper",
    "lean_batching",
    "lean_batching_bisection",
)

# Strings that must appear verbatim in the TeX. A claim can match its artifact in
# this script and still be absent from the paper, or present in a stale form, so
# the paper's own text is checked too.
MUST_APPEAR = (
    "94/200", "58/200", "70/200", "79/200",
    r"2.98\times10^{-4}",
    "0.238", "0.408", "0.019", "0.959",
    "0.5117", "0.5196", r"94\,872",
    # Edition 2.
    "73/200", "52/200", "0.136", "0.835", "0.576", "1614", "1011",
)


def load() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name in ARTIFACTS:
        path = REPO / "results" / f"{name}.json"
        if not path.exists():
            raise RuntimeError(f"artifact missing: {path}")
        out[name] = json.loads(path.read_text())
    return out


def collect(art: dict[str, Any]) -> List[Tuple[str, Any, Any, str]]:
    """(label, value as written in the paper, value from the artifact, source)."""
    rows: List[Tuple[str, Any, Any, str]] = []
    main = art["lean_gated_recombination"]
    hom = art["lean_gated_recombination_homology"]
    results = main["results"]
    seeds = main["parameters"]["seeds"]

    rows += [
        ("mutation solved", "94/200", f"{results['mutation_only_solved']}/{seeds}", "main"),
        ("crossover solved", "58/200", f"{results['crossover_solved']}/{seeds}", "main"),
        ("mutation median evals", "1286.5", results["mutation_only_median_evaluations"], "main"),
        ("crossover median evals", "1269.0", float(results["crossover_median_evaluations"]), "main"),
        ("paired pairs", "35", results["paired_seeds_both_solved"], "main"),
        ("crossover cheaper on", "18", results["crossover_cheaper_on"], "main"),
        ("paired ratio", "0.959",
         round(results["paired_median_ratio_crossover_over_mutation"], 3), "main"),
        ("fisher p solve rate", "2.98e-04",
         f"{main['statistics']['solve_rate']['fisher_exact_two_sided_p']:.2e}", "main"),
        ("sign test p", "1.000",
         f"{main['statistics']['paired_evaluations']['sign_test_two_sided_p']:.3f}", "main"),
    ]

    per_arm = hom["per_arm"]
    for arm, solved, tree in (
        ("mutation_only", "94", "48000"),
        ("crossover", "58", "48000"),
        ("homologous_crossover", "70", "94872"),
        ("anti_homologous_crossover", "79", "94812"),
    ):
        rows.append((f"{arm} solved", solved, per_arm[arm]["solved"], "homology"))
        rows.append((f"{arm} tree-point evals", tree,
                     int(per_arm[arm]["median_tree_point_evaluations"]), "homology"))

    tests = hom["verdict"]["tests"]
    for key, want in (
        ("homologous_vs_random_crossover", "0.238"),
        ("anti_vs_homologous", "0.408"),
        ("mutation_vs_homologous", "0.019"),
        ("mutation_vs_anti", "0.158"),
    ):
        rows.append((f"p {key}", want, f"{tests[key]['p']:.3f}", "homology"))

    confound = hom["verdict"]["confound_excluded_quantitatively"]
    rows += [
        ("fallback homologous %", "2.35",
         round(confound["fallback_rate_homologous"] * 100, 2), "homology"),
        ("fallback anti %", "3.91",
         round(confound["fallback_rate_anti"] * 100, 2), "homology"),
        ("effective mutation homologous", "0.5117",
         confound["effective_mutation_fraction"]["homologous"], "homology"),
        ("effective mutation anti", "0.5196",
         confound["effective_mutation_fraction"]["anti"], "homology"),
        ("effective mutation crossover", "0.5",
         confound["effective_mutation_fraction"]["crossover"], "homology"),
    ]

    ladder = {r["rung"]: r for r in art["lean_gated_recombination_calibration"]["ladder"]}
    for rung, size, pooled in (
        ("L1_base", 5, 0.75), ("L2_minus_q", 7, 0.969), ("L3_minus_wq", 9, 0.438),
        ("L4_minus_hwq", 11, 0.125), ("L5_minus_half_hwq", 13, 0.0), ("L6_full", 17, 0.0),
    ):
        rows.append((f"{rung} size", size, ladder[rung]["target_size"], "calibration"))
        rows.append((f"{rung} pooled rate", pooled, ladder[rung]["pooled_solve_rate"],
                     "calibration"))

    atom = art["lean_atomicity_is_the_wrapper"]
    observation = atom["the_decisive_observation"]
    rows += [
        ("axiom lines printed", "8", observation["axiom_lines_printed"], "atomicity"),
        ("exit code", "1", observation["exit_code"], "atomicity"),
    ]
    for row in atom["measured"]:
        rows.append((f"invocations at {row['actually_false']} false", "1",
                     row["invocations"], "atomicity"))

    contribution = art["lean_gated_recombination_contribution"]
    cpa = contribution["per_arm"]
    for arm, solved, median in (
        ("contribution_preserving", "73", 1011),
        ("same_sites_unscaled", "52", 1358.5),
    ):
        rows.append((f"{arm} solved", solved, cpa[arm]["solved"], "contribution"))
        rows.append((f"{arm} median evals", median,
                     cpa[arm]["median_evaluations_when_solved"], "contribution"))
    ctests = contribution["verdict"]["tests"]
    for key, want in (
        ("contribution_preserving_vs_crossover", 0.1357),
        ("contribution_preserving_vs_same_sites_unscaled", 0.0308),
        ("contribution_preserving_vs_mutation_only", 0.0424),
        ("same_sites_unscaled_vs_crossover", 0.5757),
        ("contribution_preserving_vs_homologous", 0.8348),
    ):
        rows.append((f"p {key}", want, ctests[key]["p"], "contribution"))
    rows.append(("bonferroni alpha", 0.01,
                 contribution["verdict"]["multiple_comparisons"]["bonferroni_alpha"],
                 "contribution"))
    rows.append(("anything survives correction", False,
                 contribution["verdict"]["multiple_comparisons"]["anything_survives"],
                 "contribution"))

    bisection = {
        r["scenario"].split()[0]: r
        for r in art["lean_batching_bisection"]["bisection_measured_first"]
    }
    for failures, want in (("0", "1"), ("1", "7"), ("2", "11"), ("4", "15")):
        rows.append((f"bisection at {failures} failures", want,
                     bisection[failures]["invocations"], "bisection"))
    return rows


def main() -> int:
    if not PAPER.exists():
        raise RuntimeError(f"paper missing: {PAPER}")
    art = load()
    rows = collect(art)

    mismatches = [r for r in rows if str(r[1]) != str(r[2])]
    print(f"{len(rows)} quantitative claims checked against artifacts")
    print(f"  matched : {len(rows) - len(mismatches)}")
    print(f"  MISMATCH: {len(mismatches)}")
    for label, paper_value, artifact_value, source in mismatches:
        print(f"    {label}: paper={paper_value!r} artifact={artifact_value!r} ({source})")

    tex = PAPER.read_text()
    absent = [s for s in MUST_APPEAR if s not in tex]
    print(f"\nexpected in the TeX but absent: {absent or 'none'}")

    # The soundness facts the paper asserts, which are booleans rather than numbers.
    atom = art["lean_atomicity_is_the_wrapper"]
    unsound = [r for r in atom["measured"] if r["false_accepted"]]
    uncaught = [r for r in atom["measured"] if not r["all_culprits_correct"]]
    print(f"scenarios accepting a false candidate: {len(unsound)} (must be 0)")
    print(f"scenarios misnaming a culprit        : {len(uncaught)} (must be 0)")

    failed = bool(mismatches or absent or unsound or uncaught)
    print("\n" + ("REFUSING DEPOSIT" if failed else "all claims trace to an artifact"))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
