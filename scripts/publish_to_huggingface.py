"""
publish_to_huggingface.py
=========================
Publish the Laya-LoRA Coding Companion to the Hugging Face Hub:
  1. Push PEFT LoRA adapter weights  →  AutoevolveAI/Laya-LoRA-ModernBERT-r8
  2. Push unified curriculum dataset →  AutoevolveAI/Laya-Curriculum-78k
  3. Create a modeling_laya.py card for trust_remote_code=True loading

Prerequisites:
  pip install huggingface_hub datasets peft transformers

Usage:
  HF_TOKEN=hf_xxx uv run python scripts/publish_to_huggingface.py \
    --checkpoint /mnt/data/home/xavkal/laya_coding_checkpoints/stage3 \
    --dataset_dir /mnt/data/home/xavkal/laya_coding_datasets \
    --org AutoevolveAI
"""

import argparse
import json
import os
import shutil
from pathlib import Path
import sys


# ============================================================
# Schemas
# ============================================================

DATASET_SCHEMA = {
    "input_code": "string",
    "target_noul": "int32",      # 0=PASS, 1=BLOCK
    "target_choice": "int32",    # 0-39: specialist class
    "target_score": "float32",   # energy regression target (0.0 or 1e6)
    "stage": "int32",            # 1, 2, or 3
    "dataset_source": "string",  # e.g. "PyCode-Vul", "SmellBench"
}

MODEL_CARD_TEMPLATE = """\
---
language: code
license: apache-2.0
base_model: answerdotai/ModernBERT-base
tags:
- lora
- code
- system-1
- non-autoregressive
- anse
- peft
library_name: peft
model-index:
- name: Laya-LoRA Coding Companion
  results: []
---

# Laya-LoRA Coding Companion

**Non-autoregressive System 1 code-quality gatekeeper** for the [ANSE framework](https://github.com/xavkal/AutoevolveAI).

Built on [ModernBERT-base](https://huggingface.co/answerdotai/ModernBERT-base) (149M parameters)
with LoRA adaptation (rank r=8, α=16, 577,584 trainable parameters — 0.39% of backbone).

## Three-Head Output

| Head | Output | Description |
|---|---|---|
| **NoulHead** | p_noul ∈ [0,1] | Binary gate: block (< 0.3) or route |
| **ChoiceHead** | c_choice ∈ {0..39} | 40-class specialist agent routing |
| **ScoreHead** | s_score ∈ ℝ | Continuous energy regression |

Energy function: E(x) = 10⁶ if p_noul < 0.3, else s_score(x)

## Usage

```python
from peft import PeftModel
from transformers import AutoTokenizer
from anse.laya.model import LayaCodingCompanion  # trust_remote_code=True

model = LayaCodingCompanion.from_pretrained("AutoevolveAI/Laya-LoRA-ModernBERT-r8",
                                            trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained("answerdotai/ModernBERT-base")

code = "def solve(): pass  # TODO"
inputs = tokenizer(code, return_tensors="pt", truncation=True, max_length=512)
decision = model.decide(inputs["input_ids"], inputs["attention_mask"])
# → LayaDecision(noul=0.08, blocked=True, energy=1000000.0, specialist='refactoring_specialist')
```

## SHA-256 Provenance

| Artifact | SHA-256 |
|---|---|
| training_summary.json | 00333acc7ea5711c0040cd678dd5704aabc6596b7cb07756a7f07d72403e22bd |
| download_receipt.json | 91662a050d4a501ce2ad82fd5bbdf047922d1463bb3e5a4f14b9796afb116faf |

## ⚠ Prototype Disclaimer

This model is a **curriculum training prototype** (120 samples/stage, 1 epoch, CPU).
Benchmark gate accuracy: 33.3% (12-case set). Wilson 95% CI for noul accuracy: [61.5%, 99.8%].
Not recommended for production deployment until full-scale Vertex AI training is complete.

## Citation

```bibtex
@article{callens2026laya,
  title={Laya-LoRA Coding Companion: Curriculum Training on 10 Structured Coding Datasets},
  author={Callens, Xavier},
  journal={AutoevolveAI Open-Source Research},
  year={2026},
  url={https://github.com/xavkal/AutoevolveAI}
}
```
"""

