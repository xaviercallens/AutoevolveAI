"""Hermetic branch-coverage tests for gateway.py (no network, no real Redis)."""

from __future__ import annotations

import asyncio
import json
import runpy
from collections.abc import AsyncIterator
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import fakeredis
import httpx
import pytest
import redis.asyncio as aioredis
from fastapi.testclient import TestClient

import gateway

GEMINI_PATH = "v1beta/models/gemini-3.1-pro:generateContent"


# ─────────────────────────────── fakes ───────────────────────────────


class FakeResp:
    def __init__(
        self,
        status_code: int = 200,
        content: bytes = b'{"ok": true}',
        json_data: Any = None,
        headers: dict[str, str] | None = None,
        json_error: Exception | None = None,
        chunks: list[bytes] | None = None,
    ) -> None:
        self.status_code = status_code
        self.content = content
        self._json = json_data
        self._json_error = json_error
        self.headers = headers if headers is not None else {"content-type": "application/json"}
        self._chunks = chunks or []
        self.closed = False

    def json(self) -> Any:
        if self._json_error is not None:
            raise self._json_error
        return self._json

    async def aiter_bytes(self) -> AsyncIterator[bytes]:
        for c in self._chunks:
            yield c

    async def aclose(self) -> None:
        self.closed = True


class FakePool:
    """Stand-in for gateway.client_pool with scriptable behaviour."""

    def __init__(self) -> None:
        self.request_result: Any = FakeResp()
        self.post_result: Any = FakeResp()
        self.stream_result: FakeResp = FakeResp(chunks=[b"a", b"b"])
        self.calls: list[tuple[str, Any]] = []
        self.closed = False

    @staticmethod
    def _give(result: Any) -> Any:
        if isinstance(result, Exception):
            raise result
        return result

    async def request(self, method: str, url: str, **kw: Any) -> Any:
        self.calls.append(("request", (method, url, kw)))
        return self._give(self.request_result)

    async def post(self, url: str, **kw: Any) -> Any:
        self.calls.append(("post", (url, kw)))
        return self._give(self.post_result)

    def build_request(self, **kw: Any) -> dict[str, Any]:
        self.calls.append(("build_request", kw))
        return kw

    async def send(self, req: Any, stream: bool = False) -> FakeResp:
        self.calls.append(("send", req))
        return self.stream_result

    async def aclose(self) -> None:
        self.closed = True


OPENAI_OK = {
    "choices": [{"message": {"content": "hi"}, "finish_reason": "stop"}],
    "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3},
}


@pytest.fixture()
def pool(monkeypatch: pytest.MonkeyPatch) -> FakePool:
    p = FakePool()
    monkeypatch.setattr(gateway, "client_pool", p)
    monkeypatch.setattr(gateway, "redis_client", None)
    return p


@pytest.fixture()
def client(pool: FakePool) -> TestClient:
    return TestClient(gateway.app)


# ─────────────────────────── pure helpers ────────────────────────────


def test_safe_decode_payload_all_branches() -> None:
    assert gateway._safe_decode_payload(b'{"a": 1}') == {"a": 1}
    assert gateway._safe_decode_payload(b"not json") == "not json"
    # invalid UTF-8 raises UnicodeDecodeError (generic branch) then is decoded with replacement
    assert gateway._safe_decode_payload(b"\xff\xfe") == "��"


def test_classify_phase_by_text() -> None:
    assert gateway._classify_phase_by_text("please DECOMPOSE this")[1] == "PLANNING"
    assert gateway._classify_phase_by_text("run test now")[1] == "VERIFICATION"
    assert gateway._classify_phase_by_text("write code")[1] == "EXECUTION"


@pytest.mark.parametrize(
    "phase,expected",
    [
        ("Plan", "PLANNING"),
        (" architect ", "PLANNING"),
        ("verify", "VERIFICATION"),
        ("REVIEW", "VERIFICATION"),
        ("exec", "EXECUTION"),
        ("diff", "EXECUTION"),
    ],
)
def test_resolve_target_model_explicit_phase(phase: str, expected: str) -> None:
    assert gateway.resolve_target_model(phase, {})[1] == expected


def test_resolve_target_model_path_and_text() -> None:
    assert gateway.resolve_target_model(None, {}, path="models/gemini-3.8-flash:x") == (
        gateway.MODEL_EXECUTION,
        "EXECUTION",
    )
    assert gateway.resolve_target_model("bogus", {}, path="models/gemini-3.1-pro:x") == (
        gateway.MODEL_PLANNING,
        "PLANNING",
    )
    body = {
        "contents": [
            {"parts": [{"inlineData": {}}, {"text": "please audit the diff"}]},
        ]
    }
    assert gateway.resolve_target_model(None, body)[1] == "VERIFICATION"
    assert gateway.resolve_target_model(None, {})[1] == "EXECUTION"


