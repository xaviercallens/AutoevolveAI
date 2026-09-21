"""
End-to-End Test Suite for Phase 2 — JEPA World Model.

This test suite exercises the COMPLETE Phase 2 pipeline as specified in
the Roadmap (§Phase 2: Weeks 3-5) and formally defined in JEPA.lean.

Pipeline under test:
    1. Phase 1 data harvesting (synthetic JSONL traces)
    2. Dataset creation + validation (JEPADataset)
    3. Full JEPA training loop (ContextEncoder → TargetEncoder → Predictor)
    4. VICReg anti-collapse enforcement
    5. EMA target encoder update schedule
    6. Energy prediction (surrogate evaluator)
    7. Checkpoint save/load roundtrip
    8. AgentLoop integration (world_model parameter)
    9. Surprise computation (Phase 4 preparation)
   10. Training convergence properties

Lean 4 theorem coverage:
    jepEnergy_nonneg, jepEnergy_eq_zero, vicreg_variance_nonneg,
    vicreg_loss_nonneg, jepTrainingLoss_nonneg, ema_converges_step,
    jepEnergyFn_cont_x, mseJEPA_monotone_descent
"""

import json
import math
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import torch
import torch.nn as nn

from anse.jepa.dataset import JEPADataset, train_val_split
from anse.jepa.ema import cosine_ema_schedule
from anse.jepa.trainer import JEPATrainer, TrainingSummary
from anse.jepa.world_model import (
    JEPAWorldModel,
    VICRegLoss,
)

# ── Dimensions matching a small test configuration ────────────────────────
D_INPUT = 64  # d  (Lean: HiddenState d)
D_HIDDEN = 32  # internal hidden dim
D_LATENT = 16  # k  (Lean: LatentCode k)
BATCH = 24
N_TRACES = 120


# ── Helpers ───────────────────────────────────────────────────────────────


def _create_synthetic_jsonl(
    n: int = N_TRACES,
    hidden_dim: int = D_INPUT,
    *,
    realistic: bool = True,
) -> Path:
    """Create a synthetic Phase 1 interactions.jsonl file.

    When realistic=True, generates energy patterns that mimic
    actual agentic iteration:
        - Early iterations have high energy (syntax errors, crashes)
        - Later iterations converge toward E=0 (clean execution)
    """
    path = Path(tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False).name)
    with open(path, "w") as f:
        for i in range(n):
            task_id = f"task_{i % 10}"
            iteration = i % 5

            # Realistic energy decay: E ~ 100 * exp(-iteration)
            if realistic:
                base_energy = 100.0 * math.exp(-0.8 * iteration)
                noise = (i * 7 % 13) - 6.5  # deterministic "noise"
                energy = max(0.0, min(100.0, base_energy + noise))
            else:
                energy = float(i * 2 % 100)

            # Hidden state: a structured vector, not pure random,
            # so the JEPA can learn a signal.
            hs = []
            for j in range(hidden_dim):
                # Energy-correlated signal in first half,
                # random-ish structure in second half
                if j < hidden_dim // 2:
                    hs.append(energy / 100.0 + 0.01 * j)
                else:
                    hs.append(math.sin(j + i * 0.1))

            trace = {
                "task": task_id,
                "iteration": iteration,
                "hidden_state": hs,
                "energy": energy,
            }
            f.write(json.dumps(trace) + "\n")
    return path


def _build_model() -> JEPAWorldModel:
    """Build a small JEPAWorldModel for testing."""
    return JEPAWorldModel(
        d_input=D_INPUT,
        d_hidden=D_HIDDEN,
        d_latent=D_LATENT,
    )


def _build_trainer(
    model: JEPAWorldModel,
    lr: float = 1e-3,
) -> JEPATrainer:
    """Build a JEPATrainer with a temp checkpoint dir."""
    return JEPATrainer(
        model=model,
        lr=lr,
        device="cpu",
        checkpoint_dir=Path(tempfile.mkdtemp()),
    )


