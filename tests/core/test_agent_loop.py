import pytest
from unittest.mock import Mock, patch
from anse.core.agent_loop import AgentLoop, LoopSummary, PromptBudgetPolicy
from anse.symbolic.sandbox import ExecutionResult
from anse.symbolic.evaluator import EnergyResult, EnergyCategory

def test_banach_convergence_failure():
    # Mock extractor to always return a fake code
    mock_extractor = Mock()
    mock_extractor.extract.return_value = ("```python\nprint(1)\n```", Mock())
    
    # Mock sandbox to always return the same stderr length, ensuring non_shrink_count increments
    mock_sandbox = Mock()
    # A stderr that doesn't shrink across 4 iterations
    same_stderr = "This is a fake error trace that remains the same size"
    mock_sandbox.execute.return_value = ExecutionResult(
        returncode=1,
        stdout="",
        stderr=same_stderr,
        duration_ms=10.0,
        timed_out=False,
        tier_used=1,
        dangerous_imports=False
    )
    mock_sandbox._cfg = Mock(timeout_seconds=5.0)

    # Mock evaluator to return hard difficulty and non-converging energy
    mock_evaluator = Mock()
    energy_res = EnergyResult(score=45.0, category=EnergyCategory.RUNTIME_ERROR, pain_signal="Bad", execution=mock_sandbox.execute.return_value)
    mock_evaluator.evaluate.return_value = energy_res
    
    mock_harvester = Mock()
    mock_harvester.record = Mock()
    
    agent_loop = AgentLoop(
        extractor=mock_extractor,
        sandbox=mock_sandbox,
        evaluator=mock_evaluator,
        harvester=mock_harvester,
        lesson_memory=None,
        max_retries=4
    )
    
    # Needs to be "small" to trigger early stop
    agent_loop.is_small = True
    
    summary = agent_loop.run(task="mock task")
    
    # Iterations:
    # 1: len_delta N/A, non_shrink=0
    # 2: len_delta=0, non_shrink=1
    # 3: len_delta=0, non_shrink=2 -> triggers early stop
    assert summary.iterations == 3
    assert not summary.converged
