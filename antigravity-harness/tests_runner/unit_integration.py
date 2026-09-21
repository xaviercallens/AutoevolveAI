"""
Unit & Integration Test Runner: Pytest and Testcontainers orchestration.
Executes test suites with deterministic timeouts, memory boundaries, and structured reports.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TestRunSummary:
    """Structured report from test execution."""

    success: bool
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration_seconds: float = 0.0
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    failures: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        status = "PASSED" if self.success else "FAILED"
        return (
            f"Test Suite {status} in {self.duration_seconds:.2f}s: "
            f"{self.passed} passed, {self.failed} failed, {self.skipped} skipped (code {self.exit_code})"
        )


class UnitIntegrationRunner:
    """Executes pytest suites with isolation and captures structured telemetry."""

    def __init__(
        self,
        default_timeout_seconds: float = 120.0,
        use_containers: bool = False,
    ) -> None:
        self.default_timeout = default_timeout_seconds
        self.use_containers = use_containers

    @property
    def is_docker_available(self) -> bool:
        """Checks if Docker daemon/CLI is available for Testcontainers."""
        return shutil.which("docker") is not None

    def run_pytest(
        self,
        test_path: str | Path,
        extra_args: list[str] | None = None,
        timeout: float | None = None,
    ) -> TestRunSummary:
        """
        Executes pytest on the specified target path.
        """
        path = Path(test_path)
        actual_timeout = timeout or self.default_timeout

        cmd = ["pytest", str(path)]
        if extra_args:
            cmd.extend(extra_args)

        # Prefer uv run pytest if uv is present
        if shutil.which("uv"):
            cmd = ["uv", "run"] + cmd

        start_time = time.perf_counter()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=actual_timeout,
            )
            elapsed = time.perf_counter() - start_time

            stdout = proc.stdout
            stderr = proc.stderr

            passed, failed, skipped = self._parse_pytest_counts(stdout)
            failures = self._extract_failure_messages(stdout)

            success = proc.returncode == 0

            return TestRunSummary(
                success=success,
                total_tests=passed + failed + skipped,
                passed=passed,
                failed=failed,
                skipped=skipped,
                duration_seconds=elapsed,
                stdout=stdout,
                stderr=stderr,
                exit_code=proc.returncode,
                failures=failures,
            )

        except subprocess.TimeoutExpired:
            elapsed = time.perf_counter() - start_time
            return TestRunSummary(
                success=False,
                duration_seconds=elapsed,
                exit_code=-1,
                failures=[f"Test execution timed out after {actual_timeout}s."],
            )
        except Exception as exc:
            elapsed = time.perf_counter() - start_time
            return TestRunSummary(
                success=False,
                duration_seconds=elapsed,
                exit_code=-2,
                failures=[f"Failed to launch test runner: {exc}"],
            )

    def _parse_pytest_counts(self, output: str) -> tuple[int, int, int]:
        """Parses output line like '== 87 passed, 43 skipped in 59.56s =='."""
        passed, failed, skipped = 0, 0, 0

        p_match = re.search(r"(\d+)\s+passed", output)
        if p_match:
            passed = int(p_match.group(1))

        f_match = re.search(r"(\d+)\s+failed", output)
        if f_match:
            failed = int(f_match.group(1))

        s_match = re.search(r"(\d+)\s+skipped", output)
        if s_match:
            skipped = int(s_match.group(1))

        return passed, failed, skipped

    def _extract_failure_messages(self, output: str) -> list[str]:
        """Extracts failure headers and error messages from pytest summary."""
        failures: list[str] = []
        in_failure = False
        current_failure: list[str] = []

        for line in output.splitlines():
            if line.startswith("FAILURES"):
                in_failure = True
                continue
            if line.startswith("====") and in_failure:
                if current_failure:
                    failures.append("\n".join(current_failure[:10]))
                    current_failure = []
                in_failure = False

            if in_failure:
                if line.startswith("___"):
                    if current_failure:
                        failures.append("\n".join(current_failure[:10]))
                        current_failure = []
                    current_failure.append(line)
                elif current_failure:
                    current_failure.append(line)

        if current_failure:
            failures.append("\n".join(current_failure[:10]))

        return failures

    def run_with_junit_xml(
        self,
        test_path: str | Path,
        xml_output_path: str | Path,
        extra_args: list[str] | None = None,
    ) -> TestRunSummary:
        """Runs pytest and generates a standardized JUnit XML artifact."""
        xml_p = Path(xml_output_path)
        xml_p.parent.mkdir(parents=True, exist_ok=True)
        args = ["--junitxml", str(xml_p)]
        if extra_args:
            args.extend(extra_args)
        return self.run_pytest(test_path, extra_args=args)

    def group_failures_by_exception(self, failures: list[str]) -> dict[str, list[str]]:
        """Categorizes failure messages by their top-level exception class."""
        grouped: dict[str, list[str]] = {}
        exc_pattern = re.compile(r"([A-Za-z0-9_]+Error|[A-Za-z0-9_]+Exception):")

        for failure in failures:
            match = exc_pattern.search(failure)
            category = match.group(1) if match else "AssertionOrGeneralFailure"
            grouped.setdefault(category, []).append(failure)

        return grouped
