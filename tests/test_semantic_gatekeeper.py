"""Unit tests for anse.core.semantic_gatekeeper and Two-Stage HardGate."""

import pytest
import tempfile
import os
from anse.core.semantic_gatekeeper import (
    SemanticGatekeeper,
    SemanticAuditResult,
    audit_lean4_code,
)
from anse.core.hard_gate_compiler import HardGateCompiler


def test_smuggled_hypothesis_rejection():
    # Case 1: Smuggled involution hypothesis
    code_smuggled = """
import Mathlib.Tactic

theorem hodge_trivial (h_invol : ∀ x : Int, x = -(-x)) : 1 = 1 := by
  rfl
"""
    result = audit_lean4_code(code_smuggled)
    assert not result.passed
    assert result.energy_score == 1_000_000.0
    assert any("Hypothesis Smuggling" in err for err in result.violations)
    assert any("h_invol" in err for err in result.violations)


def test_smuggled_comm_ortho_rejection():
    # Case 2: Smuggled commutativity or orthogonality
    code_comm = """
theorem ns_pythagoras (h_ortho : ∀ u v : Float, u * v = 0) : 0 = 0 := by
  rfl
"""
    result = audit_lean4_code(code_comm)
    assert not result.passed
    assert result.energy_score == 1_000_000.0
    assert any("h_ortho" in err for err in result.violations)


def test_vacuous_mock_rejection():
    # Case 3: Empty mock structure mocking complex manifold
    code_vacuous = """
structure ComplexProjectiveManifold where
  dim : Nat
  is_smooth : Prop
"""
    result = audit_lean4_code(code_vacuous)
    assert not result.passed
    assert result.energy_score == 1_000_000.0
    assert any("Vacuous Structure" in err for err in result.violations)


def test_missing_grounded_requirements():
    # Case 4: Navier-Stokes code missing differential / divergence operators
    code_bad_ns = """
-- navier-stokes model
theorem ns_smooth : 1 = 1 := by
  rfl
"""
    result = audit_lean4_code(code_bad_ns, topic="navier_stokes")
    assert not result.passed
    assert result.energy_score == 1_000_000.0
    assert any("Missing essential operators for navier_stokes" in err for err in result.violations)


def test_valid_mathlib_code_passes():
    # Case 5: Sound Lean 4 code with Mathlib imports
    valid_code = """
import Mathlib.Analysis.Calculus.FDeriv.Basic
import Mathlib.Analysis.InnerProductSpace.Basic

theorem valid_norm_nonneg (x : ℝ) : 0 ≤ x * x := by
  exact mul_self_nonneg x
"""
    result = audit_lean4_code(valid_code)
    assert result.passed
    assert result.energy_score == 0.0
    assert len(result.violations) == 0


def test_python_scalar_mock_rejection():
    # Case 6: Python scalar zero simplification
    bad_python = """
def check_einstein():
    drift = 0 - 0.5 * 0 * g
    return drift
"""
    gk = SemanticGatekeeper()
    passed, violations, energy = gk.audit_python_code(bad_python)
    assert not passed
    assert energy == 1_000_000.0
    assert any(v.rule == "NO_SCALAR_MOCK" for v in violations)


def test_hard_gate_compiler_semantic_rejection():
    compiler = HardGateCompiler()
    # Write a temporary python script with a semantic mock violation
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write("err = abs(0.0 - 0.0)\nprint('Done')\n")
        tmp_name = f.name
    try:
        success, msg = compiler.compile_and_verify(tmp_name)
        assert not success
        assert "Semantic audit rejected" in msg
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
