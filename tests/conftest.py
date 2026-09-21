"""
Global pytest configuration and anti-cheat runtime enforcement for ANSE test suites.
"""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import patch

import pytest

# Ensure Hypothesis is optionally loaded if installed
try:
    from hypothesis import HealthCheck, Phase, Verbosity, settings

    # 1. Fast profile for local agent iteration
    settings.register_profile(
        "dev",
        max_examples=25,
        deadline=400,  # 400ms timeout per example to catch accidental recursion
        verbosity=Verbosity.normal,
        phases=[Phase.explicit, Phase.reuse, Phase.generate, Phase.shrink],
    )

    # 2. Strict profile for pre-commit & CI validation
    settings.register_profile(
        "ci",
        max_examples=500,
        deadline=None,  # Suppress strict timeouts on heavy computational tests
        suppress_health_check=[HealthCheck.too_slow],
    )

    # 3. Deterministic replay profile for debugging agent failure traces
    settings.register_profile(
        "debug",
        max_examples=50,
        derandomize=True,  # Seed RNG deterministically to reproduce shrunken cases
        verbosity=Verbosity.verbose,
    )

    # 4. Profile tuned specifically for mutation runners (Mutmut)
    settings.register_profile(
        "mutation",
        max_examples=25,  # Catches >98% of breakages if strategies include boundaries
        phases=[Phase.explicit, Phase.generate],  # Skip Phase.shrink to kill mutant instantly
        deadline=None,  # Prevent slow-run false positives during mutation evaluation
        derandomize=True,  # Deterministic seed for reproducible runs
        suppress_health_check=[
            HealthCheck.too_slow,
            HealthCheck.filter_too_much,
            HealthCheck.data_too_large,
        ],
        verbosity=Verbosity.quiet,
    )

    # Load profile from environment variable (default: dev)
    profile_name = os.getenv("HYPOTHESIS_PROFILE", "dev")
    settings.load_profile(profile_name)

except ImportError:
    pass


# ─── Anti-Overmocking Enforcement ─────────────────────────────────────────────

FORBIDDEN_MOCK_TARGETS = [
    "anse.core",
    "anse.symbolic",
    "anse.jepa",
    "anse.autopoiesis",
    "src.core",
    "src.algorithms",
]


@pytest.fixture(autouse=True)
def prevent_overmocking(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Intercept unittest.mock.patch to prevent agents from mocking the primary SUT.
    Agents frequently hollow out tests by mocking out the exact functions being tested.
    """
    original_patch = patch

    def guarded_patch(target: Any, *args: Any, **kwargs: Any) -> Any:
        for forbidden in FORBIDDEN_MOCK_TARGETS:
            if isinstance(target, str) and target.startswith(forbidden):
                pytest.fail(
                    f"Agent Violation: Mocking '{target}' is forbidden. "
                    f"Unit tests must exercise real implementations for internal modules."
                )
        return original_patch(target, *args, **kwargs)

    monkeypatch.setattr("unittest.mock.patch", guarded_patch)


@pytest.fixture(autouse=True)
def isolated_attestation_path(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Isolate the execution attestation file so tests do not dirty the git working tree."""
    monkeypatch.setenv("ANSE_ATTESTATION_PATH", str(tmp_path / ".antigravity_attestation"))
