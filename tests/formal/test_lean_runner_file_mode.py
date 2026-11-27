"""File-path mode of ``anse.formal.lean_runner`` (TODO 15).

The gate must accept a real proof and reject the two failure classes that exit 0:
``sorry`` and a smuggled axiom. Tests compile import-free files with the plain ``lean``
binary, so they need no Mathlib and cannot trigger a ``lake`` dependency fetch.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from anse.formal.lean_runner import (
    LeanEnvironmentError,
    LeanKernelVerifier,
    declared_theorems,
    main,
    parse_axiom_lines,
)

needs_lean = pytest.mark.skipif(shutil.which("lean") is None, reason="lean binary not installed")


def _verify(tmp_path: Path, source: str):
    f = tmp_path / "Case.lean"
    f.write_text(source, encoding="utf-8")
    return f, LeanKernelVerifier(tmp_path, lean_cmd=["lean"]).verify_file(f, timeout_s=300)


@needs_lean
def test_real_proof_is_accepted_and_reports_no_axioms(tmp_path: Path) -> None:
    _, res = _verify(tmp_path, "theorem t : 1 + 1 = 2 := rfl\n#print axioms t\n")
    assert len(res) == 1
    assert res[0].compiled_successfully and not res[0].has_sorry
    assert res[0].axioms == [] and res[0].untrusted_axioms == []
    assert res[0].energy_score < 100


@needs_lean
def test_classical_axioms_are_trusted(tmp_path: Path) -> None:
    _, res = _verify(tmp_path, "theorem em' (p : Prop) : p ∨ ¬p := Classical.em p\n#print axioms em'\n")
    assert res[0].axioms and set(res[0].axioms) <= {"propext", "Classical.choice", "Quot.sound"}
    assert not res[0].untrusted_axioms and not res[0].has_sorry


@needs_lean
def test_sorry_compiles_with_exit_zero_but_is_rejected(tmp_path: Path) -> None:
    src = "theorem s : 1 + 1 = 3 := by sorry\n#print axioms s\n"
    f, res = _verify(tmp_path, src)
    # The trap this gate exists for: Lean itself calls this a success.
    assert subprocess.run(["lean", str(f)], capture_output=True).returncode == 0
    assert res[0].has_sorry and "sorryAx" in res[0].axioms
    assert res[0].energy_score == 1000000.0


@needs_lean
def test_smuggled_axiom_is_rejected(tmp_path: Path) -> None:
    src = "axiom cheat : False\ntheorem c : 1 = 2 := cheat.elim\n#print axioms c\n"
    _, res = _verify(tmp_path, src)
    assert res[0].compiled_successfully and not res[0].has_sorry
    assert res[0].untrusted_axioms == ["cheat"]
    assert res[0].energy_score == 1000000.0


@needs_lean
def test_theorem_without_axioms_line_is_unchecked_not_clean(tmp_path: Path) -> None:
    _, res = _verify(tmp_path, "theorem a : 1 = 1 := rfl\ntheorem b : 2 = 2 := rfl\n#print axioms a\n")
    by_name = {r.theorem_name: r for r in res}
    assert by_name["a"].compiled_successfully and not by_name["a"].untrusted_axioms
    assert not by_name["b"].compiled_successfully and "unchecked" in by_name["b"].output


@needs_lean
def test_file_with_no_theorem_verifies_nothing(tmp_path: Path) -> None:
    _, res = _verify(tmp_path, "def x : Nat := 1\n")
    assert len(res) == 1 and not res[0].compiled_successfully
    assert "nothing was verified" in res[0].output


@needs_lean
def test_compile_error_is_a_failure(tmp_path: Path) -> None:
    _, res = _verify(tmp_path, "theorem t : 1 = 2 := rfl\n#print axioms t\n")
    assert not res[0].compiled_successfully and res[0].returncode != 0


@needs_lean
def test_namespaced_theorem_matches_its_qualified_axioms_line(tmp_path: Path) -> None:
    src = "namespace Foo\ntheorem bar : 3 = 3 := rfl\nend Foo\n#print axioms Foo.bar\n"
    _, res = _verify(tmp_path, src)
    assert res[0].theorem_name == "bar" and res[0].compiled_successfully and res[0].axioms == []


def test_parse_axiom_lines_accepts_primed_theorem_names() -> None:
    # Regression: `theorem em'` prints as `'em'' depends on ...`; a `[^']+` pattern lost it.
    out = "'em'' depends on axioms: [propext]\n'E_pos'' does not depend on any axioms\n"
    assert parse_axiom_lines(out) == {"em'": ["propext"], "E_pos'": []}


def test_declared_theorems_ignores_comments_and_docstrings() -> None:
    src = (
        "/-- a docstring mentioning theorem fake1 : True -/\n"
        "-- theorem fake2 : True\n"
        "/- block\n theorem fake3 : True -/\n"
        "@[simp] theorem real_one : 1 = 1 := rfl\n"
        "  private lemma real_two : 2 = 2 := rfl\n"
        "theorem real_three (n : Nat) : n = n := rfl\n"
    )
    assert declared_theorems(src) == ["real_one", "real_two", "real_three"]


def test_parse_axiom_lines_handles_wrapped_lists_and_empty() -> None:
    out = (
        "'A.f' depends on axioms: [propext,\n Classical.choice,\n Quot.sound]\n"
        "'A.g' does not depend on any axioms\n"
    )
    assert parse_axiom_lines(out) == {
        "A.f": ["propext", "Classical.choice", "Quot.sound"],
        "A.g": [],
    }


def test_lake_mode_refuses_a_directory_with_no_lake_dir_at_all(tmp_path: Path) -> None:
    f = tmp_path / "X.lean"
    f.write_text("theorem t : 1 = 1 := rfl\n#print axioms t\n")
    with pytest.raises(LeanEnvironmentError, match="no built Mathlib"):
        LeanKernelVerifier(tmp_path).verify_file(f)
    assert not (tmp_path / ".lake").exists()  # lake was never started, so it fetched nothing


def test_lake_mode_refuses_a_checked_out_but_unbuilt_mathlib(tmp_path: Path) -> None:
    """Regression (2026-09-28): an aborted `lake env` clone leaves .lake/packages/mathlib
    as a real, non-empty checked-out directory with source files but ZERO oleans anywhere
    under it — a check that only asked ".lake/packages is a directory" would have called
    this environment usable and let `lake env` resume the fetch/build. Reproduces the
    exact shape found in the AutoevolveAI cosmo3-run worktree after that incident."""
    mathlib = tmp_path / ".lake" / "packages" / "mathlib"
    (mathlib / "Mathlib").mkdir(parents=True)
    (mathlib / "Mathlib" / "Basic.lean").write_text("-- source only, never built\n")
    (mathlib / ".git").mkdir()  # a real git checkout, just like the aborted clone
    f = tmp_path / "X.lean"
    f.write_text("theorem t : 1 = 1 := rfl\n#print axioms t\n")
    with pytest.raises(LeanEnvironmentError, match="no built Mathlib"):
        LeanKernelVerifier(tmp_path).verify_file(f)


def test_lake_mode_accepts_a_build_dir_with_no_mathlib_olean_umbrella(tmp_path: Path) -> None:
    """This project's own build never produces a Mathlib.olean umbrella (imports are
    pinned to individual built modules — CLAUDE.md); checking for that file would reject
    the real, working environment. At least one built module is what must be accepted."""
    build = tmp_path / ".lake" / "packages" / "mathlib" / ".lake" / "build" / "lib" / "lean"
    build.mkdir(parents=True)
    (build / "Mathlib" / "Tactic" / "Ring").mkdir(parents=True)
    (build / "Mathlib" / "Tactic" / "Ring" / "Basic.olean").write_bytes(b"\x00")
    assert LeanKernelVerifier(tmp_path)._lake_env_cmd() == ["lake", "env", "lean"]


@needs_lean
def test_cli_exit_code_follows_the_gate(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    good = tmp_path / "Good.lean"
    good.write_text("theorem g : 1 = 1 := rfl\n#print axioms g\n")
    bad = tmp_path / "Bad.lean"
    bad.write_text("theorem b : 1 = 2 := by sorry\n#print axioms b\n")
    # The CLI has no lean_cmd flag (production uses lake); drive the same code path directly.
    ok_good = all(r.compiled_successfully and not r.has_sorry and not r.untrusted_axioms
                  for r in LeanKernelVerifier(tmp_path, lean_cmd=["lean"]).verify_file(good))
    ok_bad = all(r.compiled_successfully and not r.has_sorry and not r.untrusted_axioms
                 for r in LeanKernelVerifier(tmp_path, lean_cmd=["lean"]).verify_file(bad))
    assert ok_good and not ok_bad
    with pytest.raises(LeanEnvironmentError):
        main([str(good), "--formal-dir", str(tmp_path)])


@needs_lean
def test_exit_forgery_and_print_string_spoof_are_rejected(tmp_path: Path) -> None:
    """TODO 27: A proof with forged `#print "... depends on axioms: [propext]"` + `#exit`
    before a sorried theorem must be rejected by `verify_file`."""
    forged = (
        '#print "\'forged_thm\' depends on axioms: [propext]"\n'
        "#exit\n"
        "theorem forged_thm : 1 = 2 := by sorry\n"
    )
    _, res = _verify(tmp_path, forged)
    assert len(res) == 1
    assert not res[0].compiled_successfully
    assert res[0].energy_score == 1000000.0
    assert "FORGERY_EXIT_TRUNCATION" in res[0].output
    assert "FORGERY_PRINT_STRING" in res[0].output


@needs_lean
def test_eval_stdout_spoof_and_vacuous_true_are_rejected(tmp_path: Path) -> None:
    """Reject `#eval IO.println` stdout spoofing and vacuous `: True := trivial` theorems."""
    eval_spoof = (
        '#eval IO.println "\'spoofed\' depends on axioms: [propext]"\n'
        "theorem spoofed : 1 = 1 := rfl\n"
    )
    _, res_eval = _verify(tmp_path, eval_spoof)
    assert not res_eval[0].compiled_successfully
    assert "FORGERY_META_STDOUT" in res_eval[0].output

    vacuous = "theorem vac : True := trivial\n#print axioms vac\n"
    _, res_vac = _verify(tmp_path, vacuous)
    assert not res_vac[0].compiled_successfully
    assert "VACUOUS_TRUE_THEOREM" in res_vac[0].output


REPO = Path(__file__).resolve().parents[2]
FORMAL = REPO / "formal"


@needs_lean
def test_todo7_deep_think_auditor_uses_lean_runner(tmp_path: Path) -> None:
    """TODO 7: DeepThinkAuditor verdicts come from lean_runner, with zero 'Simulated PRM'."""
    from anse.core.red_team import DeepThinkAuditor

    red_team_src = (REPO / "anse" / "core" / "red_team.py").read_text(encoding="utf-8")
    regen_src = (REPO / "scripts" / "regenerate_10_math_problems_dspy.py").read_text(encoding="utf-8")
    assert "Simulated PRM" not in red_team_src
    assert "Simulated PRM" not in regen_src

    good = tmp_path / "AuditGood.lean"
    good.write_text("theorem audit_ok : 2 + 2 = 4 := rfl\n#print axioms audit_ok\n")
    auditor = DeepThinkAuditor()
    res_good = auditor.verify_with_lean_kernel(good, formal_dir=tmp_path, lean_cmd=["lean"])
    assert res_good["clean"] is True
    assert res_good["verdict"] == "ACCEPT: KERNEL VERIFIED"

    bad = tmp_path / "AuditBad.lean"
    bad.write_text("theorem audit_bad : 2 + 2 = 5 := by sorry\n#print axioms audit_bad\n")
    res_bad = auditor.verify_with_lean_kernel(bad, formal_dir=tmp_path, lean_cmd=["lean"])
    assert res_bad["clean"] is False
    assert res_bad["verdict"].startswith("REJECT:")


def test_todo8_and_9_formal_anse_statement_review() -> None:
    """TODO 8 & 9: NavierStokesSmoothness maps Clay hypotheses; formal/ANSE has 0 sorry and 0 vacuous True."""
    import re
    from anse.formal.lean_runner import _BLOCK_COMMENT, _LINE_COMMENT, detect_lean_source_forgeries

    ns_src = (FORMAL / "ANSE" / "NavierStokesSmoothness.lean").read_text(encoding="utf-8")
    assert "Clay Millennium Problem Formulation (Fefferman 2000/2006)" in ns_src
    assert "Statement-Review Note" in ns_src
    assert "def HasSchwartzRapidDecay" in ns_src
    assert "def HasBoundedKineticEnergy" in ns_src

    for lean_file in sorted((FORMAL / "ANSE").glob("*.lean")):
        raw = lean_file.read_text(encoding="utf-8")
        stripped = _LINE_COMMENT.sub("", _BLOCK_COMMENT.sub("", raw))
        assert not re.search(r"\bsorry\b", stripped), f"Unexpected sorry in {lean_file.name}"
        assert detect_lean_source_forgeries(raw) == [], f"Source forgery/vacuous theorem in {lean_file.name}"


def test_todo11_and_23_ltm_mix_and_heldout_baseline_provenance() -> None:
    """TODO 11 & 23: ltm_mix.jsonl is wired into night_training_workflow and heldout_baseline matches retrieval_ab."""
    import hashlib
    import json

    ntw_src = (REPO / "scripts" / "night_training_workflow.py").read_text(encoding="utf-8")
    assert 'LTM_MIX_PATH = REPO / "data" / "training" / "ltm_mix.jsonl"' in ntw_src
    ltm_mix = REPO / "data" / "training" / "ltm_mix.jsonl"
    assert ltm_mix.exists()
    rows = [json.loads(line) for line in ltm_mix.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) > 0
    assert all(r["verified"] is True and r["verdict"] is True for r in rows)

    rab_path = REPO / "results" / "hardness" / "retrieval_ab.json"
    hb_path = REPO / "results" / "v2" / "heldout_baseline.json"
    rab_sha = hashlib.sha256(rab_path.read_bytes()).hexdigest()
    hb = json.loads(hb_path.read_text(encoding="utf-8"))
    assert hb["sha256"]["retrieval_ab"] == rab_sha
    for arm in ("deepseek", "goedel", "deepseek+premises", "goedel+premises"):
        assert hb["models"][arm]["n_items"] == 46
        assert hb["models"][arm]["false_accepted"] == 0


def test_todo16_ledger_builder_hardened_against_stale_or_untyped_audits(tmp_path: Path) -> None:
    """TODO 16: Audit objects must carry auditor_kind and audited_file_sha256; changed file yields audit: null."""
    from scripts.openai_math.hypotheses.build_ledger import claim, resolve_audit, sha256_hex

    audited = tmp_path / "formal" / "ANSE" / "Sample.lean"
    audited.parent.mkdir(parents=True, exist_ok=True)
    audited.write_text("theorem sample : 1 + 1 = 2 := rfl\n", encoding="utf-8")
    initial_sha = sha256_hex(audited)

    ev = tmp_path / "evidence.json"
    ev.write_text('{"ok": true}\n', encoding="utf-8")

    valid_audit = {
        "by": "automated model referee",
        "auditor_kind": "model",
        "audited_file": "formal/ANSE/Sample.lean",
        "audited_file_sha256": initial_sha,
        "faithful": True,
    }
    c_fresh = claim("TEST-A-1", "Sample claim", "A", "lean_axioms", ev, audit=valid_audit, repo_root=tmp_path)
    assert c_fresh["audit"] is not None
    assert c_fresh["audit"]["auditor_kind"] == "model"
    assert c_fresh["audit"]["audited_file_sha256"] == initial_sha

    # Negative control 1: missing or invalid auditor_kind is rejected
    with pytest.raises(ValueError, match="auditor_kind"):
        resolve_audit({"audited_file": "formal/ANSE/Sample.lean", "audited_file_sha256": initial_sha}, repo_root=tmp_path)

    # Negative control 2: missing or malformed audited_file_sha256 is rejected
    with pytest.raises(ValueError, match="audited_file_sha256"):
        resolve_audit({"auditor_kind": "human", "audited_file": "formal/ANSE/Sample.lean", "audited_file_sha256": "bad"}, repo_root=tmp_path)

    # Negative control 3: modifying the audited file makes the sha256 stale -> yields audit: None (audit: null in JSON)
    audited.write_text("theorem sample : 1 + 1 = 2 := by rfl -- modified\n", encoding="utf-8")
    c_changed = claim("TEST-A-1", "Sample claim", "A", "lean_axioms", ev, audit=valid_audit, repo_root=tmp_path)
    assert c_changed["audit"] is None
    with pytest.raises(ValueError, match="stale audit sha256"):
        resolve_audit(valid_audit, repo_root=tmp_path, refuse_stale=True)


