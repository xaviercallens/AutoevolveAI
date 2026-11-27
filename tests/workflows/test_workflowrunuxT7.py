"""
Unit tests for Tier 7 Workflow (workflowrunuxT7_tpu_convergence.py).
Validates the RunuX-Ubuntu Convergence & Google TPU Hardness Harness.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from workflowrunuxT7_tpu_convergence import (
    ANSEPhysicsEngine,
    GateResult,
    RunuxT7ConvergenceWorkflowRunner,
)


class TestANSEPhysicsEngine:
    def test_energy_calculation_nominal(self):
        engine = ANSEPhysicsEngine(wt=1.0, wm=2.0)
        # 10ms, 20MB -> 10*1.0 + 20*2.0 = 50.0
        energy = engine.calculate_energy(duration_ms=10.0, peak_rss_mb=20.0, failed=False)
        assert energy == 50.0

    def test_energy_calculation_failure_penalty(self):
        engine = ANSEPhysicsEngine(max_penalty=1_000_000.0)
        energy = engine.calculate_energy(duration_ms=5.0, peak_rss_mb=10.0, failed=True)
        assert energy == 1_000_000.0

    def test_mint_proof_token(self):
        engine = ANSEPhysicsEngine()
        token = engine.mint_proof_token("TEST_PAYLOAD")
        assert token.startswith("PROOF_TOKEN:")
        assert len(token) == len("PROOF_TOKEN:") + 16

    def test_mint_master_receipt(self):
        engine = ANSEPhysicsEngine()
        tokens = [engine.mint_proof_token("T1"), engine.mint_proof_token("T2")]
        receipt = engine.mint_master_receipt(tokens)
        assert receipt.startswith("PROOF_RECEIPT:RUNUX_UBUNTU_TPU_CONVERGENCE_")


class TestRunuxT7Gates:
    @pytest.fixture
    def runner(self):
        return RunuxT7ConvergenceWorkflowRunner(dry_run=True)

    def test_gate1_syscall_trampoline(self, runner):
        result = runner.run_gate1_syscall_trampoline()
        assert isinstance(result, GateResult)
        assert result.status == "PASSED"
        assert result.gate_id == "T7.1"
        assert result.details["stat_size_bytes"] == 144
        assert result.details["msr_lstar"] == "0xc0000082"
        assert result.proof_token is not None

    def test_gate2_systemd_crucible(self, runner):
        result = runner.run_gate2_systemd_crucible()
        assert isinstance(result, GateResult)
        assert result.status == "PASSED"
        assert result.gate_id == "T7.2"
        assert result.details["proc_stat_fields"] >= 20
        assert "cpu" in result.details["cgroups_v2_controllers"]
        assert result.proof_token is not None

    def test_gate3_tpu_acceleration(self, runner):
        result = runner.run_gate3_tpu_acceleration()
        assert isinstance(result, GateResult)
        assert result.status == "PASSED"
        assert result.gate_id == "T7.3"
        assert result.details["doorbell_speedup_ratio"] > 50.0
        assert result.details["ai_speedup_gain_pct"] >= 25.0
        assert result.details["composite_ai_gain_pct"] >= 50.0
        assert result.details["gigapage_size_bytes"] % 128 == 0
        assert result.proof_token is not None

    def test_gate4_gwaya_lsm(self, runner):
        result = runner.run_gate4_gwaya_lsm()
        assert isinstance(result, GateResult)
        assert result.status == "PASSED"
        assert result.gate_id == "T7.4"
        assert result.details["blocked_count"] >= 2
        assert result.details["passed_count"] >= 2
        assert result.details["flr_guillotine_status"] == "ARMED_AND_VERIFIED"
        assert result.proof_token is not None

    def test_gate5_boot_curriculum(self, runner):
        result = runner.run_gate5_boot_curriculum()
        assert isinstance(result, GateResult)
        assert result.status == "PASSED"
        assert result.gate_id == "T7.5"
        assert result.details["milestones_reached"] == 4
        assert result.details["convergence_status"] == "CONVERGED_100_PERCENT"
        assert result.proof_token is not None

    def test_run_all_gates_e2e(self, runner, tmp_path):
        report = runner.run_all_gates()
        assert report["tier"] == "T7"
        assert report["status"] == "PASSED_100_PERCENT"
        assert report["gates_evaluated"] == 5
        assert report["gates_passed"] == 5
        assert len(report["proof_tokens"]) == 5
        assert report["master_proof_receipt"].startswith("PROOF_RECEIPT:RUNUX_UBUNTU_TPU_CONVERGENCE_")
        assert report["cumulative_energy"] < 1_000_000.0  # Must not incur maximum pain penalty
