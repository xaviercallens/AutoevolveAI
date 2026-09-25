theorem problem_96_chandrasekhar_mass_limit
    (M M_ch : ℝ) (hM : M ≤ M_ch) :
    0 ≤ M_ch - M := by
  linarith