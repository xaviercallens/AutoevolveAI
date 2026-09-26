"""Exceptions raised when modules report success without doing the work."""


class FabricatedResultError(RuntimeError):
    """Base exception for fabricated results.

    Raised when a module reports success without actually performing the work.
    Stores component and remedy information for callers to take corrective action.
    """

    def __init__(
        self, message: str, *, component: str, remedy: str
    ) -> None:
        """Initialize the exception with message, component, and remedy.

        Args:
            message: Description of what went wrong.
            component: The name of the component that failed.
            remedy: Instructions on what to do instead.
        """
        super().__init__(message)
        self.component = component
        self.remedy = remedy

    def __str__(self) -> str:
        """Return a string representation including component and remedy."""
        base = super().__str__()
        return f"{base}\nComponent: {self.component}\nRemedy: {self.remedy}"


class TelemetryUnavailableError(FabricatedResultError):
    """Raised when telemetry was supposed to be collected but is unavailable."""

    pass


class SimulationRefusedError(FabricatedResultError):
    """Raised when a simulation refuses to run."""

    pass


class UnverifiedDataError(FabricatedResultError):
    """Raised when data cannot be verified."""

    pass
