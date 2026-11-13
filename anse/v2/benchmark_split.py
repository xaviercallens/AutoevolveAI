"""Deterministic hash-based benchmark task splitter and SHA-256 manifest verifier (card V0-5)."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def _list_sha256(names: list[str]) -> str:
    payload = json.dumps(names, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def split_tasks(
    tasks: list[dict[str, Any]],
    fractions: tuple[float, float, float] = (0.6, 0.2, 0.2),
    salt: str = "anse-v2",
) -> dict[str, list[dict[str, Any]]]:
    """Assign each task deterministically to train, dev, or test by SHA-256 bucket.

    Assigns each task by ``int(sha256(salt + task['name']).hexdigest(), 16) % 1000``
    thresholds so adding new tasks never moves existing ones.
    """
    if len(fractions) != 3 or any(f < 0.0 for f in fractions) or abs(sum(fractions) - 1.0) > 1e-6:
        raise ValueError(f"fractions must be a 3-tuple of non-negative numbers summing to 1.0, got {fractions}")

    t_train = round(fractions[0] * 1000)
    t_dev = round((fractions[0] + fractions[1]) * 1000)

    seen: set[str] = set()
    splits: dict[str, list[dict[str, Any]]] = {"train": [], "dev": [], "test": []}

    for task in tasks:
        raw_name = task.get("name")
        if not isinstance(raw_name, str) or not raw_name:
            raise ValueError("Every task must have a non-empty string 'name'")
        if raw_name in seen:
            raise ValueError(f"Duplicate task name: {raw_name!r}")
        seen.add(raw_name)

        digest = hashlib.sha256((salt + raw_name).encode("utf-8")).hexdigest()
        bucket = int(digest, 16) % 1000
        if bucket < t_train:
            splits["train"].append(task)
        elif bucket < t_dev:
            splits["dev"].append(task)
        else:
            splits["test"].append(task)

    return splits


def manifest(splits: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    """Map each split name to its sorted list of task names and their SHA-256 digest."""
    out: dict[str, dict[str, Any]] = {}
    for split_name, items in splits.items():
        names = sorted(str(item["name"]) for item in items)
        out[split_name] = {
            "tasks": names,
            "sha256": _list_sha256(names),
        }
    return out


def verify_manifest(
    splits: dict[str, list[dict[str, Any]]],
    expected: dict[str, dict[str, Any]],
) -> bool:
    """Return True iff *splits* matches *expected* split keys, sorted task names, and digests."""
    if set(splits.keys()) != set(expected.keys()):
        return False
    actual = manifest(splits)
    for key, actual_entry in actual.items():
        exp_entry = expected[key]
        if actual_entry["tasks"] != exp_entry.get("tasks"):
            return False
        if actual_entry["sha256"] != exp_entry.get("sha256"):
            return False
    return True
