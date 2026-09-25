theorem problem_74_tolman_temperature_constancy
    (T₁ T₂ g00_1 g00_2 : ℝ) (h_tolman : T₁ * Real.sqrt g00_1 = T₂ * Real.sqrt g00_2) :
    T₁ * Real.sqrt g00_1 - T₂ * Real.sqrt g00_2 = 0 := by
  linarith