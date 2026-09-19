"""
JEPA World Model — Context Encoder, Target Encoder, Predictor, VICReg, and
full JEPAWorldModel composition.

Lean 4 refs (JEPA.lean):
    ContextEncoder (d k : ℕ) — encode : HiddenState d → LatentCode k
    TargetEncoder (d k : ℕ)  — extends ContextEncoder with EMA momentum
    Predictor (k : ℕ)        — predict : LatentCode k → LatentCode k → LatentCode k
    jepEnergy                — ‖z_pred − z_tgt‖²
    vicreg_variance          — hinge std loss
    vicreg_covariance        — off-diagonal covariance penalty
    jepTrainingLoss_nonneg   — proved ≥ 0

Reference: vendor/eb_jepa/eb_jepa/jepa.py, vendor/eb_jepa/eb_jepa/losses.py
"""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

from anse.config import JEPAConfig, ModelConfig

logger = logging.getLogger("anse.jepa.world_model")


# ──────────────────────────────────────────────────────────────────────────────
# Context Encoder
# ──────────────────────────────────────────────────────────────────────────────


class ContextEncoder(nn.Module):
    """Projects LLM hidden states to JEPA latent codes.

    Lean 4 ref::

        structure ContextEncoder (d k : ℕ) where
          encode : HiddenState d → LatentCode k
          lipschitz : ∃ K : NNReal, LipschitzWith K encode

    Spectral normalisation on both linear layers enforces the
    Lipschitz condition required by the Lean 4 specification.

    Architecture: Linear(d, hidden) → LayerNorm → GELU → Linear(hidden, k)
    """

    def __init__(self, d_input: int = 4096, d_hidden: int = 1024, d_latent: int = 512):
        super().__init__()
        self.net = nn.Sequential(
            nn.utils.parametrizations.spectral_norm(nn.Linear(d_input, d_hidden)),
            nn.LayerNorm(d_hidden),
            nn.GELU(),
            nn.utils.parametrizations.spectral_norm(nn.Linear(d_hidden, d_latent)),
        )

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        """Encode hidden state h ∈ ℝ^d → latent code z ∈ ℝ^k."""
        return self.net(h)


# ──────────────────────────────────────────────────────────────────────────────
# Target Encoder (EMA copy)
# ──────────────────────────────────────────────────────────────────────────────


class TargetEncoder(nn.Module):
    """EMA copy of the context encoder — no gradients.

    Lean 4 ref::

        structure TargetEncoder (d k : ℕ) extends ContextEncoder d k where
          momentum : ℝ
          hmom : 0 < momentum ∧ momentum ≤ 1

    All parameters have ``requires_grad=False``.
    Updated via ``ema_update(target, context, τ)`` after each training step.
    """

    def __init__(self, context_encoder: ContextEncoder):
        super().__init__()
        self.net = copy.deepcopy(context_encoder.net)
        # Freeze all parameters — EMA-only updates
        for p in self.net.parameters():
            p.requires_grad = False

    @torch.no_grad()
    def forward(self, h: torch.Tensor) -> torch.Tensor:
        """Encode hidden state (no gradient flow)."""
        return self.net(h)


# ──────────────────────────────────────────────────────────────────────────────
# Predictor
# ──────────────────────────────────────────────────────────────────────────────


class Predictor(nn.Module):
    """Maps (z_context, z_context) → z_predicted in latent space.

    Lean 4 ref::

        structure Predictor (k : ℕ) where
          predict : LatentCode k → LatentCode k → LatentCode k
          lipschitz : ∃ K : NNReal, LipschitzWith K ...

    Architecture: Linear(k*2, hidden) → LayerNorm → GELU → Linear(hidden, k)
    """

    def __init__(self, d_latent: int = 512, d_hidden: int = 1024):
        super().__init__()
        self.net = nn.Sequential(
            nn.utils.parametrizations.spectral_norm(nn.Linear(d_latent * 2, d_hidden)),
            nn.LayerNorm(d_hidden),
            nn.GELU(),
            nn.utils.parametrizations.spectral_norm(nn.Linear(d_hidden, d_latent)),
        )

    def forward(self, z_ctx: torch.Tensor, z_ctx2: torch.Tensor) -> torch.Tensor:
        """Predict target latent code from context.

        In the JEPA paradigm, both inputs are from the context encoder.
        The predictor learns to bridge from context to target representation.
        """
        combined = torch.cat([z_ctx, z_ctx2], dim=-1)
        return self.net(combined)


