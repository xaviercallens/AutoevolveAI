"""
Tests for ANSE Ultra-Complex Physics World Models (PWM-21 to PWM-25) & RL Prior Leveraging.
"""

from __future__ import annotations

import fakeredis

from anse.physics.ultra_complex_world_models import (
    ULTRA_PHYSICS_USE_CASES,
    UltraComplexPhysicsBenchmark,
    run_ultra_physics_with_rl_prior_learning_loop,
)


def test_ultra_physics_catalog():
    """Verify that PWM-21 to PWM-25 are properly registered."""
    assert len(ULTRA_PHYSICS_USE_CASES) == 5
    ids = [c["id"] for c in ULTRA_PHYSICS_USE_CASES]
    assert ids == ["PWM-21", "PWM-22", "PWM-23", "PWM-24", "PWM-25"]
    for case in ULTRA_PHYSICS_USE_CASES:
        assert "name" in case
        assert "domain" in case
        assert "invariant" in case
        assert "tol" in case


def test_simulate_all_ultra_cases():
    """Simulate each ultra-complex case and verify physical invariant compliance."""
    bench = UltraComplexPhysicsBenchmark(state_dim=64, steps_per_sim=15)
    for case in ULTRA_PHYSICS_USE_CASES:
        res = bench.simulate_case(case)
        assert res.case_id == case["id"]
        assert res.passed_invariants is True
        assert res.reward_delta > 0.0
        assert res.grpo_advantage > 0.0
        assert res.physical_energy < 1000.0


def test_ultra_physics_rl_prior_transfer():
    """Verify that leveraging prior RL policy accelerates convergence on ultra-complex cases."""
    fake_r = fakeredis.FakeRedis(decode_responses=False)
    summary = run_ultra_physics_with_rl_prior_learning_loop(epochs=3, state_dim=64, redis_client=fake_r)

    assert summary["status"] == "COMPLETED"
    assert summary["total_cases"] == 5
    assert summary["passed_invariants"] == 5
    assert summary["rl_transfer_advantage"] >= 0.0  # Warm-started model has lower or equal initial loss
    assert summary["loss_reduction"] >= 0.0
    assert summary["mean_dpo_reward_delta"] > 0.0
    assert summary["mean_grpo_advantage"] > 0.0
    assert summary["redis_persisted"] is True

    # Check Redis keys
    assert fake_r.scard("antigravity:physics:ultra_cases") == 5
    assert fake_r.exists("antigravity:conversation:ultra_physics_rl_session:turns") == 1
