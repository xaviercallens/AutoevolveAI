"""Hermetic branch-coverage tests for claude_workflow.py, context_manager.py, attestation_reporter.py."""

from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path
from typing import Any

import fakeredis
import httpx
import pytest

import attestation_reporter
import claude_workflow as cw
import context_manager

PY = shlex.quote(sys.executable)


@pytest.fixture(autouse=True)
def _isolated_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cw.WorkflowState, "STATE_FILE", tmp_path / "state.json")


def _task(cmd: str = "true", files: list[str] | None = None, tid: str = "T1") -> cw.Subtask:
    return cw.Subtask(id=tid, title="title", target_files=files or [], acceptance_command=cmd)


# ───────────────────────── WorkflowState ──────────────────────────


def test_state_missing_file_is_empty() -> None:
    s = cw.WorkflowState("goal")
    assert s.goal == "goal" and s.subtasks == []


def test_state_corrupt_or_unreadable_file_is_ignored(tmp_path: Path) -> None:
    (tmp_path / "state.json").write_text("{not json", encoding="utf-8")
    assert cw.WorkflowState("g").subtasks == []

    (tmp_path / "state.json").unlink()
    (tmp_path / "state.json").mkdir()  # exists() but read_text raises IsADirectoryError (OSError)
    assert cw.WorkflowState("g").goal == "g"


def test_state_roundtrip_and_transitions() -> None:
    s = cw.WorkflowState("goal")
    s.subtasks = [_task(tid="A"), _task(tid="B")]
    s.subtasks[0].last_error = "old"
    s.save()

    loaded = cw.WorkflowState()
    assert loaded.goal == "goal"
    assert [t.id for t in loaded.subtasks] == ["A", "B"]
    assert loaded.subtasks[0].status is cw.TaskStatus.PENDING

    active = loaded.get_active_subtask()
    assert active is not None and active.id == "A"
    loaded.mark_completed("nope")  # unknown id: no-op
    assert loaded.subtasks[0].status is cw.TaskStatus.PENDING
    loaded.mark_completed("A")
    assert loaded.subtasks[0].last_error is None
    loaded.mark_completed("B")
    assert loaded.get_active_subtask() is None
    assert cw.WorkflowState().subtasks[1].status is cw.TaskStatus.COMPLETED


def test_state_load_applies_optional_field_defaults(tmp_path: Path) -> None:
    (tmp_path / "state.json").write_text(
        json.dumps(
            {
                "subtasks": [
                    {"id": "X", "title": "t", "acceptance_command": "c", "status": "FAILED"}
                ]
            }
        ),
        encoding="utf-8",
    )
    s = cw.WorkflowState("ignored")
    t = s.subtasks[0]
    assert s.goal == "" and t.target_files == [] and t.max_retries == 3 and t.retry_count == 0
    assert t.last_error is None
    assert s.get_active_subtask() is None  # FAILED is not active


# ───────────────────────── stub detection ─────────────────────────


def test_stub_helpers() -> None:
    assert cw._has_suspicious_stub("x = 1") is False
    for marker in ("pass", "...", "NotImplementedError"):
        assert cw._has_suspicious_stub(f"a {marker} b")
    assert cw._has_naked_stub_lines("x = 1\n    pass\n") is False  # no def
    assert cw._has_naked_stub_lines("def f():\n    pass\n") is True
    assert cw._has_naked_stub_lines("def f():\n    ...\n") is True
    assert cw._has_naked_stub_lines("def f():\n    return 'pass'\n") is False


def test_check_file_stubs(tmp_path: Path) -> None:
    assert cw._check_file_stubs(tmp_path / "missing.py") == (True, "")
    txt = tmp_path / "a.txt"
    txt.write_text("pass")
    assert cw._check_file_stubs(txt) == (True, "")

    unreadable = tmp_path / "dir.py"
    unreadable.mkdir()
    ok, msg = cw._check_file_stubs(unreadable)
    assert ok is False and "Failed to read file" in msg

    clean = tmp_path / "clean.py"
    clean.write_text("def f():\n    return 1\n")
    assert cw._check_file_stubs(clean) == (True, "")

    subtle = tmp_path / "subtle.py"
    subtle.write_text("def f():\n    return 'pass'\n")  # marker present but not naked
    assert cw._check_file_stubs(subtle) == (True, "")

    naked = tmp_path / "naked.py"
    naked.write_text("def f():\n    pass\n")
    ok, msg = cw._check_file_stubs(naked)
    assert ok is False and "naked stubs" in msg


# ───────────────────────── verify_subtask ─────────────────────────


def test_verify_subtask_outcomes(tmp_path: Path) -> None:
    ok, msg = cw.verify_subtask(_task(f"{PY} -c 'import sys; sys.exit(0)'"))
    assert ok and "passed cleanly" in msg

    ok, msg = cw.verify_subtask(
        _task(f"{PY} -c 'import sys; sys.stderr.write(\"boom\"); sys.exit(3)'")
    )
    assert not ok and "exit code 3" in msg and "boom" in msg

    ok, msg = cw.verify_subtask(_task(f"{PY} -c 'print(\"only-stdout\"); raise SystemExit(1)'"))
    assert not ok and "only-stdout" in msg

    stub = tmp_path / "stub.py"
    stub.write_text("def f():\n    pass\n")
    ok, msg = cw.verify_subtask(_task("true", files=[str(stub)]))
    assert not ok and "Anti-Stub" in msg

    clean = tmp_path / "clean.py"
    clean.write_text("def f():\n    return 1\n")
    ok, _ = cw.verify_subtask(_task("true", files=[str(clean), str(tmp_path / "absent.py")]))
    assert ok  # clean files pass the audit and the loop proceeds to the acceptance command


