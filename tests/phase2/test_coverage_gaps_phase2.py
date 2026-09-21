"""Phase 2 coverage-completion tests: JEPA dataset edge cases, EMA, world-model config, perf loop."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import torch
import torch.nn as nn

from anse.config import JEPAConfig, MemoryConfig, ModelConfig
from anse.core.encoder import HiddenStateExtractor, HiddenStateRecord
from anse.core.performance_loop import PerformanceAgentLoop
from anse.jepa.dataset import JEPADataset
from anse.jepa.ema import ema_update
from anse.jepa.world_model import JEPAWorldModel
from anse.memory.harvester import Harvester
from anse.symbolic.performance_evaluator import PerformanceEnergyEvaluator
from anse.symbolic.sandbox import SandboxExecutor

# ─── JEPADataset ─────────────────────────────────────────────────────────────


def _write(path: Path, rows: list[object | str]) -> Path:
    path.write_text(
        "\n".join(r if isinstance(r, str) else json.dumps(r) for r in rows) + "\n",
        encoding="utf-8",
    )
    return path


def test_dataset_skips_blank_malformed_empty_and_non_numeric(tmp_path: Path) -> None:
    good = {"task": "t", "iteration": 1, "energy": 10.0, "hidden_state": [0.1] * 4}
    path = _write(
        tmp_path / "t.jsonl",
        [
            "",  # blank line
            "{not json",  # malformed
            {"task": "t", "iteration": 0, "energy": 5.0, "hidden_state": []},  # empty hs
            {"task": "t", "iteration": 0, "energy": 5.0},  # missing hs
            {"task": "t", "iteration": 0, "energy": 5.0, "hidden_state": ["a", "b"]},  # bad
            good,
        ],
    )
    ds = JEPADataset(path, hidden_dim=4)
    assert len(ds) >= 1
    ctx, tgt, energy = ds[0]
    assert ctx.shape == (4,) and tgt.shape == (4,)
    assert 0.0 <= float(energy) <= 1.0


def test_dataset_pads_and_truncates_to_hidden_dim(tmp_path: Path) -> None:
    short = {"task": "a", "iteration": 1, "energy": 1.0, "hidden_state": [1.0, 2.0]}
    long = {"task": "b", "iteration": 1, "energy": 1.0, "hidden_state": [1.0] * 10}
    ds = JEPADataset(_write(tmp_path / "t.jsonl", [short, long]), hidden_dim=6)
    for i in range(len(ds)):
        ctx, tgt, _ = ds[i]
        assert ctx.shape == (6,) and tgt.shape == (6,)
    assert ds._to_tensor([1.0, 2.0])[2:].abs().sum() == 0  # zero padding
    assert ds._to_tensor([1.0] * 10).shape == (6,)
    assert ds._to_tensor(["x"]) is None


def test_dataset_missing_file_is_empty(tmp_path: Path) -> None:
    assert len(JEPADataset(tmp_path / "nope.jsonl", hidden_dim=4)) == 0


# ─── EMA ─────────────────────────────────────────────────────────────────────


def test_ema_update_is_convex_combination_and_validates_tau() -> None:
    tgt, src = nn.Linear(2, 2), nn.Linear(2, 2)
    before = [p.detach().clone() for p in tgt.parameters()]
    ema_update(tgt, src, tau=0.75)
    for p_t, p_b, p_s in zip(tgt.parameters(), before, src.parameters()):
        assert torch.allclose(p_t, 0.75 * p_b + 0.25 * p_s, atol=1e-6)
        assert p_t.requires_grad and p_t.grad is None
    for bad in (0.0, -0.1, 1.5):
        with pytest.raises(ValueError):
            ema_update(tgt, src, tau=bad)


# ─── JEPAWorldModel.from_config ──────────────────────────────────────────────


def test_world_model_from_config() -> None:
    wm = JEPAWorldModel.from_config(
        ModelConfig(hidden_dim=16), JEPAConfig(hidden_dim=8, latent_dim=4)
    )
    assert wm.predict_energy_scalar(torch.zeros(16)) == pytest.approx(
        wm.predict_energy_scalar(torch.zeros(16))
    )


# ─── PerformanceAgentLoop JEPA metadata ──────────────────────────────────────


def _perf_loop(world_model, tmp_path: Path) -> PerformanceAgentLoop:
    cfg = MemoryConfig(
        persist_directory=tmp_path / "chroma", interactions_log=tmp_path / "log.jsonl"
    )
    return PerformanceAgentLoop(
        extractor=HiddenStateExtractor(mock_mode=True),
        sandbox=SandboxExecutor(),
        evaluator=PerformanceEnergyEvaluator(),
        harvester=Harvester(config=cfg, enable_chroma=False),
        world_model=world_model,
    )


def test_perf_loop_metadata_jepa_success_and_failure(tmp_path: Path) -> None:
    exec_res = SandboxExecutor().execute("print(1)")
    hs = HiddenStateRecord(
        hidden_state=torch.ones(1, 8), layer_indices=[-1], token_count=1,
        model_id="mock", device="mock",
    )
    energy_res = MagicMock(
        duration_ms=1.0, peak_ram_mb=2.0, speedup_factor=1.0, energy_delta=0.0,
        is_valid=True, score=5.0,
    )
    wm = MagicMock()
    wm.predict_energy_scalar.return_value = 9.0
    meta = _perf_loop(wm, tmp_path)._build_perf_trace_metadata(hs, exec_res, energy_res, 4.0)
    assert meta["jepa_predicted_energy"] == 9.0 and meta["jepa_surprise"] == 4.0

    wm.predict_energy_scalar.side_effect = RuntimeError("no jepa")
    meta = _perf_loop(wm, tmp_path)._build_perf_trace_metadata(hs, exec_res, energy_res, 4.0)
    assert meta["jepa_error"] == "no jepa"

    meta = _perf_loop(None, tmp_path)._build_perf_trace_metadata(hs, exec_res, energy_res, 4.0)
    assert "jepa_predicted_energy" not in meta and "jepa_error" not in meta


# ─── PerformanceEnergyEvaluator._categorize_performance ──────────────────────


@pytest.mark.parametrize(
    "speedup,duration,base,expected",
    [
        (6.0, 100.0, 100.0, "VECTORIZED"),
        (1.0, 10.0, 100.0, "VECTORIZED"),  # <15% of baseline duration
        (2.5, 100.0, 100.0, "OPTIMIZED"),
        (1.2, 100.0, 100.0, "MODERATE"),
        (1.0, 100.0, 100.0, "INEFFICIENT"),
        (None, 10.0, 0.0, "OPTIMIZED"),
        (None, 80.0, 0.0, "INEFFICIENT"),
    ],
)
def test_categorize_performance_all_branches(speedup, duration, base, expected) -> None:
    from anse.symbolic.performance_evaluator import PerformanceCategory

    got = PerformanceEnergyEvaluator()._categorize_performance(speedup, duration, base)
    assert got is PerformanceCategory[expected]


def test_dataset_normalise_false_and_zero_vector(tmp_path: Path) -> None:
    rows = [{"task": "a", "iteration": 1, "energy": 1.0, "hidden_state": [3.0, 4.0]}]
    raw = JEPADataset(_write(tmp_path / "r.jsonl", rows), hidden_dim=2, normalise=False)
    assert torch.equal(raw._to_tensor([3.0, 4.0]), torch.tensor([3.0, 4.0]))
    normed = JEPADataset(_write(tmp_path / "n.jsonl", rows), hidden_dim=2, normalise=True)
    assert float(normed._to_tensor([3.0, 4.0]).norm()) == pytest.approx(1.0)
    zero = normed._to_tensor([0.0, 0.0])  # norm == 0 -> left untouched, no NaN
    assert torch.equal(zero, torch.zeros(2))


def test_performance_evaluator_matching_expected_output_is_not_wrong() -> None:
    from anse.symbolic.performance_evaluator import PerformanceCategory

    res = SandboxExecutor().execute("print('same')")
    out = PerformanceEnergyEvaluator().evaluate(res, expected_output="same")
    assert out.category is not PerformanceCategory.WRONG_OUTPUT
    assert out.is_valid is True