def test_extract_system_messages() -> None:
    assert gateway._extract_system_messages({}) == []
    assert gateway._extract_system_messages({"system_instruction": {"parts": [{"x": 1}]}}) == []
    got = gateway._extract_system_messages(
        {"system_instruction": {"parts": [{"text": "a"}, {"other": 1}, {"text": "b"}]}}
    )
    assert got == [{"role": "system", "content": "a\nb"}]


def test_extract_content_messages() -> None:
    req = {
        "contents": [
            {"role": "user", "parts": [{"text": "q"}]},
            {"role": "model", "parts": [{"functionCall": {"name": "f"}}, {"text": "t"}]},
            {"role": "user", "parts": [{"inlineData": {}}]},  # nothing extractable
        ]
    }
    msgs = gateway._extract_content_messages(req)
    assert msgs[0] == {"role": "user", "content": "q"}
    assert msgs[1]["role"] == "assistant"
    assert '<tool_call>{"name": "f"}</tool_call>' in msgs[1]["content"]
    assert len(msgs) == 2


def test_gemini_to_openai_payload_defaults_and_overrides() -> None:
    p = gateway.gemini_to_openai_payload({"contents": [{"role": "user", "parts": [{"text": "x"}]}]})
    assert p["temperature"] == 0.1 and p["top_p"] == 0.95 and p["max_tokens"] == 4096
    p = gateway.gemini_to_openai_payload(
        {"generationConfig": {"temperature": 0.5, "topP": 0.5, "maxOutputTokens": 9}}, "m"
    )
    assert (p["model"], p["temperature"], p["top_p"], p["max_tokens"]) == ("m", 0.5, 0.5, 9)


def test_extract_tool_calls_from_text() -> None:
    assert gateway._extract_tool_calls_from_text("plain") == [{"text": "plain"}]
    assert gateway._extract_tool_calls_from_text("<tool_call>only-open") == [
        {"text": "<tool_call>only-open"}
    ]
    ok = gateway._extract_tool_calls_from_text('<tool_call>{"name": "f"}</tool_call>')
    assert ok == [{"functionCall": {"name": "f"}}]
    bad = "<tool_call>{oops</tool_call>"
    assert gateway._extract_tool_calls_from_text(bad) == [{"text": bad}]
    # pathological nesting raises RecursionError, exercising the generic handler
    deep = "<tool_call>" + "[" * 200000 + "</tool_call>"
    assert gateway._extract_tool_calls_from_text(deep) == [{"text": deep}]


def test_openai_to_gemini_response_variants() -> None:
    assert gateway.openai_to_gemini_response({}) == {"candidates": []}

    out = gateway.openai_to_gemini_response(OPENAI_OK)
    cand = out["candidates"][0]
    assert cand["finishReason"] == "STOP"
    assert cand["content"]["parts"] == [{"text": "hi"}]
    assert out["usageMetadata"]["totalTokenCount"] == 3

    deep_args = "[" * 200000
    resp = {
        "choices": [
            {
                "message": {
                    "content": None,
                    "tool_calls": [
                        {"function": {"name": "a", "arguments": '{"x": 1}'}},
                        {"function": {"name": "b", "arguments": {"y": 2}}},
                        {"function": {"name": "c", "arguments": "{bad"}},
                        {"function": {"name": "d", "arguments": deep_args}},
                        {},
                    ],
                },
                "finish_reason": "length",
            }
        ]
    }
    out = gateway.openai_to_gemini_response(resp)
    parts = out["candidates"][0]["content"]["parts"]
    assert out["candidates"][0]["finishReason"] == "MAX_TOKENS"
    assert parts[1] == {"functionCall": {"name": "a", "args": {"x": 1}}}
    assert parts[2]["functionCall"]["args"] == {"y": 2}
    assert parts[3]["functionCall"]["args"] == {"raw": "{bad"}
    assert parts[4]["functionCall"]["args"] == {"raw": deep_args}
    assert parts[5]["functionCall"] == {"name": "", "args": {}}
    assert out["usageMetadata"]["promptTokenCount"] == 0


def test_routing_helpers() -> None:
    assert gateway._build_upstream_url("p", None) == f"{gateway.UPSTREAM_GEMINI}/p"
    assert gateway._build_upstream_url("p", "a=1") == f"{gateway.UPSTREAM_GEMINI}/p?a=1"
    assert gateway._should_force_local("TRUE", "auto")
    assert gateway._should_force_local("false", "Local")
    assert not gateway._should_force_local("false", "auto")


# ────────────────────────── redis logging ────────────────────────────


