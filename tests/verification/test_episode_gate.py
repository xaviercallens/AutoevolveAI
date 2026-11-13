"""Tests for anse.verification.episode_gate and its use by the mix builder. The gate callable is injected."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

pytest.importorskip("gwaya")
from anse.verification.episode_gate import DEMOTION_ENERGY, apply_gate  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from ltm_learning_mix import load_verified  # noqa: E402


def _gate(status: str, reasons: tuple[str, ...] = ()):
    return lambda code, tests: SimpleNamespace(status=status, reasons=reasons)


def test_reject_demotes_a_converged_episode() -> None:
    g = apply_gate("def f(): pass", "assert f() is None", True, 0.0, gate=_gate("REJECT", ("stub",)))
    assert g.converged is False and g.energy == DEMOTION_ENERGY
    assert g.meta["demoted"] and not g.meta["confirmed"]


def test_accept_confirms_and_changes_nothing() -> None:
    g = apply_gate("x", "y", True, 0.5, gate=_gate("ACCEPT"))
    assert (g.converged, g.energy, g.meta["confirmed"]) == (True, 0.5, True)


def test_blocked_never_upgrades_or_demotes() -> None:
    ok = apply_gate("x", "y", True, 0.5, gate=_gate("BLOCKED", ("no bwrap",)))
    bad = apply_gate("x", "y", False, 200.0, gate=_gate("BLOCKED"))
    assert ok.converged is True and ok.meta["confirmed"] is False
    assert bad.converged is False and bad.energy == 200.0


def test_accept_of_a_failed_episode_is_flagged_not_trusted() -> None:
    g = apply_gate("x", "y", False, 100.0, gate=_gate("ACCEPT"))
    assert g.converged is False and "disagreement" in g.meta and g.meta["confirmed"] is False


def test_real_gate_rejects_a_stub_that_passes_its_test() -> None:
    g = apply_gate("def f(x):\n    pass\n", "assert f(1) is None", True, 0.0)
    assert g.converged is False and g.meta["status"] == "REJECT"


def _episode(task: str, gate_meta: dict | None) -> str:
    meta = {"tests_total": 1, "tests_passed": 1}
    if gate_meta is not None:
        meta["gwaya"] = gate_meta
    return json.dumps({"task": task, "prompt": "p", "code": "c", "converged": True, "metadata": meta})


def test_require_gate_keeps_only_confirmed_rows(tmp_path: Path) -> None:
    f = tmp_path / "h.jsonl"
    f.write_text("\n".join([
        _episode("legacy", None),
        _episode("blocked", {"status": "BLOCKED", "confirmed": False}),
        _episode("accepted", {"status": "ACCEPT", "confirmed": True}),
    ]) + "\n")
    assert len(load_verified(f)) == 3
    strict = load_verified(f, require_gate=True)
    assert [r["gate"] for r in strict] == ["ACCEPT"]
