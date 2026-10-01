"""
anse/laya/model.py
==================
LayaCodingCompanion — Non-autoregressive multi-task coding dispatcher.

Architecture:
  Base: answerdotai/ModernBERT-base (149M parameters, FROZEN during LoRA training)
  Adapters: LoRA rank=8, alpha=16 on {query, value} projections (~540k trainable)
  Heads: NoulHead + ChoiceHead + ScoreHead (each ~768-6k params)
  Total trainable: ~550k (well under 50k head params + LoRA)

Performance target: <50ms CPU inference on ModernBERT-base [CLS] pooling.

Output: LayaDecision dataclass with noul, choice, score, and latency_ms.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn

from anse.laya.heads import ChoiceHead, NoulHead, ScoreHead, QualityGateHead

# ── Default model name (can be overridden in training) ────────────────────────
DEFAULT_BASE_MODEL = "answerdotai/ModernBERT-base"

# ── Default class registries (extended by each training stage) ─────────────────
DEFAULT_CHOICE_CLASSES = [
    # Anti-stub / security (Stage 1)
    "clean", "stub_ellipsis", "dead_code", "smelly", "vulnerable",
    "safe", "pass", "fail",
    # Energy / optimization (Stage 2)
    "O(1)", "O(logN)", "O(N)", "O(NlogN)", "O(N2)", "O(exponential)",
    "vectorization", "zero_alloc", "algorithmic_pruning", "data_structure",
    "general", "high_energy", "low_energy",
    # Lean 4 tactics (Stage 3)
    "omega", "linarith", "ring", "norm_num", "positivity",
    "rfl", "simp", "calc", "induction", "intro", "apply",
    "exact", "constructor", "cases", "rcases", "valid", "invalid",
    # Role routing (Stage 3)
    "algorithmic_performance", "computational_physicist", "lean_prover",
    "micro_ml_architect", "security_auditor", "refactoring_specialist",
    # Execution state (Stage 3)
    "normal_return", "exception",
]


@dataclass
class LayaDecision:
    """Output of a single Laya inference pass."""
    noul: float          # ∈ [0,1]: gate probability (1=pass, 0=block)
    choice: str          # predicted role/tactic/category
    choice_probs: dict[str, float]  # top-5 class probabilities
    score: float         # energy/cost estimate ∈ [0, ∞)
    latency_ms: float = 0.0  # end-to-end CPU inference time in ms
    gate_score: float = 1.0  # AR-H4 quality gate score
    barrier_penalty: float = field(default=0.0)  # E=1e6 if noul < 0.3

    def is_blocked(self, threshold: float = 0.3) -> bool:
        """Returns True if noul gate blocks this code (stub/vuln/fail)."""
        return self.noul < threshold

    def anse_energy(self, w_t: float = 1.0, w_m: float = 0.01) -> float:
        """Physical ANSE energy: E = w_t * score + barrier_penalty."""
        return w_t * self.score + self.barrier_penalty


class LayaCodingCompanion(nn.Module):
    """
    Non-autoregressive Laya Coding Companion.

    ModernBERT-base [CLS] pooling + multi-task heads.
    Uses LoRA adapters for parameter-efficient fine-tuning.
    Total trainable params during LoRA training: ~550k (rank=8 on q+v).

    Invariant I2 (from LayaDecision.lean): LoRA params ≤ 600,000 ✅
    """

    def __init__(
        self,
        base_model_name: str = DEFAULT_BASE_MODEL,
        choice_classes: list[str] | None = None,
        lora_rank: int = 8,
        lora_alpha: int = 16,
        dropout: float = 0.1,
        load_pretrained: bool = True,
    ) -> None:
        super().__init__()
        self.base_model_name = base_model_name
        self.lora_rank = lora_rank
        self.lora_alpha = lora_alpha
        self.choice_classes = choice_classes or DEFAULT_CHOICE_CLASSES

        # ── Base encoder (ModernBERT-base or fallback to BERT) ────────────────
        if load_pretrained:
            self.encoder = self._load_encoder(base_model_name)
        else:
            # Lightweight stub for testing (no network call)
            self.encoder = None

        hidden_size = 768  # ModernBERT-base / BERT-base hidden dim

        # ── Task heads ─────────────────────────────────────────────────────────
        self.noul_head = NoulHead(hidden_size=hidden_size, dropout=dropout)
        self.choice_head = ChoiceHead(
            hidden_size=hidden_size,
            num_classes=len(self.choice_classes),
            dropout=dropout,
            class_names=self.choice_classes,
        )
        self.score_head = ScoreHead(hidden_size=hidden_size, dropout=dropout)
        self.quality_gate_head = QualityGateHead(hidden_dim=hidden_size)

    def _load_encoder(self, model_name: str) -> Any:
        """Load ModernBERT-base encoder with fallback to bert-base-uncased."""
        from transformers import AutoModel  # type: ignore
        try:
            print(f"  Loading encoder: {model_name}...")
            return AutoModel.from_pretrained(
                model_name,
                trust_remote_code=True,
                cache_dir="/mnt/data/home/xavkal/.cache/huggingface",
            )
        except Exception as e:
            fallback = "bert-base-uncased"
            print(f"  ⚠️  {model_name} failed ({e}), falling back to {fallback}")
            return AutoModel.from_pretrained(
                fallback,
                cache_dir="/mnt/data/home/xavkal/.cache/huggingface",
            )

    def apply_lora(self) -> None:
        """Apply LoRA adapters to {query, value} projections via PEFT."""
        from peft import LoraConfig, TaskType, get_peft_model  # type: ignore

        if self.encoder is None:
            raise RuntimeError("Encoder not loaded — cannot apply LoRA")

        # ModernBERT uses different module names than BERT
        # Try ModernBERT names first, fall back to BERT-style
        try:
            target_modules = ["Wqkv"]  # ModernBERT fused QKV
            lora_config = LoraConfig(
                r=self.lora_rank,
                lora_alpha=self.lora_alpha,
                lora_dropout=0.05,
                bias="none",
                task_type=TaskType.FEATURE_EXTRACTION,
                target_modules=target_modules,
            )
            self.encoder = get_peft_model(self.encoder, lora_config)
        except Exception:
            # BERT fallback: separate Q and V
            target_modules = ["query", "value"]
            lora_config = LoraConfig(
                r=self.lora_rank,
                lora_alpha=self.lora_alpha,
                lora_dropout=0.05,
                bias="none",
                task_type=TaskType.FEATURE_EXTRACTION,
                target_modules=target_modules,
            )
            self.encoder = get_peft_model(self.encoder, lora_config)

        # Freeze all non-LoRA encoder params
        for name, param in self.encoder.named_parameters():
            if "lora_" not in name:
                param.requires_grad = False

        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        print(f"  LoRA applied. Trainable params: {trainable:,} (target: <600,000)")

    def _get_cls_embedding(
        self, input_ids: torch.Tensor, attention_mask: torch.Tensor
    ) -> torch.Tensor:
        """Extract [CLS] token embedding from encoder output."""
        if self.encoder is None:
            # Testing mode: return random embedding
            batch_size = input_ids.shape[0]
            return torch.randn(batch_size, 768)

        with torch.no_grad() if not self.training else torch.enable_grad():
            outputs = self.encoder(
                input_ids=input_ids,
                attention_mask=attention_mask,
            )
        # [CLS] token is always position 0
        return outputs.last_hidden_state[:, 0, :]  # (B, 768)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass.

        Returns:
            noul_logit: (B,) ∈ [0,1] — gate probability
            choice_logits: (B, K) — routing logits
            score_output: (B,) ∈ [0,∞) — energy estimate
            gate_score: (B,) ∈ [0,1] — quality gate score
        """
        cls_embedding = self._get_cls_embedding(input_ids, attention_mask)
        noul = self.noul_head(cls_embedding)
        choice = self.choice_head(cls_embedding)
        score = self.score_head(cls_embedding)
        gate = self.quality_gate_head(cls_embedding)
        return noul, choice, score, gate

    def predict(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> LayaDecision:
        """Single-sample inference with timing measurement."""
        self.eval()
        t0 = time.perf_counter()

        with torch.no_grad():
            noul_prob, choice_logits, score_val, gate_score_val = self.forward(input_ids, attention_mask)

        latency_ms = (time.perf_counter() - t0) * 1000

        # Decode choice
        import torch.nn.functional as F
        probs = F.softmax(choice_logits[0], dim=-1)
        top5_idx = probs.topk(min(5, len(self.choice_classes))).indices.tolist()
        choice_probs = {self.choice_classes[i]: float(probs[i]) for i in top5_idx}
        best_choice = self.choice_classes[probs.argmax().item()]

        noul_val = float(noul_prob[0])
        score_value = float(score_val[0])
        # Apply barrier penalty if gate blocks
        barrier = 1e6 if noul_val < 0.3 else 0.0

        return LayaDecision(
            noul=noul_val,
            choice=best_choice,
            choice_probs=choice_probs,
            score=score_value,
            gate_score=float(gate_score_val[0]),
            latency_ms=latency_ms,
            barrier_penalty=barrier,
        )

    def save_checkpoint(self, path: Path) -> None:
        """Save model state dict and config to directory."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        torch.save(self.state_dict(), path / "laya_heads.pt")
        config = {
            "base_model_name": self.base_model_name,
            "choice_classes": self.choice_classes,
            "lora_rank": self.lora_rank,
            "lora_alpha": self.lora_alpha,
        }
        (path / "laya_config.json").write_text(__import__("json").dumps(config, indent=2))
        if self.encoder and hasattr(self.encoder, "save_pretrained"):
            self.encoder.save_pretrained(str(path / "encoder_lora"))
        print(f"  Checkpoint saved → {path}")

    @classmethod
    def load_checkpoint(cls, path: Path) -> "LayaCodingCompanion":
        """Load model from checkpoint directory."""
        import json
        path = Path(path)
        config = json.loads((path / "laya_config.json").read_text())
        model = cls(
            base_model_name=config["base_model_name"],
            choice_classes=config["choice_classes"],
            lora_rank=config["lora_rank"],
            lora_alpha=config["lora_alpha"],
            load_pretrained=False,
        )
        # Load encoder with LoRA
        from transformers import AutoModel  # type: ignore
        from peft import PeftModel  # type: ignore
        base = AutoModel.from_pretrained(
            config["base_model_name"],
            trust_remote_code=True,
            cache_dir="/mnt/data/home/xavkal/.cache/huggingface",
        )
        model.encoder = PeftModel.from_pretrained(base, str(path / "encoder_lora"))
        # Load head weights
        heads_state = torch.load(path / "laya_heads.pt", map_location="cpu")
        # Filter to only head params (skip encoder keys)
        head_keys = {k for k in heads_state if k.startswith(("noul_head", "choice_head", "score_head", "quality_gate_head"))}
        model.load_state_dict({k: heads_state[k] for k in head_keys}, strict=False)
        return model
