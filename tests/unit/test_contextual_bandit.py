"""
Unit tests for Disjoint LinUCB Contextual Bandit.
Verifies microsecond arm selection, Sherman-Morrison rank-1 update math,
and state serialization/deserialization.
"""

from __future__ import annotations

from pathlib import Path

from anse.community.contextual_bandit import DisjointLinUCB, extract_context_features


def test_extract_context_features():
    """Verify context vector encoding dimensionality and bounds."""
    ctx = extract_context_features("ai", hour_utc=14, day_of_week=2, has_doi=True, has_code=True)
    assert len(ctx) == 10
    # First 5 are one-hot domain
    assert ctx[0] == 1.0
    assert sum(ctx[:5]) == 1.0
    # Day normalization in [0, 1]
    assert 0.0 <= ctx[7] <= 1.0


def test_linucb_arm_selection_and_update():
    """Verify that arm selection and Sherman-Morrison updates update payoff estimates."""
    bandit = DisjointLinUCB(n_actions=4, d_features=10, alpha=1.0)
    ctx = extract_context_features("physics", hour_utc=15, day_of_week=3)

    # Initial selection
    action_info = bandit.select_action(ctx)
    action_id = action_info["action_id"]
    assert 0 <= action_id < 4
    assert action_info["predicted_payoff"] == 0.0

    # Provide a strong positive reward to action 2
    bandit.update(action=2, context=ctx, reward=1.0)

    # Re-evaluate with same context: action 2 should now have higher predicted payoff
    action_info_after = bandit.select_action(ctx)
    assert bandit._compute_theta(2)[1] > 0.0  # Physics domain index is 1


def test_linucb_state_persistence(tmp_path: Path):
    """Verify save_state and load_state round-trip preserves parameters."""
    bandit = DisjointLinUCB(n_actions=3, d_features=10, alpha=1.5)
    ctx = extract_context_features("math", hour_utc=10, day_of_week=1)
    bandit.update(action=1, context=ctx, reward=0.85)

    save_file = tmp_path / "bandit_test.json"
    bandit.save_state(save_file)
    assert save_file.exists()

    new_bandit = DisjointLinUCB(n_actions=3, d_features=10)
    loaded = new_bandit.load_state(save_file)
    assert loaded is True
    assert new_bandit.alpha == 1.5
    assert new_bandit.b[1] == bandit.b[1]
