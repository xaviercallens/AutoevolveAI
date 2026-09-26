#!/usr/bin/env python3
"""
Continuous Autonomous LoRA Training & Hot-Reload Daemon.
Periodically queries Redis traces, fine-tunes new adapters, and hot-swaps weights in vLLM.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

import redis

from anse.infrastructure.fabrication import UnverifiedDataError
from harvest_delta import extract_delta_dataset
from train_checkpoint import run_training_job
from vllm_reloader import hot_reload_vllm_adapter

logger = logging.getLogger("anse.daily_trainer_daemon")

CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", 86400))  # 24 Hours
MIN_TRAIN_SAMPLES = int(os.getenv("MIN_TRAIN_SAMPLES", 50))
VLLM_URL = os.getenv("VLLM_URL", "http://localhost:8000")
ADAPTER_ALIAS = os.getenv("ADAPTER_ALIAS", "antigravity-local")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))


def _verify_trained_adapter(adapter_path: Path) -> None:
    """Confirms the adapter directory holds real trained weights, not a dry-run stub."""
    config_path = adapter_path / "adapter_config.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        raise UnverifiedDataError(
            f"Cannot read adapter_config.json at {config_path}: {err}",
            component="daily_trainer_daemon._record_successful_deployment",
            remedy="Ensure run_training_job wrote a valid adapter_config.json before deployment.",
        ) from err

    if config.get("mode") == "DRY_RUN":
        raise UnverifiedDataError(
            f"Adapter at {adapter_path} was produced by a DRY_RUN training job.",
            component="daily_trainer_daemon._record_successful_deployment",
            remedy="Run training with GPU/deps available so it produces real weights, then retry deployment.",
        )

    weights_path = adapter_path / "adapter_model.safetensors"
    if not weights_path.is_file():
        raise UnverifiedDataError(
            f"Adapter at {adapter_path} is missing adapter_model.safetensors.",
            component="daily_trainer_daemon._record_successful_deployment",
            remedy="Do not deploy a checkpoint without trained weights on disk.",
        )


def _record_successful_deployment(
    r: Any,
    cycle_id: int,
    cycle_watermark: float,
    adapter_path: Path,
) -> None:
    """Updates Redis watermark and active adapter metadata atomically.

    Raises UnverifiedDataError if the adapter at adapter_path is a dry-run stub
    or is missing trained weights; a deployment record requires real weights on disk.
    """
    _verify_trained_adapter(adapter_path)

    pipe = r.pipeline()
    pipe.set("antigravity:training:watermark_ts", str(cycle_watermark))
    pipe.set("antigravity:active_lora_version", f"checkpoint_v{cycle_id}")
    pipe.set("antigravity:active_lora_path", str(adapter_path))
    pipe.rpush("antigravity:lora:history", f"v{cycle_id}")
    pipe.execute()
    print(f"🎉 Pipeline Cycle {cycle_id} successfully deployed and watermarked.")


def run_cycle(
    redis_client: Any = None,
    vllm_url: str = VLLM_URL,
    min_samples: int = MIN_TRAIN_SAMPLES,
    adapter_alias: str = ADAPTER_ALIAS,
    dry_run: bool = False,
    http_client: Any = None,
) -> bool:
    """Executes a single end-to-end iteration of the autonomous training and reload loop."""
    r = redis_client or redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    cycle_id = int(time.time())
    print("\n=======================================================")
    print(f"🚀 Starting LoRA Adaptation Cycle: {cycle_id}")
    print("=======================================================")

    has_data, dataset_file, cycle_watermark = extract_delta_dataset(
        min_samples=min_samples,
        redis_client=r,
    )
    if not has_data or not dataset_file:
        print("ℹ️ Cycle completed: Insufficient data. Waiting for next interval.")
        return False

    out_dir = Path(f"./adapters/checkpoint_v{cycle_id}").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        adapter_path = run_training_job(dataset_file, out_dir, dry_run=dry_run)
    except Exception as err:
        print(f"❌ Training failed with exception: {err}")
        return False

    success = hot_reload_vllm_adapter(
        adapter_name=adapter_alias,
        adapter_path=adapter_path,
        vllm_base_url=vllm_url,
        client=http_client,
    )

    if success:
        try:
            _record_successful_deployment(r, cycle_id, cycle_watermark, adapter_path)
        except UnverifiedDataError as err:
            logger.error(
                "Cycle %s produced no trained weights (%s). Watermark NOT advanced.",
                cycle_id,
                err,
            )
            return False
        return True

    print("⚠️ vLLM failed to load weights. Redis watermark preserved for retry.")
    return False


def start_daemon_loop() -> None:
    """Long-running polling loop executing adaptation cycles at configured intervals."""
    print("🤖 Antigravity Autonomous LoRA Background Daemon active.")
    print(f"   Interval: {CHECK_INTERVAL_SECONDS}s | Min Samples: {MIN_TRAIN_SAMPLES}")

    while True:
        try:
            run_cycle()
        except Exception as err:
            print(f"❌ Unexpected cycle failure: {err}")

        print(f"\n💤 Sleeping for {CHECK_INTERVAL_SECONDS} seconds...")
        time.sleep(CHECK_INTERVAL_SECONDS)


def main() -> None:
    """CLI Entrypoint for the autonomous daemon."""
    parser = argparse.ArgumentParser(description="Autonomous LoRA Training & Hot-Reload Daemon")
    parser.add_argument("--once", action="store_true", help="Execute a single cycle and exit")
    parser.add_argument(
        "--dry-run", action="store_true", help="Run in dry-run mode without training"
    )
    parser.add_argument(
        "--min-samples", type=int, default=MIN_TRAIN_SAMPLES, help="Minimum sample count"
    )
    args = parser.parse_args()

    if args.once:
        run_cycle(min_samples=args.min_samples, dry_run=args.dry_run)
    else:
        start_daemon_loop()


__all__ = [
    "run_cycle",
    "start_daemon_loop",
    "main",
]


if __name__ == "__main__":
    main()
