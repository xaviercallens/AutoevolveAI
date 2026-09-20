"""
Integration and Unit Tests for Local LoRA / vLLM / Ollama Translation Gateway:
Verifies Gemini-to-OpenAI schema translation, local routing, and fallback to upstream Gemini.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import fakeredis.aioredis
import httpx
import pytest

import gateway
from gateway import gemini_to_openai_payload, openai_to_gemini_response


def _verify_openai_payload_metadata(payload: dict[str, Any]) -> None:
    assert payload["model"] == "antigravity-local"
    assert payload["temperature"] == 0.1
    assert payload["top_p"] == 0.9
    assert payload["max_tokens"] == 2048


def _verify_openai_payload_messages(messages: list[dict[str, str]]) -> None:
    assert len(messages) == 3
    assert messages[0]["role"] == "system"
    assert "specialized LoRA" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Implement calculate_risk."
    assert messages[2]["role"] == "assistant"
    assert "read_source" in messages[2]["content"]


def test_gemini_to_openai_payload_translation() -> None:
    """Validate translation of Gemini request payload to OpenAI chat format."""
    gemini_req = {
        "system_instruction": {"parts": [{"text": "You are a specialized LoRA code model."}]},
        "contents": [
            {"role": "user", "parts": [{"text": "Implement calculate_risk."}]},
            {
                "role": "model",
                "parts": [
                    {
                        "functionCall": {
                            "name": "read_source",
                            "args": {"path": "src/risk.py"},
                        }
                    }
                ],
            },
        ],
        "generationConfig": {"temperature": 0.1, "topP": 0.9, "maxOutputTokens": 2048},
    }

    payload = gemini_to_openai_payload(gemini_req, model_name="antigravity-local")
    _verify_openai_payload_metadata(payload)
    _verify_openai_payload_messages(payload["messages"])


def _verify_gemini_candidate_parts(parts: list[dict[str, Any]]) -> None:
    assert len(parts) == 1
    assert "functionCall" in parts[0]
    assert parts[0]["functionCall"]["name"] == "write_file"
    assert parts[0]["functionCall"]["args"]["path"] == "src/risk.py"


def _verify_gemini_usage(usage: dict[str, Any]) -> None:
    assert usage["promptTokenCount"] == 45
    assert usage["candidatesTokenCount"] == 20
    assert usage["totalTokenCount"] == 65


def test_openai_to_gemini_response_with_tool_call() -> None:
    """Validate translation of OpenAI response containing <tool_call> tags into Gemini candidates."""  # noqa: E501
    openai_resp = {
        "id": "chatcmpl-test-123",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": '<tool_call>{"name": "write_file", "args": {"path": "src/risk.py"}}</tool_call>',  # noqa: E501
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 45, "completion_tokens": 20, "total_tokens": 65},
    }

    gemini_resp = openai_to_gemini_response(openai_resp)
    assert "candidates" in gemini_resp
    assert len(gemini_resp["candidates"]) == 1

    candidate = gemini_resp["candidates"][0]
    assert candidate["finishReason"] == "STOP"
    _verify_gemini_candidate_parts(candidate["content"]["parts"])
    _verify_gemini_usage(gemini_resp["usageMetadata"])


@pytest.mark.asyncio
async def test_gateway_routes_to_local_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test gateway routes generation requests to local inference when route target is local."""
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=False)
    monkeypatch.setattr(gateway, "redis_client", fake_redis)
    monkeypatch.setattr(gateway, "ROUTE_TO_LOCAL", True)

    def mock_local_transport(request: httpx.Request) -> httpx.Response:
        assert "v1/chat/completions" in str(request.url)
        body = json.loads(request.content.decode("utf-8"))
        assert body["model"] == "antigravity-local"
        openai_res = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "def calculate_risk(portfolio):\n    return sum(portfolio) * 0.05",  # noqa: E501
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 30, "completion_tokens": 15, "total_tokens": 45},
        }
        return httpx.Response(200, json=openai_res)

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_local_transport))
    monkeypatch.setattr(gateway, "client_pool", mock_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=gateway.app), base_url="http://testgateway"
    ) as client:
        req = {"contents": [{"role": "user", "parts": [{"text": "Implement calculate_risk."}]}]}
        headers = {
            "X-Antigravity-Session-ID": "session_lora_test",
            "X-Subtask-ID": "subtask_lora_1",
            "X-Route-Target": "local",
        }

        resp = await client.post(
            "/v1beta/models/gemini-3.1-pro:generateContent",
            json=req,
            headers=headers,
        )

        assert resp.status_code == 200
        assert resp.headers["x-backend-routed"] == "local-lora"
        assert "x-trace-id" in resp.headers

        data = resp.json()
        assert "candidates" in data
        assert "calculate_risk" in data["candidates"][0]["content"]["parts"][0]["text"]

    await asyncio.sleep(0.05)
    traces = await fake_redis.lrange("antigravity:subtask:subtask_lora_1:traces", 0, -1)
    assert len(traces) == 1


@pytest.mark.asyncio
async def test_gateway_fallback_to_upstream_when_local_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test gateway falls back to upstream Gemini if local inference returns an error."""
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=False)
    monkeypatch.setattr(gateway, "redis_client", fake_redis)
    monkeypatch.setattr(gateway, "ROUTE_TO_LOCAL", True)

    def mock_dispatcher(request: httpx.Request) -> httpx.Response:
        # Simulate local vLLM failing with 503 Service Unavailable
        if "chat/completions" in str(request.url):
            return httpx.Response(503, text="Model loading in progress")

        # Upstream Gemini answers as fallback
        gemini_res = {
            "candidates": [
                {
                    "content": {"parts": [{"text": "Upstream Gemini fallback output."}]},
                    "finishReason": "STOP",
                }
            ]
        }
        return httpx.Response(200, json=gemini_res)

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_dispatcher))
    monkeypatch.setattr(gateway, "client_pool", mock_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=gateway.app), base_url="http://testgateway"
    ) as client:
        req = {"contents": [{"role": "user", "parts": [{"text": "Generate test function."}]}]}
        headers = {
            "X-Antigravity-Session-ID": "session_fallback_test",
            "X-Route-Target": "auto",
        }

        resp = await client.post(
            "/v1beta/models/gemini-3.1-pro:generateContent",
            json=req,
            headers=headers,
        )

        assert resp.status_code == 200
        assert resp.headers["x-backend-routed"] == "upstream-gemini"
        data = resp.json()
        assert (
            "Upstream Gemini fallback output."
            in data["candidates"][0]["content"]["parts"][0]["text"]
        )  # noqa: E501
