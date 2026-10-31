import Mathlib.Tactic

namespace BornM2T1

def quad (C : Fin 6 → Fin 6 → ℚ) (x : Fin 6 → ℚ) : ℚ := ∑ i, ∑ j, x i * C i j * x j

def Cfoot : Fin 6 → Fin 6 → ℚ := fun i j => (![![1/2, -1, 0, 0, 0, 0], ![-1, 1, 0, 0, 0, 0], ![0, 0, 1, 0, 0, 0],
  ![0, 0, 0, 1, 0, 0], ![0, 0, 0, 0, 1, 0], ![0, 0, 0, 0, 0, 1]] : Matrix (Fin 6) (Fin 6) ℚ) i j

-- TAMPERED: witness (1,0,...) gives x^T C x = 1/2 > 0, so the claim must be rejected by the kernel pipeline.
theorem tampered_witness : ∃ x : Fin 6 → ℚ, x ≠ 0 ∧ quad Cfoot x ≤ 0 := by
  refine ⟨![1, 0, 0, 0, 0, 0], ?_, ?_⟩
  · intro h
    have := congrFun h 0
    norm_num at this
  · simp [quad, Cfoot, Fin.sum_univ_succ]

end BornM2T1
