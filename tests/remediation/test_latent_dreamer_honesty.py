"""P1-4: latent_dreamer must stop asserting outcomes it never measured."""

import inspect
import re
from pathlib import Path
from typing import Any

import pytest

from anse.core.latent_dreamer import (
    DEFAULT_JEPA_CHECKPOINT,
    HippocampalReplayEngine,
    SimulationRefusedError,
)


class _StubPredictor:
    """Carries loaded weights and returns two known scores in sequence."""

    def __init__(self, scores: list[float]) -> None:
        self.is_trained = True
        self._scores = list(scores)
        self.scored_batches: list[list[dict[str, Any]]] = []
        self.consolidate_calls: list[list[dict[str, Any]]] = []

    def score_replay_batch(self, traces: list[dict[str, Any]]) -> float:
        self.scored_batches.append(traces)
        return self._scores.pop(0)

    def consolidate(self, traces: list[dict[str, Any]]) -> None:
        self.consolidate_calls.append(traces)


def _make_engine_with_traces(
    tmp_path: Path, predictor: _StubPredictor | None = None
) -> HippocampalReplayEngine:
    memory_file = tmp_path / "hippocampus_replay.jsonl"
    engine = HippocampalReplayEngine(memory_file=memory_file, predictor=predictor)
    engine.log_wake_episode("physics", "prompt-a", "summary-a", energy=1.0)
    engine.log_wake_episode("math", "prompt-b", "summary-b", energy=2.0)
    engine.log_wake_episode("chemistry", "prompt-c", "summary-c", energy=3.0)
    return engine


def test_execute_sleep_cycle_raises_without_trained_predictor(tmp_path: Path) -> None:
    engine = _make_engine_with_traces(tmp_path, predictor=None)

    with pytest.raises(SimulationRefusedError, match=re.escape(str(DEFAULT_JEPA_CHECKPOINT))) as exc_info:
        engine.execute_sleep_cycle()

    assert ".pt" in str(exc_info.value)


def test_execute_sleep_cycle_reports_measured_retention_from_injected_scores(tmp_path: Path) -> None:
    predictor = _StubPredictor(scores=[0.8, 0.76])
    engine = _make_engine_with_traces(tmp_path, predictor=predictor)

    result = engine.execute_sleep_cycle(batch_size=1)

    assert result["measured_retention"] == pytest.approx(round(0.76 / 0.8, 4))
    assert result["measured_retention"] != 1.0
    assert "catastrophic_forgetting_prevented" not in result

    # The arithmetic must come from a real before/after comparison on data
    # distinct from what was consolidated, not a constant.
    assert len(predictor.scored_batches) == 2
    assert len(predictor.consolidate_calls) == 1
    held_out_ids = {t["trace_id"] for t in predictor.scored_batches[0]}
    consolidated_ids = {t["trace_id"] for t in predictor.consolidate_calls[0]}
    assert held_out_ids
    assert consolidated_ids
    assert held_out_ids.isdisjoint(consolidated_ids)


def test_catastrophic_forgetting_literal_removed_from_source() -> None:
    source = inspect.getsource(HippocampalReplayEngine.execute_sleep_cycle)
    assert 'catastrophic_forgetting_prevented": True' not in source
    assert "'catastrophic_forgetting_prevented': True" not in source
