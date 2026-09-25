import os
import sys
import torch
from transformers import AutoConfig, AutoModel
from pathlib import Path

laya_dir = Path(__file__).resolve().parent / "checkpoints" / "laya"
sys.path.insert(0, str(laya_dir))

cfg_path = laya_dir / "rl_agent_config.json"
import json
with open(cfg_path) as f:
    cfg = json.load(f)

print("Encoder type:", cfg["encoder"])
encoder = AutoModel.from_pretrained(cfg["encoder"])
for name, mod in encoder.named_modules():
    if isinstance(mod, torch.nn.Linear):
        print(name)
        break

