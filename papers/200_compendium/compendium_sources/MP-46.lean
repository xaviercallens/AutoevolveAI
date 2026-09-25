theorem problem_46_equipartition_kinetic_nonneg
    (kB T : ℝ) (hkB : 0 < kB) (hT : 0 ≤ T) :
    0 ≤ (1 / 2) * kB * T := by
  positivity