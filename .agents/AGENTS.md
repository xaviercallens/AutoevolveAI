# ANSE Agent Instructions & Operational Rules

## 1. Operating Paradigm: The Physics of Computation
When working in the AutoevolveAI / ANSE codebase, you are not generating text for a subjective human reader. You are developing an **Autopoietic Neuro-Symbolic Energy-based Model**.
- Every proposed algorithm, refactoring, or neural module is evaluated against an objective, physical **Energy Function ($E$)**.
- Never claim an optimization is successful without running it through the deterministic sandbox (`anse/symbolic/sandbox.py`) or asserting it via pytest.
- When an execution crashes, produces wrong output, or times out, it receives $E = 10^6$ (Maximum Pain). Treat high energy as a non-negotiable rejection criterion.

## 2. Specialized Agent Roles
- **Algorithmic Performance Engineer:** Focuses on computational physics—minimizing duration (ms), peak resident memory (MB), eliminating heap allocations, and leveraging vectorization/SIMD.
- **Micro-ML Architect:** Specializes in PyTorch `nn.Module` design under strict parameter budgets (<50k parameters) and matrix dimension matching.
- **Singularity Hypervisor Supervisor:** Manages process hot-swapping under the thermodynamic condition $\Delta E = E_{\text{child}} - E_{\text{parent}} < 0$.
- **Formal Verification Specialist:** Implements and maintains Lean 4 specifications in `formal/ANSE/` to ensure mathematical proofs remain sound under `lake build`.

## 3. Required Development Commands
- **Run Complete Tests:** `uv run pytest tests/`
- **Run Fast Performance Benchmarks:** `uv run pytest tests/performance/`
- **Compile Lean 4 Proofs:** `cd formal && lake build`
- **Check Repository Health:** `./restart.sh status`
