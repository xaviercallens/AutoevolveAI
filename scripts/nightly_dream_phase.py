#!/usr/bin/env python3
"""
Nightly Dream Phase: Hippocampus Replay & Laya LoRA/RLCD Fine-Tuning.

This script should be scheduled via cron (e.g. at 2 AM every night) to:
1. Trigger the REM Sleep cycle in HippocampalReplayEngine to consolidate memories.
2. Fine-tune the Laya System 1 model on those traces via LoRA adapters,
   improving the model's triage classification using RLCD (RCFL) optimization.
"""
import sys
import logging
from pathlib import Path

# Add project root to PYTHONPATH
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from anse.core.latent_dreamer import HippocampalReplayEngine
from anse.autopoiesis.dream_lora_trainer import LayaDreamLoRATrainer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("nightly_dream_phase")

def run_dream_phase():
    logger.info("Initiating Nightly Dream Phase...")
    
    # 1. Hippocampal Replay (Consolidation)
    hippocampus = HippocampalReplayEngine()
    sleep_res = hippocampus.execute_sleep_cycle(batch_size=64)
    
    if sleep_res.get("status") in ["NO_TRACES", "EMPTY_MEMORY"]:
        logger.info("No episodic memory traces found. Dream Phase aborting.")
        return
        
    num_traces = sleep_res["consolidated_traces"]
    logger.info(f"Hippocampal REM Sleep consolidated {num_traces} traces.")
    logger.info(f"Domains covered: {sleep_res['domains_covered']}")
    
    # Extract the actual traces from the hippocampus memory file for training
    traces = []
    if hippocampus.memory_file.exists():
        import json
        with open(hippocampus.memory_file, "r") as f:
            for line in f:
                if line.strip():
                    traces.append(json.loads(line))
    
    if not traces:
        return
        
    # Only train on the most recent 500 traces + anchors to avoid overfitting
    # (Simplified for demonstration)
    train_traces = traces[-500:]
    
    # 2. Laya System 1 LoRA + RCFL/RLCD Fine-Tuning
    logger.info("Initializing Laya LoRA Trainer...")
    # Use device="cuda" if available, else "cpu"
    trainer = LayaDreamLoRATrainer()
    
    logger.info("Applying LoRA adapters and running RLCD proper-scoring optimization...")
    train_res = trainer.train_on_traces(traces=train_traces, epochs=3, batch_size=4)
    
    logger.info(f"Dream Phase fully concluded. Laya System 1 updated.")
    logger.info(f"Loss: {train_res['avg_loss']:.4f}, Duration: {train_res['duration_sec']:.2f}s")

if __name__ == "__main__":
    run_dream_phase()
