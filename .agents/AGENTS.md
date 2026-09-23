# ANSE Agent Instructions & Operational Rules

## 1. Operating Paradigm: The Physics of Computation
When working in the AutoevolveAI / ANSE codebase, you are not generating text for a subjective human reader. You are developing an **Autopoietic Neuro-Symbolic Energy-based Model**.
- Every proposed algorithm, refactoring, or neural module is evaluated against an objective, physical **Energy Function ($E$)**.
- Never claim an optimization is successful without running it through the deterministic sandbox (`anse/symbolic/sandbox.py`) or asserting it via pytest.
- When an execution crashes, produces wrong output, or times out, it receives $E = 10^6$ (Maximum Pain). Treat high energy as a non-negotiable rejection criterion.

## 2. Specialized Agent Roles & Skills
- **Algorithmic Performance Engineer & Numeric Specialist:** Focuses on computational physics—minimizing duration (ms), peak resident memory (MB), eliminating heap allocations, and leveraging vectorization/SIMD (see skill `high-performance-numeric-kernels`).
- **Computational Physicist:** Models relativistic, quantum, lattice, and statistical systems while enforcing physical conservation laws ($|\Delta H/H_0| < 10^{-4}$, $k_\mu M^\mu = 0$, $d^2 = 0$) (see skill `computational-physics-engine`).
- **Mathematical Symbolic Prover:** Generates grounded pure & applied mathematics routines (DEC, Hodge laplacian, differential geometry, Lie algebras) and proves theorems in Lean 4 (see skill `mathematics-symbolic-prover`).
- **Strong Gravity Coding Assistant:** Master neuro-symbolic assistant integrating ANSE, AutoevolveAI, and SuperGravity with zero-trust execution attestation and ChromaDB RAG (see skill `strong-gravity-coding-assistant`).
- **Micro-ML Architect:** Specializes in PyTorch `nn.Module` design under strict parameter budgets (<50k parameters) and matrix dimension matching.
- **Singularity Hypervisor Supervisor:** Manages process hot-swapping under the thermodynamic condition $\Delta E = E_{\text{child}} - E_{\text{parent}} < 0$.
- **Formal Verification Specialist:** Implements and maintains Lean 4 specifications in `formal/ANSE/` to ensure mathematical proofs remain sound under `lake build` (see skill `anse-lean-prover`).

## 3. Required Development Commands
- **First, once per machine:** `uv sync --all-extras` (installs web, gateway, guard, sandbox and training extras plus the dev group; `antigravity_guard.py` needs them all to resolve imports).
- **Run Complete Tests:** `uv run pytest tests/`
- **Run Fast Performance Benchmarks:** `uv run pytest tests/performance/`
- **Run Multidisciplinary Benchmarks:** `uv run python -m scripts.run_phd_multidisciplinary_benchmark` (see skill `phd-multidisciplinary-benchmark`)
- **Run Antigravity Harness:** `uv run python -m antigravity_harness {audit,verify,test,dpo,qa}` (see skill `antigravity-harness`)
- **Compile Lean 4 Proofs:** `cd formal && lake build`
- **Check Repository Health:** `./restart.sh status`
- **Run the Evolution Lab:** `uv run python run_phase{1,2,3}_evolution.py` (see skill `anse-evolution-lab`)
- **Web interface:** `PORT=5000 uv run python web/server.py`, tab "Evolution Lab" and "Command Deck (ASCD)"

## 4. Measured Improvement Contract
Any claim that a phase "improved" must come from the phase's evolution runner: five use cases, a gate that can fail, results written to `results/phase{N}_evolution/results.json`. A failing gate is reported as a finding, never hidden or tuned away. Goals, numbers and limitations live in `docs/EVOLUTION_LAB.md`.

## 5. Two Agent Environments, One Repository
Antigravity (`.antigravity/`, `.agents/`, `memory.md`) and Claude Code (`.claude/`, `.mcp.json`, `CLAUDE.md`) share this repository and the same rules. Both start the same MCP guard server (`mcp_guard_server.py`). Branch `antigravity` is the integration branch for Antigravity-driven work.

## 6. Active Specifications
- `docs/specs/HARDENING_AND_GPU_POD.md`: security hardening (out-of-process Phase 1 harness, fail-closed sandbox, supply chain, result provenance, gates) and the remote RunPod GPU pod. Work packages WP1-WP7; read section 4 (guardrails) and section 5 (unverified assumptions) first.
