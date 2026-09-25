theorem problem_10_cauchy_schwarz_real
    {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E] (x y : E) :
    @inner ℝ E _ x y ≤ ‖x‖ * ‖y‖ := by
  exact real_inner_le_norm x y