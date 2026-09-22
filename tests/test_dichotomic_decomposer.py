"""
Tests for ANSE Dichotomic Task Decomposition and Zero-Stub Hardness Engine.
"""

import ast
from pathlib import Path
import pytest

from anse.orchestration.dichotomic_decomposer import (
    DichotomicTaskNode,
    DichotomyAxis,
    DichotomyEngine,
    TaskStatus,
    TokenBudgetManager,
    ZeroStubAudit,
)


def test_token_budget_allocation():
    parent_budget = 16000
    left, right, reserve = TokenBudgetManager.allocate_subtask_budgets(parent_budget)

    assert left == 7200
    assert right == 7200
    assert reserve == 1600
    assert left + right + reserve == parent_budget


def test_context_pruning():
    huge_context = {
        "interfaces": {"KerrMetric": "g_mu_nu", "CarterConstant": "Q"},
        "invariants": ["dQ/dt == 0", "H_shadow == 0", "det(J) == 1", "E < 1e6"],
        "unrelated_history": "A" * 10000,
    }

    pruned = TokenBudgetManager.prune_context(
        goal="Symplectic Carter Integrator",
        raw_context=huge_context,
        max_tokens=200,
    )

    assert "interfaces" in pruned
    assert "unrelated_history" not in pruned
    assert TokenBudgetManager.estimate_tokens(str(pruned)) <= 200


def test_zero_stub_audit_detects_pass_and_ellipsis():
    code_with_pass = """
def compute_carter_flux(r, theta):
    pass
"""
    audit_pass = ZeroStubAudit.audit_python_code(code_with_pass)
    assert not audit_pass.is_clean
    assert audit_pass.penalty_energy == 1e6
    assert any("pass" in v for v in audit_pass.violations)

    code_with_ellipsis = """
def solve_geodesic(p0):
    ...
"""
    audit_ellipsis = ZeroStubAudit.audit_python_code(code_with_ellipsis)
    assert not audit_ellipsis.is_clean
    assert audit_ellipsis.penalty_energy == 1e6
    assert any("Ellipsis" in v for v in audit_ellipsis.violations)


def test_zero_stub_audit_detects_mock_identifiers():
    code_with_mock = """
def mock_instanton_calculation():
    return 1.0
"""
    audit_mock = ZeroStubAudit.audit_python_code(code_with_mock)
    assert not audit_mock.is_clean
    assert audit_mock.penalty_energy == 1e6
    assert any("mock_instanton_calculation" in v for v in audit_mock.violations)


def test_zero_stub_audit_detects_lean_sorry():
    lean_with_sorry = """
theorem carter_conserved (H : Hamiltonian) : dQ_dt = 0 := by
  sorry
"""
    audit_lean = ZeroStubAudit.audit_lean_code(lean_with_sorry)
    assert not audit_lean.is_clean
    assert audit_lean.penalty_energy == 1e6
    assert any("sorry" in v for v in audit_lean.violations)


def test_zero_stub_audit_clean_code_passes():
    clean_python = """
def integrate_rk4(q0, p0, dt):
    dq = p0 * dt
    dp = -q0 * dt
    return q0 + dq, p0 + dp
"""
    audit_clean = ZeroStubAudit.audit_python_code(clean_python)
    assert audit_clean.is_clean
    assert audit_clean.penalty_energy == 0.0
    assert len(audit_clean.violations) == 0


def test_dichotomic_tree_decomposition_structure():
    engine = DichotomyEngine()
    root = engine.decompose(
        goal="Prove Banach Fixed-Point Contraction in Lean 4 and Verify Numerical Carter Drift",
        total_budget=16000,
        max_depth=2,
    )

    assert root.task_id == "root"
    assert root.depth == 0
    assert not root.is_leaf
    assert root.left_child is not None
    assert root.right_child is not None
    assert root.token_budget == 16000

    # Depth 1
    assert root.left_child.depth == 1
    assert root.right_child.depth == 1

    # Leaves at Depth 2
    leaves = root.get_all_leaves()
    assert len(leaves) == 4
    for leaf in leaves:
        assert leaf.is_leaf
        assert leaf.depth == 2
        assert leaf.acceptance_command != ""
        assert leaf.status == TaskStatus.PENDING


def test_leaf_execution_and_parent_synthesis():
    engine = DichotomyEngine()
    root = engine.decompose(
        goal="Silicon Array STA and Real SCM_RIGHTS Process Migration",
        total_budget=8000,
        max_depth=1,
    )

    leaves = root.get_all_leaves()
    assert len(leaves) == 2

    # Execute left leaf with clean mock-free runner
    clean_code = "def valid_op(): return 42"
    engine.execute_leaf(
        leaves[0],
        source_code=clean_code,
        custom_runner=lambda n: {"passed": True, "custom_metric": 0.99},
    )
    assert leaves[0].status == TaskStatus.VERIFIED
    assert leaves[0].proof_token is not None
    assert leaves[0].energy_score < 10.0

    # Execute right leaf
    engine.execute_leaf(
        leaves[1],
        source_code=clean_code,
        custom_runner=lambda n: {"passed": True, "custom_metric": 0.88},
    )
    assert leaves[1].status == TaskStatus.VERIFIED
    assert leaves[1].proof_token is not None

    # Synthesize root
    engine.synthesize_node(root)
    assert root.status == TaskStatus.VERIFIED
    assert root.proof_token is not None
    assert root.verification_receipt["passed"] is True
    assert root.verification_receipt["synthesized_from"] == ["root.L", "root.R"]


def test_stub_detection_aborts_pipeline():
    engine = DichotomyEngine()
    root = engine.decompose(
        goal="Kerr Symplectic Integrator",
        total_budget=8000,
        max_depth=1,
    )

    leaves = root.get_all_leaves()
    # Execute left leaf with forbidden stub
    stubby_code = "def compute(): pass"
    engine.execute_leaf(leaves[0], source_code=stubby_code)

    assert leaves[0].status == TaskStatus.STUB_DETECTED
    assert leaves[0].energy_score == 1e6
    assert leaves[0].proof_token is None

    # Attempting to synthesize root must fail
    engine.synthesize_node(root)
    assert root.status == TaskStatus.REJECTED
    assert root.energy_score == 1e6