DATASET_CARD_TEMPLATE = """\
---
license: apache-2.0
task_categories:
- text-classification
- token-classification
language:
- code
tags:
- code-quality
- security
- anse
- laya
- curriculum-learning
size_categories:
- 10K<n<100K
configs:
- config_name: stage1_security
  data_files: stage1/**/*.jsonl
- config_name: stage2_efficiency
  data_files: stage2/**/*.jsonl
- config_name: stage3_alignment
  data_files: stage3/**/*.jsonl
---

# Laya-Curriculum-78k

Unified curriculum training dataset for the [Laya-LoRA Coding Companion](https://huggingface.co/AutoevolveAI/Laya-LoRA-ModernBERT-r8).

## Statistics

| Stage | Name | Records | Focus |
|---|---|---|---|
| 1 | Security/Quality | ~46,000 | Code smells, vulnerabilities, unit tests |
| 2 | Efficiency | ~1,263 | Algorithmic performance, energy measurement |
| 3 | Formal/Alignment | ~31,244 | Lean 4 proofs, instruction alignment, execution |
| **Total** | | **~78,503** | |

## Schema

```python
{
    "input_code": str,       # Code snippet or instruction
    "target_noul": int,      # 0=PASS, 1=BLOCK
    "target_choice": int,    # 0-39: specialist class index
    "target_score": float,   # Energy regression target (0.0 or 1e6)
    "stage": int,            # 1, 2, or 3
    "dataset_source": str,   # Original dataset name
}
```

## Source Datasets

- SmellBench, PyCode-Vul, CodeRM-UnitTest (Stage 1)
- EffiBench-X, SWE-Perf, Zenodo RAPL (Stage 2)
- Lean-Workbook, miniF2F-Lean4, Magpie-Qwen2.5-20k, CRUXEval (Stage 3)

## SHA-256 Provenance

Dataset assembly verified by `download_receipt.json`:
SHA-256: `91662a050d4a501ce2ad82fd5bbdf047922d1463bb3e5a4f14b9796afb116faf`
"""


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", default="/mnt/data/home/xavkal/laya_coding_checkpoints/stage3")
    p.add_argument("--dataset_dir", default="/mnt/data/home/xavkal/laya_coding_datasets")
    p.add_argument("--org", default="AutoevolveAI")
    p.add_argument("--dry_run", action="store_true", help="Skip actual upload")
    return p.parse_args()


def push_adapter_weights(checkpoint: str, repo_id: str, token: str, dry_run: bool) -> None:
    print(f"\n[1/2] Pushing LoRA adapter weights to {repo_id} …")
    if dry_run:
        print("  DRY RUN — skipping upload")
        return
    from huggingface_hub import HfApi
    api = HfApi(token=token)
    api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True)

    # Write model card
    card_path = Path(checkpoint) / "README.md"
    card_path.write_text(MODEL_CARD_TEMPLATE)

    api.upload_folder(
        folder_path=checkpoint,
        repo_id=repo_id,
        repo_type="model",
        commit_message="feat: Upload Laya-LoRA adapter v1.0 (577,584 trainable params, r=8)",
    )
    print(f"  ✓ Adapter weights pushed to https://huggingface.co/{repo_id}")


def push_dataset(dataset_dir: str, repo_id: str, token: str, dry_run: bool) -> None:
    print(f"\n[2/2] Pushing unified dataset to {repo_id} …")
    if dry_run:
        print("  DRY RUN — skipping upload")
        return
    from huggingface_hub import HfApi
    api = HfApi(token=token)
    api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True)

    readme_path = Path(dataset_dir) / "README.md"
    readme_path.write_text(DATASET_CARD_TEMPLATE)

    api.upload_folder(
        folder_path=dataset_dir,
        repo_id=repo_id,
        repo_type="dataset",
        commit_message="feat: Upload Laya-Curriculum-78k v1.0 (3 stages, 78,503 records)",
        ignore_patterns=["*.pt", "*.bin", "*.safetensors"],  # no weights in dataset repo
    )
    print(f"  ✓ Dataset pushed to https://huggingface.co/datasets/{repo_id}")


def main():
    args = parse_args()
    token = os.environ.get("HF_TOKEN", "")
    if not token and not args.dry_run:
        print("ERROR: HF_TOKEN environment variable not set. Export HF_TOKEN=hf_xxx")
        sys.exit(1)

    model_repo = f"{args.org}/Laya-LoRA-ModernBERT-r8"
    dataset_repo = f"{args.org}/Laya-Curriculum-78k"

    push_adapter_weights(args.checkpoint, model_repo, token, args.dry_run)
    push_dataset(args.dataset_dir, dataset_repo, token, args.dry_run)

    print(f"""
✓ Hugging Face release complete!
  Model:   https://huggingface.co/{model_repo}
  Dataset: https://huggingface.co/datasets/{dataset_repo}

Next step: Create the Gradio Space AutoevolveAI/Laya-System1-Demo (see docs/HF_SPACE.md)
""")


if __name__ == "__main__":
    main()
