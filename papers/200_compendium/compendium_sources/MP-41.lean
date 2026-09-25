theorem problem_41_friedmann_flat_expansion_nonneg
    (G rho : ℝ) (hG : 0 < G) (hrho : 0 ≤ rho) :
    0 ≤ (8 * Real.pi * G / 3) * rho := by
  have : 0 ≤ 8 * Real.pi * G / 3 := by { have hpi : 0 < Real.pi := Real.pi_pos; positivity }
  exact mul_nonneg this hrho