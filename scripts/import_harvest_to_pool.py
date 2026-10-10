#!/usr/bin/env python3
"""Import sandbox-verified harvest episodes into the verified pool as binary verdicts.

The harvest runs each hidden assertion separately in the sandbox, so ``tests_passed`` is a real
count. Its energy is continuous (failures weighted by 100, plus a runtime tiebreak). The pool
needs a binary verdict, so the label here is: 0.0 when every hidden assertion passed, 1.0 when
any failed. Rows with ``tests_total == 0`` are not verdicts and are refused by the contract.

Idempotent per source file: refuses if rows tagged with this file's source are already present.

Usage:
    .venv/bin/python scripts/import_harvest_to_pool.py data/episodes/harvest_2026-10-10.jsonl
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from anse.jepa.verified_pool import append_verified_episode, load_verified_pool  # noqa: E402

POOL_PATH = Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI/datalake/episodes/verified_pool.jsonl")
DIM = 1024
EMBEDDER = "qwen3-embedding:0.6b"


def binary_episode(row: dict[str, Any], source_tag: str) -> dict[str, Any]:
    meta = row.get("metadata", {})
    passed = int(meta.get("tests_passed", 0))
    total = int(meta.get("tests_total", 0))
    return {
        "task": f"harvest:{row['task']}",
        "hidden_state": row["hidden_state"],
        "energy": 0.0 if total > 0 and passed == total else 1.0,
        "converged": total > 0 and passed == total,
        "metadata": {
            "tests_total": total,
            "tests_passed": passed,
            "verifier": "anse.symbolic.sandbox per-assertion execution",
            "evidence_path": source_tag,
            "embedding_model": EMBEDDER,
            "source": source_tag,
            "iteration": row.get("iteration", 0),
        },
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    source = Path(sys.argv[1])
    source_tag = f"harvest_sandbox:{source.name}"
    existing, _ = load_verified_pool(POOL_PATH, DIM) if POOL_PATH.exists() else ([], {})
    if any(r.get("metadata", {}).get("source") == source_tag for r in existing):
        print(f"already imported: {source_tag}; nothing written")
        return 0

    imported = refused = passes = 0
    for line in source.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        episode = binary_episode(json.loads(line), source_tag)
        try:
            append_verified_episode(POOL_PATH, episode, DIM)
            imported += 1
            passes += int(episode["energy"] == 0.0)
        except ValueError:
            refused += 1
    print(json.dumps({"source": source_tag, "imported": imported, "refused": refused,
                      "passes": passes, "failures": imported - passes}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
