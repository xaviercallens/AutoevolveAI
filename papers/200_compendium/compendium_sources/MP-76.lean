theorem problem_76_callan_symanzik_asymptotic_freedom
    (beta_0 g : ℝ) (h_beta : 0 < beta_0) (hg : 0 < g) :
    -beta_0 * g ^ 3 < 0 := by
  have : 0 < beta_0 * g ^ 3 := by positivity
  linarith