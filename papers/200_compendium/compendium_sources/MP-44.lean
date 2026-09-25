theorem problem_44_larmor_power_nonneg
    (q a eps0 c : ℝ) (heps : 0 < eps0) (hc : 0 < c) :
    0 ≤ (q^2 * a^2) / (6 * Real.pi * eps0 * c^3) := by
  have hpi : 0 < Real.pi := Real.pi_pos
  have h_num : 0 ≤ q^2 * a^2 := mul_nonneg (sq_nonneg q) (sq_nonneg a)
  have h_den : 0 < 6 * Real.pi * eps0 * c^3 := by positivity
  exact div_nonneg h_num (le_of_lt h_den)