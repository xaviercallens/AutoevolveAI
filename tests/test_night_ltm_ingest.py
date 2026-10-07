"""Tests for the scheduling helper of scripts/night_ltm_ingest.py."""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "night_ltm_ingest.py"


def _load():
    pytest.importorskip("gpu_lease", reason="needs /mnt/disks/disk-socrateai-local-1/gpu_lease")
    spec = importlib.util.spec_from_file_location("night_ltm_ingest", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["night_ltm_ingest"] = module
    spec.loader.exec_module(module)
    return module


sys.path.insert(0, "/mnt/disks/disk-socrateai-local-1/gpu_lease")


def test_at_utc_rolls_to_next_day_when_time_has_passed() -> None:
    m = _load()
    evening = datetime(2026, 10, 7, 21, 40, tzinfo=timezone.utc)
    target = m.at_utc("04:40", evening)
    assert target == datetime(2026, 10, 8, 4, 40, tzinfo=timezone.utc)
    assert (target - evening).total_seconds() == 7 * 3600


def test_at_utc_same_day_when_still_ahead() -> None:
    m = _load()
    early = datetime(2026, 10, 8, 1, 0, tzinfo=timezone.utc)
    target = m.at_utc("04:25", early)
    assert target.day == 8
    assert target.hour == 4 and target.minute == 25
