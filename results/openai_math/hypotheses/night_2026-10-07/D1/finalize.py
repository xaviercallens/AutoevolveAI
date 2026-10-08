"""Lane D1 finalisation: prepends a short summary to definition_holes.md (the generated table is kept below it)
and writes result.json and lane_results.tsv. All numbers come from definition_holes.json and controls.json."""

import hashlib
import json
from pathlib import Path

LANE = Path(__file__).resolve().parent
WT = LANE.parents[4]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    dh = json.loads((LANE / "definition_holes.json").read_text(encoding="utf-8"))
    ctl = json.loads((LANE / "controls.json").read_text(encoding="utf-8"))
    eye = json.loads((LANE / "eye_review.json").read_text(encoding="utf-8"))
    holes = [h for ch in dh["challenges"] for h in ch["holes"]]
    eye_counts: dict[str, int] = {}
    for h in holes:
        eye_counts[h["eye_verdict"]] = eye_counts.get(h["eye_verdict"], 0) + 1
    unpinned = [h["hole"] for h in holes if eye[h["hole"]]["meaning_pinned"] is not True]
    mc = dh["mechanical_counts"]
    script = WT / "scripts/openai_math/d1_hole_bodies.py"
    tests = WT / "tests/openai_math/test_d1_hole_bodies.py"

    md_table = (LANE / "definition_holes.md").read_text(encoding="utf-8")
    if md_table.startswith("# "):
        md_table = md_table.split("\n## Full table\n", 1)[1].lstrip("\n")
    short = ["| Challenge | Hole | Challenge def | Solution def | Mechanical | By eye | Meaning pinned |", "|---|---|---|---|---|---|---|"]
    for ch in dh["challenges"]:
        for h in ch["holes"]:
            if h["verdict"] == "MATCHES" and h["eye_verdict"] == "MATCHES":
                continue
            sol = h["solution"][0]
            cdef = ("sorry" if h.get("challenge_sorry_only") else "body with sorry") if h.get("challenge_has_sorry") else "body"
            short.append(f"| {ch['challenge']} | {h['hole'].split('.')[-1]} | {cdef} | `{sol['file']}:{sol['line']}` | {h['verdict']} | {h['eye_verdict']} | {eye[h['hole']]['meaning_pinned']} |")
    head = [
        "# D1: definition-hole bodies (openai/math @ adc7f124, nine Comparator configs)",
        "",
        f"Controls: {ctl['n_pass']}/{ctl['n']} pass (all_pass={ctl['all_pass']}). Holes: {dh['n_holes']}. "
        f"Mechanical: {mc.get('MATCHES', 0)} MATCHES, {mc.get('DIFFERS', 0)} DIFFERS, {mc.get('SORRIED_IN_CHALLENGE', 0)} SORRIED_IN_CHALLENGE, "
        f"{mc.get('NOT_FOUND', 0)} NOT_FOUND, {mc.get('AMBIGUOUS', 0)} AMBIGUOUS. "
        f"By eye: {', '.join(f'{v} {k}' for k, v in sorted(eye_counts.items()))}. meaning_pinned=false: {len(unpinned)}.",
        "",
        "Text comparison is not elaboration. EQUIVALENT_BY_READING is a reading verdict and never replaces a mechanical DIFFERS. "
        "Every one of the six comes from an instrument limitation (`run_cmd` absorbed, `ᶜ` lexed into the identifier, a renaming that reuses one name for two binders) or from a difference only in Prop-valued proof fields/parentheses. "
        "The two flagged holes: DefocusingNLS.sobolevProduct (the challenge sorry sits only in the Memℓp proof; the data part is identical) and "
        "elementaryPositivityWitness (sorry-only; the config has no theorem_names, so the hole's type *is* the claim and any inhabitant is accepted).",
        "",
        "## Holes that are not plain MATCHES/MATCHES",
        "",
        *short,
        "",
        "## Full table",
        "",
        "",
    ]
    (LANE / "definition_holes.md").write_text("\n".join(head) + md_table, encoding="utf-8")

    result = {
        "lane": "D1",
        "todo": 28,
        "status": "DONE",
        "upstream_commit": "adc7f1241b42e322a6451854ab7e4b4c146bf78a",
        "controls": {"n": ctl["n"], "n_pass": ctl["n_pass"], "all_pass": ctl["all_pass"], "file": "controls.json"},
        "n_holes": dh["n_holes"],
        "mechanical_counts": mc,
        "eye_counts": eye_counts,
        "eye_disagreements": dh["eye_disagreements"],
        "meaning_pinned_false": unpinned,
        "code": {
            "scripts/openai_math/d1_hole_bodies.py": sha(script),
            "tests/openai_math/test_d1_hole_bodies.py": sha(tests),
            "matches_preregistered_sha256": sha(script) == "82b5147337fadabe61ce95380f9acf0651d0dc0ca45fbb7efdbf3f6211a38de1"
            and sha(tests) == "539d03bb94a16f4cabf7bc9bc4f5995c6a14840b7d8ae8b8ff93fc5b1e31d127",
        },
        "instrument_defects_found": [
            "run_cmd missing from COMMAND_STARTS: a following column-0 run_cmd line is absorbed into the declaration (DefocusingNLS sobolevOddPower, schrodingerFlow, sobolevProduct challenge text). Can only cause a false DIFFERS.",
            "U+1D9C (ᶜ) is matched by \\w and lexed into the identifier (Brenier IsSupported). Can only cause a false DIFFERS.",
            "Single global bijection: a name used for two different binders on one side (KServer `requests`) cannot map to two names (σ, rs), which gives a false DIFFERS. bound_identifiers is also scope-insensitive: a name bound in one place and used free elsewhere in the same declaration could be accepted as renamed, which is a false-MATCHES vector. The eye check covers it: in every renaming map of the 37 MATCHES, each renamed name is a local binder at every occurrence (all challenge/solution texts read).",
            "shadow_candidates does not resolve `open X` against the enclosing namespace stack, so an empty list is not proof that nothing shadows. eye_aid.py redoes this with resolution (deviations.md item 1).",
        ],
        "deviations": "deviations.md item 1: advisory eye aids (eye_aid.py, mathlib_scan.py) plus listings visible_instances.json/closure_instances.json. Frozen script not edited; mechanical verdicts unchanged.",
        "not_checked": [
            "Nothing elaborated or compiled (no Lean). Expr-level comparison is deferred to D2.",
            "Instances and notation that the solution closure adds can change how token-identical text elaborates. Only the instance/notation lines visible at each solution declaration were listed (visible_instances.json) and read in part. All that were read are on OAI-local types or are file-local.",
            "eye_aid/mathlib_scan only scan namespaces opened on the solution side alone. Opens present only on the challenge side (e.g. DefocusingNLS: Set Filter Topology MeasureTheory ProbabilityTheory) were not scanned for captures on the challenge side.",
            "The Mathlib capture scan used LeanMaster's Mathlib checkout (rev 85e3a25e), not upstream's pin (d13f23b7).",
            "Comparator's definitionHoleMatches behaviour (name/levels/type/safety only) and the full comparison of non-hole constants were read from upstream source in an earlier session and not re-verified here (Compare.lean is not in the local clone).",
        ],
        "outputs": ["definition_holes.json", "definition_holes.md", "eye_review.json", "eye_aid.json", "mathlib_scan.json", "visible_instances.json", "controls.json", "chunks/"],
    }
    (LANE / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    row = [
        "D1",
        "D1-definition-hole-bodies",
        "token compare of 45 Comparator definition-hole bodies (9 configs), challenge vs solution import closure, plus eye review",
        "-",
        "verdict counts (mechanical; eye)",
        f"mech {mc.get('MATCHES', 0)} MATCHES/{mc.get('DIFFERS', 0)} DIFFERS/{mc.get('SORRIED_IN_CHALLENGE', 0)} SORRIED/{mc.get('NOT_FOUND', 0)} NF/{mc.get('AMBIGUOUS', 0)} AMB; eye "
        + "/".join(f"{v} {k}" for k, v in sorted(eye_counts.items())),
        "pass" if ctl["all_pass"] else "fail",
        "keep" if ctl["all_pass"] else "crash",
        f"controls {ctl['n_pass']}/{ctl['n']}; flagged (meaning_pinned=false): {', '.join(h.split('.')[-1] for h in unpinned)}; no Lean elaboration (D2)",
    ]
    tsv = LANE / "lane_results.tsv"
    header = "run\thypothesis\tstrategy\tbudget_s\tmetric\tvalue\tcontrols\tstatus\tnote\n"
    existing = tsv.read_text(encoding="utf-8").splitlines(keepends=True) if tsv.is_file() else [header]
    kept = [ln for ln in existing if not ln.startswith("D1\tD1-definition-hole-bodies\t")]
    tsv.write_text("".join(kept) + "\t".join(row) + "\n", encoding="utf-8")
    print(json.dumps({"mech": mc, "eye": eye_counts, "unpinned": unpinned, "sha_ok": result["code"]["matches_preregistered_sha256"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
