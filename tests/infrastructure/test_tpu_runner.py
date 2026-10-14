"""Tests for anse.infrastructure.tpu_runner. Only the gcloud subprocess is mocked."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from anse.infrastructure.tpu_runner import (
    TPURunError,
    TPUTarget,
    fetch,
    run_command,
    run_job,
    upload,
)

T = TPUTarget("tpu-x", "us-west4-a")


def _ok(stdout: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], 0, stdout=stdout, stderr="")


def _patch_run(result: subprocess.CompletedProcess[str]):
    return (
        patch("anse.infrastructure.tpu_runner.shutil.which", return_value="/usr/bin/gcloud"),
        patch("anse.infrastructure.tpu_runner.subprocess.run", return_value=result),
    )


def test_from_env_requires_both_vars() -> None:
    with patch.dict("os.environ", {"AUTOEVOLVE_TPU_NAME": "n"}, clear=True), pytest.raises(TPURunError):
        TPUTarget.from_env()
    with patch.dict("os.environ", {"AUTOEVOLVE_TPU_NAME": "n", "AUTOEVOLVE_TPU_ZONE": "z"}, clear=True):
        target = TPUTarget.from_env()
    assert (target.name, target.zone, target.internal_ip) == ("n", "z", True)


def test_run_command_activates_venv_and_uses_internal_ip() -> None:
    which, run = _patch_run(_ok("hello\n"))
    with which, run as mock_run:
        out = run_command(T, "python x.py")
    argv = mock_run.call_args.args[0]
    assert out == "hello\n"
    assert "--internal-ip" in argv and "--zone=us-west4-a" in argv
    assert argv[-1] == "--command=. ~/venv-tpu/bin/activate && python x.py"


def test_failure_raises_with_stderr() -> None:
    bad = subprocess.CompletedProcess([], 3, stdout="", stderr="PERMISSION_DENIED")
    which, run = _patch_run(bad)
    with which, run, pytest.raises(TPURunError, match="PERMISSION_DENIED"):
        run_command(T, "true")


def test_timeout_is_reported() -> None:
    with (
        patch("anse.infrastructure.tpu_runner.shutil.which", return_value="/usr/bin/gcloud"),
        patch("anse.infrastructure.tpu_runner.subprocess.run",
              side_effect=subprocess.TimeoutExpired("gcloud", 1)),
        pytest.raises(TPURunError, match="timed out"),
    ):
        run_command(T, "sleep 99", timeout_s=1)


def test_upload_rejects_missing_local_file(tmp_path: Path) -> None:
    with pytest.raises(TPURunError, match="missing"):
        upload(T, [tmp_path / "nope.py"])


def test_run_job_orders_upload_run_fetch(tmp_path: Path) -> None:
    f = tmp_path / "a.py"
    f.write_text("print(1)\n")
    which, run = _patch_run(_ok("done\n"))
    with which, run as mock_run:
        out, got = run_job(T, [f], "python a.py", ["r.json"], tmp_path / "out")
    verbs = [c.args[0][4] for c in mock_run.call_args_list]
    assert verbs == ["scp", "ssh", "scp"]
    assert out == "done\n" and got == [tmp_path / "out" / "r.json"]


def test_fetch_creates_destination(tmp_path: Path) -> None:
    which, run = _patch_run(_ok())
    with which, run:
        fetch(T, ["a.json"], tmp_path / "deep" / "dir")
    assert (tmp_path / "deep" / "dir").is_dir()


def test_no_files_and_no_results_only_runs_the_command(tmp_path: Path) -> None:
    which, run = _patch_run(_ok("x\n"))
    with which, run as mock_run:
        out, got = run_job(T, [], "python -V", [], tmp_path)
    assert [c.args[0][4] for c in mock_run.call_args_list] == ["ssh"]
    assert out == "x\n" and got == []
