theorem problem_47_unruh_temperature_positivity
    (hbar a kB c : ℝ)
    (hh : 0 < hbar) (ha : 0 < a) (hk : 0 < kB) (hc : 0 < c) :
    0 < (hbar * a) / (2 * Real.pi * kB * c) := by
  have hpi : 0 < Real.pi := Real.pi_pos
  positivity