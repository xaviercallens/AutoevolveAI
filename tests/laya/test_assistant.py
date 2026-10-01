"""
tests/laya/test_assistant.py
============================
Unit and integration tests for LayaDualProcessAssistant:
- Anti-stub AST validation (pass, ..., NotImplementedError)
- Security vulnerability screening (eval, os.system)
- Specialist pillar routing (Python, Rust, Lean 4, Physics)
- Dual-process escalation and anti-hallucination post-filtering
"""
import pytest
from anse.laya.assistant import (
    CodeAuditReport,
    DualProcessResponse,
    LayaDualProcessAssistant,
    SpecialistPillar,
)


@pytest.fixture
def assistant():
    # Uses mock dispatcher for fast unit tests without full model load
    return LayaDualProcessAssistant(checkpoint_path=None, noul_threshold=0.30, mock=True)



def test_audit_detects_pass_stub(assistant):
    code = """
def calculate_trajectory(v0, angle):
    pass
"""
    audit = assistant.audit_code_safety_and_stubs(code)
    assert audit.blocked is True
    assert audit.energy == 1e6
    assert any("empty 'pass' stub" in s for s in audit.detected_stubs)


def test_audit_detects_ellipsis_stub(assistant):
    code = """
def solve_kepler_equation(M, e):
    ...
"""
    audit = assistant.audit_code_safety_and_stubs(code)
    assert audit.blocked is True
    assert audit.energy == 1e6
    assert any("ellipsis stub" in s for s in audit.detected_stubs)


def test_audit_detects_security_risk(assistant):
    code = """
def run_command(cmd):
    return eval(cmd)
"""
    audit = assistant.audit_code_safety_and_stubs(code)
    assert audit.blocked is True
    assert audit.energy == 1e6
    assert any("eval()" in s for s in audit.security_flags)


def test_route_specialist_pillars(assistant):
    assert assistant.route_specialist_pillar("prove theorem with omega and linarith") == SpecialistPillar.LEAN4
    assert assistant.route_specialist_pillar("implement AVX-512 SIMD vectorization zero-alloc kernel in rust") == SpecialistPillar.RUST
    assert assistant.route_specialist_pillar("solve relativistic symplectic Hamiltonian conservation") == SpecialistPillar.PHYSICS
    assert assistant.route_specialist_pillar("write pytest unit tests for fastapi endpoint") == SpecialistPillar.PYTHON


def test_dual_process_fast_reflex(assistant):
    prompt = "audit code smell in this snippet"
    resp = assistant.assist(prompt=prompt, code_context="x = 1\ny = 2")
    assert resp.resolved_by == "System 1 (Laya Reflex)"
    assert resp.escalated_to_system2 is False
    assert resp.energy_wh < 0.001


def test_dual_process_catches_system2_hallucination(assistant):
    # Simulate a System 2 LLM that hallucinated a stub
    def hallucinating_llm(prompt: str, role: str) -> str:
        return "def generated_function():\n    pass  # TODO: implement later"

    assistant.system2_caller = hallucinating_llm
    resp = assistant.assist(prompt="Implement matrix multiply", force_system2=True)

    assert resp.resolved_by == "Blocked (Quality Gate)"
    assert resp.escalated_to_system2 is True
    assert "FILTERED BY LAYA QUALITY GATE" in resp.content
    assert resp.audit.blocked is True
