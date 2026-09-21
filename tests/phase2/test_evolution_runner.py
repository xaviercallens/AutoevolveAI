"""
Tests for run_phase2_evolution.py: it refuses to run on too little verified data,
and a complete (tiny) run honours the results contract rendered by the web tab.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pytest
import torch

import run_phase2_evolution as runner

DIM = 20


def _args(tmp_path: Path, traces: list[Path], **overrides: Any) -> argparse.Namespace:
    values: dict[str, Any] = dict(
        traces=[str(p) for p in traces], seeds=[1, 2], folds=2, min_traces=12, epochs=3, batch_size=8,
        lr=1e-3, weight_decay=0.05, dropout=0.2, d_hidden=8, d_latent=4, energy_weight=10.0,
        ridge_alpha=1.0, threads=1, uc=["1", "2", "3", "4", "5"], out=str(tmp_path / "out"),
    )
    values.update(overrides)
    return argparse.Namespace(**values)


def _traces(path: Path, n_tasks: int, verified: bool = True) -> Path:
    """Each task: one run that fails then passes, and one run that passes first time."""
    generator = torch.Generator().manual_seed(21)
    lines = []
    for t in range(n_tasks):
        for iteration, energy in ((1, 60.0), (2, 0.0), (1, 0.0)):
            h = torch.randn(DIM, generator=generator)
            h[0] += 3.0 if energy > 0 else -3.0
            lines.append(json.dumps({
                "task": f"Write function number {t}", "iteration": iteration, "energy": energy,
                "code": f"def f{t}():\n    return {len(lines)}", "hidden_state": h.tolist(),
                "metadata": {"tests_total": 5, "tests_passed": 5 if energy == 0 else 2} if verified else {},
            }))
    path.write_text("\n".join(lines) + "\n")
    return path


class TestInsufficientData:
    def test_too_few_traces_fails_with_a_clear_message_and_writes_nothing(self, tmp_path: Path) -> None:
        traces = _traces(tmp_path / "few.jsonl", n_tasks=2)
        with pytest.raises(runner.InsufficientDataError, match=r"only 6 usable verified traces over 2 tasks \(need >= 30"):
            runner.Bench(_args(tmp_path, [traces], min_traces=30))

        assert not (tmp_path / "out").exists()

    def test_self_graded_traces_do_not_count_as_usable(self, tmp_path: Path) -> None:
        traces = _traces(tmp_path / "legacy.jsonl", n_tasks=8, verified=False)
        with pytest.raises(runner.InsufficientDataError, match="only 0 usable verified traces") as excinfo:
            runner.Bench(_args(tmp_path, [traces]))

        assert "'unverified': 24" in str(excinfo.value)

    def test_missing_files_are_reported(self, tmp_path: Path) -> None:
        with pytest.raises(runner.InsufficientDataError, match="Files found: none"):
            runner.Bench(_args(tmp_path, [tmp_path / "absent.jsonl"]))
        assert not (tmp_path / "out" / "results.json").exists()


@pytest.fixture(scope="module")
def finished_run(tmp_path_factory: pytest.TempPathFactory) -> tuple[dict[str, Any], bool, runner.Bench]:
    tmp_path = tmp_path_factory.mktemp("phase2_runner")
    bench = runner.Bench(_args(tmp_path, [_traces(tmp_path / "traces.jsonl", n_tasks=6)]))
    bench.train_all()
    for step in (bench.uc1_beats_constant, bench.uc2_discrimination, bench.uc3_pairs_ablation,
                 bench.uc4_selection, bench.uc5_robustness):
        step()
    passed = bench.gate()
    return json.loads((tmp_path / "out" / "results.json").read_text()), passed, bench


class TestResultsContract:
    def test_top_level_keys(self, finished_run: tuple[dict[str, Any], bool, runner.Bench]) -> None:
        results, passed, _ = finished_run

        assert results["phase"] == 2
        assert isinstance(results["backend"], str) and "JEPA" in results["backend"]
        assert results["started"] <= results["finished"]
        assert len(results["gate"]) == 5
        assert all(isinstance(ok, bool) for ok in results["gate"].values())
        assert passed == all(results["gate"].values())

    def test_every_use_case_is_flat_with_rows(self, finished_run: tuple[dict[str, Any], bool, runner.Bench]) -> None:
        results, _, _ = finished_run
        scalar = (int, float, str, bool, type(None))
        for key in ("uc1", "uc2", "uc3", "uc4", "uc5"):
            uc = results[key]
            assert uc["title"] == runner.UC_META[key][0]
            assert uc["question"].endswith("?")
            assert isinstance(uc["rows"], list) and len(uc["rows"]) > 0
            for row in uc["rows"]:
                assert all(isinstance(v, scalar) for v in row.values()), f"{key} row is not flat: {row}"
            for name, value in uc.items():
                if name != "rows" and isinstance(value, dict):
                    assert all(isinstance(v, scalar) for v in value.values()), f"{key}.{name} nests too deep"

    def test_out_of_fold_predictions_cover_each_state_exactly_once(
        self, finished_run: tuple[dict[str, Any], bool, runner.Bench]
    ) -> None:
        results, _, bench = finished_run
        for seed in (1, 2):
            mixed = [r for r in bench.runs if r.seed == seed and r.arm == "mixed"]
            covered = sorted(i for r in mixed for i in r.val_states)
            assert covered == list(range(18))
            for run in mixed:
                held_out_tasks = {bench.ds.states[i].task for i in run.val_states}
                assert len(held_out_tasks) == 3
        assert [row["all_states_leaky"] for row in results["uc1"]["rows"]] == [18, 18]
        assert [row["first_attempt_states"] for row in results["uc1"]["rows"]] == [12, 12]

    def test_reported_numbers_are_recomputable_from_rows(self, finished_run: tuple[dict[str, Any], bool, runner.Bench]) -> None:
        results, _, _ = finished_run
        uc1, uc2, uc4 = results["uc1"], results["uc2"], results["uc4"]

        assert uc1["mae_jepa"] == pytest.approx(sum(r["mae_jepa"] for r in uc1["rows"]) / 2, abs=1e-3)
        assert uc2["verified_fail"] == 6 and uc2["verified_pass"] == 6
        assert uc2["all_states_fail"] == 6 and uc2["all_states_pass"] == 12
        assert uc2["auc_min"] == min(r["auc_jepa"] for r in uc2["rows"])
        assert uc4["tasks_with_2plus_distinct_candidates"] == 6
        assert uc4["decidable_only"]["random_pass_rate"] == pytest.approx(2.0 / 3.0, abs=1e-3)
        assert uc4["decidable_only"]["oracle_pass_rate"] == 1.0

    def test_uc3_refuses_to_conclude_on_too_few_transitions(self, finished_run: tuple[dict[str, Any], bool, runner.Bench]) -> None:
        results, _, _ = finished_run
        uc3 = results["uc3"]

        assert uc3["transition_pairs"] == 6
        assert uc3["enough_data"] is False
        assert uc3["conclusion"].startswith("INSUFFICIENT DATA: only 6 transition pairs")
        assert [ok for name, ok in results["gate"].items() if name.startswith("G3")] == [False]

    def test_uc5_checks_all_ran_against_real_behaviour(self, finished_run: tuple[dict[str, Any], bool, runner.Bench]) -> None:
        results, _, _ = finished_run
        rows = {row["check"]: row for row in results["uc5"]["rows"]}

        assert set(rows) == {"no_representation_collapse", "dimension_mismatch_raises", "nan_and_empty_states_skipped",
                             "predictions_within_0_100", "raw_embedding_predicts_like_training_input"}
        assert rows["raw_embedding_predicts_like_training_input"]["passed"] is True
        assert rows["raw_embedding_predicts_like_training_input"]["raw_norm_min"] > 1.5, "fixture states are not unit vectors"
        assert "refusing to pad or truncate" in rows["dimension_mismatch_raises"]["dataset_error"]
        assert rows["nan_and_empty_states_skipped"]["states_kept"] == 2
        assert 0.0 <= rows["predictions_within_0_100"]["min_prediction"] <= rows["predictions_within_0_100"]["max_prediction"] <= 100.0
        assert results["uc5"]["failures"] == sum(not row["passed"] for row in rows.values())


class TestLeakageAndReplication:
    """UC1/UC2 score first attempts only; retries leak their label and replays add nothing."""

    def test_scoring_uses_one_first_attempt_per_run_and_reports_the_leaky_baseline(
        self, finished_run: tuple[dict[str, Any], bool, runner.Bench]
    ) -> None:
        results, _, bench = finished_run

        assert results["n_first_attempt_states"] == 12 and results["n_states"] == 18
        assert all(bench.ds.states[i].iteration == 1 for i in bench.first)
        assert results["uc2"]["independent_tasks"] == 6
        # fixture: every iteration-2 state passes, so the iteration number alone is a (reversed) perfect cue
        assert results["uc2"]["auc_iteration_number_all_states"] == pytest.approx(0.25, abs=1e-3)
        assert [name for name in results["gate"] if "first-attempt" in name][:2] == [
            name for name in results["gate"] if name.startswith(("G1", "G2"))]

    def test_replayed_trace_file_changes_no_count(self, tmp_path: Path) -> None:
        single = _traces(tmp_path / "single.jsonl", n_tasks=6)
        doubled = tmp_path / "doubled.jsonl"
        doubled.write_text(single.read_text() * 3)
        bench = runner.Bench(_args(tmp_path, [doubled]))

        assert bench.results["n_states"] == 18
        assert bench.results["n_duplicate_traces_dropped"] == 36
        assert bench.results["n_first_attempt_states"] == 12

    def test_duplicates_cannot_satisfy_the_minimum_trace_guard(self, tmp_path: Path) -> None:
        single = _traces(tmp_path / "single.jsonl", n_tasks=2)
        replayed = tmp_path / "replayed.jsonl"
        replayed.write_text(single.read_text() * 10)  # 60 lines, 6 distinct traces

        with pytest.raises(runner.InsufficientDataError, match="only 6 usable verified traces") as excinfo:
            runner.Bench(_args(tmp_path, [replayed], min_traces=30))
        assert "'duplicate': 54" in str(excinfo.value)
