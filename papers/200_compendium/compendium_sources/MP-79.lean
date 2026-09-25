theorem problem_79_polyakov_conformal_invariance
    (omega : ℝ) (g_det : ℝ) (hg : 0 < g_det) :
    0 < Real.exp (2 * omega) * g_det := by
  positivity