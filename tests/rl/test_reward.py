"""Unit tests for DifferentialRewardCalculator (anse/rl/reward.py).

Run 5: First test coverage for the reward module (zero coverage prior to this commit).
"""
from __future__ import annotations

import pytest

from anse.rl.reward import DifferentialRewardCalculator, RewardComponents


class TestDifferentialRewardCalculator:
    """Tests for DifferentialRewardCalculator across phases 1–4."""

    # ------------------------------------------------------------------
    # Failure path
    # ------------------------------------------------------------------

    def test_failed_or_panicked_returns_catastrophic_penalty(self) -> None:
        """failed_or_panicked=True must always return total_reward = -1100."""
        for phase in (1, 2, 3, 4):
            calc = DifferentialRewardCalculator(phase=phase)
            r = calc.compute_reward(
                functional_parity=1.0,
                ops_ratio=100.0,
                energy_anse=0.0,
                failed_or_panicked=True,
            )
            assert r.total_reward == pytest.approx(-1100.0), f"Phase {phase} failure penalty wrong"
            assert not r.passed_iso_80
            assert not r.passed_perf_gain_10

    # ------------------------------------------------------------------
    # Gate checks
    # ------------------------------------------------------------------

    def test_iso_80_gate_true(self) -> None:
        calc = DifferentialRewardCalculator(phase=1)
        r = calc.compute_reward(functional_parity=0.80, ops_ratio=1.0, energy_anse=0.0)
        assert r.passed_iso_80

    def test_iso_80_gate_false(self) -> None:
        calc = DifferentialRewardCalculator(phase=1)
        r = calc.compute_reward(functional_parity=0.79, ops_ratio=1.0, energy_anse=0.0)
        assert not r.passed_iso_80

    def test_iso_90_gate(self) -> None:
        calc = DifferentialRewardCalculator(phase=2)
        r_pass = calc.compute_reward(functional_parity=0.90, ops_ratio=1.0, energy_anse=0.0)
        r_fail = calc.compute_reward(functional_parity=0.89, ops_ratio=1.0, energy_anse=0.0)
        assert r_pass.passed_iso_90
        assert not r_fail.passed_iso_90

    def test_iso_100_gate(self) -> None:
        calc = DifferentialRewardCalculator(phase=3)
        r_pass = calc.compute_reward(functional_parity=1.0, ops_ratio=1.0, energy_anse=0.0)
        r_fail = calc.compute_reward(functional_parity=0.999, ops_ratio=1.0, energy_anse=0.0)
        assert r_pass.passed_iso_100
        assert not r_fail.passed_iso_100

    def test_degradation_50_gate_via_ops_ratio(self) -> None:
        """ops_ratio >= 0.67 means RunuX is within 50% degradation — gate passes."""
        calc = DifferentialRewardCalculator(phase=2)
        r = calc.compute_reward(functional_parity=1.0, ops_ratio=0.67, energy_anse=0.0)
        assert r.passed_degradation_50

    def test_degradation_50_gate_fails_below_floor(self) -> None:
        """ops_ratio < 0.67 and no degradation_pct kwarg — gate fails (F-10 fix)."""
        calc = DifferentialRewardCalculator(phase=2)
        r = calc.compute_reward(functional_parity=1.0, ops_ratio=0.10, energy_anse=0.0)
        assert not r.passed_degradation_50

    def test_degradation_50_gate_via_direct_pct_kwarg(self) -> None:
        """Direct degradation_pct kwarg overrides ops_ratio proxy (F-10 alignment)."""
        calc = DifferentialRewardCalculator(phase=2)
        # ops_ratio < 0.67 but actual degradation is ≤ 50% → gate passes
        r = calc.compute_reward(
            functional_parity=1.0, ops_ratio=0.10, energy_anse=0.0, degradation_pct=30.0
        )
        assert r.passed_degradation_50

    def test_perf_gain_10_gate(self) -> None:
        calc = DifferentialRewardCalculator(phase=2)
        r_pass = calc.compute_reward(functional_parity=1.0, ops_ratio=1.0, energy_anse=0.0, perf_gain_pct=10.0)
        r_fail = calc.compute_reward(functional_parity=1.0, ops_ratio=1.0, energy_anse=0.0, perf_gain_pct=9.9)
        assert r_pass.passed_perf_gain_10
        assert not r_fail.passed_perf_gain_10

    def test_perf_gain_30_gate(self) -> None:
        calc = DifferentialRewardCalculator(phase=4)
        r_pass = calc.compute_reward(functional_parity=1.0, ops_ratio=1.0, energy_anse=0.0, perf_gain_pct=30.0)
        r_fail = calc.compute_reward(functional_parity=1.0, ops_ratio=1.0, energy_anse=0.0, perf_gain_pct=29.9)
        assert r_pass.passed_perf_gain_30
        assert not r_fail.passed_perf_gain_30

    def test_ai_speedup_50_gate(self) -> None:
        calc = DifferentialRewardCalculator(phase=4)
        r_pass = calc.compute_reward(functional_parity=1.0, ops_ratio=1.0, energy_anse=0.0, ai_speedup_pct=50.0)
        r_fail = calc.compute_reward(functional_parity=1.0, ops_ratio=1.0, energy_anse=0.0, ai_speedup_pct=49.9)
        assert r_pass.passed_ai_speedup_50
        assert not r_fail.passed_ai_speedup_50

    # ------------------------------------------------------------------
    # Reward structure
    # ------------------------------------------------------------------

    def test_phase1_milestone_bonus_triggers_on_iso80_and_deg50(self) -> None:
        calc = DifferentialRewardCalculator(phase=1)
        r = calc.compute_reward(functional_parity=0.80, ops_ratio=0.67, energy_anse=0.0)
        assert r.milestone_bonus > 0.0

    def test_phase4_milestone_bonus_requires_all_four_gates(self) -> None:
        calc = DifferentialRewardCalculator(phase=4)
        # All four gates met
        r_full = calc.compute_reward(
            functional_parity=1.0, ops_ratio=2.0, energy_anse=0.0,
            perf_gain_pct=30.0, ai_speedup_pct=50.0
        )
        assert r_full.milestone_bonus > 0.0
        # Missing ai_speedup_50
        r_partial = calc.compute_reward(
            functional_parity=1.0, ops_ratio=2.0, energy_anse=0.0,
            perf_gain_pct=30.0, ai_speedup_pct=40.0
        )
        assert r_partial.milestone_bonus == pytest.approx(0.0)

    def test_total_reward_components_sum(self) -> None:
        """total_reward must equal the sum of its three components + bonus."""
        calc = DifferentialRewardCalculator(phase=3)
        r = calc.compute_reward(functional_parity=1.0, ops_ratio=5.0, energy_anse=100.0, perf_gain_pct=25.0)
        expected = r.functional_reward + r.performance_reward - r.energy_penalty + r.milestone_bonus
        assert r.total_reward == pytest.approx(expected, rel=1e-6)

    def test_energy_penalty_is_positive_contribution_to_total(self) -> None:
        """energy_penalty stored as positive float; subtracted in total."""
        calc = DifferentialRewardCalculator(phase=1)
        r_hi = calc.compute_reward(functional_parity=0.5, ops_ratio=1.0, energy_anse=1000.0)
        r_lo = calc.compute_reward(functional_parity=0.5, ops_ratio=1.0, energy_anse=1.0)
        assert r_hi.total_reward < r_lo.total_reward

    def test_return_type_is_reward_components(self) -> None:
        calc = DifferentialRewardCalculator(phase=1)
        r = calc.compute_reward(functional_parity=0.5, ops_ratio=1.0, energy_anse=0.0)
        assert isinstance(r, RewardComponents)
        assert r.phase == 1
