theorem problem_6_dec_coboundary_algebraic_core
    (f₀ f₁ f₂ : ℝ) :
    let d0_01 := f₁ - f₀; let d0_12 := f₂ - f₁; let d0_20 := f₀ - f₂;
    let d1_curl := d0_01 + d0_12 + d0_20;
    d1_curl = 0 := by
  intro d0_01 d0_12 d0_20 d1_curl; dsimp; ring