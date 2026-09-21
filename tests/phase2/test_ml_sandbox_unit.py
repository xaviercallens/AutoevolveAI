from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from anse.config import SandboxConfig
from anse.symbolic.ml_sandbox import MLSandboxExecutor, _parse_ml_stats, _tier1_ml_execute


def test_ml_sandbox_executor_init() -> None:
    executor = MLSandboxExecutor()
    assert executor._cfg is not None

    cfg = SandboxConfig(timeout_seconds=5)
    executor2 = MLSandboxExecutor(cfg=cfg)
    assert executor2._cfg.timeout_seconds == 5


@patch("anse.symbolic.ml_sandbox.subprocess.run")
def test_tier1_ml_execute_success(mock_run: MagicMock) -> None:
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = "output"
    mock_proc.stderr = ""
    mock_run.return_value = mock_proc

    result = _tier1_ml_execute("print('hello')", timeout=10.0)

    assert mock_run.called is True
    assert result.returncode == 0
    assert result.timed_out is False
    assert result.parameters == 0
    assert result.stdout == "output"


@patch("anse.symbolic.ml_sandbox.subprocess.run")
def test_tier1_ml_execute_timeout(mock_run: MagicMock) -> None:
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="python", timeout=10.0)

    result = _tier1_ml_execute("while True: pass", timeout=10.0)

    assert result.timed_out is True
    assert result.returncode == -1
    assert "timed out after 10.0s" in result.stderr


def test_parse_ml_stats_file_exists(tmp_path: Path) -> None:
    stats_file = tmp_path / "_stats.json"
    stats_data = {
        "parameters": 100,
        "accuracy": 0.9,
        "val_loss": 0.5,
        "train_loss": 0.4,
        "duration_ms": 150.0,
        "is_shape_mismatch": False,
        "is_oom": False,
    }
    stats_file.write_text(json.dumps(stats_data))

    params, acc, val_loss, train_loss, elapsed, mismatch, oom = _parse_ml_stats(
        stats_file, 0, "", 10.0
    )

    assert params == 100
    assert acc == 0.9
    assert val_loss == 0.5
    assert train_loss == 0.4
    assert elapsed == 150.0
    assert mismatch is False
    assert oom is False


def test_parse_ml_stats_shape_mismatch() -> None:
    stats_file = Path("nonexistent.json")

    params, acc, val_loss, train_loss, elapsed, mismatch, oom = _parse_ml_stats(
        stats_file, 1, "RuntimeError: size mismatch at...", 10.0
    )

    assert mismatch is True
    assert oom is False


def test_parse_ml_stats_oom() -> None:
    stats_file = Path("nonexistent.json")

    params, acc, val_loss, train_loss, elapsed, mismatch, oom = _parse_ml_stats(
        stats_file, 1, "RuntimeError: CUDA out of memory", 10.0
    )

    assert oom is True
    assert mismatch is False
