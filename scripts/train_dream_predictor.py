#!/usr/bin/env python3
"""Train the dream-phase verdict predictor from the verified pool, behind a gate.

Steps:
1. Import: if the pool file does not exist yet, copy the cosmo3 verdict corpus into it. Each
   row is validated against the pool contract. The source rows carry no ``embedding_model``, so
   it is filled from the retrofit summary, which recorded the embedder that produced them.
2. Gate: run real and shuffled-label probes across task-grouped folds and seeds
   (``anse.jepa.dream_predictor_trainer.evaluate_gate``).
3. Report: write ``results/dream_predictor/gate_report.json`` with the numbers, PASS or BLOCKED.
4. Checkpoint: only on PASS, fit the probe on every row and write
   ``checkpoints/dream_predictor_probe.pt`` plus a manifest. On BLOCKED nothing is written, and
   the script exits 2 so the pipeline step fails closed.

Usage:
    .venv/bin/python scripts/train_dream_predictor.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from anse.jepa.dream_predictor_trainer import evaluate_gate, fit_probe_state  # noqa: E402
from anse.jepa.verified_pool import append_verified_episode, load_verified_pool  # noqa: E402

POOL_PATH = Path(
    "/mnt/disks/disk-socrateai-local-1/AutoevolveAI/datalake/episodes/verified_pool.jsonl"
)
COSMO3_SOURCE = Path(
    "/mnt/disks/disk-socrateai-local-1/AutoevolveAI/datalake/episodes/cosmo3_2026-09-27.jsonl"
)
COSMO3_SUMMARY = REPO / "results" / "cosmo3_learning" / "retrofit_summary.json"
REPORT_PATH = REPO / "results" / "dream_predictor" / "gate_report.json"
CHECKPOINT = REPO / "checkpoints" / "dream_predictor_probe.pt"
MANIFEST = REPO / "checkpoints" / "dream_predictor_probe.manifest.json"


def import_cosmo3(pool_path: Path, embedding_dim: int) -> dict[str, int]:
    """Copy the cosmo3 verdicts into a fresh pool. Refuses to re-import into an existing pool."""
    summary = json.loads(COSMO3_SUMMARY.read_text(encoding="utf-8"))
    embedder = summary["embedding_model"]
    counts = {"imported": 0, "refused": 0}
    for line in COSMO3_SOURCE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        row["metadata"] = dict(row.get("metadata", {}), embedding_model=embedder)
        try:
            append_verified_episode(pool_path, row, embedding_dim)
            counts["imported"] += 1
        except ValueError:
            counts["refused"] += 1
    return counts


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    embedding_dim = int(json.loads(COSMO3_SUMMARY.read_text(encoding="utf-8"))["embedding_dim"])

    if not POOL_PATH.exists():
        imported = import_cosmo3(POOL_PATH, embedding_dim)
        print(f"pool created at {POOL_PATH}: {imported}")

    rows, refused = load_verified_pool(POOL_PATH, embedding_dim)
    gate = evaluate_gate(rows)
    report: dict[str, Any] = {
        "status": gate.status,
        "timestamp": datetime.now(UTC).isoformat(),
        "pool": str(POOL_PATH),
        "pool_sha256": sha256_file(POOL_PATH),
        "rows_accepted": len(rows),
        "rows_refused": refused,
        "positives_failed": gate.positives,
        "embedding_dim": embedding_dim,
        "worst_real_fold_auroc": gate.worst_real,
        "best_control_fold_auroc": gate.control_best,
        "control_spread": gate.control_spread,
        "real_folds": gate.real_folds,
        "control_folds": gate.control_folds,
        "reasons": gate.reasons,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "status",
                    "rows_accepted",
                    "worst_real_fold_auroc",
                    "best_control_fold_auroc",
                    "control_spread",
                )
            },
            indent=2,
        )
    )

    if gate.status != "PASS":
        print("BLOCKED: no checkpoint written. Reasons: " + "; ".join(gate.reasons))
        return 2

    labels = torch.tensor([float(r["energy"]) for r in rows], dtype=torch.float32)
    x = torch.tensor([r["hidden_state"] for r in rows], dtype=torch.float32)
    state = fit_probe_state(x, labels, seed=0)
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    torch.save(state, CHECKPOINT)
    MANIFEST.write_text(
        json.dumps(
            {
                "checkpoint": str(CHECKPOINT),
                "sha256": sha256_file(CHECKPOINT),
                "pool_sha256": report["pool_sha256"],
                "embedding_dim": embedding_dim,
                "rows": len(rows),
                "gate_report": str(REPORT_PATH),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"PASS: checkpoint written to {CHECKPOINT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
