theorem problem_70_spectral_density_positivity
    (rho_0 delta_rho : ℝ) (_h0 : 0 ≤ rho_0) (h_bound : -rho_0 ≤ delta_rho) :
    0 ≤ rho_0 + delta_rho := by
  linarith