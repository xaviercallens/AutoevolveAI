"""
Unit tests for PerformanceEnergyEvaluator and PerformanceEnergyResult.
Verifies continuous computational physics energy calculation, correctness gate (E = ∞),
pain signal generation, and speedup tracking.
"""

import pytest
from anse.config import PerformanceConfig
from anse.symbolic.performance_evaluator import (
    PerformanceCategory,
    PerformanceEnergyEvaluator,
    PerformanceEnergyResult,
)
from anse.symbolic.sandbox import ExecutionResult


@pytest.fixture
def evaluator():
    cfg = PerformanceConfig(
        weight_time_ms=1.0,
        weight_peak_ram_mb=1.0,
        penalty_infinite_energy=1e6,
    )
    return PerformanceEnergyEvaluator(config=cfg)


def test_clean_execution_energy(evaluator):
    res = ExecutionResult(
        stdout="OK",
        stderr="",
        returncode=0,
        timed_out=False,
        duration_ms=45.5,
        tier_used=1,
        peak_ram_mb=12.5,
    )
    energy_res = evaluator.evaluate(res)
    assert energy_res.is_valid is True
    # E = 1.0 * 45.5 + 1.0 * 12.5 = 58.0
    assert energy_res.score == pytest.approx(58.0, abs=1e-3)
    assert energy_res.duration_ms == 45.5
    assert energy_res.peak_ram_mb == 12.5


def test_syntax_error_infinite_energy(evaluator):
    res = ExecutionResult(
        stdout="",
        stderr="File 'solution.py', line 1\n  def bad(:\n          ^\nSyntaxError: invalid syntax",
        returncode=1,
        timed_out=False,
        duration_ms=5.0,
        tier_used=1,
        peak_ram_mb=10.0,
    )
    energy_res = evaluator.evaluate(res)
    assert energy_res.is_valid is False
    assert energy_res.score == 1e6
    assert energy_res.category == PerformanceCategory.SYNTAX_ERROR
    assert "SYNTAX ERROR" in energy_res.pain_signal


def test_assertion_failure_infinite_energy(evaluator):
    res = ExecutionResult(
        stdout="Testing...",
        stderr="Traceback (most recent call last):\nAssertionError: Output mismatch!",
        returncode=1,
        timed_out=False,
        duration_ms=15.0,
        tier_used=1,
        peak_ram_mb=10.0,
    )
    energy_res = evaluator.evaluate(res)
    assert energy_res.is_valid is False
    assert energy_res.score == 1e6
    assert energy_res.category == PerformanceCategory.TEST_FAILURE
    assert "CORRECTNESS FAILURE" in energy_res.pain_signal


def test_runtime_crash_infinite_energy(evaluator):
    res = ExecutionResult(
        stdout="",
        stderr="ZeroDivisionError: division by zero",
        returncode=1,
        timed_out=False,
        duration_ms=8.0,
        tier_used=1,
        peak_ram_mb=10.0,
    )
    energy_res = evaluator.evaluate(res)
    assert energy_res.is_valid is False
    assert energy_res.score == 1e6
    assert energy_res.category == PerformanceCategory.CRASH


def test_timeout_infinite_energy(evaluator):
    res = ExecutionResult(
        stdout="",
        stderr="Execution timed out after 5.0s",
        returncode=-1,
        timed_out=True,
        duration_ms=5000.0,
        tier_used=1,
        peak_ram_mb=0.0,
    )
    energy_res = evaluator.evaluate(res)
    assert energy_res.is_valid is False
    assert energy_res.score == 1e6
    assert energy_res.category == PerformanceCategory.TIMEOUT


def test_expected_output_mismatch(evaluator):
    res = ExecutionResult(
        stdout="Wrong Result",
        stderr="",
        returncode=0,
        timed_out=False,
        duration_ms=20.0,
        tier_used=1,
        peak_ram_mb=10.0,
    )
    energy_res = evaluator.evaluate(res, expected_output="Expected Result")
    assert energy_res.is_valid is False
    assert energy_res.score == 1e6
    assert energy_res.category == PerformanceCategory.WRONG_OUTPUT


def test_baseline_comparison_and_speedup(evaluator):
    base_res = ExecutionResult(
        stdout="OK",
        stderr="",
        returncode=0,
        timed_out=False,
        duration_ms=500.0,
        tier_used=1,
        peak_ram_mb=25.0,
    )
    cand_res = ExecutionResult(
        stdout="OK",
        stderr="",
        returncode=0,
        timed_out=False,
        duration_ms=50.0,
        tier_used=1,
        peak_ram_mb=20.0,
    )
    energy_res = evaluator.evaluate(cand_res, baseline_result=base_res)
    assert energy_res.is_valid is True
    # Speedup: 500 / 50 = 10.0x
    assert energy_res.speedup_factor == pytest.approx(10.0, abs=1e-2)
    # Energy delta: (500 + 25) - (50 + 20) = 525 - 70 = 455
    assert energy_res.energy_delta == pytest.approx(455.0, abs=1e-2)
    assert energy_res.category == PerformanceCategory.VECTORIZED
    assert "PERFORMANCE REWARD" in energy_res.pain_signal


def test_inefficient_candidate_pain_signal(evaluator):
    base_res = ExecutionResult(
        stdout="OK",
        stderr="",
        returncode=0,
        timed_out=False,
        duration_ms=500.0,
        tier_used=1,
        peak_ram_mb=25.0,
    )
    cand_res = ExecutionResult(
        stdout="OK",
        stderr="",
        returncode=0,
        timed_out=False,
        duration_ms=480.0,
        tier_used=1,
        peak_ram_mb=26.0,
    )
    energy_res = evaluator.evaluate(cand_res, baseline_result=base_res)
    assert energy_res.is_valid is True
    assert energy_res.category == PerformanceCategory.INEFFICIENT
    assert "PERFORMANCE PAIN SIGNAL" in energy_res.pain_signal
    assert "replace sequential for-loops with NumPy" in energy_res.pain_signal