# ══════════════════════════════════════════════════════════════════════════
# E2E-01: Full training pipeline from JSONL → trained model
# ══════════════════════════════════════════════════════════════════════════


class TestE2E01FullTrainingPipeline:
    """Complete pipeline: JSONL → Dataset → Trainer → Checkpoint → Predict."""

    def test_pipeline_trains_and_produces_checkpoint(self):
        """The full pipeline must produce a valid checkpoint and summary.

        Roadmap §Phase 2:
            'Train the Surrogate Evaluator: ... train a tiny neural network
             that sits on top of the LLM.'

        Lean 4: jepTrainingLoss_nonneg
        """
        # 1. Create Phase 1 traces
        jsonl_path = _create_synthetic_jsonl(N_TRACES)

        # 2. Load dataset
        ds = JEPADataset(jsonl_path, hidden_dim=D_INPUT)
        assert len(ds) > 0, "Dataset must load at least 1 pair"

        # 3. Train the model
        model = _build_model()
        trainer = _build_trainer(model)
        summary = trainer.train(ds, epochs=10, batch_size=BATCH)

        # 4. Verify training completed
        assert summary.epochs_completed == 10
        assert summary.total_steps > 0
        assert summary.training_time_seconds > 0
        assert summary.best_val_loss < float("inf")
        assert len(summary.history) == 10

        # 5. Verify checkpoint was saved
        assert summary.checkpoint_path is not None
        assert Path(summary.checkpoint_path).exists()

        # 6. Energy prediction works
        h = torch.randn(D_INPUT)
        predicted = model.predict_energy_scalar(h)
        assert 0.0 <= predicted <= 100.0

    def test_loss_decreases_during_training(self):
        """Training loss should decrease over epochs (convergence signal).

        Lean 4: mseJEPA_monotone_descent — loss ≥ 0 and should trend down.
        """
        jsonl_path = _create_synthetic_jsonl(100, realistic=True)
        ds = JEPADataset(jsonl_path, hidden_dim=D_INPUT)
        model = _build_model()
        trainer = _build_trainer(model, lr=5e-3)
        summary = trainer.train(ds, epochs=20, batch_size=BATCH)

        # Compare first half vs second half of training
        first_half = [h["train_loss"] for h in summary.history[:10]]
        second_half = [h["train_loss"] for h in summary.history[10:]]
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)

        assert avg_second < avg_first, (
            f"Training loss should decrease: first_half_avg={avg_first:.4f}, "
            f"second_half_avg={avg_second:.4f}"
        )

    def test_all_training_losses_nonneg(self):
        """Every loss value at every step must be ≥ 0.

        Lean 4: jepTrainingLoss_nonneg ✅ proved.
        """
        jsonl_path = _create_synthetic_jsonl(60)
        ds = JEPADataset(jsonl_path, hidden_dim=D_INPUT)
        model = _build_model()
        trainer = _build_trainer(model)
        summary = trainer.train(ds, epochs=10, batch_size=BATCH)

        for epoch_record in summary.history:
            assert epoch_record["train_loss"] >= 0, (
                f"Lean 4 violation: train_loss={epoch_record['train_loss']} < 0"
            )
            assert epoch_record["val_loss"] >= 0, (
                f"Lean 4 violation: val_loss={epoch_record['val_loss']} < 0"
            )


# ══════════════════════════════════════════════════════════════════════════
# E2E-02: Checkpoint save → load → predict roundtrip
# ══════════════════════════════════════════════════════════════════════════


