import os
import json
import logging
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOConfig, DPOTrainer
from peft import LoraConfig, get_peft_model, TaskType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATASET_PATH = "results/dpo_scientific_dissemination.jsonl"
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
OUTPUT_DIR = "results/qwen-simpo-reddit-audience"

def main() -> None:
    logger.info("Initializing Night Batch RL (SimPO) on CPU...")
    if not os.path.exists(DATASET_PATH):
        logger.error(f"Dataset {DATASET_PATH} not found.")
        return

    logger.info("Loading DPO dataset...")
    ds = load_dataset("json", data_files=DATASET_PATH, split="train")
    ds = ds.shuffle(seed=42).select(range(20))
    
    logger.info("Loading model and tokenizer for CPU...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, local_files_only=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        device_map="cpu",
        torch_dtype=torch.float32,
        local_files_only=False
    )
    
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )
    
    training_args = DPOConfig(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=5e-5,
        num_train_epochs=1,
        logging_steps=1,
        save_steps=100,
        use_cpu=True,
        max_steps=2,
        report_to="none",
        beta=0.1
    )
    
    logger.info("Initializing DPOTrainer...")
    trainer = DPOTrainer(
        model=model,
        args=training_args,
        train_dataset=ds,
        processing_class=tokenizer,
        peft_config=lora_config
    )
    
    logger.info("Starting night reinforcement learning batch...")
    try:
        trainer.train()
        trainer.save_model(OUTPUT_DIR)
        logger.info("Night batch completed successfully.")
    except Exception as e:
        logger.error(f"RL trace encountered an error: {e}")

if __name__ == "__main__":
    main()
