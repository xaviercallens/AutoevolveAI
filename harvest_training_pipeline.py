#!/usr/bin/env python3
"""
Continuous Data Harvester for LoRA & RL:
Extracts execution traces and deterministic attestation receipts from Redis into:
1. SFT Training Data (Verified successful executions across frontier and local models)
2. DPO Preference Pairs (Chosen passing implementation vs. rejected stubs/failures)
3. GRPO / RL Training Groups (Prompts with multiple candidate outputs and scalar reward labels)
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))


def _extract_system_turn(req: dict[str, Any]) -> dict[str, str] | None:
    """Extract system instruction message from Gemini request payload."""
    sys_parts = req.get("system_instruction", {}).get("parts", [])
    if not sys_parts:
        return None
    sys_text = "\n".join(p.get("text", "") for p in sys_parts if "text" in p).strip()
    return {"role": "system", "content": sys_text} if sys_text else None


def _extract_conversation_turns(req: dict[str, Any]) -> list[dict[str, str]]:
    """Extract user and prior assistant turns from Gemini request payload."""
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
    """Extract final model completion or tool calls from Gemini response payload."""
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


def parse_trace_message(
    req_raw: Any, resp_raw: Any
) -> tuple[list[dict[str, str]] | None, str | None]:
    """Parse raw request and response JSON payloads into conversational turns and completion."""
    try:
        req = json.loads(req_raw) if isinstance(req_raw, (str, bytes)) else req_raw
        resp = json.loads(resp_raw) if isinstance(resp_raw, (str, bytes)) else resp_raw
    except (json.JSONDecodeError, KeyError):
        return None, None

    if not isinstance(req, dict) or not isinstance(resp, dict):
        return None, None

    messages: list[dict[str, str]] = []
    sys_turn = _extract_system_turn(req)
    if sys_turn:
        messages.append(sys_turn)
    messages.extend(_extract_conversation_turns(req))

    completion = _extract_candidate_completion(resp)
    return (messages, completion) if (messages and completion) else (None, None)


def _classify_subtask_verdicts(
    trace_ids: list[str], r: Any
) -> tuple[list[tuple[str, dict[str, str]]], list[tuple[str, dict[str, str]]]]:
    """Classify traces into passed and failed lists based on Redis attestation hashes."""
    passed_traces: list[tuple[str, dict[str, str]]] = []
    failed_traces: list[tuple[str, dict[str, str]]] = []

    for tid in trace_ids:
        tid_str = tid.decode("utf-8") if isinstance(tid, bytes) else str(tid)
        raw_att = r.hgetall(f"antigravity:attestation:{tid_str}")
        if not raw_att:
            continue
        att = {
            (k.decode("utf-8") if isinstance(k, bytes) else str(k)): (
                v.decode("utf-8") if isinstance(v, bytes) else str(v)
            )
            for k, v in raw_att.items()
        }
        verdict = att.get("verdict")
        if verdict == "PASSED":
            passed_traces.append((tid_str, att))
        elif verdict == "FAILED":
            failed_traces.append((tid_str, att))

    return passed_traces, failed_traces


def _harvest_sft_from_passed(
    passed_traces: list[tuple[str, dict[str, str]]], r: Any
) -> list[dict[str, Any]]:
    """Harvest verified successful traces for Supervised Fine-Tuning (SFT)."""
    sft_records: list[dict[str, Any]] = []
    for tid, _ in passed_traces:
        raw = r.get(f"antigravity:trace:{tid}")
        if not raw:
            continue
        raw_str = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
        try:
            record = json.loads(raw_str)
        except (json.JSONDecodeError, KeyError):
            continue

        msgs, comp = parse_trace_message(record.get("request_json"), record.get("response_json"))
        if msgs and comp:
            sft_records.append(
                {
                    "messages": msgs + [{"role": "assistant", "content": comp}],
                    "metadata": {
                        "trace_id": tid,
                        "model": record.get("model_used", "unknown"),
                        "phase": record.get("phase", "EXECUTION"),
                    },
                }
            )
    return sft_records


def _build_dpo_and_grpo_pairs(
    passed_traces: list[tuple[str, dict[str, str]]],
    failed_traces: list[tuple[str, dict[str, str]]],
    r: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Pair successful completions with failed attempts for DPO and GRPO formats."""
    dpo_records: list[dict[str, Any]] = []
    grpo_records: list[dict[str, Any]] = []

    best_tid, _ = passed_traces[-1]
    best_raw = r.get(f"antigravity:trace:{best_tid}")
    if not best_raw:
        return [], []

    best_str = best_raw.decode("utf-8") if isinstance(best_raw, bytes) else str(best_raw)
    best_record = json.loads(best_str)
    prompt_msgs, chosen_comp = parse_trace_message(
        best_record.get("request_json"), best_record.get("response_json")
    )
    if not prompt_msgs or not chosen_comp:
        return [], []

    for fail_tid, fail_att in failed_traces:
        fail_raw = r.get(f"antigravity:trace:{fail_tid}")
        if not fail_raw:
            continue
        fail_str = fail_raw.decode("utf-8") if isinstance(fail_raw, bytes) else str(fail_raw)
        fail_record = json.loads(fail_str)
        _, rejected_comp = parse_trace_message(
            fail_record.get("request_json"), fail_record.get("response_json")
        )
        if not rejected_comp or rejected_comp == chosen_comp:
            continue

        dpo_records.append(
            {"prompt": prompt_msgs, "chosen": chosen_comp, "rejected": rejected_comp}
        )
        grpo_records.append(
            {
                "prompt": prompt_msgs,
                "candidates": [
                    {"completion": chosen_comp, "reward": 1.0, "verdict": "PASSED"},
                    {
                        "completion": rejected_comp,
                        "reward": -1.0,
                        "verdict": "FAILED",
                        "reasons": json.loads(fail_att.get("reasons", "[]")),
                    },
                ],
            }
        )

    return dpo_records, grpo_records


