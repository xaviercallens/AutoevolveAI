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


def test_lake_mode_refuses_an_unbuilt_directory_and_writes_nothing(tmp_path: Path) -> None:
    f = tmp_path / "X.lean"
    f.write_text("theorem t : 1 = 1 := rfl\n#print axioms t\n")
    with pytest.raises(LeanEnvironmentError, match="no built Lean environment"):
        LeanKernelVerifier(tmp_path).verify_file(f)
    assert not (tmp_path / ".lake").exists()  # lake was never started, so it fetched nothing


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
