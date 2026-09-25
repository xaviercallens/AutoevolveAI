theorem problem_48_hawking_temperature_positivity
    (hbar c G M kB : ℝ)
    (hh : 0 < hbar) (hc : 0 < c) (hG : 0 < G) (hM : 0 < M) (hk : 0 < kB) :
    0 < (hbar * c^3) / (8 * Real.pi * G * M * kB) := by
  have hpi : 0 < Real.pi := Real.pi_pos
  positivity