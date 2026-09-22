---
name: phd-multidisciplinary-benchmark
description: Parallel execution, formal verification, and RL distillation for 30 PhD-level multidisciplinary benchmarks across Rust numerical computing, pure mathematics, and theoretical physics.
---

# PhD Multidisciplinary Benchmark Skill

This skill governs the parallel orchestration, sandbox compilation, mathematical verification, and RL post-processing across three frontier technical domains:
1. **10 Rust Numerical Computing Kernels** (SIMD matrix multiplication, Cooley-Tukey FFT, RKF45, LU decomposition, Monte Carlo option pricer, KD-Tree, Graham Scan, PCG solver, SpMV, BFGS).
2. **10 Pure Mathematics Formal Problems** (Fundamental group $\pi_1$, Riemann curvature tensor, Residue theorem, Galois group solvability, Hilbert spectral decomposition, Riemann zeta functional equation, Radon-Nikodym derivative, Symplectic 2-form Darboux theorem, Itô's lemma, Yoneda lemma).
3. **10 Pure Physics Theory Problems** (QED Ward-Takahashi identity, Raychaudhuri singularity congruence, Onsager reciprocal relations, Landau damping, Calabi-Cardy entanglement entropy, Laughlin fractional Hall state, KAM theorem, CKM matrix unitarity, Hawking radiation, Onsager's 1/3 turbulence conjecture).

---

## 1. Operational Invariants

1. **Dual Verification Rule:**
   - Rust code must compile natively with `rustc -O` and execute in under $50\text{ ms}$.
   - Mathematical and theoretical physics problems must evaluate through verified symbolic & numerical CAS engines (SymPy, NumPy, SciPy) and assert formal invariants $\mathcal{I}(s) = 0$.
2. **Parallel Execution Architecture:**
   - All 30 benchmarks execute concurrently via `ThreadPoolExecutor` or `ProcessPoolExecutor` to profile throughput and physical latency in parallel.
3. **Zero-Hallucination Numeric Enforcement:**
   - Freehand floating-point calculation by LLMs is strictly prohibited. Numbers must be derived from code execution receipts.
4. **Reinforcement Learning (DPO & GRPO) Pipeline:**
   - Every benchmark produces a chosen candidate ($E < 50$, zero stubs, valid invariant) and a rejected candidate (unoptimized, higher latency or invariant drift).
   - Trajectories are committed to Redis LTM (`antigravity:subtasks:*`, `antigravity:dpo:*`) and exported to JSONL for policy fine-tuning.

---

## 2. Command Reference

```bash
# Run all 30 benchmarks in parallel with real compilation and CAS execution
uv run python -m scripts.run_phd_multidisciplinary_benchmark

# Extract DPO preference pairs for TRL fine-tuning
uv run python -m scripts.extract_multidisciplinary_dpo

# Audit workspace with AntiStubGuard
uv run python -m antigravity_harness audit anse/benchmark/
```
