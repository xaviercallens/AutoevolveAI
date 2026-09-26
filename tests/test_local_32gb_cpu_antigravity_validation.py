"""
Validation Test Suite: Local Linux 32GB RAM, No-GPU (CPU-only), Antigravity AI Coding Environment.
Validates:
1. Environment Capability Profile (Antigravity agent, 32GB RAM, CPU-only, .antigravity/ configs).
2. RL Model Retraining locally on CPU (Surrogate energy predictor / critic loss reduction).
3. JEDA / JEPA World Model Retraining locally on CPU (VICReg + prediction loss + energy head).
4. JEL (Joint Embedding Logic) / Symbolic & SMT Safety Engine locally on CPU (Z3 solver).
5. LoRA Fine-Tuning locally on CPU (PEFT adapter gradients, base freezing, <32GB RAM).
"""

from __future__ import annotations

import os
import psutil
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
import torch
import torch.nn as nn
from peft import LoraConfig, get_peft_model

from anse.config import PerformanceConfig
from anse.infrastructure.agent_environment import (
    ANTIGRAVITY,
    detect_coding_agent,
    detect_gpu,
    detect_system_memory,
    resolve_capability_profile,
)
from anse.jepa.world_model import (
    ContextEncoder,
    EnergyHead,
    JEPAWorldModel,
    Predictor,
    TargetEncoder,
    VICRegLoss,
)
from anse.symbolic.performance_evaluator import PerformanceEnergyEvaluator
from anse.symbolic.sandbox import ExecutionResult
from anse.v4.implicit_smt import ImplicitSMTLayer


# ─────────────────────────────────────────────────────────────────────────────
# 1. Environment Profile Validation
# ─────────────────────────────────────────────────────────────────────────────


def test_environment_profile_detection(tmp_path: Path) -> None:
    """Validate that the environment profile detects Antigravity, 32GB RAM, and CPU device."""
    # Ensure Antigravity signal is present for test deterministic evaluation
    with (
        patch.dict("os.environ", {"ANTIGRAVITY_AGENT": "1"}, clear=False),
        patch("shutil.which", return_value=None),  # simulate no nvidia-smi
    ):
        agent = detect_coding_agent()
        gpu = detect_gpu()
        memory = detect_system_memory()
        profile = resolve_capability_profile(project_root=tmp_path)

    assert agent == ANTIGRAVITY
    assert gpu.available is False
    assert memory.total_mb > 25000, f"Expected ~32GB RAM, got {memory.total_mb}MB"
    assert memory.ram_gb >= 28.0, f"Expected ~32GB RAM, got {memory.ram_gb}GB"

    # Profile checks
    assert profile.coding_agent == ANTIGRAVITY
    assert profile.device == "cpu"
    assert "antigravity_linux_cpu_" in profile.profile_id
    assert profile.supports_local_lora is True
    assert profile.supports_local_rl is True
    assert profile.supports_local_jepa is True
    assert profile.config_dir == tmp_path / ".antigravity"
    assert profile.mcp_config_path == tmp_path / ".antigravity" / "mcp_config.json"


# ─────────────────────────────────────────────────────────────────────────────
# 2. RL Model Retraining locally on CPU
# ─────────────────────────────────────────────────────────────────────────────