# ───────────────────────── gateway phases ─────────────────────────


class FakeHttpResp:
    def __init__(self, payload: dict[str, Any], fail: bool = False) -> None:
        self._p, self._fail = payload, fail

    def raise_for_status(self) -> None:
        if self._fail:
            raise httpx.HTTPStatusError("bad", request=None, response=None)  # type: ignore[arg-type]

    def json(self) -> dict[str, Any]:
        return self._p


class FakeHttpClient:
    def __init__(self, fail: bool = False) -> None:
        self.fail, self.calls = fail, []

    def post(self, url: str, json: Any, headers: Any, timeout: float) -> FakeHttpResp:
        self.calls.append((url, json, headers, timeout))
        return FakeHttpResp({"echo": url}, self.fail)


def test_phases_with_injected_client() -> None:
    c = FakeHttpClient()
    plan = cw.run_planning_phase("build it", "http://gw/", client=c)  # type: ignore[arg-type]
    assert plan["phase"] == "PLANNING" and plan["success"] and "build it" in json.dumps(c.calls[0][1])
    assert c.calls[0][0] == "http://gw/v1beta/models/gemini-3.1-pro:generateContent"

    ex = cw.run_execution_phase("S1", "do it", client=c)  # type: ignore[arg-type]
    assert ex["subtask_id"] == "S1" and c.calls[1][2]["X-Subtask-ID"] == "S1"

    passed, msg = cw.run_verification_phase(_task(f"{PY} -c 'pass'"), client=c)  # type: ignore[arg-type]
    assert passed and "passed" in msg
    assert "PASSED" in c.calls[2][1]["contents"][0]["parts"][0]["text"]


def test_phase_uses_managed_client_when_none_injected(monkeypatch: pytest.MonkeyPatch) -> None:
    real_client = httpx.Client
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(str(request.url))
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(
        cw.httpx,
        "Client",
        lambda timeout: real_client(timeout=timeout, transport=httpx.MockTransport(handler)),
    )
    out = cw.run_planning_phase("goal")
    assert out["raw_response"] == {"ok": True} and seen


def test_verification_phase_swallows_gateway_errors_and_reports_failure() -> None:
    c = FakeHttpClient(fail=True)
    passed, msg = cw.run_verification_phase(_task("false"), client=c)  # type: ignore[arg-type]
    assert passed is False and "Acceptance command failed" in msg
    assert "FAILED" in c.calls[0][1]["contents"][0]["parts"][0]["text"]


def test_planning_phase_propagates_gateway_errors() -> None:
    with pytest.raises(httpx.HTTPStatusError):
        cw.run_planning_phase("g", client=FakeHttpClient(fail=True))  # type: ignore[arg-type]


# ───────────────────────── context_manager ────────────────────────


def test_context_manager_inline_and_offload(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setattr(context_manager, "SCRATCHPAD_DIR", scratch)

    small = "\n".join(str(i) for i in range(context_manager.MAX_INLINE_LINES))
    assert context_manager.truncate_and_offload_context("t", small) == small

    big = "\n".join(f"L{i}" for i in range(200))
    out = context_manager.truncate_and_offload_context("t", big)
    assert "200 lines total" in out and "L0" in out and "L199" in out and "L100" not in out
    (log,) = scratch.glob("t_*.log")
    assert log.read_text(encoding="utf-8") == big


# ───────────────────────── attestation_reporter ───────────────────


def test_record_verdict_passed_failed_and_no_subtask() -> None:
    r = fakeredis.FakeRedis(decode_responses=True)
    attestation_reporter.record_attestation_verdict(
        "tr1", "sub1", True, ["ok"], "x" * 3000, redis_client=r
    )
    h = r.hgetall("antigravity:attestation:tr1")
    assert h["verdict"] == "PASSED" and len(h["test_stdout"]) == 2000
    assert r.sismember("antigravity:subtasks:completed", "sub1")
    assert r.lrange("antigravity:subtask:sub1:traces", 0, -1) == ["tr1"]

    attestation_reporter.record_attestation_verdict("tr2", "sub2", False, ["bad"], redis_client=r)
    assert r.hget("antigravity:attestation:tr2", "verdict") == "FAILED"
    assert r.sismember("antigravity:subtasks:in_progress", "sub2")

    attestation_reporter.record_attestation_verdict("tr3", "", True, [], redis_client=r)
    assert r.exists("antigravity:attestation:tr3")
    assert r.scard("antigravity:subtasks:completed") == 1  # empty subtask id not tracked


def test_record_verdict_swallows_redis_errors(capsys: pytest.CaptureFixture[str]) -> None:
    class Boom:
        def pipeline(self) -> Any:
            raise ConnectionError("no redis")

    attestation_reporter.record_attestation_verdict("t", "s", True, [], redis_client=Boom())
    assert "Failed to record attestation verdict" in capsys.readouterr().out


def test_record_verdict_builds_default_client(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = fakeredis.FakeRedis(decode_responses=True)
    made: dict[str, Any] = {}

    def factory(**kw: Any) -> Any:
        made.update(kw)
        return fake

    monkeypatch.setattr(attestation_reporter.redis, "Redis", factory)
    attestation_reporter.record_attestation_verdict("t9", "", False, ["r"])
    assert made["decode_responses"] is True
    assert fake.hget("antigravity:attestation:t9", "verdict") == "FAILED"