# ──────────────────────────────────────────────────────────────────────────────
# VICReg Loss
# ──────────────────────────────────────────────────────────────────────────────


class VICRegLoss(nn.Module):
    """Variance-Invariance-Covariance Regularisation (VICReg).

    Prevents representation collapse by ensuring:
    1. Each latent dimension has sufficient variance (hinge std loss)
    2. Latent dimensions are decorrelated (off-diagonal covariance penalty)

    Lean 4 refs::

        vicreg_variance  — hinge loss on per-dim standard deviation
        vicreg_covariance — off-diagonal covariance penalty
        vicreg_loss_nonneg — proved ≥ 0

    Reference: vendor/eb_jepa/eb_jepa/losses.py → VCLoss, HingeStdLoss
    """

    def __init__(
        self,
        std_coeff: float = 25.0,
        cov_coeff: float = 1.0,
        std_margin: float = 1.0,
    ):
        super().__init__()
        self.std_coeff = std_coeff
        self.cov_coeff = cov_coeff
        self.std_margin = std_margin

    def forward(self, z: torch.Tensor) -> tuple[torch.Tensor, dict[str, float]]:
        """Compute VICReg loss.

        Args:
            z: Batch of latent codes, shape [B, k].

        Returns:
            (total_loss, {"std_loss": ..., "cov_loss": ...})
        """
        # Variance (hinge std loss)
        # Lean 4: vicreg_variance = (1/k) * Σ_j max(0, γ − σ_j)
        z_centered = z - z.mean(dim=0, keepdim=True)
        std = torch.sqrt(z_centered.var(dim=0) + 1e-4)
        std_loss = torch.mean(F.relu(self.std_margin - std))

        # Covariance
        # Lean 4: vicreg_covariance = (1/k) * Σ_{a≠b} C(a,b)²
        batch_size = z.shape[0]
        cov_matrix = (z_centered.T @ z_centered) / max(batch_size - 1, 1)
        # Zero out diagonal
        diag_mask = torch.eye(cov_matrix.shape[0], device=z.device, dtype=torch.bool)
        off_diag = cov_matrix.masked_fill(diag_mask, 0.0)
        cov_loss = (off_diag ** 2).sum() / z.shape[1]

        total = self.std_coeff * std_loss + self.cov_coeff * cov_loss

        return total, {
            "std_loss": std_loss.item(),
            "cov_loss": cov_loss.item(),
        }


# ──────────────────────────────────────────────────────────────────────────────
# Energy Head (scalar prediction)
# ──────────────────────────────────────────────────────────────────────────────


