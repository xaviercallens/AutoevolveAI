---
name: antigravity-harness
description: Autonomous Neuro-Symbolic Execution & Hardening Harness for Antigravity CLI. Enforces anti-stub AST validation, Lean 4 formal proof verification, Gemini large-window context orchestration, computational physics profiling, and DPO RL pipeline.
---

# Antigravity Harness: Autonomous Neuro-Symbolic Execution & Hardening

The **Antigravity Harness** (`antigravity-harness/` or `python -m antigravity_harness`) provides a zero-trust verification and execution architecture designed for autonomous agents operating under the physical computation model of ANSE.

---

## 1. Quick CLI Commands

Run directly inside the repository via `uv run python -m antigravity_harness <command>`:

| Command | Action | Key Verification Invariant |
|---|---|---|
| `uv run python -m antigravity_harness audit <path>` | Audits files/dirs against stubs & mock artifacts | Fails with penalty $E = 10^6$ on `pass`, `...`, `mock_*`, or `time.sleep` |
| `uv run python -m antigravity_harness verify --formal-dir formal` | Audits Lean 4 mathematical proofs | Fails if ungrounded `sorry` or unchecked axioms exist |
| `uv run python -m antigravity_harness test [path]` | Executes test runner with structured telemetry | Captures execution duration, pass/fail metrics & traces |
| `uv run python -m antigravity_harness qa <file.py> --module <path>` | Synthesizes adversarial and property tests | Exposes null handling, numeric boundary traps, and stress scale |
| `uv run python -m antigravity_harness dpo --output results/dpo.jsonl` | Generates DPO preference pairs | Assembles chosen (low $E$, zero stub) vs rejected (stubs, high $E$) pairs |

---

## 2. Core Architecture

```
antigravity-harness/
├── core/
│   ├── context_orchestrator.py   # Gemini 1M-2M context manager, AST skeletonizer, .scratchpad/ offload
│   ├── anti_stub_guard.py        # AST analyzer: blocks pass, ..., fake_*, and constant returns
│   └── lean4_verifier.py         # Lake / Lean 4 formal proof verification interface
├── storage/
│   └── redis_bus.py              # Redis Streams, JSON trace documents & Vector Store
├── agents/
│   ├── qa_agent.py               # Adversarial test generator (null, overflow, catastrophic regex)
│   └── optimizer_agent.py        # Physics profiling: E = w_t·ms + w_m·RAM, verifies Delta E < 0
├── tests_runner/
│   ├── unit_integration.py       # Pytest & containerized execution runner with JUnit XML
│   └── visual_regression.py      # Playwright + Pixelmatch runner for UI & Evolution Lab dashboard
└── rl_pipeline/
    ├── trace_extractor.py        # Reconstructs multi-turn session trajectories from Redis
    └── dpo_dataset_builder.py    # Generates chosen/rejected pairs for TRL / DPOTrainer
```

---

## 3. Operational Protocols for Antigravity Agents

### Protocol A: Pre-Commit Implementation Audit
Before proposing any code change or claiming task completion:
```bash
uv run python -m antigravity_harness audit <modified_file.py>
```
If violations are detected, refactor the code to eliminate stubs and fake mock objects before submitting.

### Protocol B: Mathematical Verification (Lean 4)
When modifying formal specifications in `formal/ANSE/`:
```bash
uv run python -m antigravity_harness verify --formal-dir formal
```
Ensure that no `sorry` tokens or unverified axioms are introduced.

### Protocol C: Physics of Computation Optimization
When refactoring an algorithm or neural module:
1. Profile baseline vs candidate:
   ```python
   from antigravity_harness.agents import OptimizerAgent
   opt = OptimizerAgent()
   proposal = opt.compare_and_evaluate(baseline_fn, candidate_fn, candidate_source, test_inputs)
   assert proposal.is_thermodynamically_favorable, "Delta E >= 0: rejected"
   ```
2. Confirm that duration and peak RAM satisfy $\Delta E < 0$.

### Protocol D: DPO Alignment Pipeline
To export recorded agent trajectories into fine-tuning datasets:
```bash
uv run python -m antigravity_harness dpo --output results/dpo_dataset.jsonl
```
Creates pairs formatted for Hugging Face `TRL` DPOTrainer.