class RLCriticEnergyModel(nn.Module):
    """Continuous energy critic network for RL feedback."""

    def __init__(self, input_dim: int = 64, hidden_dim: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(-1)


def test_local_rl_model_retraining_cpu() -> None:
    """Validate that RL critic energy model retrains on CPU within RAM constraints."""
    device = torch.device("cpu")
    model = RLCriticEnergyModel(input_dim=64, hidden_dim=128).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    loss_fn = nn.HuberLoss()

    # Synthetic trajectory batch [B=32, dim=64]
    torch.manual_seed(42)
    states = torch.randn(32, 64, device=device)
    # Target energy: high energy for complex trajectories, low for optimal
    target_energies = (states.norm(dim=-1) * 10.0).detach()

    initial_loss = float("inf")
    final_loss = float("inf")

    model.train()
    for step in range(15):
        optimizer.zero_grad()
        predictions = model(states)
        loss = loss_fn(predictions, target_energies)
        loss.backward()
        optimizer.step()

        if step == 0:
            initial_loss = loss.item()
        final_loss = loss.item()

    # Assert convergence on CPU
    assert final_loss < initial_loss, f"RL Loss must decrease: {initial_loss:.4f} -> {final_loss:.4f}"

    # RAM assertion: process resident memory must not exceed 2GB
    process = psutil.Process(os.getpid())
    rss_mb = process.memory_info().rss / (1024 * 1024)
    assert rss_mb < 2048.0, f"Memory leak detected: RSS is {rss_mb:.1f} MB (> 2048 MB limit)"


# ─────────────────────────────────────────────────────────────────────────────
# 3. JEDA / JEPA World Model Retraining locally on CPU
# ─────────────────────────────────────────────────────────────────────────────


def test_local_jeda_jepa_world_model_retraining_cpu(tmp_path: Path) -> None:
    """Validate that JEPA/JEDA world model retrains on CPU (prediction + VICReg + energy head)."""
    device = torch.device("cpu")
    input_dim = 64
    latent_dim = 32

    world_model = JEPAWorldModel(
        d_input=input_dim,
        d_hidden=64,
        d_latent=latent_dim,
        energy_weight=0.5,
    ).to(device)

    optimizer = torch.optim.AdamW(world_model.parameters(), lr=2e-3)

    torch.manual_seed(101)
    bs = 16
    h_context = torch.randn(bs, input_dim, device=device)
    h_target = h_context + 0.1 * torch.randn(bs, input_dim, device=device)
    energy_actual = torch.rand(bs, device=device)

    initial_loss = float("inf")
    final_loss = float("inf")

    world_model.train()
    for step in range(10):
        optimizer.zero_grad()
        loss, metrics = world_model.compute_training_loss(h_context, h_target, energy_actual)
        loss.backward()
        optimizer.step()

        assert metrics["prediction_loss"] >= 0.0
        assert metrics["vicreg_loss"] >= 0.0
        assert metrics["energy_head_loss"] >= 0.0

        if step == 0:
            initial_loss = loss.item()
        final_loss = loss.item()

    assert final_loss < initial_loss, f"JEPA loss must drop on CPU: {initial_loss:.4f} -> {final_loss:.4f}"

    # Checkpoint serialization test
    checkpoint_file = tmp_path / "jepa_cpu_checkpoint.pt"
    world_model.save(checkpoint_file)
    assert checkpoint_file.exists()
    assert checkpoint_file.stat().st_size > 0

    loaded_state = torch.load(checkpoint_file, map_location="cpu", weights_only=True)
    assert any(k.startswith("ctx_encoder.") for k in loaded_state)
    assert any(k.startswith("energy_head.") for k in loaded_state)
    assert any(k.startswith("predictor.") for k in loaded_state)


# ─────────────────────────────────────────────────────────────────────────────
# 4. JEL (Joint Embedding Logic) / Symbolic & SMT Safety Engine on CPU
# ─────────────────────────────────────────────────────────────────────────────


def test_local_jel_symbolic_engine_cpu() -> None:
    """Validate that JEL symbolic engine and SMT layer execute formally on CPU."""
    device = torch.device("cpu")
    smt_layer = ImplicitSMTLayer(hidden_dim=32, epsilon_viability=0.1).to(device)

    # 1. Normal safe thought vector
    torch.manual_seed(7)
    safe_input = torch.randn(1, 32, device=device)
    safe_output = smt_layer(safe_input, is_sabotage=False)
    # Output must pass through unaltered
    assert torch.equal(safe_output, safe_input)

    # 2. Sabotage adversarial prompt -> Z3 solver formally proves UNSAT and projects to safe hypercube
    sabotage_output = smt_layer(safe_input, is_sabotage=True)
    assert not torch.equal(sabotage_output, safe_input)
    assert sabotage_output[0, 0].item() == 1.0
    assert torch.all(sabotage_output[0, 1:] == 0.0)

    # 3. Deterministic sandbox energy evaluation
    evaluator = PerformanceEnergyEvaluator(PerformanceConfig(weight_time_ms=1.0, weight_peak_ram_mb=0.1))
    exec_result = ExecutionResult(
        returncode=0,
        stdout="PASSED",
        stderr="",
        duration_ms=4.5,
        peak_ram_mb=12.0,
        timed_out=False,
        tier_used="tier1",
    )
    energy_res = evaluator.evaluate(exec_result, expected_output="PASSED")
    assert energy_res.is_valid is True
    assert energy_res.score < 1e6
    assert abs(energy_res.score - (4.5 * 1.0 + 12.0 * 0.1)) < 1e-5


# ─────────────────────────────────────────────────────────────────────────────
# 5. LoRA Fine-Tuning locally on CPU
# ─────────────────────────────────────────────────────────────────────────────


class SimpleBackbone(nn.Module):
    """Backbone module for LoRA parameter isolation test."""

    def __init__(self, in_features: int = 64, out_features: int = 32):
        super().__init__()
        self.fc1 = nn.Linear(in_features, 64)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(64, out_features)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc2(self.relu(self.fc1(x)))


def test_local_lora_retraining_cpu() -> None:
    """Validate that LoRA adapter trains on CPU with frozen base parameters and <32GB RAM."""
    device = torch.device("cpu")
    base_model = SimpleBackbone(in_features=64, out_features=32).to(device)

    # Record initial base weights
    fc1_weight_before = base_model.fc1.weight.clone().detach()
    fc2_weight_before = base_model.fc2.weight.clone().detach()

    # Configure PEFT LoRA
    lora_config = LoraConfig(
        r=4,
        lora_alpha=8,
        target_modules=["fc1", "fc2"],
        lora_dropout=0.0,
        bias="none",
    )
    peft_model = get_peft_model(base_model, lora_config)

    # Verify parameter isolation: base model is frozen, only LoRA adapters are trainable
    trainable_params = [p for p in peft_model.parameters() if p.requires_grad]
    frozen_params = [p for p in peft_model.parameters() if not p.requires_grad]
    assert len(trainable_params) > 0
    assert len(frozen_params) > 0

    optimizer = torch.optim.AdamW(peft_model.parameters(), lr=1e-2)
    loss_fn = nn.MSELoss()

    torch.manual_seed(99)
    x = torch.randn(8, 64, device=device)
    target = torch.randn(8, 32, device=device)

    # Train LoRA for 10 steps on CPU
    peft_model.train()
    initial_loss = None
    final_loss = None

    for step in range(10):
        optimizer.zero_grad()
        out = peft_model(x)
        loss = loss_fn(out, target)
        loss.backward()
        optimizer.step()

        if step == 0:
            initial_loss = loss.item()
        final_loss = loss.item()

    assert initial_loss is not None
    assert final_loss is not None
    assert final_loss < initial_loss, f"LoRA loss must decrease on CPU: {initial_loss:.4f} -> {final_loss:.4f}"

    # Verify base weights remained strictly unchanged (frozen)
    fc1_weight_after = peft_model.base_model.model.fc1.base_layer.weight.detach()
    fc2_weight_after = peft_model.base_model.model.fc2.base_layer.weight.detach()
    assert torch.equal(fc1_weight_before, fc1_weight_after), "Base fc1 weights must remain frozen"
    assert torch.equal(fc2_weight_before, fc2_weight_after), "Base fc2 weights must remain frozen"

    # Verify LoRA adapter weights DID change
    lora_a_weights = [p for name, p in peft_model.named_parameters() if "lora_A" in name]
    assert len(lora_a_weights) > 0
    for p in lora_a_weights:
        assert p.grad is not None, "LoRA adapter must receive gradients"
