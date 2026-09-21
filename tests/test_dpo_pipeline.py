"""
Integration tests for the Antigravity DPO Pair Generation Pipeline:
Verifies attestation recording, trace correlation, and (prompt, chosen, rejected) triplet extraction.  # noqa: E501
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import fakeredis
import fakeredis.aioredis
import httpx
import pytest

import gateway
from attestation_reporter import record_attestation_verdict
from extract_dpo_pairs import extract_dpo_pairs


@pytest.fixture
def fake_sync_redis() -> Any:
    """Synchronous in-memory Redis for attestation reporter and DPO extraction."""
    return fakeredis.FakeRedis(decode_responses=False)


def test_record_attestation_verdict(fake_sync_redis: Any) -> None:
    """Test recording FAILED and PASSED verification verdicts into Redis."""
    # 1. Record a failed attestation
    record_attestation_verdict(
        trace_id="trace_fail_1",
        subtask_id="subtask_energy_calc",
        passed=False,
        reasons=["Hollow stub detected: pass statement", "Production trace missing"],
        test_stdout="AssertionError: Expected 42, got None",
        redis_client=fake_sync_redis,
    )

    att_fail = fake_sync_redis.hgetall("antigravity:attestation:trace_fail_1")
    assert att_fail[b"verdict"] == b"FAILED"
    assert att_fail[b"subtask_id"] == b"subtask_energy_calc"
    reasons = json.loads(att_fail[b"reasons"].decode("utf-8"))
    assert len(reasons) == 2
    assert "Hollow stub detected: pass statement" in reasons

    in_progress = fake_sync_redis.smembers("antigravity:subtasks:in_progress")
    assert b"subtask_energy_calc" in in_progress

    # 2. Record a passing attestation
    record_attestation_verdict(
        trace_id="trace_pass_1",
        subtask_id="subtask_energy_calc",
        passed=True,
        reasons=[],
        test_stdout="1 passed in 0.02s",
        redis_client=fake_sync_redis,
    )

    att_pass = fake_sync_redis.hgetall("antigravity:attestation:trace_pass_1")
    assert att_pass[b"verdict"] == b"PASSED"
    completed = fake_sync_redis.smembers("antigravity:subtasks:completed")
    assert b"subtask_energy_calc" in completed


def test_compute_edit_distance_and_trajectory_reward() -> None:
    """Test normalized Levenshtein ratio and physical Mini-RL scalar reward."""
    from extract_dpo_pairs import compute_edit_distance_ratio, compute_trajectory_reward

    # Identical strings -> distance 0.0
    assert compute_edit_distance_ratio("abc", "abc") == 0.0
    # Completely different strings
    assert compute_edit_distance_ratio("", "abc") == 1.0
    # Partial change
    ratio = compute_edit_distance_ratio("def foo(): return 1", "def foo(): return 2")
    assert 0.0 < ratio < 0.2

    # Reward: Perfect passing Lean & tests, 0 distance -> high positive
    r_win = compute_trajectory_reward(
        lean_valid=True,
        tests_pass=True,
        anti_stub_failed=False,
        edit_distance_human=0.0,
    )
    assert r_win == 3.0  # W1(2.0) + W2(1.0)

    # Reward: Stub failed, wrong tests, high human edit distance -> negative
    r_lose = compute_trajectory_reward(
        lean_valid=False,
        tests_pass=False,
        anti_stub_failed=True,
        edit_distance_human=0.8,
    )
    assert r_lose == -2.3  # -W3(1.5) - W4(1.0 * 0.8)
    assert r_win > r_lose


def _setup_failed_trace(r: Any, subtask_id: str, req_payload: dict[str, Any]) -> str:
    trace_rej_id = "trace_rej_101"
    resp_rejected = {
        "candidates": [
            {"content": {"parts": [{"text": "def matmul(a, b):\n    pass  # TODO: implement"}]}}
        ]
    }
    r.set(
        f"antigravity:trace:{trace_rej_id}",
        json.dumps(
            {
                "event_id": trace_rej_id,
                "session_id": "session_alpha",
                "subtask_id": subtask_id,
                "request_json": json.dumps(req_payload),
                "response_json": json.dumps(resp_rejected),
            }
        ),
    )
    record_attestation_verdict(
        trace_id=trace_rej_id,
        subtask_id=subtask_id,
        passed=False,
        reasons=["Anti-stub violation: pass in matmul"],
        test_stdout="FAILED tests/test_matmul.py - StubError",
        redis_client=r,
    )
    return trace_rej_id


def _setup_passing_trace(r: Any, subtask_id: str, req_payload: dict[str, Any]) -> str:
    trace_cho_id = "trace_cho_202"
    resp_chosen = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": (
                                "import torch\n\n"
                                "def matmul(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:\n"
                                "    return torch.matmul(a, b)\n"
                            )
                        }
                    ]
                }
            }
        ]
    }
    r.set(
        f"antigravity:trace:{trace_cho_id}",
        json.dumps(
            {
                "event_id": trace_cho_id,
                "session_id": "session_alpha",
                "subtask_id": subtask_id,
                "request_json": json.dumps(req_payload),
                "response_json": json.dumps(resp_chosen),
            }
        ),
    )
    record_attestation_verdict(
        trace_id=trace_cho_id,
        subtask_id=subtask_id,
        passed=True,
        reasons=[],
        test_stdout="1 passed, 0 failed in 0.05s",
        redis_client=r,
    )
    return trace_cho_id


def _verify_pair_structure(pair: dict[str, Any], subtask_id: str, cho_id: str, rej_id: str) -> None:
    assert len(pair["prompt"]) == 2
    assert pair["prompt"][0]["role"] == "system"
    assert "Micro-ML Architect" in pair["prompt"][0]["content"]
    assert "torch.matmul" in pair["chosen"]
    assert "pass  # TODO: implement" in pair["rejected"]
    assert pair["metadata"]["subtask_id"] == subtask_id
    assert pair["metadata"]["chosen_trace_id"] == cho_id
    assert pair["metadata"]["rejected_trace_id"] == rej_id


def test_extract_dpo_pairs(fake_sync_redis: Any, tmp_path: Path) -> None:
    """Test full DPO pair extraction from correlated failed and passing traces."""
    subtask_id = "subtask_matrix_mult"
    req_payload = {
        "system_instruction": {"parts": [{"text": "You are a Micro-ML Architect."}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": "Implement deterministic matrix multiplication under 50k params."}
                ],  # noqa: E501
            }
        ],
    }

    rej_id = _setup_failed_trace(fake_sync_redis, subtask_id, req_payload)
    cho_id = _setup_passing_trace(fake_sync_redis, subtask_id, req_payload)

    out_file = tmp_path / "dpo_dataset.jsonl"
    pairs = extract_dpo_pairs(output_file=str(out_file), redis_client=fake_sync_redis)

    assert len(pairs) == 1
    _verify_pair_structure(pairs[0], subtask_id, cho_id, rej_id)
    assert out_file.exists()


def _decode_redis_val(val: Any) -> str:
    return val.decode("utf-8") if isinstance(val, bytes) else str(val)


@pytest.mark.asyncio
async def test_gateway_subtask_header_and_trace_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test Gateway captures X-Subtask-ID and returns X-Trace-ID header."""
    fake_aioredis = fakeredis.aioredis.FakeRedis(decode_responses=False)
    monkeypatch.setattr(gateway, "redis_client", fake_aioredis)

    def mock_handler(_: httpx.Request) -> httpx.Response:
        resp = {"candidates": [{"content": {"parts": [{"text": "Verified gate code."}]}}]}
        return httpx.Response(200, json=resp)

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))
    monkeypatch.setattr(gateway, "client_pool", mock_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=gateway.app), base_url="http://testgateway"
    ) as client:
        req_payload = {
            "contents": [{"role": "user", "parts": [{"text": "Generate verified module."}]}]
        }
        headers = {
            "X-Antigravity-Session-ID": "session_gate_test",
            "X-Subtask-ID": "subtask_gateway_1",
        }

        resp = await client.post(
            "/v1beta/models/gemini-3.1-pro:generateContent",
            json=req_payload,
            headers=headers,
        )

        assert resp.status_code == 200
        assert "x-trace-id" in resp.headers
        trace_id = resp.headers["x-trace-id"]

    await asyncio.sleep(0.05)
    subtask_traces = await fake_aioredis.lrange(
        "antigravity:subtask:subtask_gateway_1:traces", 0, -1
    )  # noqa: E501
    assert len(subtask_traces) == 1
    assert _decode_redis_val(subtask_traces[0]) == trace_id

    trace_raw = await fake_aioredis.get(f"antigravity:trace:{trace_id}")
    assert trace_raw is not None
    record = json.loads(_decode_redis_val(trace_raw))
    assert record["subtask_id"] == "subtask_gateway_1"
    assert record["session_id"] == "session_gate_test"
