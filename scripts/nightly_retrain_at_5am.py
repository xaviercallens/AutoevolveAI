#!/usr/bin/env python3
"""
Autonomous Nightly Model Retraining Pipeline (Scheduled after 05:00 AM).

Orchestrates the complete overnight retraining of:
1. Redis Long-Term Memory (LTM) Sync from brain transcripts
2. Qwen2.5-0.5B LoRA Adapter fine-tuning on Redis LTM conversations
3. RL EnergyCriticPolicy multi-disciplinary DPO / reward retraining
4. System 1.5 EB-JEPA World Model closed-loop physics training
5. Autonomous Phase 2 JEPA evolution validation
6. Automated synchronization of updated checkpoints to SocrateAI GCP Data Lake
7. Regeneration of Google Cloud Storage Data Lake Cartography
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("NightlyRetrainer")

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = REPO_ROOT / "results" / "nightly_training"
LOG_DIR.mkdir(parents=True, exist_ok=True)
RUN_LOG = LOG_DIR / "nightly_retrain_5am.log"


def log_both(msg: str) -> None:
    logger.info(msg)
    with RUN_LOG.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now().isoformat()} - {msg}\n")


def run_pipeline_step(name: str, cmd: list[str]) -> dict[str, Any]:
    """Execute a single pipeline command with logging and timing."""
    log_both(f"▶️ Starting step: {name}")
    log_both(f"   Command: {' '.join(cmd)}")
    start = time.time()
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False)
    elapsed = time.time() - start

    if res.returncode == 0:
        log_both(f"✅ Step '{name}' completed successfully in {elapsed:.2f}s")
        success = True
    else:
        log_both(f"❌ Step '{name}' failed with code {res.returncode} in {elapsed:.2f}s")
        log_both(f"   Stderr: {res.stderr[-1000:] if res.stderr else 'None'}")
        success = False

    return {
        "step": name,
        "success": success,
        "returncode": res.returncode,
        "elapsed_sec": round(elapsed, 2),
        "stdout_tail": res.stdout[-500:] if res.stdout else "",
        "stderr_tail": res.stderr[-500:] if res.stderr else "",
    }


def wait_until_target_time(target_hour: int = 5, target_minute: int = 5) -> None:
    """Sleep until the next occurrence of target_hour:target_minute (default 05:05 AM)."""
    now = datetime.datetime.now()
    target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if target <= now:
        # If target has passed today, schedule for tomorrow morning
        target += datetime.timedelta(days=1)

    wait_seconds = (target - now).total_seconds()
    log_both(f"🕒 Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    log_both(f"🎯 Target retraining time: {target.strftime('%Y-%m-%d %H:%M:%S')}")
    log_both(f"⏳ Sleeping for {wait_seconds:.0f} seconds ({wait_seconds/3600:.2f} hours)...")

    # Sleep in chunks to allow responsive logging and health tracking
    while True:
        remaining = (target - datetime.datetime.now()).total_seconds()
        if remaining <= 0:
            break
        sleep_duration = min(remaining, 600)  # log countdown every 10 minutes
        time.sleep(sleep_duration)
        now_check = datetime.datetime.now()
        rem_hours = (target - now_check).total_seconds() / 3600
        if rem_hours > 0:
            log_both(f"⏳ Nightly countdown: {rem_hours:.2f} hours remaining until 05:05 AM retraining.")

    log_both("⏰ Target time reached! Commencing Nightly Model Retraining Pipeline...")


def execute_nightly_retraining() -> dict[str, Any]:
    """Execute all phases of model retraining, database snapshotting, and cloud deployment."""
    pipeline_start = time.time()
    log_both("=" * 80)
    log_both("🌙 ANSE MASTER NIGHTLY RETRAINING & CONTINUAL LEARNING LOOP")
    log_both("=" * 80)

    results: list[dict[str, Any]] = []

    # 1. Sync brain transcripts to Redis LTM
    results.append(
        run_pipeline_step(
            "Redis Long-Term Memory Sync",
            ["uv", "run", "python", "scripts/sync_conversations_to_redis.py"],
        )
    )

    # 2. Retrain Qwen LoRA on Redis LTM conversations
    results.append(
        run_pipeline_step(
            "Qwen LoRA LTM Retraining",
            ["uv", "run", "python", "scripts/execute_local_redis_ltm_lora.py", "--steps", "60", "--max-len", "256"],
        )
    )

    # 3. Retrain RL EnergyCriticPolicy & DPO on multi-domain cases
    results.append(
        run_pipeline_step(
            "Reinforcement Learning Critic Retraining",
            ["uv", "run", "python", "scripts/retrain_multidisciplinary_rl.py"],
        )
    )

    # 4. Retrain JEPA World Model on Physics Systems
    results.append(
        run_pipeline_step(
            "JEPA World Model Continual Learning",
            ["uv", "run", "python", "-m", "anse.physics.advanced_world_models"],
        )
    )

    # 5. Run Autopoietic V2 Validation
    results.append(
        run_pipeline_step(
            "ANSE V2 Autopoietic Engine Validation",
            ["uv", "run", "python", "scripts/run_v2_autopoiesis.py"],
        )
    )

    # 6. Deploy updated checkpoints & databases to GCP Data Lake
    results.append(
        run_pipeline_step(
            "GCP Data Lake Synchronization & Cartography",
            ["uv", "run", "python", "scripts/deploy_models_and_datalake.py"],
        )
    )

    total_elapsed = time.time() - pipeline_start
    all_success = all(r["success"] for r in results)

    summary = {
        "status": "SUCCESS" if all_success else "PARTIAL_FAILURE",
        "timestamp": datetime.datetime.now().isoformat(),
        "total_elapsed_sec": round(total_elapsed, 2),
        "steps": results,
    }

    report_path = LOG_DIR / "nightly_retrain_5am_report.json"
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    log_both("=" * 80)
    log_both(f"🎉 NIGHTLY RETRAINING COMPLETE: Status={summary['status']} in {total_elapsed:.2f}s")
    log_both(f"📄 Report written to {report_path}")
    log_both("=" * 80)

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Nightly Model Retraining Pipeline after 05:00 AM")
    parser.add_argument("--wait", action="store_true", help="Sleep until 05:05 AM before running")
    parser.add_argument("--now", action="store_true", help="Run immediately without waiting")
    parser.add_argument("--hour", type=int, default=5, help="Target hour (default 5)")
    parser.add_argument("--minute", type=int, default=5, help="Target minute (default 5)")
    args = parser.parse_args()

    if args.wait:
        wait_until_target_time(target_hour=args.hour, target_minute=args.minute)
    elif not args.now:
        # Default behavior: if currently before target hour (e.g. 23:00), wait until 05:05 AM
        now = datetime.datetime.now()
        if now.hour != args.hour:
            wait_until_target_time(target_hour=args.hour, target_minute=args.minute)

    summary = execute_nightly_retraining()
    return 0 if summary["status"] == "SUCCESS" else 1


if __name__ == "__main__":
    sys.exit(main())
