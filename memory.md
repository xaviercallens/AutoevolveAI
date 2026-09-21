# ANSE Repository Memory & State Ledger
**Version:** 0.3.0 + Evolution Lab (branch `antigravity`)  
**Repository:** `xaviercallens/AutoevolveAI`  
**Last Updated:** 2026-09-21  

---

## 1. Core Architecture & Philosophy

The **Autopoietic Neuro-Symbolic Energy-based model (ANSE)** rejects ungrounded next-token generation for autonomous reasoning. Instead, intelligence and self-evolution are grounded in the **deterministic physics of computation and neural network dynamics**:

- **Physical Energy Function ($E$)**:
  $$E(y, x) = w_t \cdot \text{Duration}(y, x) + w_m \cdot \text{Peak RAM}(y, x)$$
  Any execution failure, crash, syntax error, or timeout triggers an infinite energy barrier ($E_{\infty} = 10^6$), creating a steep optimization gradient ("Pain Signal") for System 2 Pondering.
- **Deterministic Sandbox Execution**:
  Two-tier isolation:
  - *Tier 1:* Subprocess execution with `/usr/bin/time -v` capturing exact resident set size (RSS) and wall-clock execution down to microseconds.
  - *Tier 2:* Docker container for network and filesystem isolation when untrusted imports are detected.
- **Autopoietic Thermodynamic Condition**:
  A child agent proposing architectural refactoring is granted process hot-swapping if and only if:
  $$\Delta E = E_{\text{child}} - E_{\text{parent}} < 0$$
  Formally verified via the Banach Fixed-Point Contraction Mapping Theorem.

---

## 2. Canonical Use Cases Summary

| # | Use Case | Domain | Energy / Penalty Formulation | Formal Verification (Lean 4) |
|---|---|---|---|---|
| **1** | **Algorithmic Performance Engineer** | Latency & Cache Physics | $E = \text{Duration (ms)} + \text{Peak RAM (MB)}$ | `ANSE.Performance` (Theorems P1–P5) |
| **2** | **Micro-ML Architect** | Neural Architecture Physics | $E = 1000$ (shape mismatch), $+1$ per param $>50\text{k}$, or $\mathcal{L}_{\text{val}}$ | `ANSE.MicroML` (Theorems M1–M3) |
| **3** | **Autopoietic Bootstrap** | Self-Referential Hot-Swap | $\Delta E = E_{\text{child}} - E_{\text{parent}} < 0$ | `ANSE.Autopoiesis` (Banach fixed point & hot-swap) |
| **4** | **Complexity Explorer** | Big-O Complexity ($O(N^2) \to O(N)$) | $O(N \times M)$ linear list scan $\to O(N + M)$ set lookup ($>9.5\times$ speedup) | `ANSE.Performance` (Theorem P6: `hash_lookup_energy_reduction`) |
| **5** | **Automata Physics** | State Explosion ($O(2^N) \to O(N)$) | Traps catastrophic backtracking, enforces timeout $E = 10^6$ | `ANSE.Performance` (Theorem P7: `catastrophic_backtracking_timeout_avoidance`) |

---

## 3. Engineering Guidelines & Known Gotchas

1. **Python Environment Management**:
   - `pyproject.toml` is PEP 621 since 2026-09-21. Run `uv sync --all-extras` once. (Before that date it was Poetry-only, and `uv sync` / `uv run` would have uninstalled all 115 packages including torch.)
   - Always run Python commands through `uv`:
     - `uv run pytest tests/`
     - `uv sync`
   - Zero third-party ML dependency drift: Synthetic datasets for architecture search must use pure PyTorch tensors (`torch.randn`). Do NOT reintroduce `scikit-learn` dependencies into `ml_sandbox.py`.
