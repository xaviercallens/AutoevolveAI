"""
End-to-End Architecture Integration Test for SuperGravity:
Verifies Antigravity Agent -> Intercept Gateway -> Mock Upstream Gemini API ->
Persistent Redis Streams -> Dataset Exporter (SFT / DPO JSONL).
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import fakeredis.aioredis
import httpx
import pytest

import gateway
from export_training_data import parse_gemini_interaction


@pytest.fixture
def fake_redis_instance() -> Any:
    """Provides an in-memory Redis instance supporting Streams and Pipelines."""
    return fakeredis.aioredis.FakeRedis(decode_responses=False)


@pytest.fixture
def mock_gemini_transport() -> httpx.MockTransport:
    """
    Mock upstream HTTP transport simulating Google Gemini API:
    Handles unary generateContent and streaming streamGenerateContent (SSE).
    """

    def handler(request: httpx.Request) -> httpx.Response:
        url_str = str(request.url)

        # 1. Server-Sent Events (SSE) Streaming Endpoint
        if "streamGenerateContent" in url_str:
            chunk1 = {
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": "First streaming chunk from Gemini 3.8 Flash. "}]
                        }
                    }
                ]
            }
            chunk2 = {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "functionCall": {
                                        "name": "search_codebase",
                                        "args": {"query": "hypervisor"},
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
            sse_body = (f"data: {json.dumps(chunk1)}\n\ndata: {json.dumps(chunk2)}\n\n").encode()
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                content=sse_body,
            )

        # 2. Standard Unary Endpoint
        unary_resp = {
            "candidates": [
                {"content": {"parts": [{"text": "Refactored implementation by Gemini 3.1 Pro."}]}}
            ]
        }
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            content=json.dumps(unary_resp).encode("utf-8"),
        )

    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_end_to_end_unary_flow(
    fake_redis_instance: Any,
    mock_gemini_transport: httpx.MockTransport,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Test Step 1: Unary Interaction Flow
    Agent -> Gateway -> Upstream -> Redis -> Dataset Exporter
    """
    monkeypatch.setattr(gateway, "redis_client", fake_redis_instance)
    mock_client = httpx.AsyncClient(transport=mock_gemini_transport)
    monkeypatch.setattr(gateway, "client_pool", mock_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=gateway.app), base_url="http://testgateway"
    ) as agent_client:
        req_payload = {
            "system_instruction": {"parts": [{"text": "You are a SuperGravity code agent."}]},
            "contents": [{"role": "user", "parts": [{"text": "Fix the hypervisor loop."}]}],
        }
        headers = {"X-Antigravity-Session-ID": "session_test_unary"}

        # Agent initiates request to Gateway
        response = await agent_client.post(
            "/v1beta/models/gemini-3.1-pro:generateContent",
            json=req_payload,
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "candidates" in data
        assert (
            "Refactored implementation by Gemini 3.1 Pro."
            in data["candidates"][0]["content"]["parts"][0]["text"]
        )

    # Give background async Redis logging task a moment to complete
    await asyncio.sleep(0.05)

    # Verify audit event written to Redis stream
    stream_events = await fake_redis_instance.xrange("antigravity:stream:audit", min="-", max="+")
    assert len(stream_events) >= 1

    last_event = stream_events[-1][1]
    assert last_event[b"session_id"] == b"session_test_unary"
    assert b"Fix the hypervisor loop." in last_event[b"request_json"]
    assert b"Refactored implementation by Gemini 3.1 Pro." in last_event[b"response_json"]

    # Verify session set contains the event ID
    session_traces = await fake_redis_instance.lrange(
        "antigravity:session:session_test_unary:traces", 0, -1
    )
    assert len(session_traces) == 1
    assert session_traces[0] == last_event[b"event_id"]


@pytest.mark.asyncio
async def test_end_to_end_streaming_sse_flow(
    fake_redis_instance: Any,
    mock_gemini_transport: httpx.MockTransport,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Test Step 2: SSE Streaming Flow with Tool Call Reassembly
    Agent -> Gateway -> Stream Relay -> Reassembly -> Redis
    """
    monkeypatch.setattr(gateway, "redis_client", fake_redis_instance)
    mock_client = httpx.AsyncClient(transport=mock_gemini_transport)
    monkeypatch.setattr(gateway, "client_pool", mock_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=gateway.app), base_url="http://testgateway"
    ) as agent_client:
        req_payload = {
            "system_instruction": {"parts": [{"text": "You are a streaming code agent."}]},
            "contents": [{"role": "user", "parts": [{"text": "Analyze the codebase."}]}],
        }
        headers = {"X-Antigravity-Session-ID": "session_test_streaming"}

        # Agent initiates SSE Streaming request
        response = await agent_client.post(
            "/v1beta/models/gemini-3.8-flash:streamGenerateContent?alt=sse",
            json=req_payload,
            headers=headers,
        )

        assert response.status_code == 200
        sse_text = response.text
        assert "data:" in sse_text
        assert "First streaming chunk from Gemini 3.8 Flash." in sse_text
        assert "search_codebase" in sse_text

    # Allow async background task to reassemble full stream and write to Redis
    await asyncio.sleep(0.05)

    stream_events = await fake_redis_instance.xrange("antigravity:stream:audit", min="-", max="+")
    assert len(stream_events) >= 1

    last_event = stream_events[-1][1]
    assert last_event[b"session_id"] == b"session_test_streaming"
    assert b"Analyze the codebase." in last_event[b"request_json"]
    assert b"First streaming chunk from Gemini 3.8 Flash." in last_event[b"response_json"]
    assert b"search_codebase" in last_event[b"response_json"]


def _verify_sft_messages(messages: list[dict[str, str]]) -> None:
    assert len(messages) == 3
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are an autonomous code agent."
    assert messages[1]["role"] == "user"
    assert "run_benchmark" in messages[1]["content"]
    assert messages[2]["role"] == "assistant"
    assert "Benchmark completed with 0 errors." in messages[2]["content"]


def _verify_dataset_file(out_file: Path) -> None:
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8").strip()
    loaded = json.loads(content)
    assert loaded["metadata"]["session_id"] == "session_e2e_verified"
    assert len(loaded["messages"]) == 3


def test_end_to_end_dataset_extraction(tmp_path: Path) -> None:
    """
    Test Step 3: Dataset Exporter processing Redis Stream events into SFT JSONL
    """
    req = {
        "system_instruction": {"parts": [{"text": "You are an autonomous code agent."}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": "Execute tool to inspect performance."},
                    {"functionCall": {"name": "run_benchmark", "args": {"iterations": 50}}},
                ],
            }
        ],
    }
    resp = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "Benchmark completed with 0 errors."},
                        {"functionCall": {"name": "report_energy", "args": {"energy": 42}}},
                    ]
                }
            }
        ]
    }

    parsed = parse_gemini_interaction(req, resp)
    assert parsed is not None
    _verify_sft_messages(parsed["messages"])

    out_file = tmp_path / "sft_dataset.jsonl"
    parsed["metadata"] = {"session_id": "session_e2e_verified", "latency_ms": 15.2}
    out_file.write_text(json.dumps(parsed) + "\n", encoding="utf-8")
    _verify_dataset_file(out_file)
