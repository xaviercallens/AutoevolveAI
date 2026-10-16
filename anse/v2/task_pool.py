"""Convert MBPP-style JSONL rows into the ANSE Phase 1 task YAML schema (card T-1)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REQUIRED_KEYS = ("task_id", "text", "test_list")


def _is_valid_row(row: dict[str, Any]) -> bool:
    if not all(k in row for k in REQUIRED_KEYS):
        return False
    task_id = row["task_id"]
    text = row["text"]
    test_list = row["test_list"]
    if not isinstance(task_id, int) or isinstance(task_id, bool):
        return False
    if not isinstance(text, str) or not text.strip():
        return False
    if not isinstance(test_list, list) or not test_list or not all(isinstance(x, str) for x in test_list):
        return False
    return True


def count_skipped(rows: list[dict[str, Any]]) -> int:
    """Count rows missing any required key or holding invalid types."""
    return sum(1 for row in rows if not _is_valid_row(row))


def convert_mbpp(rows: list[dict[str, Any]], tier: str = "pool") -> list[dict[str, Any]]:
    """Convert valid MBPP rows into the ANSE task schema."""
    out: list[dict[str, Any]] = []
    for row in rows:
        if not _is_valid_row(row):
            continue
        asserts_block = "\n".join(row["test_list"])
        out.append(
            {
                "name": f"mbpp_{row['task_id']}",
                "tier": tier,
                "task": (
                    f"{row['text']} Include these asserts at the bottom of your code:\n{asserts_block}"
                ),
                "expected_output": None,
            }
        )
    return out


def dump_yaml(tasks: list[dict[str, Any]], path: Path | str) -> None:
    """Write ``{'tasks': tasks}`` to *path* using ``yaml.safe_dump(sort_keys=False)``."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump({"tasks": tasks}, sort_keys=False), encoding="utf-8")
