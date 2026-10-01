"""
modeling_laya.py
================
Standalone implementation of LayaCodingCompanion for Hugging Face Hub.
Provides single-pass non-autoregressive inference across 4 task heads:
  - noul: Binary pass/block gate
  - choice: 46-class specialist router
  - score: Physical energy regression
  - gate: AR-H4 token quality pre-filter
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from peft import PeftModel
from transformers import AutoModel, AutoTokenizer


@dataclass
class LayaDecision:
    noul: float
    choice: str
    choice_probs: Dict[str, float] = field(default_factory=dict)
    score: float = 0.0
    gate_score: float = 0.5
    latency_ms: float = 0.0
    barrier_penalty: float = 0.0

    @property
    def passed(self) -> bool:
        return self.noul >= 0.3

    @property
    def blocked(self) -> bool:
        return not self.passed

    @property
    def total_energy(self) -> float:
        return self.score + self.barrier_penalty


class NoulHead(nn.Module):
    def __init__(self, hidden_size: int = 768, dropout: float = 0.1) -> None:
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        return self.sigmoid(self.linear(self.dropout(h))).squeeze(-1)


class ChoiceHead(nn.Module):
    def __init__(self, hidden_size: int = 768, num_classes: int = 46, dropout: float = 0.1, class_names: Optional[List[str]] = None) -> None:
        super().__init__()
        self.num_classes = num_classes
        self.class_names = class_names or [str(i) for i in range(num_classes)]
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(hidden_size, num_classes)

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        return self.linear(self.dropout(h))


class ScoreHead(nn.Module):
    def __init__(self, hidden_size: int = 768, dropout: float = 0.1) -> None:
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(hidden_size, 1)
        self.relu = nn.ReLU()

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        return self.relu(self.linear(self.dropout(h))).squeeze(-1)


class QualityGateHead(nn.Module):
    def __init__(self, hidden_dim: int = 768) -> None:
        super().__init__()
        self.linear = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        return self.sigmoid(self.linear(h)).squeeze(-1)


class LayaCodingCompanion(nn.Module):
    def __init__(
        self,
        base_model_name: str = "answerdotai/ModernBERT-base",
        choice_classes: Optional[List[str]] = None,
        lora_rank: int = 8,
        lora_alpha: int = 16,
    ) -> None:
        super().__init__()
        self.base_model_name = base_model_name
        self.lora_rank = lora_rank
        self.lora_alpha = lora_alpha
        self.choice_classes = choice_classes or []

        hidden_size = 768
        self.noul_head = NoulHead(hidden_size=hidden_size)
        self.choice_head = ChoiceHead(hidden_size=hidden_size, num_classes=len(self.choice_classes), class_names=self.choice_classes)
        self.score_head = ScoreHead(hidden_size=hidden_size)
        self.quality_gate_head = QualityGateHead(hidden_dim=hidden_size)
        self.encoder: Optional[nn.Module] = None

    def _get_cls_embedding(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        if hasattr(outputs, "last_hidden_state"):
            return outputs.last_hidden_state[:, 0, :]
        return outputs[0][:, 0, :]

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor):
        cls_emb = self._get_cls_embedding(input_ids, attention_mask)
        noul = self.noul_head(cls_emb)
        choice = self.choice_head(cls_emb)
        score = self.score_head(cls_emb)
        gate = self.quality_gate_head(cls_emb)
        return noul, choice, score, gate

    def predict(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> LayaDecision:
        self.eval()
        t0 = time.perf_counter()
        with torch.no_grad():
            noul, choice_logits, score, gate = self.forward(input_ids, attention_mask)
        latency_ms = (time.perf_counter() - t0) * 1000

        probs = F.softmax(choice_logits[0], dim=-1)
        top5 = probs.topk(min(5, len(self.choice_classes))).indices.tolist()
        choice_probs = {self.choice_classes[i]: float(probs[i]) for i in top5}
        best_choice = self.choice_classes[probs.argmax().item()] if self.choice_classes else "unknown"

        noul_val = float(noul[0])
        barrier = 1e6 if noul_val < 0.3 else 0.0

        return LayaDecision(
            noul=noul_val,
            choice=best_choice,
            choice_probs=choice_probs,
            score=float(score[0]),
            gate_score=float(gate[0]),
            latency_ms=latency_ms,
            barrier_penalty=barrier,
        )

    @classmethod
    def from_pretrained(cls, repo_id_or_path: str) -> "LayaCodingCompanion":
        from huggingface_hub import snapshot_download
        from safetensors.torch import load_file

        path = Path(repo_id_or_path)
        if not path.exists():
            path = Path(snapshot_download(repo_id=repo_id_or_path))

        config = json.loads((path / "laya_config.json").read_text())
        model = cls(
            base_model_name=config.get("base_model_name", "answerdotai/ModernBERT-base"),
            choice_classes=config.get("choice_classes", []),
            lora_rank=config.get("lora_rank", 8),
            lora_alpha=config.get("lora_alpha", 16),
        )

        # Base encoder + LoRA
        base = AutoModel.from_pretrained(model.base_model_name, trust_remote_code=True)
        model.encoder = PeftModel.from_pretrained(base, str(path))

        # Heads
        heads_safetensors = path / "laya_heads.safetensors"
        if heads_safetensors.exists():
            heads_state = load_file(str(heads_safetensors))
        else:
            heads_state = torch.load(path / "laya_heads.pt", map_location="cpu")

        head_keys = {k: heads_state[k] for k in heads_state if k.startswith(("noul_head", "choice_head", "score_head", "quality_gate_head"))}
        model.load_state_dict(head_keys, strict=False)
        return model
"""