2. **Formal Verification in Lean 4**:
   - Root Lean entry point is [formal/ANSE.lean](file:///home/xavkal/xdev/AutoevolveAI/formal/ANSE.lean).
   - Build command: `cd formal && lake build`.
   - Mathlib4 deprecations: Use `ite_eq_left` / `ite_eq_right` instead of `if_pos` / `if_neg`.
   - Banach Contraction Mapping theorem requires `[Nonempty α]` instance hypothesis.
3. **Sandbox Timeouts & Backtracking**:
   - Default sandbox timeout is 10.0s.
   - For fast adversarial regression testing, configure `SandboxConfig(timeout_seconds=1.0)` to swiftly penalize exponential complexity without hanging test suites.
4. **Git & Releases**:
   - Pushes are direct to `main`.
   - Releases are tagged and published via GitHub CLI (`gh release create`).

---

## 4. Test Suite Reference

- **Total Test Count:** 195 tests across 7 test suites.
- **Key Modules:**
  - `tests/performance/test_algorithmic_benchmark.py`: 7 canonical algorithmic tasks.
  - `tests/performance/test_automata_and_complexity.py`: Complexity Explorer & Automata Physics.
  - `tests/phase2/test_ml_sandbox.py` & `test_ml_evaluator.py`: PyTorch module dimension & parameter limits.
  - `tests/autopoiesis/test_hypervisor.py`: Process hot-swapping and energy dominance gating.
  - `tests/phase1/` & `tests/phase2/`: End-to-end loops, JEPA world models, encoders, and harvesters.

---

## 5. Evolution Lab State (2026-09-21)

Measured with `qwen2.5-coder:1.5b` on CPU through Ollama. Details: `docs/EVOLUTION_LAB.md`, skill `anse-evolution-lab`.

| Phase | Gate | What the numbers say |
|---|---|---|
| 1 | 4 of 6 | Legacy self-graded loop: 4 of 11 claimed convergences were false. Verified pass@1 42.5% -> pass@3 52.5%. Adaptive retry and lesson memory did not help; both are opt-in and off. |
| 2 | 2 of 5 | JEPA does not beat a constant on MAE; AUC 0.606 vs 0.669 for a linear probe; candidate selection below random. |
| 3 | 5 of 5 | 5/5 correct children promoted, 5/5 wrong children rejected, 0/15 A/A false promotions, rollback exact, 2 of 4 LLM proposals promoted. |

Gotchas learned:
- Ollama 0.1.44 ignores `seed` and `temperature` on `/v1/chat/completions`; use `APIExtractor(ollama_native=True)`.
- Retries leak their label (a retry exists only because the previous attempt failed); score first attempts only.
- In-process test harnesses can be forged by code that reads its own source file; Phase 1 and 3 now use an out-of-process trusted driver (WP1 completed).
- Sandbox policy is now explicitly fail-closed (deny), enforcing a Docker container execution (Tier 2) for untrusted LLM-generated code (WP2 completed).
- `tests/phase3/test_neuro_surgeon.py` rewrites the tracked file `.antigravity_attestation` on every run.
- The loop returns the last attempt although energy often rises on retries; returning the best attempt is the next cheap win.
- Next focus: remote GPU pod (7B model, true hidden states instead of reply-text embeddings, LoRA/GRPO training).

---

## 6. Antigravity Harness Architecture (2026-09-21)

Fully implemented, documented (`docs/ANTIGRAVITY_HARNESS.md`), and tested (`tests/test_antigravity_harness.py`, 43 tests passing):
- **Package:** `antigravity-harness/` (aliased as `antigravity_harness`).
- **Sub-packages:**
  - `core`: `ContextOrchestrator` (Gemini 1M-2M context, AST skeletonizer, sliding window), `AntiStubGuard` (AST stubs, mock data, trivial constant returns, silent try-pass), `Lean4Verifier` (proof inventory, sorry auditor, lake runner).
  - `storage`: `RedisBus` (Streams, JSON traces, k-NN vector search with transparent in-memory mock fallback).
  - `agents`: `QAAgent` (adversarial edge cases & Hypothesis property testing), `OptimizerAgent` (computational physics $E$, vectorization opportunities, $\Delta E < 0$).
  - `tests_runner`: `UnitIntegrationRunner` (Pytest, JUnit XML), `VisualRegressionRunner` (Playwright & Pixelmatch HTML diff).
  - `rl_pipeline`: `TraceExtractor` (session reconstruction, time/energy filters), `DPODatasetBuilder` (chosen/rejected pair generation, TRL Chat DPO formatting).
- **CLI Commands:** `uv run python -m antigravity_harness {audit,verify,test,dpo,qa}`.
- **MCP Integration:** Native tools registered in `mcp_guard_server.py` (`audit_anti_stub`, `verify_lean4_soundness`, `generate_adversarial_qa_suite`, `build_dpo_preference_dataset`).
- **Quality Gate:** Hooked into `.antigravity/hooks/hardened_gate.py` and documented in `.agents/skills/antigravity-harness/SKILL.md`.
