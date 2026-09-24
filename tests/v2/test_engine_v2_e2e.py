"""End-to-End integration tests for ANSE 2.0 Autopoietic Engine."""

import shutil
import tempfile
from pathlib import Path

import torch

from anse.v2.engine_v2 import ANSEEngineV2


def test_anse_v2_autonomous_cycle():
    temp_dir = Path(tempfile.mkdtemp())
    try:
        engine = ANSEEngineV2(input_dim=32, latent_dim=16, registry_dir=temp_dir)
        sensory_input = torch.randn(2, 32)

        result = engine.run_autonomous_cycle(
            sensory_input=sensory_input,
            prompt_text="Evolve high-performance tensor routing module",
            num_monte_carlo=200,
            trigger_sleep_after=True,
        )

        assert result.cycle_id == 1
        assert result.surrogate_summary.total_evaluated == 200
        assert result.surrogate_summary.selected_count == 8
        assert result.falsification_report.is_falsified is False
        assert result.sandbox_verified is True
        assert result.final_energy_score < 1e5
        assert result.rem_summary is not None
        assert result.total_cycle_ms > 0.0

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