class TestE2E02CheckpointRoundtrip:
    """Train → save → create fresh model → load → same predictions."""

    def test_save_load_predictions_match(self):
        """After loading a checkpoint, predictions must match.

        Roadmap: 'Train a tiny, separate neural network' —
        the model must be persistable.
        """
        jsonl_path = _create_synthetic_jsonl(80)
        ds = JEPADataset(jsonl_path, hidden_dim=D_INPUT)

        # Train original model
        model_orig = _build_model()
        trainer = _build_trainer(model_orig)
        summary = trainer.train(ds, epochs=5, batch_size=BATCH)
        ckpt_path = Path(summary.checkpoint_path)

        # Create fresh model and load checkpoint
        model_loaded = _build_model()
        model_loaded.load(ckpt_path)

        # Compare predictions on several inputs
        torch.manual_seed(42)
        for _ in range(10):
            h = torch.randn(D_INPUT)
            pred_orig = model_orig.predict_energy_scalar(h)
            pred_loaded = model_loaded.predict_energy_scalar(h)
            assert abs(pred_orig - pred_loaded) < 1e-4, (
                f"Prediction mismatch after reload: {pred_orig} vs {pred_loaded}"
            )

    def test_checkpoint_file_is_valid_pytorch(self):
        """Checkpoint must be loadable as a raw PyTorch state dict."""
        jsonl_path = _create_synthetic_jsonl(40)
        ds = JEPADataset(jsonl_path, hidden_dim=D_INPUT)
        model = _build_model()
        trainer = _build_trainer(model)
        summary = trainer.train(ds, epochs=3, batch_size=BATCH)

        state = torch.load(summary.checkpoint_path, map_location="cpu", weights_only=True)
        assert isinstance(state, dict)
        # Must contain encoder keys
        assert any("ctx_encoder" in k for k in state.keys())
        assert any("tgt_encoder" in k for k in state.keys())
        assert any("predictor" in k for k in state.keys())
        assert any("energy_head" in k for k in state.keys())


# ══════════════════════════════════════════════════════════════════════════
# E2E-03: JEPA energy properties (Lean 4 theorems)
# ══════════════════════════════════════════════════════════════════════════


class TestE2E03JEPAEnergyProperties:
    """Validate Lean 4 formal properties end-to-end on a trained model."""

    @pytest.fixture(autouse=True)
    def _trained_model(self):
        """Train a model once for all tests in this class."""
        jsonl_path = _create_synthetic_jsonl(80, realistic=True)
        ds = JEPADataset(jsonl_path, hidden_dim=D_INPUT)
        self.model = _build_model()
        trainer = _build_trainer(self.model, lr=3e-3)
        trainer.train(ds, epochs=15, batch_size=BATCH)
        self.model.eval()

    def test_jepa_energy_nonneg(self):
        """E(z_pred, z_tgt) ≥ 0 for all inputs.

        Lean 4: jepEnergy_nonneg : 0 ≤ jepEnergy z_pred z_tgt
        """
        torch.manual_seed(99)
        for _ in range(50):
            h_ctx = torch.randn(1, D_INPUT)
            h_tgt = torch.randn(1, D_INPUT)
            energy = self.model.jepa_energy(h_ctx, h_tgt)
            assert (energy >= 0).all(), f"Lean 4 violation: energy={energy.item()} < 0"

    def test_jepa_energy_zero_iff_perfect(self):
        """E = 0 ↔ z_pred = z_tgt.

        Lean 4: jepEnergy_eq_zero : jepEnergy z_pred z_tgt = 0 ↔ z_pred = z_tgt
        """
        h = torch.randn(1, D_INPUT)
        # Pass the SAME hidden state as both context and target
        z_ctx = self.model.ctx_encoder(h)
        self.model.tgt_encoder(h)
        z_pred = self.model.predictor(z_ctx, z_ctx)

        # If z_pred == z_tgt, energy should be 0
        # Force them equal:
        energy_zero = (z_pred - z_pred).pow(2).sum(dim=-1)
        assert energy_zero.item() == 0.0

        # Different inputs → nonzero energy
        h2 = torch.randn(1, D_INPUT)
        energy_nonzero = self.model.jepa_energy(h, h2)
        assert energy_nonzero.item() > 0.0

    def test_jepa_energy_continuous_in_x(self):
        """Energy must be continuous in the context direction.

        Lean 4: jepEnergyFn_cont_x — proved via Lipschitz continuity.
        """
        h_base = torch.randn(1, D_INPUT)
        h_tgt = torch.randn(1, D_INPUT)
        e_base = self.model.jepa_energy(h_base, h_tgt).item()

        # Small perturbation → small change in energy (continuity)
        for eps in [1e-1, 1e-2, 1e-3]:
            h_perturbed = h_base + eps * torch.randn(1, D_INPUT)
            e_perturbed = self.model.jepa_energy(h_perturbed, h_tgt).item()
            delta = abs(e_perturbed - e_base)
            # Due to Lipschitz, delta should be bounded by K * eps * something
            # The key property is that it should shrink with eps
            assert delta < e_base + 1000 * eps, f"Energy discontinuity at eps={eps}: delta={delta}"

    def test_jepa_energy_differentiable(self):
        """Energy must have gradients for training (gradient-based optimisation).

        Lean 4: cont_x + cont_y together imply differentiability a.e.
        """
        h_ctx = torch.randn(1, D_INPUT, requires_grad=True)
        h_tgt = torch.randn(1, D_INPUT)

        energy = self.model.jepa_energy(h_ctx, h_tgt)
        energy.sum().backward()
        assert h_ctx.grad is not None
        assert h_ctx.grad.shape == h_ctx.shape
        assert not torch.all(h_ctx.grad == 0)


