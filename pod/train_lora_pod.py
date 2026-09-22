#!/usr/bin/env python3
"""
GPU Pod LoRA Distillation Trainer (SFT / DPO).

Runs on remote cloud GPU instances (RunPod / Lambda Labs) to fine-tune open-weight
models (e.g. Qwen2.5-Coder-7B-Instruct) using demonstrations distilled from Frontier Models
(Claude Opus, Gemini 3.1 Pro) harvested from Redis LTM.
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from trl import DPOTrainer, SFTTrainer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_pod_training(
    mode: str,
    dataset_path: str,
    model_name: str = "Qwen/Qwen2.5-Coder-7B-Instruct",
    output_base: str = "adapters",
    epochs: int = 3,
    batch_size: int = 2,
    gradient_accumulation_steps: int = 4,
    learning_rate: float = 2e-4,
    lora_r: int = 16,
    lora_alpha: int = 32,
) -> Path:
    """Executes high-throughput LoRA fine-tuning on GPU Pod hardware."""
    logger.info("Starting GPU Pod Training in mode '%s' on model '%s'", mode, model_name)
    
    timestamp = int(time.time())
    adapter_dir = Path(output_base) / f"checkpoint_pod_{timestamp}" / "final_adapter"
    adapter_dir.mkdir(parents=True, exist_ok=True)

    # 4-bit Quantization configuration for maximal VRAM efficiency
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    logger.info("Loading base tokenizer and model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=False,
    )
    model = prepare_model_for_kbit_training(model)

    peft_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    logger.info("Loading training dataset from '%s'...", dataset_path)
    dataset = load_dataset("json", data_files=dataset_path, split="train")

    training_args = TrainingArguments(
        output_dir=str(adapter_dir / "checkpoints"),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        learning_rate=learning_rate,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=10,
        save_strategy="no",
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        report_to="none",
    )

    if mode == "sft":
        def formatting_func(batch: dict[str, list[Any]]) -> list[str]:
            formatted: list[str] = []
            for prompt, comp in zip(batch["prompt"], batch["completion"], strict=False):
                text = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n{comp}<|im_end|>"
                formatted.append(text)
            return formatted

        trainer = SFTTrainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
            peft_config=peft_config,
            formatting_func=formatting_func,
        )
    elif mode == "dpo":
        trainer = DPOTrainer(
            model=model,
            ref_model=None,
            args=training_args,
            beta=0.1,
            train_dataset=dataset,
            peft_config=peft_config,
            tokenizer=tokenizer,
        )
    else:
        raise ValueError(f"Unsupported training mode: {mode}")

    logger.info("Executing training loop...")
    trainer.train()

    logger.info("Exporting final PEFT LoRA adapter to '%s'...", adapter_dir)
    trainer.model.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))

    # Write provenance receipt
    receipt = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "mode": mode,
        "base_model": model_name,
        "adapter_path": str(adapter_dir),
        "status": "COMPLETED",
        "dataset": dataset_path,
        "samples_trained": len(dataset),
    }
    with open(adapter_dir / "training_receipt.json", "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)

    logger.info("🎉 Pod LoRA training completed successfully!")
    return adapter_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="GPU Pod LoRA Distillation Trainer")
    parser.add_argument("--mode", choices=["sft", "dpo"], default="sft", help="Training mode")
    parser.add_argument("--dataset", required=True, help="Path to JSONL dataset")
    parser.add_argument("--model_name", default="Qwen/Qwen2.5-Coder-7B-Instruct", help="Base model")
    parser.add_argument("--epochs", type=int, default=3, help="Training epochs")
    parser.add_argument("--batch_size", type=int, default=2, help="Per device batch size")
    args = parser.parse_args()

    run_pod_training(
        mode=args.mode,
        dataset_path=args.dataset,
        model_name=args.model_name,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
