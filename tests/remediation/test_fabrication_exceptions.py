"""Tests for fabrication exception classes."""

import pytest

from anse.infrastructure.fabrication import (
    FabricatedResultError,
    SimulationRefusedError,
    TelemetryUnavailableError,
    UnverifiedDataError,
)


def test_telemetry_unavailable_error_carries_attributes() -> None:
    """Test that TelemetryUnavailableError stores and retrieves component and remedy."""
    component = "data_collector"
    remedy = "restart the data collection daemon"
    message = "Failed to collect telemetry"

    error = TelemetryUnavailableError(
        message, component=component, remedy=remedy
    )

    # Assert attributes are stored
    assert error.component == component
    assert error.remedy == remedy

    # Assert they appear in string representation
    error_str = str(error)
    assert component in error_str
    assert remedy in error_str
    assert message in error_str


def test_telemetry_unavailable_is_fabricated_result_error() -> None:
    """Test that TelemetryUnavailableError is a FabricatedResultError."""
    error = TelemetryUnavailableError(
        "test", component="comp", remedy="fix it"
    )

    assert isinstance(error, FabricatedResultError)
    assert isinstance(error, RuntimeError)


def test_all_subclasses_caught_by_base() -> None:
    """Test that pytest.raises catches all exception subclasses."""
    # Test TelemetryUnavailableError is caught
    with pytest.raises(FabricatedResultError, match="telemetry"):
        raise TelemetryUnavailableError(
            "telemetry failed", component="c1", remedy="r1"
        )

    # Test SimulationRefusedError is caught
    with pytest.raises(FabricatedResultError, match="simulation"):
        raise SimulationRefusedError(
            "simulation refused", component="c2", remedy="r2"
        )

    # Test UnverifiedDataError is caught
    with pytest.raises(FabricatedResultError, match="unverified"):
        raise UnverifiedDataError(
            "unverified data", component="c3", remedy="r3"
        )


def test_multiple_distinct_subclasses() -> None:
    """Assert at least two distinct subclasses are caught by the base."""
    subclasses = [
        TelemetryUnavailableError,
        SimulationRefusedError,
        UnverifiedDataError,
    ]

    # Verify they are all distinct
    assert len(set(subclasses)) >= 2

    # Verify they all inherit from FabricatedResultError
    for exc_class in subclasses:
        assert issubclass(exc_class, FabricatedResultError)

        # Instantiate and verify
        error = exc_class("msg", component="c", remedy="r")
        assert isinstance(error, FabricatedResultError)
