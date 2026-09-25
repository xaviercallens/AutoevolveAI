theorem problem_11_ivt (f : ℝ → ℝ) (a b y : ℝ) (hab : a ≤ b) 
    (hf : ContinuousOn f (Icc a b)) (hy : f a ≤ y ∧ y ≤ f b) : 
    ∃ x ∈ Icc a b, f x = y := by
  have h_sub := intermediate_value_Icc hab hf
  have hy_icc : y ∈ Icc (f a) (f b) := hy
  rcases h_sub hy_icc with ⟨x, hx, hfx⟩
  exact ⟨x, hx, hfx⟩