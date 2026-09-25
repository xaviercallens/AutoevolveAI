"""Unit tests for anse.symbolic.repl_pain_loop (Physical Lean 4 REPL & Anti-LaTeX Bleed-Through)."""

import pytest
from anse.symbolic.repl_pain_loop import (
    REPLPainLoop,
    detect_latex_bleed_through,
)


def test_latex_bleed_through_detection():
    # Code with raw TeX backslash commands
    leaky_code = r"""
import Mathlib.Analysis.Complex.Basic

def InCriticalStrip (s: ℂ): Prop := \theta < s.re \wedge s.re < 1
"""
    leaks = detect_latex_bleed_through(leaky_code)
    assert len(leaks) >= 1
    assert r"\theta" in leaks


def test_clean_unicode_no_bleed():
    # Pure Unicode Lean 4 code
    clean_code = """
import Mathlib.NumberTheory.LSeries.RiemannZeta

open Complex

def InCriticalStrip (s : ℂ) : Prop :=
  0 < s.re ∧ s.re < 1
"""
    leaks = detect_latex_bleed_through(clean_code)
    assert len(leaks) == 0


def test_repl_pain_loop_rejects_latex_bleed():
    repl = REPLPainLoop()
    leaky_code = "def bad_thm : Prop := \\Sigma i : Fin 3, i = 0"
    attempt = repl.compile_lean_snippet(leaky_code, filename_prefix="bleed_test")
    assert attempt.returncode != 0
    assert attempt.energy == 1_000_000.0
    assert any("LaTeX Bleed-Through" in viol for viol in attempt.violations)


def test_repl_pain_loop_physical_error_capture():
    repl = REPLPainLoop()
    # Invalid syntax that fails the physical Lean 4 elaboration
    broken_lean = "def broken : Nat := true + \"string\""
    attempt = repl.compile_lean_snippet(broken_lean, filename_prefix="broken_test")
    assert attempt.returncode != 0
    assert attempt.energy == 1_000_000.0
    assert len(attempt.stderr) > 0


def test_repl_pain_loop_valid_snippet_compiles():
    repl = REPLPainLoop()
    # Simple, sound Lean 4 snippet
    valid_lean = """
theorem simple_identity (n : Nat) : n + 0 = n := by
  rfl
"""
    attempt = repl.compile_lean_snippet(valid_lean, filename_prefix="valid_test")
    assert attempt.returncode == 0
    assert attempt.energy == 0.0
    assert len(attempt.violations) == 0


def test_repl_pain_loop_iterative_repair():
    repl = REPLPainLoop(max_retries=3)

    # Initial broken code
    broken_code = "def thm_foo : Nat := \\theta"

    # Generator repair function that cleans up on iteration 2
    def repair_fn(bad_code: str, error_msg: str) -> str:
        if "\\theta" in bad_code:
            return "theorem sound_foo (n : Nat) : n = n := by rfl"
        return bad_code

    result = repl.run_pain_loop(
        initial_code=broken_code,
        generator_repair_fn=repair_fn,
    )

    assert result.success
    assert result.iterations == 2
    assert result.energy_score == 0.0
    assert "sound_foo" in result.final_code
