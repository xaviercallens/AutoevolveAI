theorem problem_86_gross_pitaevskii_energy_nonneg
    (E_kin E_int : ℝ) (hk : 0 ≤ E_kin) (hi : 0 ≤ E_int) :
    0 ≤ E_kin + E_int := by
  linarith