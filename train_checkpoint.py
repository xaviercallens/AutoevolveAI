#!/usr/bin/env python3
"""
Lightweight LoRA / QLoRA Checkpoint Generator:
Trains an updated PEFT adapter on freshly harvested delta datasets.
Configured for single-GPU RTX 2080 (8GB VRAM) or cluster execution.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

# Optional ML imports with robust fallbacks
try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    torch = None  # type: ignore[assignment]
    TORCH_AVAILABLE = False

try:
    from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training

    PEFT_AVAILABLE = True
except ImportError:
    LoraConfig = None  # type: ignore[assignment,misc]
    TaskType = None  # type: ignore[assignment,misc]
    get_peft_model = None  # type: ignore[assignment]
    prepare_model_for_kbit_training = None  # type: ignore[assignment]
    PEFT_AVAILABLE = False

try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        TrainingArguments,
    )

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    AutoModelForCausalLM = None  # type: ignore[assignment,misc]
    AutoTokenizer = None  # type: ignore[assignment,misc]
    BitsAndBytesConfig = None  # type: ignore[assignment,misc]
    TrainingArguments = None  # type: ignore[assignment,misc]
    TRANSFORMERS_AVAILABLE = False


try:
    from datasets import load_dataset

    DATASETS_AVAILABLE = True
except ImportError:
    load_dataset = None  # type: ignore[assignment]
    DATASETS_AVAILABLE = False

try:
    from trl import SFTTrainer

    TRL_AVAILABLE = True
except ImportError:
    SFTTrainer = None  # type: ignore[assignment]
    TRL_AVAILABLE = False

BASE_MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"


def get_bnb_quantization_config() -> Any:
    """Builds 4-bit NormalFloat (NF4) BitsAndBytes quantization configuration."""
    if not TRANSFORMERS_AVAILABLE or BitsAndBytesConfig is None or not TORCH_AVAILABLE:
        return None
    try:
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=dtype,
            bnb_4bit_use_double_quant=True,
        )
    except (OSError, RuntimeError):
        return None


def get_lora_config(
    r: int = 16,
    lora_alpha: int = 32,
    lora_dropout: float = 0.05,
) -> Any:
    """Builds LoRA / PEFT configuration targeting Coder projection layers."""
    targets = [
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ]
    if PEFT_AVAILABLE and LoraConfig is not None and TaskType is not None:
        return LoraConfig(
            r=r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
            target_modules=targets,
        )
    return {
        "r": r,
        "lora_alpha": lora_alpha,
        "lora_dropout": lora_dropout,
        "target_modules": targets,
    }


def get_training_arguments(
    output_dir: Path,
    batch_size: int = 2,
    grad_accum: int = 4,
    learning_rate: float = 2e-4,
    num_epochs: int = 1,
) -> Any:
    """Builds Hugging Face TrainingArguments or dictionary fallback."""
    ckpt_dir = output_dir / "checkpoints"
    use_bf16 = TORCH_AVAILABLE and torch.cuda.is_available() and torch.cuda.is_bf16_supported()

    if TRANSFORMERS_AVAILABLE and TrainingArguments is not None:
        return TrainingArguments(
            output_dir=str(ckpt_dir),
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=grad_accum,
            warmup_steps=10,
            learning_rate=learning_rate,
            num_train_epochs=num_epochs,
            bf16=use_bf16,
            fp16=not use_bf16 and TORCH_AVAILABLE,
            logging_steps=5,
            save_strategy="no",
            report_to="none",
        )
    return {
        "output_dir": str(ckpt_dir),
        "per_device_train_batch_size": batch_size,
        "gradient_accumulation_steps": grad_accum,
        "learning_rate": learning_rate,
        "num_train_epochs": num_epochs,
    }


def _execute_dry_run_training(
    dataset_path: Path,
    output_dir: Path,
    base_model_id: str,
) -> Path:
    """Emits mock adapter configuration metadata for dry-runs and unit testing."""
    final_adapter_path = output_dir / "final_adapter"
    final_adapter_path.mkdir(parents=True, exist_ok=True)
    meta = {
        "base_model": base_model_id,
        "dataset": str(dataset_path),
        "lora_rank": 16,
        "lora_alpha": 32,
        "mode": "DRY_RUN",
    }
    (final_adapter_path / "adapter_config.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    print(f"📦 Dry-run adapter exported at: {final_adapter_path}")
    return final_adapter_path


def _prepare_formatted_dataset(
    dataset_path: Path,
    tokenizer: Any,
) -> Any:
    """Loads JSON dataset and maps chat templates."""
    if not DATASETS_AVAILABLE or load_dataset is None:
        return None

    raw_dataset = load_dataset(  # nosec B615
        "json", data_files=str(dataset_path), split="train"
    )

    def format_chat(batch: dict[str, Any]) -> dict[str, Any]:
        texts: list[str] = []
        for msgs in batch["messages"]:
            if hasattr(tokenizer, "apply_chat_template"):
                texts.append(
                    tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)
                )
            else:
                texts.append("\n".join(m.get("content", "") for m in msgs))
        return {"text": texts}

    return raw_dataset.map(format_chat, batched=True)


def run_training_job(
    dataset_path: Path,
    output_dir: Path,
    base_model_id: str = BASE_MODEL_ID,
    dry_run: bool = False,
) -> Path:
    """Trains a new LoRA checkpoint using QLoRA and exports weights."""
    print(f"🚀 Initializing LoRA training on: {dataset_path}")

    can_train_live = (
        not dry_run
        and TORCH_AVAILABLE
        and PEFT_AVAILABLE
        and TRANSFORMERS_AVAILABLE
        and TRL_AVAILABLE
        and DATASETS_AVAILABLE
        and torch.cuda.is_available()
    )
    if not can_train_live:
        return _execute_dry_run_training(dataset_path, output_dir, base_model_id)

    bnb_config = get_bnb_quantization_config()
    tokenizer = AutoTokenizer.from_pretrained(base_model_id, use_fast=True)  # nosec B615
    tokenizer.pad_token = tokenizer.eos_token

    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    model = AutoModelForCausalLM.from_pretrained(  # nosec B615
        base_model_id,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=dtype,
    )

    model = prepare_model_for_kbit_training(model)

    lora_config = get_lora_config()
    model = get_peft_model(model, lora_config)

    formatted_dataset = _prepare_formatted_dataset(dataset_path, tokenizer)
    training_args = get_training_arguments(output_dir)

    trainer = SFTTrainer(
        model=model,
        train_dataset=formatted_dataset,
        dataset_text_field="text",
        max_seq_length=2048,
        tokenizer=tokenizer,
        args=training_args,
    )
    trainer.train()

    final_adapter_path = output_dir / "final_adapter"
    model.save_pretrained(final_adapter_path)
    tokenizer.save_pretrained(final_adapter_path)
    print(f"✅ Adapter saved successfully at: {final_adapter_path}")
    return final_adapter_path


def main() -> None:
    """CLI Entrypoint for checkpoint training."""
    parser = argparse.ArgumentParser(description="Incremental LoRA Checkpoint Trainer")
    parser.add_argument("--dataset", required=True, help="Path to input JSONL dataset")
    parser.add_argument("--output-dir", required=True, help="Output directory for checkpoints")
    parser.add_argument("--model", default=BASE_MODEL_ID, help="Base model identifier")
    parser.add_argument(
        "--dry-run", action="store_true", help="Execute dry-run without GPU training"
    )
    args = parser.parse_args()

    adapter_path = run_training_job(
        dataset_path=Path(args.dataset),
        output_dir=Path(args.output_dir),
        base_model_id=args.model,
        dry_run=args.dry_run,
    )
    print(f"🎯 Output adapter path: {adapter_path}")


__all__ = [
    "BASE_MODEL_ID",
    "get_bnb_quantization_config",
    "get_lora_config",
    "get_training_arguments",
    "run_training_job",
    "main",
]


if __name__ == "__main__":
    main()
