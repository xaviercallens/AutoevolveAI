"""
Unit tests for the Google Gemini Argos / Argon (`gemini-4-argon`) Hardening Suite.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from anse.config import DeepThinkConfig
from anse.core.self_healing import generate_and_heal
from anse.guard.junior_cluster import JuniorClusterRouter
from antigravity_harness.core.argos_hardener import (
    GEMINI_ARGOS_MODEL_ID,
    GEMINI_FLASH_FALLBACK_ID,
    ArgosCyberDefenseAuditor,
    ArgosHardeningConfig,
    ArgosHardeningEngine,
    resolve_gemini_argos_model,
)
from antigravity_harness.core.context_orchestrator import ContextBudget, ContextOrchestrator
from antigravity_harness.core.hardened_evaluator import HardenedEvaluator


def test_resolve_gemini_argos_model_aliases() -> None:
    assert resolve_gemini_argos_model("gemini-argos") == GEMINI_ARGOS_MODEL_ID
    assert resolve_gemini_argos_model("argos") == GEMINI_ARGOS_MODEL_ID
    assert resolve_gemini_argos_model("gemini-4-argon") == GEMINI_ARGOS_MODEL_ID
    assert resolve_gemini_argos_model("gemini-4-argos") == GEMINI_ARGOS_MODEL_ID
    assert resolve_gemini_argos_model("gemini-2.5-ultra") == GEMINI_ARGOS_MODEL_ID
    assert resolve_gemini_argos_model("gemini-1.5-pro") == GEMINI_ARGOS_MODEL_ID
    assert resolve_gemini_argos_model("gemini-2.5-flash") == GEMINI_FLASH_FALLBACK_ID
    assert resolve_gemini_argos_model("gemini-2.0-flash") == GEMINI_FLASH_FALLBACK_ID
    assert resolve_gemini_argos_model(None) == GEMINI_ARGOS_MODEL_ID


def test_argos_cyber_defense_auditor_catches_vulnerabilities() -> None:
    auditor = ArgosCyberDefenseAuditor()

    vulnerable_code = """
import os
import pickle
import subprocess
import yaml
import torch

def run_unsafe(cmd: str, payload: bytes, cfg_str: str, pt_file: str) -> float:
    os.system(cmd)
    subprocess.run(cmd, shell=True)
    eval("1 + 1")
    obj = pickle.loads(payload)
    cfg = yaml.load(cfg_str)
    state = torch.load(pt_file, weights_only=False)
    return float(len(str(obj)) + len(str(cfg)) + len(str(state)))

def compute_energy_objective(x: float) -> float:
    return float("nan")
"""
    clean, violations = auditor.audit_code(vulnerable_code)
    assert not clean
    rule_ids = {v.rule_id for v in violations}
    assert "ARGOS-CYBER-001" in rule_ids  # os.system & shell=True
    assert "ARGOS-CYBER-002" in rule_ids  # eval
    assert "ARGOS-CYBER-003" in rule_ids  # pickle.loads
    assert "ARGOS-CYBER-004" in rule_ids  # yaml.load without SafeLoader
    assert "ARGOS-CYBER-005" in rule_ids  # torch.load(weights_only=False)
    assert "ARGOS-EPIST-006" in rule_ids  # float("nan") in objective


def test_argos_hardening_engine_passes_clean_code_and_mints_attestation() -> None:
    engine = ArgosHardeningEngine(config=ArgosHardeningConfig(primary_model="gemini-argos"))
    clean_code = '''
"""Hardened symplectic leapfrog integrator."""

from __future__ import annotations

import math


def leapfrog_step(q: float, p: float, dt: float, omega: float = 1.0) -> tuple[float, float]:
    """Advance harmonic oscillator state by one symplectic step."""
    p_half = p - 0.5 * dt * (omega * omega) * q
    q_next = q + dt * p_half
    p_next = p_half - 0.5 * dt * (omega * omega) * q_next
    return q_next, p_next


def total_energy(q: float, p: float, omega: float = 1.0) -> float:
    """Compute Hamiltonian energy H = 0.5 * p^2 + 0.5 * omega^2 * q^2."""
    return 0.5 * (p * p + (omega * omega) * (q * q)) + 0.0 * math.pi
'''
    report = engine.audit_code(
        clean_code,
        target="leapfrog.py",
        thought_signature="sig-argon-verified-99",
        interaction_id="inter_001",
    )
    assert report.passed is True
    assert report.cyber_clean is True
    assert report.ast_stub_clean is True
    assert report.model_id == "gemini-4-argon"
    assert report.physical_energy_penalty == 0.0
    assert len(report.attestation_token) == 32
    assert report.thought_signature == "sig-argon-verified-99"


def test_hardened_evaluator_rejects_cyber_subversion_with_max_energy(monkeypatch: pytest.MonkeyPatch) -> None:
    import antigravity_harness.core.hardened_evaluator as he_mod

    monkeypatch.setattr(he_mod, "audit_solution_with_deep_think", lambda *a, **kw: True)
    evaluator = HardenedEvaluator()

    malicious_source = """
