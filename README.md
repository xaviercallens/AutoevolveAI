# AutoevolveAI — ANSE Architecture

[![Lean 4 Formal Specs](https://img.shields.io/badge/Lean_4-v4.34.0--rc2-blue)](formal/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: >=3.12](https://img.shields.io/badge/Python->=3.12-brightgreen.svg)](pyproject.toml)

**ANSE (Autopoietic Neuro-Symbolic Energy-based model)** is an autonomous AI paradigm that grounds machine learning, System 2 reasoning, and autonomous self-refactoring in the **deterministic physics of computation and neural networks**.

---

## Key Pillars

1. **Continuous Physical Energy Signal ($E$)**:
   - Replaces subjective LLM output evaluation with strict computational metrics (latency, memory footprint, vectorization, tensor dimensions, parameter budgets, and validation loss).
2. **Deterministic Sandbox Execution**:
   - Two-tier execution environment (Subprocess & Docker) that runs candidate algorithms and PyTorch neural modules under deterministic hardware constraints.
3. **Formal Verification in Lean 4**:
   - Mathematical theorems certifying energy monotonicity, parameter boundary constraints, and Banach fixed-point autopoietic convergence proven in Lean 4 with Mathlib4.
4. **Autopoietic Self-Refactoring & Hot-Swapping**:
   - The AI Neuro-Surgeon: An integrated hypervisor evaluates child processes refactoring core routines (such as $O(N^2)$ Attention $\to$ FlashAttention), executing safe OS-level process hot-swapping when thermodynamic dominance is proven ($E_{child} < E_{parent}$).

---

## Architecture Progression

| Phase | Role | Domain | Optimization Objective |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Algorithmic Performance Engineer** | Computational Physics | Minimize $E = \text{Duration (ms)} + \text{Peak RAM (MB)}$ via cache locality & SIMD. |
| **Phase 2** | **Micro-ML Architect** | Neural Network Architecture | Classify messy datasets with $>95\%$ accuracy under $<50{,}000$ parameters. |
| **Phase 3** | **Autopoietic Bootstrap** | Self-Referential Engine | Refactor internal System 2 attention mechanisms with FlashAttention and hot-swap. |

---

## Getting Started

### Prerequisites
- Python >= 3.12 (managed via `uv`)
- Lean 4 `v4.34.0-rc2` & `lake`

### Installation
```bash
# Clone the repository
git clone https://github.com/xaviercallens/AutoevolveAI.git
cd AutoevolveAI

# Install Python dependencies
uv sync

# Build formal Lean 4 verification proofs
cd formal
lake build
cd ..
```

### Running Tests
```bash
# Run unit & performance regression test suite (32 tests across all 3 phases)
uv run pytest tests/performance tests/phase2/test_ml_evaluator.py tests/phase2/test_ml_sandbox.py tests/autopoiesis
```

---

## Formal Theorems Certified in Lean 4
All proofs compile cleanly via `lake build`:
- **Theorem P1–P5 (`ANSE.Performance`)**: Computational energy non-negativity, maximal penalty on failure, monotonicity, and vectorization supremacy.
- **Theorem M1–M3 (`ANSE.MicroML`)**: Shape mismatch maximal pain barrier, parameter boundary penalty, and validation loss monotonicity.
- **Autopoietic Fixed Point & Hot-Swap (`ANSE.Autopoiesis`)**: Banach contraction mapping equilibrium and thermodynamic hot-swap validity.

---

## License
MIT License.
