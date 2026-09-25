theorem problem_66_fluctuation_dissipation_positivity
    (kB T gamma : ℝ) (_hk : 0 < kB) (_hT : 0 < T) (hg : 0 ≤ gamma) :
    0 ≤ 2 * kB * T * gamma := by
  positivity