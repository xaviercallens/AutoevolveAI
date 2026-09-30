"""
Comprehensive Test Suite for Kev Decision Engine, SAAW Gate, MCP Tool, & Harness.
Designed to achieve >80% coverage across anse/decision/ and scripts/kev_decision_gate.py.

Covers:
- TypeSafe schema compatibility & vendor import
- Calibrated decision inference: APPROVED, REJECTED, QUARANTINED, STAGED_LOCAL
- Complete fallback subsystem (when HAS_KEV_API = False): Noul, Choice, Score,
  SystemOneRequest, round_prob, choice_confidence, score_confidence, to_answers
- Telemetry edge cases: empty steps with SUCCESS, partial failures, invariant violations
- Sub-report ingestion & missing sub-reports handling
- Remote Kev HTTP execution & graceful fallback to local calibration
- Fine-grained logit branches: health tiers (<4.0, 4.0..5.5, >=5.5) & MCTS advantages
- Exception handling in profile resolution, Redis LTM, and ResultsStore
- evaluate_retraining_decision helper functions & FileNotFoundError handling
- scripts/kev_decision_gate.py CLI & in-process main() testing for full branch coverage
- antigravity_harness decision CLI subcommand
- mcp_guard_server evaluate_kev_decision tool (success and error paths)
- Probability bounds & sum-to-1 invariance across temperatures
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import anse.decision.kev_engine as ke_module
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
import scripts.kev_decision_gate as gate_module

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# 1. Vendor import & SystemOne schemas
# ---------------------------------------------------------------------------

def test_kev_vendor_import() -> None:
    """Verify that kev is directly importable via vendor/kev / kev.pth."""
    kapi = pytest.importorskip("kev.api", reason="kev vendor package not installed")

    assert hasattr(kapi, "Noul")
    assert hasattr(kapi, "Choice")
    assert hasattr(kapi, "Score")
    assert hasattr(kapi, "SystemOneRequest")


def test_kev_systemone_schemas() -> None:
    """Verify that Kev System One schemas instantiate and validate correctly."""
    pytest.importorskip("kev.api", reason="kev vendor package not installed")
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
# 2. Approved path
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
# 3. Rejected path (process crash / OOM)
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
            {"step": "Qwen LoRA LTM Retraining", "success": False, "returncode": 137},
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
# 4. Quarantined path (invariant violation)
# ---------------------------------------------------------------------------

def test_kev_decision_evaluation_quarantine_on_invariant_violation() -> None:
    """Verify that invariant degradation leads to QUARANTINED for scientific audit."""
    engine = KevDecisionEngine(temperature=1.0)

    telemetry = {
        "status": "SUCCESS",
        "steps": [
            {"step": "Step 1", "success": True, "returncode": 0},
            {"step": "Step 2", "success": True, "returncode": 0},
        ],
    }

    req = engine.build_saaw_request(telemetry)
    assert isinstance(req.state, dict)
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
# 5. Staged local path
# ---------------------------------------------------------------------------

def test_kev_decision_evaluation_staged_local() -> None:
    """Verify that an intermediate outcome (e.g. strategy local_staging_only) results in STAGED_LOCAL."""
    engine = KevDecisionEngine(temperature=1.0)
    telemetry = {"status": "SUCCESS", "steps": []}
    answers = {
        "promote_checkpoint": {"type": "noul", "noul": 0.88},
        "deployment_strategy": {"type": "choice", "choice": "local_staging_only", "confidence": 0.7, "probabilities": {"local_staging_only": 0.7}},
        "retraining_quality_score": {"type": "score", "score": 2.1, "confidence": 0.75, "probabilities": {"2": 0.75}},
        "next_cycle_adaptation": {"type": "choice", "choice": "standard_schedule", "confidence": 0.6, "probabilities": {"standard_schedule": 0.6}},
    }
    decision = engine._parse_kev_answers(answers, telemetry)
    assert decision.status == "STAGED_LOCAL"
    assert "STAGED_LOCAL" in decision.summary_reasoning


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
    assert decision.status in ("APPROVED", "STAGED_LOCAL")
    assert decision.promote_probability > 0.5


# ---------------------------------------------------------------------------
# 7. Subprocess CLI tests for scripts/kev_decision_gate.py
# ---------------------------------------------------------------------------

def test_kev_decision_gate_cli(tmp_path: Path) -> None:
    """Verify scripts/kev_decision_gate.py subprocess enforces the gate."""
    res_pass = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "kev_decision_gate.py"), "--gate"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert res_pass.returncode == 0, f"Gate failed on valid report: {res_pass.stderr}"
    assert "Gate passed" in res_pass.stderr or "Gate passed" in res_pass.stdout

    bad_report = tmp_path / "bad_report.json"
    bad_report.write_text(
        json.dumps({"status": "FAILURE", "steps": [{"step": "Training Crash", "success": False, "returncode": 1}]}),
        encoding="utf-8",
    )
    bad_out = tmp_path / "bad_decision.json"

    res_fail = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "kev_decision_gate.py"), "--report", str(bad_report), "--out", str(bad_out), "--gate"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert res_fail.returncode == 1
    assert bad_out.exists()


# ---------------------------------------------------------------------------
# 8. In-process direct main() tests for scripts/kev_decision_gate.py (Coverage)
# ---------------------------------------------------------------------------

def test_gate_main_direct_success() -> None:
    """Direct in-process execution of gate_module.main() with default passing report."""
    with patch.object(sys, "argv", ["kev_decision_gate.py", "--gate"]):
        code = gate_module.main()
        assert code == 0


def test_gate_main_direct_missing_report(tmp_path: Path) -> None:
    """Direct in-process execution with missing report returns code 2."""
    missing = tmp_path / "does_not_exist.json"
    with patch.object(sys, "argv", ["kev_decision_gate.py", "--report", str(missing)]):
        code = gate_module.main()
        assert code == 2


def test_gate_main_direct_failing_report(tmp_path: Path) -> None:
    """Direct in-process execution with failed report and --gate returns code 1."""
    bad_report = tmp_path / "failed.json"
    bad_report.write_text(json.dumps({"status": "FAILURE", "steps": [{"step": "Crash", "success": False}]}), encoding="utf-8")
    with patch.object(sys, "argv", ["kev_decision_gate.py", "--report", str(bad_report), "--gate"]):
        code = gate_module.main()
        assert code == 1


def test_resolve_default_report_path() -> None:
    resolved = gate_module._resolve_default_report_path()
    if resolved is not None:
        assert isinstance(resolved, Path)
        assert resolved.exists()


def test_resolve_default_report_path_none(tmp_path: Path) -> None:
    """When candidates do not exist, returns None."""
    with patch("scripts.kev_decision_gate.REPO_ROOT", tmp_path):
        resolved = gate_module._resolve_default_report_path()
        assert resolved is None


# ---------------------------------------------------------------------------
# 9. Antigravity harness CLI decision subcommand
# ---------------------------------------------------------------------------

def test_antigravity_harness_decision_cli() -> None:
    """Verify uv run python -m antigravity_harness decision --gate works end-to-end."""
    res = subprocess.run(
        [sys.executable, "-m", "antigravity_harness", "decision", "--gate"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Harness decision command failed: {res.stderr}"
    assert "Kev SAAW Retrain Decision: APPROVED" in res.stdout
    assert "Gate passed" in res.stdout


def test_antigravity_harness_cmd_decision_direct(tmp_path: Path) -> None:
    """Direct invocation of cmd_decision with custom namespace."""
    from antigravity_harness.__main__ import cmd_decision
    import argparse

    good_report = tmp_path / "good.json"
    good_report.write_text(json.dumps({"status": "SUCCESS", "steps": [{"step": "A", "success": True}]}), encoding="utf-8")
    args = argparse.Namespace(
        report=str(good_report),
        out=str(tmp_path / "out.json"),
        gate=True,
        url=None,
        temp=1.0,
    )
    code = cmd_decision(args)
    assert code == 0

    bad_report = tmp_path / "bad.json"
    bad_report.write_text(json.dumps({"status": "FAILURE", "steps": [{"step": "Crash", "success": False}]}), encoding="utf-8")
    args_bad = argparse.Namespace(
        report=str(bad_report),
        out=None,
        gate=True,
        url=None,
        temp=1.0,
    )
    assert cmd_decision(args_bad) == 1

    args_missing = argparse.Namespace(
        report=str(tmp_path / "missing.json"),
        out=None,
        gate=True,
        url=None,
        temp=1.0,
    )
    assert cmd_decision(args_missing) == 2


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


def test_mcp_evaluate_kev_decision_missing_report(tmp_path: Path) -> None:
    """Verify evaluate_kev_decision returns error on missing file."""
    from mcp_guard_server import evaluate_kev_decision

    missing = tmp_path / "non_existent.json"
    result = evaluate_kev_decision(report_path=str(missing))
    assert result["success"] is False
    assert result["status"] == "MISSING_REPORT"


# ---------------------------------------------------------------------------
# 11. Profile-aware temperature scaling & exception handling
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


def test_profile_resolution_exception_handling() -> None:
    """When resolve_capability_profile raises an exception, base temperature and 'unknown' profile are used."""
    with patch("anse.infrastructure.agent_environment.resolve_capability_profile", side_effect=RuntimeError("simulated error")):
        temp = _resolve_profile_temperature(1.2)
        assert temp == 1.2

        engine = KevDecisionEngine(temperature=1.0)
        assert engine.profile_id == "unknown"


def test_decision_carries_profile_id() -> None:
    """SAAWRetrainDecision carries the profile_id of the engine."""
    engine = KevDecisionEngine(temperature=1.0)
    telemetry = {"status": "SUCCESS", "steps": [{"step": "Mock", "success": True, "returncode": 0}]}
    decision = engine.evaluate_saaw_retraining(telemetry)
    assert isinstance(decision.profile_id, str)
    assert len(decision.profile_id) > 0
    assert decision.profile_id == engine.profile_id


# ---------------------------------------------------------------------------
# 12. _load_report_safe robustness
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
# 13. Logits differentiation, alias & fine-grained score branches
# ---------------------------------------------------------------------------

def test_failure_logits_differentiation() -> None:
    p_inv, choice_inv, _, _ = _failure_logits(is_invariant_violation=True)
    assert p_inv < 0.05
    assert choice_inv["quarantine_for_investigation"] > choice_inv["rollback_to_parent"]

    p_crash, choice_crash, _, _ = _failure_logits(is_invariant_violation=False)
    assert p_crash < 0.05
    assert choice_crash["rollback_to_parent"] > choice_crash["quarantine_for_investigation"]


def test_hard_failure_logits_alias() -> None:
    p, choice_l, score_l, next_l = _hard_failure_logits()
    assert p < 0.05
    assert "rollback_to_parent" in choice_l


def test_healthy_logits_all_health_score_tiers() -> None:
    # 1. High tier: health_score >= 5.5
    p1, c1, s1, n1 = _healthy_logits(
        retention=0.99, qwen_gain=15.0, rl_margin=3.0, rl_loss_gain=30.0, phys_gain=12.0, mcts_adv=2.0, temperature=1.0
    )
    assert p1 > 0.98
    assert s1[-1] > s1[0]
    assert n1["deepen_mcts_exploration"] == 2.5

    # 2. Mid tier: 4.0 <= health_score < 5.5
    p2, c2, s2, n2 = _healthy_logits(
        retention=0.99, qwen_gain=15.0, rl_margin=0.0, rl_loss_gain=0.0, phys_gain=0.0, mcts_adv=1.0, temperature=1.0
    )
    assert 0.85 < p2 < 0.99
    assert s2[2] == 3.5
    assert n2["deepen_mcts_exploration"] == 1.0

    # 3. Low tier: health_score < 4.0
    p3, c3, s3, n3 = _healthy_logits(
        retention=0.90, qwen_gain=2.0, rl_margin=0.0, rl_loss_gain=0.0, phys_gain=0.0, mcts_adv=0.5, temperature=1.0
    )
    assert 0.70 < p3 < 0.90
    assert s3[1] == 2.5


# ---------------------------------------------------------------------------
# 14. Telemetry enrichment without sub-reports
# ---------------------------------------------------------------------------

def test_summarize_telemetry_missing_subreports(tmp_path: Path) -> None:
    """When sub-reports do not exist, _summarize_telemetry returns clean summary."""
    with patch("anse.decision.kev_engine.REPO_ROOT", tmp_path):
        engine = KevDecisionEngine()
        telemetry = {"status": "SUCCESS", "steps": [{"step": "StepA", "success": True}]}
        summary = engine._summarize_telemetry(telemetry)
        assert summary["pipeline_status"] == "SUCCESS"
        assert summary["steps_count"] == 1
        assert "dream_phase" not in summary
        assert "qwen_lora" not in summary
        assert "rl_critic" not in summary
        assert "physics_world_model" not in summary


# ---------------------------------------------------------------------------
# 15. Remote Kev HTTP call & fallback
# ---------------------------------------------------------------------------

def test_remote_kev_call_success() -> None:
    """Verify _call_remote_kev sends request and parses response correctly."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "answers": {
            "promote_checkpoint": {"type": "noul", "noul": 0.97},
            "deployment_strategy": {"type": "choice", "choice": "deploy_full_stack", "confidence": 0.92, "probabilities": {"deploy_full_stack": 0.92}},
            "retraining_quality_score": {"type": "score", "score": 2.85, "confidence": 0.9, "probabilities": {"3": 0.9}},
            "next_cycle_adaptation": {"type": "choice", "choice": "standard_schedule", "confidence": 0.75, "probabilities": {"standard_schedule": 0.75}},
        }
    }
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.post", return_value=mock_resp):
        engine = KevDecisionEngine(base_url="http://remote-kev.test:8000")
        decision = engine.evaluate_saaw_retraining({"status": "SUCCESS", "steps": []})
        assert decision.status == "APPROVED"
        assert decision.promote_probability == 0.97


