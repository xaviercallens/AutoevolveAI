theorem problem_64_bohmian_kinetic_positivity
    (m v : ℝ) (_hm : 0 < m) :
    0 ≤ (1 / 2 : ℝ) * m * v ^ 2 := by
  positivity