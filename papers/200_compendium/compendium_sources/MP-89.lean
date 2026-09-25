theorem problem_89_bethe_ansatz_total_momentum
    (k₁ k₂ theta₁₂ theta₂₁ : ℝ)
    (h_scatter : theta₁₂ + theta₂₁ = 0) :
    (k₁ + theta₁₂) + (k₂ + theta₂₁) = k₁ + k₂ := by
  linarith