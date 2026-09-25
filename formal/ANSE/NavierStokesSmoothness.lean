import Mathlib.Analysis.InnerProductSpace.PiL2

-- Définition stricte avec les notations Unicode natives de Lean 4
def is_bounded (u : ℝ → (Fin 3 → ℝ) → (Fin 3 → ℝ)) (M : ℝ) : Prop :=
  ∀ (t : ℝ) (x : Fin 3 → ℝ), ‖u t x‖ ≤ M
