#!/usr/bin/env python3
"""
Laya Coding Companion — 3-Stage Training Orchestrator
=====================================================
Orchestrates multi-task training across 10 coding datasets:
  Stage 1: Fast Gating & Anti-Stub (SmellBench, PyCode-Vul, CodeRM-UnitTest)
  Stage 2: Thermodynamic Energy (EffiBench, SWE-Perf, Zenodo-RAPL)
  Stage 3: Lean 4 & System 2 Routing (Lean-Workbook, miniF2F-lean4, Magpie-Qwen, CRUXEval)

Outputs trained checkpoints to /mnt/data/home/xavkal/laya_coding_checkpoints/v2/
and JSON training receipts to results/laya_v2_training/
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch
from transformers import AutoTokenizer

from anse.laya.dataset import LayaCodingDataset
from anse.laya.model import LayaCodingCompanion, DEFAULT_BASE_MODEL
from anse.laya.trainer import LayaTrainer

DATA_ROOT = Path("/mnt/data/home/xavkal/laya_coding_datasets")
RESULTS_DIR = Path("results/laya_v2_training")

STAGE_DATASETS = {
    1: [
        DATA_ROOT / "stage1" / "smell_bench.jsonl",
        DATA_ROOT / "stage1" / "pycode_vul.jsonl",
        DATA_ROOT / "stage1" / "code_rm_unittest.jsonl",
    ],
    2: [
        DATA_ROOT / "stage2" / "effibench.jsonl",
        DATA_ROOT / "stage2" / "swe_perf.jsonl",
        DATA_ROOT / "stage2" / "zenodo_rapl.jsonl",
    ],
    3: [
        DATA_ROOT / "stage3" / "lean_workbook.jsonl",
        DATA_ROOT / "stage3" / "minif2f_lean4.jsonl",
        DATA_ROOT / "stage3" / "magpie_qwen25_20k.jsonl",
        DATA_ROOT / "stage3" / "cruxeval.jsonl",
    ],
}

STAGE_LOSS_WEIGHTS = {
    1: {'noul': 1.0, 'choice': 0.5, 'score': 0.0, 'gate': 0.5},
    2: {'noul': 0.3, 'choice': 0.5, 'score': 1.0, 'gate': 0.3},
    3: {'noul': 0.5, 'choice': 1.0, 'score': 0.3, 'gate': 0.5},
}

STAGE_EPOCHS = {
    1: 5,
    2: 10,
    3: 5,
}

def load_tokenizer(model_name: str = DEFAULT_BASE_MODEL) -> AutoTokenizer:
    """Loads tokenizer with fallback."""
    try:
        return AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            cache_dir="/mnt/data/home/xavkal/.cache/huggingface",
        )
    except Exception:
        return AutoTokenizer.from_pretrained(
            "bert-base-uncased",
            cache_dir="/mnt/data/home/xavkal/.cache/huggingface",
        )


def run_training_stage(
    stage: int,
    model: LayaCodingCompanion,
    tokenizer: AutoTokenizer,
    checkpoint_dir: Path,
    epochs: int | None = None,
    batch_size: int = 16,
    grad_accum: int = 4,
    learning_rate: float = 2e-4,
    max_samples: int | None = None,
) -> dict:
    """Runs a single training stage and returns the receipt."""
    paths = STAGE_DATASETS[stage]
    existing_paths = [p for p in paths if p.exists()]
    if not existing_paths:
        print(f"  ❌ No dataset files found for Stage {stage} in {paths}")
        return {"stage": stage, "status": "NO_DATA", "records": 0}

    print(f"\n=======================================================")
    print(f"Starting Stage {stage} Training...")
    print(f"Dataset files: {[str(p.name) for p in existing_paths]}")
    print(f"=======================================================")

    dataset = LayaCodingDataset(
        jsonl_paths=existing_paths,
        tokenizer=tokenizer,
        choice_classes=model.choice_classes,
        max_length=256,
        max_samples=max_samples,
    )

    if len(dataset) == 0:
        print(f"  ❌ Dataset for Stage {stage} is empty.")
        return {"stage": stage, "status": "EMPTY_DATA", "records": 0}

    if epochs is None:
        epochs = STAGE_EPOCHS[stage]

    trainer = LayaTrainer(
        model=model,
        checkpoint_dir=checkpoint_dir,
        learning_rate=learning_rate,
        batch_size=batch_size,
        accumulation_steps=grad_accum,
        num_epochs=epochs,
        val_split=0.1,
        device="cpu",
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results_json_path = RESULTS_DIR / f"stage{stage}_metrics.json"

    receipt = trainer.train_stage(
        stage=stage,
        dataset=dataset,
        results_json_path=results_json_path,
        loss_weights=STAGE_LOSS_WEIGHTS[stage],
        epochs=epochs,
    )
    
    stage_receipt_file = RESULTS_DIR / f"stage{stage}_receipt.json"
    stage_receipt_file.write_text(json.dumps(receipt, indent=2))
    print(f"Stage {stage} receipt saved to {stage_receipt_file}")

    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Laya Coding Companion across 10 datasets")
    parser.add_argument("--stage", type=int, choices=[1, 2, 3], help="Train specific stage (default: all)")
    parser.add_argument("--epochs", type=int, default=None, help="Epochs per stage (override defaults)")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size (default: 16)")
    parser.add_argument("--grad-accum", type=int, default=4, help="Gradient accumulation steps (default: 4)")
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate (default: 2e-4)")
    
    # Mutually exclusive flags
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--full_scale", action="store_true", help="Run full scale training")
    group.add_argument("--prototype", action="store_true", help="Run prototype training (120 samples)")
    
    parser.add_argument("--checkpoint_dir", type=str, default="/mnt/data/home/xavkal/laya_coding_checkpoints/v2/", help="Checkpoint directory")
    parser.add_argument("--dry-run", action="store_true", help="Validate setup without training")
    args = parser.parse_args()

    max_samples = 120 if args.prototype else None
    checkpoint_dir = Path(args.checkpoint_dir)

    print("=" * 65)
    print("ANSE Laya Coding Companion: 3-Stage Training Orchestration")
    print(f"Mode:            {'Full Scale' if args.full_scale else 'Prototype (120 samples)'}")
    print(f"Checkpoints Dir: {checkpoint_dir}")
    print(f"Datasets Dir:    {DATA_ROOT}")
    print(f"Target Base:     {DEFAULT_BASE_MODEL} (149M ModernBERT)")
    print("=" * 65)

    if args.dry_run:
        print("Dry run requested. Checking datasets existence:")
        for stg, files in STAGE_DATASETS.items():
            print(f"  Stage {stg}:")
            for f in files:
                exists = f.exists()
                size = f.stat().st_size if exists else 0
                print(f"    - {f.name}: {'FOUND (' + str(size) + ' bytes)' if exists else 'MISSING'}")
        return

    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("\n1. Initializing Laya Model and LoRA...")
    tokenizer = load_tokenizer(DEFAULT_BASE_MODEL)
    
    # If running a specific stage > 1, try to load the previous stage's checkpoint
    if args.stage and args.stage > 1:
        prev_stage_dir = checkpoint_dir / f"stage{args.stage - 1}"
        if (prev_stage_dir / "laya_heads.pt").exists():
            print(f"Loading checkpoint from previous stage: {prev_stage_dir}")
            model = LayaCodingCompanion.load_checkpoint(prev_stage_dir)
        else:
            print(f"Warning: Previous stage checkpoint {prev_stage_dir} not found. Starting from scratch.")
            model = LayaCodingCompanion(base_model_name=DEFAULT_BASE_MODEL, load_pretrained=True)
            model.apply_lora()
    else:
        model = LayaCodingCompanion(base_model_name=DEFAULT_BASE_MODEL, load_pretrained=True)
        model.apply_lora()

    stages_to_run = [args.stage] if args.stage else [1, 2, 3]
    all_receipts = {}

    for stg in stages_to_run:
        # Load previous stage's checkpoint if we're not running stage 1
        # In this script, we apply the LoRA, but we must load the head weights if doing sequential
        # Actually the orchestrator script (retrain_laya_full.sh) might run this script per stage.
        # So we'll just train the current stage.
        receipt = run_training_stage(
            stage=stg,
            model=model,
            tokenizer=tokenizer,
            checkpoint_dir=checkpoint_dir,
            epochs=args.epochs,
            batch_size=args.batch_size,
            grad_accum=args.grad_accum,
            learning_rate=args.lr,
            max_samples=max_samples,
        )
        all_receipts[f"stage_{stg}"] = receipt
        
        # We need to make sure we load the weights from the previous stage if doing sequentially in one run
        # Since model is passed along, it preserves weights across stages! 
        # So sequential training within the same script run works.

    summary_file = RESULTS_DIR / "training_summary.json"
    summary_file.write_text(json.dumps(all_receipts, indent=2))
    print(f"\nTraining pipeline completed. Summary written to {summary_file}")


if __name__ == "__main__":
    main()
