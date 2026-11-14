import Mathlib.Tactic

namespace BornM2

/-- Quadratic form x^T C x for a 6x6 rational matrix. -/
def quad (C : Fin 6 → Fin 6 → ℚ) (x : Fin 6 → ℚ) : ℚ := ∑ i, ∑ j, x i * C i j * x j

def Cfoot : Fin 6 → Fin 6 → ℚ := fun i j => (![![1/2, -1, 0, 0, 0, 0], ![-1, 1, 0, 0, 0, 0], ![0, 0, 1, 0, 0, 0],
  ![0, 0, 0, 1, 0, 0], ![0, 0, 0, 0, 1, 0], ![0, 0, 0, 0, 0, 1]] : Matrix (Fin 6) (Fin 6) ℚ) i j

theorem foot_witness : ∃ x : Fin 6 → ℚ, x ≠ 0 ∧ quad Cfoot x ≤ 0 := by
  refine ⟨![2, 1, 0, 0, 0, 0], ?_, ?_⟩
  · intro h
    have := congrFun h 0
    norm_num at this
  · simp [quad, Cfoot, Fin.sum_univ_succ]

def Cdia : Fin 6 → Fin 6 → ℚ := fun i j => (![![1079, 124, 124, 0, 0, 0], ![124, 1079, 124, 0, 0, 0], ![124, 124, 1079, 0, 0, 0],
  ![0, 0, 0, 578, 0, 0], ![0, 0, 0, 0, 578, 0], ![0, 0, 0, 0, 0, 578]] : Matrix (Fin 6) (Fin 6) ℚ) i j

theorem dia_pd (x : Fin 6 → ℚ) : 578 * ∑ i, x i ^ 2 ≤ quad Cdia x := by
  simp [quad, Cdia, Fin.sum_univ_succ]
  nlinarith [sq_nonneg (x 0), sq_nonneg (x 1), sq_nonneg (x 2), sq_nonneg (x 0 + x 1 + x 2),
    sq_nonneg (x 3), sq_nonneg (x 4), sq_nonneg (x 5)]

end BornM2

#print axioms BornM2.foot_witness
#print axioms BornM2.dia_pd
