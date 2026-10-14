#!/usr/bin/env python3
"""Read-only audit: does the Redis LTM transcript store agree with the Chroma transcript index?

Redis key  anse:ltm:transcript:<session>:<turn>      (hash)
Chroma id  <session>:<turn>:<chunk>                  (collection claude_code_sessions)

Reports turns present in only one store and any row whose `trainable` flag disagrees with its
`usage` (transcript rows are retrieval_only until docs/v2/gates/N8.md exists, see origin policy).
Writes nothing to Redis or Chroma. Exit 0 = consistent, 1 = discrepancies found.

    .venv/bin/python scripts/ltm_consistency_audit.py [--chroma datalake/chroma/ltm/transcripts]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import chromadb
import redis


def redis_turns(client: redis.Redis) -> tuple[set[tuple[str, str]], list[str]]:
    turns: set[tuple[str, str]] = set()
    bad_flags: list[str] = []
    for key in client.scan_iter("anse:ltm:transcript:*"):
        parts = key.split(":")
        if len(parts) != 5:
            continue
        turns.add((parts[3], parts[4]))
        row = client.hmget(key, ["trainable", "usage"])
        if row[0] == "1" and row[1] == "retrieval_only":
            bad_flags.append(key)
    return turns, bad_flags


def chroma_turns(path: Path) -> tuple[set[tuple[str, str]], list[str]]:
    col = chromadb.PersistentClient(path=str(path)).get_collection("claude_code_sessions")
    rec = col.get(limit=col.count(), include=["metadatas"])
    turns: set[tuple[str, str]] = set()
    bad_flags: list[str] = []
    for cid, meta in zip(rec["ids"], rec["metadatas"], strict=True):
        session, turn, _chunk = cid.rsplit(":", 2)
        turns.add((session, turn))
        if meta.get("trainable") is True and meta.get("usage") == "retrieval_only":
            bad_flags.append(cid)
    return turns, bad_flags


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--chroma", type=Path, default=Path("datalake/chroma/ltm/transcripts"))
    a = p.parse_args()
    r_turns, r_bad = redis_turns(redis.Redis(decode_responses=True))
    c_turns, c_bad = chroma_turns(a.chroma)
    only_r, only_c = sorted(r_turns - c_turns), sorted(c_turns - r_turns)
    print(f"redis turns={len(r_turns)} chroma turns={len(c_turns)} both={len(r_turns & c_turns)}")
    print(f"only in redis: {len(only_r)} {only_r[:3]}")
    print(f"only in chroma: {len(only_c)} {only_c[:3]}")
    print(f"trainable-but-retrieval_only: redis={len(r_bad)} chroma={len(c_bad)}")
    return 0 if not (only_r or only_c or r_bad or c_bad) else 1


if __name__ == "__main__":
    sys.exit(main())