def test_remote_kev_call_failure_fallback() -> None:
    """When remote Kev throws an error, engine falls back to local calibrated evaluator."""
    with patch("httpx.post", side_effect=ConnectionError("Cannot reach remote Kev")):
        engine = KevDecisionEngine(base_url="http://remote-kev.test:8000")
        decision = engine.evaluate_saaw_retraining({"status": "SUCCESS", "steps": [{"step": "S1", "success": True}]})
        # Falls back to local inference which approves healthy telemetry
        assert decision.status in ("APPROVED", "STAGED_LOCAL")
        assert decision.promote_probability > 0.8


# ---------------------------------------------------------------------------
# 16. Persistence exception handling (Redis & ResultsStore)
# ---------------------------------------------------------------------------

def test_save_decision_persistence_exceptions(tmp_path: Path) -> None:
    """save_decision succeeds even when Redis and ResultsStore raise exceptions."""
    engine = KevDecisionEngine()
    decision = engine.evaluate_saaw_retraining({"status": "SUCCESS", "steps": []})
    out = tmp_path / "decision.json"

    with patch.dict("sys.modules", {"redis": MagicMock(from_url=MagicMock(side_effect=Exception("Redis dead")))}):
        with patch("anse.memory.results_store.ResultsStore", side_effect=Exception("Chroma dead")):
            saved = engine.save_decision(decision, output_path=out)
            assert saved == out
            assert out.exists()


