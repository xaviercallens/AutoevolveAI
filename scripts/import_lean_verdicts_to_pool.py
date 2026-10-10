#!/usr/bin/env python3
"""Import real Lean verifier verdicts from the premise-retrieval A/B into the verified pool.

Source: results/hardness/retrieval_ab.json, one row per (model, arm, item). A row is imported
only when the Lean compiler actually ran on the proof (``compile_s`` present). A row where no
proof was extracted is not a verifier verdict and is excluded.

Label: energy 0.0 when the proof compiled cleanly with only whitelisted axioms (``clean``),
otherwise 1.0. Task = the hardness item, so folds never share an item between train and test.
Embedding = qwen3-embedding:0.6b over the item id, tier, model, arm and the proof head.

Idempotent: refuses to import when rows from this source are already in the pool.

Usage:
    .venv/bin/python scripts/import_lean_verdicts_to_pool.py
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, "/mnt/disks/disk-socrateai-local-1/gpu_lease")

from gpu_lease import gpu_lease  # noqa: E402

from anse.jepa.verified_pool import append_verified_episode, load_verified_pool  # noqa: E402
from anse.memory.ollama_embeddings import OllamaEmbeddingFunction  # noqa: E402

SOURCE_JSON = REPO / "results" / "hardness" / "retrieval_ab.json"
POOL_PATH = Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI/datalake/episodes/verified_pool.jsonl")
EMBEDDER = "qwen3-embedding:0.6b"
DIM = 1024
SOURCE_TAG = "retrieval_ab_lean_verifier"
PROOF_HEAD_CHARS = 600


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip() == "True"


def _axioms(value: Any) -> list[str]:
    if isinstance(value, list):
        return value
    try:
        parsed = ast.literal_eval(str(value))
    except (ValueError, SyntaxError):
        return []
    return parsed if isinstance(parsed, list) else []


def verdict_rows(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep only runs where the compiler ran, and attach the binary verdict."""
    kept: list[dict[str, Any]] = []
    for run in runs:
        if "compile_s" not in run or run.get("compile_s") in (None, "None", ""):
            continue
        clean = _as_bool(run.get("clean"))
        kept.append(
            {
                "item": str(run["id"]),
                "tier": str(run["tier"]),
                "model": str(run["model"]),
                "arm": str(run["arm"]),
                "clean": clean,
                "axioms": _axioms(run.get("axioms")),
                "proof_head": str(run.get("proof_head", ""))[:PROOF_HEAD_CHARS],
            }
        )
    return kept


def episode_text(row: dict[str, Any]) -> str:
    return (
        f"lean hardness {row['tier']} item {row['item']} model {row['model']} arm {row['arm']}\n"
        f"{row['proof_head']}"
    )


def main() -> int:
    if not SOURCE_JSON.exists():
        print(f"missing source {SOURCE_JSON}", file=sys.stderr)
        return 1

    existing, _ = load_verified_pool(POOL_PATH, DIM) if POOL_PATH.exists() else ([], {})
    if any(r.get("metadata", {}).get("source") == SOURCE_TAG for r in existing):
        print(f"already imported: pool already holds rows tagged {SOURCE_TAG}; nothing written")
        return 0

    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    rows = verdict_rows(data["runs"])
    if not rows:
        print("no compiled runs found in source; nothing imported")
        return 1

    emb = OllamaEmbeddingFunction()
    with gpu_lease("lean-verdict-import", "embed Lean verdicts for the verified pool", ttl_s=1800, timeout_s=3600):
        vectors = emb([episode_text(r) for r in rows])

    imported = 0
    refused = 0
    for row, vec in zip(rows, vectors, strict=True):
        episode = {
            "task": f"lean:{row['tier']}:{row['item']}",
            "hidden_state": [float(v) for v in vec],
            "energy": 0.0 if row["clean"] else 1.0,
            "converged": row["clean"],
            "metadata": {
                "tests_total": 1,
                "tests_passed": 1 if row["clean"] else 0,
                "verifier": "anse.formal.lean_runner.verify_file",
                "evidence_path": "results/hardness/retrieval_ab.json",
                "embedding_model": EMBEDDER,
                "source": SOURCE_TAG,
                "model": row["model"],
                "arm": row["arm"],
                "axioms": row["axioms"],
            },
        }
        try:
            append_verified_episode(POOL_PATH, episode, DIM)
            imported += 1
        except ValueError:
            refused += 1

    passes = sum(1 for r in rows if r["clean"])
    print(json.dumps({"source": SOURCE_TAG, "imported": imported, "refused": refused,
                      "passes": passes, "failures": len(rows) - passes}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
