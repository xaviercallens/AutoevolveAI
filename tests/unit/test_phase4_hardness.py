import pytest
import os
import json
from anse.core.low_tier_hardness import LowTierHardnessPolicy, HardnessMetrics

@pytest.fixture
def policy(tmp_path):
    dpo_file = tmp_path / "test_dpo.jsonl"
    return LowTierHardnessPolicy(dpo_export_path=str(dpo_file))

def test_d1_prompt_budget(policy):
    long_stderr = "A" * 100 + "ERROR: out of bounds" + "B" * 100
    compressed = policy.apply_d1_prompt_budget(long_stderr, max_length=50)
    assert len(compressed) <= 50
    assert "..." in compressed

def test_d2_capacity_gating(policy):
    # Laya (149M + 577k) should NOT allow retry branches if adaptive_retry is gated by size
    laya_params = 149_000_000 + 577_000
    assert policy.apply_d2_capacity_gating(laya_params) is False
    # 7B model should allow
    assert policy.apply_d2_capacity_gating(7_000_000_000) is True

def test_d3_energy_monotonicity(policy):
    assert policy.apply_d3_energy_monotonic_abort(70.0, 50.0) is True # E1 > 60
    assert policy.apply_d3_energy_monotonic_abort(10.0, 15.0) is True # E2 > E1
    assert policy.apply_d3_energy_monotonic_abort(40.0, 20.0) is False # Monotonic and E1 <= 60

def test_d4_skeleton_lessons(policy):
    code = '''
def calculate_energy(mass: float, velocity: float) -> float:
    """Calculates kinetic energy."""
    return 0.5 * mass * velocity**2
'''
    skeleton = policy.apply_d4_skeleton_lessons(code)
    assert "def calculate_energy(...):" in skeleton
    assert "Calculates kinetic energy." in skeleton
    assert "0.5 *" not in skeleton

def test_d5_triage(policy):
    assert policy.apply_d5_triage(0.5) == "trivial"
    assert policy.apply_d5_triage(8.0) == "fixable"
    assert policy.apply_d5_triage(50.0) == "hard"

def test_d6_live_dpo_export(policy):
    exported = policy.apply_d6_live_dpo_export(
        prompt="Fix the tensor shape.",
        chosen="Good code",
        rejected="Bad code",
        e_chosen=5.0,
        e_rejected=25.0
    )
    assert exported is True
    with open(policy.dpo_export_path, "r") as f:
        lines = f.readlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["delta_e"] == 20.0

def test_d7_tier_gates(policy):
    good_metrics = HardnessMetrics(pass_at_1=0.35, false_convergence=0.40, rescue_efficiency=0.15, energy_monotonicity=0.45)
    bad_metrics = HardnessMetrics(pass_at_1=0.20, false_convergence=0.60, rescue_efficiency=0.05, energy_monotonicity=0.20)
    
    assert policy.evaluate_d7_gates(good_metrics) is True
    assert policy.evaluate_d7_gates(bad_metrics) is False

def test_d8_component_registry(policy):
    policy.registry.register_strategy("fix_prompt", "v1.0", "Fix this code: {code}")
    policy.registry.register_strategy("fix_prompt", "v1.1", "Carefully fix this code: {code}")
    
    # Should auto-activate v1.0
    assert policy.registry.get_active_strategy("fix_prompt") == "Fix this code: {code}"
    
    policy.registry.rollback("fix_prompt", "v1.1")
    assert policy.registry.get_active_strategy("fix_prompt") == "Carefully fix this code: {code}"
