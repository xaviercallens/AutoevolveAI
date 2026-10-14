"""
Unit tests for Xavuntu vs. Ubuntu Dual Benchmark on GCP Spot (scripts/run_xavuntu_dual_kernel_gcp_benchmark.py).
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from scripts.run_xavuntu_dual_kernel_gcp_benchmark import (
    FeatureReport,
    XavuntuBenchConfig,
    XavuntuGCPBenchmarkRunner,
)


class TestXavuntuBenchConfig:
    def test_default_config(self):
        config = XavuntuBenchConfig(project_id="test-project")
        assert config.machine_type == "e2-small"
        assert config.disk_size_gb == 10
        assert config.max_duration_seconds == 600
        assert config.max_budget_usd == 0.01
        assert config.spot_hourly_rate_usd == 0.00504

    def test_spot_hourly_rate_lookup(self):
        cfg_micro = XavuntuBenchConfig(project_id="p", machine_type="e2-micro")
        assert cfg_micro.spot_hourly_rate_usd == 0.00220
        cfg_small = XavuntuBenchConfig(project_id="p", machine_type="e2-small")
        assert cfg_small.spot_hourly_rate_usd == 0.00504


class TestXavuntuGCPBenchmarkRunner:
    @pytest.fixture
    def runner(self):
        config = XavuntuBenchConfig(project_id="test-project", machine_type="e2-small")
        return XavuntuGCPBenchmarkRunner(config=config)

    def test_calculate_cost_5_minutes(self, runner):
        # 300 seconds (5 minutes)
        cost = runner.calculate_cost(300)
        assert cost > 0.0
        assert cost < 0.001  # Must be strictly under one-tenth of a cent

    def test_calculate_cost_10_minutes(self, runner):
        # 600 seconds (10 minutes)
        cost = runner.calculate_cost(600)
        assert cost > 0.0
        assert cost < 0.002  # Must be strictly under 0.2 cents

    def test_dry_run_validation(self, runner):
        res = runner.run_benchmark(dry_run=True)
        assert res["status"] == "DRY_RUN_PASSED"
        assert res["within_budget"] is True
        assert len(res["create_cmd"]) > 10
        assert any("SPOT" in arg for arg in res["create_cmd"])
        assert len(res["delete_cmd"]) == 8

    def test_feature_report_dataclass(self):
        feat = FeatureReport(
            feature_id="FEAT_TEST",
            feature_name="Test Feature",
            benchmark_source="Test Source",
            baseline_latency_us=10.0,
            xavuntu_latency_us=2.0,
            throughput_ratio=5.0,
            speedup_gain_pct=80.0,
            degradation_pct=0.0,
            functional_parity=1.0,
            status="PASSED_SPEEDUP",
            details={"key": "val"},
        )
        d = feat.to_dict()
        assert d["speedup_gain_pct"] == 80.0
        assert d["degradation_pct"] <= 10.0
        assert d["functional_parity"] == 1.0
