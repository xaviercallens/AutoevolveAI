"""
Unit tests for Xavuntu 1-Hour Performance Endurance Benchmark Suite.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
import pytest

from scripts.xavuntu_1hr_benchmark import (
    XavuntuEnduranceBenchmark,
    RoundMetrics,
    BenchmarkFinalSummary,
)


class TestXavuntuEnduranceBenchmark:
    @pytest.fixture
    def temp_bench(self, tmp_path):
        base_dir = tmp_path / "bench_base"
        io_dir = tmp_path / "io_test"
        base_dir.mkdir(parents=True, exist_ok=True)
        io_dir.mkdir(parents=True, exist_ok=True)
        bench = XavuntuEnduranceBenchmark(
            target_duration_seconds=3,
            base_dir=base_dir,
            io_dir=io_dir,
        )
        return bench

    def test_syscall_benchmark(self, temp_bench):
        res = temp_bench.run_syscall_benchmark(iterations=1000)
        assert res["ops_per_sec"] > 1000.0
        assert res["p50_us"] > 0.0
        assert res["p99_us"] >= res["p50_us"]

    def test_memory_benchmark(self, temp_bench):
        # 16 MB test for fast unit test
        res = temp_bench.run_memory_benchmark(size_mb=16)
        assert res["bandwidth_gbps"] > 0.0
        assert res["page_alloc_us"] > 0.0

    def test_storage_benchmark(self, temp_bench):
        # 4 MB file for quick unit test
        res = temp_bench.run_storage_benchmark(file_size_mb=4)
        assert res["write_mbps"] > 0.0
        assert res["read_mbps"] > 0.0
        assert res["iops_4k"] > 0.0

    def test_tpu_acceleration_benchmark(self, temp_bench):
        res = temp_bench.run_tpu_acceleration_benchmark(iterations=1000)
        assert res["doorbell_latency_ns"] > 0.0
        assert res["doorbell_ops_per_sec"] > 0.0
        assert res["xla_barrier_us"] >= 0.0

    def test_pytorch_gemm_benchmark(self, temp_bench):
        res = temp_bench.run_pytorch_gemm_benchmark(dim=128)
        assert "tflops" in res
        assert "gemm_ms" in res
