theorem problem_53_ryu_takayanagi_area_positivity
    (Area G_N : ℝ) (hA : 0 ≤ Area) (hG : 0 < G_N) :
    0 ≤ Area / (4 * G_N) := by
  have : 0 < 4 * G_N := by positivity
  exact div_nonneg hA (le_of_lt this)