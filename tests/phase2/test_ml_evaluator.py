import pytest
from anse.symbolic.ml_sandbox import MLExecutionResult
from anse.symbolic.ml_evaluator import MLEnergyEvaluator
from anse.symbolic.performance_evaluator import PerformanceCategory

@pytest.fixture
def evaluator():
    return MLEnergyEvaluator()

class TestMLEnergyEvaluator:
    def test_shape_mismatch_max_pain(self, evaluator):
        result = MLExecutionResult(
            stdout="",
            stderr="RuntimeError: mat1 and mat2 shapes cannot be multiplied (2000x20 and 15x64)",
            returncode=1,
            timed_out=False,
            duration_ms=100.0,
            tier_used=1,
            is_shape_mismatch=True
        )
        energy = evaluator.evaluate(result)
        assert energy.category == PerformanceCategory.CRASH
        assert energy.score == 1000.0
        assert "MAXIMUM PAIN" in energy.pain_signal

    def test_parameter_exceedance(self, evaluator):
        result = MLExecutionResult(
            stdout="",
            stderr="",
            returncode=0,
            timed_out=False,
            duration_ms=500.0,
            tier_used=1,
            parameters=75000,
            accuracy=0.96,
            val_loss=0.04
        )
        energy = evaluator.evaluate(result)
        assert energy.category == PerformanceCategory.INEFFICIENT
        assert energy.score == 25000.0  # 75000 - 50000
        assert "Memory Limit Exceeded" in energy.pain_signal
        assert not energy.is_valid

    def test_low_accuracy_moderate_pain(self, evaluator):
        result = MLExecutionResult(
            stdout="",
            stderr="",
            returncode=0,
            timed_out=False,
            duration_ms=500.0,
            tier_used=1,
            parameters=10000,
            accuracy=0.80,
            val_loss=0.65
        )
        energy = evaluator.evaluate(result)
        assert energy.category == PerformanceCategory.MODERATE
        assert energy.score == 0.65
        assert "Accuracy too low" in energy.pain_signal
        assert energy.is_valid

    def test_optimized_success(self, evaluator):
        result = MLExecutionResult(
            stdout="",
            stderr="",
            returncode=0,
            timed_out=False,
            duration_ms=500.0,
            tier_used=1,
            parameters=15000,
            accuracy=0.97,
            val_loss=0.08
        )
        energy = evaluator.evaluate(result)
        assert energy.category == PerformanceCategory.OPTIMIZED
        assert energy.score == 0.08
        assert "OPTIMIZED model successfully discovered" in energy.pain_signal
        assert energy.is_valid
