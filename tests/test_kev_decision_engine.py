"""
Test Suite for Kev Decision Engine & SAAW Integration.
Verifies TypeSafe System One schema compatibility, calibrated decision inference,
and automated gating for overnight model retraining.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from anse.decision.kev_engine import (
    KevDecisionEngine,
    SAAWRetrainDecision,
    evaluate_retraining_decision,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_kev_vendor_import() -> None:
    """Verify that kev is directly importable via vendor/kev / kev.pth."""
    import kev.api as kapi

    assert hasattr(kapi, "Noul")
    assert hasattr(kapi, "Choice")
    assert hasattr(kapi, "Score")
    assert hasattr(kapi, "SystemOneRequest")


def test_kev_systemone_schemas() -> None:
    """Verify that Kev System One schemas instantiate and validate correctly."""
    from kev.api import Choice, Noul, Score, SystemOneRequest

    req = SystemOneRequest(
        state={"test_key": "test_val", "loss": 1.25},
        model="kev-latest",
        questions={
            "q_noul": Noul(
                type="noul",
                instructions="Is this valid?",
                criteria={"true": "valid", "false": "invalid"},
            ),
            "q_choice": Choice(
                type="choice",
                instructions="Select team",
                criteria={"team_a": "alpha", "team_b": "beta"},
            ),
            "q_score": Score(
                type="score",
                instructions="Rate quality",
                criteria=["Low", "Medium", "High"],
            ),
        },
    )

    assert req.model == "kev-latest"
    assert "q_noul" in req.questions
    assert "q_choice" in req.questions
    assert "q_score" in req.questions


def test_kev_decision_evaluation_approved() -> None:
    """Verify calibrated decision evaluation on realistic healthy retraining telemetry."""
    engine = KevDecisionEngine(temperature=1.0)

    healthy_telemetry = {
        "status": "SUCCESS",
        "timestamp": "2026-09-29T05:00:00",
        "total_elapsed_sec": 1375.2,
        "steps": [
            {"step": "REM Dream Consolidation", "success": True, "returncode": 0},
            {"step": "Redis Memory Sync", "success": True, "returncode": 0},
            {"step": "Qwen LoRA LTM Retraining", "success": True, "returncode": 0},
            {"step": "RL Critic Retraining", "success": True, "returncode": 0},
            {"step": "JEPA World Model Continual Learning", "success": True, "returncode": 0},
            {"step": "ANSE V2 Autopoietic Engine Validation", "success": True, "returncode": 0},
        ],
    }

    decision: SAAWRetrainDecision = engine.evaluate_saaw_retraining(healthy_telemetry)

    assert decision.status == "APPROVED"
    assert decision.promote_checkpoint is True
    assert decision.promote_probability >= 0.90
    assert decision.deployment_strategy == "deploy_full_stack"
    assert decision.deployment_confidence >= 0.80
    assert decision.retraining_quality_score >= 2.0
    assert 0.0 <= decision.retraining_quality_confidence <= 1.0
    assert decision.next_cycle_adaptation in (
        "standard_schedule",
        "deepen_mcts_exploration",
        "prioritize_physics_invariants",
        "scale_lora_learning_rate",
    )
    assert "APPROVED" in decision.summary_reasoning


def test_kev_decision_evaluation_rejected_on_failure() -> None:
    """Verify that Kev decision engine rejects promotion when a training step fails or invariants degrade."""
    engine = KevDecisionEngine(temperature=1.0)

    failed_telemetry = {
        "status": "PARTIAL_FAILURE",
        "timestamp": "2026-09-29T05:00:00",
        "total_elapsed_sec": 450.0,
        "steps": [
            {"step": "REM Dream Consolidation", "success": True, "returncode": 0},
            {"step": "Redis Memory Sync", "success": True, "returncode": 0},
            {"step": "Qwen LoRA LTM Retraining", "success": False, "returncode": 137},  # OOM crash
            {"step": "RL Critic Retraining", "success": False, "returncode": 1},
        ],
    }

    decision: SAAWRetrainDecision = engine.evaluate_saaw_retraining(failed_telemetry)

    assert decision.status == "REJECTED"
    assert decision.promote_checkpoint is False
    assert decision.promote_probability < 0.15
    assert decision.deployment_strategy in ("rollback_to_parent", "quarantine_for_investigation")
    assert decision.retraining_quality_score < 1.0
    assert "REJECTED" in decision.summary_reasoning


def test_kev_decision_gate_cli(tmp_path: Path) -> None:
    """Verify that scripts/kev_decision_gate.py executes and enforces the gate."""
    # 1. Test passing gate on actual nightly report
    res_pass = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "kev_decision_gate.py"),
            "--gate",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert res_pass.returncode == 0, f"Gate failed on valid report: {res_pass.stderr}"
    assert "Gate passed" in res_pass.stderr or "Gate passed" in res_pass.stdout

    # 2. Test failing gate on simulated failure report
    bad_report = tmp_path / "bad_report.json"
    bad_report.write_text(
        json.dumps(
            {
                "status": "FAILURE",
                "steps": [{"step": "Training Crash", "success": False, "returncode": 1}],
            }
        ),
        encoding="utf-8",
    )
    bad_out = tmp_path / "bad_decision.json"

    res_fail = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "kev_decision_gate.py"),
            "--report",
            str(bad_report),
            "--out",
            str(bad_out),
            "--gate",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert res_fail.returncode == 1, "Gate should have exited with code 1 on failed report"
    assert bad_out.exists()
    d_bad = json.loads(bad_out.read_text(encoding="utf-8"))
    assert d_bad["status"] == "REJECTED"
