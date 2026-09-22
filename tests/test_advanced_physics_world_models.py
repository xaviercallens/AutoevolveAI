"""
Tests for ANSE Advanced Frontier Physics World Models (PWM-11 to PWM-20).
"""

from __future__ import annotations

import fakeredis

from anse.physics.advanced_world_models import (
    ADVANCED_PHYSICS_USE_CASES,
    AdvancedPhysicsBenchmark,
    run_advanced_physics_learning_loop,
)


def test_advanced_physics_catalog():
    """Verify that all 10 advanced cases PWM-11 to PWM-20 are defined."""
    assert len(ADVANCED_PHYSICS_USE_CASES) == 10
    ids = [c["id"] for c in ADVANCED_PHYSICS_USE_CASES]
    assert ids == [f"PWM-{i}" for i in range(11, 21)]
    for case in ADVANCED_PHYSICS_USE_CASES:
        assert "name" in case
        assert "domain" in case
        assert "invariant" in case
        assert "tol" in case


def test_simulate_all_advanced_cases():
    """Simulate each advanced case and verify physical invariant compliance."""
    bench = AdvancedPhysicsBenchmark(state_dim=64, steps_per_sim=15)
    for case in ADVANCED_PHYSICS_USE_CASES:
        res = bench.simulate_case(case)
        assert res.case_id == case["id"]
        assert res.passed_invariants is True
        assert res.reward_delta > 0.0
        assert res.grpo_advantage > 0.0
        assert res.physical_energy < 1000.0


def test_advanced_physics_learning_loop():
    """Verify continuous JEPA training loop and Redis LTM persistence on advanced physics."""
    fake_r = fakeredis.FakeRedis(decode_responses=False)
    summary = run_advanced_physics_learning_loop(epochs=3, state_dim=64, redis_client=fake_r)

    assert summary["status"] == "COMPLETED"
    assert summary["total_cases"] == 10
    assert summary["passed_invariants"] == 10
    assert summary["loss_reduction"] >= 0.0
    assert summary["mean_dpo_reward_delta"] > 0.0
    assert summary["mean_grpo_advantage"] > 0.0
    assert summary["redis_persisted"] is True

    # Check Redis keys
    assert fake_r.scard("antigravity:physics:advanced_cases") == 10
    assert fake_r.exists("antigravity:conversation:advanced_physics_session:turns") == 1
