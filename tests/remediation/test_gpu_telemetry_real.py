"""Tests for real GPU telemetry via nvidia-smi."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from anse.infrastructure.fabrication import TelemetryUnavailableError
from anse.infrastructure.gpu_telemetry import GPUTelemetryHook


class TestGPUTelemetryHookInit:
    """Test __init__ properly detects GPU availability."""

    def test_init_with_nvidia_smi_available(self) -> None:
        """When nvidia-smi is available, connected should be True."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/nvidia-smi"
            hook = GPUTelemetryHook()
            assert hook.connected is True

    def test_init_without_nvidia_smi(self) -> None:
        """When nvidia-smi is not available, connected should be False."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None
            hook = GPUTelemetryHook()
            assert hook.connected is False


class TestGetRealTelemetry:
    """Test get_real_telemetry parses real nvidia-smi output."""

    def test_parse_valid_csv_output(self) -> None:
        """Verify all fields are correctly parsed from valid CSV output."""
        with patch("shutil.which") as mock_which, patch(
            "subprocess.run"
        ) as mock_run:
            mock_which.return_value = "/usr/bin/nvidia-smi"
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="42.0, 75, 8192, 15360\n",
                stderr="",
            )
            hook = GPUTelemetryHook()
            telemetry = hook.get_real_telemetry()

            assert telemetry["gpu_temp_c"] == 42.0
            assert telemetry["gpu_utilization_percent"] == 75.0
            assert telemetry["memory_used_mb"] == 8192
            assert telemetry["memory_total_mb"] == 15360

    def test_parse_output_with_whitespace(self) -> None:
        """Verify parsing handles extra whitespace in CSV fields."""
        with patch("shutil.which") as mock_which, patch(
            "subprocess.run"
        ) as mock_run:
            mock_which.return_value = "/usr/bin/nvidia-smi"
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="  50.5  ,  60  ,  4096  ,  16000  \n",
                stderr="",
            )
            hook = GPUTelemetryHook()
            telemetry = hook.get_real_telemetry()

            assert telemetry["gpu_temp_c"] == 50.5
            assert telemetry["gpu_utilization_percent"] == 60.0
            assert telemetry["memory_used_mb"] == 4096
            assert telemetry["memory_total_mb"] == 16000

    def test_memory_values_converted_to_int(self) -> None:
        """Verify memory fields are converted to integers."""
        with patch("shutil.which") as mock_which, patch(
            "subprocess.run"
        ) as mock_run:
            mock_which.return_value = "/usr/bin/nvidia-smi"
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="45.0, 50, 1024.5, 8192.7\n",
                stderr="",
            )
            hook = GPUTelemetryHook()
            telemetry = hook.get_real_telemetry()

            assert isinstance(telemetry["memory_used_mb"], int)
            assert isinstance(telemetry["memory_total_mb"], int)
            assert telemetry["memory_used_mb"] == 1024
            assert telemetry["memory_total_mb"] == 8192


class TestTelemetryUnavailableErrors:
    """Test TelemetryUnavailableError raised when nvidia-smi unavailable."""

    def test_raises_when_nvidia_smi_not_found(self) -> None:
        """Raise TelemetryUnavailableError when shutil.which returns None."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None
            hook = GPUTelemetryHook()
            with pytest.raises(TelemetryUnavailableError, match="nvidia-smi not found"):
                hook.get_real_telemetry()

    def test_error_includes_remedy_for_driver(self) -> None:
        """Error message should mention the driver card."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None
            hook = GPUTelemetryHook()
            with pytest.raises(TelemetryUnavailableError) as exc_info:
                hook.get_real_telemetry()
            assert "P0-3" in str(exc_info.value) or "driver" in str(
                exc_info.value
            ).lower()

    def test_raises_on_non_zero_exit(self) -> None:
        """Raise TelemetryUnavailableError when nvidia-smi exits non-zero."""
        with patch("shutil.which") as mock_which, patch(
            "subprocess.run"
        ) as mock_run:
            mock_which.return_value = "/usr/bin/nvidia-smi"
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="",
                stderr="GPU not found",
            )
            hook = GPUTelemetryHook()
            with pytest.raises(TelemetryUnavailableError):
                hook.get_real_telemetry()

    def test_raises_on_empty_output(self) -> None:
        """Raise TelemetryUnavailableError when nvidia-smi returns no output."""
        with patch("shutil.which") as mock_which, patch(
            "subprocess.run"
        ) as mock_run:
            mock_which.return_value = "/usr/bin/nvidia-smi"
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="",
                stderr="",
            )
            hook = GPUTelemetryHook()
            with pytest.raises(TelemetryUnavailableError):
                hook.get_real_telemetry()

    def test_raises_on_insufficient_fields(self) -> None:
        """Raise TelemetryUnavailableError when output has fewer than 4 fields."""
        with patch("shutil.which") as mock_which, patch(
            "subprocess.run"
        ) as mock_run:
            mock_which.return_value = "/usr/bin/nvidia-smi"
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="42.0, 75, 8192\n",
                stderr="",
            )
            hook = GPUTelemetryHook()
            with pytest.raises(TelemetryUnavailableError):
                hook.get_real_telemetry()

    def test_raises_on_unparseable_values(self) -> None:
        """Raise TelemetryUnavailableError when values cannot be parsed as numbers."""
        with patch("shutil.which") as mock_which, patch(
            "subprocess.run"
        ) as mock_run:
            mock_which.return_value = "/usr/bin/nvidia-smi"
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="not_a_number, 75, 8192, 15360\n",
                stderr="",
            )
            hook = GPUTelemetryHook()
            with pytest.raises(TelemetryUnavailableError):
                hook.get_real_telemetry()

    def test_raises_on_timeout(self) -> None:
        """Raise TelemetryUnavailableError when nvidia-smi times out."""
        with patch("shutil.which") as mock_which, patch(
            "subprocess.run"
        ) as mock_run:
            mock_which.return_value = "/usr/bin/nvidia-smi"
            mock_run.side_effect = subprocess.TimeoutExpired("nvidia-smi", 5.0)
            hook = GPUTelemetryHook()
            with pytest.raises(TelemetryUnavailableError):
                hook.get_real_telemetry()

    def test_raises_on_oserror(self) -> None:
        """Raise TelemetryUnavailableError when subprocess launch fails."""
        with patch("shutil.which") as mock_which, patch(
            "subprocess.run"
        ) as mock_run:
            mock_which.return_value = "/usr/bin/nvidia-smi"
            mock_run.side_effect = OSError("launch failed")
            hook = GPUTelemetryHook()
            with pytest.raises(TelemetryUnavailableError):
                hook.get_real_telemetry()


class TestSourceCode:
    """Verify the module contains no random functions."""

    def test_module_contains_no_random_uniform(self) -> None:
        """Assert the module source does not contain random.uniform."""
        with open(
            "anse/infrastructure/gpu_telemetry.py", encoding="utf-8"
        ) as f:
            content = f.read()
            assert "random.uniform" not in content

    def test_module_contains_no_random_gauss(self) -> None:
        """Assert the module source does not contain random.gauss."""
        with open(
            "anse/infrastructure/gpu_telemetry.py", encoding="utf-8"
        ) as f:
            content = f.read()
            assert "random.gauss" not in content