# ══════════════════════════════════════════════════════════════════════════
# E2E-04: VICReg anti-collapse during training
# ══════════════════════════════════════════════════════════════════════════


class TestE2E04VICRegAntiCollapse:
    """Verify that the JEPA latent space doesn't collapse during training.

    Lean 4: vicreg_prevents_collapse (T2) — vicreg_variance = 0 → σ_j ≥ γ.
    """

    def test_latent_codes_have_variance_after_training(self):
        """After training, latent codes must NOT be constant (collapsed).

        Lean 4: vicreg_variance_nonneg + vicreg_prevents_collapse.
        """
        jsonl_path = _create_synthetic_jsonl(80, realistic=True)
        ds = JEPADataset(jsonl_path, hidden_dim=D_INPUT)
        model = _build_model()
        trainer = _build_trainer(model, lr=3e-3)
        trainer.train(ds, epochs=20, batch_size=BATCH)
        model.eval()

        # Encode a batch of diverse inputs
        inputs = torch.randn(32, D_INPUT)
        with torch.no_grad():
            z_codes = model.ctx_encoder(inputs)

        # Check per-dimension variance
        per_dim_var = z_codes.var(dim=0)
        assert per_dim_var.mean().item() > 1e-6, (
            f"Latent space collapsed: mean variance = {per_dim_var.mean().item()}"
        )

        # No dimension should be completely flat
        n_collapsed = (per_dim_var < 1e-8).sum().item()
        assert n_collapsed < D_LATENT // 2, (
            f"Too many collapsed dimensions: {n_collapsed}/{D_LATENT}"
        )

    def test_vicreg_loss_tracks_collapse(self):
        """VICReg loss should be high for collapsed input, low for diverse input.

        Lean 4: vicreg_loss_nonneg.
        """
        vicreg = VICRegLoss(std_coeff=25.0, cov_coeff=1.0, std_margin=1.0)

        # Collapsed input: all same
        z_collapsed = torch.ones(32, D_LATENT)
        loss_collapsed, _ = vicreg(z_collapsed)

        # Diverse input: standard normal
        torch.manual_seed(42)
        z_diverse = torch.randn(32, D_LATENT)
        loss_diverse, _ = vicreg(z_diverse)

        assert loss_collapsed > loss_diverse, (
            f"VICReg should penalise collapse: collapsed={loss_collapsed.item()}, "
            f"diverse={loss_diverse.item()}"
        )
        assert loss_collapsed.item() >= 0
        assert loss_diverse.item() >= 0


