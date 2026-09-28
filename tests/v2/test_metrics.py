"""Tests for anse.v2.metrics (card V0-3): rank metrics for a zero-inflated target."""

from __future__ import annotations

import math
import random

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from anse.v2.metrics import auroc, average_ranks, bootstrap_ci, median_baseline_mae, spearman


def _brute_force_auroc(scores: list[float], labels: list[int]) -> float:
    """O(n^2) pair count: P(score_pos > score_neg) + 0.5 * P(tie)."""
    pos = [s for s, y in zip(scores, labels, strict=True) if y == 1]
    neg = [s for s, y in zip(scores, labels, strict=True) if y == 0]
    total = 0.0
    for p in pos:
        for q in neg:
            total += 1.0 if p > q else 0.5 if p == q else 0.0
    return total / (len(pos) * len(neg))


# ── average_ranks ──────────────────────────────────────────────────────────


def test_average_ranks_ties_share_mean_position() -> None:
    assert average_ranks([10.0, 20.0, 20.0, 30.0]) == [1.0, 2.5, 2.5, 4.0]
    assert average_ranks([3.0, 1.0, 2.0]) == [3.0, 1.0, 2.0]
    assert average_ranks([]) == []


# ── auroc ──────────────────────────────────────────────────────────────────


def test_auroc_perfect_inverted_ties_single_class() -> None:
    assert auroc([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1]) == 1.0
    assert auroc([0.9, 0.8, 0.2, 0.1], [0, 0, 1, 1]) == 0.0
    assert auroc([0.5, 0.5, 0.5, 0.5], [0, 1, 0, 1]) == 0.5
    assert auroc([0.1, 0.2, 0.3], [1, 1, 1]) is None
    assert auroc([0.1, 0.2, 0.3], [0, 0, 0]) is None
    assert auroc([], []) is None


def test_auroc_rejects_bad_input() -> None:
    with pytest.raises(ValueError):
        auroc([0.1, 0.2], [0])
    with pytest.raises(ValueError):
        auroc([0.1, 0.2], [0, 2])


def test_auroc_partial_ties_match_half_credit() -> None:
    # One tie between a positive and a negative out of 2x2 pairs: (1 + 1 + 1 + 0.5) / 4.
    scores = [0.3, 0.5, 0.5, 0.9]
    labels = [0, 0, 1, 1]
    value = auroc(scores, labels)
    assert value == pytest.approx(0.875)
    assert value == pytest.approx(_brute_force_auroc(scores, labels))


def test_auroc_matches_brute_force_on_seeded_few_valued_data() -> None:
    rng = random.Random(1234)
    for _ in range(200):
        n = rng.randint(2, 40)
        scores = [rng.choice([0.0, 0.25, 0.5, 0.75, 1.0]) for _ in range(n)]
        labels = [rng.randint(0, 1) for _ in range(n)]
        value = auroc(scores, labels)
        if len(set(labels)) < 2:
            assert value is None
            continue
        assert value == pytest.approx(_brute_force_auroc(scores, labels), abs=1e-12)


@settings(max_examples=150, deadline=None)
@given(
    st.lists(
        st.tuples(st.floats(min_value=-5, max_value=5, allow_nan=False), st.integers(0, 1)),
        min_size=2,
        max_size=30,
    )
)
def test_auroc_matches_brute_force_hypothesis(pairs: list[tuple[float, int]]) -> None:
    scores = [p[0] for p in pairs]
    labels = [p[1] for p in pairs]
    value = auroc(scores, labels)
    if len(set(labels)) < 2:
        assert value is None
    else:
        assert value is not None
        assert 0.0 <= value <= 1.0
        assert value == pytest.approx(_brute_force_auroc(scores, labels), abs=1e-9)


# ── spearman ───────────────────────────────────────────────────────────────


def test_spearman_perfect_inverted_ties_constant() -> None:
    assert spearman([1.0, 2.0, 3.0, 4.0], [10.0, 20.0, 30.0, 40.0]) == pytest.approx(1.0)
    assert spearman([1.0, 2.0, 3.0, 4.0], [40.0, 30.0, 20.0, 10.0]) == pytest.approx(-1.0)
    # Monotone but nonlinear is still a perfect rank correlation.
    assert spearman([1.0, 2.0, 3.0, 4.0], [1.0, 8.0, 27.0, 64.0]) == pytest.approx(1.0)
    # Ties: xs ranks (1, 2.5, 2.5, 4), ys ranks (1, 2, 3, 4) -> 0.9487 (closed form 0.6*sqrt(2.5)).
    assert spearman([1.0, 2.0, 2.0, 3.0], [1.0, 2.0, 3.0, 4.0]) == pytest.approx(0.6 * math.sqrt(2.5))
    assert spearman([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]) is None
    assert spearman([1.0, 2.0, 3.0], [7.0, 7.0, 7.0]) is None
    assert spearman([1.0, 2.0], [1.0, 2.0]) is None


