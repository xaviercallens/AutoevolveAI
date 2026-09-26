"""P1-3: engine_v3 must report a real sandbox measurement, not a hardcoded multiplier."""

import inspect
from unittest.mock import patch

import pytest
import torch

from anse.infrastructure.fabrication import TelemetryUnavailableError
from anse.symbolic.sandbox import ExecutionResult
from anse.v3.engine_v3 import ANSEEngineV3

_FAKE_TELEMETRY = {
    "gpu_temp_c": 50.0,
    "gpu_utilization_percent": 10.0,
    "memory_used_mb": 100.0,
    "memory_total_mb": 15360.0,
}


def _make_engine() -> ANSEEngineV3:
    torch.manual_seed(0)
    return ANSEEngineV3(latent_dim=32)


def test_final_energy_is_real_sandbox_measurement_not_hardcoded_multiplier() -> None:
    engine = _make_engine()
    baseline_energy = 2000.0

    known_result = ExecutionResult(
        stdout="ok",
        stderr="",
        returncode=0,
        timed_out=False,
        duration_ms=123.456,
        tier_used=1,
        peak_ram_mb=45.678,
    )

    with (
        patch.object(engine.sandbox, "execute", return_value=known_result) as mock_execute,
        patch(
            "anse.v3.engine_v3.GPUTelemetryHook.get_real_telemetry",
            return_value=_FAKE_TELEMETRY,
        ),
    ):
        result = engine.run_singularity_loop(torch.randn(32), baseline_energy)

    mock_execute.assert_called_once()
    expected_energy = known_result.duration_ms + known_result.peak_ram_mb
    assert result.final_physical_energy == pytest.approx(expected_energy)
    assert result.final_physical_energy != baseline_energy * 0.95
    assert result.final_physical_energy != baseline_energy * 0.99


def test_telemetry_unavailable_propagates_out_of_engine() -> None:
    engine = _make_engine()

    with patch(
        "anse.v3.engine_v3.GPUTelemetryHook.get_real_telemetry",
        side_effect=TelemetryUnavailableError(
            "nvidia-smi not found on PATH",
            component="gpu_telemetry",
            remedy="Install NVIDIA drivers and ensure nvidia-smi is available.",
        ),
    ):
        with pytest.raises(TelemetryUnavailableError):
            engine.run_singularity_loop(torch.randn(32), 2000.0)


def test_no_hardcoded_energy_multipliers_remain_in_source() -> None:
    source = inspect.getsource(ANSEEngineV3.run_singularity_loop)
    assert "* 0.95" not in source
    assert "* 0.99" not in source
