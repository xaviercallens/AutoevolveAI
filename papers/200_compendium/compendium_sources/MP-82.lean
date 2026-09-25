theorem problem_82_poiseuille_velocity_centerline
    (r R v_max : ℝ) (hr : 0 ≤ r) (hR : r ≤ R) (hR_pos : 0 < R) (hv : 0 ≤ v_max) :
    0 ≤ v_max * (1 - (r / R) ^ 2) := by
  have h_ratio : (r / R) ^ 2 ≤ 1 := by
    have h1 : 0 ≤ r / R := div_nonneg hr (le_of_lt hR_pos)
    have h2 : r / R ≤ 1 := (div_le_one hR_pos).mpr hR
    nlinarith
  have h_diff : 0 ≤ 1 - (r / R) ^ 2 := by linarith
  exact mul_nonneg hv h_diff