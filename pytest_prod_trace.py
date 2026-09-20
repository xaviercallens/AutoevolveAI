"""
Pytest Production Code Trace Enforcement Plugin.
Hooks into pytest_runtest_call using sys.settrace to verify tests invoke real production code.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import pytest

DEFAULT_PROD_DIR = "anse" if os.path.exists("anse") else "src"


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register CLI flags and ini configuration options."""
    group = parser.getgroup("prod-trace", "Production Code Trace Enforcement")
    group.addoption(
        "--prod-dir",
        action="store",
        default=DEFAULT_PROD_DIR,
        help=(
            f"Directory containing production code that tests must execute "
            f"(default: '{DEFAULT_PROD_DIR}')"
        ),
    )
    group.addoption(
        "--min-prod-calls",
        action="store",
        type=int,
        default=1,
        help="Minimum number of unique production function calls required per test (default: 1)",
    )
    parser.addini(
        "prod_dir",
        default=DEFAULT_PROD_DIR,
        help="Default production directory to trace",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        (
            "no_prod_trace: Mark test to skip production execution enforcement "
            "(e.g. meta-tests, smoke tests)."
        ),
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item: pytest.Item) -> Any:
    """
    Hook wrapping ONLY the test execution body (excluding setup/teardown fixtures).
    Installs sys.settrace to monitor frame calls into production code.
    """
    # 1. Check for opt-out marker
    if item.get_closest_marker("no_prod_trace"):
        yield
        return

    # 2. Resolve production directory root
    prod_dir_opt = item.config.getoption("--prod-dir") or item.config.getini("prod_dir")
    prod_dir_abs = os.path.abspath(prod_dir_opt)
    min_calls = item.config.getoption("--min-prod-calls")

    # Storage for captured production function call frames: (file, func_name, line)
    captured_calls: list[tuple[str, str, int]] = []

    def trace_calls(frame: Any, event: str, _arg: Any) -> Any:
        """
        Global tracer: Listens for 'call' events.
        Returning None disables line-level tracing for massive performance gains.
        """
        if event == "call":
            filename = os.path.abspath(frame.f_code.co_filename)
            # Filter strictly for files within the target production root
            if filename.startswith(prod_dir_abs):
                # Exclude tests if accidentally located in prod_dir
                if "tests" not in Path(filename).parts:
                    captured_calls.append((filename, frame.f_code.co_name, frame.f_lineno))
        return None

    # 3. Attach tracer during test execution
    previous_trace = sys.gettrace()
    sys.settrace(trace_calls)

    try:
        # Execute the test body
        outcome = yield
    finally:
        # Restore prior tracer state (e.g., if coverage/debugging is running)
        sys.settrace(previous_trace)

    # 4. Enforce verification gate if test didn't otherwise raise an exception
    if outcome.excinfo is None:
        unique_calls = set(captured_calls)
        if len(unique_calls) < min_calls:
            msg = (
                f"\n PHANTOM TEST DETECTED in '{item.nodeid}'!\n"
                f"   Expected at least {min_calls} call(s) into '{prod_dir_opt}/', "
                f"but recorded {len(unique_calls)}.\n"
                f"   The test either asserted tautologies (e.g., 'assert True'), "
                f"over-mocked the system, or failed to invoke the implementation under test."
            )
            pytest.fail(msg, pytrace=False)
