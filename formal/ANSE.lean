/-
  ANSE — Autopoietic Neuro-Symbolic Energy-based model
  Formal specification in Lean 4 + Mathlib4

  Module hierarchy:
    ANSE.Basic        — Energy functions, inference, loss taxonomy (Phase 1 verified)
    ANSE.JEPA         — World model, VICReg, training loss (Phase 2 verified)
    ANSE.System2      — Soft-token pondering (System 2 inference) (Phase 3)
    ANSE.Plasticity   — Surprise updates, EWC, sleep consolidation (Phase 4)
    ANSE.Autopoiesis  — Self-improvement fixed-point & safety (Phase 5)
    ANSE.Theorems     — Blueprint: all proof obligations
-/
import ANSE.Basic
import ANSE.JEPA
import ANSE.Performance
import ANSE.MicroML
import ANSE.Autopoiesis
import ANSE.StrongGravity
import ANSE.Ecosystem
