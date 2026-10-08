"""The nightly retrain must run every step with the interpreter that launched it (night 2026-10-08)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "nightly_retrain_at_5am.py"


def _load(monkeypatch: pytest.MonkeyPatch, use_uv: str | None):
    pytest.importorskip("gpu_lease", reason="needs /mnt/disks/disk-socrateai-local-1/gpu_lease")
    if use_uv is None:
        monkeypatch.delenv("AUTOEVOLVE_NIGHTLY_USE_UV", raising=False)
    else:
        monkeypatch.setenv("AUTOEVOLVE_NIGHTLY_USE_UV", use_uv)
    spec = importlib.util.spec_from_file_location(f"nightly_retrain_{use_uv}", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sys.path.insert(0, "/mnt/disks/disk-socrateai-local-1/gpu_lease")


def test_steps_default_to_the_launching_interpreter(monkeypatch: pytest.MonkeyPatch) -> None:
    m = _load(monkeypatch, None)
    assert m.STEP_PYTHON == [sys.executable]
    assert "uv" not in m.STEP_PYTHON


def test_uv_is_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    m = _load(monkeypatch, "1")
    assert m.STEP_PYTHON == ["uv", "run", "python"]
    other = _load(monkeypatch, "0")
    assert other.STEP_PYTHON == [sys.executable]


def test_no_step_hardcodes_uv_run() -> None:
    source = SCRIPT.read_text()
    assert '"uv", "run", "python", ' not in source
    assert source.count("*STEP_PYTHON") >= 8
