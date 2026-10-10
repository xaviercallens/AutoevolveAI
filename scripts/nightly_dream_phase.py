#!/usr/bin/env python3
"""
Nightly Dream Phase: Hippocampus Replay, Laya LoRA/RLCD Fine-Tuning & Latent MCTS.

This script should be scheduled via cron (e.g. at 2 AM or before 5 AM every night) to:
1. Trigger the REM Sleep cycle in HippocampalReplayEngine to consolidate episodic memories.
2. Fine-tune the Laya System 1 model on those traces via LoRA adapters,
   improving the model's triage classification using RLCD (RCFL) optimization.
3. Execute Latent MCTS thought trajectory exploration and GRPO advantage optimization.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

# Add project root to PYTHONPATH
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, "/mnt/disks/disk-socrateai-local-1/gpu_lease")

from gpu_lease import gpu_lease  # noqa: E402

from anse.autopoiesis.dream_lora_trainer import LayaDreamLoRATrainer  # noqa: E402
from anse.core.latent_dreamer import (  # noqa: E402
    DEFAULT_JEPA_CHECKPOINT,
    FastJEPALatentPredictor,
    HippocampalReplayEngine,
    LatentDreamer,
)
from anse.infrastructure.agent_environment import resolve_capability_profile  # noqa: E402

# Same holder as scripts/nightly_retrain_at_5am.py, which launches this script while holding
# the lease: gpu_lease re-enters only for an identical holder string.
LEASE_HOLDER = "autoevolve-nightly"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("nightly_dream_phase")


def run_dream_phase() -> dict[str, Any]:
    t0 = time.time()
    logger.info("🌙 Initiating Nightly Dream Phase...")

    profile = resolve_capability_profile()
    logger.info(
        f"🖥️ Hardware capability profile detected: {profile.profile_id} "
        f"(device={profile.device}, RAM={profile.memory.ram_gb}GB)"
    )

    # 1. Hippocampal Replay (REM Sleep Memory Consolidation)
    with gpu_lease(LEASE_HOLDER, "nightly dream: JEPA replay + Laya LoRA + latent MCTS", ttl_s=7200, timeout_s=3600):
        logger.info("🧠 Initializing Hippocampal Replay Engine with JEPA World Model Predictor...")
        predictor = FastJEPALatentPredictor()
        predictor.load_checkpoint(DEFAULT_JEPA_CHECKPOINT)
        predictor.to(profile.device)

        hippocampus = HippocampalReplayEngine(predictor=predictor)

        # Replay only real wake traces. The hand-written seed episodes that used to be logged
        # here carried invented energies (one was 1_000_000.0) and were removed: they made the
        # retention figure measure a fiction. With no real traces the sleep cycle reports NO_TRACES.
        # Replay batch size should leave ample held-out traces to measure retention
        with open(hippocampus.memory_file, encoding="utf-8") as f:
            total_traces = sum(1 for line in f if line.strip())
        sleep_batch_size = max(4, min(8, total_traces // 3))

        sleep_res = hippocampus.execute_sleep_cycle(batch_size=sleep_batch_size)
        logger.info(
            f"💤 Hippocampal REM Sleep status: {sleep_res.get('status')} | "
            f"Consolidated traces: {sleep_res.get('consolidated_traces')} | "
            f"Retention score: {sleep_res.get('retention_score')} | "
            f"Average replay energy: {sleep_res.get('average_replay_energy')}"
        )

        # Extract traces from the hippocampus memory file for training
        traces = []
        if hippocampus.memory_file.exists():
            with open(hippocampus.memory_file, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            traces.append(json.loads(line))
                        except Exception:
                            pass

        # 2. Laya System 1 LoRA + RCFL/RLCD Fine-Tuning
        logger.info("⚡ Initializing Laya System 1 LoRA Trainer...")
        trainer = LayaDreamLoRATrainer(device=profile.device)

        max_traces = 16 if profile.device == "cpu" else 500
        batch_size = 2 if profile.device == "cpu" else 8
        epochs = 1 if profile.device == "cpu" else 3
        seq_len = 64 if profile.device == "cpu" else 256

        logger.info(
            f"🔄 Running LoRA + RLCD fine-tuning (traces={len(traces)}, max_traces={max_traces}, "
            f"batch_size={batch_size}, epochs={epochs}, seq_len={seq_len})..."
        )
        train_res = trainer.train_on_traces(
            traces=traces,
            epochs=epochs,
            batch_size=batch_size,
            seq_len=seq_len,
            max_traces=max_traces,
            save_adapter=True,
        )
        logger.info(
            f"🎯 Laya LoRA training complete: Loss={train_res['avg_loss']:.4f}, "
            f"Duration={train_res['duration_sec']:.2f}s, Adapters Saved={train_res['adapter_saved']}"
        )

        # 3. Latent MCTS Thought Evolution & GRPO Advantage Optimization
        logger.info("🌲 Executing Latent MCTS Multi-Trajectory Dream Search...")
        branching_factor = 16 if profile.device == "cpu" else 32
        dreamer = LatentDreamer(checkpoint_path=DEFAULT_JEPA_CHECKPOINT, num_branches=branching_factor)
        mcts_res = dreamer.dream_and_search(
            prompt="Verify Hamiltonian conservation and discrete exterior calculus Hodge duality",
            seed_code_candidates=[
                "symplectic_integrator_step(q, p, dt)",
                "hodge_star_duality_operator(omega_k)",
                "banach_fixed_point_contraction(T, x)",
                "wilson_loop_plaquette_trace(U_mu)",
            ],
            sandbox_baseline_ms=120.0,
        )
        logger.info(
            f"✨ Latent MCTS explored {mcts_res.num_candidates} thoughts in {mcts_res.latency_ms:.2f}ms "
            f"(Speedup: {mcts_res.speedup_vs_sandbox}x vs sandbox)"
        )
        logger.info(
            f"🏆 Best Thought Advantage: {mcts_res.best_thought.group_advantage:+.4f}, "
            f"Predicted Energy: {mcts_res.best_thought.predicted_energy:.4f}"
        )

    total_duration = time.time() - t0
    report = {
        "status": "SUCCESS",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_duration_sec": round(total_duration, 2),
        "profile": {
            "profile_id": profile.profile_id,
            "device": profile.device,
            "ram_gb": profile.memory.ram_gb,
        },
        "sleep_consolidation": sleep_res,
        "laya_lora_training": train_res,
        "latent_mcts": {
            "num_candidates": mcts_res.num_candidates,
            "latency_ms": mcts_res.latency_ms,
            "speedup_vs_sandbox": mcts_res.speedup_vs_sandbox,
            "group_mean_energy": mcts_res.group_mean_energy,
            "group_std_energy": mcts_res.group_std_energy,
            "best_advantage": mcts_res.best_thought.group_advantage,
            "best_predicted_energy": mcts_res.best_thought.predicted_energy,
        },
    }

    report_dir = project_root / "results" / "nightly_training"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "nightly_dream_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"✅ Nightly Dream Phase successfully concluded in {total_duration:.2f}s!")
    logger.info(f"📄 Report written to {report_path}")
    return report


if __name__ == "__main__":
    run_dream_phase()
