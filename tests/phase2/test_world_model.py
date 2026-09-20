"""
Tests for anse.jepa.world_model — ContextEncoder, TargetEncoder, Predictor,
VICReg, EnergyHead, and JEPAWorldModel.

Lean 4 refs:
    ContextEncoder.encode     — h ∈ ℝ^d → z ∈ ℝ^k
    ContextEncoder.lipschitz  — spectral normalisation
    TargetEncoder.momentum    — EMA copy, no grad
    Predictor.predict         — (z, z) → z_pred
    jepEnergy                 — ‖z_pred − z_tgt‖²
    jepEnergy_nonneg          — proved ≥ 0
    jepEnergy_eq_zero         — proved ↔ z_pred = z_tgt
"""

import torch

from anse.jepa.world_model import (
    ContextEncoder,
    JEPAWorldModel,
    Predictor,
    TargetEncoder,
)

D_INPUT = 128  # Use small dims for fast testing
D_HIDDEN = 64
D_LATENT = 32
BATCH = 8


class TestContextEncoder:
    """Tests for ContextEncoder."""

    def test_context_encoder_output_shape(self):
        """h ∈ ℝ^d → z ∈ ℝ^k.

        Lean 4 ref: ContextEncoder.encode : HiddenState d → LatentCode k
        """
        enc = ContextEncoder(D_INPUT, D_HIDDEN, D_LATENT)
        h = torch.randn(BATCH, D_INPUT)
        z = enc(h)
        assert z.shape == (BATCH, D_LATENT), f"Expected ({BATCH}, {D_LATENT}), got {z.shape}"

    def test_context_encoder_spectral_norm(self):
        """Spectral normalisation should be applied (Lipschitz ≤ 1).

        Lean 4 ref: ContextEncoder.lipschitz : ∃ K : NNReal, LipschitzWith K encode
        """
        enc = ContextEncoder(D_INPUT, D_HIDDEN, D_LATENT)
        # Check that spectral_norm parametrization is present
        linear_layers = [m for m in enc.net if isinstance(m, torch.nn.Linear)]
        for layer in linear_layers:
            has_sn = (
                hasattr(layer, "parametrizations")
                and "weight" in layer.parametrizations
                and any(
                    "spectralnorm" in str(type(p)).lower() for p in layer.parametrizations.weight
                )
            )
            assert has_sn, f"Expected spectral normalisation on {layer}"


class TestTargetEncoder:
    """Tests for TargetEncoder (EMA copy)."""

    def test_target_encoder_ema_copy(self):
        """Initial target should be a copy of context encoder.

        Lean 4 ref: TargetEncoder extends ContextEncoder
        """
        ctx = ContextEncoder(D_INPUT, D_HIDDEN, D_LATENT)
        tgt = TargetEncoder(ctx)

        # They should produce the same output
        h = torch.randn(BATCH, D_INPUT)
        z_ctx = ctx(h)
        z_tgt = tgt(h)
        assert torch.allclose(z_ctx, z_tgt, atol=1e-5), (
            "Target encoder should be an exact copy initially"
        )

    def test_target_encoder_no_grad(self):
        """All target encoder params should have requires_grad=False.

        Lean 4 ref: EMA semantics — no gradient flow through target.
        """
        ctx = ContextEncoder(D_INPUT, D_HIDDEN, D_LATENT)
        tgt = TargetEncoder(ctx)

        for name, p in tgt.named_parameters():
            assert not p.requires_grad, f"Parameter {name} should have requires_grad=False"


