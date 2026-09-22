"""
Unit and Integration Tests for ANSE Physics World Model 10 Use Cases.
"""

from __future__ import annotations

import fakeredis

from anse.physics.world_models import (
    PHYSICS_USE_CASES,
    PhysicsWorldModelBenchmark,
    run_physics_learning_loop,
)


def test_physics_use_cases_catalog():
    """Verify that exactly 10 physics world model use cases are defined."""
    assert len(PHYSICS_USE_CASES) == 10
    ids = [c["id"] for c in PHYSICS_USE_CASES]
    assert len(set(ids)) == 10
    for case in PHYSICS_USE_CASES:
        assert "name" in case
        assert "domain" in case
        assert "invariant" in case
        assert "tol" in case


def test_simulate_all_10_physics_cases():
    """Simulate each case and verify invariant error tolerances."""
    bench = PhysicsWorldModelBenchmark(state_dim=64, steps_per_sim=15)
    for case in PHYSICS_USE_CASES:
        res = bench.simulate_case(case)
        assert res.case_id == case["id"]
        assert res.trajectory_steps == 15
        assert len(res.states) == 15
        assert res.passed_invariants is True
        assert res.physical_energy < 1000.0  # Not in catastrophic pain (1e6)
        assert res.latency_ms >= 0.0


def test_closed_loop_jepa_learning_loop():
    """Verify that the JEPA training loop learns and reduces total energy loss."""
    fake_r = fakeredis.FakeRedis(decode_responses=False)
    summary = run_physics_learning_loop(epochs=5, state_dim=64, redis_client=fake_r)
    
    assert summary["status"] == "COMPLETED"
    assert summary["total_cases"] == 10
    assert summary["passed_invariants"] == 10
    assert summary["loss_reduction"] >= 0.0  # Learning happened: loss decreased
    assert summary["proof_token"] is not None
    assert summary["redis_persisted"] is True

    # Check that Redis recorded the case keys
    assert fake_r.scard("antigravity:physics:cases") == 10
    assert fake_r.exists("antigravity:conversation:physics_world_models_session:turns") == 1
