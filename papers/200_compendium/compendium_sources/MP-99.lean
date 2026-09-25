theorem problem_99_conformal_bootstrap_crossing
    (s t u_mandelstam : ℝ) (M : ℝ)
    (h_mandelstam : s + t + u_mandelstam = 4 * M ^ 2)
    (h_symmetric : s = t) :
    2 * s + u_mandelstam = 4 * M ^ 2 := by
  linarith