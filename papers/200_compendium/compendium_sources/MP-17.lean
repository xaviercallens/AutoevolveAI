theorem problem_17_am_gm_2 (x y : ℝ) (hx : 0 ≤ x) (hy : 0 ≤ y) : 
    Real.sqrt (x * y) ≤ (x + y) / 2 := by
  have h : 0 ≤ (Real.sqrt x - Real.sqrt y) ^ 2 := sq_nonneg (Real.sqrt x - Real.sqrt y)
  have h_exp : (Real.sqrt x - Real.sqrt y) ^ 2 = (Real.sqrt x)^2 - 2 * (Real.sqrt x * Real.sqrt y) + (Real.sqrt y)^2 := by ring
  rw [Real.sq_sqrt hx, Real.sq_sqrt hy] at h_exp
  have h_mul : Real.sqrt x * Real.sqrt y = Real.sqrt (x * y) := by rw [Real.sqrt_mul hx]
  rw [h_mul] at h_exp
  linarith