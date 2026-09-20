"""
Tests for anse.jepa.ema — EMA update and cosine schedule.

Lean 4 refs:
    ema_step            — θ̄ ← τ · θ̄ + (1 − τ) · θ
    ema_converges_step  — proved by rfl
    TargetEncoder.hmom  — 0 < τ ∧ τ ≤ 1
"""

import pytest
import torch
import torch.nn as nn

from anse.jepa.ema import cosine_ema_schedule, ema_update


def _make_pair() -> tuple[nn.Module, nn.Module]:
    """Create a source and target network pair for testing."""
    source = nn.Sequential(nn.Linear(10, 5))
    target = nn.Sequential(nn.Linear(10, 5))
    # Initialise differently so we can detect updates
    with torch.no_grad():
        for p in source.parameters():
            p.fill_(1.0)
        for p in target.parameters():
            p.fill_(0.0)
    return source, target


class TestEMAUpdate:
    """Tests for ema_update function."""

    def test_ema_update_moves_target_toward_context(self):
        """After one EMA update, target weights should be closer to source.

        Lean 4 ref: ema_step — θ̄ ← τ · θ̄ + (1 − τ) · θ
        """
        source, target = _make_pair()
        # target = 0.0, source = 1.0
        # After EMA with τ=0.9: target = 0.9 * 0.0 + 0.1 * 1.0 = 0.1
        ema_update(target, source, tau=0.9)

        for p in target.parameters():
            assert torch.allclose(p.data, torch.full_like(p.data, 0.1), atol=1e-6), (
                f"Expected 0.1, got {p.data.mean().item()}"
            )

    def test_ema_momentum_1_freezes_target(self):
        """τ=1.0 means target stays unchanged (frozen).

        Lean 4 ref: hmom boundary — τ = 1 → θ̄ = 1·θ̄ + 0·θ = θ̄
        """
        source, target = _make_pair()
        old_params = [p.data.clone() for p in target.parameters()]

        ema_update(target, source, tau=1.0)

        for p, old in zip(target.parameters(), old_params):
            assert torch.allclose(p.data, old), "τ=1.0 should freeze target encoder"

    def test_ema_momentum_near_zero_copies_context(self):
        """Very small τ (close to 0, but > 0) almost copies source to target.

        Lean 4 ref: hmom — as τ → 0+, target → source
        """
        source, target = _make_pair()

        ema_update(target, source, tau=0.001)

        for p_tgt, p_src in zip(target.parameters(), source.parameters()):
            assert torch.allclose(p_tgt.data, p_src.data, atol=1e-2), (
                "Very small τ should make target ≈ source"
            )

    def test_ema_precondition_assertion(self):
        """τ outside (0, 1] must raise ValueError.

        Lean 4 ref: hmom : 0 < momentum ∧ momentum ≤ 1
        """
        source, target = _make_pair()

        with pytest.raises(ValueError, match="0 < τ ≤ 1"):
            ema_update(target, source, tau=0.0)

        with pytest.raises(ValueError, match="0 < τ ≤ 1"):
            ema_update(target, source, tau=-0.5)

        with pytest.raises(ValueError, match="0 < τ ≤ 1"):
            ema_update(target, source, tau=1.5)


class TestCosineEMASchedule:
    """Tests for cosine_ema_schedule function."""

    def test_ema_cosine_schedule_boundaries(self):
        """Schedule should produce tau_start at step 0 and tau_end at the last step.

        Reference: eb_jepa cosine schedule
        """
        tau_start, tau_end = 0.996, 1.0

        tau_0 = cosine_ema_schedule(0, 100, tau_start, tau_end)
        tau_end_val = cosine_ema_schedule(100, 100, tau_start, tau_end)

        assert abs(tau_0 - tau_start) < 1e-6, f"Expected {tau_start}, got {tau_0}"
        assert abs(tau_end_val - tau_end) < 1e-6, f"Expected {tau_end}, got {tau_end_val}"

    def test_ema_cosine_schedule_monotonic(self):
        """τ should monotonically increase from tau_start to tau_end."""
        values = [cosine_ema_schedule(i, 100, 0.996, 1.0) for i in range(101)]
        for i in range(len(values) - 1):
            assert values[i] <= values[i + 1] + 1e-10, (
                f"τ must be monotonic: τ[{i}]={values[i]} > τ[{i + 1}]={values[i + 1]}"
            )

    def test_ema_cosine_schedule_invalid_inputs(self):
        """Invalid inputs should raise ValueError."""
        with pytest.raises(ValueError):
            cosine_ema_schedule(0, 0)  # total_steps = 0

        with pytest.raises(ValueError):
            cosine_ema_schedule(-1, 100)  # negative step
