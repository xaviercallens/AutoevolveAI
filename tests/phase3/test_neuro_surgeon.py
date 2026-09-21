"""
Unit tests for Phase 3: The Autopoietic Bootstrap & AI Neuro-Surgeon.
Tests:
- MicroMLRealityEngine physical assertions & shape mismatch interception
- ActiveInferenceLoop multi-turn dimension debugging from ENERGY: 100 -> ENERGY: 0
- AutopoieticNeuroSurgeon FlashAttention hot-swap under ΔE < 0
"""

from __future__ import annotations

import textwrap

from anse.autopoiesis.neuro_surgeon import (
    ActiveInferenceLoop,
    AutopoieticNeuroSurgeon,
    MicroMLRealityEngine,
)


def test_reality_engine_clean_model() -> None:
    """Verify that a valid CustomNet satisfies the laws of physics (ENERGY: 0)."""
    engine = MicroMLRealityEngine()
    code = textwrap.dedent("""
import torch
import torch.nn as nn

class CustomNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d((4, 4))
        self.linear = nn.Linear(3 * 4 * 4, 10)

    def forward(self, x):
        h = self.pool(x).reshape(x.size(0), -1)
        return self.linear(h)
""")
    res = engine.evaluate_code(code)
    assert res.is_valid is True
    assert res.energy == 0.0
    assert res.output_shape == "(16, 10)"
    assert res.proof_token is not None
    assert res.parameters < 50000


def test_reality_engine_shape_mismatch() -> None:
    """Verify that a dimension collapse triggers ENERGY: 100 and diagnostic error."""
    engine = MicroMLRealityEngine()
    code = textwrap.dedent("""
import torch
import torch.nn as nn

class CustomNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d((4, 4))
        # Wrong output shape: 32 instead of 10!
        self.linear = nn.Linear(3 * 4 * 4, 32)

    def forward(self, x):
        h = self.pool(x).reshape(x.size(0), -1)
        return self.linear(h)
""")
    res = engine.evaluate_code(code)
    assert res.is_valid is False
    assert res.energy == 100.0
    assert res.error_trace is not None
    assert "Shape mismatch" in res.error_trace


def test_reality_engine_parameter_budget_exceeded() -> None:
    """Verify that models exceeding the 50k parameter budget receive ENERGY: 100."""
    engine = MicroMLRealityEngine(max_params=1000)
    code = textwrap.dedent("""
import torch
import torch.nn as nn

class CustomNet(nn.Module):
    def __init__(self):
        super().__init__()
        # 12288 * 10 = 122,880 parameters (> 1000 limit)
        self.linear = nn.Linear(3 * 64 * 64, 10)

    def forward(self, x):
        return self.linear(x.reshape(x.size(0), -1))
""")
    res = engine.evaluate_code(code)
    assert res.is_valid is False
    assert res.energy == 100.0
    assert "Parameter budget exceeded" in str(res.error_trace)


def test_reality_engine_ast_stub_rejected() -> None:
    """Verify that deceptive empty stubs are blocked before execution."""
    engine = MicroMLRealityEngine()
    code = textwrap.dedent("""
import torch.nn as nn

class CustomNet(nn.Module):
    def forward(self, x):
        pass
""")
    res = engine.evaluate_code(code)
    assert res.is_valid is False
    assert res.energy == 100.0
    assert "AST Whistleblower rejection" in str(res.error_trace)


def test_active_inference_loop_multi_turn() -> None:
    """Verify that ActiveInferenceLoop drives the agent from ENERGY: 100 to ENERGY: 0."""
    loop = ActiveInferenceLoop()
    steps = loop.run_simulation()

    assert len(steps) == 2
    # Turn 1: Shape collapse
    assert steps[0].iteration == 1
    assert steps[0].energy == 100.0
    assert steps[0].is_valid is False
    assert "failed the laws of physics" in str(steps[0].feedback_prompt)

    # Turn 2: Self-corrected mathematical transformation
    assert steps[1].iteration == 2
    assert steps[1].energy == 0.0
    assert steps[1].is_valid is True
    assert steps[1].proof_token is not None


def test_autopoietic_neuro_surgeon_hotswap() -> None:
    """Verify that the Neuro-Surgeon benchmarks parent vs FlashAttention child and hot-swaps under ΔE < 0."""
    surgeon = AutopoieticNeuroSurgeon()
    assert surgeon.live_engine.version == "1.0.0-quadratic-parent"

    # On CPU-only hosts parent and child latencies are statistically indistinguishable, so the
    # swap outcome is hardware-dependent. Assert the thermodynamic invariant (swap iff ΔE < 0);
    # the deterministic authorize/reject scenarios live in test_coverage_gaps_phase3.py.
    report = surgeon.execute_neuro_surgery()
    assert report.hotswap_authorized == (report.delta_energy < 0)
    assert report.speedup_factor > 0
    assert (report.proof_token is not None) == report.hotswap_authorized
    expected = "2.0.0-flash-child" if report.hotswap_authorized else "1.0.0-quadratic-parent"
    assert surgeon.live_engine.version == expected
