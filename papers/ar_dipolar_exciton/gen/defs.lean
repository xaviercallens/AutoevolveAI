noncomputable def g (d : ℝ) : ℝ → ℝ := fun t => 2 * (t ^ (-(1 / 2 : ℝ)) - (t + d ^ 2) ^ (-(1 / 2 : ℝ)))

noncomputable def h (d : ℝ) : ℝ → ℝ := fun t => t ^ (-(1 / 2 : ℝ)) - 2 * (t + d ^ 2) ^ (-(1 / 2 : ℝ))

noncomputable def shiftDiff (s c : ℝ) : ℝ → ℝ := fun t => t ^ (-(s / 2)) - (t + c) ^ (-(s / 2))
