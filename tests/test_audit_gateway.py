"""
Tests for Antigravity LLM Audit Gateway and Dataset Exporter.
Verifies payload decoding, conversation extraction, tool call preservation, and dataset output.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

from export_training_data import (
    _extract_conversation_turns,
    _extract_model_completion,
    _extract_system_instruction,
    export_traces,
    parse_gemini_interaction,
)
from gateway import _safe_decode_payload


def test_safe_decode_payload():
    # Valid JSON
    data = {"model": "gemini-3.8-flash", "temperature": 0.2}
    raw = json.dumps(data).encode("utf-8")
    assert _safe_decode_payload(raw) == data

    # Non-JSON string
    raw_str = b"raw string payload"
    assert _safe_decode_payload(raw_str) == "raw string payload"


def test_parse_gemini_interaction_with_tools():
    req = {
        "system_instruction": {"parts": [{"text": "You are a code agent."}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": "Refactor the solver"},
                    {"functionCall": {"name": "read_file", "args": {"path": "solver.py"}}},
                ],
            }
        ],
    }
    resp = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "I will execute the tool."},
                        {"functionCall": {"name": "execute_tool", "args": {"cmd": "pytest"}}},
                    ]
                }
            }
        ]
    }

    parsed = parse_gemini_interaction(req, resp)
    assert parsed is not None
    messages = parsed["messages"]

    assert len(messages) == 3

    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are a code agent."

    assert messages[1]["role"] == "user"
    assert "Refactor the solver" in messages[1]["content"]
    assert "<tool_call>" in messages[1]["content"]


def test_extract_helpers_individually():
    req = {
        "system_instruction": {"parts": [{"text": "System prompt text"}]},
        "contents": [
            {"role": "user", "parts": [{"text": "Hello world"}]},
            {"role": "model", "parts": [{"text": "Hello back"}]},
        ],
    }
    resp = {"candidates": [{"content": {"parts": [{"text": "Final response"}]}}]}

    sys_text = _extract_system_instruction(req)
    assert sys_text == "System prompt text"

    turns = _extract_conversation_turns(req)
    assert len(turns) == 2
    assert turns[0]["role"] == "user"
    assert turns[0]["content"] == "Hello world"
    assert turns[1]["role"] == "assistant"
    assert turns[1]["content"] == "Hello back"

    completion = _extract_model_completion(resp)
    assert completion == "Final response"


def test_export_traces_mock_redis(tmp_path: Path, monkeypatch):
    mock_redis = MagicMock()
    mock_event = (
        "1710000000-0",
        {
            "endpoint": "v1beta/models/gemini-3.8-flash:generateContent",
            "session_id": "session_test_123",
            "latency_ms": "120.5",
            "timestamp": "1710000000.0",
            "request_json": json.dumps(
                {
                    "system_instruction": {"parts": [{"text": "System prompt"}]},
                    "contents": [{"role": "user", "parts": [{"text": "Perform action"}]}],
                }
            ),
            "response_json": json.dumps(
                {"candidates": [{"content": {"parts": [{"text": "Action performed."}]}}]}
            ),
        },
    )
    mock_redis.return_value.xrange.return_value = [mock_event]
    monkeypatch.setattr("redis.Redis", mock_redis)

    out_file = tmp_path / "dataset.jsonl"
    count = export_traces(str(out_file))

    assert count == 1
    assert out_file.exists()
    lines = out_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert len(row["messages"]) == 3

    assert row["metadata"]["session_id"] == "session_test_123"
    assert row["metadata"]["latency_ms"] == 120.5
