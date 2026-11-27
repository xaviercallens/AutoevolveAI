"""
Unit tests for Xavuntu AIOps Hardness Workflow (workflowAIOps.py).
Validates closed-loop autonomous optimization, self-healing, and ANSE thermodynamics.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from anse.aiops.engine import AIOpsEngine, AIOpsTelemetry, RemediationResult
from workflowAIOps import (
    AIOpsGateResult,
    AIOpsHardnessReport,
    AIOpsPhysicsEngine,
    AIOpsWorkflowRunner,
)


class TestAIOpsPhysicsEngine:
    def test_energy_nominal(self):
        engine = AIOpsPhysicsEngine(w_time=1.0, w_mem=2.0)
        energy = engine.calculate_energy(duration_ms=10.0, peak_rss_mb=20.0, failed=False)
        assert energy == 50.0

    def test_energy_failure_penalty(self):
        engine = AIOpsPhysicsEngine(penalty=1_000_000.0)
        energy = engine.calculate_energy(duration_ms=5.0, peak_rss_mb=10.0, failed=True)
        assert energy == 1_000_000.0

    def test_proof_token_minting(self):
        engine = AIOpsPhysicsEngine()
        token = engine.mint_proof_token("TEST_AIOPS_PAYLOAD")
        assert token.startswith("PROOF_TOKEN:")
        assert len(token) == len("PROOF_TOKEN:") + 16


class TestAIOpsGates:
    @pytest.fixture
    def runner(self):
        return AIOpsWorkflowRunner(dry_run=True)

    def test_gate1_memory_vram(self, runner):
        result = runner.run_gate1_memory_vram()
        assert isinstance(result, AIOpsGateResult)
        assert result.status == "PASSED"
        assert result.gate_id == "G1_MEMORY_VRAM_RECLAMATION"
        assert result.details["freed_mb"] >= 1500.0
        assert result.proof_token is not None

    def test_gate2_toolchain_hygiene(self, runner):
        result = runner.run_gate2_toolchain_hygiene()
        assert isinstance(result, AIOpsGateResult)
        assert result.status == "PASSED"
        assert result.gate_id == "G2_TOOLCHAIN_STORAGE_HYGIENE"
        assert result.proof_token is not None

    def test_gate3_tpu_and_io(self, runner):
        result = runner.run_gate3_tpu_and_io()
        assert isinstance(result, AIOpsGateResult)
        assert result.status == "PASSED"
        assert result.gate_id == "G3_TPU_SYSTOLIC_IO"
        assert result.details["details"]["tpu_latency_ns"] <= 200.0
        assert result.details["details"]["gigapage_aligned"] is True
        assert result.proof_token is not None

    def test_gate4_gwaya_system2_rca(self, runner):
        result = runner.run_gate4_gwaya_system2_rca()
        assert isinstance(result, AIOpsGateResult)
        assert result.status == "PASSED"
        assert result.gate_id == "G4_GWAYA_SYSTEM2_RCA"
        assert "rca_engine" in result.details
        assert len(result.details["remediation_plan"]) >= 2
        assert result.proof_token is not None

    def test_gate5_closed_loop_thermodynamics(self, runner):
        result = runner.run_gate5_closed_loop_thermodynamics()
        assert isinstance(result, AIOpsGateResult)
        assert result.status == "PASSED"
        assert result.gate_id == "G5_THERMODYNAMICS_ANTISTUB"
        assert result.details["delta_e_uj"] < 0
        assert result.details["antistubguard_ast_passed"] is True
        assert result.proof_token is not None

    def test_execute_all(self, runner):
        report = runner.execute_all()
        assert isinstance(report, AIOpsHardnessReport)
        assert report.status == "PASSED_100_PERCENT"
        assert report.gates_evaluated == 5
        assert report.gates_passed == 5
        assert report.delta_energy_saved_uj > 0
        assert report.master_proof_receipt.startswith("PROOF_RECEIPT:XAVUNTU_AIOPS_SYSTEM_")
        assert len(report.proof_tokens) == 5

        report_file = Path("dist/aiops_hardness_report.json")
        assert report_file.exists()
        with open(report_file, "r") as f:
            data = json.load(f)
        assert data["status"] == "PASSED_100_PERCENT"
        assert len(data["gate_results"]) == 5
