"""
Tests for the evolved JEPA dataset: real transition pairs, data-driven input
dimension, task-level splitting and skipping of unusable traces.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pytest
import torch

from anse.jepa.dataset import (
    HiddenDimMismatchError,
    JEPADataset,
    task_kfold,
    train_val_split,
)

DIM = 12


def _state(marker: float, dim: int = DIM) -> list[float]:
    """A deterministic, non-degenerate hidden state that encodes *marker*."""
    return [math.sin(marker + j) + 0.1 * marker for j in range(dim)]


def _trace(task: str, iteration: int, energy: float, marker: float, **extra: Any) -> dict[str, Any]:
    trace: dict[str, Any] = {
        "task": task,
        "iteration": iteration,
        "energy": energy,
        "code": f"def solution():\n    return {marker}",
        "hidden_state": _state(marker),
        "metadata": {"tests_total": 5, "tests_passed": 5 if energy == 0 else 2},
    }
    trace.update(extra)
    return trace


def _write(path: Path, traces: list[Any]) -> Path:
    path.write_text("\n".join(t if isinstance(t, str) else json.dumps(t) for t in traces) + "\n")
    return path


def _two_run_file(tmp_path: Path) -> Path:
    """Task A: seed 1 fails twice then passes, seed 2 passes first time. Task B: one pass."""
    return _write(
        tmp_path / "traces.jsonl",
        [
            _trace("A", 1, 60.0, 1.0),
            _trace("A", 2, 20.0, 2.0),
            _trace("A", 3, 0.0, 3.0),
            _trace("B", 1, 0.0, 4.0),
            _trace("A", 1, 0.0, 5.0),  # a new seed of task A: iteration restarts
        ],
    )


class TestTransitionPairs:
    def test_consecutive_attempts_of_one_run_become_transitions(self, tmp_path: Path) -> None:
        ds = JEPADataset(_two_run_file(tmp_path))

        assert len(ds.states) == 5
        assert ds.transitions == [(0, 1), (1, 2)]
        assert len(ds) == 5 + 2

    def test_transition_item_is_a_real_pair_with_next_attempt_energy(self, tmp_path: Path) -> None:
        ds = JEPADataset(_two_run_file(tmp_path), pair_mode="transition")

        h_ctx, h_tgt, energy = ds[0]
        assert not torch.equal(h_ctx, h_tgt), (
            "context must differ from target (old bug: ctx == tgt)"
        )
        assert torch.equal(h_ctx, ds.states[0].hidden)
        assert torch.equal(h_tgt, ds.states[1].hidden)
        assert energy.item() == pytest.approx(
            0.20
        )  # energy of attempt t+1, not of attempt t (0.60)

    def test_different_seeds_of_a_task_are_never_chained(self, tmp_path: Path) -> None:
        ds = JEPADataset(_two_run_file(tmp_path))

        run_ids = [s.run_id for s in ds.states]
        assert run_ids[0] == run_ids[1] == run_ids[2]
        assert run_ids[4] != run_ids[0], "iteration restart must open a new run"
        assert all(ds.states[a].run_id == ds.states[b].run_id for a, b in ds.transitions)

    def test_skipped_attempt_breaks_the_chain(self, tmp_path: Path) -> None:
        path = _write(
            tmp_path / "hole.jsonl",
            [
                _trace("A", 1, 60.0, 1.0),
                _trace("A", 2, 40.0, 2.0, hidden_state=[]),
                _trace("A", 3, 0.0, 3.0),
            ],
        )
        ds = JEPADataset(path)

        assert len(ds.states) == 2
        assert ds.transitions == [], "attempt 1 -> 3 is not a consecutive transition"

    def test_pair_modes_select_item_kinds(self, tmp_path: Path) -> None:
        ds = JEPADataset(_two_run_file(tmp_path), pair_mode="self")
        assert len(ds) == 5
        assert not any(ds.is_transition(i) for i in range(len(ds)))

        ds.set_pair_mode("mixed")
        assert len(ds) == 7
        assert [ds.is_transition(i) for i in range(len(ds))] == [False] * 5 + [True] * 2

    def test_self_item_keeps_state_energy_alignment(self, tmp_path: Path) -> None:
        ds = JEPADataset(_two_run_file(tmp_path), pair_mode="self")

        for idx, state in enumerate(ds.states):
            h_ctx, h_tgt, energy = ds[idx]
            assert torch.equal(h_ctx, h_tgt)
            assert energy.item() == pytest.approx(state.energy / 100.0)

    def test_unknown_pair_mode_is_rejected(self, tmp_path: Path) -> None:
        path = _two_run_file(tmp_path)
        with pytest.raises(ValueError, match="pair_mode must be one of"):
            JEPADataset(path, pair_mode="identity")
        ds = JEPADataset(path)
        with pytest.raises(ValueError, match="pair_mode must be one of"):
            ds.set_pair_mode("")

    def test_multiple_files_are_concatenated_without_cross_file_chains(
        self, tmp_path: Path
    ) -> None:
        first = _write(tmp_path / "a.jsonl", [_trace("A", 1, 50.0, 1.0)])
        second = _write(tmp_path / "b.jsonl", [_trace("A", 1, 0.0, 2.0), _trace("C", 1, 0.0, 3.0)])
        ds = JEPADataset([first, second, tmp_path / "missing.jsonl"])

        assert [s.task for s in ds.states] == ["A", "A", "C"]
        assert ds.transitions == []


class TestInputDimension:
    def test_dimension_is_inferred_from_the_data(self, tmp_path: Path) -> None:
        ds = JEPADataset(_two_run_file(tmp_path), hidden_dim=None)

        assert ds.hidden_dim == DIM
        assert ds[0][0].shape == (DIM,)

    def test_wrong_declared_dimension_raises_instead_of_padding(self, tmp_path: Path) -> None:
        path = _two_run_file(tmp_path)
        with pytest.raises(
            HiddenDimMismatchError, match=f"dimension {DIM} but the dataset expects 4096"
        ):
            JEPADataset(path, hidden_dim=4096)
        with pytest.raises(HiddenDimMismatchError, match="refusing to pad or truncate"):
            JEPADataset(path, hidden_dim=DIM - 1)

    def test_mixed_dimensions_in_one_file_raise(self, tmp_path: Path) -> None:
        short = _trace("B", 1, 0.0, 9.0, hidden_state=_state(9.0, DIM - 3))
        path = _write(tmp_path / "mixed.jsonl", [_trace("A", 1, 0.0, 1.0), short])

        with pytest.raises(HiddenDimMismatchError, match=f"dimension {DIM - 3}"):
            JEPADataset(path)
        assert isinstance(HiddenDimMismatchError("x"), ValueError)

    def test_no_state_is_zero_padded(self, tmp_path: Path) -> None:
        ds = JEPADataset(_two_run_file(tmp_path))

        for state in ds.states:
            assert state.hidden.shape == (DIM,)
            assert int((state.hidden == 0).sum()) == 0
            assert state.hidden.norm().item() == pytest.approx(1.0, abs=1e-5)


class TestUnusableTraces:
    def test_nan_inf_empty_and_malformed_are_skipped_and_counted(self, tmp_path: Path) -> None:
        nan_state = _state(2.0)
        nan_state[3] = float("nan")
        inf_state = _state(3.0)
        inf_state[0] = float("inf")
        path = _write(
            tmp_path / "dirty.jsonl",
            [
                _trace("A", 1, 0.0, 1.0),
                _trace("A", 1, 0.0, 2.0, hidden_state=nan_state),
                _trace("B", 1, 0.0, 3.0, hidden_state=inf_state),
                _trace("B", 1, 0.0, 4.0, hidden_state=[]),
                _trace("B", 1, 0.0, 5.0, hidden_state=None),
                "{this is not json",
                _trace("C", 1, float("nan"), 6.0),
                _trace("C", 1, 30.0, 7.0),
            ],
        )
        ds = JEPADataset(path)

        assert [s.task for s in ds.states] == ["A", "C"]
        assert ds.skipped == {
            "malformed_json": 1,
            "empty_hidden_state": 2,
            "non_finite": 3,
            "unverified": 0,
            "duplicate": 0,
        }
        assert all(bool(torch.isfinite(s.hidden).all()) for s in ds.states)

    def test_verified_only_drops_self_graded_traces(self, tmp_path: Path) -> None:
        path = _write(
            tmp_path / "legacy.jsonl",
            [
                _trace("A", 1, 0.0, 1.0),
                _trace("A", 1, 0.0, 2.0, metadata={"timed_out": False}),
                _trace("B", 1, 0.0, 3.0, metadata=None),
            ],
        )
        verified = JEPADataset(path, verified_only=True)
        everything = JEPADataset(path, verified_only=False)

        assert len(verified.states) == 1
        assert verified.skipped["unverified"] == 2
        assert len(everything.states) == 3

    def test_energy_is_clamped_to_unit_interval(self, tmp_path: Path) -> None:
        path = _write(tmp_path / "e.jsonl", [_trace("A", 1, 250.0, 1.0), _trace("B", 1, -5.0, 2.0)])
        ds = JEPADataset(path)

        assert ds[0][2].item() == pytest.approx(1.0)
        assert ds[1][2].item() == pytest.approx(0.0)


def _many_task_file(tmp_path: Path, n_tasks: int = 10) -> Path:
    traces = []
    for t in range(n_tasks):
        traces.append(_trace(f"task-{t}", 1, 40.0, float(t)))
        traces.append(_trace(f"task-{t}", 2, 0.0, float(t) + 0.5))
        traces.append(_trace(f"task-{t}", 1, 0.0, float(t) + 0.25))
    return _write(tmp_path / "many.jsonl", traces)


class TestTaskLevelSplit:
    def test_no_task_appears_on_both_sides(self, tmp_path: Path) -> None:
        ds = JEPADataset(_many_task_file(tmp_path))
        tasks = ds.item_tasks
        for seed in range(5):
            train, val = train_val_split(ds, val_fraction=0.3, seed=seed)
            train_tasks = {tasks[i] for i in train.indices}
            val_tasks = {tasks[i] for i in val.indices}

            assert train_tasks.isdisjoint(val_tasks)
            assert len(val_tasks) == 3
            assert sorted(train.indices + val.indices) == list(range(len(ds)))

    def test_transition_items_follow_their_task(self, tmp_path: Path) -> None:
        ds = JEPADataset(_many_task_file(tmp_path))
        _, val = train_val_split(ds, val_fraction=0.2, seed=7)
        val_tasks = {ds.item_tasks[i] for i in val.indices}

        val_transitions = [i for i in val.indices if ds.is_transition(i)]
        assert len(val_transitions) == len(val_tasks)  # one transition per task in this fixture
        assert len(val.indices) == 4 * len(val_tasks)  # 3 states + 1 transition per task

    def test_split_is_deterministic_and_seed_dependent(self, tmp_path: Path) -> None:
        ds = JEPADataset(_many_task_file(tmp_path))
        first = train_val_split(ds, 0.2, seed=42)[1].indices
        again = train_val_split(ds, 0.2, seed=42)[1].indices
        others = [train_val_split(ds, 0.2, seed=s)[1].indices for s in range(1, 6)]

        assert first == again
        assert any(other != first for other in others)

    def test_both_sides_non_empty_at_extreme_fractions(self, tmp_path: Path) -> None:
        ds = JEPADataset(_many_task_file(tmp_path, n_tasks=3))
        for fraction in (0.0, 0.01, 0.99, 1.0):
            train, val = train_val_split(ds, val_fraction=fraction, seed=1)
            assert len(train) > 0
            assert len(val) > 0

    def test_single_task_falls_back_to_item_split(self, tmp_path: Path) -> None:
        path = _write(
            tmp_path / "one.jsonl", [_trace("only", 1, float(i), float(i)) for i in range(10)]
        )
        ds = JEPADataset(path)
        train, val = train_val_split(ds, val_fraction=0.2, seed=3)

        assert len(val) == 2
        assert sorted(train.indices + val.indices) == list(range(10))


class TestTaskKFold:
    def test_folds_partition_the_tasks(self) -> None:
        tasks = [f"t{i % 11}" for i in range(40)]
        folds = task_kfold(tasks, k=4, seed=9)

        assert len(folds) == 4
        assert set().union(*folds) == set(tasks)
        assert sum(len(f) for f in folds) == 11
        assert max(len(f) for f in folds) - min(len(f) for f in folds) <= 1

    def test_folds_ignore_trace_order_and_depend_on_seed(self) -> None:
        tasks = [f"t{i}" for i in range(12)]
        assert task_kfold(tasks, 3, seed=5) == task_kfold(list(reversed(tasks)) * 2, 3, seed=5)
        assert any(
            task_kfold(tasks, 3, seed=5) != task_kfold(tasks, 3, seed=s) for s in range(6, 10)
        )

    def test_invalid_k_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="k must be >= 2"):
            task_kfold(["a", "b"], k=1, seed=0)
        with pytest.raises(ValueError, match="cannot build 3 task folds from 2 distinct tasks"):
            task_kfold(["a", "b", "a"], k=3, seed=0)


class TestDuplicateTraces:
    """A re-run of a seeded Phase 1 benchmark appends byte-identical traces to the same file."""

    def test_replayed_run_adds_no_states_and_no_transitions(self, tmp_path: Path) -> None:
        run = [_trace("A", 1, 60.0, 1.0), _trace("A", 2, 60.0, 2.0), _trace("B", 1, 0.0, 3.0)]
        once = JEPADataset(_write(tmp_path / "once.jsonl", run))
        replayed = JEPADataset(_write(tmp_path / "replayed.jsonl", run + run + run))

        assert len(replayed.states) == len(once.states) == 3
        assert replayed.transitions == once.transitions == [(0, 1)]
        assert replayed.skipped["duplicate"] == 6
        assert once.skipped["duplicate"] == 0

    def test_duplicates_across_files_are_dropped_too(self, tmp_path: Path) -> None:
        first = _write(tmp_path / "a.jsonl", [_trace("A", 1, 0.0, 1.0), _trace("B", 1, 10.0, 2.0)])
        second = _write(tmp_path / "b.jsonl", [_trace("A", 1, 0.0, 1.0), _trace("C", 1, 0.0, 3.0)])
        ds = JEPADataset([first, second])

        assert [s.task for s in ds.states] == ["A", "B", "C"]
        assert ds.skipped["duplicate"] == 1

    def test_same_embedding_at_a_later_iteration_is_kept_as_a_transition(
        self, tmp_path: Path
    ) -> None:
        """The LLM repeating itself on a retry is a real (unchanged) transition, not a replayed trace."""
        ds = JEPADataset(
            _write(tmp_path / "t.jsonl", [_trace("A", 1, 60.0, 1.0), _trace("A", 2, 60.0, 1.0)])
        )

        assert len(ds.states) == 2
        assert ds.transitions == [(0, 1)]
        assert ds.skipped["duplicate"] == 0
        assert ds.distinct_embedding_count() == 1

    def test_replay_that_diverges_links_the_new_attempt_to_the_existing_state(
        self, tmp_path: Path
    ) -> None:
        traces = [
            _trace("A", 1, 60.0, 1.0),
            _trace("A", 2, 60.0, 2.0),
            _trace("A", 1, 60.0, 1.0),
            _trace("A", 2, 0.0, 9.0),  # same first attempt, different retry
        ]
        ds = JEPADataset(_write(tmp_path / "t.jsonl", traces))

        assert len(ds.states) == 3
        assert ds.skipped["duplicate"] == 1
        assert ds.transitions == [(0, 1), (0, 2)]
        assert ds.states[2].energy == 0.0

    def test_deduplicate_false_keeps_every_trace(self, tmp_path: Path) -> None:
        run = [_trace("A", 1, 60.0, 1.0), _trace("A", 1, 60.0, 1.0)]
        ds = JEPADataset(_write(tmp_path / "t.jsonl", run), deduplicate=False)

        assert len(ds.states) == 2
        assert ds.skipped["duplicate"] == 0


class TestFirstAttempts:
    def test_first_attempts_are_run_openers_only(self, tmp_path: Path) -> None:
        ds = JEPADataset(_two_run_file(tmp_path))

        first = ds.first_attempt_indices()
        assert first == [0, 3, 4]
        assert all(ds.states[i].iteration == 1 for i in first)
        assert not set(first) & {tgt for _, tgt in ds.transitions}

    def test_orphan_retry_is_not_a_first_attempt(self, tmp_path: Path) -> None:
        """A retry whose first attempt was unusable opens a run but still carries the retry cue."""
        nan_state = _state(1.0)
        nan_state[0] = float("nan")
        traces = [
            _trace("A", 1, 60.0, 1.0, hidden_state=nan_state),
            _trace("A", 2, 60.0, 2.0),
            _trace("B", 1, 0.0, 3.0),
        ]
        ds = JEPADataset(_write(tmp_path / "t.jsonl", traces))

        assert [s.iteration for s in ds.states] == [2, 1]
        assert ds.first_attempt_indices() == [1]
