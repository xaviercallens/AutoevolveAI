"""
Comprehensive Test Suite for Kev Decision Engine, SAAW Gate, MCP Tool, & Harness.
Covers:
- TypeSafe schema compatibility & vendor import
- Calibrated decision inference: APPROVED, REJECTED, QUARANTINED
- Telemetry edge cases: empty steps with SUCCESS, partial failures, invariant violations
- Provenance diagnostics: failed_steps reported in reasoning
- Profile-aware temperature scaling (Antigravity CPU +0.08 offset)
- scripts/kev_decision_gate.py CLI & interim/final report resolution
- antigravity_harness decision CLI subcommand
- mcp_guard_server evaluate_kev_decision tool
- Dual-tier LTM persistence (Redis LTM + Chroma ResultsStore)
- Numerical & probability bounds across diverse temperature regimes
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
    _failure_logits,
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
    assert len(decision.failed_steps) == 0
    assert "APPROVED" in decision.summary_reasoning


# ---------------------------------------------------------------------------
# 4. Rejected path (process crash / OOM)
# ---------------------------------------------------------------------------

def test_kev_decision_evaluation_rejected_on_step_failure() -> None:
    """Verify that process crash leads to REJECTED with rollback_to_parent."""
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
    assert decision.deployment_strategy == "rollback_to_parent"
    assert decision.retraining_quality_score < 1.0
    assert "Qwen LoRA LTM Retraining" in decision.failed_steps
    assert "RL Critic Retraining" in decision.failed_steps
    assert "Qwen LoRA LTM Retraining" in decision.summary_reasoning


# ---------------------------------------------------------------------------
# 5. Quarantined path (invariant violation)
# ---------------------------------------------------------------------------

def test_kev_decision_evaluation_quarantine_on_invariant_violation(tmp_path: Path) -> None:
    """Verify that invariant degradation leads to QUARANTINED for scientific audit."""
    engine = KevDecisionEngine(temperature=1.0)

    # Telemetry where all steps finished, but physics reports invariant degradation
    telemetry = {
        "status": "SUCCESS",
        "steps": [
            {"step": "Step 1", "success": True, "returncode": 0},
            {"step": "Step 2", "success": True, "returncode": 0},
        ],
    }

    # Simulate invariant failure in the request state
    req = engine.build_saaw_request(telemetry)
    assert isinstance(req.state, dict)
    # Inject invariant failure
    req.state["physics_world_model"] = {
        "total_cases": 10,
        "passed_invariants": 7,  # 70% < 90% threshold
        "loss_reduction": 0.0,
        "invariant_pass_rate": 0.70,
    }

    answers = engine._local_calibrated_decision(req, telemetry)
    decision = engine._parse_kev_answers(answers, telemetry)

    assert decision.status == "QUARANTINED"
    assert decision.promote_checkpoint is False
    assert decision.deployment_strategy == "quarantine_for_investigation"
    assert "QUARANTINED" in decision.summary_reasoning


# ---------------------------------------------------------------------------
# 6. Edge case: empty steps with SUCCESS status
# ---------------------------------------------------------------------------

def test_kev_decision_evaluation_empty_steps_success() -> None:
    """Empty steps list with status=SUCCESS should not falsely trigger crash failure."""
    engine = KevDecisionEngine(temperature=1.0)
    telemetry = {
        "status": "SUCCESS",
        "steps": [],
        "total_elapsed_sec": 100.0,
    }
    decision = engine.evaluate_saaw_retraining(telemetry)
    # Should not be hard failure
    assert decision.status in ("APPROVED", "STAGED_LOCAL")
    assert decision.promote_probability > 0.5


# ---------------------------------------------------------------------------
# 7. CLI gate script
# ---------------------------------------------------------------------------

def test_kev_decision_gate_cli(tmp_path: Path) -> None:
    """Verify scripts/kev_decision_gate.py enforces the gate."""
    # 1. Passing gate on actual report
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

    # 2. Failing gate on failure report
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
    assert res_fail.returncode == 1
    assert bad_out.exists()
    d_bad = json.loads(bad_out.read_text(encoding="utf-8"))
    assert d_bad["status"] in ("REJECTED", "QUARANTINED")


# ---------------------------------------------------------------------------
# 8. Interim report resolution in gate
# ---------------------------------------------------------------------------

def test_resolve_default_report_path(tmp_path: Path) -> None:
    from scripts.kev_decision_gate import _resolve_default_report_path

    resolved = _resolve_default_report_path()
    # If any report exists in results/nightly_training, resolved must be a valid Path
    if resolved is not None:
        assert isinstance(resolved, Path)
        assert resolved.exists()


# ---------------------------------------------------------------------------
# 9. Antigravity harness CLI decision subcommand
# ---------------------------------------------------------------------------

def test_antigravity_harness_decision_cli() -> None:
    """Verify uv run python -m antigravity_harness decision --gate works end-to-end."""
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "antigravity_harness",
            "decision",
            "--gate",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Harness decision command failed: {res.stderr}"
    assert "Kev SAAW Retrain Decision: APPROVED" in res.stdout
    assert "Gate passed" in res.stdout


# ---------------------------------------------------------------------------
# 10. FastMCP server evaluate_kev_decision tool
# ---------------------------------------------------------------------------

def test_mcp_evaluate_kev_decision() -> None:
    """Verify mcp_guard_server.evaluate_kev_decision tool executes and returns structured JSON."""
    from mcp_guard_server import evaluate_kev_decision

    result = evaluate_kev_decision(enforce_gate=True)
    assert result["success"] is True
    assert result["gate_passed"] is True
    assert "decision" in result
    decision_dict = result["decision"]
    assert decision_dict["status"] == "APPROVED"
    assert decision_dict["promote_checkpoint"] is True
    assert "profile_id" in decision_dict


# ---------------------------------------------------------------------------
# 11. Profile-aware temperature scaling
# ---------------------------------------------------------------------------

def test_profile_aware_temperature_cpu() -> None:
    """Profile-aware engine on CPU profile raises temperature by _CPU_TEMPERATURE_OFFSET."""
    from anse.decision.kev_engine import _CPU_TEMPERATURE_OFFSET

    with patch("anse.decision.kev_engine._resolve_profile_temperature") as mock_resolve:
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
# 12. profile_id stamped on decision
# ---------------------------------------------------------------------------

def test_decision_carries_profile_id() -> None:
    """SAAWRetrainDecision carries the profile_id of the engine."""
    engine = KevDecisionEngine(temperature=1.0)
    telemetry = {
        "status": "SUCCESS",
        "steps": [{"step": "Mock", "success": True, "returncode": 0}],
    }
    decision = engine.evaluate_saaw_retraining(telemetry)
    assert isinstance(decision.profile_id, str)
    assert len(decision.profile_id) > 0
    assert decision.profile_id == engine.profile_id


# ---------------------------------------------------------------------------
# 13. _load_report_safe robustness
# ---------------------------------------------------------------------------

def test_load_report_safe_edge_cases(tmp_path: Path) -> None:
    missing = tmp_path / "nonexistent.json"
    assert _load_report_safe(missing, "test") is None

    bad = tmp_path / "bad.json"
    bad.write_text("{corrupt json", encoding="utf-8")
    assert _load_report_safe(bad, "test") is None

    good = tmp_path / "good.json"
    good.write_text(json.dumps({"key": 100}), encoding="utf-8")
    assert _load_report_safe(good, "test") == {"key": 100}


# ---------------------------------------------------------------------------
# 14. Logit differentiation: invariant violation vs process crash
# ---------------------------------------------------------------------------

def test_failure_logits_differentiation() -> None:
    # 1. Invariant violation: quarantine should dominate
    p_inv, choice_inv, _, _ = _failure_logits(is_invariant_violation=True)
    assert p_inv < 0.05
    assert choice_inv["quarantine_for_investigation"] > choice_inv["rollback_to_parent"]

    # 2. Process crash: rollback should dominate
    p_crash, choice_crash, _, _ = _failure_logits(is_invariant_violation=False)
    assert p_crash < 0.05
    assert choice_crash["rollback_to_parent"] > choice_crash["quarantine_for_investigation"]


def test_healthy_logits_scaling() -> None:
    p, choice_l, score_l, next_l = _healthy_logits(
        retention=0.99,
        qwen_gain=15.0,
        rl_margin=3.0,
        rl_loss_gain=40.0,
        phys_gain=12.0,
        mcts_adv=2.0,
        temperature=1.0,
    )
    assert p > 0.98
    assert choice_l["deploy_full_stack"] > 5.0
    assert score_l[-1] > score_l[0]


# ---------------------------------------------------------------------------
# 15. Dual persistence (Redis + Chroma ResultsStore)
# ---------------------------------------------------------------------------

def test_dual_persistence_graceful_fallback(tmp_path: Path) -> None:
    """Verify save_decision succeeds and writes disk file even if Redis/Chroma are mocked/offline."""
    engine = KevDecisionEngine(temperature=1.0)
    telemetry = {
        "status": "SUCCESS",
        "steps": [{"step": "Mock", "success": True, "returncode": 0}],
    }
    decision = engine.evaluate_saaw_retraining(telemetry)

    out = tmp_path / "decision.json"
    saved = engine.save_decision(decision, output_path=out)
    assert saved == out
    assert out.exists()
    loaded = json.loads(out.read_text())
    assert loaded["status"] == decision.status
    assert "profile_id" in loaded
    assert "failed_steps" in loaded


# ---------------------------------------------------------------------------
# 16. Numerical & probability bounds across diverse temperature regimes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("temp", [0.1, 0.5, 1.0, 2.0, 5.0])
def test_temperature_probability_bounds(temp: float) -> None:
    """Verify probabilities remain strictly in [0.0, 1.0] and sum to 1.0 ± 0.02 across temperatures."""
    engine = KevDecisionEngine(temperature=temp, profile_aware=False)
    telemetry = {
        "status": "SUCCESS",
        "steps": [{"step": "TestStep", "success": True, "returncode": 0}],
    }
    decision = engine.evaluate_saaw_retraining(telemetry)

    assert 0.0 <= decision.promote_probability <= 1.0
    assert 0.0 <= decision.deployment_confidence <= 1.0
    assert 0.0 <= decision.retraining_quality_confidence <= 1.0
    assert 0.0 <= decision.retraining_quality_score <= 3.0

    # Verify probability distribution sums to 1.0 ± 0.02
    probs_sum = sum(decision.deployment_probabilities.values())
    assert abs(probs_sum - 1.0) < 0.02, f"Probabilities do not sum to 1.0 at temp={temp}: {probs_sum}"
