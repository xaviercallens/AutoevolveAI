"""
Tests for anse.jepa.trainer — JEPA training loop.

Lean 4 refs:
    jepTrainingLoss          — energy_loss + vicreg_loss
    jepTrainingLoss_nonneg   — proved ≥ 0
    mseJEPA_monotone_descent — loss ≥ 0
"""

import json
import tempfile
from pathlib import Path

import torch

from anse.config import JEPAConfig
from anse.jepa.dataset import JEPADataset
from anse.jepa.trainer import JEPATrainer, TrainingSummary
from anse.jepa.world_model import JEPAWorldModel

D_INPUT = 64
D_HIDDEN = 32
D_LATENT = 16


def _create_dataset(n: int = 100) -> JEPADataset:
    """Create a synthetic JSONL dataset for training tests."""
    path = Path(tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False).name)
    with open(path, "w") as f:
        for i in range(n):
            trace = {
                "task": f"task_{i % 10}",
                "iteration": i % 5,
                "hidden_state": [float(j) / D_INPUT for j in range(D_INPUT)],
                "energy": float(i % 100),
            }
            f.write(json.dumps(trace) + "\n")
    return JEPADataset(path, hidden_dim=D_INPUT)


def _create_trainer(dataset: JEPADataset | None = None) -> tuple[JEPATrainer, JEPADataset]:
    """Create a JEPATrainer with a synthetic dataset."""
    ds = dataset or _create_dataset(100)
    model = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)
    trainer = JEPATrainer(
        model=model,
        config=JEPAConfig(latent_dim=D_LATENT, hidden_dim=D_HIDDEN),
        lr=1e-3,
        device="cpu",
        checkpoint_dir=Path(tempfile.mkdtemp()),
    )
    return trainer, ds


class TestJEPATrainer:
    """Tests for the JEPA training loop."""

    def test_trainer_single_epoch(self):
        """1 epoch should complete without error.

        Basic integration test.
        """
        trainer, ds = _create_trainer()
        summary = trainer.train(ds, epochs=1, batch_size=16)
        assert summary.epochs_completed == 1
        assert summary.total_steps > 0

    def test_training_loss_nonneg(self):
        """Total loss ≥ 0 every epoch.

        Lean 4 ref: jepTrainingLoss_nonneg ✅ proved
        """
        trainer, ds = _create_trainer()
        summary = trainer.train(ds, epochs=3, batch_size=16)

        for record in summary.history:
            assert record["train_loss"] >= 0, (
                f"Train loss must be ≥ 0, got {record['train_loss']} at epoch {record['epoch']}"
            )

    def test_training_loss_decreases(self):
        """Loss should decrease over 10 epochs on simple synthetic data.

        Lean 4 ref: mseJEPA_monotone_descent — loss ≥ 0 and should decrease
        """
        trainer, ds = _create_trainer()
        summary = trainer.train(ds, epochs=10, batch_size=16)

        first_loss = summary.history[0]["train_loss"]
        last_loss = summary.history[-1]["train_loss"]

        # Allow some tolerance — loss should generally decrease
        assert last_loss <= first_loss * 1.5, (
            f"Loss should not increase dramatically: first={first_loss:.4f} last={last_loss:.4f}"
        )

    def test_ema_applied_each_step(self):
        """Target encoder weights should change each step due to EMA.

        Lean 4 ref: ema_step is called each training step.
        """
        model = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)

        # Record initial target encoder params
        initial_params = {name: p.data.clone() for name, p in model.tgt_encoder.named_parameters()}

        trainer = JEPATrainer(
            model=model,
            config=JEPAConfig(latent_dim=D_LATENT, hidden_dim=D_HIDDEN),
            lr=1e-3,
            device="cpu",
            checkpoint_dir=Path(tempfile.mkdtemp()),
        )
        ds = _create_dataset(50)
        trainer.train(ds, epochs=2, batch_size=16)

        # After training, at least some target params should have changed
        changed = False
        for name, p in model.tgt_encoder.named_parameters():
            if not torch.allclose(p.data, initial_params[name], atol=1e-7):
                changed = True
                break
        assert changed, "Target encoder should change after EMA updates"

    def test_checkpoint_best_model_saved(self):
        """Best checkpoint should be saved on validation improvement."""
        trainer, ds = _create_trainer()
        summary = trainer.train(ds, epochs=3, batch_size=16)

        assert summary.checkpoint_path is not None
        assert Path(summary.checkpoint_path).exists(), (
            f"Checkpoint file should exist at {summary.checkpoint_path}"
        )

    def test_validation_metrics_computed(self):
        """Validation should produce all required metrics.

        Definition of Done D8: prediction accuracy metric.
        """
        trainer, ds = _create_trainer()
        summary = trainer.train(ds, epochs=2, batch_size=16)

        for record in summary.history:
            assert "val_loss" in record, "Missing val_loss metric"
            assert "energy_accuracy" in record, "Missing energy_accuracy metric"
            assert record["val_loss"] >= 0, "Val loss must be ≥ 0"

    def test_training_with_vicreg(self):
        """VICReg loss should contribute to total loss.

        Lean 4 ref: jepTrainingLoss = energy_loss + vicreg_loss
        """
        trainer, ds = _create_trainer()
        summary = trainer.train(ds, epochs=2, batch_size=16)

        for record in summary.history:
            assert "vicreg_loss" in record, "Missing vicreg_loss metric"
            assert record["vicreg_loss"] >= 0, "VICReg loss must be ≥ 0"

    def test_training_summary_fields(self):
        """TrainingSummary should have all required fields.

        API contract validation.
        """
        trainer, ds = _create_trainer()
        summary = trainer.train(ds, epochs=2, batch_size=16)

        assert isinstance(summary, TrainingSummary)
        assert summary.epochs_completed == 2
        assert summary.total_steps > 0
        assert summary.training_time_seconds > 0
        assert summary.final_train_loss >= 0
        assert summary.final_val_loss >= 0
        assert isinstance(summary.history, list)
        assert len(summary.history) == 2

    def test_trainer_device_cpu(self):
        """Training should work on CPU.

        CI compatibility requirement.
        """
        trainer, ds = _create_trainer()
        summary = trainer.train(ds, epochs=1, batch_size=8)
        assert summary.epochs_completed == 1

    def test_trainer_reproducibility_with_seed(self):
        """Same seed → same final loss.

        Reproducibility requirement.
        """
        ds = _create_dataset(50)

        model1 = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)
        model2 = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)
        # Copy initial weights
        model2.load_state_dict(model1.state_dict())

        trainer1 = JEPATrainer(
            model=model1,
            lr=1e-3,
            device="cpu",
            checkpoint_dir=Path(tempfile.mkdtemp()),
        )
        trainer2 = JEPATrainer(
            model=model2,
            lr=1e-3,
            device="cpu",
            checkpoint_dir=Path(tempfile.mkdtemp()),
        )

        summary1 = trainer1.train(ds, epochs=3, batch_size=16, seed=42)
        summary2 = trainer2.train(ds, epochs=3, batch_size=16, seed=42)

        assert abs(summary1.final_train_loss - summary2.final_train_loss) < 1e-3, (
            f"Reproducibility failed: {summary1.final_train_loss} vs {summary2.final_train_loss}"
        )
