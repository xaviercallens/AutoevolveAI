theorem problem_69_anderson_localization_decay
    (C _xi _r : ℝ) (hC : 0 ≤ C) (_hxi : 0 < _xi) (_hr : 0 ≤ _r) :
    0 ≤ C * Real.exp (-_r / _xi) := by
  positivity