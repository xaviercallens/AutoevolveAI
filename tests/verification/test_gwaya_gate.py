"""Tests for anse.verification.gwaya_gate. Only the bubblewrap sandbox (external I/O) is stubbed."""

from __future__ import annotations

import pytest

pytest.importorskip("gwaya")
from anse.verification.gwaya_gate import GateVerdict, verify_python, verify_rust  # noqa: E402

GOOD = "def add(a: int, b: int) -> int:\n    return a + b\n"


def _runner(ok: bool, out: str = "", err: str = "", timed_out: bool = False):
    calls: list[dict] = []

    def run(cmd, **kw):
        calls.append({"cmd": cmd, **kw})
        return ok, out, err, timed_out

    run.calls = calls  # type: ignore[attr-defined]
    return run


def test_stub_is_rejected_without_ever_touching_the_sandbox() -> None:
    run = _runner(True)
    v = verify_python("def f(x):\n    pass\n", "assert f(1) is None", sandbox_available=lambda: True, runner=run)
    assert v.status == "REJECT" and not v.accepted
    assert any("pass" in r for r in v.reasons)
    assert run.calls == []


def test_no_isolation_means_blocked_not_accepted() -> None:
    run = _runner(True)
    v = verify_python(GOOD, "assert add(1, 2) == 3", sandbox_available=lambda: False, runner=run)
    assert v.status == "BLOCKED" and not v.accepted
    assert run.calls == []


def test_tests_are_appended_and_clean_exit_is_accepted() -> None:
    run = _runner(True)
    v = verify_python(GOOD, "assert add(1, 2) == 3", sandbox_available=lambda: True, runner=run)
    assert v == GateVerdict("ACCEPT", "python")
    assert "assert add(1, 2) == 3" in run.calls[0]["files"]["cand.py"]
    assert run.calls[0]["cmd"][1] == "-I"


def test_failing_tests_are_rejected_with_stderr() -> None:
    run = _runner(False, err="AssertionError: add(1,2)")
    v = verify_python(GOOD, "assert add(1, 2) == 4", sandbox_available=lambda: True, runner=run)
    assert v.status == "REJECT" and "AssertionError" in v.reasons[0]


def test_timeout_and_unverified_stderr_are_blocked() -> None:
    t = verify_python(GOOD, "while True: pass", sandbox_available=lambda: True, runner=_runner(False, timed_out=True))
    u = verify_python(GOOD, "x", sandbox_available=lambda: True,
                      runner=_runner(False, err="UNVERIFIED: bwrap unavailable"))
    assert t.status == "BLOCKED" and u.status == "BLOCKED"


def test_rust_placeholder_rejected_and_missing_toolchain_blocked() -> None:
    assert verify_rust("fn f() -> i32 { todo!() }").status == "REJECT"

    class NoRustc:
        def verify_snippet(self, code: str):
            from gwaya.oracles import OracleResult

            return OracleResult(False, "rustc", "UNVERIFIED: rustc toolchain not installed",
                                details={"unverified": True})

    assert verify_rust("pub fn f() -> i32 { 1 }", oracle=NoRustc()).status == "BLOCKED"  # type: ignore[arg-type]
