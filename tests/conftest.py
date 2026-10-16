"""
Global pytest configuration and anti-cheat runtime enforcement for ANSE test suites.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# Wire datalake vendor path for vendored imports like rl_common and rl_agent_api
for _candidate in [
    Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI/datalake/vendor/laya"),
    Path(__file__).resolve().parent.parent / "checkpoints" / "laya",
    Path(__file__).resolve().parent.parent / "vendor" / "laya",
]:
    if _candidate.exists() and str(_candidate) not in sys.path:
        sys.path.insert(0, str(_candidate))

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
    """Isolate the execution attestation file so tests do not dirty the git working tree.

    Both paths are needed: execution_attestation reads ANSE_ATTESTATION_PATH at
    call time in some functions, but also freezes ATTESTATION_FILE at import.
    """
    import execution_attestation

    receipt = tmp_path / ".antigravity_attestation"
    monkeypatch.setenv("ANSE_ATTESTATION_PATH", str(receipt))
    monkeypatch.setattr(execution_attestation, "ATTESTATION_FILE", receipt)


# ── T-02: Optional-extras collection guard ───────────────────────────────────
# These modules require packages from the 'web', 'gateway', or 'training' extras.
# If the extras are not installed, skip collection without erroring — so that
# `uv run pytest tests/` succeeds and runs the core suite.
# To run everything: `uv sync --all-extras && uv run pytest tests/`

import importlib.util as _ilu

_OPTIONAL_EXTRAS_TESTS = [
    "tests/stronggravity/test_gateway_routing.py",
    "tests/test_architecture_e2e.py",
    "tests/test_audit_gateway.py",
    "tests/test_benchmark_complete_coverage.py",
    "tests/test_claude_opus_gateway.py",
    "tests/test_dpo_pipeline.py",
    "tests/test_harvest_pipeline.py",
    "tests/test_local_32gb_cpu_antigravity_validation.py",
    "tests/test_local_lora_gateway.py",
    "tests/test_mcp_gateway_integration.py",
    "tests/test_multi_tier_gateway.py",
    "tests/test_serverless_coldstart_endpoint.py",
    "tests/test_ten_hardening_validations.py",
    "tests/test_ui_features.py",
    "tests/test_web_server.py",
    "tests/web/test_anse_v2_v3_v4_ui.py",
    "tests/web/test_anse_v5_ui.py",
    "tests/web/test_control_center.py",
    "tests/web/test_factory_api.py",
    "tests/web/test_factory_mobile.py",
]

_GATEWAY_EXTRAS_AVAILABLE = all(
    _ilu.find_spec(pkg) is not None for pkg in ("fastapi", "httpx", "fakeredis")
)

_REPO_ROOT = Path(__file__).parent

collect_ignore: list[str] = []
if not _GATEWAY_EXTRAS_AVAILABLE:
    collect_ignore = [str(_REPO_ROOT / p) for p in _OPTIONAL_EXTRAS_TESTS]

