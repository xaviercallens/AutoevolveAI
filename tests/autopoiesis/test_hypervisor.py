import pytest

from anse.autopoiesis.hypervisor import BaselineMetrics, legacy_single_sample_rule
from anse.symbolic.performance_evaluator import PerformanceCategory, PerformanceEnergyResult
from anse.symbolic.sandbox import ExecutionResult


@pytest.fixture
def baseline():
    # Parent has 5.0 energy
    return BaselineMetrics(energy=5.0, duration_ms=400.0, peak_ram_mb=100.0)


class TestLegacySingleSampleRule:
    """The pre-evolution swap condition, kept as a pure function for comparison in Phase 3 UC2/UC3."""

    def test_hot_swap_authorized(self, baseline):
        # Child has 3.0 energy (better)
        child_result = PerformanceEnergyResult(
            score=3.0,
            category=PerformanceCategory.OPTIMIZED,
            is_valid=True,
            duration_ms=300.0,
            peak_ram_mb=80.0,
            execution=ExecutionResult("", "", 0, False, 300.0, 1, 80.0),
            pain_signal="",
            speedup_factor=1.3,
            memory_reduction_ratio=1.2,
            energy_delta=2.0,
            relative_energy=0.6,
        )
        assert legacy_single_sample_rule(child_result, baseline)

    def test_hot_swap_rejected_worse_energy(self, baseline):
        # Child has 6.0 energy (worse)
        child_result = PerformanceEnergyResult(
            score=6.0,
            category=PerformanceCategory.INEFFICIENT,
            is_valid=True,
            duration_ms=500.0,
            peak_ram_mb=120.0,
            execution=ExecutionResult("", "", 0, False, 500.0, 1, 120.0),
            pain_signal="",
            speedup_factor=0.8,
            memory_reduction_ratio=0.8,
            energy_delta=-1.0,
            relative_energy=1.2,
        )
        assert not legacy_single_sample_rule(child_result, baseline)

    def test_hot_swap_rejected_invalid(self, baseline):
        # Child is invalid
        child_result = PerformanceEnergyResult(
            score=1000.0,
            category=PerformanceCategory.CRASH,
            is_valid=False,
            duration_ms=10.0,
            peak_ram_mb=0.0,
            execution=ExecutionResult("", "", 1, False, 10.0, 1, 0.0),
            pain_signal="",
            speedup_factor=0.0,
            memory_reduction_ratio=0.0,
            energy_delta=-995.0,
            relative_energy=200.0,
        )
        assert not legacy_single_sample_rule(child_result, baseline)
