import shutil
"""Tests for SandboxExecutor and AST safety scanner."""

import pytest

from anse.config import SandboxConfig
from anse.symbolic.sandbox import SandboxExecutor


@pytest.fixture
def sandbox():
    cfg = SandboxConfig(timeout_seconds=2.0)
    return SandboxExecutor(config=cfg)


def test_sandbox_clean_execution(sandbox):
    code = "print('Hello, ANSE!')"
    result = sandbox.execute(code)
    assert result.returncode == 0
    assert "Hello, ANSE!" in result.stdout
    assert not result.timed_out
    assert result.duration_ms > 0


def test_sandbox_syntax_error(sandbox):
    code = "def bad_syntax(:"
    result = sandbox.execute(code)
    assert result.returncode != 0
    assert "SyntaxError" in result.stderr


def test_sandbox_runtime_error(sandbox):
    code = "x = 1 / 0"
    result = sandbox.execute(code)
    assert result.returncode != 0
    assert "ZeroDivisionError" in result.stderr


def test_sandbox_timeout(sandbox):
    code = "import time\ntime.sleep(5)"
    result = sandbox.execute(code)
    assert result.timed_out is True
    assert result.returncode != 0


@pytest.mark.skipif(shutil.which('docker') is None, reason='Docker not installed')
def test_sandbox_ast_safety_detection(sandbox):
    sandbox._execute_tier2 = lambda c, b=None: __import__('anse.symbolic.sandbox', fromlist=['']).ExecutionResult(0, '', '', 2, False)
    code = "import os\nimport sys\nprint('danger')"
    result = sandbox.execute(code)
    # Detected dangerous imports: 'os', 'sys'
    assert "os" in result.dangerous_imports
    assert "sys" in result.dangerous_imports


@pytest.mark.skipif(shutil.which('docker') is None, reason='Docker not installed')
def test_sandbox_ast_safety_import_from(sandbox):
    sandbox._execute_tier2 = lambda c, b=None: __import__('anse.symbolic.sandbox', fromlist=['']).ExecutionResult(0, '', '', 2, False)
    code = "from os import system\nprint('danger')"
    result = sandbox.execute(code)
    assert "os" in result.dangerous_imports
    assert result.tier_used == 2  # Tier 2 fallback because of dangerous import


def test_sandbox_tier2_docker_missing(sandbox, monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "docker", None)

    # Force tier 2
    code = "import os\nprint('danger')"
    result = sandbox.execute(code, force_tier=2)
    assert result.returncode == 0
    assert "Docker unavailable, fell back to Tier-1" in result.stderr


def test_sandbox_tier2_execution_success(sandbox, monkeypatch):
    class MockDockerClient:
        class MockContainers:
            def run(self, *args, **kwargs):
                return b"hello docker"

        containers = MockContainers()

    import sys
    from unittest.mock import MagicMock

    docker_mock = MagicMock()
    docker_mock.from_env = lambda: MockDockerClient()
    monkeypatch.setitem(sys.modules, "docker", docker_mock)

    code = "import os\nprint('hello docker')"
    result = sandbox.execute(code, force_tier=2)

    assert result.tier_used == 2
    assert result.returncode == 0
    assert "hello docker" in result.stdout


def test_sandbox_tier2_execution_timeout(sandbox, monkeypatch):
    import requests

    class MockDockerClient:
        class MockContainers:
            def run(self, *args, **kwargs):
                raise requests.exceptions.ReadTimeout("Timeout")

        containers = MockContainers()

    import sys
    from unittest.mock import MagicMock

    docker_mock = MagicMock()
    docker_mock.from_env = lambda: MockDockerClient()
    monkeypatch.setitem(sys.modules, "docker", docker_mock)

    code = "import os\nimport time\ntime.sleep(5)"
    result = sandbox.execute(code, force_tier=2)

    assert result.tier_used == 2
    assert result.timed_out is True
    assert result.returncode == -1


def test_tier1_reports_user_oserror_traceback_not_runner_nameerror():
    result = SandboxExecutor().execute("raise OSError('disk on fire')", force_tier=1)
    assert result.returncode == 1
    assert "disk on fire" in result.stderr
    assert "NameError" not in result.stderr


def test_tier1_memory_limit_blocks_oversized_allocation():
    cfg = SandboxConfig(tier1_mem_limit_mb=512)
    result = SandboxExecutor(config=cfg).execute("x = bytearray(2 * 1024**3)", force_tier=1)
    assert result.returncode != 0
    assert "MemoryError" in result.stderr