class EnergyHead(nn.Module):
    """Small MLP that maps a latent code → scalar energy prediction.

    This enables the JEPA to predict sandbox energy scores directly:
        predict_energy(h) → E_predicted ∈ [0, 100]

    Not part of the core JEPA formalism (which operates in latent space),
    but needed for practical integration with AgentLoop.
    """

    def __init__(self, d_latent: int = 512):
        super().__init__()
        self.head = nn.Sequential(
            nn.Linear(d_latent, 128),
            nn.GELU(),
            nn.Linear(128, 1),
            nn.Sigmoid(),  # → [0, 1], then scale to [0, 100]
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        """Predict energy ∈ [0, 1] from latent code z."""
        return self.head(z).squeeze(-1)


# ──────────────────────────────────────────────────────────────────────────────
# Full JEPA World Model
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class JEPAEnergyResult:
    """Result of a JEPA energy computation."""
    latent_energy: float      # ‖z_pred − z_tgt‖² (JEPA latent energy)
    predicted_energy: float   # Scalar energy prediction ∈ [0, 100]
    z_pred: torch.Tensor      # Predicted latent code
    z_tgt: torch.Tensor       # Target latent code


class JEPAWorldModel(nn.Module):
    """Full JEPA World Model composing all components.

    Lean 4 ref::

        jepEnergyFn — combines ctx, tgt, pred into EnergyFn
        jepEnergy = ‖z_pred − z_tgt‖²
        jepEnergy_nonneg — proved ≥ 0
        jepEnergy_eq_zero — proved ↔ z_pred = z_tgt

    This model gives the AI "intuition" — it can predict whether
    a hidden state will produce working code without running the sandbox.
    """

    def __init__(
        self,
        d_input: int = 4096,
        d_hidden: int = 1024,
        d_latent: int = 512,
        mock_mode: bool = False,
    ):
        super().__init__()
        self.d_input = d_input
        self.d_latent = d_latent
        self.mock_mode = mock_mode

        if mock_mode:
            # For CI/testing without GPU
            self.ctx_encoder = None
            self.tgt_encoder = None
            self.predictor = None
            self.energy_head = None
            self.vicreg = None
            return

        self.ctx_encoder = ContextEncoder(d_input, d_hidden, d_latent)
        self.tgt_encoder = TargetEncoder(self.ctx_encoder)
        self.predictor = Predictor(d_latent, d_hidden)
        self.energy_head = EnergyHead(d_latent)
        self.vicreg = VICRegLoss()

    def jepa_energy(
        self, h_context: torch.Tensor, h_target: torch.Tensor
    ) -> torch.Tensor:
        """Compute JEPA energy: ‖z_pred − z_tgt‖².

        Lean 4 ref::

            noncomputable def jepEnergy {k : ℕ}
                (z_pred z_tgt : LatentCode k) : ℝ :=
              ‖z_pred - z_tgt‖ ^ 2

        Args:
            h_context: Context hidden state [B, d].
            h_target: Target hidden state [B, d].

        Returns:
            Scalar energy per sample [B].
        """
        z_ctx = self.ctx_encoder(h_context)
        z_tgt = self.tgt_encoder(h_target)
        z_pred = self.predictor(z_ctx, z_ctx)

        # ‖z_pred − z_tgt‖²  (per-sample)
        energy = (z_pred - z_tgt).pow(2).sum(dim=-1)
        return energy

    @torch.no_grad()
    def predict_energy_scalar(self, h_context: torch.Tensor) -> float:
        """Predict sandbox energy score from a hidden state.

        This is the "intuition" — the whole point of Phase 2.

        Args:
            h_context: Hidden state [1, d] or [d].

        Returns:
            Predicted energy ∈ [0, 100].
        """
        if self.mock_mode:
            return 25.0  # Conservative default for testing

        self.eval()
        if h_context.dim() == 1:
            h_context = h_context.unsqueeze(0)

        z_ctx = self.ctx_encoder(h_context)
        raw = self.energy_head(z_ctx)
        return (raw.item() * 100.0)

    def compute_training_loss(
        self,
        h_context: torch.Tensor,
        h_target: torch.Tensor,
        energy_actual: torch.Tensor,
    ) -> tuple[torch.Tensor, dict[str, float]]:
        """Compute the full JEPA training loss.

        Lean 4 ref: jepTrainingLoss = energy_loss + vicreg_loss
                    jepTrainingLoss_nonneg ✅ proved

        Args:
            h_context: Context hidden states [B, d].
            h_target: Target hidden states [B, d].
            energy_actual: Actual energy scores [B] normalised to [0, 1].

        Returns:
            (total_loss, metrics_dict)
        """
        z_ctx = self.ctx_encoder(h_context)
        z_tgt = self.tgt_encoder(h_target)
        z_pred = self.predictor(z_ctx, z_ctx)

        # JEPA prediction loss: ‖z_pred − z_tgt‖²
        prediction_loss = (z_pred - z_tgt).pow(2).sum(dim=-1).mean()

        # VICReg anti-collapse on predicted embeddings
        vicreg_loss, vicreg_metrics = self.vicreg(z_pred)

        # Energy head MSE loss (predicts actual sandbox energy)
        energy_pred = self.energy_head(z_ctx)
        energy_head_loss = F.mse_loss(energy_pred, energy_actual)

        # Total loss (Lean 4: jepTrainingLoss = prediction_loss + vicreg)
        total_loss = prediction_loss + vicreg_loss + energy_head_loss

        metrics = {
            "prediction_loss": prediction_loss.item(),
            "vicreg_loss": vicreg_loss.item(),
            "energy_head_loss": energy_head_loss.item(),
            "total_loss": total_loss.item(),
            **vicreg_metrics,
        }

        return total_loss, metrics

    def save(self, path: Path | str) -> None:
        """Save model checkpoint."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.state_dict(), path)
        logger.info("JEPA checkpoint saved to %s", path)

    def load(self, path: Path | str) -> None:
        """Load model checkpoint."""
        path = Path(path)
        self.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
        logger.info("JEPA checkpoint loaded from %s", path)

    @classmethod
    def from_config(cls, model_cfg: ModelConfig, jepa_cfg: JEPAConfig, **kwargs) -> JEPAWorldModel:
        """Create JEPAWorldModel from configuration dataclasses."""
        return cls(
            d_input=model_cfg.hidden_dim,
            d_hidden=jepa_cfg.hidden_dim,
            d_latent=jepa_cfg.latent_dim,
            **kwargs,
        )