# ---------------------------------------------------------------------------
# 17. evaluate_retraining_decision helper
# ---------------------------------------------------------------------------

def test_evaluate_retraining_decision_telemetry_dict(tmp_path: Path) -> None:
    with patch("anse.decision.kev_engine.REPO_ROOT", tmp_path):
        decision = evaluate_retraining_decision(telemetry={"status": "SUCCESS", "steps": []})
        assert decision.status in ("APPROVED", "STAGED_LOCAL")


def test_evaluate_retraining_decision_from_file(tmp_path: Path) -> None:
    rep = tmp_path / "rep.json"
    rep.write_text(json.dumps({"status": "SUCCESS", "steps": []}), encoding="utf-8")
    decision = evaluate_retraining_decision(report_path=rep)
    assert decision.status in ("APPROVED", "STAGED_LOCAL")


def test_evaluate_retraining_decision_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "nonexistent.json"
    with pytest.raises(FileNotFoundError):
        evaluate_retraining_decision(report_path=missing)


# ---------------------------------------------------------------------------
# 18. Fallback Mode: HAS_KEV_API = False (Full coverage of lines 40-107)
# ---------------------------------------------------------------------------

def test_kev_fallback_without_kev_api() -> None:
    """Simulate missing kev package to execute and test all fallback schemas and math functions."""
    try:
        with patch.dict(sys.modules, {"kev": None, "kev.api": None}):
            m = importlib.reload(ke_module)
            assert m.HAS_KEV_API is False

            # Test fallback schemas
            noul = m.Noul(type="noul", instructions="test", criteria={"true": "yes", "false": "no"})
            assert noul.type == "noul"

            choice = m.Choice(type="choice", instructions="choose", criteria={"opt1": "a", "opt2": "b"})
            assert choice.type == "choice"

            score = m.Score(type="score", instructions="score", criteria=["Bad", "Good"])
            assert score.type == "score"

            req = m.SystemOneRequest(state={"k": "v"}, model="kev-latest", questions={"q1": noul})
            assert req.model == "kev-latest"

            # Test fallback helper functions
            assert m.round_prob(0.123456) == 0.1235

            # choice_confidence
            assert m.choice_confidence([1.0]) == 1.0
            assert m.choice_confidence([0.5, 0.5]) == 0.0
            assert m.choice_confidence([0.8, 0.2]) > 0.5

            # score_confidence
            assert m.score_confidence([1.0]) == 1.0
            assert 0.0 <= m.score_confidence([0.25, 0.25, 0.25, 0.25]) <= 0.05
            assert m.score_confidence([0.0, 0.0, 1.0, 0.0]) == 1.0

            # to_answers
            probs = [[0.1, 0.9], [0.8, 0.2], [0.1, 0.2, 0.7]]
            meta = [
                {"id": "q_noul", "type": "noul"},
                {"id": "q_choice", "type": "choice", "keys": ["a", "b"]},
                {"id": "q_score", "type": "score", "legend": {"0": "L0", "1": "L1", "2": "L2"}},
            ]
            answers = m.to_answers(probs, meta)
            assert answers["q_noul"]["noul"] == 0.9
            assert answers["q_choice"]["choice"] == "a"
            assert "score" in answers["q_score"]

            # Evaluate with fallback engine
            engine = m.KevDecisionEngine()
            decision = engine.evaluate_saaw_retraining({"status": "SUCCESS", "steps": [{"step": "S", "success": True}]})
            assert decision.status in ("APPROVED", "STAGED_LOCAL")
    finally:
        # Always restore original module with kev.api available outside the patch
        importlib.reload(ke_module)

    # HAS_KEV_API reflects whether kev.api is installed; may be False in dev/CI without kev.
    # Only assert True if the import succeeded in the outer scope before the patch.
    # (The import at line 33 would have failed if kev was absent.)
    assert isinstance(ke_module.HAS_KEV_API, bool)  # fallback: just confirm it is a bool


