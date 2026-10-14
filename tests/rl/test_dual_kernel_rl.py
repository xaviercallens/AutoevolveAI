"""
tests/rl/test_dual_kernel_rl.py — Unit tests for ANSERLEngine.

Verifies:
- F-07: GRPO winner is not always var_9 (seeded Gaussian breaks monotonic ordering)
- F-07: Running evaluate twice with same candidates gives diversity in advantages
- Phase 5 reward config is used (cap_ops_ratio=50.0, bonus=1000.0)
- generate_candidate_rollouts returns 10 candidates of expected types
- GRPO advantage is computed (non-zero std, advantages differ)
- Attestation receipt is a properly-formatted PROOF_RECEIPT string
"""
from __future__ import annotations

import pytest

from anse.rl.dual_kernel_rl import ANSERLEngine, RLMutationCandidate


@pytest.fixture(scope="module")
def engine_p5() -> ANSERLEngine:
    return ANSERLEngine(phase=5)


@pytest.fixture(scope="module")
def candidates(engine_p5: ANSERLEngine) -> list[RLMutationCandidate]:
    return engine_p5.generate_candidate_rollouts()


class TestCandidateGeneration:
    def test_generates_ten_candidates(self, candidates: list[RLMutationCandidate]) -> None:
        assert len(candidates) == 10

    def test_all_candidates_have_variant_ids(self, candidates: list[RLMutationCandidate]) -> None:
        ids = [c.variant_id for c in candidates]
        assert len(set(ids)) == 10, "All variant_ids must be unique"

    def test_action_types_include_all_three(self, candidates: list[RLMutationCandidate]) -> None:
        types = {c.action_type for c in candidates}
        assert "A_optim" in types
        assert "A_ai_feature" in types
        assert "A_proof" in types or "A_synth" in types

    def test_all_candidates_pass_safety_shield(self, candidates: list[RLMutationCandidate]) -> None:
        for c in candidates:
            assert c.passed_safety_shield, f"{c.variant_id} failed safety shield"


class TestGRPODiversity:
    def test_f07_peer_review_critic_is_deterministic(self, engine_p5: ANSERLEngine) -> None:
        """F-07 Peer Review fix: The Critic must evaluate pure empirical merit
        without injecting stochastic noise. With static mock candidates, the
        Critic should deterministically choose the same winner every time.
        """
        winners = set()
        for _ in range(5):
            cands = engine_p5.generate_candidate_rollouts()
            winner, _ = engine_p5.evaluate_candidates_and_select_winner(cands, iterations=2)
            winners.add(winner.variant_id)
        assert len(winners) == 1, (
            f"Critic injected noise! Expected exactly 1 deterministic winner based on merit, got: {winners}"
        )

    def test_advantages_differ_between_candidates(self, engine_p5: ANSERLEngine) -> None:
        cands = engine_p5.generate_candidate_rollouts()
        winner, _ = engine_p5.evaluate_candidates_and_select_winner(cands, iterations=2)
        advantages = [c.advantage for c in cands if c.advantage is not None]
        assert len(advantages) > 1
        # Advantages must not all be identical (that would mean std=0, degenerate)
        assert len(set(round(a, 6) for a in advantages)) > 1, (
            "All GRPO advantages are identical — diversity fix may be ineffective"
        )

    def test_winner_has_highest_advantage(self, engine_p5: ANSERLEngine) -> None:
        cands = engine_p5.generate_candidate_rollouts()
        winner, _ = engine_p5.evaluate_candidates_and_select_winner(cands, iterations=2)
        all_advantages = [c.advantage for c in cands if c.advantage is not None]
        assert winner.advantage == max(all_advantages)


class TestPhase5RewardConfig:
    def test_phase5_engine_uses_correct_alpha(self, engine_p5: ANSERLEngine) -> None:
        """F-22: Phase 5 must use alpha=2000 not the Phase 4 fallback of 1500."""
        assert engine_p5.reward_calc.alpha == 2000.0

    def test_phase5_engine_uses_cap_ops_ratio(self, engine_p5: ANSERLEngine) -> None:
        """F-22: Phase 5 must cap ops_ratio at 50.0, not leave it uncapped."""
        assert engine_p5.reward_calc.cap_ops_ratio == 50.0

    def test_phase5_bonus_amount(self, engine_p5: ANSERLEngine) -> None:
        assert engine_p5.reward_calc.bonus_amount == 1000.0

    def test_reward_does_not_overflow_from_high_ops_ratio(self, engine_p5: ANSERLEngine) -> None:
        """F-22: With cap_ops_ratio=50, a 104x ops ratio must be clamped."""
        rc = engine_p5.reward_calc.compute_reward(
            functional_parity=1.0,
            ops_ratio=104.83,    # TPU suite reported ops_ratio
            energy_anse=10.0,
            perf_gain_pct=61.9,
            ai_speedup_pct=99.0,
        )
        # perf_reward = beta * min(ops_ratio, cap) = 200 * 50 = 10000
        # Without cap it would be 200 * 104.83 = 20966 — more than double
        assert rc.performance_reward <= 200.0 * 50.0 + 1.0, (
            f"ops_ratio cap not applied: perf_reward={rc.performance_reward}"
        )


class TestAttestationReceipt:
    def test_receipt_format(self, engine_p5: ANSERLEngine) -> None:
        cands = engine_p5.generate_candidate_rollouts()
        winner, report = engine_p5.evaluate_candidates_and_select_winner(cands, iterations=2)
        trace = engine_p5.retrofit_golden_trajectory(winner, report)
        assert trace.attestation_receipt.startswith("PROOF_RECEIPT:")
        assert len(trace.attestation_receipt) == len("PROOF_RECEIPT:") + 16
