"""Tests for fabrication exceptions."""

import pytest

from anse.infrastructure.fabrication import (
    FabricatedResultError,
    SimulationRefusedError,
    TelemetryUnavailableError,
    UnverifiedDataError,
)


class TestTelemetryUnavailableError:
    """Test TelemetryUnavailableError carries component and remedy through str() and attributes."""

    def test_exception_attributes(self) -> None:
        """Verify that raised exception preserves component and remedy attributes."""
        exc = TelemetryUnavailableError(
            "Metrics not collected",
            component="gpu_monitor",
            remedy="Enable GPU metrics in configuration and retry",
        )
        assert exc.component == "gpu_monitor"
        assert exc.remedy == "Enable GPU metrics in configuration and retry"

    def test_exception_string_representation(self) -> None:
        """Verify that str() includes component and remedy information."""
        exc = TelemetryUnavailableError(
            "Metrics not collected",
            component="gpu_monitor",
            remedy="Enable GPU metrics in configuration and retry",
        )
        exc_str = str(exc)
        assert "gpu_monitor" in exc_str
        assert "Enable GPU metrics in configuration and retry" in exc_str
        assert "Metrics not collected" in exc_str

    def test_is_fabricated_result_error(self) -> None:
        """Verify that TelemetryUnavailableError is a FabricatedResultError."""
        exc = TelemetryUnavailableError(
            "Metrics not collected",
            component="gpu_monitor",
            remedy="Enable GPU metrics in configuration and retry",
        )
        assert isinstance(exc, FabricatedResultError)

    def test_is_runtime_error(self) -> None:
        """Verify that TelemetryUnavailableError is a RuntimeError."""
        exc = TelemetryUnavailableError(
            "Metrics not collected",
            component="gpu_monitor",
            remedy="Enable GPU metrics in configuration and retry",
        )
        assert isinstance(exc, RuntimeError)


class TestFabricatedResultErrorCatching:
    """Test that FabricatedResultError catches multiple distinct subclasses."""

    def test_catch_telemetry_unavailable_error(self) -> None:
        """Verify that FabricatedResultError catches TelemetryUnavailableError."""
        with pytest.raises(FabricatedResultError, match="telemetry data"):
            raise TelemetryUnavailableError(
                "No telemetry data available",
                component="monitor",
                remedy="Check monitor service",
            )

    def test_catch_simulation_refused_error(self) -> None:
        """Verify that FabricatedResultError catches SimulationRefusedError."""
        with pytest.raises(FabricatedResultError, match="Simulation"):
            raise SimulationRefusedError(
                "Simulation was refused",
                component="simulator",
                remedy="Restart the simulator",
            )

    def test_catch_unverified_data_error(self) -> None:
        """Verify that FabricatedResultError catches UnverifiedDataError."""
        with pytest.raises(FabricatedResultError, match="Unverified"):
            raise UnverifiedDataError(
                "Unverified data returned",
                component="validator",
                remedy="Re-validate the data",
            )

    def test_multiple_subclasses_caught_by_base(self) -> None:
        """Verify that at least two distinct subclasses are caught by the base."""
        subclass_caught_count = 0

        # Test TelemetryUnavailableError
        try:
            raise TelemetryUnavailableError(
                "Telemetry unavailable",
                component="telemetry",
                remedy="Enable telemetry",
            )
        except FabricatedResultError:
            subclass_caught_count += 1

        # Test SimulationRefusedError
        try:
            raise SimulationRefusedError(
                "Simulation refused",
                component="sim",
                remedy="Retry simulation",
            )
        except FabricatedResultError:
            subclass_caught_count += 1

        # Test UnverifiedDataError
        try:
            raise UnverifiedDataError(
                "Data unverified",
                component="data",
                remedy="Verify data",
            )
        except FabricatedResultError:
            subclass_caught_count += 1

        assert subclass_caught_count >= 2, "At least two distinct subclasses must be caught"