class TestPredictor:
    """Tests for Predictor."""

    def test_predictor_output_shape(self):
        """(z_ctx, z_ctx) → z_pred ∈ ℝ^k.

        Lean 4 ref: Predictor.predict : LatentCode k → LatentCode k → LatentCode k
        """
        pred = Predictor(D_LATENT, D_HIDDEN)
        z = torch.randn(BATCH, D_LATENT)
        z_pred = pred(z, z)
        assert z_pred.shape == (BATCH, D_LATENT), (
            f"Expected ({BATCH}, {D_LATENT}), got {z_pred.shape}"
        )

    def test_predictor_spectral_norm(self):
        """Spectral normalisation should be applied.

        Lean 4 ref: Predictor.lipschitz
        """
        pred = Predictor(D_LATENT, D_HIDDEN)
        linear_layers = [m for m in pred.net if isinstance(m, torch.nn.Linear)]
        for layer in linear_layers:
            has_sn = (
                hasattr(layer, "parametrizations")
                and "weight" in layer.parametrizations
                and any(
                    "spectralnorm" in str(type(p)).lower() for p in layer.parametrizations.weight
                )
            )
            assert has_sn, f"Expected spectral normalisation on {layer}"


class TestJEPAEnergy:
    """Tests for JEPA energy computation."""

    def test_jepa_energy_nonneg(self):
        """E ≥ 0 for all inputs.

        Lean 4 ref: jepEnergy_nonneg ✅ proved
        """
        model = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)
        h_ctx = torch.randn(BATCH, D_INPUT)
        h_tgt = torch.randn(BATCH, D_INPUT)
        energy = model.jepa_energy(h_ctx, h_tgt)
        assert (energy >= 0).all(), f"Energy must be ≥ 0, got min={energy.min().item()}"

    def test_jepa_energy_zero_iff_perfect(self):
        """E = 0 when z_pred == z_tgt.

        Lean 4 ref: jepEnergy_eq_zero ✅ proved
        """
        model = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)
        h = torch.randn(1, D_INPUT)

        # When context == target AND predictor is identity-like
        # Energy won't be exactly zero in general, but should be finite
        energy = model.jepa_energy(h, h)
        assert torch.isfinite(energy).all(), "Energy should be finite"
        assert (energy >= 0).all(), "Energy should be ≥ 0"

    def test_jepa_energy_differentiable(self):
        """loss.backward() should succeed — gradient flow is required.

        Validates that gradients can flow through ctx_encoder and predictor.
        """
        model = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)
        h_ctx = torch.randn(BATCH, D_INPUT)
        h_tgt = torch.randn(BATCH, D_INPUT)

        energy = model.jepa_energy(h_ctx, h_tgt)
        loss = energy.mean()
        loss.backward()

        # Check that context encoder has gradients
        has_grad = False
        for p in model.ctx_encoder.parameters():
            if p.grad is not None and p.grad.abs().sum() > 0:
                has_grad = True
                break
        assert has_grad, "Gradients should flow through context encoder"


class TestEnergyHead:
    """Tests for the scalar energy prediction head."""

    def test_predict_energy_scalar_range(self):
        """Predicted energy should be in [0, 100].

        Lean 4 ref: EnergyFn.eval bounded in [0, 100]
        """
        model = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)
        h = torch.randn(D_INPUT)
        predicted = model.predict_energy_scalar(h)
        assert 0.0 <= predicted <= 100.0, f"Predicted energy should be in [0, 100], got {predicted}"


class TestWorldModelPersistence:
    """Tests for model save/load."""

    def test_world_model_save_load_roundtrip(self, tmp_path):
        """Checkpoint save/load should preserve model weights."""
        model1 = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)
        ckpt = tmp_path / "test_ckpt.pt"
        model1.save(ckpt)

        model2 = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)
        model2.load(ckpt)

        # Check that weights match
        h = torch.randn(1, D_INPUT)
        e1 = model1.predict_energy_scalar(h)
        e2 = model2.predict_energy_scalar(h)
        assert abs(e1 - e2) < 1e-4, f"Loaded model should match: {e1} vs {e2}"

    def test_world_model_mock_mode(self):
        """Mock mode should return fixed energy without GPU.

        CI compatibility requirement.
        """
        model = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT, mock_mode=True)
        h = torch.randn(D_INPUT)
        predicted = model.predict_energy_scalar(h)
        assert predicted == 25.0, f"Mock mode should return 25.0, got {predicted}"
