#!/usr/bin/env python3
"""
Dataset Builder: Parses Antigravity Redis traces into SFT / DPO conversational JSONL.
Formats training data for Unsloth, Axolotl, and LLaMA-Factory.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

import redis


def _extract_system_instruction(req: dict[str, Any]) -> str | None:
    """Extract system instruction text from Gemini request payload."""
    sys_inst = req.get("system_instruction", {}).get("parts", [])
    if not sys_inst:
        return None
    parts = [p.get("text", "") for p in sys_inst if "text" in p]
    text = "\n".join(parts).strip()
    return text if text else None


def _extract_conversation_turns(req: dict[str, Any]) -> list[dict[str, str]]:
    """Extract user and prior assistant turns from Gemini request payload."""
    messages: list[dict[str, str]] = []
    contents = req.get("contents", [])
    for turn in contents:
        role = "user" if turn.get("role") == "user" else "assistant"
        parts = turn.get("parts", [])
        text_content = ""
        for p in parts:
            if "text" in p:
                text_content += p["text"]
            elif "functionCall" in p:
                text_content += f"\n<tool_call>{json.dumps(p['functionCall'])}</tool_call>"
        if text_content.strip():
            messages.append({"role": role, "content": text_content.strip()})
    return messages


def _extract_model_completion(resp: dict[str, Any]) -> str | None:
    """Extract final model completion or tool calls from Gemini response payload."""
    candidates = resp.get("candidates", [])
    if not candidates:
        return None

    model_parts = candidates[0].get("content", {}).get("parts", [])
    completion = ""
    for p in model_parts:
        if "text" in p:
            completion += p["text"]
        elif "functionCall" in p:
            completion += f"\n<tool_call>{json.dumps(p['functionCall'])}</tool_call>"

    return completion.strip() if completion.strip() else None


def parse_gemini_interaction(req: dict[str, Any], resp: dict[str, Any]) -> dict[str, Any] | None:
    """Extract system instructions, user turns, and model turns into standard format."""
    messages: list[dict[str, str]] = []

    sys_text = _extract_system_instruction(req)
    if sys_text:
        messages.append({"role": "system", "content": sys_text})

    turns = _extract_conversation_turns(req)
    messages.extend(turns)

    completion = _extract_model_completion(resp)
    if not completion:
        return None

    messages.append({"role": "assistant", "content": completion})
    return {"messages": messages}


def _process_single_stream_event(item: Any) -> dict[str, Any] | None:
    """Extract and validate training pair from a single Redis stream entry."""
    if not item or len(item) < 2 or not isinstance(item[1], dict):
        return None
    data: dict[Any, Any] = item[1]
    try:
        req = json.loads(str(data["request_json"]))
        resp = json.loads(str(data["response_json"]))
    except (json.JSONDecodeError, KeyError):
        return None

    if "generatecontent" not in str(data.get("endpoint", "")).lower():
        return None

    parsed = parse_gemini_interaction(req, resp)
    if not parsed or len(parsed.get("messages", [])) < 2:
        return None

    parsed["metadata"] = {
        "session_id": data.get("session_id"),
        "latency_ms": float(data.get("latency_ms", 0)),
        "timestamp": float(data.get("timestamp", 0)),
    }
    return parsed


def export_traces(output_file: str, redis_host: str = "localhost", redis_port: int = 6379) -> int:
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    stream_key = "antigravity:stream:audit"

    print(f"Reading records from Redis Stream: {stream_key}...")
    try:
        raw_events = r.xrange(stream_key, min="-", max="+")
    except Exception as err:
        print(f"Error connecting to Redis at {redis_host}:{redis_port}: {err}")
        return 0

    events = raw_events if raw_events is not None else []
    print(f"Found {len(events)} total transactions.")
    valid_samples = 0

    with open(output_file, "w", encoding="utf-8") as out:
        for item in events:
            sample = _process_single_stream_event(item)
            if sample is not None:
                out.write(json.dumps(sample) + "\n")
                valid_samples += 1

    print(f"Successfully exported {valid_samples} training examples to: {output_file}")
    return valid_samples


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export Antigravity Redis logs to SFT training JSONL"
    )
    parser.add_argument("--out", default="antigravity_training_dataset.jsonl", help="Output path")
    parser.add_argument("--host", default="localhost", help="Redis host")
    parser.add_argument("--port", type=int, default=6379, help="Redis port")
    args = parser.parse_args()
    export_traces(args.out, redis_host=args.host, redis_port=args.port)


if __name__ == "__main__":
    main()
