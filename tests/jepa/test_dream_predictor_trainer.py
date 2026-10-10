"""Tests for the gated dream-predictor trainer: AUROC, task-grouped folds, and the PASS/BLOCKED gate."""

from __future__ import annotations

import math
import random
from typing import Any

from hypothesis import given
from hypothesis import strategies as st

from anse.jepa.dream_predictor_trainer import (
    MIN_POSITIVES,
    auroc,
    evaluate_gate,
    grouped_folds,
)


def _rows(n_tasks: int, per_task: int, seed: int, signal: bool) -> list[dict[str, Any]]:
    """Synthetic rows. With ``signal`` the first feature separates failures from passes."""
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    for t in range(n_tasks):
        for i in range(per_task):
            label = 1.0 if i % 2 == 0 else 0.0
            centre = 2.0 if (signal and label == 1.0) else 0.0
            hidden = [centre + rng.gauss(0, 0.3)] + [rng.gauss(0, 1.0) for _ in range(5)]
            rows.append({"task": f"task-{t}", "hidden_state": hidden, "energy": label})
    return rows


def test_auroc_is_one_for_perfect_separation_and_zero_for_reversed() -> None:
    labels = [0, 0, 1, 1]

    assert auroc([0.1, 0.2, 0.8, 0.9], labels) == 1.0
    assert auroc([0.9, 0.8, 0.2, 0.1], labels) == 0.0


def test_auroc_counts_ties_as_half_and_is_undefined_without_both_classes() -> None:
    assert auroc([0.5, 0.5], [0, 1]) == 0.5
    assert math.isnan(auroc([0.1, 0.9], [1, 1]))


@given(
    tasks=st.lists(st.text(min_size=1, max_size=8), min_size=1, max_size=40),
    k=st.integers(min_value=1, max_value=6),
    seed=st.integers(min_value=0, max_value=10_000),
)
def test_grouped_folds_partition_the_distinct_tasks(tasks: list[str], k: int, seed: int) -> None:
    folds = grouped_folds(tasks, k, seed)

    assert len(folds) == k
    assert set().union(*folds) == set(tasks)
    assert sum(len(f) for f in folds) == len(set(tasks))


def test_gate_blocks_when_there_are_too_few_failures() -> None:
    rows = _rows(n_tasks=10, per_task=4, seed=1, signal=True)
    for row in rows[: len(rows) - (MIN_POSITIVES - 1)]:
        row["energy"] = 0.0

    gate = evaluate_gate(rows, seeds=(0,))

    assert gate.status == "BLOCKED"
    assert gate.positives < MIN_POSITIVES
    assert any("need >=" in reason for reason in gate.reasons)


def test_gate_passes_on_a_real_signal_with_shuffled_control_at_chance() -> None:
    rows = _rows(n_tasks=12, per_task=10, seed=3, signal=True)

    gate = evaluate_gate(rows, seeds=(0, 1))

    assert gate.status == "PASS", gate.reasons
    assert gate.worst_real > gate.control_best + gate.control_spread
    assert gate.worst_real > 0.9


def test_gate_blocks_when_labels_carry_no_signal() -> None:
    rows = _rows(n_tasks=12, per_task=10, seed=4, signal=False)

    gate = evaluate_gate(rows, seeds=(0, 1))

    assert gate.status == "BLOCKED"
    assert gate.worst_real <= gate.control_best + gate.control_spread
    assert gate.reasons
