"""
Integration and Unit Tests for Multi-Tier Routing and Circuit-Breaker Gateway.
Verifies phase resolution (Gemini 3.1 Pro for Planning/Verification, Gemini 3.8 Flash for Execution),  # noqa: E501
circuit breaker automatic failover on 429/500 to local LoRA model, and client workflow phase dispatchers.  # noqa: E501
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import MagicMock

import fakeredis.aioredis
import httpx
import pytest

import gateway
from claude_workflow import (
    Subtask,
    run_execution_phase,
    run_planning_phase,
    run_verification_phase,
)
from gateway import (
    MODEL_EXECUTION,
    MODEL_PLANNING,
    MODEL_VERIFICATION,
    app,
    resolve_target_model,
)


@pytest.fixture(autouse=True)
def setup_fake_redis_and_client():
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=False)
    gateway.redis_client = fake_redis
    yield fake_redis
    asyncio.run(fake_redis.aclose())


def test_resolve_target_model_explicit_phases() -> None:
    """Validate target model resolution based on explicit X-Task-Phase headers."""
    dummy_body: dict[str, Any] = {"contents": []}

    # Planning phase
    model, phase = resolve_target_model("PLANNING", dummy_body)
    assert model == MODEL_PLANNING
    assert phase == "PLANNING"

    # Execution phase
    model, phase = resolve_target_model("EXECUTION", dummy_body)
    assert model == MODEL_EXECUTION
    assert phase == "EXECUTION"

    # Verification phase
    model, phase = resolve_target_model("VERIFICATION", dummy_body)
    assert model == MODEL_VERIFICATION
    assert phase == "VERIFICATION"


def test_resolve_target_model_semantic_fallback() -> None:
    """Validate semantic token inspection when no explicit header is provided."""
    # Planning prompt
    plan_body = {
        "contents": [{"parts": [{"text": "Please decompose this architecture into subtasks."}]}]
    }
    model, phase = resolve_target_model(None, plan_body)
    assert model == MODEL_PLANNING
    assert phase == "PLANNING"

    # Verification prompt
    verify_body = {"contents": [{"parts": [{"text": "Inspect the code and run test assertions."}]}]}
    model, phase = resolve_target_model(None, verify_body)
    assert model == MODEL_VERIFICATION
    assert phase == "VERIFICATION"

    # Execution prompt
    exec_body = {
        "contents": [{"parts": [{"text": "Generate the diff for the calculate_tax function."}]}]
    }
    model, phase = resolve_target_model(None, exec_body)
    assert model == MODEL_EXECUTION
    assert phase == "EXECUTION"


@pytest.mark.asyncio
async def test_circuit_breaker_failover_on_429(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validate circuit-breaker failover to local LoRA model on upstream 429 rate limit."""
    mock_local_response = {
        "id": "chatcmpl-fallback-429",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "def fallback_calc():\n    return 42",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
    }

    async def mock_post(url: str, **kwargs: Any) -> httpx.Response:
        assert "localhost:11434" in url or "v1/chat/completions" in url
        return httpx.Response(200, json=mock_local_response)

    async def mock_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
        # Upstream returns 429 Too Many Requests
        return httpx.Response(429, json={"error": {"code": 429, "message": "Resource exhausted"}})

    monkeypatch.setattr(gateway.client_pool, "post", mock_post)
    monkeypatch.setattr(gateway.client_pool, "request", mock_request)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        payload = {
            "contents": [{"parts": [{"text": "Implement resilient algorithm"}]}],
        }
        headers = {
            "Content-Type": "application/json",
            "X-Task-Phase": "EXECUTION",
            "X-Subtask-ID": "TASK-RATE-LIMIT",
        }
        resp = await client.post(
            "/v1beta/models/gemini-3.8-flash:generateContent?key=TEST_KEY",
            json=payload,
            headers=headers,
        )

        assert resp.status_code == 200
        assert resp.headers["x-backend-routed"] == "local-lora"
        assert "FALLBACK" in resp.headers["x-served-by"]

        data = resp.json()
        assert "candidates" in data
        assert "def fallback_calc" in data["candidates"][0]["content"]["parts"][0]["text"]


def _setup_mock_client():
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Mock phase response"}]}}]
    }
    mock_client.post.return_value = mock_resp
    return mock_client


def test_claude_workflow_planning_phase() -> None:
    mock_client = _setup_mock_client()
    plan_res = run_planning_phase(
        goal="Build Tokenizer",
        client=mock_client,
    )
    assert plan_res["phase"] == "PLANNING"
    assert plan_res["success"] is True

    call_args = mock_client.post.call_args
    assert call_args[1]["headers"]["X-Task-Phase"] == "PLANNING"
    assert "gemini-3.1-pro" in call_args[0][0]


def test_claude_workflow_execution_phase() -> None:
    mock_client = _setup_mock_client()
    exec_res = run_execution_phase(
        subtask_id="SUB-01",
        prompt="Write tokenizer code",
        client=mock_client,
    )
    assert exec_res["phase"] == "EXECUTION"
    call_args = mock_client.post.call_args
    assert call_args[1]["headers"]["X-Task-Phase"] == "EXECUTION"
    assert call_args[1]["headers"]["X-Subtask-ID"] == "SUB-01"
    assert "gemini-3.8-flash" in call_args[0][0]


def test_claude_workflow_verification_phase() -> None:
    mock_client = _setup_mock_client()
    dummy_subtask = Subtask(
        id="SUB-VERIFY",
        title="Verify Tokenizer",
        target_files=[],
        acceptance_command='python -c "import sys; sys.exit(0)"',
    )
    passed, msg = run_verification_phase(
        subtask=dummy_subtask,
        client=mock_client,
    )
    assert passed is True
    assert "All acceptance checks passed cleanly" in msg
    call_args = mock_client.post.call_args
    assert call_args[1]["headers"]["X-Task-Phase"] == "VERIFICATION"
    assert call_args[1]["headers"]["X-Subtask-ID"] == "SUB-VERIFY"
