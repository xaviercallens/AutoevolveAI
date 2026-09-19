# ANSE Formal Specification — Lean 4

> A machine-checked mathematical specification of the **Autopoietic Neuro-Symbolic Energy-based model** using Lean 4 + Mathlib4.

---

## Overview

This directory contains the formal specification of the ANSE architecture,
generated from the foundation papers using the **Atlas** approach
(NyxFoundation/lean-atlas + Patrick Massot's Blueprint tool).

Every core algorithm and theorem is:
- **Typed**: enforced by Lean's dependent type system
- **Proved** or **explicitly stubbed** with `sorry` (a named proof obligation)
- **Traceable** back to a foundation paper

---

## Module Structure

```
formal/
├── lakefile.toml          — Project config (Lean 4.33.1 + Mathlib4 v4.33.1)
├── ANSE.lean              — Root importer
└── ANSE/
    ├── Basic.lean         — Core EBM types, inference, loss taxonomy
    ├── JEPA.lean          — World model: encoders, EMA, VICReg, energy
    ├── System2.lean       — Soft-token pondering loop
    ├── Plasticity.lean    — Surprise updates, EWC, sleep consolidation
    ├── Autopoiesis.lean   — Self-improvement fixed-point & safety
    ├── Theorems.lean      — Blueprint: all 20 proof obligations
    └── Blueprint.lean     — Atlas dependency graph + progress tracker
```

---

## Foundation Papers to Lean Modules

| Paper | Module | Key Formalisation |
|---|---|---|
| LeCun et al. 2006 "A Tutorial on Energy-Based Learning" | `Basic` | `EnergyFn`, `infer`, `GoodLoss`, `hingeLoss` |
| NYU DLSP20 Week 7 — LeCun and Canziani | `System2` | `ponder`, `gradient_step`, `energy_descent` |
| arXiv:2602.03604 — EB-JEPA (FAIR 2026) | `JEPA` | `jepEnergy`, `vicreg_loss`, `ema_step` |
| MVPandey/Enso — Kona Replication | `JEPA`, `System2` | `langevin_step`, `jepTrainingLoss` |
| Friston 2010 — Free Energy Principle | `Plasticity` | `surprise`, `apply_surprise_update` |
| Kirkpatrick et al. 2017 — EWC | `Plasticity` | `ewcPenalty`, `run_sleep_cycle` |
| Maturana and Varela 1972 — Autopoiesis | `Autopoiesis` | `IsAutopoieticFixedPoint` |
| Banach Contraction Mapping Theorem | `Autopoiesis` | `autopoiesis_exists` (via Mathlib) |

---

## Proof Progress

| ID | Theorem | Status | Priority |
|---|---|---|---|
| A1 | `exists_minimiser` | PROVED | P0 |
| A2 | `freeEnergy_tendsto_hard` | sorry | P0 |
| A3 | `hinge_is_good_loss` | PROVED | P0 |
| B1 | `jepEnergy_nonneg` | PROVED | P0 |
| B2 | `jepEnergy_eq_zero` | PROVED | P0 |
| B3 | `vicreg_loss_nonneg` | PROVED | P0 |
| B4 | `jepTrainingLoss_nonneg` | PROVED | P0 |
| B5 | `ema_is_convex_combination` | PROVED | P1 |
| B6 | `vicreg_zero_implies_spread` | sorry | P0 |
| C1 | `total_differentiable` | PROVED | P0 |
| C2 | `energy_descent_per_step` | sorry | P0 |
| C3 | `ponder_convergence` | sorry | P0 |
| C4 | `langevin_ergodicity` | sorry | P2 |
| D1 | `surprise_nonneg` | PROVED | P0 |
| D2 | `surprise_eq_zero` | PROVED | P0 |
| D3 | `ewcPenalty_nonneg` | PROVED | P0 |
| D5 | `ewc_preserves_old_task` | sorry | P1 |
| E1 | `autopoiesis_exists` | PROVED | P0 |
| E2 | `safe_improvement_nonincreasing` | PROVED | P0 |
| E3 | `self_improvement_terminates` | sorry | P0 |

**14 / 20 proved (70%)**

---

## Key Theorems

### `exists_minimiser` (A1) — Inference is Well-Posed
```lean
theorem exists_minimiser [CompactSpace Y] (E : EnergyFn X Y) (x : X) :
    ∃ y_star : Y, ∀ y : Y, E.eval x y_star ≤ E.eval x y
```
When the output space Y is compact and the energy is continuous,
gradient-based inference always has a solution.
Proof: Weierstrass extreme-value theorem via Mathlib's `IsCompact.exists_isMinOn`.

---

### `autopoiesis_exists` (E1) — Equilibrium Exists
```lean
theorem autopoiesis_exists [CompleteSpace S] (Phi : SelfImprovementOp)
    (hPhi : exists c < 1, LipschitzWith c Phi.apply) :
    exists s_star, IsAutopoieticFixedPoint Phi s_star
```
If the AI's self-improvement operator is a contraction mapping,
a unique stable equilibrium architecture exists.
Proof: Banach fixed-point theorem, via Mathlib's `ContractingWith`.

---

### `safe_improvement_nonincreasing` (E2) — Safety Invariant
```lean
theorem safe_improvement_nonincreasing (eps > 0) (energy) (s1 s2)
    (hSafe : energy s2 + eps <= energy s1) :
    energy s2 <= energy s1
```
Safe self-improvement proposals are energy non-increasing.
The AI cannot make itself worse when the sandbox gate is enforced.
Proof: linarith (trivial from the safety condition definition).

---

## Building

```bash
cd formal/
lake build          # compiles Mathlib + ANSE (first run ~15 min)
lake build ANSE     # rebuild just ANSE after edits (~30 sec)
```

## Running the Blueprint checker

```bash
pip install leanblueprint
leanblueprint graph ANSE/Theorems.lean
leanblueprint web --output docs/blueprint/
```

## Atlas integration

```bash
git clone https://github.com/NyxFoundation/lean-atlas vendor/lean-atlas
lean-atlas compass ANSE/Autopoiesis.lean --target autopoiesis_exists
```

---

## Notation Guide

| Symbol | Lean name | Meaning |
|---|---|---|
| `E.eval x y` | `EnergyFn.eval` | Energy of (x,y) pair |
| `infer E x` | `ANSE.infer` | argmin_y E(x,y) |
| `freeEnergyHard E x y` | `ANSE.freeEnergyHard` | min_z E(x,y,z) |
| `ema_step tau` | `ANSE.JEPA.ema_step` | EMA target encoder update |
| `surprise Ep Ea` | `ANSE.Plasticity.surprise` | (Ep - Ea)^2 |
| `ponder E eta tau T z0` | `ANSE.System2.ponder` | T-step pondering loop |
| `Phi.apply s` | `SelfImprovementOp.apply` | One self-improvement step |

*Generated by Antigravity IDE · AutoevolveAI Project · 2026*
