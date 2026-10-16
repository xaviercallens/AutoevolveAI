"""
Unit tests for KALSpeak Workflow (workflowKALSpeak.py).
Validates the Local Autonomous Voice AI & GWAYA Dual-Process Hardness Harness.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from workflowKALSpeak import (
    GateResult,
    KALSpeakHardnessRunner,
    PhysicalMetrics,
)


class TestPhysicalMetrics:
    def test_energy_calculation_nominal(self):
        engine = PhysicalMetrics(w_time=1.0, w_mem=2.0)
        energy = engine.calculate_energy(duration_ms=10.0, peak_rss_mb=20.0, failed=False)
        assert energy == 50.0

    def test_energy_calculation_failure_penalty(self):
        engine = PhysicalMetrics(penalty=1_000_000.0)
        energy = engine.calculate_energy(duration_ms=5.0, peak_rss_mb=10.0, failed=True)
        assert energy == 1_000_000.0

    def test_mint_proof_token(self):
        engine = PhysicalMetrics()
        token = engine.mint_proof_token("TEST_PAYLOAD")
        assert token.startswith("PROOF_TOKEN:")
        assert len(token) == len("PROOF_TOKEN:") + 16


class TestKALSpeakGates:
    @pytest.fixture
    def runner(self):
        return KALSpeakHardnessRunner()

    def test_gate1_wake_word(self, runner):
        result = runner.run_gate1_wake_word()
        assert isinstance(result, GateResult)
        assert result.status == "PASSED"
        assert result.gate_id == "G1_WAKE_WORD"
        assert result.details["accuracy"] == 1.0
        assert result.details["avg_detection_latency_ms"] < 20.0
        assert result.details["cloud_streaming_bytes"] == 0
        assert result.proof_token is not None

    def test_gate2_transcription(self, runner):
        result = runner.run_gate2_transcription()
        assert isinstance(result, GateResult)
        assert result.status == "PASSED"
        assert result.gate_id == "G2_FASTER_WHISPER"
        assert result.details["quantization"] == "INT8"
        assert result.details["avg_transcription_ms"] < 120.0
        assert result.details["memory_isolation"] == "VOLATILE_RAM_LOCKED"
        assert result.proof_token is not None

    def test_gate3_laya_lora_system1(self, runner):
        result = runner.run_gate3_laya_lora_system1()
        assert isinstance(result, GateResult)
        assert result.status == "PASSED"
        assert result.gate_id == "G3_LAYA_LORA_SYSTEM1"
        assert result.details["noulhead_security_recall"] == 1.0
        assert result.details["fast_path_count"] == 2
        assert result.details["system2_escalations"] == 1
        assert result.proof_token is not None

    def test_gate4_gwaya_qwen_system2(self, runner):
        result = runner.run_gate4_gwaya_qwen_system2()
        assert isinstance(result, GateResult)
        assert result.status == "PASSED"
        assert result.gate_id == "G4_GWAYA_QWEN_SYSTEM2"
        assert result.details["model_engine"] == "gwaya-qwen:3.8"
        assert result.details["scale_to_zero_idle_vram_gb"] == 0.0
        assert result.details["tree_of_thoughts_score"] >= 0.95
        assert result.proof_token is not None

    def test_gate5_safeguards(self, runner):
        result = runner.run_gate5_safeguards()
        assert isinstance(result, GateResult)
        assert result.status == "PASSED"
        assert result.gate_id == "G5_SAFEGUARDS_ANTISTUB_FASTMCP"
        assert result.details["ast_audit_enforced"] is True
        assert result.details["zero_stub_policy"] == "STRICT_REJECT_ON_TODO_PASS"
        assert result.proof_token is not None

    def test_gate6_speech_action(self, runner):
        result = runner.run_gate6_speech_action()
        assert isinstance(result, GateResult)
        assert result.status == "PASSED"
        assert result.gate_id == "G6_VOICE_ACTION_PIPER_TTS"
        assert result.details["tts_latency_ms"] < 60.0
        assert result.details["accuracy_contract_pct"] >= 95.0
        assert result.details["energy_reduction_contract_pct"] >= 50.0
        assert result.proof_token is not None

    def test_execute_all(self, runner, tmp_path):
        report = runner.execute_all()
        assert report.status == "PASSED_100_PERCENT"
        assert report.gates_evaluated == 6
        assert report.gates_passed == 6
        assert report.accuracy_pct == 96.0
        assert report.energy_reduction_pct == 53.2
        assert report.master_proof_receipt.startswith("PROOF_RECEIPT:KALSPEAK_GWAYA_DUAL_PROCESS_")
        assert len(report.proof_tokens) == 6

        report_file = Path("dist/kalspeak_hardness_report.json")
        assert report_file.exists()
        with open(report_file, "r") as f:
            data = json.load(f)
        assert data["status"] == "PASSED_100_PERCENT"
        assert len(data["gate_results"]) == 6
