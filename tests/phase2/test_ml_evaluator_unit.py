from __future__ import annotations

import pytest

from anse.symbolic.ml_evaluator import MLEnergyEvaluator
from anse.symbolic.ml_sandbox import MLExecutionResult
from anse.symbolic.performance_evaluator import PerformanceCategory


@pytest.fixture
def evaluator() -> MLEnergyEvaluator:
    return MLEnergyEvaluator()


def test_evaluate_timeout(evaluator: MLEnergyEvaluator) -> None:
    result = MLExecutionResult(
        stdout="", stderr="", returncode=-1, timed_out=True, duration_ms=100.0, tier_used=1, peak_ram_mb=0.0
    )
    energy = evaluator.evaluate(result)
    assert energy.is_valid is False
    assert energy.category == PerformanceCategory.TIMEOUT
    assert energy.score == evaluator.max_pain


def test_evaluate_syntax_error(evaluator: MLEnergyEvaluator) -> None:
    result = MLExecutionResult(
        stdout="",
        stderr="SyntaxError: invalid syntax",
        returncode=1,
        timed_out=False,
        duration_ms=10.0,
        tier_used=1,
        peak_ram_mb=0.0
    )
    energy = evaluator.evaluate(result)
    assert energy.is_valid is False
    assert energy.category == PerformanceCategory.SYNTAX_ERROR
    assert "COMPUTATIONAL CRASH (SYNTAX ERROR)" in energy.pain_signal


def test_evaluate_shape_mismatch(evaluator: MLEnergyEvaluator) -> None:
    result = MLExecutionResult(
        stdout="",
        stderr="size mismatch",
        returncode=1,
        timed_out=False,
        duration_ms=20.0,
        tier_used=1,
        peak_ram_mb=0.0,
        is_shape_mismatch=True
    )
    energy = evaluator.evaluate(result)
    assert energy.is_valid is False
    assert energy.category == PerformanceCategory.CRASH
    assert "Tensor Shape Mismatch" in energy.pain_signal


def test_evaluate_oom(evaluator: MLEnergyEvaluator) -> None:
    result = MLExecutionResult(
        stdout="",
        stderr="CUDA out of memory",
        returncode=1,
        timed_out=False,
        duration_ms=20.0,
        tier_used=1,
        peak_ram_mb=0.0,
        is_oom=True
    )
    energy = evaluator.evaluate(result)
    assert energy.is_valid is False
    assert energy.category == PerformanceCategory.CRASH
    assert "Out of Memory" in energy.pain_signal


def test_evaluate_runtime_exception(evaluator: MLEnergyEvaluator) -> None:
    result = MLExecutionResult(
        stdout="",
        stderr="TypeError",
        returncode=1,
        timed_out=False,
        duration_ms=20.0,
        tier_used=1,
        peak_ram_mb=0.0
    )
    energy = evaluator.evaluate(result)
    assert energy.is_valid is False
    assert energy.category == PerformanceCategory.CRASH
    assert "Runtime exception raised" in energy.pain_signal


def test_evaluate_exceeds_max_params(evaluator: MLEnergyEvaluator) -> None:
    evaluator.max_params = 100
    result = MLExecutionResult(
        stdout="",
        stderr="",
        returncode=0,
        timed_out=False,
        duration_ms=50.0,
        tier_used=1,
        peak_ram_mb=0.0,
        parameters=150
    )
    energy = evaluator.evaluate(result)
    assert energy.is_valid is False
    assert energy.category == PerformanceCategory.INEFFICIENT
    assert energy.score == 50.0
    assert "Memory Limit Exceeded" in energy.pain_signal


def test_evaluate_low_accuracy(evaluator: MLEnergyEvaluator) -> None:
    evaluator.max_params = 100
    result = MLExecutionResult(
        stdout="",
        stderr="",
        returncode=0,
        timed_out=False,
        duration_ms=50.0,
        tier_used=1,
        peak_ram_mb=0.0,
        parameters=50,
        accuracy=0.8,
        val_loss=0.5
    )
    energy = evaluator.evaluate(result)
    assert energy.is_valid is True
    assert energy.category == PerformanceCategory.MODERATE
    assert energy.score == 0.5
    assert "Accuracy too low" in energy.pain_signal


def test_evaluate_optimized(evaluator: MLEnergyEvaluator) -> None:
    evaluator.max_params = 100
    result = MLExecutionResult(
        stdout="",
        stderr="",
        returncode=0,
        timed_out=False,
        duration_ms=50.0,
        tier_used=1,
        peak_ram_mb=0.0,
        parameters=50,
        accuracy=0.96,
        val_loss=0.1
    )
    energy = evaluator.evaluate(result)
    assert energy.is_valid is True
    assert energy.category == PerformanceCategory.OPTIMIZED
    assert energy.score == 0.1
    assert "Target accuracy achieved!" in energy.pain_signal