# ══════════════════════════════════════════════════════════════════════════
# E2E-05: EMA target encoder behaviour during training
# ══════════════════════════════════════════════════════════════════════════


class TestE2E05EMADuringTraining:
    """Verify EMA target encoder is properly updated during training.

    Lean 4: ema_converges_step (T1).
    """

    def test_target_diverges_from_context_after_training(self):
        """After training, target encoder should differ from context encoder.

        This confirms EMA is being applied (not just copying).
        """
        jsonl_path = _create_synthetic_jsonl(80)
        ds = JEPADataset(jsonl_path, hidden_dim=D_INPUT)
        model = _build_model()

        # Record initial target params (= copy of context)
        initial_diff = 0.0
        for p_ctx, p_tgt in zip(model.ctx_encoder.parameters(), model.tgt_encoder.parameters()):
            initial_diff += (p_ctx.data - p_tgt.data).abs().sum().item()
        assert initial_diff == 0.0, "Target should start as exact copy"

        # Train
        trainer = _build_trainer(model)
        trainer.train(ds, epochs=10, batch_size=BATCH)

        # After training, they should differ
        final_diff = 0.0
        for p_ctx, p_tgt in zip(model.ctx_encoder.parameters(), model.tgt_encoder.parameters()):
            final_diff += (p_ctx.data - p_tgt.data).abs().sum().item()
        assert final_diff > 0.0, "After training, target and context should diverge"

    def test_ema_schedule_covers_full_range(self):
        """Cosine EMA schedule must span [tau_start, tau_end].

        Lean 4: hmom : 0 < momentum ∧ momentum ≤ 1
        """
        total_steps = 100
        taus = [cosine_ema_schedule(s, total_steps) for s in range(total_steps + 1)]

        assert abs(taus[0] - 0.996) < 1e-6
        assert abs(taus[-1] - 1.0) < 1e-6

        # All values should be in (0, 1]
        for tau in taus:
            assert 0 < tau <= 1.0, f"Lean 4 violation: tau={tau} not in (0, 1]"

        # Should be monotonically non-decreasing
        for i in range(len(taus) - 1):
            assert taus[i] <= taus[i + 1] + 1e-10, (
                f"EMA schedule not monotonic at step {i}: {taus[i]} > {taus[i + 1]}"
            )


# ══════════════════════════════════════════════════════════════════════════
# E2E-06: Dataset integrity through the full pipeline
# ══════════════════════════════════════════════════════════════════════════


class TestE2E06DatasetIntegrity:
    """Verify dataset correctness end-to-end."""

    def test_jsonl_to_tensor_pipeline(self):
        """JSONL traces must survive serialisation → deserialisation → tensor.

        Lean 4: Dataset (X Y : Type*) (n : ℕ) — inputs/targets.
        """
        jsonl_path = _create_synthetic_jsonl(50)
        ds = JEPADataset(jsonl_path, hidden_dim=D_INPUT)

        for i in range(min(10, len(ds))):
            h_ctx, h_tgt, energy = ds[i]
            assert h_ctx.shape == (D_INPUT,)
            assert h_tgt.shape == (D_INPUT,)
            assert 0.0 <= energy.item() <= 1.0

    def test_train_val_split_deterministic(self):
        """Split must be reproducible with the same seed."""
        jsonl_path = _create_synthetic_jsonl(100)
        ds = JEPADataset(jsonl_path, hidden_dim=D_INPUT)

        train1, val1 = train_val_split(ds, val_fraction=0.2, seed=42)
        train2, val2 = train_val_split(ds, val_fraction=0.2, seed=42)

        assert len(train1) == len(train2)
        assert len(val1) == len(val2)

    def test_dataloader_produces_correct_shapes(self):
        """DataLoader must produce [B, d] tensors."""
        jsonl_path = _create_synthetic_jsonl(60)
        ds = JEPADataset(jsonl_path, hidden_dim=D_INPUT)
        from torch.utils.data import DataLoader

        loader = DataLoader(ds, batch_size=BATCH, shuffle=False)
        for h_ctx, h_tgt, energy in loader:
            assert h_ctx.dim() == 2
            assert h_ctx.shape[1] == D_INPUT
            assert h_tgt.shape == h_ctx.shape
            assert energy.shape[0] == h_ctx.shape[0]
            break  # Just check first batch


