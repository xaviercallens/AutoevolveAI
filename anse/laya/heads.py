"""
anse/laya/heads.py
==================
Multi-task decision heads for Laya Coding Companion.

Architecture (per head):
  NoulHead:   Linear(768, 1) + Sigmoid  → binary gate ∈ [0, 1]
  ChoiceHead: Linear(768, K) + Softmax  → K-class routing distribution
  ScoreHead:  Linear(768, 1) + ReLU     → continuous energy/cost ∈ [0, ∞)

Parameter count per head: ~768 * K ≈ 768-4608 params (negligible vs LoRA)
"""
from __future__ import annotations

import torch
import torch.nn as nn


class NoulHead(nn.Module):
    """Binary gate head: pass(1) / block(0).

    Used for: anti-stub detection, security clearance, unit test pass prediction,
    proof closability (without sorry), code smell presence.
    """

    def __init__(self, hidden_size: int = 768, dropout: float = 0.1) -> None:
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """Args: hidden_states (B, hidden_size). Returns: (B,) ∈ [0,1]."""
        x = self.dropout(hidden_states)
        return self.sigmoid(self.linear(x)).squeeze(-1)


class ChoiceHead(nn.Module):
    """K-class routing head: role / tactic / category dispatcher.

    Used for: ANSE role routing, Lean 4 tactic selection, defect classification,
    CWE category, time complexity class, optimization tactic.
    """

    def __init__(
        self,
        hidden_size: int = 768,
        num_classes: int = 8,
        dropout: float = 0.1,
        class_names: list[str] | None = None,
    ) -> None:
        super().__init__()
        self.num_classes = num_classes
        self.class_names = class_names or [str(i) for i in range(num_classes)]
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(hidden_size, num_classes)

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """Args: hidden_states (B, hidden_size). Returns: (B, K) log-probs."""
        x = self.dropout(hidden_states)
        return self.linear(x)  # raw logits; loss uses CrossEntropyLoss

    def predict(self, hidden_states: torch.Tensor) -> list[str]:
        """Returns predicted class names (post-softmax argmax)."""
        logits = self.forward(hidden_states)
        indices = logits.argmax(dim=-1).tolist()
        if isinstance(indices, int):
            indices = [indices]
        return [self.class_names[i] for i in indices]


class ScoreHead(nn.Module):
    """Continuous energy/cost regression head.

    Used for: ANSE physical energy E = w_t*τ + w_m*M, cyclomatic complexity,
    RAPL Joules, pass-rate prediction, proof completeness distance.
    """

    def __init__(self, hidden_size: int = 768, dropout: float = 0.1) -> None:
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(hidden_size, 1)
        self.relu = nn.ReLU()

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """Args: hidden_states (B, hidden_size). Returns: (B,) ∈ [0, ∞)."""
        x = self.dropout(hidden_states)
        return self.relu(self.linear(x)).squeeze(-1)


class QualityGateHead(nn.Module):
    """AR-H4 NAR pre-filter quality gate.
    
    Predicts per-token quality probability. Tokens with gate < tau
    are masked from training loss (prevents learning from hallucinations).
    Architecture: Linear(hidden_dim, 1) -> Sigmoid
    Bias initialized so sigmoid(bias) ≈ 0.3 (conservative default).
    """
    def __init__(self, hidden_dim: int = 768) -> None:
        super().__init__()
        self.gate = nn.Sequential(
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid(),
        )
        # Initialize bias so sigmoid(bias) ≈ 0.3 → bias = ln(0.3/0.7) ≈ -0.847
        nn.init.constant_(self.gate[-2].bias, -0.847)
    
    def forward(self, cls_embedding: torch.Tensor) -> torch.Tensor:
        return self.gate(cls_embedding).squeeze(-1)
