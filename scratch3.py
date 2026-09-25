import torch
from transformers import AutoModel, AutoConfig
from peft import LoraConfig, get_peft_model

config = AutoConfig.from_pretrained("answerdotai/ModernBERT-large")
model = AutoModel.from_config(config)

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules="all-linear",
    lora_dropout=0.05,
    bias="none",
    task_type="FEATURE_EXTRACTION"
)

try:
    peft_model = get_peft_model(model, lora_config)
    print("Success!")
    peft_model.print_trainable_parameters()
except Exception as e:
    print("Error:", e)