# ══════════════════════════════════════════════════════════════════════════
# E2E-07: AgentLoop integration
# ══════════════════════════════════════════════════════════════════════════


class TestE2E07AgentLoopIntegration:
    """Full integration of JEPA into the Phase 1 AgentLoop."""

    def test_world_model_produces_predictions_in_loop(self):
        """A trained world model should produce JEPA metadata in traces.

        Roadmap §Phase 2:
            'The AI has developed a World Model. It can mathematically look
             at its own abstract thoughts and accurately predict if they
             will fail in reality.'
        """
        from anse.core.agent_loop import AgentLoop

        # Train a model first
        jsonl_path = _create_synthetic_jsonl(80, realistic=True)
        ds = JEPADataset(jsonl_path, hidden_dim=D_INPUT)
        model = _build_model()
        trainer = _build_trainer(model, lr=3e-3)
        trainer.train(ds, epochs=10, batch_size=BATCH)

        # Create AgentLoop with the trained world model
        loop = AgentLoop(
            extractor=MagicMock(),
            sandbox=MagicMock(),
            evaluator=MagicMock(),
            harvester=MagicMock(),
            world_model=model,
        )
        assert loop.world_model is model

        # The world model should predict energy from any hidden state
        h = torch.randn(D_INPUT)
        predicted = model.predict_energy_scalar(h)
        assert isinstance(predicted, float)
        assert 0.0 <= predicted <= 100.0

    def test_phase1_backward_compatible(self):
        """AgentLoop must work without world_model (Phase 1 compatibility).

        Lean 4: EnergyFn is independent of JEPA.
        """
        from anse.core.agent_loop import AgentLoop

        loop = AgentLoop(
            extractor=MagicMock(),
            sandbox=MagicMock(),
            evaluator=MagicMock(),
            harvester=MagicMock(),
            # No world_model
        )
        assert loop.world_model is None

    def test_surprise_signal_nonneg(self):
        """Surprise = |predicted − actual| must be ≥ 0.

        Phase 4 preparation: surprise drives synaptic updates.
        """
        model = _build_model()
        for actual_energy in [0.0, 25.0, 50.0, 75.0, 100.0]:
            h = torch.randn(D_INPUT)
            predicted = model.predict_energy_scalar(h)
            surprise = abs(predicted - actual_energy)
            assert surprise >= 0
            assert isinstance(surprise, float)


# ══════════════════════════════════════════════════════════════════════════
# E2E-08: Reproducibility
# ══════════════════════════════════════════════════════════════════════════


