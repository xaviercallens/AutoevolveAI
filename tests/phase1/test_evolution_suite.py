"""The evolution task suite must be internally sound before it is used to judge a model."""

from collections import Counter
from pathlib import Path

import pytest
import yaml

from anse.memory.lessons import Lesson, LessonMemory
from anse.symbolic.evaluator import EnergyEvaluator
from anse.symbolic.hidden_tests import attach_harness, parse_report, strip_report
from anse.symbolic.sandbox import SandboxExecutor

SUITE = yaml.safe_load((Path(__file__).parents[2] / "tasks" / "phase1_evolution.yaml").read_text())["tasks"]


@pytest.mark.parametrize("task", SUITE, ids=[t["name"] for t in SUITE])
def test_reference_solution_passes_every_hidden_test(task):
    nonce = "ANSE-suitecheck"
    result = SandboxExecutor().execute(attach_harness(task["reference"], task["tests"], nonce), force_tier=1)
    report = parse_report(result.stdout, nonce)
    result.stdout = strip_report(result.stdout, nonce)
    assert report is not None, result.stderr
    assert report.failures == []
    assert report.passed == report.total == len(task["tests"])
    assert EnergyEvaluator().evaluate_hidden_tests(result, report).score == 0.0


def test_suite_is_balanced_two_train_and_two_test_tasks_per_family():
    counts = Counter((t["family"], t["split"]) for t in SUITE)
    assert len(SUITE) == 20
    assert set(counts.values()) == {2}
    assert len({t["name"] for t in SUITE}) == 20


def test_every_test_task_retrieves_a_lesson_from_its_own_family_first(tmp_path):
    memory = LessonMemory(tmp_path / "lessons.jsonl")
    family_of = {}
    for t in SUITE:
        if t["split"] == "train":
            memory.add(Lesson(task=t["task"], code=t["reference"]))
            family_of[t["task"]] = t["family"]
    for t in SUITE:
        if t["split"] == "test":
            hits = memory.retrieve(t["task"], k=2)
            assert hits, f"no lesson retrieved for {t['name']}"
            assert family_of[hits[0][1].task] == t["family"], t["name"]
