def meanFit (w₁ w₂ p : ℚ) : ℚ := p * w₁ + (1 - p) * w₂

def selectP (w₁ w₂ p : ℚ) : ℚ := p * w₁ / meanFit w₁ w₂ p

theorem aurelia_mean_fitness_increment (w₁ w₂ p : ℚ) (hm : meanFit w₁ w₂ p ≠ 0) :
    meanFit w₁ w₂ (selectP w₁ w₂ p) - meanFit w₁ w₂ p
      = p * (1 - p) * (w₁ - w₂) ^ 2 / meanFit w₁ w₂ p := -- proof elided

theorem kal_increment_is_variance (w₁ w₂ p : ℚ) :
    p * (1 - p) * (w₁ - w₂) ^ 2
      = p * (w₁ - meanFit w₁ w₂ p) ^ 2 + (1 - p) * (w₂ - meanFit w₁ w₂ p) ^ 2 := -- proof elided
