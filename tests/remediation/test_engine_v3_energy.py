"""Remediation tests for P1-3: engine_v3 must stop faking final_physical_energy.

Verifies that ANSEEngineV3.run_singularity_loop reports a real measurement
taken from the deterministic sandbox (anse/symbolic/sandbox.py) instead of a
hardcoded baseline_energy * 0.95 / 0.99 multiplier, and that a GPU telemetry
failure propagates instead of being swallowed.
"""

import inspect
from unittest.mock import patch

import pytest
import torch

from anse.infrastructure.fabrication import TelemetryUnavailableError
from anse.symbolic.sandbox import ExecutionResult
from anse.v3.engine_v3 import ANSEEngineV3

_FAKE_TELEMETRY = {
    "gpu_temp_c": 55.0,
    "gpu_utilization_percent": 30.0,
    "memory_used_mb": 1024,
    "memory_total_mb": 16384,
}


def test_final_energy_comes_from_sandbox_measurement_not_multiplier() -> None:
    engine = ANSEEngineV3(latent_dim=128)
    baseline_energy = 2000.0
    known_duration_ms = 137.25
    known_peak_ram_mb = 48.0
    expected_energy = known_duration_ms + known_peak_ram_mb

    fake_result = ExecutionResult(
        stdout="",
        stderr="",
        returncode=0,
        timed_out=False,
        duration_ms=known_duration_ms,
        tier_used=1,
        peak_ram_mb=known_peak_ram_mb,
    )

    with patch(
        "anse.infrastructure.gpu_telemetry.GPUTelemetryHook.get_real_telemetry",
        return_value=_FAKE_TELEMETRY,
    ), patch(
        "anse.symbolic.sandbox.SandboxExecutor.execute",
        return_value=fake_result,
    ):
        result = engine.run_singularity_loop(torch.randn(128), baseline_energy)

    assert result.final_physical_energy == expected_energy
    assert result.final_physical_energy != baseline_energy * 0.95
    assert result.final_physical_energy != baseline_energy * 0.99


def test_telemetry_unavailable_propagates_out_of_engine() -> None:
    engine = ANSEEngineV3(latent_dim=128)

    with patch(
        "anse.infrastructure.gpu_telemetry.GPUTelemetryHook.get_real_telemetry",
        side_effect=TelemetryUnavailableError(
            "GPU telemetry unavailable: nvidia-smi not found",
            component="gpu_telemetry",
            remedy="Install NVIDIA driver",
        ),
    ):
        with pytest.raises(TelemetryUnavailableError, match="nvidia-smi not found"):
            engine.run_singularity_loop(torch.randn(128), 2000.0)


def test_no_hardcoded_energy_multiplier_literals_remain() -> None:
    source = inspect.getsource(ANSEEngineV3.run_singularity_loop)

    assert "0.95" not in source
    assert "0.99" not in source
