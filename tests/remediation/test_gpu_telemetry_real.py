"""Tests for GPUTelemetryHook real hardware interface."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from anse.infrastructure.fabrication import TelemetryUnavailableError
from anse.infrastructure.gpu_telemetry import GPUTelemetryHook, GPUTelemetryData


def test_get_real_telemetry_parses_csv_fields() -> None:
    """Test that get_real_telemetry correctly parses nvidia-smi CSV output."""
    csv_output = "45.5, 60.0, 2048.5, 15360.0"

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = csv_output
    mock_result.stderr = ""

    hook = GPUTelemetryHook()

    with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
        with patch("subprocess.run", return_value=mock_result):
            data = hook.get_real_telemetry()

    # Assert all 4 fields are parsed correctly
    assert data["gpu_temp_c"] == 45.5
    assert data["gpu_utilization_percent"] == 60.0
    assert data["memory_used_mb"] == 2048.5
    assert data["memory_total_mb"] == 15360.0


def test_get_real_telemetry_raises_when_nvidia_smi_missing() -> None:
    """Test that get_real_telemetry raises TelemetryUnavailableError when nvidia-smi unavailable."""
    hook = GPUTelemetryHook()

    with patch("shutil.which", return_value=None):
        with pytest.raises(TelemetryUnavailableError, match="gpu"):
            hook.get_real_telemetry()


def test_telemetry_unavailable_error_mentions_driver_card() -> None:
    """Test that TelemetryUnavailableError remedy mentions the driver card P0-3."""
    hook = GPUTelemetryHook()

    with patch("shutil.which", return_value=None):
        with pytest.raises(TelemetryUnavailableError) as exc_info:
            hook.get_real_telemetry()

    error = exc_info.value
    assert "P0-3" in error.remedy


def test_get_real_telemetry_raises_on_nonzero_exit() -> None:
    """Test that get_real_telemetry raises when nvidia-smi exits non-zero."""
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "NVIDIA driver error"
    mock_result.stdout = ""

    hook = GPUTelemetryHook()

    with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(TelemetryUnavailableError):
                hook.get_real_telemetry()


def test_get_real_telemetry_raises_on_timeout() -> None:
    """Test that get_real_telemetry raises when nvidia-smi times out."""
    hook = GPUTelemetryHook()

    with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 5.0)):
            with pytest.raises(TelemetryUnavailableError):
                hook.get_real_telemetry()


def test_get_real_telemetry_raises_on_launch_error() -> None:
    """Test that get_real_telemetry raises when nvidia-smi cannot launch."""
    hook = GPUTelemetryHook()

    with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
        with patch("subprocess.run", side_effect=OSError("permission denied")):
            with pytest.raises(TelemetryUnavailableError):
                hook.get_real_telemetry()


def test_init_connected_true_when_nvidia_smi_present() -> None:
    """Test that __init__ sets connected=True when nvidia-smi is on PATH."""
    with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
        hook = GPUTelemetryHook()
        assert hook.connected is True


def test_init_connected_false_when_nvidia_smi_missing() -> None:
    """Test that __init__ sets connected=False when nvidia-smi is not on PATH."""
    with patch("shutil.which", return_value=None):
        hook = GPUTelemetryHook()
        assert hook.connected is False


def test_module_contains_no_random_import() -> None:
    """Test that gpu_telemetry.py does not use random module."""
    module_path = Path(__file__).resolve().parents[2] / "anse" / "infrastructure" / "gpu_telemetry.py"
    source = module_path.read_text()

    # Assert no random.uniform or random.gauss calls
    assert "random.uniform" not in source
    assert "random.gauss" not in source


def test_parse_telemetry_with_integer_memory_values() -> None:
    """Test that _parse_telemetry handles integer memory values."""
    csv_output = "50.0, 75.0, 4096, 8192"

    result = GPUTelemetryHook._parse_telemetry(csv_output)

    assert result["gpu_temp_c"] == 50.0
    assert result["gpu_utilization_percent"] == 75.0
    assert result["memory_used_mb"] == 4096.0
    assert result["memory_total_mb"] == 8192.0


def test_parse_telemetry_raises_on_missing_fields() -> None:
    """Test that _parse_telemetry raises when too few fields provided."""
    csv_output = "50.0, 75.0"  # Only 2 fields, needs 4

    with pytest.raises(TelemetryUnavailableError):
        GPUTelemetryHook._parse_telemetry(csv_output)


def test_parse_telemetry_raises_on_non_numeric_values() -> None:
    """Test that _parse_telemetry raises when fields are not numeric."""
    csv_output = "invalid, 75.0, 4096, 8192"

    with pytest.raises(TelemetryUnavailableError):
        GPUTelemetryHook._parse_telemetry(csv_output)


def test_parse_telemetry_raises_on_empty_output() -> None:
    """Test that _parse_telemetry raises on empty input."""
    with pytest.raises(TelemetryUnavailableError):
        GPUTelemetryHook._parse_telemetry("")


def test_get_real_telemetry_empty_output() -> None:
    """Test that get_real_telemetry raises when nvidia-smi returns empty output."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""

    hook = GPUTelemetryHook()

    with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(TelemetryUnavailableError):
                hook.get_real_telemetry()


def test_telemetry_data_type_dict() -> None:
    """Test that returned telemetry data conforms to GPUTelemetryData TypedDict."""
    csv_output = "42.5, 50.0, 1024.0, 2048.0"

    data = GPUTelemetryHook._parse_telemetry(csv_output)

    # Verify all keys are present and types are correct
    assert isinstance(data["gpu_temp_c"], float)
    assert isinstance(data["gpu_utilization_percent"], float)
    assert isinstance(data["memory_used_mb"], float)
    assert isinstance(data["memory_total_mb"], float)
