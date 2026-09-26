import logging
import shutil
import subprocess
from typing import TypedDict

from anse.infrastructure.fabrication import TelemetryUnavailableError

logger = logging.getLogger(__name__)


class GPUTelemetryData(TypedDict):
    """Parsed output from nvidia-smi GPU telemetry query."""
    gpu_temp_c: float
    gpu_utilization_percent: float
    memory_used_mb: float
    memory_total_mb: float


class GPUTelemetryHook:
    """
    Reads live GPU metrics via nvidia-smi.
    Connects to nvidia-smi at initialization to verify GPU is reachable.
    """
    def __init__(self) -> None:
        exe = shutil.which("nvidia-smi")
        self.connected = exe is not None
        if self.connected:
            logger.info("GPUTelemetryHook initialized. Connected to nvidia-smi.")
        else:
            logger.warning("GPUTelemetryHook initialized. nvidia-smi not found on PATH.")

    def get_real_telemetry(self) -> GPUTelemetryData:
        """Fetches live GPU temperature, utilization, and memory metrics.

        Returns:
            A dict with gpu_temp_c, gpu_utilization_percent, memory_used_mb, memory_total_mb.

        Raises:
            TelemetryUnavailableError: If nvidia-smi is not available or fails.
        """
        exe = shutil.which("nvidia-smi")
        if exe is None:
            raise TelemetryUnavailableError(
                "nvidia-smi not found on PATH",
                component="gpu_telemetry",
                remedy="Install NVIDIA drivers and ensure nvidia-smi is available. See card P0-3.",
            )

        try:
            result = subprocess.run(
                [
                    exe,
                    "--query-gpu=temperature.gpu,utilization.gpu,memory.used,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5.0,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise TelemetryUnavailableError(
                "nvidia-smi timed out",
                component="gpu_telemetry",
                remedy="GPU query took too long. See card P0-3.",
            ) from exc
        except OSError as exc:
            raise TelemetryUnavailableError(
                f"Failed to launch nvidia-smi: {exc}",
                component="gpu_telemetry",
                remedy="Cannot launch nvidia-smi. See card P0-3.",
            ) from exc

        if result.returncode != 0:
            error_msg = (result.stderr or result.stdout).strip() or f"exit {result.returncode}"
            raise TelemetryUnavailableError(
                f"nvidia-smi failed: {error_msg}",
                component="gpu_telemetry",
                remedy="nvidia-smi command failed. Verify driver is installed. See card P0-3.",
            )

        if not result.stdout.strip():
            raise TelemetryUnavailableError(
                "nvidia-smi returned no output",
                component="gpu_telemetry",
                remedy="No GPU devices detected by nvidia-smi. See card P0-3.",
            )

        return self._parse_telemetry(result.stdout)

    @staticmethod
    def _parse_telemetry(output: str) -> GPUTelemetryData:
        """Parse nvidia-smi CSV output into typed dict.

        Args:
            output: CSV line from nvidia-smi with temp, utilization, mem_used, mem_total.

        Returns:
            GPUTelemetryData with parsed float/int values.

        Raises:
            TelemetryUnavailableError: If parsing fails.
        """
        line = next((ln for ln in output.strip().splitlines() if ln.strip()), "")
        if not line:
            raise TelemetryUnavailableError(
                "No GPU telemetry data in nvidia-smi output",
                component="gpu_telemetry",
                remedy="nvidia-smi returned empty result. See card P0-3.",
            )

        fields = [f.strip() for f in line.split(",")]
        if len(fields) < 4:
            raise TelemetryUnavailableError(
                f"Expected 4 fields, got {len(fields)}: {line}",
                component="gpu_telemetry",
                remedy="nvidia-smi output format unexpected. See card P0-3.",
            )

        try:
            temp_c = float(fields[0])
            util_percent = float(fields[1])
            mem_used_mb = float(fields[2])
            mem_total_mb = float(fields[3])
        except (ValueError, IndexError) as exc:
            raise TelemetryUnavailableError(
                f"Cannot parse telemetry fields: {exc}",
                component="gpu_telemetry",
                remedy="nvidia-smi output values are not numeric. See card P0-3.",
            ) from exc

        return GPUTelemetryData(
            gpu_temp_c=temp_c,
            gpu_utilization_percent=util_percent,
            memory_used_mb=mem_used_mb,
            memory_total_mb=mem_total_mb,
        )
