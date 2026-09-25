theorem problem_38_stefan_boltzmann_monotonicity
    (sigma T₁ T₂ : ℝ) (h_sigma : 0 ≤ sigma) (h_nonneg : 0 ≤ T₁) (h_le : T₁ ≤ T₂) :
    sigma * T₁ ^ 4 ≤ sigma * T₂ ^ 4 := by
  have h_pow : T₁ ^ 4 ≤ T₂ ^ 4 := pow_le_pow_left₀ h_nonneg h_le 4
  exact mul_le_mul_of_nonneg_left h_pow h_sigma