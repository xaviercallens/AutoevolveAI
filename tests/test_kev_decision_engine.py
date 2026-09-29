"""
Test Suite for Kev Decision Engine & SAAW Integration (v2).
Covers: TypeSafe schema compatibility, calibrated decision inference,
profile-aware temperature scaling, _load_report_safe error handling,
Redis LTM persistence, and automated gating for overnight model retraining.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from anse.decision.kev_engine import (
    KevDecisionEngine,
    SAAWRetrainDecision,
    _hard_failure_logits,
    _healthy_logits,
    _load_report_safe,
    _resolve_profile_temperature,
    evaluate_retraining_decision,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# 1. Vendor import
# ---------------------------------------------------------------------------

def test_kev_vendor_import() -> None:
    """Verify that kev is directly importable via vendor/kev / kev.pth."""
    import kev.api as kapi

    assert hasattr(kapi, "Noul")
    assert hasattr(kapi, "Choice")
    assert hasattr(kapi, "Score")
    assert hasattr(kapi, "SystemOneRequest")


# ---------------------------------------------------------------------------
# 2. Schema validation
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# 3. Approved path
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# 4. Rejected path
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# 5. CLI gate
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# 6. Profile-aware temperature scaling
# ---------------------------------------------------------------------------

def test_profile_aware_temperature_cpu() -> None:
    """Profile-aware engine on CPU profile raises temperature by _CPU_TEMPERATURE_OFFSET."""
    from anse.decision.kev_engine import _CPU_TEMPERATURE_OFFSET

    with patch("anse.decision.kev_engine._resolve_profile_temperature") as mock_resolve:
        # Simulate CPU profile returning base + offset
        mock_resolve.side_effect = lambda t: t + _CPU_TEMPERATURE_OFFSET
        engine = KevDecisionEngine(temperature=1.0, profile_aware=True)
        assert abs(engine.temperature - (1.0 + _CPU_TEMPERATURE_OFFSET)) < 1e-9
        assert engine._base_temperature == 1.0


def test_profile_aware_disabled() -> None:
    """With profile_aware=False temperature is used as-is."""
    engine = KevDecisionEngine(temperature=0.8, profile_aware=False)
    assert engine.temperature == 0.8
    assert engine._base_temperature == 0.8


# ---------------------------------------------------------------------------
# 7. profile_id stamped on decision
# ---------------------------------------------------------------------------

def test_decision_carries_profile_id() -> None:
    """SAAWRetrainDecision should carry the profile_id of the engine that made it."""
    engine = KevDecisionEngine(temperature=1.0)
    telemetry = {
        "status": "SUCCESS",
        "steps": [{"step": "Mock", "success": True, "returncode": 0}],
    }
    decision = engine.evaluate_saaw_retraining(telemetry)
    # profile_id should be non-empty and match the engine's detected profile
    assert isinstance(decision.profile_id, str)
    assert len(decision.profile_id) > 0
    assert decision.profile_id == engine.profile_id


# ---------------------------------------------------------------------------
# 8. _load_report_safe – missing file returns None, bad JSON returns None+logs
# ---------------------------------------------------------------------------

def test_load_report_safe_missing(tmp_path: Path) -> None:
    missing = tmp_path / "nonexistent.json"
    result = _load_report_safe(missing, "test")
    assert result is None


def test_load_report_safe_bad_json(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json}", encoding="utf-8")
    result = _load_report_safe(bad, "test")
    assert result is None


def test_load_report_safe_valid(tmp_path: Path) -> None:
    good = tmp_path / "good.json"
    good.write_text(json.dumps({"key": 42}), encoding="utf-8")
    result = _load_report_safe(good, "test")
    assert result == {"key": 42}


# ---------------------------------------------------------------------------
# 9. _hard_failure_logits / _healthy_logits purity
# ---------------------------------------------------------------------------

def test_hard_failure_logits_structure() -> None:
    p, choice_l, score_l, next_l = _hard_failure_logits()
    assert p < 0.1
    assert "deploy_full_stack" in choice_l
    assert "rollback_to_parent" in choice_l
    assert len(score_l) == 4
    assert "prioritize_physics_invariants" in next_l


def test_healthy_logits_health_score_scaling() -> None:
    # High-quality run: high retention, big Qwen gain, high RL margins, high physics
    p, choice_l, score_l, next_l = _healthy_logits(
        retention=0.99,
        qwen_gain=15.0,
        rl_margin=3.0,
        rl_loss_gain=40.0,
        phys_gain=12.0,
        mcts_adv=2.0,
        temperature=1.0,
    )
    assert p > 0.98  # health_score=6.2 → sigmoid very close to 1
    assert choice_l["deploy_full_stack"] > 5.0  # bonus applied
    assert score_l[-1] > score_l[0]  # best tier logit > worst


# ---------------------------------------------------------------------------
# 10. Redis LTM persistence (mocked)
# ---------------------------------------------------------------------------

def test_redis_ltm_persistence_mocked(tmp_path: Path) -> None:
    """Verify save_decision attempts Redis LTM and fails gracefully when Redis unavailable."""
    engine = KevDecisionEngine(temperature=1.0)
    telemetry = {
        "status": "SUCCESS",
        "steps": [{"step": "Mock", "success": True, "returncode": 0}],
    }
    decision = engine.evaluate_saaw_retraining(telemetry)

    out = tmp_path / "decision.json"
    # With no real Redis (localhost typically not running in CI), save_decision must not raise
    saved = engine.save_decision(decision, output_path=out)
    assert saved == out
    assert out.exists()
    loaded = json.loads(out.read_text())
    assert loaded["status"] == decision.status
    assert "profile_id" in loaded
