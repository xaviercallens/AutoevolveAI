"""Tests for EnergyEvaluator and energy mapping."""

import pytest

from anse.symbolic.evaluator import EnergyCategory, EnergyEvaluator
from anse.symbolic.sandbox import ExecutionResult


@pytest.fixture
def evaluator():
    return EnergyEvaluator()


def test_evaluator_perfect(evaluator):
    # Has asserts and clean run
    code = "assert 1 + 1 == 2\nprint('Done')"
    result = ExecutionResult(
        stdout="Done\n",
        stderr="",
        returncode=0,
        timed_out=False,
        duration_ms=50.0,
        tier_used=1,
    )
    res = evaluator.evaluate(result, code=code)
    assert res.score == 0.0
    assert res.category == EnergyCategory.PERFECT


def test_evaluator_no_tests(evaluator):
    # No asserts in code, clean run
    code = "print('Done')"
    result = ExecutionResult(
        stdout="Done\n",
        stderr="",
        returncode=0,
        timed_out=False,
        duration_ms=50.0,
        tier_used=1,
    )
    res = evaluator.evaluate(result, code=code)
    assert res.score == 5.0
    assert res.category == EnergyCategory.NO_TESTS


def test_evaluator_wrong_output(evaluator):
    code = "print('42')"
    result = ExecutionResult(
        stdout="42\n",
        stderr="",
        returncode=0,
        timed_out=False,
        duration_ms=50.0,
        tier_used=1,
    )
    res = evaluator.evaluate(result, code=code, expected_output="100")
    assert res.score == 30.0
    assert res.category == EnergyCategory.WRONG_OUTPUT


def test_evaluator_test_failure(evaluator):
    code = "assert False, 'Test failed'"
    result = ExecutionResult(
        stdout="",
        stderr="Traceback ... AssertionError: Test failed",
        returncode=1,
        timed_out=False,
        duration_ms=50.0,
        tier_used=1,
    )
    res = evaluator.evaluate(result, code)
    assert res.score == 50.0
    assert res.category == EnergyCategory.TEST_FAILURE


def test_evaluator_runtime_error(evaluator):
    code = "x = 1 / 0"
    result = ExecutionResult(
        stdout="",
        stderr="Traceback ... ZeroDivisionError: division by zero",
        returncode=1,
        timed_out=False,
        duration_ms=50.0,
        tier_used=1,
    )
    res = evaluator.evaluate(result, code)
    assert res.score == 60.0
    assert res.category == EnergyCategory.RUNTIME_ERROR


def test_evaluator_timeout(evaluator):
    code = "while True: pass"
    result = ExecutionResult(
        stdout="",
        stderr="Process timed out",
        returncode=124,
        timed_out=True,
        duration_ms=10000.0,
        tier_used=1,
    )
    res = evaluator.evaluate(result, code)
    assert res.score == 80.0
    assert res.category == EnergyCategory.TIMEOUT


def test_evaluator_syntax_error(evaluator):
    code = "def foo("
    result = ExecutionResult(
        stdout="",
        stderr="SyntaxError: unexpected EOF while parsing",
        returncode=1,
        timed_out=False,
        duration_ms=10.0,
        tier_used=1,
    )
    res = evaluator.evaluate(result, code)
    assert res.score == 100.0
    assert res.category == EnergyCategory.SYNTAX_ERROR


def test_evaluator_import_error(evaluator):
    code = "import some_nonexistent_module"
    result = ExecutionResult(
        stdout="",
        stderr="Traceback ... ModuleNotFoundError: No module named 'some_nonexistent_module'",
        returncode=1,
        timed_out=False,
        duration_ms=10.0,
        tier_used=1,
    )
    res = evaluator.evaluate(result, code)
    assert res.score == 40.0
    assert res.category == EnergyCategory.IMPORT_ERROR


def test_global_evaluate_energy():
    from anse.symbolic.evaluator import evaluate_energy
    
    code = "assert 1 + 1 == 2\nprint('Done')"
    result = ExecutionResult(
        stdout="Done\n",
        stderr="",
        returncode=0,
        timed_out=False,
        duration_ms=50.0,
        tier_used=1,
    )
    res = evaluate_energy(result, code=code)
    assert res.score == 0.0
    assert res.category == EnergyCategory.PERFECT
