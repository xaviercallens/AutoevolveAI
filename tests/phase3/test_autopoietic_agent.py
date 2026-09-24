"""
Tests for ANSEAutopoieticAgent:
- System 2 Deep Think (Thought Optimization)
- Self-Coding & Deterministic Sandbox Verification
- Neural Network Auto-Influencing & Zero-Downtime Hot-Swapping
- Continuous Plasticity & Active Inference
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import torch
import torch.nn as nn

from anse.autopoiesis.autopoietic_agent import (
    ANSEAutopoieticAgent,
    AutopoieticJEPAWorldModel,
    SelfCodingActionDecoder,
)


def test_jepa_world_model_prediction() -> None:
    """Verify that JEPA World Model predicts latent transitions in conceptual space."""
    world_model = AutopoieticJEPAWorldModel(latent_dim=64, hidden_dim=128)
    z_t = torch.randn(4, 64)
    a_t = torch.randn(4, 64)

    z_pred = world_model(z_t, a_t)
    assert z_pred.shape == (4, 64)
    assert not torch.isnan(z_pred).any()


def test_system_2_deep_think_pondering(tmp_path: Path) -> None:
    """Verify that System 2 Deep Think minimizes internal energy through calculus on thoughts."""
    agent = ANSEAutopoieticAgent(input_dim=64, latent_dim=32, registry_dir=tmp_path / "reg")
    sensory_input = torch.randn(2, 64)

    curr_state, best_thought, trajectory = agent.system_2_deep_think(
        sensory_input, thinking_steps=5, lr=0.1
    )

    assert curr_state.shape == (2, 32)
    assert best_thought.shape == (2, 32)
    assert len(trajectory) == 5

    # Initial energy vs final energy after pondering
    e_initial = trajectory[0].thought_energy
    e_final = trajectory[-1].thought_energy
    # Pondering should reduce or minimize cognitive proxy energy
    assert trajectory[-1].proxy_energy <= trajectory[0].proxy_energy + 1e-4


def test_self_coding_and_sandbox_verification(tmp_path: Path) -> None:
    """Verify that thought vector decodes to executable PyTorch code and passes sandbox physics."""
    agent = ANSEAutopoieticAgent(input_dim=64, latent_dim=32, registry_dir=tmp_path / "reg")

    # Positive coherent thought vector -> triggers valid neural architecture
    positive_thought = torch.ones(1, 32) * 1.5
    result = agent.self_code_and_verify(positive_thought)

    assert result.is_valid is True
    assert result.energy == 0.0
    assert result.parameters < 50000
    assert result.output_shape == "(16, 10)"
    assert result.proof_token is not None


def test_autopoietic_neural_auto_influencing_hotswap(tmp_path: Path) -> None:
    """Verify that the agent auto-influences its own architecture, asserts ΔE < 0, and hot-swaps."""
    agent = ANSEAutopoieticAgent(input_dim=64, latent_dim=128, registry_dir=tmp_path / "reg")

    # Verify initial baseline engine
    assert agent.attention_engine.version == "1.0.0-quadratic-parent"
    assert agent.registry.active_version("attention_engine") == 1

    # Execute autopoietic self-evolution
    report = agent.auto_evolve_attention_engine()

    assert report.is_promoted is True
    assert report.delta_energy < 0.0
    assert report.proof_token is not None
    assert agent.attention_engine.version == "2.0.0-flash-child"
    assert agent.registry.active_version("attention_engine") == 2

    # Forward pass executes seamlessly with newly installed engine
    x = torch.randn(4, 64)
    out = agent(x)
    assert out.shape == (4, 128)


def test_continuous_plasticity_active_inference(tmp_path: Path) -> None:
    """Verify that active inference updates synaptic weights instantly on reality surprise."""
    agent = ANSEAutopoieticAgent(input_dim=64, latent_dim=32, lr=1e-3, registry_dir=tmp_path / "reg")

    state = torch.randn(1, 32)
    action = torch.randn(1, 32)
    reality_feedback = torch.randn(1, 64)

    # Initial weights snapshot
    initial_weight = agent.world_model.predictor[0].weight.clone()

    surprise_energy = agent.continuous_plasticity(state, action, reality_feedback)

    assert isinstance(surprise_energy, float)
    assert surprise_energy >= 0.0

    # Synapses were immediately rewired via backward pass
    updated_weight = agent.world_model.predictor[0].weight
    diff = torch.norm(updated_weight - initial_weight).item()
    assert diff > 0.0, "Continuous plasticity must update synaptic weights on surprise"
