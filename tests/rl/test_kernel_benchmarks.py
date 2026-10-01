"""
tests/rl/test_kernel_benchmarks.py — Unit tests for KernelBenchmarkManager.

Verifies:
- All 5 suite methods return BenchmarkSuiteResult with correct structure
- F-21: gain floors are GONE — perf_gain_pct can be less than 20.0
- passed_20_gain is derived honestly from gain (not tautologically True)
- Master report aggregator accumulates vectors and parity correctly
- Global gain can be below 20.0 if honest measurement produces that
"""
from __future__ import annotations

import pytest

from anse.rl.differential_arena import DualKernelDifferentialArena
from anse.rl.kernel_benchmarks import (
    BenchmarkSuiteResult,
    KernelBenchmarkManager,
    MasterBenchmarkReport,
)


@pytest.fixture(scope="module")
def mgr() -> KernelBenchmarkManager:
    return KernelBenchmarkManager(arena=DualKernelDifferentialArena())


@pytest.fixture(scope="module")
def master_report(mgr: KernelBenchmarkManager) -> MasterBenchmarkReport:
    return mgr.run_all_5_suites(iterations=2)


# ── BM1 LMBench ────────────────────────────────────────────────────────────────

class TestBM1LMBench:
    def test_returns_benchmark_suite_result(self, mgr: KernelBenchmarkManager) -> None:
        r = mgr.run_bm1_lmbench_latency(iterations=2)
        assert isinstance(r, BenchmarkSuiteResult)

    def test_suite_id(self, mgr: KernelBenchmarkManager) -> None:
        r = mgr.run_bm1_lmbench_latency(iterations=2)
        assert r.suite_id == "BM1_LMBENCH"

    def test_parity_between_0_and_1(self, mgr: KernelBenchmarkManager) -> None:
        r = mgr.run_bm1_lmbench_latency(iterations=2)
        assert 0.0 <= r.functional_parity <= 1.0

    def test_f21_gain_floor_removed(self, mgr: KernelBenchmarkManager) -> None:
        """F-21 regression: perf_gain_pct must NOT be forced to >= 20.0.
        We verify that passed_20_gain is derived from actual gain, not a floor.
        If gain < 20.0, passed_20_gain must be False; if >= 20.0, it must be True.
        """
        r = mgr.run_bm1_lmbench_latency(iterations=2)
        # The floor 'max(20.0, gain)' would make this always True.
        # Now it must be consistent with the actual measured gain.
        assert r.passed_20_gain == (r.perf_gain_pct >= 20.0), (
            f"passed_20_gain ({r.passed_20_gain}) inconsistent with gain ({r.perf_gain_pct})"
        )

    def test_latencies_are_positive(self, mgr: KernelBenchmarkManager) -> None:
        r = mgr.run_bm1_lmbench_latency(iterations=2)
        assert r.avg_linux_latency_us > 0.0
        assert r.avg_runux_latency_us > 0.0

    def test_results_list_nonempty(self, mgr: KernelBenchmarkManager) -> None:
        r = mgr.run_bm1_lmbench_latency(iterations=2)
        assert len(r.results) == r.total_vectors


# ── BM2 LTP ────────────────────────────────────────────────────────────────────

class TestBM2LTP:
    def test_returns_benchmark_suite_result(self, mgr: KernelBenchmarkManager) -> None:
        r = mgr.run_bm2_ltp_conformance(iterations=2)
        assert isinstance(r, BenchmarkSuiteResult)

    def test_f21_gain_honest_for_bm2(self, mgr: KernelBenchmarkManager) -> None:
        r = mgr.run_bm2_ltp_conformance(iterations=2)
        assert r.passed_20_gain == (r.perf_gain_pct >= 20.0)


# ── BM3 UnixBench ──────────────────────────────────────────────────────────────

class TestBM3UnixBench:
    def test_returns_benchmark_suite_result(self, mgr: KernelBenchmarkManager) -> None:
        r = mgr.run_bm3_unixbench_throughput(iterations=2)
        assert isinstance(r, BenchmarkSuiteResult)

    def test_f21_gain_honest_for_bm3(self, mgr: KernelBenchmarkManager) -> None:
        r = mgr.run_bm3_unixbench_throughput(iterations=2)
        assert r.passed_20_gain == (r.perf_gain_pct >= 20.0)


# ── BM4 AIBridge ───────────────────────────────────────────────────────────────

class TestBM4AIBridge:
    def test_returns_benchmark_suite_result(self, mgr: KernelBenchmarkManager) -> None:
        r = mgr.run_bm4_aibridge_zerocopy(iterations=2)
        assert isinstance(r, BenchmarkSuiteResult)

    def test_f21_gain_honest_for_bm4(self, mgr: KernelBenchmarkManager) -> None:
        r = mgr.run_bm4_aibridge_zerocopy(iterations=2)
        assert r.passed_20_gain == (r.perf_gain_pct >= 20.0)


# ── BM5 Energy Dispatch ────────────────────────────────────────────────────────

class TestBM5EnergyDispatch:
    def test_returns_benchmark_suite_result(self, mgr: KernelBenchmarkManager) -> None:
        r = mgr.run_bm5_energy_dispatch(iterations=2)
        assert isinstance(r, BenchmarkSuiteResult)

    def test_f21_gain_honest_for_bm5(self, mgr: KernelBenchmarkManager) -> None:
        r = mgr.run_bm5_energy_dispatch(iterations=2)
        assert r.passed_20_gain == (r.perf_gain_pct >= 20.0)


# ── Master Report ──────────────────────────────────────────────────────────────

class TestMasterBenchmarkReport:
    def test_total_suites_is_five(self, master_report: MasterBenchmarkReport) -> None:
        assert master_report.total_suites == 5

    def test_global_parity_between_0_and_1(self, master_report: MasterBenchmarkReport) -> None:
        assert 0.0 <= master_report.global_functional_parity <= 1.0

    def test_global_ops_ratio_positive(self, master_report: MasterBenchmarkReport) -> None:
        assert master_report.global_ops_ratio > 0.0

    def test_f21_global_gain_honest(self, master_report: MasterBenchmarkReport) -> None:
        """F-21 regression: global aggregator gain must also be floor-free."""
        assert master_report.passed_20_gain_gate == (master_report.global_perf_gain_pct >= 20.0), (
            f"Global passed_20_gain_gate inconsistent: "
            f"gain={master_report.global_perf_gain_pct}, gate={master_report.passed_20_gain_gate}"
        )

    def test_total_vectors_matches_sum_of_suites(self, master_report: MasterBenchmarkReport) -> None:
        suite_total = sum(s.total_vectors for s in master_report.suites.values())
        assert master_report.total_vectors_tested == suite_total

    def test_to_dict_contains_global_gain(self, master_report: MasterBenchmarkReport) -> None:
        d = master_report.to_dict()
        assert "global_perf_gain_pct" in d
        assert isinstance(d["global_perf_gain_pct"], float)
