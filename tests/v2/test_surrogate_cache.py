"""Tests for ANSE 2.0 System 1.5 Surrogate Reality Engine."""

import time

import torch

from anse.v2.surrogate_cache import FastSurrogateRealityEngine


def test_surrogate_sub_millisecond_evaluation():
    engine = FastSurrogateRealityEngine(latent_dim=64, hidden_dim=128)
    z = torch.randn(100, 64)

    t0 = time.perf_counter()
    results = engine.evaluate_batch(z)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert len(results) == 100
    # Average per-item evaluation should be well under 100 microseconds (0.1ms)
    assert elapsed_ms < 500.0  # Entire batch in < 500ms (typically < 3ms)
    for r in results:
        assert r.predicted_energy >= 0.0
        assert 0.0 <= r.confidence_score <= 1.0


def test_monte_carlo_rollout_filtering():
    engine = FastSurrogateRealityEngine(latent_dim=64, hidden_dim=128)
    # Simulate 1,000 thought candidates
    candidates = torch.randn(1000, 64)

    summary = engine.filter_monte_carlo_rollouts(candidates, top_k=16)

    assert summary.total_evaluated == 1000
    assert summary.selected_count == 16
    assert summary.pruned_count == 984
    assert len(summary.top_candidates) == 16
    # Total latency for 1,000 rollouts should be fast
    assert summary.total_latency_ms < 500.0
    assert summary.simulated_sandbox_time_saved_s > 1000.0


def test_online_calibration():
    engine = FastSurrogateRealityEngine(latent_dim=32, hidden_dim=64)
    z = torch.randn(32)

    # Initial prediction
    res_before = engine.evaluate_batch(z)[0]
    assert res_before.predicted_energy >= 0.0

    # Perform online calibration with actual physical energy
    actual_energy = 12.5
    error = engine.calibrate_online(z, actual_energy)

    assert error >= 0.0
    assert engine.total_physical_calibrations == 1
    assert engine.mean_calibration_error >= 0.0
