#!/usr/bin/env python3
"""
Incremental Data Harvester:
Queries Redis for verified traces recorded since the last training watermark.
Emits delta datasets for SFT / DPO incremental training.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))


def _extract_system_turn(req: dict[str, Any]) -> dict[str, str] | None:
    """Extracts system instruction message from Gemini request payload."""
    sys_parts = req.get("system_instruction", {}).get("parts", [])
    if not sys_parts:
        return None
    sys_text = "\n".join(p.get("text", "") for p in sys_parts if "text" in p).strip()
    return {"role": "system", "content": sys_text} if sys_text else None


def _extract_conversation_turns(req: dict[str, Any]) -> list[dict[str, str]]:
    """Extracts user and assistant conversational turns from Gemini request payload."""
    messages: list[dict[str, str]] = []
    for turn in req.get("contents", []):
        role = "user" if turn.get("role") == "user" else "assistant"
        parts: list[str] = []
        for p in turn.get("parts", []):
            if "text" in p:
                parts.append(p["text"])
            elif "functionCall" in p:
                parts.append(f"<tool_call>{json.dumps(p['functionCall'])}</tool_call>")
        if parts:
            messages.append({"role": role, "content": "\n".join(parts)})
    return messages


def _extract_candidate_completion(resp: dict[str, Any]) -> str | None:
    """Extracts model completion or tool calls from candidate responses."""
    candidates = resp.get("candidates", [])
    if not candidates:
        return None

    parts: list[str] = []
    for p in candidates[0].get("content", {}).get("parts", []):
        if "text" in p:
            parts.append(p["text"])
        elif "functionCall" in p:
            parts.append(f"<tool_call>{json.dumps(p['functionCall'])}</tool_call>")

    return "\n".join(parts).strip() if parts else None


def parse_trace(req_json: Any, resp_json: Any) -> tuple[list[dict[str, str]], str]:
    """Parses raw request and response JSON payloads into message turns and completion."""
    try:
        req = json.loads(req_json) if isinstance(req_json, (str, bytes)) else req_json
        resp = json.loads(resp_json) if isinstance(resp_json, (str, bytes)) else resp_json
    except (json.JSONDecodeError, KeyError):
        return [], ""

    if not isinstance(req, dict) or not isinstance(resp, dict):
        return [], ""

    messages: list[dict[str, str]] = []
    sys_turn = _extract_system_turn(req)
    if sys_turn:
        messages.append(sys_turn)
    messages.extend(_extract_conversation_turns(req))

    completion = _extract_candidate_completion(resp) or ""
    return messages, completion


def _is_attestation_passed(r: Any, tid_str: str) -> bool:
    """Verifies that the attestation gate for a given trace ID is PASSED."""
    raw_att = r.hgetall(f"antigravity:attestation:{tid_str}") or {}
    for k, v in raw_att.items():
        k_str = k.decode("utf-8") if isinstance(k, bytes) else str(k)
        v_str = v.decode("utf-8") if isinstance(v, bytes) else str(v)
        if k_str == "verdict":
            return v_str == "PASSED"
    return False


def _process_single_trace_delta(
    r: Any,
    tid_str: str,
    last_watermark: float,
) -> dict[str, Any] | None:
    """Inspects a single trace ID against watermark and attestation gate."""
    trace_raw = r.get(f"antigravity:trace:{tid_str}")
    if not trace_raw:
        return None

    raw_str = trace_raw.decode("utf-8") if isinstance(trace_raw, bytes) else str(trace_raw)
    try:
        record = json.loads(raw_str)
    except json.JSONDecodeError:
        return None

    trace_ts = float(record.get("timestamp", 0.0))
    if trace_ts <= last_watermark or not _is_attestation_passed(r, tid_str):
        return None

    msgs, comp = parse_trace(record.get("request_json"), record.get("response_json"))
    if not msgs or not comp:
        return None

    return {
        "messages": msgs + [{"role": "assistant", "content": comp}],
        "trace_id": tid_str,
        "timestamp": trace_ts,
    }


def _harvest_subtask_traces(
    r: Any,
    subtask_keys: list[Any],
    last_watermark: float,
) -> list[dict[str, Any]]:
    """Iterates subtask trace lists to harvest all verified new samples."""
    sft_records: list[dict[str, Any]] = []
    for key in subtask_keys:
        raw_ids = r.lrange(key, 0, -1) or []
        unique_tids = list(dict.fromkeys(raw_ids))
        for tid in unique_tids:
            tid_str = tid.decode("utf-8") if isinstance(tid, bytes) else str(tid)
            sample = _process_single_trace_delta(r, tid_str, last_watermark)
            if sample:
                sft_records.append(sample)
    return sft_records


def _write_delta_file(
    records: list[dict[str, Any]],
    cycle_ts: float,
    output_dir: Path,
) -> Path:
    """Writes delta dataset records to a timestamped JSONL file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"delta_{int(cycle_ts)}.jsonl"
    with open(out_file, "w", encoding="utf-8") as f:
        for item in records:
            f.write(json.dumps(item) + "\n")
    return out_file


def extract_delta_dataset(
    min_samples: int = 50,
    redis_client: Any = None,
    redis_host: str = REDIS_HOST,
    redis_port: int = REDIS_PORT,
    output_dir: Path = Path("./training_runs/datasets"),
) -> tuple[bool, Path | None, float]:
    """Queries Redis for verified traces recorded since the last training watermark."""
    r = redis_client or redis.Redis(host=redis_host, port=redis_port, decode_responses=False)
    raw_wm = r.get("antigravity:training:watermark_ts")
    last_watermark = float(raw_wm.decode("utf-8") if isinstance(raw_wm, bytes) else (raw_wm or 0.0))
    current_cycle_ts = time.time()

    subtask_keys = r.keys("antigravity:subtask:*:traces") or []
    sft_records = _harvest_subtask_traces(r, subtask_keys, last_watermark)

    print(
        f"📦 Harvester: Found {len(sft_records)} verified samples "
        f"since watermark ({last_watermark})."
    )

    if len(sft_records) < min_samples:
        print(f"ℹ️ Insufficient new samples ({len(sft_records)} < {min_samples}). Skipping cycle.")
        return False, None, current_cycle_ts

    out_file = _write_delta_file(sft_records, current_cycle_ts, output_dir)
    return True, out_file, current_cycle_ts


def main() -> None:
    """CLI Entrypoint for the delta harvester."""
    parser = argparse.ArgumentParser(description="Extract delta training dataset from Redis traces")
    parser.add_argument("--min-samples", type=int, default=50, help="Minimum sample threshold")
    parser.add_argument("--host", default=REDIS_HOST, help="Redis host")
    parser.add_argument("--port", type=int, default=REDIS_PORT, help="Redis port")
    args = parser.parse_args()

    success, file_path, ts = extract_delta_dataset(
        min_samples=args.min_samples,
        redis_host=args.host,
        redis_port=args.port,
    )
    if success:
        print(f"✅ Delta dataset created at: {file_path} (Watermark: {ts})")
    else:
        print("⚠️ Delta harvest skipped (insufficient samples).")


__all__ = [
    "parse_trace",
    "extract_delta_dataset",
    "main",
]


if __name__ == "__main__":
    main()
