"""Tests for ``anse.v2.benchmark_split`` (card V0-5)."""

from __future__ import annotations

import pytest

from anse.v2.benchmark_split import manifest, split_tasks, verify_manifest


def test_split_tasks_stable_under_reordering_and_appending() -> None:
    base = [{"name": f"task_{i}", "task": f"do {i}"} for i in range(50)]
    s1 = split_tasks(base)
    s2 = split_tasks(list(reversed(base)))
    for k in ("train", "dev", "test"):
        assert sorted(t["name"] for t in s1[k]) == sorted(t["name"] for t in s2[k])

    extended = base + [{"name": f"extra_{j}", "task": "x"} for j in range(25)]
    s_ext = split_tasks(extended)
    base_names = {t["name"] for t in base}
    for k in ("train", "dev", "test"):
        ext_subset = {t["name"] for t in s_ext[k] if t["name"] in base_names}
        orig_set = {t["name"] for t in s1[k]}
        assert ext_subset == orig_set


def test_split_tasks_fractions_on_500_synthetic_tasks() -> None:
    tasks = [{"name": f"synth_{i}"} for i in range(500)]
    splits = split_tasks(tasks, fractions=(0.6, 0.2, 0.2), salt="anse-v2")
    assert len(splits["train"]) + len(splits["dev"]) + len(splits["test"]) == 500
    assert 250 <= len(splits["train"]) <= 350
    assert 70 <= len(splits["dev"]) <= 130
    assert 70 <= len(splits["test"]) <= 130


def test_split_tasks_validation_errors() -> None:
    with pytest.raises(ValueError, match="Duplicate task name"):
        split_tasks([{"name": "dup"}, {"name": "dup"}])
    with pytest.raises(ValueError, match="non-empty string"):
        split_tasks([{"name": ""}])
    with pytest.raises(ValueError, match="3-tuple"):
        split_tasks([{"name": "a"}], fractions=(0.5, 0.5, 0.5))


def test_manifest_round_trips_and_detects_tampering() -> None:
    tasks = [{"name": f"t_{i}"} for i in range(30)]
    splits = split_tasks(tasks)
    m = manifest(splits)
    assert verify_manifest(splits, m) is True

    # Removing one task breaks verification
    popped = splits["train"].pop()
    assert verify_manifest(splits, m) is False
    splits["train"].append(popped)
    assert verify_manifest(splits, m) is True

    # Corrupting sha256 while keeping task list identical breaks verification
    corrupted_sha = {
        k: {"tasks": list(v["tasks"]), "sha256": ("0" * 64 if k == "train" else v["sha256"])}
        for k, v in m.items()
    }
    assert verify_manifest(splits, corrupted_sha) is False

    # Mismatched split keys return False
    assert verify_manifest(splits, {"train": m["train"]}) is False
