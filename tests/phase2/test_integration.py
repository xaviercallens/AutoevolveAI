"""
Integration tests for Phase 2 — JEPA integration with AgentLoop.

Tests the end-to-end flow:
    Phase 1 → harvest → train JEPA → predict energy
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import torch

from anse.jepa.dataset import JEPADataset
from anse.jepa.trainer import JEPATrainer
from anse.jepa.world_model import JEPAWorldModel

D_INPUT = 64
D_HIDDEN = 32
D_LATENT = 16


def _create_dataset(n: int = 50) -> JEPADataset:
    """Create a synthetic JSONL dataset."""
    path = Path(tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False).name)
    with open(path, "w") as f:
        for i in range(n):
            trace = {
                "task": f"task_{i % 5}",
                "iteration": i % 4,
                "hidden_state": [float(j + i) / D_INPUT for j in range(D_INPUT)],
                "energy": float(i * 2 % 100),
            }
            f.write(json.dumps(trace) + "\n")
    return JEPADataset(path, hidden_dim=D_INPUT)


class TestAgentLoopIntegration:
    """Tests for JEPA integration with AgentLoop."""

    def test_agent_loop_with_world_model(self):
        """AgentLoop should accept optional world model (D10: non-breaking).

        Lean 4: jepEnergyFn composition is optional.
        """
        from anse.core.agent_loop import AgentLoop

        model = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT, mock_mode=True)

        loop = AgentLoop(
            extractor=MagicMock(),
            sandbox=MagicMock(),
            evaluator=MagicMock(),
            harvester=MagicMock(),
            world_model=model,
        )
        assert loop.world_model is not None
        assert loop.world_model.mock_mode is True

    def test_agent_loop_without_world_model(self):
        """AgentLoop should work fine without a world model (Phase 1 compat).

        Lean 4: Phase 1 EnergyFn operates independently of JEPA.
        """
        from anse.core.agent_loop import AgentLoop

        loop = AgentLoop(
            extractor=MagicMock(),
            sandbox=MagicMock(),
            evaluator=MagicMock(),
            harvester=MagicMock(),
        )
        assert loop.world_model is None

    def test_surprise_calculation(self):
        """|predicted - actual| should be computed correctly.

        Phase 4 preparation: surprise signal drives plasticity.
        """
        model = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)
        h = torch.randn(D_INPUT)

        predicted = model.predict_energy_scalar(h)
        actual = 75.0
        surprise = abs(predicted - actual)

        assert surprise >= 0, "Surprise must be ≥ 0"
        assert isinstance(surprise, float)

    def test_full_pipeline_phase1_to_phase2(self):
        """Full pipeline: harvest traces → train JEPA → predict energy.

        Lean 4: jepTrainingLoss_nonneg + jepEnergy_nonneg validated E2E.
        """
        # 1. Create synthetic Phase 1 traces
        ds = _create_dataset(50)
        assert len(ds) > 0

        # 2. Create and train JEPA
        model = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)
        trainer = JEPATrainer(
            model=model,
            lr=1e-3,
            device="cpu",
            checkpoint_dir=Path(tempfile.mkdtemp()),
        )
        summary = trainer.train(ds, epochs=5, batch_size=16)

        assert summary.epochs_completed == 5
        assert summary.total_steps > 0

        # 3. Predict energy
        h = torch.randn(D_INPUT)
        predicted = model.predict_energy_scalar(h)
        assert 0.0 <= predicted <= 100.0

    def test_world_model_improves_with_more_data(self):
        """Larger dataset → more training steps.

        Lean 4: exists_minimiser — more data helps find better parameters.
        """
        ds_small = _create_dataset(20)
        model_small = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)
        trainer_small = JEPATrainer(
            model=model_small,
            lr=1e-3,
            device="cpu",
            checkpoint_dir=Path(tempfile.mkdtemp()),
        )
        summary_small = trainer_small.train(ds_small, epochs=5, batch_size=8)

        ds_large = _create_dataset(100)
        model_large = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)
        trainer_large = JEPATrainer(
            model=model_large,
            lr=1e-3,
            device="cpu",
            checkpoint_dir=Path(tempfile.mkdtemp()),
        )
        summary_large = trainer_large.train(ds_large, epochs=5, batch_size=16)

        assert summary_small.total_steps > 0
        assert summary_large.total_steps > 0
        assert summary_large.total_steps > summary_small.total_steps
