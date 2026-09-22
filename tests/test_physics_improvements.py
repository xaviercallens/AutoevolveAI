"""
Tests for ANSE Improved Physics World Models & RL Gains.
"""

from __future__ import annotations

import fakeredis

from anse.physics.improved_world_models import (
    ImprovedPhysicsBenchmark,
    evaluate_improvements_and_rl_gain,
)
from anse.physics.world_models import PHYSICS_USE_CASES


def test_improved_physics_benchmark_precision():
    """Verify that improved integrators improve physical invariant precision."""
    bench = ImprovedPhysicsBenchmark(state_dim=64, steps_per_sim=15)
    for case in PHYSICS_USE_CASES:
        res = bench.simulate_improved_case(case)
        assert res.case_id == case["id"]
        assert res.improved_invariant_error <= res.baseline_invariant_error + 1e-12
        assert res.precision_gain_factor >= 1.0
        assert res.reward_delta > 0.0  # Chosen is preferred over baseline


def test_evaluate_improvements_and_rl_gain():
    """Verify RL gain metrics and JEPA training on improved physical trajectories."""
    fake_r = fakeredis.FakeRedis(decode_responses=False)
    summary = evaluate_improvements_and_rl_gain(epochs=3, state_dim=64, redis_client=fake_r)

    assert summary["status"] == "COMPLETED"
    assert summary["total_cases"] == 10
    assert summary["mean_dpo_reward_delta"] > 0.0
    assert summary["mean_grpo_advantage"] > 0.0
    assert summary["mean_precision_gain_factor"] >= 1.0
    assert summary["jepa_loss_reduction"] >= 0.0
    assert summary["redis_persisted"] is True

    # Verify Redis keys
    assert fake_r.exists("antigravity:conversation:physics_improved_rl_session:turns") == 1
    assert fake_r.exists("antigravity:physics:improved:PWM-01") == 1
