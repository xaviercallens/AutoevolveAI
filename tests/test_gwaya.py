"""
tests/test_gwaya.py
===================
Unit tests for GWAYA: Qwen + Laya Advisor and Verifier AI Companion.
"""
import pytest
from anse.gwaya.advisor import GwayaAdvisor, VerificationVerdict
from anse.gwaya.verifier import verify_gemini_output, assert_zero_hallucination
from anse.gwaya.datasets import GwayaCurriculumBuilder
from anse.laya.assistant import SpecialistPillar
from pathlib import Path


@pytest.fixture
def gwaya():
    return GwayaAdvisor(mock=True)


def test_gwaya_verifier_blocks_stub_pass(gwaya):
    code = "def compute_trajectory():\n    pass"
    res = gwaya.verify_generation(code)
    assert res.passed is False
    assert res.verdict == VerificationVerdict.BLOCKED_STUB
    assert res.physical_energy == 1e6
    assert len(res.stubs_detected) > 0


def test_gwaya_verifier_blocks_security_eval(gwaya):
    code = "def execute_user_query(q):\n    return eval(q)"
    res = gwaya.verify_generation(code)
    assert res.passed is False
    assert res.verdict == VerificationVerdict.BLOCKED_SECURITY
    assert res.physical_energy == 1e6
    assert len(res.security_flags) > 0


def test_gwaya_verifier_approves_clean_code(gwaya):
    code = "def calculate_kinetic_energy(mass: float, velocity: float) -> float:\n    return 0.5 * mass * (velocity ** 2)"
    res = gwaya.verify_generation(code)
    assert res.passed is True
    assert res.verdict == VerificationVerdict.APPROVED
    assert res.physical_energy < 1e6


def test_gwaya_assert_zero_hallucination():
    clean_code = "def double_value(x: int) -> int:\n    return x * 2"
    # Should not raise
    assert_zero_hallucination(clean_code, mock=True)

    hallucinated_code = "def stubbed_value(x: int) -> int:\n    ..."
    with pytest.raises(AssertionError) as exc_info:
        assert_zero_hallucination(hallucinated_code, mock=True)
    assert "Zero-Hallucination Invariant Violated" in str(exc_info.value)


def test_gwaya_advisor_routing(gwaya):
    lean_advice = gwaya.advise("prove theorem using omega and linarith tactics")
    assert lean_advice.specialist_pillar == SpecialistPillar.LEAN4

    rust_advice = gwaya.advise("implement AVX2 zero-alloc SIMD kernel in rust")
    assert rust_advice.specialist_pillar == SpecialistPillar.RUST

    physics_advice = gwaya.advise("solve relativistic Hamiltonian conservation in symplectic space")
    assert physics_advice.specialist_pillar == SpecialistPillar.PHYSICS


def test_gwaya_curriculum_datasets(tmp_path):
    builder = GwayaCurriculumBuilder(output_dir=tmp_path)
    out_file = builder.build_dataset(samples_per_dataset=5)
    assert out_file.exists()
    assert out_file.stat().st_size > 0
