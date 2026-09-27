#!/usr/bin/env python3
"""
Night Master Regeneration Pipeline

Orchestrates:
1. Generate solutions for 20 master-level math problems with LLM call logging
2. Harvest verified episodes from solutions
3. Run night training workflow to retrain models on new data
4. Report results and gate status

Runs end-to-end on T4 with Ollama, no GPU needed for training (will use CPU fallback).
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("night_master_regen")

REPO = Path(__file__).parent.parent.absolute()
DISK2 = Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI")
CALL_LOGS = DISK2 / "call_logs"
RESULTS = DISK2 / "night_regen_results"


MASTER = REPO / "scripts" / "master_math"


def _run_step(step: str, argv: list[str], timeout_s: int) -> dict[str, Any]:
    """Run one pipeline stage; its exit code is its verdict, never assumed."""
    start = time.time()
    try:
        result = subprocess.run(argv, cwd=str(REPO), capture_output=True, text=True,
                                timeout=timeout_s, env={**os.environ, "PYTHONPATH": str(REPO)})
    except subprocess.TimeoutExpired:
        logger.error(f"{step} timed out after {timeout_s}s")
        return {"step": step, "status": "timeout", "elapsed_s": float(timeout_s)}
    elapsed = time.time() - start
    logger.info(f"{step} exit {result.returncode} in {elapsed:.1f}s; tail: {result.stdout[-500:]}")
    if result.stderr:
        logger.warning(f"{step} stderr: {result.stderr[-500:]}")
    return {"step": step, "status": "completed" if result.returncode == 0 else "failed",
            "exit_code": result.returncode, "elapsed_s": elapsed, "stdout_tail": result.stdout[-1500:]}


def run_master_math_generation() -> dict[str, Any]:
    """Validate the locked master-math statements, then let the provers try them.

    Replaces the run-one regenerator, which sent the model a bare title (the
    model chose -- and could weaken -- its own statement) and took its verdict
    from a canned auditor. Now: statements are fixed in problems.py, the
    instrument's controls must pass first, and the Lean kernel is the only
    judge (`scripts/master_math/run_master.py`; exit 1 = a false item was
    accepted, i.e. the gate is broken).
    """
    logger.info("=== Phase 1: validate controls, then prove the master-math ladder ===")
    CALL_LOGS.mkdir(parents=True, exist_ok=True)
    val = _run_step("master_math_validate", [sys.executable, str(MASTER / "validate.py")], 3600)
    if val["status"] != "completed":
        return {**val, "step": "master_math_generation", "blocked_by": "control failure"}
    return _run_step("master_math_generation", [sys.executable, str(MASTER / "run_master.py")], 6 * 3600)


def harvest_episodes() -> dict[str, Any]:
    """Kernel-clean prover proofs -> PASSED lake rows; clean-vs-failed -> DPO pairs."""
    logger.info("=== Phase 2: Harvest verified episodes ===")
    return _run_step("harvest_episodes", [sys.executable, str(MASTER / "harvest.py")], 600)


def run_night_training() -> dict[str, Any]:
    """Run the night training workflow to retrain models."""
    logger.info("=== Phase 3: Retrain models on harvested episodes ===")

    start = time.time()
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(REPO / "scripts" / "night_training_workflow.py"),
                "--smoke",  # Use quick smoke test for now
            ],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=1200,  # 20 minutes for smoke test
        )
        elapsed = time.time() - start

        logger.info(f"Night training completed in {elapsed:.1f}s")
        logger.info(f"Training output (last 1000 chars): {result.stdout[-1000:]}")

        return {
            "step": "night_training",
            "status": "completed" if result.returncode == 0 else "failed",
            "exit_code": result.returncode,
            "elapsed_s": elapsed,
        }
    except subprocess.TimeoutExpired:
        logger.error("Night training timed out after 1200s")
        return {"step": "night_training", "status": "timeout", "elapsed_s": 1200.0}
    except Exception as e:
        logger.error(f"Night training failed: {e}")
        return {"step": "night_training", "status": "error", "error": str(e)}


def count_jsonl_lines(path: Path) -> int:
    """Count lines in a JSONL file."""
    if not path.exists():
        return 0
    try:
        with open(path) as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def main() -> int:
    """Run the full pipeline and report results."""
    logger.info(f"Starting night master regeneration pipeline at {datetime.now(UTC)}")

    RESULTS.mkdir(parents=True, exist_ok=True)

    results = {
        "started_at": datetime.now(UTC).isoformat(),
        "phases": [],
    }

    # Phase 1: Generate
    phase1 = run_master_math_generation()
    results["phases"].append(phase1)
    if phase1.get("status") != "completed":
        logger.error("Phase 1 (master math generation) failed; stopping pipeline")
        results["outcome"] = "BLOCKED_AT_GENERATION"
        save_results(results)
        return 1

    # Phase 2: Harvest
    phase2 = harvest_episodes()
    results["phases"].append(phase2)
    if phase2.get("status") != "completed":
        logger.warning("Phase 2 (harvest) failed; attempting training anyway")

    # Phase 3: Train
    phase3 = run_night_training()
    results["phases"].append(phase3)

    results["completed_at"] = datetime.now(UTC).isoformat()
    results["outcome"] = (
        "SUCCESS"
        if all(p.get("status") == "completed" for p in results["phases"])
        else "PARTIAL_SUCCESS"
    )

    save_results(results)
    logger.info(f"Pipeline outcome: {results['outcome']}")
    return 0 if results["outcome"] == "SUCCESS" else 1


def save_results(results: dict[str, Any]) -> None:
    """Save results to disk for review."""
    results_file = RESULTS / f"night_regen_{datetime.now(UTC).isoformat()}.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {results_file}")


if __name__ == "__main__":
    sys.exit(main())
