"""Remediation tests for P1-4: latent_dreamer must stop asserting outcomes it never measured.

Verifies that HippocampalReplayEngine.execute_sleep_cycle refuses to run without a trained
predictor and, when one is present, derives its retention figure from a real held-out
comparison rather than returning a hardcoded 'catastrophic_forgetting_prevented': True.
Also verifies LatentDreamer.dream_and_search refuses to score random vectors through an
untrained JEPA predictor.
"""

import inspect
from pathlib import Path
from typing import Any

import pytest
import torch

from anse.core.latent_dreamer import (
    FastJEPALatentPredictor,
    HippocampalReplayEngine,
    LatentDreamer,
)
from anse.infrastructure.fabrication import SimulationRefusedError


class _StubPredictor:
    """Duck-typed predictor stub: returns two known scores, records call order and trace ids."""

    def __init__(self, before_score: float, after_score: float) -> None:
        self.is_loaded = True
        self.checkpoint_path = Path("stub_checkpoint.pt")
        self._scores = iter([before_score, after_score])
        self.consolidate_calls: list[list[dict[str, Any]]] = []
        self.call_log: list[tuple[str, tuple[str, ...]]] = []

    def evaluate(self, traces: list[dict[str, Any]]) -> float:
        self.call_log.append(("evaluate", tuple(t["trace_id"] for t in traces)))
        return next(self._scores)

    def consolidate(self, traces: list[dict[str, Any]]) -> None:
        self.consolidate_calls.append(traces)
        self.call_log.append(("consolidate", tuple(t["trace_id"] for t in traces)))


def _log_traces(engine: HippocampalReplayEngine, count: int) -> None:
    for i in range(count):
        engine.log_wake_episode(
            domain="lean4",
            prompt=f"prompt-{i}",
            thought_summary=f"summary-{i}",
            energy=1.0,
        )


def test_execute_sleep_cycle_refuses_without_trained_predictor(tmp_path: Path) -> None:
    memory_file = tmp_path / "hippocampus.jsonl"
    engine = HippocampalReplayEngine(memory_file=memory_file)

    with pytest.raises(SimulationRefusedError, match="checkpoint") as exc_info:
        engine.execute_sleep_cycle(batch_size=8)

    assert "latent_dreamer_jepa.pt" in str(exc_info.value)
    assert exc_info.value.component == "HippocampalReplayEngine.execute_sleep_cycle"


def test_execute_sleep_cycle_retention_is_derived_from_replay_comparison(tmp_path: Path) -> None:
    memory_file = tmp_path / "hippocampus.jsonl"
    stub = _StubPredictor(before_score=0.8, after_score=0.4)
    engine = HippocampalReplayEngine(memory_file=memory_file, predictor=stub)

    # 4 traces logged, batch_size=1 -> replay_batch is the last trace only,
    # leaving the first 3 traces as a disjoint held-out set.
    _log_traces(engine, count=4)

    result = engine.execute_sleep_cycle(batch_size=1)

    assert result["retention_score"] == 0.5
    assert result["held_out_size"] == 3
    assert len(stub.consolidate_calls) == 1
    assert len(stub.consolidate_calls[0]) == 1

    # Call order must be evaluate (before) -> consolidate -> evaluate (after),
    # and the evaluated (held-out) ids must never overlap the consolidated (replay) ids.
    call_kinds = [kind for kind, _ in stub.call_log]
    assert call_kinds == ["evaluate", "consolidate", "evaluate"]
    evaluated_ids = set(stub.call_log[0][1]) | set(stub.call_log[2][1])
    consolidated_ids = set(stub.call_log[1][1])
    assert evaluated_ids.isdisjoint(consolidated_ids)


def test_catastrophic_forgetting_literal_true_is_gone() -> None:
    source = inspect.getsource(HippocampalReplayEngine.execute_sleep_cycle)

    assert '"catastrophic_forgetting_prevented": True' not in source
    assert "'catastrophic_forgetting_prevented': True" not in source


def test_dream_and_search_refuses_untrained_predictor(tmp_path: Path) -> None:
    missing_checkpoint = tmp_path / "never_trained.pt"
    dreamer = LatentDreamer(latent_dim=8, num_branches=4, checkpoint_path=missing_checkpoint)

    with pytest.raises(SimulationRefusedError, match="checkpoint") as exc_info:
        dreamer.dream_and_search("optimize the hot loop")

    assert str(missing_checkpoint) in str(exc_info.value)
    assert exc_info.value.component == "LatentDreamer.dream_and_search"


def test_dream_and_search_runs_with_a_real_loaded_checkpoint(tmp_path: Path) -> None:
    checkpoint_path = tmp_path / "trained.pt"
    torch.save(FastJEPALatentPredictor(latent_dim=8).state_dict(), checkpoint_path)

    dreamer = LatentDreamer(latent_dim=8, num_branches=4, checkpoint_path=checkpoint_path)
    assert dreamer.predictor.is_loaded is True

    no_baseline = dreamer.dream_and_search("optimize the hot loop")
    assert no_baseline.speedup_vs_sandbox is None

    with_baseline = dreamer.dream_and_search("optimize the hot loop", sandbox_baseline_ms=5000.0)
    assert with_baseline.speedup_vs_sandbox is not None
    assert with_baseline.speedup_vs_sandbox > 0.0
