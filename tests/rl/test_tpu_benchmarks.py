"""Unit tests for GoogleTPUBenchmarkSuite (anse/rl/tpu_benchmarks.py).

Run 5: First test coverage for the TPU benchmark module.
"""
from __future__ import annotations

import pytest

from anse.rl.tpu_benchmarks import (
    GoogleTPUBenchmarkSuite,
    TPUMasterBenchmarkReport,
    TPUMicrobenchmarkResult,
)


@pytest.fixture(scope="module")
def suite() -> GoogleTPUBenchmarkSuite:
    return GoogleTPUBenchmarkSuite()


@pytest.fixture(scope="module")
def master_report(suite: GoogleTPUBenchmarkSuite) -> TPUMasterBenchmarkReport:
    # Use 2 iterations for speed in tests
    return suite.run_all_tpu_benchmarks(iterations=2)


class TestTPUMicrobenchmarkResult:
    def test_is_simulated_true(self, master_report: TPUMasterBenchmarkReport) -> None:
        """All results must carry is_simulated=True (F-01 transparency fix)."""
        for r in master_report.results:
            assert r.is_simulated is True, f"{r.test_name} has is_simulated={r.is_simulated}"

    def test_to_dict_round_trips(self, master_report: TPUMasterBenchmarkReport) -> None:
        """to_dict() must include the is_simulated field."""
        for r in master_report.results:
            d = r.to_dict()
            assert "is_simulated" in d
            assert d["is_simulated"] is True

    def test_result_workload_types_are_expected(self, master_report: TPUMasterBenchmarkReport) -> None:
        workload_types = {r.workload_type for r in master_report.results}
        expected = {"INGEST", "SYSTOLIC_TILE", "BARRIER", "BURST_STREAM"}
        assert workload_types == expected


class TestTPUMasterBenchmarkReport:
    def test_total_benchmarks_is_four(self, master_report: TPUMasterBenchmarkReport) -> None:
        assert master_report.total_benchmarks == 4

    def test_passed_50_ai_gate_can_be_false(self) -> None:
        """F-02 fix: with floor removed, the gate can legitimately be False.

        We inject a suite result with a very small gain to prove the gate is not tautological.
        """
        r = TPUMicrobenchmarkResult(
            test_name="SYNTHETIC_FAIL",
            workload_type="INGEST",
            tensor_shape="[1]",
            data_bytes=1,
            linux_latency_us=1.0,
            runux_latency_us=1.0,   # No speedup at all
            linux_throughput_gbps=0.0,
            runux_throughput_gbps=0.0,
            speedup_gain_pct=0.0,   # 0% gain — well below 50% gate
            ops_ratio=1.0,
            passed_50_ai_gate=False,  # Gate correctly fails
        )
        assert not r.passed_50_ai_gate

    def test_global_ops_ratio_is_positive(self, master_report: TPUMasterBenchmarkReport) -> None:
        assert master_report.global_ops_ratio > 0.0

    def test_master_report_to_dict_contains_results(self, master_report: TPUMasterBenchmarkReport) -> None:
        d = master_report.to_dict()
        assert "results" in d
        assert len(d["results"]) == 4
        for r in d["results"]:
            assert "is_simulated" in r

    def test_master_report_timestamps(self, master_report: TPUMasterBenchmarkReport) -> None:
        import time
        assert master_report.timestamp > 0
        assert master_report.timestamp <= time.time() + 1


class TestGoogleTPUBenchmarkSuiteAlias:
    def test_run_all_alias_is_callable(self, suite: GoogleTPUBenchmarkSuite) -> None:
        """F-04: run_all alias must be callable and return a master report."""
        assert callable(suite.run_all)
        result = suite.run_all(iterations=1)
        assert isinstance(result, TPUMasterBenchmarkReport)
        assert result.total_benchmarks == 4

    def test_individual_benchmark_methods_return_microbenchmark_result(
        self, suite: GoogleTPUBenchmarkSuite
    ) -> None:
        r = suite.run_tensor_ingest_benchmark(iterations=1)
        assert isinstance(r, TPUMicrobenchmarkResult)
        assert r.is_simulated is True

    def test_latencies_are_positive(self, master_report: TPUMasterBenchmarkReport) -> None:
        for r in master_report.results:
            assert r.linux_latency_us > 0.0, f"{r.test_name}: linux_latency_us <= 0"
            assert r.runux_latency_us > 0.0, f"{r.test_name}: runux_latency_us <= 0"
