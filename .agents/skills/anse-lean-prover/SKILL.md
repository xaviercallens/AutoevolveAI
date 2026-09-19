---
name: anse-lean-prover
description: >-
  Maintain, compile, and develop formal Lean 4 theorems and specifications for ANSE
  energy monotonicity, parameter constraints, and autopoietic Banach fixed-point hot-swapping.
  Use this skill whenever modifying Lean files or verifying mathematical proof soundness.
---

# ANSE Lean 4 Formal Prover Skill

This skill guides the agent in editing and verifying formal mathematical proofs for ANSE in Lean 4 (`v4.34.0-rc2` + Mathlib4).

## 1. Directory Structure

```
formal/
├── lakefile.lean        # Lake build configuration
├── lean-toolchain       # Toolchain pin: v4.34.0-rc2
└── ANSE/
    ├── Basic.lean       # Core definitions, states, metrics
    ├── JEPA.lean        # World model & representation invariants
    ├── Performance.lean # Computational physics, vectorization, hash tables, backtracking
    ├── MicroML.lean     # Neural parameter limits and dimension barriers
    └── Autopoiesis.lean # Banach fixed point & thermodynamic hot-swap validity
```

## 2. Compilation & Verification Commands

To compile the entire Lean 4 formalization:
```bash
cd formal
lake build
```

Verify that all 2,491 proof jobs compile without errors.

## 3. Proof Guidelines & Conventions

1. **Mathlib4 Rewrite Deprecations**:
   - Do NOT use `split_ifs` as it can be brittle under modern Lean 4 elaboration.
   - Use `rw [ite_eq_left]` or `rw [ite_eq_right]` to simplify conditionally branched expressions.
2. **Fixed-Point Hypotheses**:
   - The Banach Fixed-Point theorem (`ContractingWith.exists_fixed_point`) requires `[Nonempty α]`. Always supply a nonempty instance or hypothesis for the state space.
3. **Monotonicity Theorems**:
   - Linear arithmetic proofs should use `linarith` and `ring`.
   - Inequality chaining should use `calc` blocks for clarity and maintainability.
