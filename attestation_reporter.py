#!/usr/bin/env python3
"""
Attestation Reporter:
Logs deterministic verification verdicts back to Redis for DPO pairing.
"""

from __future__ import annotations

import json
import os
from typing import Any

import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))


def record_attestation_verdict(
    trace_id: str,
    subtask_id: str,
    passed: bool,
    reasons: list[str],
    test_stdout: str = "",
    redis_client: Any = None,
) -> None:
    """Record verification verdict, failure reasons, and bounded test log into Redis."""
    r = redis_client or redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    verdict_record = {
        "trace_id": trace_id,
        "subtask_id": subtask_id,
        "verdict": "PASSED" if passed else "FAILED",
        "reasons": json.dumps(reasons),
        "test_stdout": test_stdout[-2000:],
    }

    try:
        pipe = r.pipeline()
        pipe.hset(f"antigravity:attestation:{trace_id}", mapping=verdict_record)  # type: ignore[arg-type]
        if subtask_id:
            pipe.rpush(f"antigravity:subtask:{subtask_id}:traces", trace_id)
            status_set = (
                "antigravity:subtasks:completed" if passed else "antigravity:subtasks:in_progress"
            )
            pipe.sadd(status_set, subtask_id)
        pipe.execute()
    except Exception as err:
        print(f"Warning: Failed to record attestation verdict to Redis: {err}")
