import Mathlib.Tactic

namespace BornM2T2

def quad (C : Fin 6 → Fin 6 → ℚ) (x : Fin 6 → ℚ) : ℚ := ∑ i, ∑ j, x i * C i j * x j

def Cdia : Fin 6 → Fin 6 → ℚ := fun i j => (![![1079, 124, 124, 0, 0, 0], ![124, 1079, 124, 0, 0, 0], ![124, 124, 1079, 0, 0, 0],
  ![0, 0, 0, 578, 0, 0], ![0, 0, 0, 0, 578, 0], ![0, 0, 0, 0, 0, 578]] : Matrix (Fin 6) (Fin 6) ℚ) i j

-- TAMPERED: the lower bound 600 exceeds the smallest eigenvalue 578 (x = e_4 gives 578 < 600): must be rejected.
theorem tampered_pd (x : Fin 6 → ℚ) : 600 * ∑ i, x i ^ 2 ≤ quad Cdia x := by
  simp [quad, Cdia, Fin.sum_univ_succ]
  nlinarith [sq_nonneg (x 0), sq_nonneg (x 1), sq_nonneg (x 2), sq_nonneg (x 0 + x 1 + x 2),
    sq_nonneg (x 3), sq_nonneg (x 4), sq_nonneg (x 5)]

end BornM2T2
