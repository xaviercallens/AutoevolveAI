"""`--write-heldout-baseline --k N` must reach write_heldout_baseline (TODO 2, pass@k gate)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parents[2]


def _load_workflow() -> ModuleType:
    path = REPO / "scripts/night_training_workflow.py"
    spec = importlib.util.spec_from_file_location("night_training_workflow_k_test", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_k_flag_is_forwarded_and_defaults_to_one(monkeypatch: pytest.MonkeyPatch) -> None:
    wf = _load_workflow()
    seen: list[int] = []
    monkeypatch.setattr(wf, "write_heldout_baseline", lambda out=None, k=1: seen.append(k) or {})
    assert wf.main(["--write-heldout-baseline", "--k", "3"]) == 0
    assert wf.main(["--write-heldout-baseline"]) == 0
    assert seen == [3, 1]


def test_k_below_one_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    wf = _load_workflow()
    called: list[int] = []
    monkeypatch.setattr(wf, "write_heldout_baseline", lambda out=None, k=1: called.append(k) or {})
    with pytest.raises(SystemExit) as exc:
        wf.main(["--write-heldout-baseline", "--k", "0"])
    assert exc.value.code == 2
    assert called == []
