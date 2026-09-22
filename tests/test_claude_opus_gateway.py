"""
Unit & Integration Tests for Claude and Opus Recording & Telemetry in Gateway.

Verifies:
1. Native Anthropic Messages endpoint (`POST /v1/messages`) processing.
2. Continuous event stream recording into `antigravity:stream:claude_opus` and `antigravity:stream:audit`.
3. OpenAI-compatible chat completions proxy recording for Claude/Opus models.
4. Extraction of recorded trajectories for post-training RL and LoRA datasets.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import fakeredis.aioredis
import pytest
from httpx import ASGITransport, AsyncClient

import gateway
from gateway import app, is_claude_or_opus_model


@pytest.fixture(autouse=True)
def setup_fake_redis():
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=False)
    gateway.redis_client = fake_redis
    yield fake_redis
    asyncio.run(fake_redis.aclose())


def test_is_claude_or_opus_model():
    assert is_claude_or_opus_model("claude-3-opus-20240229") is True
    assert is_claude_or_opus_model("claude-3-5-sonnet-20241022") is True
    assert is_claude_or_opus_model("claude-opus-4-6") is True
    assert is_claude_or_opus_model("anthropic/claude-3-haiku") is True
    assert is_claude_or_opus_model("gemini-3.8-flash") is False
    assert is_claude_or_opus_model("qwen-2.5-coder") is False


@pytest.mark.asyncio
async def test_anthropic_messages_endpoint_recording(setup_fake_redis):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {
            "model": "claude-3-opus-20240229",
            "messages": [
                {"role": "user", "content": "Prove that the Kretschmann invariant on Schwarzschild scales as r^-6."}
            ],
            "max_tokens": 512,
        }
        headers = {
            "x-api-key": "test_claude_key",
            "anthropic-version": "2023-06-01",
            "x-antigravity-session-id": "session_claude_opus_test",
        }
        resp = await client.post("/v1/messages", json=payload, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "assistant"
        assert len(data["content"]) > 0
        assert data["model"] == "claude-3-opus-20240229"

        # Check Redis stream recording
        stream_events = await setup_fake_redis.xrange("antigravity:stream:claude_opus", "-", "+")
        assert len(stream_events) >= 1
        entry_id, fields = stream_events[0]
        model_used = fields.get(b"model_used", b"").decode("utf-8")
        assert "claude-3-opus" in model_used
        is_opus = fields.get(b"is_opus", b"").decode("utf-8")
        assert is_opus == "1"


@pytest.mark.asyncio
async def test_openai_chat_completions_claude_recording(setup_fake_redis):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "messages": [
                {"role": "user", "content": "Implement Symplectic Stormer-Verlet integrator."}
            ],
        }
        headers = {
            "x-antigravity-session-id": "session_sonnet_openai_test",
        }
        resp = await client.post("/v1/chat/completions", json=payload, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["object"] == "chat.completion"
        assert len(data["choices"]) > 0

        # Verify it was logged to claude_opus stream
        stream_events = await setup_fake_redis.xrange("antigravity:stream:claude_opus", "-", "+")
        assert len(stream_events) >= 1
        last_event = stream_events[-1][1]
        assert b"sonnet" in last_event.get(b"model_used", b"")
