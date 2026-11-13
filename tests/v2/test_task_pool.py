"""Tests for ``anse.v2.task_pool`` (card T-1)."""

from __future__ import annotations

from pathlib import Path

from anse.v2.task_pool import convert_mbpp, count_skipped, dump_yaml
from main import load_tasks


def test_convert_mbpp_and_count_skipped_and_yaml_round_trip(tmp_path: Path) -> None:
    rows = [
        {
            "task_id": 11,
            "text": "Write a function first_repeated_char(s).",
            "test_list": ["assert first_repeated_char('abcab') == 'a'", "assert first_repeated_char('xyz') is None"],
        },
        {"task_id": 12, "text": "Missing test_list"},
        {"task_id": "bad_id", "text": "Non-int id", "test_list": ["assert True"]},
        {"task_id": 13, "text": "   ", "test_list": ["assert True"]},
        {"task_id": 14, "text": "Empty tests", "test_list": []},
        {
            "task_id": 15,
            "text": "Write square(x).",
            "test_list": ["assert square(3) == 9"],
        },
    ]

    assert count_skipped(rows) == 4
    tasks = convert_mbpp(rows, tier="mbpp_pool")
    assert len(tasks) == 2
    assert tasks[0] == {
        "name": "mbpp_11",
        "tier": "mbpp_pool",
        "task": (
            "Write a function first_repeated_char(s). Include these asserts at the bottom of your code:\n"
            "assert first_repeated_char('abcab') == 'a'\n"
            "assert first_repeated_char('xyz') is None"
        ),
        "expected_output": None,
    }

    yaml_path = tmp_path / "sub" / "mbpp_tasks.yaml"
    dump_yaml(tasks, yaml_path)
    loaded = load_tasks(yaml_path)
    assert loaded == tasks