def test_spearman_rejects_length_mismatch() -> None:
    with pytest.raises(ValueError):
        spearman([1.0, 2.0, 3.0], [1.0, 2.0])


def test_spearman_is_symmetric_and_bounded() -> None:
    rng = random.Random(7)
    for _ in range(50):
        xs = [rng.choice([0.0, 1.0, 2.0]) for _ in range(12)]
        ys = [rng.random() for _ in range(12)]
        if len(set(xs)) < 2:
            continue
        r = spearman(xs, ys)
        assert r is not None
        assert -1.0 <= r <= 1.0
        assert r == pytest.approx(spearman(ys, xs))


# ── bootstrap_ci ───────────────────────────────────────────────────────────


def test_bootstrap_ci_deterministic_per_seed_and_ordered() -> None:
    rng = random.Random(3)
    scores = [rng.random() for _ in range(40)]
    labels = [1 if s + rng.gauss(0, 0.3) > 0.5 else 0 for s in scores]
    lo1, hi1 = bootstrap_ci(auroc, scores, labels, n=200, seed=11)
    lo2, hi2 = bootstrap_ci(auroc, scores, labels, n=200, seed=11)
    lo3, hi3 = bootstrap_ci(auroc, scores, labels, n=200, seed=12)
    assert (lo1, hi1) == (lo2, hi2)
    assert (lo1, hi1) != (lo3, hi3)
    assert lo1 <= hi1
    assert 0.0 <= lo1 and hi1 <= 1.0
    point = auroc(scores, labels)
    assert point is not None
    assert lo1 <= point <= hi1


def test_bootstrap_ci_narrows_with_alpha() -> None:
    xs = [float(i) for i in range(30)]
    ys = [float(i % 7) + 0.1 * i for i in range(30)]
    lo_wide, hi_wide = bootstrap_ci(spearman, xs, ys, n=300, seed=0, alpha=0.5)
    lo_narrow, hi_narrow = bootstrap_ci(spearman, xs, ys, n=300, seed=0, alpha=0.05)
    assert lo_narrow <= lo_wide
    assert hi_wide <= hi_narrow


def test_bootstrap_ci_raises_when_too_few_valid_resamples() -> None:
    # Every resample of a constant series is undefined -> zero valid resamples.
    with pytest.raises(ValueError, match="valid"):
        bootstrap_ci(spearman, [1.0] * 20, [float(i) for i in range(20)], n=50, seed=0)
    # Fewer than 10 resamples requested can never yield 10 valid ones.
    scores = [float(i) for i in range(30)]
    labels = [i % 2 for i in range(30)]
    with pytest.raises(ValueError, match="valid"):
        bootstrap_ci(auroc, scores, labels, n=5, seed=0)
    with pytest.raises(ValueError):
        bootstrap_ci(auroc, [], [], n=10, seed=0)
    with pytest.raises(ValueError):
        bootstrap_ci(auroc, [0.1, 0.2], [0], n=10, seed=0)


# ── median_baseline_mae ────────────────────────────────────────────────────


def test_median_baseline_mae_odd_even_and_zero_inflated() -> None:
    assert median_baseline_mae([1.0, 2.0, 10.0]) == pytest.approx((1.0 + 0.0 + 8.0) / 3)
    assert median_baseline_mae([1.0, 3.0]) == pytest.approx(1.0)  # median 2.0
    # 84 % zeros, 16 % ones: median is 0, MAE is the failure rate.
    actuals = [0.0] * 84 + [1.0] * 16
    assert median_baseline_mae(actuals) == pytest.approx(0.16)
    with pytest.raises(ValueError):
        median_baseline_mae([])


@given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False), min_size=1, max_size=50))
def test_median_baseline_mae_never_beaten_by_mean_predictor(actuals: list[float]) -> None:
    mean = sum(actuals) / len(actuals)
    mean_mae = sum(abs(a - mean) for a in actuals) / len(actuals)
    assert median_baseline_mae(actuals) <= mean_mae + 1e-9
