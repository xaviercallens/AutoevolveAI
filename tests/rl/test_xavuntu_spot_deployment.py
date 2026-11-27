"""
tests/rl/test_xavuntu_spot_deployment.py — Tests for Xavuntu 32/64GB Spot Workstation Deployment Harness.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from scripts.deploy_xavuntu_spot_workstation import (
    XavuntuWorkstationConfig,
    XavuntuWorkstationDeployer,
)


class TestXavuntuWorkstationConfig:
    def test_default_config_32gb(self):
        config = XavuntuWorkstationConfig()
        assert config.machine_type == "n2-standard-8"
        assert config.expected_ram_gb == 32
        assert config.boot_disk_gb == 50
        assert config.secondary_disk_gb == 1000
        assert config.spot_hourly_rate_usd > 0.0

    def test_64gb_config(self):
        config = XavuntuWorkstationConfig(machine_type="n2-standard-16", expected_ram_gb=64)
        assert config.machine_type == "n2-standard-16"
        assert config.expected_ram_gb == 64
        assert config.spot_hourly_rate_usd == pytest.approx(0.152, rel=0.1)

    def test_custom_pricing_lookup(self):
        config_32 = XavuntuWorkstationConfig(machine_type="n2-standard-8")
        config_64 = XavuntuWorkstationConfig(machine_type="n2-standard-16")
        assert config_64.spot_hourly_rate_usd > config_32.spot_hourly_rate_usd


class TestXavuntuWorkstationDeployer:
    def test_cost_calculation(self):
        deployer = XavuntuWorkstationDeployer(XavuntuWorkstationConfig())
        cost_1hr = deployer.calculate_cost(3600)
        assert 0.07 < cost_1hr < 0.20

        cost_10m = deployer.calculate_cost(600)
        assert 0.01 < cost_10m < 0.04

    def test_create_and_delete_commands(self):
        deployer = XavuntuWorkstationDeployer(XavuntuWorkstationConfig(project_id="test-proj", zone="us-central1-c"))
        create_cmd = deployer.build_create_cmd()
        delete_cmd = deployer.build_delete_cmd()

        assert "gcloud" in create_cmd
        assert "compute" in create_cmd
        assert "instances" in create_cmd
        assert "create" in create_cmd
        assert any("--provisioning-model=SPOT" in arg for arg in create_cmd)
        assert any("--machine-type=n2-standard-8" in arg for arg in create_cmd)
        assert any("--boot-disk-size=50GB" in arg for arg in create_cmd)
        assert any("size=1000GB" in arg for arg in create_cmd)

        assert "delete" in delete_cmd
        assert "--quiet" in delete_cmd

    def test_dry_run_validation(self):
        deployer = XavuntuWorkstationDeployer(XavuntuWorkstationConfig(project_id="test-proj"))
        res = deployer.deploy_workstation(dry_run=True)
        assert res["status"] == "DRY_RUN_PASSED"
        assert res["machine_type"] == "n2-standard-8"
        assert res["expected_ram_gb"] == 32
        assert res["secondary_disk_gb"] == 1000
        assert "gui_access" in res
        assert res["gui_access"]["web_browser_port"] == 6080
        assert res["gui_access"]["vnc_port"] == 5901
