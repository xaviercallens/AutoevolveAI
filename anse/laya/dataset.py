"""
anse/laya/dataset.py
====================
Multi-task torch Dataset for Laya Coding Companion training.

Reads preprocessed JSONL files (from download_coding_datasets.py) and
produces batches with optional noul/choice/score supervision signals.

Schema per record:
  text: str
  noul_label: int (0/1)
  choice_label: str
  score_label: float
  has_noul: bool
  has_choice: bool
  has_score: bool
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch
from torch.utils.data import Dataset, Subset

def stratified_split(dataset: Dataset, val_fraction: float = 0.2, seed: int = 42) -> tuple[Dataset, Dataset]:
    import numpy as np
    rng = np.random.default_rng(seed)
    
    labels = [dataset.records[i].get("noul_label", 0) for i in range(len(dataset))]
    pos_idx = [i for i, label in enumerate(labels) if label == 1]
    neg_idx = [i for i, label in enumerate(labels) if label == 0]
    
    rng.shuffle(pos_idx)
    rng.shuffle(neg_idx)
    
    pos_val = int(len(pos_idx) * val_fraction)
    neg_val = int(len(neg_idx) * val_fraction)
    
    val_idx = pos_idx[:pos_val] + neg_idx[:neg_val]
    train_idx = pos_idx[pos_val:] + neg_idx[neg_val:]
    
    return Subset(dataset, train_idx), Subset(dataset, val_idx)

def compute_class_weights(dataset: Dataset) -> torch.Tensor:
    labels = [dataset.records[i].get("noul_label", 0) for i in range(len(dataset))]
    pos = sum(1 for l in labels if l == 1)
    neg = len(labels) - pos
    if pos == 0 or neg == 0:
        return torch.tensor([1.0, 1.0], dtype=torch.float32)
    return torch.tensor([1.0 / neg, 1.0 / pos], dtype=torch.float32)

class LayaCodingDataset(Dataset):
    """
    Multi-task Dataset for Laya LoRA fine-tuning.

    Supports three supervision signals per sample:
      - noul_label (binary): anti-stub / security / test-pass gate
      - choice_label (categorical): role routing / tactic selection
      - score_label (continuous): energy / complexity regression

    Records without a given head signal are masked in loss computation.
    """

    def __init__(
        self,
        jsonl_paths: list[Path],
        tokenizer: Any,
        choice_classes: list[str],
        max_length: int = 256,
        max_samples: int | None = None,
    ) -> None:
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.choice_class_to_idx: dict[str, int] = {
            c: i for i, c in enumerate(choice_classes)
        }
        self.records: list[dict] = []

        for path in jsonl_paths:
            path = Path(path)
            if not path.exists():
                print(f"  ⚠️  Dataset file not found: {path}")
                continue
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            self.records.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

        if max_samples and len(self.records) > max_samples:
            import random
            rng = random.Random(42)
            rng.shuffle(self.records)
            self.records = self.records[:max_samples]

        print(f"  Dataset loaded: {len(self.records)} records from {len(jsonl_paths)} files")

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        rec = self.records[idx]
        text = str(rec.get("text", ""))

        # Tokenize
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        item: dict[str, torch.Tensor] = {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
        }

        # Noul label (binary)
        has_noul = bool(rec.get("has_noul", True))
        noul_raw = rec.get("noul_label", 0)
        item["noul_label"] = torch.tensor(float(noul_raw), dtype=torch.float32)
        item["has_noul"] = torch.tensor(float(has_noul), dtype=torch.float32)

        # Choice label (categorical)
        has_choice = bool(rec.get("has_choice", True))
        choice_str = str(rec.get("choice_label", "clean"))
        # Map to index, fallback to 0 if unknown class
        choice_idx = self.choice_class_to_idx.get(choice_str, 0)
        item["choice_label"] = torch.tensor(choice_idx, dtype=torch.long)
        item["has_choice"] = torch.tensor(float(has_choice), dtype=torch.float32)

        # Score label (continuous)
        has_score = bool(rec.get("has_score", False))
        score_raw = rec.get("score_label", 0.0)
        try:
            score_val = float(score_raw)
        except (ValueError, TypeError):
            score_val = 0.0
        item["score_label"] = torch.tensor(score_val, dtype=torch.float32)
        item["has_score"] = torch.tensor(float(has_score), dtype=torch.float32)

        return item

    @staticmethod
    def collate_fn(batch: list[dict]) -> dict[str, torch.Tensor]:
        """Stack batch items into tensors."""
        keys = batch[0].keys()
        return {k: torch.stack([item[k] for item in batch]) for k in keys}