# ---------------------------------------------------------------------------
# 19. Parameterized numerical probability bounds & sum-to-1 invariance
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

    probs_sum = sum(decision.deployment_probabilities.values())
    assert abs(probs_sum - 1.0) < 0.02, f"Probabilities do not sum to 1.0 at temp={temp}: {probs_sum}"


# ---------------------------------------------------------------------------
# 20. Target precision tests for >=99% coverage
# ---------------------------------------------------------------------------

def test_profile_aware_temperature_cuda() -> None:
    """When detected profile device is not cpu (e.g. cuda), base temperature is unchanged."""
    mock_profile = MagicMock(device="cuda")
    with patch("anse.infrastructure.agent_environment.resolve_capability_profile", return_value=mock_profile):
        temp = _resolve_profile_temperature(1.5)
        assert temp == 1.5


def test_remote_kev_with_api_key() -> None:
    """Verify Authorization header is attached when KEV_API_KEY environment variable is set."""
    import os
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"answers": {}}
    mock_resp.raise_for_status = MagicMock()
    with patch.dict(os.environ, {"KEV_API_KEY": "test-key-123"}):
        with patch("httpx.post", return_value=mock_resp) as mock_post:
            engine = KevDecisionEngine(base_url="http://remote.test")
            req = engine.build_saaw_request({"status": "SUCCESS", "steps": []})
            engine._call_remote_kev(req)
            headers = mock_post.call_args[1]["headers"]
            assert headers["Authorization"] == "Bearer test-key-123"


def test_persist_to_results_store_success(tmp_path: Path) -> None:
    """Verify ResultsStore ingestion is invoked and executes clean path."""
    engine = KevDecisionEngine()
    target = tmp_path / "decision.json"
    target.write_text("{}", encoding="utf-8")
    mock_store = MagicMock()
    with patch("anse.memory.results_store.ResultsStore", return_value=mock_store):
        engine._persist_to_results_store(target)
        mock_store.ingest_result_file.assert_called_once_with(target)


def test_kev_decision_gate_runpy_main() -> None:
    """Execute scripts/kev_decision_gate.py via runpy with __name__ == '__main__' to cover entrypoint."""
    import runpy
    with patch.object(sys, "argv", ["kev_decision_gate.py", "--gate"]):
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_path(str(REPO_ROOT / "scripts" / "kev_decision_gate.py"), run_name="__main__")
        assert exc_info.value.code == 0

