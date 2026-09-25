theorem problem_97_jeans_instability_omega_sq
    (c_s k_J k : ℝ) (hk : k < k_J) (hc : 0 < c_s) (hk_pos : 0 ≤ k) :
    c_s ^ 2 * (k ^ 2 - k_J ^ 2) < 0 := by
  have h_sq : k ^ 2 < k_J ^ 2 := by
    have h_kj_pos : 0 < k_J := by linarith
    nlinarith
  have h_diff : k ^ 2 - k_J ^ 2 < 0 := by linarith
  have hc_sq : 0 < c_s ^ 2 := by positivity
  nlinarith