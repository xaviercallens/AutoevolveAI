import pytest
from anse.symbolic.parser import check_complexity_floor
from anse.core.agent_loop import AgentLoop
from anse.symbolic.evaluator import EnergyResult, EnergyCategory
from anse.symbolic.sandbox import ExecutionResult
from unittest.mock import Mock

def test_check_complexity_floor():
    trivial_code = "return 42"
    assert not check_complexity_floor(trivial_code, min_complexity=3)

    simple_code = """
def foo(x):
    if x > 0:
        return 1
    else:
        return 2
"""
    assert not check_complexity_floor(simple_code, min_complexity=3)

    complex_code = """
def bar(y):
    if y > 10:
        for i in range(y):
            if i % 2 == 0:
                print(i)
    while y > 0:
        try:
            assert y != 5
        except AssertionError:
            pass
        y -= 1
"""
    assert check_complexity_floor(complex_code, min_complexity=5)

def test_agent_loop_trivial_simulation():
    # Mock extractor
    mock_extractor = Mock()
    mock_extractor.extract.return_value = ("```python\nreturn 42\n```", Mock())

    # Mock sandbox
    mock_sandbox = Mock()
    # Shouldn't be called on iter 2
    
    # Mock evaluator
    mock_evaluator = Mock()
    
    # Iteration 1 will execute normally and get a "hard" result
    exec_res_iter1 = ExecutionResult(returncode=1, stdout="", stderr="Error", duration_ms=10.0, timed_out=False, tier_used=1)
    energy_res_iter1 = EnergyResult(score=45.0, category=EnergyCategory.RUNTIME_ERROR, pain_signal="Bad", execution=exec_res_iter1)
    
    # On iteration 2, it should synthesize the TRIVIAL_SIMULATION error directly.
    # The evaluator should evaluate it as TRIVIAL_SIMULATION.
    exec_res_synthesized = ExecutionResult(
        stdout="",
        stderr="TRIVIAL_SIMULATION: cyclomatic complexity below floor",
        returncode=2,
        timed_out=False,
        duration_ms=0.0,
        tier_used=1,
    )
    energy_res_iter2 = EnergyResult(score=1000000.0, category=EnergyCategory.TRIVIAL_SIMULATION, pain_signal="Trivial", execution=exec_res_synthesized)
    
    mock_sandbox.execute.side_effect = [exec_res_iter1]
    mock_evaluator.evaluate.side_effect = [energy_res_iter1, energy_res_iter2]
    
    mock_harvester = Mock()
    mock_harvester.record = Mock()
    
    agent_loop = AgentLoop(
        extractor=mock_extractor,
        sandbox=mock_sandbox,
        evaluator=mock_evaluator,
        harvester=mock_harvester,
        lesson_memory=None,
        max_retries=2
    )
    
    summary = agent_loop.run(task="mock task")
    assert mock_sandbox.execute.call_count == 1
    assert mock_evaluator.evaluate.call_count == 2
