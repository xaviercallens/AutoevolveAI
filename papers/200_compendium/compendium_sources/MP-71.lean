theorem problem_71_landauer_erasure_heat
    (kB T : ℝ) (_hk : 0 < kB) (_hT : 0 < T) :
    0 < kB * T * Real.log 2 := by
  have h2 : 0 < Real.log 2 := Real.log_pos (by norm_num)
  positivity