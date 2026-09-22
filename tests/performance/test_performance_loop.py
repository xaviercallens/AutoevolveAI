"""
Integration tests for PerformanceAgentLoop.
Simulates candidate optimization cycles from slow loops to vectorized implementations.
"""

from unittest.mock import MagicMock

import pytest
import torch

from anse.config import ANSEConfig
from anse.core.encoder import HiddenStateRecord
from anse.core.performance_loop import PerformanceAgentLoop, PerformanceLoopSummary
from anse.memory.harvester import Harvester
from anse.symbolic.performance_evaluator import PerformanceEnergyEvaluator
from anse.symbolic.sandbox import SandboxExecutor


@pytest.fixture
def mock_extractor():
    extractor = MagicMock()
    return extractor


@pytest.fixture
def perf_loop(tmp_path, mock_extractor):
    cfg = ANSEConfig()
    cfg.memory.persist_directory = tmp_path / "chroma"
    cfg.memory.interactions_log = tmp_path / "interactions.jsonl"
    cfg.sandbox.timeout_seconds = 5.0
    cfg.sandbox.untrusted_requires_container = False

    sandbox = SandboxExecutor(config=cfg.sandbox)
    evaluator = PerformanceEnergyEvaluator(config=cfg.performance)
    harvester = Harvester(config=cfg.memory)

    return PerformanceAgentLoop(
        extractor=mock_extractor,
        sandbox=sandbox,
        evaluator=evaluator,
        harvester=harvester,
        config=cfg,
        max_retries=3,
        target_speedup=2.0,
    )


def test_performance_loop_immediate_convergence(perf_loop, mock_extractor):
    naive_code = """
def pairwise_sum(arr):
    N = len(arr)
    s = 0.0
    for i in range(N):
        for j in range(N):
            s += arr[i] * arr[j]
    return s
"""
    opt_code = """```python
import numpy as np
def pairwise_sum(arr):
    a = np.asarray(arr, dtype=np.float64)
    s = float(np.sum(a))
    return s * s
```"""
    test_harness = """
arr = [float(i % 100) for i in range(600)]
res = pairwise_sum(arr)
assert res > 0
print("OK")
"""

    mock_record = HiddenStateRecord(
        hidden_state=torch.zeros(1, 64),
        layer_indices=[-1],
        token_count=10,
        model_id="test-model",
        device="mock",
    )
    mock_extractor.extract.return_value = (opt_code, mock_record)

    summary = perf_loop.run_optimization(
        task="Optimize pairwise_sum",
        naive_code=naive_code,
        test_harness=test_harness,
        max_retries=2,
        target_speedup=2.0,
    )

    assert isinstance(summary, PerformanceLoopSummary)
    assert summary.converged is True
    assert summary.iterations == 1
    assert summary.final_energy < summary.initial_energy
    assert len(summary.traces) == 1
    assert summary.traces[0].converged is True


def test_performance_loop_multi_step_pain_to_reward(perf_loop, mock_extractor):
    naive_code = """
def pairwise_diff(A):
    N = len(A)
    diff = 0.0
    for i in range(N):
        for j in range(N):
            diff += abs(A[i] - A[j])
    return diff
"""
    # Attempt 1: Syntax error
    attempt1_code = "```python\ndef pairwise_diff(A:\n    return A\n```"
    # Attempt 2: Vectorized success
    attempt2_code = """```python
import numpy as np
def pairwise_diff(A):
    arr = np.asarray(A, dtype=np.float64)
    return float(np.sum(np.abs(arr[:, None] - arr[None, :])))
```"""
    test_harness = """
A = [float(i) for i in range(1200)]
res = pairwise_diff(A)
assert res > 0
print("OK")
"""

    record1 = HiddenStateRecord(
        hidden_state=torch.zeros(1, 64),
        layer_indices=[-1],
        token_count=5,
        model_id="test-model",
        device="mock",
    )
    record2 = HiddenStateRecord(
        hidden_state=torch.zeros(1, 64),
        layer_indices=[-1],
        token_count=15,
        model_id="test-model",
        device="mock",
    )

    mock_extractor.extract.side_effect = [
        (attempt1_code, record1),
        (attempt2_code, record2),
    ]

    summary = perf_loop.run_optimization(
        task="Optimize pairwise_diff",
        naive_code=naive_code,
        test_harness=test_harness,
        max_retries=2,
        target_speedup=2.0,
    )

    assert summary.converged is True
    assert summary.iterations == 2
    assert summary.traces[0].converged is False
    assert summary.traces[0].energy == 1e6  # Infinite energy penalty on syntax error
    assert summary.traces[1].converged is True
    assert summary.traces[1].energy < 1e6


def test_performance_loop_jepa_integration(tmp_path, mock_extractor):
    cfg = ANSEConfig()
    cfg.memory.persist_directory = tmp_path / "chroma"
    cfg.memory.interactions_log = tmp_path / "interactions.jsonl"
    cfg.sandbox.untrusted_requires_container = False

    mock_world_model = MagicMock()
    mock_world_model.predict_energy_scalar.return_value = 55.0

    perf_loop = PerformanceAgentLoop(
        extractor=mock_extractor,
        sandbox=SandboxExecutor(config=cfg.sandbox),
        evaluator=PerformanceEnergyEvaluator(config=cfg.performance),
        harvester=Harvester(config=cfg.memory),
        config=cfg,
        world_model=mock_world_model,
        max_retries=1,
    )

    code = "```python\ndef f(x): return x\n```"
    harness = "assert f(1) == 1\nprint('OK')"
    rec = HiddenStateRecord(
        hidden_state=torch.zeros(1, 64),
        layer_indices=[-1],
        token_count=6,
        model_id="test-model",
        device="mock",
    )
    mock_extractor.extract.return_value = (code, rec)

    summary = perf_loop.run_optimization(
        task="Trivial identity",
        naive_code="def f(x): return x",
        test_harness=harness,
        max_retries=1,
    )

    assert len(summary.traces) == 1
    meta = summary.traces[0].metadata
    assert "jepa_predicted_energy" in meta
    assert meta["jepa_predicted_energy"] == 55.0
    assert "jepa_surprise" in meta
