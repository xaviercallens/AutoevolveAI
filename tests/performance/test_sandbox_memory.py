"""
Unit tests for sandbox peak RAM and high-precision timing instrumentation.
"""

import pytest
from anse.config import SandboxConfig
from anse.symbolic.sandbox import ExecutionResult, SandboxExecutor


@pytest.fixture
def sandbox():
    cfg = SandboxConfig(timeout_seconds=3.0)
    return SandboxExecutor(config=cfg)


def test_sandbox_execution_result_has_peak_ram():
    res = ExecutionResult(
        stdout="",
        stderr="",
        returncode=0,
        timed_out=False,
        duration_ms=10.0,
        tier_used=1,
        peak_ram_mb=15.5,
    )
    assert res.peak_ram_mb == 15.5
    assert res.duration_ms == 10.0


def test_sandbox_records_positive_duration_and_ram(sandbox):
    code = "print('testing performance instrumentation')"
    result = sandbox.execute(code)
    assert result.returncode == 0
    assert result.duration_ms > 0
    assert result.peak_ram_mb > 0
    assert "testing performance instrumentation" in result.stdout


def test_sandbox_measures_memory_allocation(sandbox):
    # Allocate ~20-50MB of memory
    code = """
x = [i for i in range(1_000_000)]
print('Allocated elements:', len(x))
"""
    result = sandbox.execute(code)
    assert result.returncode == 0
    assert "Allocated elements: 1000000" in result.stdout
    # Python base memory + 1M list is typically > 20 MB
    assert result.peak_ram_mb >= 10.0


def test_sandbox_error_preserves_error_info(sandbox):
    code = "def syntax_err(:"
    result = sandbox.execute(code)
    assert result.returncode != 0
    assert "SyntaxError" in result.stderr
    assert result.peak_ram_mb >= 0.0


def test_sandbox_runtime_exception(sandbox):
    code = "raise ValueError('Custom crash for energy testing')"
    result = sandbox.execute(code)
    assert result.returncode != 0
    assert "ValueError: Custom crash for energy testing" in result.stderr
    assert result.peak_ram_mb >= 0.0


def test_sandbox_timeout_handling(sandbox):
    code = "import time\ntime.sleep(10)"
    result = sandbox.execute(code)
    assert result.timed_out is True
    assert result.returncode != 0
    assert result.duration_ms > 0
