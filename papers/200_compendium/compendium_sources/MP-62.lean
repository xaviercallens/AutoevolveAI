theorem problem_62_casimir_force_positivity
    (hbar c d : ℝ) (hh : 0 < hbar) (hc : 0 < c) (hd : 0 < d) :
    0 < (Real.pi ^ 2 * hbar * c) / (240 * d ^ 4) := by
  have hpi : 0 < Real.pi := Real.pi_pos
  positivity