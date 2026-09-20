"""
JEPA Dataset — loads Phase 1 harvested traces into a PyTorch Dataset.

Lean 4 ref: Basic.lean §5
    structure Dataset (X Y : Type*) (n : ℕ) where
      inputs  : Fin n → X    -- hidden state embeddings h ∈ ℝ^d
      targets : Fin n → Y    -- actual energy scores ∈ [0, 100]

Sources:
  · Phase 1 Harvester JSONL (interactions.jsonl)
  · HiddenStateRecord.to_embedding() → list[float] of length d_model
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import torch
from torch.utils.data import Dataset, random_split

logger = logging.getLogger("anse.jepa.dataset")


class JEPADataset(Dataset):
    """PyTorch Dataset for JEPA world model training.

    Each sample is a tuple:
        (h_context, h_target, energy_actual)

    Where:
        h_context: Hidden state from the *prompt* attempt (ℝ^d)
        h_target:  Hidden state from the *converged* attempt (ℝ^d)
        energy_actual: Sandbox energy score normalised to [0, 1]

    Lean 4 ref::

        structure Dataset (X Y : Type*) (n : ℕ) where
          inputs  : Fin n → X
          targets : Fin n → Y
    """

    def __init__(
        self,
        jsonl_path: Path | str,
        hidden_dim: int = 4096,
        normalise: bool = True,
        max_energy: float = 100.0,
    ):
        """Load traces from a Phase 1 JSONL log.

        Args:
            jsonl_path: Path to interactions.jsonl from Phase 1 Harvester.
            hidden_dim: Expected hidden state dimension (Lean 4: d).
            normalise: If True, L2-normalise hidden states.
            max_energy: Maximum energy value for normalisation (default: 100.0).
        """
        self.hidden_dim = hidden_dim
        self.normalise = normalise
        self.max_energy = max_energy
        self._pairs: list[tuple[torch.Tensor, torch.Tensor, float]] = []

        jsonl_path = Path(jsonl_path)
        if not jsonl_path.exists():
            logger.warning("JSONL file not found: %s — dataset will be empty", jsonl_path)
            return

        traces = self._load_traces(jsonl_path)
        self._build_pairs(traces)
        logger.info(
            "JEPADataset: loaded %d pairs from %d traces (%s)",
            len(self._pairs),
            len(traces),
            jsonl_path,
        )

    def _load_traces(self, path: Path) -> list[dict[str, Any]]:
        """Parse JSONL file into a list of trace dicts."""
        traces = []
        with open(path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    traces.append(obj)
                except json.JSONDecodeError:
                    logger.warning("Skipping malformed JSON at line %d", line_num)
        return traces

    def _build_pairs(self, traces: list[dict[str, Any]]) -> None:
        """Build (context, target, energy) training pairs.

        Strategy: group traces by task, then form pairs of
        (first attempt, best attempt) within each task group.
        Falls back to self-pairing if only one trace per task.
        """
        # Group by task
        task_groups: dict[str, list[dict[str, Any]]] = {}
        for t in traces:
            task = t.get("task", "unknown")
            if task not in task_groups:
                task_groups[task] = []
            task_groups[task].append(t)

        for task, group in task_groups.items():
            # Sort by iteration (ascending) — first attempt vs converged
            group.sort(key=lambda t: t.get("iteration", 0))

            for trace in group:
                hs = trace.get("hidden_state")
                energy = trace.get("energy", 100.0)

                if hs is None or len(hs) == 0:
                    continue

                # Truncate or pad to hidden_dim
                hs_tensor = self._to_tensor(hs)
                if hs_tensor is None:
                    continue

                # For now, use the same hidden state as both context and target
                # (Phase 2 trains on individual state → energy pairs)
                energy_norm = min(energy / self.max_energy, 1.0)
                self._pairs.append((hs_tensor, hs_tensor.clone(), energy_norm))

    def _to_tensor(self, hs: list[float]) -> torch.Tensor | None:
        """Convert hidden state list to tensor with optional L2 normalisation.

        Lean 4 ref: HiddenState (d : ℕ) := EuclideanSpace ℝ (Fin d)
        """
        try:
            t = torch.tensor(hs, dtype=torch.float32)
        except (TypeError, ValueError):
            return None

        # Pad or truncate to hidden_dim
        if t.shape[0] < self.hidden_dim:
            pad = torch.zeros(self.hidden_dim - t.shape[0])
            t = torch.cat([t, pad])
        elif t.shape[0] > self.hidden_dim:
            t = t[: self.hidden_dim]

        if self.normalise:
            norm = t.norm(p=2)
            if norm > 0:
                t = t / norm

        return t

    def __len__(self) -> int:
        return len(self._pairs)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        h_ctx, h_tgt, energy = self._pairs[idx]
        return h_ctx, h_tgt, torch.tensor(energy, dtype=torch.float32)


def train_val_split(
    dataset: JEPADataset,
    val_fraction: float = 0.2,
    seed: int = 42,
) -> tuple[Dataset, Dataset]:
    """Split dataset into training and validation sets.

    Args:
        dataset: Full JEPADataset.
        val_fraction: Fraction of data for validation (default: 0.2).
        seed: Random seed for reproducibility.

    Returns:
        (train_dataset, val_dataset) tuple.
    """
    n_total = len(dataset)
    n_val = max(1, int(n_total * val_fraction))
    n_train = n_total - n_val

    generator = torch.Generator().manual_seed(seed)
    return random_split(dataset, [n_train, n_val], generator=generator)  # type: ignore
