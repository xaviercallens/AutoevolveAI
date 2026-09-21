"""Evolution Lab data layer: defensive reading and normalisation of results files."""

import json
from pathlib import Path
from typing import Any

import pytest

from web.evolution_data import (
    GOALS,
    MAX_CELL_CHARS,
    PHASES,
    find_comparisons,
    load_all,
    load_phase,
    results_path,
)


def write_results(root: Path, phase: int, payload: Any) -> Path:
    path = results_path(phase, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")
    return path


def finished_phase2() -> dict[str, Any]:
    return {
        "phase": 2,
        "backend": "jepa-cpu",
        "started": "2026-09-21 08:00:00",
        "finished": "2026-09-21 08:30:00",
        "epochs": 3,
        "gate": {"G1 heldout error below baseline": True, "G2 no collapse": False},
        "uc1": {
            "title": "Energy forecast",
            "question": "Does the predictor beat a constant baseline on held-out code?",
            "mae_baseline": 0.4,
            "mae_evolved": 0.25,
            "rows": [{"sample": i, "predicted": i / 10, "actual": 0.5} for i in range(7)],
        },
    }


def test_missing_file_reports_missing_with_every_use_case_pending(tmp_path):
    phase = load_phase(2, tmp_path)
    assert phase["status"] == "missing"
    assert phase["use_cases"] == []
    assert phase["use_cases_pending"] == ["uc1", "uc2", "uc3", "uc4", "uc5"]
    assert phase["gate"] == [] and phase["error"] is None


def test_corrupt_json_reports_invalid_with_error_and_no_data(tmp_path):
    write_results(tmp_path, 3, '{"phase": 3, "uc1": {"rows": [')
    phase = load_phase(3, tmp_path)
    assert phase["status"] == "invalid"
    assert "not valid JSON" in phase["error"]
    assert phase["use_cases"] == [] and phase["backend"] is None


def test_json_that_is_not_an_object_is_invalid_not_a_crash(tmp_path):
    write_results(tmp_path, 1, [1, 2, 3])
    phase = load_phase(1, tmp_path)
    assert phase["status"] == "invalid"
    assert "expected an object" in phase["error"]


def test_partial_file_without_finished_is_running_and_lists_pending_use_cases(tmp_path):
    write_results(tmp_path, 2, {"phase": 2, "backend": "jepa-cpu", "started": "2026-09-21 08:00:00", "uc1": {"n": 4, "rows": []}})
    phase = load_phase(2, tmp_path)
    assert phase["status"] == "running"
    assert phase["finished"] is None
    assert [uc["id"] for uc in phase["use_cases"]] == ["uc1"]
    assert phase["use_cases_pending"] == ["uc2", "uc3", "uc4", "uc5"]
    assert phase["gate_total"] == 0


def test_finished_file_normalises_gate_backend_params_and_metrics(tmp_path):
    write_results(tmp_path, 2, finished_phase2())
    phase = load_phase(2, tmp_path)
    assert phase["status"] == "finished"
    assert (phase["backend"], phase["backend_kind"]) == ("jepa-cpu", "backend")
    assert phase["gate"] == [
        {"goal": "G1 heldout error below baseline", "passed": True},
        {"goal": "G2 no collapse", "passed": False},
    ]
    assert (phase["gate_passed"], phase["gate_total"]) == (1, 2)
    assert phase["params"] == {"epochs": 3}
    uc1 = phase["use_cases"][0]
    assert uc1["title"] == "Energy forecast"
    assert uc1["metrics"] == {"mae_baseline": 0.4, "mae_evolved": 0.25}
    assert uc1["rows_total"] == 7 and uc1["rows_truncated"] is False


def test_gate_value_that_is_not_literally_true_never_counts_as_pass(tmp_path):
    payload = finished_phase2()
    payload["gate"] = {"truthy string": "yes", "one": 1, "real": True}
    write_results(tmp_path, 2, payload)
    phase = load_phase(2, tmp_path)
    assert [g["passed"] for g in phase["gate"]] == [False, False, True]
    assert phase["gate_passed"] == 1


def test_rows_are_capped_and_total_is_reported(tmp_path):
    payload = finished_phase2()
    payload["uc1"]["rows"] = [{"i": i} for i in range(50)]
    write_results(tmp_path, 2, payload)
    uc1 = load_phase(2, tmp_path, max_rows=10)["use_cases"][0]
    assert len(uc1["rows"]) == 10
    assert uc1["rows_total"] == 50
    assert uc1["rows_truncated"] is True
    assert uc1["rows"][-1] == {"i": 9}


def test_nested_row_values_and_long_strings_become_bounded_text(tmp_path):
    payload = finished_phase2()
    payload["uc1"]["rows"] = [{"energies": [1.0, 0.0], "off": {"converged": True}, "code": "x" * (MAX_CELL_CHARS + 500)}, "bare"]
    payload["uc1"]["deep"] = {"inner": {"too": "deep"}}
    write_results(tmp_path, 2, payload)
    uc1 = load_phase(2, tmp_path)["use_cases"][0]
    row = uc1["rows"][0]
    assert row["energies"] == "[1.0, 0.0]"
    assert json.loads(row["off"]) == {"converged": True}
    assert row["code"].startswith("x" * MAX_CELL_CHARS) and row["code"].endswith("[500 more chars]")
    assert uc1["rows"][1] == {"value": "bare"}
    assert uc1["metrics"]["deep"] == {"inner": '{"too": "deep"}'}


def test_phase1_titles_fall_back_to_defaults_but_file_titles_win(tmp_path):
    write_results(tmp_path, 1, {"phase": 1, "model": "qwen2.5-coder:1.5b", "uc1": {"runs": 2, "rows": []}, "uc5": {"title": "Custom", "question": "Q?", "rows": []}})
    phase = load_phase(1, tmp_path)
    by_id = {uc["id"]: uc for uc in phase["use_cases"]}
    assert by_id["uc1"]["title"] == "Honest energy"
    assert by_id["uc1"]["question"].endswith("?")
    assert (by_id["uc5"]["title"], by_id["uc5"]["question"]) == ("Custom", "Q?")
    assert (phase["backend"], phase["backend_kind"]) == ("qwen2.5-coder:1.5b", "model")


def test_phase_without_defaults_falls_back_to_use_case_id(tmp_path):
    write_results(tmp_path, 3, {"phase": 3, "uc2": {"rows": []}})
    uc2 = load_phase(3, tmp_path)["use_cases"][0]
    assert uc2["title"] == "UC2"
    assert uc2["question"] == ""


def test_comparisons_pair_scalars_and_flat_dicts_without_inventing_values():
    metrics = {
        "pass_at_1": 0.4,
        "pass_at_n": 0.7,
        "memory_off": {"pass_at_1": 0.3, "mean_iterations": 2.5, "note": "text"},
        "memory_on": {"pass_at_1": 0.5, "mean_iterations": 2.0, "note": "text"},
        "runs": 20,
    }
    comparisons = find_comparisons(metrics)
    as_pairs = {c["label"]: [(b["name"], b["value"]) for b in c["bars"]] for c in comparisons}
    assert as_pairs["pass_at_1 vs pass_at_n"] == [("pass_at_1", 0.4), ("pass_at_n", 0.7)]
    assert as_pairs["mean_iterations"] == [("memory_off", 2.5), ("memory_on", 2.0)]
    assert "note" not in as_pairs
    assert len(comparisons) == 3


def test_comparisons_ignore_booleans_and_unpaired_metrics():
    assert find_comparisons({"ok_before": True, "ok_after": False, "latency_parent": 3.0}) == []
    found = find_comparisons({"latency_parent_ms": 3.0, "latency_child_ms": 1.5})
    assert [b["value"] for b in found[0]["bars"]] == [3.0, 1.5]


def test_load_all_covers_every_phase_and_flags_running(tmp_path):
    write_results(tmp_path, 2, finished_phase2())
    everything = load_all(tmp_path)
    assert set(everything["phases"]) == {"1", "2", "3"}
    assert everything["phases"]["1"]["status"] == "missing"
    assert everything["any_running"] is False
    write_results(tmp_path, 3, {"phase": 3, "started": "now"})
    assert load_all(tmp_path)["any_running"] is True


def test_goals_describe_each_phase_with_the_five_step_workflow():
    assert set(GOALS) == set(PHASES)
    for phase in PHASES:
        assert len(GOALS[phase]["goal"]) > 100
        assert [s["step"] for s in GOALS[phase]["workflow"]][0] == "Baseline"
        assert len(GOALS[phase]["workflow"]) == 5


def test_unknown_phase_is_rejected_and_max_rows_is_clamped(tmp_path):
    with pytest.raises(ValueError, match="phase must be one of"):
        load_phase(9, tmp_path)
    payload = finished_phase2()
    write_results(tmp_path, 2, payload)
    assert len(load_phase(2, tmp_path, max_rows=0)["use_cases"][0]["rows"]) == 1
