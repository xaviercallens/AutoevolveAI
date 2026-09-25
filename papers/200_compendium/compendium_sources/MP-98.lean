theorem problem_98_lieb_robinson_velocity_bound
    (v_LR t r : ℝ) (_hv : 0 < v_LR) (_ht : 0 ≤ t) (hr : v_LR * t < r) :
    0 < r - v_LR * t := by
  linarith