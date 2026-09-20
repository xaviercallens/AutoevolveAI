"""
Tests for VICReg loss in anse.jepa.world_model.

Lean 4 refs:
    vicreg_variance          — hinge loss on per-dim standard deviation
    vicreg_covariance        — off-diagonal covariance penalty
    vicreg_loss_nonneg       — proved ≥ 0
    vicreg_prevents_collapse — if variance loss = 0, all dims have std ≥ γ
"""

import torch

from anse.jepa.world_model import VICRegLoss

D_LATENT = 32
BATCH = 16


class TestVICReg:
    """Tests for VICReg anti-collapse regularisation."""

    def test_vicreg_variance_nonneg(self):
        """L_std ≥ 0.

        Lean 4 ref: vicreg_variance_nonneg ✅ proved
        """
        vicreg = VICRegLoss(std_coeff=25.0, cov_coeff=0.0)
        z = torch.randn(BATCH, D_LATENT)
        loss, metrics = vicreg(z)
        assert metrics["std_loss"] >= 0, f"std_loss must be ≥ 0, got {metrics['std_loss']}"

    def test_vicreg_covariance_nonneg(self):
        """L_cov ≥ 0.

        Lean 4 ref: vicreg_covariance — sum of squared off-diagonal entries ≥ 0
        """
        vicreg = VICRegLoss(std_coeff=0.0, cov_coeff=1.0)
        z = torch.randn(BATCH, D_LATENT)
        loss, metrics = vicreg(z)
        assert metrics["cov_loss"] >= 0, f"cov_loss must be ≥ 0, got {metrics['cov_loss']}"

    def test_vicreg_total_nonneg(self):
        """L_total = w_std * L_std + w_cov * L_cov ≥ 0.

        Lean 4 ref: vicreg_loss_nonneg ✅ proved
        """
        vicreg = VICRegLoss(std_coeff=25.0, cov_coeff=1.0)
        z = torch.randn(BATCH, D_LATENT)
        loss, _ = vicreg(z)
        assert loss.item() >= 0, f"VICReg total loss must be ≥ 0, got {loss.item()}"

    def test_vicreg_collapsed_input_high_loss(self):
        """Constant z (dimensional collapse) → high variance loss.

        Lean 4 ref: vicreg_prevents_collapse — if std_loss = 0, all dims have std ≥ γ
        """
        vicreg = VICRegLoss(std_coeff=25.0, cov_coeff=0.0, std_margin=1.0)

        # All embeddings are the same → zero variance → maximum hinge penalty
        z_collapsed = torch.ones(BATCH, D_LATENT) * 42.0
        loss_collapsed, metrics_collapsed = vicreg(z_collapsed)

        # Diverse embeddings → lower variance loss
        z_diverse = torch.randn(BATCH, D_LATENT) * 5.0
        loss_diverse, metrics_diverse = vicreg(z_diverse)

        assert loss_collapsed.item() > loss_diverse.item(), (
            f"Collapsed loss ({loss_collapsed.item()}) should exceed diverse loss ({loss_diverse.item()})"
        )  # noqa: E501

    def test_vicreg_diverse_input_low_loss(self):
        """Diverse z with high variance → low variance loss.

        When per-dim std ≫ γ, the hinge max(0, γ - σ_j) = 0.
        """
        vicreg = VICRegLoss(std_coeff=25.0, cov_coeff=0.0, std_margin=1.0)

        # High-variance embeddings: std ≈ 10 >> margin 1.0
        z = torch.randn(BATCH, D_LATENT) * 10.0
        _, metrics = vicreg(z)

        assert metrics["std_loss"] < 0.1, (
            f"High-variance input should have near-zero std_loss, got {metrics['std_loss']}"
        )

    def test_vicreg_gradient_flows(self):
        """loss.backward() should update encoder parameters.

        Training requirement: VICReg gradients must flow through the encoder.
        """
        import torch.nn as nn

        encoder = nn.Linear(64, D_LATENT)
        vicreg = VICRegLoss()

        h = torch.randn(BATCH, 64)
        z = encoder(h)
        loss, _ = vicreg(z)
        loss.backward()

        has_grad = any(p.grad is not None and p.grad.abs().sum() > 0 for p in encoder.parameters())
        assert has_grad, "VICReg gradients should flow through the encoder"