def _log(**over: Any) -> Any:
    kw: dict[str, Any] = dict(
        session_id="s1",
        endpoint="/e",
        request_headers={"h": "v"},
        request_body=b'{"q": 1}',
        response_body=b"raw",
        status_code=200,
        latency_ms=1.5,
    )
    kw.update(over)
    return gateway.log_interaction_to_redis(**kw)


def test_log_interaction_noop_without_redis(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gateway, "redis_client", None)
    assert asyncio.run(_log()) is None


def test_log_interaction_writes_stream_and_traces(monkeypatch: pytest.MonkeyPatch) -> None:
    async def run() -> tuple[int, int, int, bytes | None]:
        fake = fakeredis.aioredis.FakeRedis()
        monkeypatch.setattr(gateway, "redis_client", fake)
        await _log(event_id="e1", subtask_id="t1")
        await _log(event_id="e2")  # no subtask → skips subtask list
        return (
            await fake.xlen("antigravity:stream:audit"),
            await fake.llen("antigravity:session:s1:traces"),
            await fake.llen("antigravity:subtask:t1:traces"),
            await fake.get("antigravity:trace:e1"),
        )

    xlen, sess, sub, trace = asyncio.run(run())
    assert (xlen, sess, sub) == (2, 2, 1)
    assert trace is not None and json.loads(trace)["subtask_id"] == "t1"


@pytest.mark.parametrize("exc", [aioredis.RedisError("boom"), RuntimeError("boom")])
def test_log_interaction_swallows_errors(monkeypatch: pytest.MonkeyPatch, exc: Exception) -> None:
    pipe = MagicMock()

    async def bad_execute() -> None:
        raise exc

    pipe.execute = bad_execute
    monkeypatch.setattr(gateway, "redis_client", SimpleNamespace(pipeline=lambda: pipe))
    assert asyncio.run(_log(subtask_id="t")) is None


# ─────────────────────── local inference / lifespan ───────────────────


def _local(**over: Any) -> Any:
    kw: dict[str, Any] = dict(
        gemini_json={"contents": [{"role": "user", "parts": [{"text": "x"}]}]},
        raw_req_body=b"{}",
        session_id="s",
        subtask_id="t",
        trace_id="tr",
        phase="EXECUTION",
        path="p",
        start=0.0,
        is_fallback=False,
    )
    kw.update(over)

    async def go() -> Any:
        res = await gateway.handle_local_inference(**kw)
        await asyncio.sleep(0)  # let the fire-and-forget audit task run
        return res

    return asyncio.run(go())


def test_local_inference_success_and_fallback_header(pool: FakePool) -> None:
    pool.post_result = FakeResp(json_data=OPENAI_OK)
    res = _local()
    assert res.status_code == 200
    assert res.headers["x-served-by"].endswith("(LOCAL)")
    res = _local(is_fallback=True)
    assert res.headers["x-served-by"].endswith("(FALLBACK)")


@pytest.mark.parametrize(
    "result",
    [
        FakeResp(status_code=500),
        FakeResp(json_data=["not", "dict"]),
        FakeResp(json_data={"choices": []}),
        FakeResp(json_error=json.JSONDecodeError("m", "d", 0)),
        httpx.ConnectError("down"),
        RuntimeError("weird"),
    ],
)
def test_local_inference_failures_return_none(pool: FakePool, result: Any) -> None:
    pool.post_result = result
    assert _local() is None


def test_lifespan_opens_and_closes_resources(
    monkeypatch: pytest.MonkeyPatch, pool: FakePool
) -> None:
    closed: list[bool] = []

    class FakeRedis:
        def __init__(self, **kw: Any) -> None:
            self.kw = kw

        async def aclose(self) -> None:
            closed.append(True)

    monkeypatch.setattr(gateway.aioredis, "Redis", FakeRedis)

    async def run(clear: bool) -> None:
        async with gateway.lifespan(gateway.app):
            assert isinstance(gateway.redis_client, FakeRedis)
            if clear:
                gateway.redis_client = None

    asyncio.run(run(clear=False))
    assert closed == [True] and pool.closed
    asyncio.run(run(clear=True))  # redis already gone → skip aclose
    assert closed == [True]


# ───────────────────────── reverse proxy routes ───────────────────────

GEN_BODY = {"contents": [{"role": "user", "parts": [{"text": "write code"}]}]}


def test_passthrough_non_generation(client: TestClient, pool: FakePool) -> None:
    pool.request_result = FakeResp(status_code=201, content=b"models")
    r = client.get("/v1beta/models?key=abc")
    assert r.status_code == 201 and r.content == b"models"
    method, url, kw = pool.calls[0][1]
    assert url.endswith("/v1beta/models?key=abc") and "host" not in kw["headers"]

    r = client.get("/v1beta/models")  # no query string
    assert pool.calls[1][1][1].endswith("/v1beta/models")
    assert r.status_code == 201


