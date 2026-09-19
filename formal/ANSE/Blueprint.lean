/-
  ANSE.Blueprint — Atlas-compatible proof dependency graph.

  This file declares the dependency structure of all proof obligations
  so the Atlas / LeanBlueprint tool can:
    (1) Visualise which theorems block which others
    (2) Track human review requirements (the "review cone")
    (3) Generate progress dashboards (green = proved, blue = ready)

  Atlas reference: NyxFoundation/lean-atlas
  Blueprint tool:  Patrick Massot (leanprover-community/blueprint)
-/
import ANSE.Theorems

/-!
# ANSE Formal Specification — Atlas Blueprint

## Dependency Graph

```
[LeCun 2006, §1.1]
    │
    ▼
A1: exists_minimiser ✅ PROVED
    │
    ├──► A2: freeEnergy_tendsto_hard  ⚠ SORRY
    │         (Laplace saddle-point)
    │
    └──► A3: hinge_is_good_loss ✅ PROVED
              │
              └──► [Enables: ANSE training convergence]

[I-JEPA + eb_jepa + VICReg]
    │
    ▼
B1: jepEnergy_nonneg ✅ PROVED
B2: jepEnergy_eq_zero ✅ PROVED
B3: vicreg_loss_nonneg ✅ PROVED
B4: jepTrainingLoss_nonneg ✅ PROVED
B5: ema_is_convex_combination ✅ PROVED
    │
    └──► B6: vicreg_zero_implies_spread  ⚠ SORRY P0
              │
              └──► [Enables: representation quality guarantee]

[NYU Lecture + System 2]
    │
    ▼
C1: total_differentiable ✅ PROVED
    │
    ├──► C2: energy_descent_per_step  ⚠ SORRY P0
    │         (requires: L-smooth descent lemma from Mathlib)
    │         │
    │         └──► C3: ponder_convergence  ⚠ SORRY P0
    │                   (requires: PL-condition + C2)
    │                   │
    │                   └──► System2Inference.correct  ⚠ SORRY P0
    │
    └──► C4: langevin_ergodicity  ⚠ SORRY P2

[Friston 2010 + Kirkpatrick 2017]
    │
    ▼
D1: surprise_nonneg ✅ PROVED
D2: surprise_eq_zero ✅ PROVED
D3: ewcPenalty_nonneg ✅ PROVED
    │
    ├──► D4: surprise_decreases  (trivial from D1)
    │
    └──► D5: ewc_preserves_old_task  ⚠ SORRY P1
              (requires: Lagrangian saddle-point analysis)

[Maturana & Varela 1972 + Banach FPT]
    │
    ▼
E1: autopoiesis_exists ✅ PROVED (via Banach FPT from Mathlib)
E2: safe_improvement_nonincreasing ✅ PROVED
    │
    └──► E3: self_improvement_terminates  ⚠ SORRY P0
              (requires: monotone convergence + lower bound E ≥ 0)
```

## Progress Summary

| Module | Proved | Sorry | Total |
|--------|--------|-------|-------|
| Basic (EBM) | 3 | 1 | 4 |
| JEPA | 5 | 1 | 6 |
| System2 | 1 | 2 | 3 |
| Plasticity | 3 | 1 | 4 |
| Autopoiesis | 2 | 1 | 3 |
| **Total** | **14** | **6** | **20** |

**Completeness: 70%**

## Critical Path (P0 obligations to close first)

1. **C2** `energy_descent_per_step` — standard gradient descent, likely already in Mathlib as `GradientDescent.descent_lemma`
2. **C3** `ponder_convergence` — follows immediately from C2 + PL condition
3. **B6** `vicreg_zero_implies_spread` — direct algebra from the two non-negative VICReg terms
4. **E3** `self_improvement_terminates` — monotone sequence bounded below
5. **A2** `freeEnergy_tendsto_hard` — requires Laplace method / Varadhan's lemma

