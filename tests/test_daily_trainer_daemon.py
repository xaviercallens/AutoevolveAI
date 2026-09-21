"""
Unit and Integration Tests for Autonomous 24-Hour LoRA Trainer & Hot-Reload Daemon.
Verifies watermark filtering, delta extraction, vLLM runtime adapter hot-swapping,
and atomic Redis state progression.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import httpx

from daily_trainer_daemon import run_cycle
from harvest_delta import extract_delta_dataset, parse_trace
from vllm_reloader import (
    hot_reload_vllm_adapter,
    load_vllm_adapter,
    unload_vllm_adapter,
)


def _build_test_gemini_payloads() -> tuple[dict[str, Any], dict[str, Any]]:
    """Generates valid mock Gemini request and response dictionaries."""
    req = {
        "system_instruction": {"parts": [{"text": "You are a specialized code model."}]},
        "contents": [{"role": "user", "parts": [{"text": "Implement binary search."}]}],
    }
    resp = {
        "candidates": [
            {"content": {"parts": [{"text": "def binary_search(arr, x):\n    return 0"}]}}
        ]
    }
    return req, resp


def test_parse_trace_valid_and_invalid() -> None:
    """Validate parse_trace with valid Gemini payloads and corrupt inputs."""
    req, resp = _build_test_gemini_payloads()
    messages, comp = parse_trace(json.dumps(req), json.dumps(resp))
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "binary_search" in comp

    # Corrupt payloads return empty
    empty_msgs, empty_comp = parse_trace("invalid_json", "{}")
    assert empty_msgs == []
    assert empty_comp == ""


def test_extract_delta_dataset_skips_insufficient_samples() -> None:
    """Validate delta extraction skips cycle when verified samples < min_samples."""
    mock_redis = MagicMock()
    mock_redis.get.return_value = b"100.0"  # last watermark
    mock_redis.keys.return_value = []

    success, file_path, ts = extract_delta_dataset(
        min_samples=5,
        redis_client=mock_redis,
    )
    assert success is False
    assert file_path is None
    assert ts > 100.0


def test_extract_delta_dataset_harvests_valid_samples(tmp_path: Path) -> None:
    """Validate delta extraction writes JSONL when sample threshold is met."""
    mock_redis = MagicMock()
    mock_redis.get.side_effect = [
        b"50.0",  # watermark_ts
        json.dumps(
            {
                "timestamp": 120.0,
                "request_json": _build_test_gemini_payloads()[0],
                "response_json": _build_test_gemini_payloads()[1],
            }
        ).encode("utf-8"),
    ]
    mock_redis.keys.return_value = [b"antigravity:subtask:SUB-01:traces"]
    mock_redis.lrange.return_value = [b"trace_pass_1"]
    mock_redis.hgetall.return_value = {b"verdict": b"PASSED"}

    success, file_path, ts = extract_delta_dataset(
        min_samples=1,
        redis_client=mock_redis,
        output_dir=tmp_path,
    )
    assert success is True
    assert file_path is not None
    assert file_path.exists()

    content = file_path.read_text(encoding="utf-8")
    assert "binary_search" in content
    assert ts >= 120.0


def test_vllm_reloader_adapter_swap() -> None:
    """Validate vLLM unload and load endpoints with mock HTTP client."""
    mock_client = MagicMock(spec=httpx.Client)

    # 1. Test unload
    mock_unload_resp = MagicMock(spec=httpx.Response)
    mock_unload_resp.status_code = 200
    mock_client.post.return_value = mock_unload_resp
    assert unload_vllm_adapter(mock_client, "antigravity-local") is True

    # 2. Test load
    mock_load_resp = MagicMock(spec=httpx.Response)
    mock_load_resp.status_code = 200
    mock_client.post.return_value = mock_load_resp
    assert (
        load_vllm_adapter(mock_client, "antigravity-local", Path(tempfile.gettempdir()) / "adapter")
        is True
    )

    # 3. Test hot reload combined
    success = hot_reload_vllm_adapter(
        adapter_name="antigravity-local",
        adapter_path=Path(tempfile.gettempdir()) / "adapter",
        client=mock_client,
    )
    assert success is True


def test_vllm_reloader_handles_load_error() -> None:
    """Validate error handling when vLLM load endpoint fails."""
    mock_client = MagicMock(spec=httpx.Client)
    mock_unload_resp = MagicMock(spec=httpx.Response)
    mock_unload_resp.status_code = 200

    mock_load_resp = MagicMock(spec=httpx.Response)
    mock_load_resp.status_code = 500
    mock_load_resp.text = "GPU OOM while allocating LoRA memory"

    mock_client.post.side_effect = [mock_unload_resp, mock_load_resp]

    success = hot_reload_vllm_adapter(
        adapter_name="antigravity-local",
        adapter_path=Path(tempfile.gettempdir()) / "adapter",
        client=mock_client,
    )
    assert success is False


def test_daily_trainer_daemon_successful_cycle(tmp_path: Path) -> None:
    """Validate full autonomous cycle execution with watermark advancement."""
    mock_redis = MagicMock()
    mock_pipe = MagicMock()
    mock_redis.pipeline.return_value = mock_pipe

    req, resp = _build_test_gemini_payloads()
    mock_redis.get.side_effect = [
        b"10.0",  # watermark_ts
        json.dumps({"timestamp": 50.0, "request_json": req, "response_json": resp}).encode("utf-8"),
    ]
    mock_redis.keys.return_value = [b"antigravity:subtask:SUB-01:traces"]
    mock_redis.lrange.return_value = [b"tr_001"]
    mock_redis.hgetall.return_value = {b"verdict": b"PASSED"}

    mock_client = MagicMock(spec=httpx.Client)
    mock_ok_resp = MagicMock(spec=httpx.Response)
    mock_ok_resp.status_code = 200
    mock_client.post.return_value = mock_ok_resp

    success = run_cycle(
        redis_client=mock_redis,
        min_samples=1,
        dry_run=True,
        http_client=mock_client,
    )
    assert success is True

    # Verify atomic watermark and metadata progression in Redis
    assert mock_pipe.set.call_count >= 3
    assert mock_pipe.rpush.call_count == 1
    mock_pipe.execute.assert_called_once()


def test_daily_trainer_daemon_preserves_watermark_on_skip() -> None:
    """Validate watermark is NOT modified when a cycle has insufficient samples."""
    mock_redis = MagicMock()
    mock_redis.get.return_value = b"100.0"
    mock_redis.keys.return_value = []

    success = run_cycle(
        redis_client=mock_redis,
        min_samples=10,
        dry_run=True,
    )
    assert success is False
    # Pipeline set should never be called
    mock_redis.pipeline().execute.assert_not_called()
