# ANSE Repository Memory & State Ledger
**Version:** 0.2.0  
**Repository:** `xaviercallens/AutoevolveAI`  
**Last Updated:** 2026-09-20  

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