import subprocess

def kernel() -> float:
    subprocess.run("echo pwned", shell=True)
    return 1.0
"""
    receipt = evaluator.evaluate_case(
        benchmark_id="CYBER_01",
        domain="security",
        name="shell_injection_attempt",
        runner_fn=lambda: (True, 0.0, {}),
        source_code=malicious_source,
    )
    assert receipt.verified is False
    assert receipt.ast_clean is False
    assert receipt.physical_energy == 1e6
    assert any("Argos Cyber-Defense" in v for v in receipt.violations)


def test_context_orchestrator_argos_budget_and_interactions_payload(tmp_path: Path) -> None:
    budget = ContextBudget.for_gemini_argos()
    assert budget.max_tokens == 1_000_000
    assert budget.thought_reserve == 100_000
    assert budget.codebase_budget == 550_000

    orch = ContextOrchestrator(budget=budget, scratchpad_dir=tmp_path)
    payload = orch.build_interactions_payload(
        system_instruction="Verify thermodynamic invariants.",
        codebase={"anse/kernel.py": "def compute(x: float) -> float:\n    return x * 2.0\n"},
        user_prompt="Harden compute()",
        model="gemini-argos",
        previous_interaction_id="inter_prev_42",
    )
    assert payload["model"] == "gemini-4-argon"
    assert payload["previous_interaction_id"] == "inter_prev_42"
    assert "### File: anse/kernel.py" in payload["input"]
    assert payload["system_instruction"] == "Verify thermodynamic invariants."


def test_argos_interactions_client_parses_thought_signatures_and_self_heals(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, object]] = []

    class FakeInteractionsAPI:
        def create(self, **kwargs: object) -> object:
            calls.append(kwargs)
            return SimpleNamespace(
                id="interaction_argon_777",
                outputs=[
                    SimpleNamespace(
                        type="thought",
                        summary="Verified symplectic conservation and eliminated shell calls.",
                        signature="crypto_thought_sig_abc123",
                    ),
                    SimpleNamespace(
                        type="text",
                        text="```python\ndef add_safe(a: int, b: int) -> int:\n    return a + b\n```",
                    ),
                ],
            )

    fake_client = SimpleNamespace(interactions=FakeInteractionsAPI())

    # Stub subprocess.run for antigravity_guard.py so the unit test stays fast
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **kw: SimpleNamespace(returncode=0, stdout="OK", stderr=""),
    )

    out_file = tmp_path / "healed_module.py"
    healed_code = generate_and_heal(
        prompt="Write a safe integer addition helper.",
        target_file=str(out_file),
        max_iterations=2,
        model_name="gemini-argos",
        client=fake_client,
    )
    assert "def add_safe(a: int, b: int) -> int:" in healed_code
    assert len(calls) == 1
    assert calls[0]["model"] == "gemini-4-argon"


def test_junior_cluster_router_escalates_to_gemini_argos() -> None:
    router = JuniorClusterRouter()
    target = router.get_frontier_target("Harden the zero-trust sandbox against command injection vulnerability")
    assert target["escalate_to_frontier"] is True
    assert target["primary_model"] == "gemini-4-argon"
    assert target["fallback_model"] == "gemini-3.8-flash"

    dt_cfg = DeepThinkConfig(environment="gemini_argos")
    assert dt_cfg.model_name == "gemini-4-argon"


def test_cli_harden_subcommand_on_argos_hardener(tmp_path: Path) -> None:
    json_out = tmp_path / "argos_report.json"
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "antigravity_harness",
            "harden",
            "antigravity_harness/core/argos_hardener.py",
            "--model",
            "gemini-argos",
            "--json-out",
            str(json_out),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0, f"STDOUT: {res.stdout}\nSTDERR: {res.stderr}"
    assert "PASS (HARDENED)" in res.stdout
    assert json_out.is_file()