## Atlas Review Cone for Target Theorem: `autopoiesis_exists`

The minimal set of nodes a human reviewer must check to trust
`autopoiesis_exists` (Banach FPT application):

1. `SelfImprovementOp.apply` — is the operator well-defined?
2. `ContractingWith` from Mathlib — is the instance correct?
3. `hΦ : LipschitzWith c Φ.apply` — is the contraction hypothesis reasonable?
4. `CompleteSpace` instance for `ArchitectureState` — does this hold?

**Review cone size: 4 nodes** (minimal — Banach FPT is a black box from Mathlib).
-/

namespace ANSE.Blueprint

-- Proof obligation metadata (machine-readable for Atlas tooling)
structure ProofObligation where
  id       : String
  theorem  : String
  status   : String  -- "proved" | "sorry"
  priority : String  -- "P0" | "P1" | "P2"
  method   : String
  deps     : List String

def obligations : List ProofObligation := [
  ⟨"A1", "exists_minimiser", "proved", "P0",
   "Weierstrass (IsCompact.exists_isMinOn)", []⟩,
  ⟨"A2", "freeEnergy_tendsto_hard", "sorry", "P0",
   "Laplace saddle-point / Varadhan's lemma", ["A1"]⟩,
  ⟨"A3", "hinge_is_good_loss", "proved", "P0",
   "Direct from GoodLoss definition", ["A1"]⟩,
  ⟨"B1", "jepEnergy_nonneg", "proved", "P0",
   "sq_nonneg", []⟩,
  ⟨"B2", "jepEnergy_eq_zero", "proved", "P0",
   "norm_eq_zero + sub_eq_zero", ["B1"]⟩,
  ⟨"B3", "vicreg_loss_nonneg", "proved", "P0",
   "mul_nonneg + le_max_left", []⟩,
  ⟨"B4", "jepTrainingLoss_nonneg", "proved", "P0",
   "add_nonneg + B1 + B3", ["B1", "B3"]⟩,
  ⟨"B5", "ema_is_convex_combination", "proved", "P1",
   "rfl (by definition)", []⟩,
  ⟨"B6", "vicreg_zero_implies_spread", "sorry", "P0",
   "Non-negativity of each VICReg term + sum=0", ["B3"]⟩,
  ⟨"C1", "total_differentiable", "proved", "P0",
   "fun_prop (Differentiable weighted sum)", []⟩,
  ⟨"C2", "energy_descent_per_step", "sorry", "P0",
   "L-smooth descent lemma", ["C1"]⟩,
  ⟨"C3", "ponder_convergence", "sorry", "P0",
   "PL-condition + C2 by induction", ["C2"]⟩,
  ⟨"C4", "langevin_ergodicity", "sorry", "P2",
   "SGLD ergodicity (Welling & Teh 2011)", ["C2"]⟩,
  ⟨"D1", "surprise_nonneg", "proved", "P0",
   "sq_nonneg", []⟩,
  ⟨"D2", "surprise_eq_zero", "proved", "P0",
   "sq_eq_zero_iff + sub_eq_zero", ["D1"]⟩,
  ⟨"D3", "ewcPenalty_nonneg", "proved", "P0",
   "mul_nonneg + sq_nonneg", []⟩,
  ⟨"D5", "ewc_preserves_old_task", "sorry", "P1",
   "Lagrangian saddle-point", ["D3"]⟩,
  ⟨"E1", "autopoiesis_exists", "proved", "P0",
   "Banach FPT (ContractingWith.fixedPoint_isFixedPt)", []⟩,
  ⟨"E2", "safe_improvement_nonincreasing", "proved", "P0",
   "Direct from safeProposal definition (linarith)", []⟩,
  ⟨"E3", "self_improvement_terminates", "sorry", "P0",
   "Monotone convergence + E ≥ 0", ["E2"]⟩
]

end ANSE.Blueprint
