"""Verdict importers: labels must come from the verifier, and only verifier-backed rows may enter."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[2]


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


harvest = _load("import_harvest_to_pool")
lean = _load("import_lean_verdicts_to_pool")
pending = _load("import_pending_verdicts")


def _row(passed: int, total: int) -> dict[str, Any]:
    return {
        "task": "harvest:hard-x",
        "hidden_state": [0.0] * 1024,
        "metadata": {"tests_total": total, "tests_passed": passed},
    }


@pytest.mark.parametrize(("passed", "total", "label"), [(3, 3, 0.0), (2, 3, 1.0), (0, 3, 1.0)])
def test_harvest_label_is_zero_only_when_every_assertion_passed(
    passed: int, total: int, label: float
) -> None:
    episode = harvest.binary_episode(_row(passed, total), "harvest_sandbox:x.jsonl")

    assert episode["energy"] == label
    assert episode["converged"] is (label == 0.0)


def test_harvest_row_with_no_assertions_is_not_labelled_a_pass() -> None:
    episode = harvest.binary_episode(_row(0, 0), "harvest_sandbox:x.jsonl")

    assert episode["energy"] == 1.0
    assert episode["metadata"]["tests_total"] == 0


def test_lean_verdicts_exclude_runs_where_the_compiler_never_ran() -> None:
    runs = [
        {
            "id": "a",
            "tier": "T1",
            "model": "m",
            "arm": "k0",
            "clean": "True",
            "compile_s": "12.0",
            "axioms": "['propext']",
            "proof_head": "by",
        },
        {
            "id": "b",
            "tier": "T1",
            "model": "m",
            "arm": "k0",
            "clean": "False",
            "axioms": "[]",
            "proof_head": "",
        },
        {
            "id": "c",
            "tier": "T1",
            "model": "m",
            "arm": "k0",
            "clean": "False",
            "compile_s": "None",
            "axioms": "[]",
            "proof_head": "",
        },
    ]

    kept = lean.verdict_rows(runs)

    assert [r["item"] for r in kept] == ["a"]
    assert kept[0]["clean"] is True


def test_lean_verdict_marks_a_failed_compile_as_not_clean() -> None:
    runs = [
        {
            "id": "x",
            "tier": "T2",
            "model": "m",
            "arm": "k5",
            "clean": "False",
            "compile_s": "3.1",
            "axioms": "['sorryAx']",
            "proof_head": "by sorry",
        }
    ]

    kept = lean.verdict_rows(runs)

    assert kept[0]["clean"] is False
    assert kept[0]["axioms"] == ["sorryAx"]


def test_only_hard_harvest_files_are_pending_so_the_uninformative_easy_set_is_excluded() -> None:
    names = [p.name for p in pending.pending_harvest_files()]

    assert all(name.startswith("harvest_hard_") for name in names)
    assert "harvest.jsonl" not in names
