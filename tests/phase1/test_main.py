import shutil

import pytest

"""Tests for CLI entry point main.py."""

import yaml

from anse.core.agent_loop import AgentLoop
from anse.core.encoder import HiddenStateExtractor
from anse.memory.harvester import Harvester
from main import load_tasks, run_benchmark


@pytest.mark.skipif(shutil.which("docker") is None, reason="Requires docker")
def test_load_tasks(tmp_path):
    tasks_file = tmp_path / "test_tasks.yaml"
    data = {
        "tasks": [
            {"name": "Task A", "task": "Print 1"},
            {"name": "Task B", "task": "Print 2"},
        ]
    }
    with open(tasks_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f)

    loaded = load_tasks(tasks_file)
    assert len(loaded) == 2
    assert loaded[0]["name"] == "Task A"


@pytest.mark.skipif(shutil.which("docker") is None, reason="Requires docker")
def test_run_benchmark_mock(tmp_path):
    extractor = HiddenStateExtractor(mock_mode=True)
    harvester = Harvester(enable_chroma=False)
    harvester.log_path = tmp_path / "interactions.jsonl"

    loop = AgentLoop(
        extractor=extractor,
        harvester=harvester,
        max_retries=2,
    )

    tasks = [
        {"name": "Task 1", "task": "Return True"},
        {"name": "Task 2", "task": "Return True"},
    ]

    summaries, rate = run_benchmark(loop, tasks, max_retries=1)
    assert len(summaries) == 2
    # Mock extractor returns working assert solution() is True (energy=0.0)
    assert rate == 100.0


@pytest.mark.skipif(shutil.which("docker") is None, reason="Requires docker")
def test_load_tasks_missing_file(tmp_path):
    missing = tmp_path / "does_not_exist.yaml"
    loaded = load_tasks(missing)
    assert loaded == []


@pytest.mark.skipif(shutil.which("docker") is None, reason="Requires docker")
def test_main_cli_single_task(monkeypatch, tmp_path):
    import sys

    from main import main

    test_args = [
        "main.py",
        "--mock-llm",
        "--no-chroma",
        "--output-dir",
        str(tmp_path),
        "--single-task",
        "Write simple solution",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    exit_code = main()
    assert exit_code == 0
