"""Tests for AgentLoop and pain-signal injection."""

from unittest.mock import MagicMock
import pytest

from anse.config import ANSEConfig
from anse.core.agent_loop import AgentLoop
from anse.core.encoder import HiddenStateExtractor, HiddenStateRecord
from anse.memory.harvester import Harvester
from anse.symbolic.evaluator import EnergyCategory, EnergyEvaluator
from anse.symbolic.sandbox import ExecutionResult, SandboxExecutor


class MockExtractorSequential:
    """Mock extractor that returns different responses per attempt."""

    def __init__(self, responses: list[str]):
        self.responses = responses
        self.calls = 0

    def extract(self, prompt: str, system_prompt: str | None = None):
        resp = self.responses[min(self.calls, len(self.responses) - 1)]
        self.calls += 1
        record = MagicMock(spec=HiddenStateRecord)
        record.to_embedding.return_value = [0.0] * 64
        record.model_id = "mock-seq"
        return resp, record


def test_agent_loop_immediate_convergence(tmp_path):
    # Response produces energy 0 (asserts pass)
    code = "```python\nassert 1 + 1 == 2\n```"
    extractor = MockExtractorSequential([code])
    harvester = Harvester(enable_chroma=False)
    harvester.log_path = tmp_path / "interactions.jsonl"

    loop = AgentLoop(
        extractor=extractor,
        harvester=harvester,
        max_retries=3,
        convergence_threshold=5.0,
    )

    summary = loop.run("Simple task")
    assert summary.converged is True
    assert summary.iterations == 1
    assert summary.final_energy == 0.0
    assert len(summary.traces) == 1


def test_agent_loop_retry_and_converge(tmp_path):
    # First response fails with ZeroDivisionError, second succeeds
    code_bad = "```python\nx = 1 / 0\n```"
    code_good = "```python\nassert 2 * 2 == 4\n```"
    extractor = MockExtractorSequential([code_bad, code_good])

    harvester = Harvester(enable_chroma=False)
    harvester.log_path = tmp_path / "interactions.jsonl"

    loop = AgentLoop(
        extractor=extractor,
        harvester=harvester,
        max_retries=3,
        convergence_threshold=5.0,
    )

    summary = loop.run("Task that needs retry")
    assert summary.converged is True
    assert summary.iterations == 2
    assert summary.traces[0].energy == 60.0  # ZeroDivisionError
    assert summary.traces[1].energy == 0.0   # Converged
    assert "PAIN SIGNAL" in summary.traces[1].prompt
    assert "ZeroDivisionError" in summary.traces[1].prompt


def test_agent_loop_exhaust_retries(tmp_path):
    # Code always fails
    code_fail = "```python\nassert False, 'Never works'\n```"
    extractor = MockExtractorSequential([code_fail])

    harvester = Harvester(enable_chroma=False)
    harvester.log_path = tmp_path / "interactions.jsonl"

    loop = AgentLoop(
        extractor=extractor,
        harvester=harvester,
        max_retries=3,
        convergence_threshold=5.0,
    )

    summary = loop.run("Failing task")
    assert summary.converged is False
    assert summary.iterations == 3
    assert summary.final_energy == 50.0  # Test failure
    assert harvester.get_trace_count() == 3


def test_agent_loop_custom_convergence_threshold(tmp_path):
    # Code has no asserts (energy = 5.0)
    code_no_tests = "```python\nprint('Done without asserts')\n```"
    extractor = MockExtractorSequential([code_no_tests])

    harvester = Harvester(enable_chroma=False)
    harvester.log_path = tmp_path / "interactions.jsonl"

    # Strict threshold 0.0 -> does NOT converge on 5.0
    loop_strict = AgentLoop(
        extractor=extractor,
        harvester=harvester,
        max_retries=2,
        convergence_threshold=0.0,
    )
    s_strict = loop_strict.run("No asserts task")
    assert s_strict.converged is False
    assert s_strict.final_energy == 5.0

    # Relaxed threshold 10.0 -> CONVERGES on 5.0
    loop_relaxed = AgentLoop(
        extractor=extractor,
        harvester=harvester,
        max_retries=2,
        convergence_threshold=10.0,
    )
    s_relaxed = loop_relaxed.run("No asserts task")
    assert s_relaxed.converged is True
    assert s_relaxed.final_energy == 5.0