def test_upstream_success_rewrites_model(client: TestClient, pool: FakePool) -> None:
    pool.request_result = FakeResp(
        content=b'{"ok": 1}', headers={"content-encoding": "gzip", "x-up": "1"}
    )
    r = client.post(f"/{GEMINI_PATH}?key=k", json=GEN_BODY, headers={"x-task-phase": "plan"})
    assert r.status_code == 200
    assert r.headers["x-backend-routed"] == "upstream-gemini"
    assert r.headers["x-served-by"] == gateway.MODEL_PLANNING
    assert r.headers["x-up"] == "1"
    url = pool.calls[0][1][1]
    assert f"models/{gateway.MODEL_PLANNING}:generateContent?key=k" in url


def test_upstream_non_dict_body_and_bad_json(client: TestClient, pool: FakePool) -> None:
    assert client.post(f"/{GEMINI_PATH}", content=b"[1, 2]").status_code == 200
    assert client.post(f"/{GEMINI_PATH}", content=b"garbage").status_code == 200


def test_force_local_success_and_fallthrough(client: TestClient, pool: FakePool) -> None:
    pool.post_result = FakeResp(json_data=OPENAI_OK)
    r = client.post(f"/{GEMINI_PATH}", json=GEN_BODY, headers={"x-force-local": "true"})
    assert r.headers["x-backend-routed"] == "local-lora"

    r = client.post(f"/{GEMINI_PATH}", json=GEN_BODY, headers={"x-route-target": "local"})
    assert r.headers["x-served-by"].endswith("(LOCAL)")

    pool.post_result = FakeResp(status_code=500)  # local fails → upstream handles it
    r = client.post(f"/{GEMINI_PATH}", json=GEN_BODY, headers={"x-force-local": "true"})
    assert r.headers["x-backend-routed"] == "upstream-gemini"


@pytest.mark.parametrize(
    "path,query",
    [("v1beta/models/gemini-3.8-flash:streamGenerateContent", ""), (GEMINI_PATH, "?alt=sse")],
)
def test_streaming_relay(client: TestClient, pool: FakePool, path: str, query: str) -> None:
    r = client.post(f"/{path}{query}", json=GEN_BODY)
    assert r.content == b"ab"
    assert r.headers["x-served-by"] == gateway.MODEL_EXECUTION
    assert pool.stream_result.closed
    assert "host" not in pool.calls[0][1]["headers"]


@pytest.mark.parametrize("code", [429, 503])
def test_circuit_breaker_local_fallback(client: TestClient, pool: FakePool, code: int) -> None:
    pool.request_result = FakeResp(status_code=code)
    pool.post_result = FakeResp(json_data=OPENAI_OK)
    r = client.post(f"/{GEMINI_PATH}", json=GEN_BODY)
    assert r.headers["x-served-by"].endswith("(FALLBACK)")


def test_circuit_breaker_local_also_fails_returns_upstream(
    client: TestClient, pool: FakePool
) -> None:
    pool.request_result = FakeResp(status_code=502, content=b"bad gateway")
    pool.post_result = FakeResp(status_code=500)
    r = client.post(f"/{GEMINI_PATH}", json=GEN_BODY)
    assert r.status_code == 502 and r.content == b"bad gateway"


@pytest.mark.parametrize("err", [httpx.ConnectTimeout("t"), httpx.ReadTimeout("t")])
def test_network_error_falls_back_or_503(client: TestClient, pool: FakePool, err: Exception) -> None:
    pool.request_result = err
    pool.post_result = FakeResp(json_data=OPENAI_OK)
    r = client.post(f"/{GEMINI_PATH}", json=GEN_BODY)
    assert r.headers["x-backend-routed"] == "local-lora"

    pool.post_result = httpx.ConnectError("local down")
    r = client.post(f"/{GEMINI_PATH}", json=GEN_BODY)
    assert r.status_code == 503
    assert b"fallback failed" in r.content


# ───────────────────────────── __main__ ──────────────────────────────


def test_main_guard_launches_uvicorn(monkeypatch: pytest.MonkeyPatch) -> None:
    import uvicorn

    seen: dict[str, Any] = {}
    monkeypatch.setattr(uvicorn, "run", lambda app, host, port: seen.update(host=host, port=port))
    monkeypatch.setenv("GATEWAY_HOST", "127.0.0.9")
    monkeypatch.setenv("GATEWAY_PORT", "9999")
    runpy.run_path(str(Path(gateway.__file__)), run_name="__main__")
    assert seen == {"host": "127.0.0.9", "port": 9999}
