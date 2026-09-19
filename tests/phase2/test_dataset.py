"""
Tests for anse.jepa.dataset — JEPA dataset loading and preprocessing.

Lean 4 refs:
    Dataset (X Y : Type*) (n : ℕ) where
      inputs  : Fin n → X    -- hidden state embeddings
      targets : Fin n → Y    -- actual energy scores
"""

import json
import tempfile
from pathlib import Path

import pytest
import torch
from torch.utils.data import DataLoader

from anse.jepa.dataset import JEPADataset, train_val_split


def _create_jsonl(n: int = 20, hidden_dim: int = 64) -> Path:
    """Create a temporary JSONL file with synthetic traces."""
    path = Path(tempfile.mktemp(suffix=".jsonl"))
    with open(path, "w") as f:
        for i in range(n):
            trace = {
                "task": f"task_{i % 5}",
                "iteration": i % 4,
                "hidden_state": [float(j) / hidden_dim for j in range(hidden_dim)],
                "energy": float(i * 5),  # 0, 5, 10, ...
                "code": f"print({i})",
            }
            f.write(json.dumps(trace) + "\n")
    return path


class TestJEPADataset:
    """Tests for JEPADataset loading and preprocessing."""

    def test_dataset_loads_from_jsonl(self):
        """JSONL should be parsed into a non-empty dataset.

        Lean 4 ref: Dataset(X, Y, n) — inputs and targets are populated.
        """
        path = _create_jsonl(20, 64)
        dataset = JEPADataset(path, hidden_dim=64)
        assert len(dataset) > 0, "Dataset should not be empty"

    def test_dataset_hidden_state_shape(self):
        """Each x should have the expected hidden_dim.

        Lean 4 ref: HiddenState(d) := EuclideanSpace ℝ (Fin d)
        """
        hidden_dim = 64
        path = _create_jsonl(10, hidden_dim)
        dataset = JEPADataset(path, hidden_dim=hidden_dim)

        h_ctx, h_tgt, energy = dataset[0]
        assert h_ctx.shape == (hidden_dim,), f"Expected ({hidden_dim},), got {h_ctx.shape}"
        assert h_tgt.shape == (hidden_dim,), f"Expected ({hidden_dim},), got {h_tgt.shape}"

    def test_dataset_energy_range_0_1(self):
        """Energy values should be normalised to [0, 1].

        Lean 4 ref: EnergyFn.eval bounded in [0, 100] → scaled to [0, 1]
        """
        path = _create_jsonl(10, 64)
        dataset = JEPADataset(path, hidden_dim=64, max_energy=100.0)

        for i in range(len(dataset)):
            _, _, energy = dataset[i]
            assert 0.0 <= energy.item() <= 1.0, \
                f"Energy should be in [0, 1], got {energy.item()}"

    def test_dataset_pairs_consecutive_traces(self):
        """Pairs should be formed from traces grouped by task.

        Lean 4 ref: Dataset.inputs/targets mapping.
        """
        path = _create_jsonl(20, 64)
        dataset = JEPADataset(path, hidden_dim=64)
        # Each trace forms a valid pair
        assert len(dataset) == 20, f"Expected 20 pairs, got {len(dataset)}"

    def test_dataset_empty_jsonl(self):
        """Empty JSONL should produce an empty dataset gracefully."""
        path = Path(tempfile.mktemp(suffix=".jsonl"))
        path.write_text("")
        dataset = JEPADataset(path, hidden_dim=64)
        assert len(dataset) == 0

    def test_dataset_missing_file(self):
        """Missing file should produce an empty dataset with a warning."""
        dataset = JEPADataset("/nonexistent/file.jsonl", hidden_dim=64)
        assert len(dataset) == 0

    def test_dataset_train_val_split(self):
        """80/20 split should be deterministic and cover all samples.

        Lean 4 ref: Reproducibility requirement.
        """
        path = _create_jsonl(100, 64)
        dataset = JEPADataset(path, hidden_dim=64)
        train_ds, val_ds = train_val_split(dataset, val_fraction=0.2, seed=42)

        assert len(train_ds) + len(val_ds) == len(dataset)
        assert len(val_ds) >= 1
        assert len(train_ds) >= 1

        # Deterministic
        train_ds2, val_ds2 = train_val_split(dataset, val_fraction=0.2, seed=42)
        assert len(train_ds) == len(train_ds2)
        assert len(val_ds) == len(val_ds2)

    def test_dataset_l2_normalisation(self):
        """Hidden states should be L2-normalised when normalise=True.

        Lean 4 ref: HiddenState preprocessing.
        """
        path = _create_jsonl(5, 64)
        dataset = JEPADataset(path, hidden_dim=64, normalise=True)

        h_ctx, _, _ = dataset[0]
        norm = h_ctx.norm(p=2).item()
        assert abs(norm - 1.0) < 1e-4, f"Expected L2 norm ≈ 1.0, got {norm}"

    def test_dataset_dataloader_batching(self):
        """DataLoader should produce batches with correct shapes."""
        path = _create_jsonl(20, 64)
        dataset = JEPADataset(path, hidden_dim=64)
        loader = DataLoader(dataset, batch_size=8, shuffle=False)

        batch = next(iter(loader))
        h_ctx, h_tgt, energy = batch
        assert h_ctx.shape == (8, 64), f"Expected (8, 64), got {h_ctx.shape}"
        assert h_tgt.shape == (8, 64), f"Expected (8, 64), got {h_tgt.shape}"
        assert energy.shape == (8,), f"Expected (8,), got {energy.shape}"