def _write_jsonl(file_path: Path, records: list[dict[str, Any]]) -> None:
    """Write list of dictionaries to JSONL format."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        for r_entry in records:
            f.write(json.dumps(r_entry) + "\n")


def _process_subtask_key(
    st_key: Any, r: Any
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Extracts SFT, DPO, and GRPO records for a single subtask key."""
    raw_trace_ids = r.lrange(st_key, 0, -1) or []
    trace_ids = [
        t.decode("utf-8") if isinstance(t, bytes) else str(t)
        for t in list(dict.fromkeys(raw_trace_ids))
    ]
    passed_traces, failed_traces = _classify_subtask_verdicts(trace_ids, r)
    sft_samples = _harvest_sft_from_passed(passed_traces, r)

    dpo_samples: list[dict[str, Any]] = []
    grpo_samples: list[dict[str, Any]] = []
    if passed_traces and failed_traces:
        dpo_samples, grpo_samples = _build_dpo_and_grpo_pairs(passed_traces, failed_traces, r)

    return sft_samples, dpo_samples, grpo_samples


def _write_harvested_outputs(
    sft_out: Path | None,
    dpo_out: Path | None,
    grpo_out: Path | None,
    all_sft: list[dict[str, Any]],
    all_dpo: list[dict[str, Any]],
    all_grpo: list[dict[str, Any]],
) -> None:
    """Writes harvested dataset lists to their respective JSONL output files."""
    if sft_out:
        _write_jsonl(sft_out, all_sft)
    if dpo_out:
        _write_jsonl(dpo_out, all_dpo)
    if grpo_out:
        _write_jsonl(grpo_out, all_grpo)


def harvest_datasets(
    sft_out: Path | None = None,
    dpo_out: Path | None = None,
    grpo_out: Path | None = None,
    redis_client: Any = None,
    redis_host: str = REDIS_HOST,
    redis_port: int = REDIS_PORT,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Continuous data harvester for SFT, DPO, and GRPO training datasets."""
    r = redis_client or redis.Redis(host=redis_host, port=redis_port, decode_responses=False)
    subtask_keys = r.keys("antigravity:subtask:*:traces") or []

    all_sft: list[dict[str, Any]] = []
    all_dpo: list[dict[str, Any]] = []
    all_grpo: list[dict[str, Any]] = []

    for st_key in subtask_keys:
        sft_s, dpo_s, grpo_s = _process_subtask_key(st_key, r)
        all_sft.extend(sft_s)
        all_dpo.extend(dpo_s)
        all_grpo.extend(grpo_s)

    _write_harvested_outputs(sft_out, dpo_out, grpo_out, all_sft, all_dpo, all_grpo)
    return all_sft, all_dpo, all_grpo


def main() -> None:
    """CLI Entrypoint for the Continuous Data Harvester."""
    parser = argparse.ArgumentParser(
        description="Extract SFT, DPO, and GRPO training datasets from persistent Redis traces"
    )
    parser.add_argument("--sft-out", default="dataset_sft.jsonl", help="Output SFT JSONL path")
    parser.add_argument("--dpo-out", default="dataset_dpo.jsonl", help="Output DPO JSONL path")
    parser.add_argument("--grpo-out", default="dataset_grpo.jsonl", help="Output GRPO JSONL path")
    parser.add_argument("--host", default=REDIS_HOST, help="Redis host")
    parser.add_argument("--port", type=int, default=REDIS_PORT, help="Redis port")
    args = parser.parse_args()

    sft, dpo, grpo = harvest_datasets(
        sft_out=Path(args.sft_out),
        dpo_out=Path(args.dpo_out),
        grpo_out=Path(args.grpo_out),
        redis_host=args.host,
        redis_port=args.port,
    )
    print(f"✅ Harvester complete: SFT={len(sft)}, DPO={len(dpo)}, GRPO={len(grpo)}")


if __name__ == "__main__":
    main()
