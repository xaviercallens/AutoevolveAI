#!/usr/bin/env python3
"""
DPO Dataset Builder:
Correlates failed agent traces with verified completions using Redis attestation receipts.
Exports aligned (prompt, chosen, rejected) triplets for Direct Preference Optimization (TRL / Unsloth).
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))


def _extract_dpo_system_prompt(req: dict[str, Any]) -> dict[str, str] | None:
    """Extract system instruction message from request payload."""
    sys_inst = req.get("system_instruction", {}).get("parts", [])
    if not sys_inst:
        return None
    parts = [p.get("text", "") for p in sys_inst if "text" in p]
    text = "\n".join(parts).strip()
    return {"role": "system", "content": text} if text else None


def _extract_dpo_history(req: dict[str, Any]) -> list[dict[str, str]]:
    """Extract conversation history turns from request payload."""
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


def _extract_dpo_completion(resp: dict[str, Any]) -> str:
    """Extract final model completion or tool calls from response payload."""
    candidates = resp.get("candidates", [])
    if not candidates:
        return ""
    parts = candidates[0].get("content", {}).get("parts", [])
    chunks: list[str] = []
    for p in parts:
        if "text" in p:
            chunks.append(p["text"])
        elif "functionCall" in p:
            chunks.append(f"<tool_call>{json.dumps(p['functionCall'])}</tool_call>")
    return "\n".join(chunks).strip()


def _parse_json_field(val: Any) -> Any:
    """Parse JSON field if encoded as string or bytes, or return as-is."""
    if isinstance(val, (bytes, str)):
        try:
            return json.loads(val)
        except (json.JSONDecodeError, KeyError):
            return {}
    return val if isinstance(val, dict) else {}


def _discover_candidate_subtasks(r: Any) -> list[str]:
    """Discover subtask IDs from completed sets or key pattern scanning."""
    completed = r.smembers("antigravity:subtasks:completed")
    if completed:
        return [s.decode("utf-8") if isinstance(s, bytes) else str(s) for s in completed]

    keys = r.keys("antigravity:subtask:*:traces")
    subtask_ids: list[str] = []
    for k in keys:
        key_str = k.decode("utf-8") if isinstance(k, bytes) else str(k)
        parts = key_str.split(":")
        if len(parts) >= 3:
            subtask_ids.append(parts[2])
    return list(dict.fromkeys(subtask_ids))


def _classify_subtask_traces(
    trace_ids: list[str], r: Any
) -> tuple[str | None, list[tuple[str, str]]]:
    """Classify traces into a chosen passing trace and list of rejected failed traces."""
    chosen_trace_id: str | None = None
    failed_traces: list[tuple[str, str]] = []

    for trace_id in trace_ids:
        tid_str = trace_id.decode("utf-8") if isinstance(trace_id, bytes) else str(trace_id)
        att_raw = r.hgetall(f"antigravity:attestation:{tid_str}")
        if not att_raw:
            continue
        att = {
            (k.decode("utf-8") if isinstance(k, bytes) else str(k)): (
                v.decode("utf-8") if isinstance(v, bytes) else str(v)
            )
            for k, v in att_raw.items()
        }
        verdict = att.get("verdict", "")
        if verdict == "PASSED":
            chosen_trace_id = tid_str
        elif verdict == "FAILED":
            reasons = att.get("reasons", "[]")
            failed_traces.append((tid_str, reasons))

    return chosen_trace_id, failed_traces


def _load_trace_payloads(trace_id: str, r: Any) -> tuple[dict[str, Any], dict[str, Any]] | None:
    """Load and parse request and response payloads for a trace."""
    raw = r.get(f"antigravity:trace:{trace_id}")
    if not raw:
        return None
    raw_str = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
    try:
        record = json.loads(raw_str)
    except (json.JSONDecodeError, KeyError, OSError):
        return None
    req = _parse_json_field(record.get("request_json"))
    resp = _parse_json_field(record.get("response_json"))
    return req, resp


def compute_edit_distance_ratio(s1: str, s2: str) -> float:
    """Computes normalized Levenshtein edit distance between 0.0 (identical) and 1.0."""
    if not s1 and not s2:
        return 0.0
    if s1 == s2:
        return 0.0
    if not s1 or not s2:
        return 1.0

    # Cap comparison length to 80 chars for thermodynamic algorithmic efficiency
    s1, s2 = s1[:80], s2[:80]
    len1, len2 = len(s1), len(s2)
    prev_row = list(range(len2 + 1))
    for i, c1 in enumerate(s1):
        curr_row = [i + 1] * (len2 + 1)
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row[j + 1] = min(insertions, deletions, substitutions)
        prev_row = curr_row

    dist = prev_row[len2]
    return min(1.0, dist / max(len1, len2))


def compute_trajectory_reward(
    lean_valid: bool = False,
    tests_pass: bool = False,
    anti_stub_failed: bool = False,
    edit_distance_human: float = 0.0,
    w1: float = 2.0,
    w2: float = 1.0,
    w3: float = 1.5,
    w4: float = 1.0,
) -> float:
    """
    Evaluates the physical Mini-RL scalar reward:
    R = (W1 * LeanValid) + (W2 * TestsPass) - (W3 * AntiStubFailed) - (W4 * EditDistanceHuman)
    """
    reward = (
        (w1 if lean_valid else 0.0)
        + (w2 if tests_pass else 0.0)
        - (w3 if anti_stub_failed else 0.0)
        - (w4 * edit_distance_human)
    )
    return round(reward, 4)


def _load_human_ground_truth(subtask_id: str, r: Any) -> str | None:
    """Retrieves human patch or developer-verified final implementation from Redis."""
    raw = r.get(f"antigravity:subtask:{subtask_id}:human_patch")
    if not raw:
        raw = r.get(f"antigravity:telemetry:{subtask_id}:chosen")
    if not raw:
        return None
    return raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)


def _build_prompt_messages(req: dict[str, Any]) -> list[dict[str, str]]:
    """Build prompt history list from request payload."""
    prompt_messages: list[dict[str, str]] = []
    sys_prompt = _extract_dpo_system_prompt(req)
    if sys_prompt:
        prompt_messages.append(sys_prompt)
    prompt_messages.extend(_extract_dpo_history(req))
    return prompt_messages


def _create_single_rejected_pair(
    rej_trace_id: str,
    reasons_str: str,
    r: Any,
    subtask_id: str,
    chosen_trace_id: str,
    reference_winner: str,
    human_patch: str | None,
    chosen_reward: float,
    prompt_messages: list[dict[str, str]],
) -> dict[str, Any] | None:
    """Creates a single DPO pair for a failed trace."""
    rej_payloads = _load_trace_payloads(rej_trace_id, r)
    if not rej_payloads:
        return None
    _, rej_resp = rej_payloads
    rej_text = _extract_dpo_completion(rej_resp)
    if not rej_text:
        return None

    reasons = _parse_json_field(reasons_str)
    failure_reasons = reasons if isinstance(reasons, list) else [str(reasons)]
    is_stub_fail = any("stub" in str(reason).lower() for reason in failure_reasons)

    ref_for_dist = human_patch if human_patch else reference_winner
    rej_dist = compute_edit_distance_ratio(rej_text, ref_for_dist)
    rej_reward = compute_trajectory_reward(
        tests_pass=False,
        anti_stub_failed=is_stub_fail,
        edit_distance_human=rej_dist,
    )

    return {
        "prompt": prompt_messages,
        "chosen": reference_winner,
        "rejected": rej_text,
        "metadata": {
            "subtask_id": subtask_id,
            "chosen_trace_id": chosen_trace_id,
            "rejected_trace_id": rej_trace_id,
            "failure_reasons": failure_reasons,
            "reward_chosen": chosen_reward,
            "reward_rejected": rej_reward,
            "reward_delta": round(chosen_reward - rej_reward, 4),
            "human_ground_truth_applied": bool(human_patch),
        },
    }


def _build_pairs_for_subtask(
    subtask_id: str,
    chosen_trace_id: str,
    failed_traces: list[tuple[str, str]],
    r: Any,
) -> list[dict[str, Any]]:
    """Build DPO training pairs from chosen trace, failed traces, and human telemetry."""
    chosen_payloads = _load_trace_payloads(chosen_trace_id, r)
    if not chosen_payloads:
        return []

    req, chosen_resp = chosen_payloads
    chosen_text = _extract_dpo_completion(chosen_resp)
    if not chosen_text:
        return []

    human_patch = _load_human_ground_truth(subtask_id, r)
    reference_winner = human_patch if human_patch else chosen_text

    prompt_messages = _build_prompt_messages(req)
    if not prompt_messages:
        return []

    chosen_dist = compute_edit_distance_ratio(chosen_text, human_patch) if human_patch else 0.0
    chosen_reward = compute_trajectory_reward(
        tests_pass=True,
        anti_stub_failed=False,
        edit_distance_human=chosen_dist,
    )

    pairs: list[dict[str, Any]] = []
    for rej_trace_id, reasons_str in failed_traces:
        pair = _create_single_rejected_pair(
            rej_trace_id=rej_trace_id,
            reasons_str=reasons_str,
            r=r,
            subtask_id=subtask_id,
            chosen_trace_id=chosen_trace_id,
            reference_winner=reference_winner,
            human_patch=human_patch,
            chosen_reward=chosen_reward,
            prompt_messages=prompt_messages,
        )
        if pair:
            pairs.append(pair)

    return pairs


def _process_subtask_traces(subtask_id: str, r: Any) -> list[dict[str, Any]]:
    """Process a single subtask, returning any generated DPO pairs."""
    raw_traces = r.lrange(f"antigravity:subtask:{subtask_id}:traces", 0, -1)
    if not raw_traces:
        return []
    trace_ids = [
        t.decode("utf-8") if isinstance(t, bytes) else str(t)
        for t in list(dict.fromkeys(raw_traces))
    ]
    chosen_tid, failed_traces = _classify_subtask_traces(trace_ids, r)
    if chosen_tid and failed_traces:
        return _build_pairs_for_subtask(subtask_id, chosen_tid, failed_traces, r)
    return []


def _write_pairs_to_jsonl(output_file: str, pairs: list[dict[str, Any]]) -> None:
    """Write generated DPO pairs to a JSONL file."""
    with open(output_file, "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p) + "\n")


def extract_dpo_pairs(
    output_file: str | None = None,
    redis_client: Any = None,
    redis_host: str = "localhost",
    redis_port: int = 6379,
    max_workers: int = 16,
) -> list[dict[str, Any]]:
    """Extract DPO training triplets from Redis for all aligned subtasks."""
    r = redis_client or redis.Redis(host=redis_host, port=redis_port, decode_responses=False)
    subtask_ids = _discover_candidate_subtasks(r)
    all_pairs: list[dict[str, Any]] = []

    if max_workers > 1 and len(subtask_ids) > 10:
        from concurrent.futures import ThreadPoolExecutor

        def _fetch_worker(sid: str) -> list[dict[str, Any]]:
            return _process_subtask_traces(sid, r)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            batch_results = list(executor.map(_fetch_worker, subtask_ids))
            for pairs in batch_results:
                all_pairs.extend(pairs)
    else:
        for subtask_id in subtask_ids:
            pairs = _process_subtask_traces(subtask_id, r)
            all_pairs.extend(pairs)

    if output_file and all_pairs:
        _write_pairs_to_jsonl(output_file, all_pairs)

    return all_pairs


def main() -> None:
    """CLI entrypoint for extracting DPO training pairs."""
    parser = argparse.ArgumentParser(
        description="Extract DPO preference pairs (prompt, chosen, rejected) from Redis"
    )
    parser.add_argument("--out", default="antigravity_dpo_dataset.jsonl", help="Output JSONL path")
    parser.add_argument("--host", default="localhost", help="Redis host")
    parser.add_argument("--port", type=int, default=6379, help="Redis port")
    args = parser.parse_args()

    pairs = extract_dpo_pairs(output_file=args.out, redis_host=args.host, redis_port=args.port)
    print(f"Extracted {len(pairs)} DPO pairs to {args.out}")


if __name__ == "__main__":
    main()
