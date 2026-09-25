theorem problem_73_bps_mass_bound
    (M Z : ℝ) (h_bps : |Z| ≤ M) :
    0 ≤ M - |Z| := by
  linarith