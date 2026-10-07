"""Tests for scripts/openai_math/index_corpus.py.

The fixture builds a tiny on-disk tree with the layout of github.com/openai/math.
One challenge is clean (positive control); each negative control plants exactly
one defect that the audit must flag.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "openai_math" / "index_corpus.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("index_corpus", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ic = _load()

GOOD_LEAN = """import Mathlib

namespace OAI

namespace InternalCatalan

theorem catalan_irrational :
    Irrational (∑' j : ℕ, (-1 : ℝ) ^ j / ((2 * j + 1 : ℕ) : ℝ) ^ 2) := by
  sorry

end InternalCatalan

end OAI
"""


def _config(module: str, theorems: list[str], axioms: list[str] | None = None) -> dict[str, object]:
    return {
        "challenge_module": f"ComparatorChallenges.{module}",
        "solution_module": f"OAI.NumberTheory.{module}.Main",
        "theorem_names": theorems,
        "definition_names": [],
        "enable_nanoda": False,
        "permitted_axioms": axioms if axioms is not None else ["propext", "Quot.sound", "Classical.choice"],
    }


def _write_challenge(root: Path, name: str, lean: str, config: dict[str, object]) -> None:
    d = root / "lean" / "ComparatorChallenges"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.lean").write_text(lean)
    (d / f"{name}.json").write_text(json.dumps(config))


@pytest.fixture()
def clone(tmp_path: Path) -> Path:
    root = tmp_path / "openai-math"
    (root / "lean" / "docs").mkdir(parents=True)
    (root / "README.md").write_text("# Math\n")
    (root / "lean" / "lakefile.lean").write_text("import Lake\n")
    (root / "lean" / "lean-toolchain").write_text("leanprover/lean4:v4.34.1\n")
    paper = root / "preprints" / "Catalans-constant-is-irrational-September-24-2026"
    paper.mkdir(parents=True)
    (paper / "paper.pdf").write_bytes(b"%PDF-1.5\n")
    (root / "preprints" / "No-pdf-yet").mkdir()
    (root / "preprints" / "Main-pdf-name").mkdir()
    (root / "preprints" / "Main-pdf-name" / "main.pdf").write_bytes(b"%PDF-1.5\n")
    (root / "reasoning_traces").mkdir()
    (root / "reasoning_traces" / "trace.pdf").write_bytes(b"%PDF-1.5\n")
    (root / "lean" / "docs" / "005.md").write_text(
        "# Irrationality of Catalan's constant\n\n| r | [Catalan.lean](../ComparatorChallenges/Catalan.lean) |\n"
    )
    (root / "lean" / "docs" / "999.md").write_text(
        "# Dangling\n\n[Ghost.lean](../ComparatorChallenges/Ghost.lean)\n"
    )
    _write_challenge(root, "Catalan", GOOD_LEAN, _config("Catalan", ["OAI.InternalCatalan.catalan_irrational"]))
    git = root / ".git"
    (git / "refs" / "heads").mkdir(parents=True)
    (git / "HEAD").write_text("ref: refs/heads/main\n")
    (git / "refs" / "heads" / "main").write_text("adc7f124" + "0" * 32 + "\n")
    return root


def test_positive_control_clean_challenge_has_no_problems(clone: Path) -> None:
    audits = ic.audit_challenges(clone / "lean")
    assert [a.name for a in audits] == ["Catalan"]
    assert audits[0].problems == []
    assert audits[0].declared_theorems == ["OAI.InternalCatalan.catalan_irrational"]
    assert audits[0].imports == ["Mathlib"]
    assert audits[0].sorry_count == 1


def test_negative_control_untrusted_axiom_is_flagged(clone: Path) -> None:
    _write_challenge(
        clone,
        "Cheat",
        GOOD_LEAN,
        _config("Cheat", ["OAI.InternalCatalan.catalan_irrational"], ["propext", "Lean.ofReduceBool"]),
    )
    audit = {a.name: a for a in ic.audit_challenges(clone / "lean")}["Cheat"]
    assert any("Lean.ofReduceBool" in p for p in audit.problems)
    assert len(audit.problems) == 1


def test_negative_control_undeclared_theorem_name_is_flagged(clone: Path) -> None:
    _write_challenge(clone, "Renamed", GOOD_LEAN, _config("Renamed", ["OAI.catalan_irrational"]))
    audit = {a.name: a for a in ic.audit_challenges(clone / "lean")}["Renamed"]
    assert audit.problems == ["theorem_names not declared in challenge file: ['OAI.catalan_irrational']"]
    assert audit.declared_theorems == ["OAI.InternalCatalan.catalan_irrational"]


def test_negative_control_proof_inside_challenge_is_flagged(clone: Path) -> None:
    proved = GOOD_LEAN.replace("  sorry", "  norm_num")
    _write_challenge(clone, "Proved", proved, _config("Proved", ["OAI.InternalCatalan.catalan_irrational"]))
    audit = {a.name: a for a in ic.audit_challenges(clone / "lean")}["Proved"]
    assert audit.problems == ["challenge file has no sorry (expected a statement-only file)"]
    assert audit.notes == []


AXIOM_POSED = """import Mathlib
namespace OAI
namespace HarmonicCounterexample
def MainClaim : Prop := ∃ n : ℕ, 8 ≤ n
axiom mainStatement : MainClaim
theorem main : MainClaim := mainStatement
end HarmonicCounterexample
end OAI
"""


def test_axiom_posed_statement_is_a_note_when_axiom_not_permitted(clone: Path) -> None:
    # Pattern found upstream in HarmonicGrowth.lean (2026-10-07 clone).
    _write_challenge(clone, "Harmonic", AXIOM_POSED, _config("Harmonic", ["OAI.HarmonicCounterexample.main"]))
    audit = {a.name: a for a in ic.audit_challenges(clone / "lean")}["Harmonic"]
    assert audit.problems == []
    assert audit.declared_axioms == ["mainStatement"]
    assert audit.notes == ["statement posed via axiom ['mainStatement'] (not permitted to the solution)"]


def test_negative_control_axiom_posed_statement_with_permitted_axiom_is_a_defect(clone: Path) -> None:
    axioms = ["propext", "OAI.HarmonicCounterexample.mainStatement"]
    _write_challenge(
        clone, "Leaky", AXIOM_POSED, _config("Leaky", ["OAI.HarmonicCounterexample.main"], axioms)
    )
    audit = {a.name: a for a in ic.audit_challenges(clone / "lean")}["Leaky"]
    assert "challenge axiom is in permitted_axioms: ['mainStatement']" in audit.problems
    assert any("untrusted" in p for p in audit.problems)


def test_definition_hole_is_a_note_not_a_problem(clone: Path) -> None:
    # Pattern found upstream in ElementaryPositivity.json (2026-10-07 clone).
    config = _config("Hole", [])
    config["definition_names"] = ["OAI.elementaryPositivityWitness"]
    _write_challenge(clone, "Hole", "import Mathlib\nnamespace OAI\ndef elementaryPositivityWitness : ℕ := sorry\nend OAI\n", config)
    audit = {a.name: a for a in ic.audit_challenges(clone / "lean")}["Hole"]
    assert audit.problems == []
    assert audit.notes == ["definition hole ['OAI.elementaryPositivityWitness']: needs an additional verifier"]
    empty = _config("Empty", [])
    _write_challenge(clone, "Empty", GOOD_LEAN, empty)
    empty_audit = {a.name: a for a in ic.audit_challenges(clone / "lean")}["Empty"]
    assert empty_audit.problems == ["theorem_names and definition_names are both empty"]


def test_universe_parameters_are_stripped_from_theorem_names() -> None:
    # Pattern found upstream in MatroidProphet.lean / MatroidSecretary.lean.
    src = (
        "namespace OAI\nnamespace MatroidProphet.Assigned\n"
        "theorem one_sample.{u} : MatroidProphet.OneSampleChallenge.{u} := by\n  sorry\n"
        "theorem hidden_vector : MatroidProphet.HiddenVectorChallenge := by\n  sorry\n"
        "end MatroidProphet.Assigned\nend OAI\n"
    )
    assert ic.declared_theorem_names(src) == [
        "OAI.MatroidProphet.Assigned.one_sample",
        "OAI.MatroidProphet.Assigned.hidden_vector",
    ]
    assert ic.declared_theorem_names("theorem t.{u, v} : True := trivial\n") == ["t"]


def test_sorry_inside_a_comment_does_not_count(clone: Path) -> None:
    commented = GOOD_LEAN.replace("  sorry", "  rfl -- sorry was here\n  /- sorry -/")
    _write_challenge(clone, "Commented", commented, _config("Commented", ["OAI.InternalCatalan.catalan_irrational"]))
    audit = {a.name: a for a in ic.audit_challenges(clone / "lean")}["Commented"]
    assert audit.sorry_count == 0
    assert "challenge file has no sorry (expected a statement-only file)" in audit.problems


def test_missing_lean_file_and_bad_json_are_reported(clone: Path) -> None:
    d = clone / "lean" / "ComparatorChallenges"
    (d / "Orphan.json").write_text(json.dumps(_config("Orphan", ["X.y"])))
    (d / "Broken.json").write_text("{not json")
    audits = {a.name: a for a in ic.audit_challenges(clone / "lean")}
    assert "challenge .lean file missing" in audits["Orphan"].problems
    assert audits["Broken"].problems[0].startswith("invalid JSON")


def test_build_index_recounts_from_disk(clone: Path) -> None:
    index = ic.build_index(clone)
    counts = index["counts"]
    assert counts["preprint_dirs"] == 3
    assert counts["preprint_dirs_with_pdf"] == 2
    assert counts["preprint_dirs_with_paper_pdf"] == 1
    assert counts["formalization_docs"] == 2
    assert counts["comparator_challenges"] == 1
    assert counts["reasoning_traces"] == 1
    assert index["doc_links_to_missing_challenges"] == ["Ghost"]
    assert index["challenges_not_linked_from_docs"] == []
    assert index["clone_head"] == "adc7f124" + "0" * 32
    assert index["toolchain"]["upstream"] == "leanprover/lean4:v4.34.1"


def test_toolchain_mismatch_is_reported(
    clone: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    local = tmp_path / "lean-toolchain"
    monkeypatch.setattr(ic, "LOCAL_TOOLCHAIN_FILE", local)
    local.write_text("leanprover/lean4:v4.34.0-rc2\n")
    mismatch = ic.build_index(clone)["toolchain"]
    assert mismatch["local_formal"] == "leanprover/lean4:v4.34.0-rc2"
    assert mismatch["compatible"] is False
    local.write_text("leanprover/lean4:v4.34.1\n")
    assert ic.build_index(clone)["toolchain"]["compatible"] is True
    local.unlink()
    absent = ic.build_index(clone)["toolchain"]
    assert absent["local_formal"] is None
    assert absent["compatible"] is False


def test_missing_clone_is_blocked_and_writes_nothing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = tmp_path / "out" / "corpus_index.json"
    rc = ic.main(["--clone", str(tmp_path / "absent"), "--out", str(out)])
    assert rc == ic.EXIT_BLOCKED
    assert not out.exists()
    assert capsys.readouterr().out.startswith("BLOCKED:")


def test_main_writes_index_for_valid_clone(clone: Path, tmp_path: Path) -> None:
    out = tmp_path / "idx.json"
    assert ic.main(["--clone", str(clone), "--out", str(out)]) == 0
    written = json.loads(out.read_text())
    assert written["counts"]["comparator_challenges"] == 1
    assert written["challenges"][0]["name"] == "Catalan"


def test_packed_refs_head_resolution(tmp_path: Path) -> None:
    git = tmp_path / ".git"
    git.mkdir()
    (git / "HEAD").write_text("ref: refs/heads/main\n")
    (git / "packed-refs").write_text("# pack-refs with: peeled\n" + "f" * 40 + " refs/heads/main\n")
    assert ic.read_head_commit(tmp_path) == "f" * 40
    (git / "HEAD").write_text("e" * 40 + "\n")
    assert ic.read_head_commit(tmp_path) == "e" * 40


def test_root_prefixed_and_nested_namespaces() -> None:
    src = "namespace A.B\ntheorem t : True := trivial\nend A.B\ntheorem _root_.Z.u : True := trivial\n"
    assert ic.declared_theorem_names(src) == ["A.B.t", "Z.u"]
    unclosed = "namespace A\ntheorem v : True := trivial\nend B\ntheorem w : True := trivial\n"
    assert ic.declared_theorem_names(unclosed) == ["A.v", "A.w"]


def test_attributes_and_modifiers_before_theorem_are_recognised() -> None:
    src = (
        "namespace N\n"
        "@[simp] theorem a : True := trivial\n"
        "@[simp, norm_cast]\nprotected theorem b : True := trivial\n"
        "nonrec lemma c : True := trivial\n"
        "private noncomputable theorem d : True := trivial\n"
        "end N\n"
    )
    assert ic.declared_theorem_names(src) == ["N.a", "N.b", "N.c", "N.d"]
    assert ic.declared_theorem_names("@[simp] def notATheorem : Nat := 0\n") == []
