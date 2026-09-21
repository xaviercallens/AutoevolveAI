"""
Tests for anse.jepa.metrics — the measurements behind the Phase 2 evolution gate.
"""

from __future__ import annotations

import math
import random

import pytest
import torch

from anse.jepa.metrics import (
    average_ranks,
    latent_std,
    mean_absolute_error,
    ridge_fit_predict,
    roc_auc,
    spearman,
)


def _random_values(seed: int, n: int = 25) -> list[float]:
    rng = random.Random(seed)
    return [rng.uniform(-50.0, 150.0) for _ in range(n)]


class TestMeanAbsoluteError:
    def test_known_value_and_zero_on_identity(self) -> None:
        assert mean_absolute_error([0.0, 10.0, 30.0], [10.0, 10.0, 0.0]) == pytest.approx(40.0 / 3.0)
        values = _random_values(1)
        assert mean_absolute_error(values, values) == 0.0

    @pytest.mark.parametrize("seed", range(5))
    def test_symmetry_and_translation_invariance(self, seed: int) -> None:
        a, b = _random_values(seed), _random_values(seed + 100)
        base = mean_absolute_error(a, b)

        assert mean_absolute_error(b, a) == pytest.approx(base)
        assert mean_absolute_error([x + 7.5 for x in a], [y + 7.5 for y in b]) == pytest.approx(base)

    def test_invalid_input_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="length mismatch: 2 predictions vs 1 labels"):
            mean_absolute_error([1.0, 2.0], [1.0])
        with pytest.raises(ValueError, match="at least one sample"):
            mean_absolute_error([], [])


class TestAverageRanks:
    def test_ties_share_their_mean_rank(self) -> None:
        assert average_ranks([10.0, 0.0, 10.0, 5.0]) == [3.5, 1.0, 3.5, 2.0]
        assert average_ranks([4.0, 4.0, 4.0]) == [2.0, 2.0, 2.0]

    @pytest.mark.parametrize("seed", range(5))
    def test_rank_sum_is_preserved_even_with_ties(self, seed: int) -> None:
        values = [round(v / 40.0) for v in _random_values(seed, 30)]  # heavy ties
        ranks = average_ranks(values)

        assert sum(ranks) == pytest.approx(30 * 31 / 2)
        assert all((values[i] < values[j]) == (ranks[i] < ranks[j]) for i in range(30) for j in range(30))


class TestSpearman:
    @pytest.mark.parametrize("seed", range(5))
    def test_monotone_transform_gives_plus_or_minus_one(self, seed: int) -> None:
        x = _random_values(seed)

        assert spearman(x, [math.exp(v / 50.0) for v in x]) == pytest.approx(1.0)
        assert spearman(x, [-3.0 * v + 2.0 for v in x]) == pytest.approx(-1.0)

    def test_constant_side_is_undefined_not_zero(self) -> None:
        assert spearman([1.0, 2.0, 3.0], [0.0, 0.0, 0.0]) is None
        assert spearman([5.0], [1.0]) is None

    def test_known_value_with_ties(self) -> None:
        # ranks x = [1, 2, 3, 4], ranks y = [1.5, 1.5, 3.5, 3.5] → Pearson = 0.8944...
        value = spearman([1.0, 2.0, 3.0, 4.0], [0.0, 0.0, 50.0, 50.0])
        assert value == pytest.approx(2.0 / math.sqrt(5.0))
        with pytest.raises(ValueError, match="length mismatch"):
            spearman([1.0], [1.0, 2.0])


class TestRocAuc:
    def test_perfect_inverted_and_tied_scores(self) -> None:
        labels = [True, True, False, False, False]
        assert roc_auc([90.0, 80.0, 10.0, 20.0, 30.0], labels) == 1.0
        assert roc_auc([1.0, 2.0, 10.0, 20.0, 30.0], labels) == 0.0
        assert roc_auc([5.0] * 5, labels) == 0.5

    def test_boundary_one_pair_swapped(self) -> None:
        # 2 positives x 3 negatives = 6 pairs, exactly one is ordered wrongly
        assert roc_auc([90.0, 15.0, 10.0, 20.0, 5.0], [True, True, False, False, False]) == pytest.approx(5.0 / 6.0)
        assert roc_auc([90.0, 20.0, 10.0, 20.0, 5.0], [True, True, False, False, False]) == pytest.approx(5.5 / 6.0)

    @pytest.mark.parametrize("seed", range(5))
    def test_negating_scores_complements_the_auc(self, seed: int) -> None:
        scores = _random_values(seed, 40)
        rng = random.Random(seed)
        labels = [rng.random() < 0.3 for _ in scores]
        labels[0], labels[1] = True, False
        auc = roc_auc(scores, labels)
        flipped = roc_auc([-s for s in scores], labels)

        assert auc is not None and flipped is not None
        assert auc + flipped == pytest.approx(1.0)

    def test_single_class_is_undefined(self) -> None:
        assert roc_auc([1.0, 2.0], [False, False]) is None
        assert roc_auc([1.0, 2.0], [True, True]) is None
        with pytest.raises(ValueError, match="length mismatch"):
            roc_auc([1.0], [True, False])


class TestRidge:
    def test_recovers_a_linear_function_when_alpha_is_tiny(self) -> None:
        generator = torch.Generator().manual_seed(0)
        x = torch.randn(40, 6, generator=generator)
        weights = torch.tensor([3.0, -2.0, 0.5, 0.0, 1.0, -1.0])
        y = x @ weights + 12.0
        x_new = torch.randn(10, 6, generator=generator)
        predicted = ridge_fit_predict(x, y, x_new, alpha=1e-8)

        assert torch.allclose(predicted, x_new @ weights + 12.0, atol=1e-3)
        assert predicted.dtype == torch.float32

    def test_huge_alpha_shrinks_to_the_training_mean(self) -> None:
        generator = torch.Generator().manual_seed(1)
        x, y = torch.randn(15, 30, generator=generator), torch.rand(15, generator=generator) * 100.0
        predicted = ridge_fit_predict(x, y, torch.randn(5, 30, generator=generator), alpha=1e12)

        assert torch.allclose(predicted, y.mean().expand(5), atol=1e-3)
        with pytest.raises(ValueError, match="alpha must be > 0"):
            ridge_fit_predict(x, y, x, alpha=0.0)

    def test_row_mismatch_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="same number of rows"):
            ridge_fit_predict(torch.zeros(3, 2), torch.zeros(4), torch.zeros(1, 2))
        assert ridge_fit_predict(torch.eye(3), torch.tensor([1.0, 2.0, 3.0]), torch.eye(3)).shape == (3,)


class TestLatentStd:
    def test_collapsed_and_spread_dimensions_are_told_apart(self) -> None:
        z = torch.zeros(6, 3)
        z[:, 1] = torch.tensor([0.0, 2.0, 4.0, 6.0, 8.0, 10.0])
        std = latent_std(z)

        assert std[0].item() == 0.0
        assert std[1].item() == pytest.approx(math.sqrt(14.0))
        assert std.shape == (3,)

    def test_needs_a_batch(self) -> None:
        with pytest.raises(ValueError, match="B >= 2"):
            latent_std(torch.zeros(1, 4))
        with pytest.raises(ValueError, match="B >= 2"):
            latent_std(torch.zeros(4))