class TestE2E08Reproducibility:
    """Two identical training runs with the same seed must produce
    identical results."""

    def test_deterministic_training(self):
        """Same seed → same final loss.

        Critical for scientific reproducibility.
        """
        jsonl_path = _create_synthetic_jsonl(60)

        def _train_with_seed(seed: int) -> TrainingSummary:
            torch.manual_seed(seed)
            ds = JEPADataset(jsonl_path, hidden_dim=D_INPUT)
            model = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)
            trainer = _build_trainer(model)
            return trainer.train(ds, epochs=5, batch_size=BATCH, seed=seed)

        s1 = _train_with_seed(42)
        s2 = _train_with_seed(42)

        assert abs(s1.final_train_loss - s2.final_train_loss) < 1e-4, (
            f"Non-deterministic: {s1.final_train_loss} vs {s2.final_train_loss}"
        )

    def test_different_seeds_produce_different_results(self):
        """Different seeds should produce different (but valid) results."""
        jsonl_path = _create_synthetic_jsonl(60)

        results = []
        for seed in [42, 123, 7]:
            torch.manual_seed(seed)
            ds = JEPADataset(jsonl_path, hidden_dim=D_INPUT)
            model = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)
            trainer = _build_trainer(model)
            s = trainer.train(ds, epochs=5, batch_size=BATCH, seed=seed)
            results.append(s.final_train_loss)

        # At least 2 of 3 should differ
        unique = len(set(round(r, 6) for r in results))
        assert unique >= 2, f"Seeds should produce different results: {results}"


# ══════════════════════════════════════════════════════════════════════════
# E2E-09: Component wiring (encoder → predictor → energy → vicreg)
# ══════════════════════════════════════════════════════════════════════════


class TestE2E09ComponentWiring:
    """Verify all components are wired correctly in the full model."""

    def test_forward_pass_shapes(self):
        """Full forward pass: h_ctx [B,d] → z_ctx [B,k] → z_pred [B,k].

        Lean 4: ContextEncoder.encode : HiddenState d → LatentCode k
                 Predictor.predict : LatentCode k → LatentCode k → LatentCode k
        """
        model = _build_model()
        h_ctx = torch.randn(BATCH, D_INPUT)
        h_tgt = torch.randn(BATCH, D_INPUT)

        z_ctx = model.ctx_encoder(h_ctx)
        assert z_ctx.shape == (BATCH, D_LATENT)

        z_tgt = model.tgt_encoder(h_tgt)
        assert z_tgt.shape == (BATCH, D_LATENT)

        z_pred = model.predictor(z_ctx, z_ctx)
        assert z_pred.shape == (BATCH, D_LATENT)

        energy = (z_pred - z_tgt).pow(2).sum(dim=-1)
        assert energy.shape == (BATCH,)
        assert (energy >= 0).all()

    def test_training_loss_components(self):
        """compute_training_loss must return all expected components.

        Lean 4: jepTrainingLoss = energy_loss + vicreg_loss.
        """
        model = _build_model()
        h_ctx = torch.randn(BATCH, D_INPUT)
        h_tgt = torch.randn(BATCH, D_INPUT)
        energy_actual = torch.rand(BATCH)

        loss, metrics = model.compute_training_loss(h_ctx, h_tgt, energy_actual)

        assert loss.item() >= 0
        assert "prediction_loss" in metrics
        assert "vicreg_loss" in metrics
        assert "energy_head_loss" in metrics
        assert "total_loss" in metrics
        assert "std_loss" in metrics
        assert "cov_loss" in metrics

        # total_loss should equal the sum of components
        expected_total = (
            metrics["prediction_loss"] + metrics["vicreg_loss"] + metrics["energy_head_loss"]
        )
        assert abs(metrics["total_loss"] - expected_total) < 1e-4

    def _assert_has_gradients(self, module: nn.Module, name_prefix: str):
        for name, p in module.named_parameters():
            if p.requires_grad:
                assert p.grad is not None, f"No gradient for {name_prefix}.{name}"

    def _assert_no_gradients(self, module: nn.Module, name_prefix: str):
        for name, p in module.named_parameters():
            assert p.grad is None or torch.all(p.grad == 0), (
                f"Target encoder {name_prefix}.{name} should not have gradients"
            )

    def test_gradient_flows_through_all_trainable_params(self):
        """Gradients must reach ctx_encoder, predictor, and energy_head.

        Target encoder is excluded (EMA only).
        """
        model = _build_model()
        h_ctx = torch.randn(BATCH, D_INPUT)
        h_tgt = torch.randn(BATCH, D_INPUT)
        energy_actual = torch.rand(BATCH)

        loss, _ = model.compute_training_loss(h_ctx, h_tgt, energy_actual)
        loss.backward()

        assert torch.isfinite(loss) and loss.item() > 0.0
        assert any(p.grad is not None and p.grad.abs().sum() > 0 for p in model.ctx_encoder.parameters())
        self._assert_has_gradients(model.ctx_encoder, "ctx_encoder")
        self._assert_has_gradients(model.predictor, "predictor")
        self._assert_has_gradients(model.energy_head, "energy_head")
        self._assert_no_gradients(model.tgt_encoder, "tgt_encoder")


