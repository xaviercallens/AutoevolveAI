import Mathlib.Tactic

namespace BornM2T3

def quad (C : Fin 6 → Fin 6 → ℚ) (x : Fin 6 → ℚ) : ℚ := ∑ i, ∑ j, x i * C i j * x j

def Cdia : Fin 6 → Fin 6 → ℚ := fun i j => (![![1079, 124, 124, 0, 0, 0], ![124, 1079, 124, 0, 0, 0], ![124, 124, 1079, 0, 0, 0],
  ![0, 0, 0, 578, 0, 0], ![0, 0, 0, 0, 578, 0], ![0, 0, 0, 0, 0, 578]] : Matrix (Fin 6) (Fin 6) ℚ) i j

-- TAMPERED LDL^T-style identity: first pivot altered (1079 -> 1078); identity is false and must be rejected.
theorem tampered_ldl (x : Fin 6 → ℚ) : quad Cdia x =
    1078 * (x 0 + x 1 * (124 / 1079) + x 2 * (124 / 1079)) ^ 2 + 578 * (x 3) ^ 2 + 578 * (x 4) ^ 2 + 578 * (x 5) ^ 2 := by
  simp only [quad, Cdia, Fin.sum_univ_succ, Fin.sum_univ_zero]
  norm_num
  ring

end BornM2T3