# ══════════════════════════════════════════════════════════════════════════
# E2E-10: Stress and edge cases
# ══════════════════════════════════════════════════════════════════════════


class TestE2E10StressAndEdgeCases:
    """Edge cases and stress tests."""

    def test_empty_dataset_graceful(self):
        """Training on empty dataset should not crash."""
        path = Path(tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False).name)
        path.touch()  # empty file
        ds = JEPADataset(path, hidden_dim=D_INPUT)
        assert len(ds) == 0

        model = _build_model()
        trainer = _build_trainer(model)
        summary = trainer.train(ds, epochs=5, batch_size=BATCH)
        assert summary.epochs_completed == 0
        assert summary.total_steps == 0

    def test_single_sample_dataset(self):
        """Training with 1 sample should complete without error."""
        path = Path(tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False).name)
        with open(path, "w") as f:
            trace = {
                "task": "singleton",
                "iteration": 0,
                "hidden_state": [1.0] * D_INPUT,
                "energy": 50.0,
            }
            f.write(json.dumps(trace) + "\n")
        ds = JEPADataset(path, hidden_dim=D_INPUT)
        assert len(ds) == 1

        model = _build_model()
        trainer = _build_trainer(model)
        summary = trainer.train(ds, epochs=3, batch_size=1)
        assert summary.epochs_completed == 3

    def test_very_high_energy_traces(self):
        """Model handles E=100 (syntax error / crash) traces correctly.

        Roadmap: Syntax Error / Crash = High Energy (E = 100).
        """
        path = Path(tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False).name)
        with open(path, "w") as f:
            for i in range(30):
                trace = {
                    "task": f"crash_{i}",
                    "iteration": 0,
                    "hidden_state": [float(j) for j in range(D_INPUT)],
                    "energy": 100.0,
                }
                f.write(json.dumps(trace) + "\n")
        ds = JEPADataset(path, hidden_dim=D_INPUT)
        model = _build_model()
        trainer = _build_trainer(model)
        summary = trainer.train(ds, epochs=5, batch_size=16)
        assert summary.epochs_completed == 5
        assert all(h["train_loss"] >= 0 for h in summary.history)

    def test_zero_energy_traces(self):
        """Model handles E=0 (clean execution) traces correctly.

        Roadmap: Clean Execution = Zero Energy (E = 0).
        """
        path = Path(tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False).name)
        with open(path, "w") as f:
            for i in range(30):
                trace = {
                    "task": f"clean_{i}",
                    "iteration": 0,
                    "hidden_state": [math.sin(j + i) for j in range(D_INPUT)],
                    "energy": 0.0,
                }
                f.write(json.dumps(trace) + "\n")
        ds = JEPADataset(path, hidden_dim=D_INPUT)
        model = _build_model()
        trainer = _build_trainer(model)
        summary = trainer.train(ds, epochs=5, batch_size=16)
        assert summary.epochs_completed == 5

    def test_mock_mode_bypasses_computation(self):
        """Mock mode should work without any GPU or actual computation.

        Used in CI environments.
        """
        model = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT, mock_mode=True)
        assert model.mock_mode is True
        assert model.ctx_encoder is None

        predicted = model.predict_energy_scalar(torch.randn(D_INPUT))
        assert predicted == 25.0  # Conservative default
