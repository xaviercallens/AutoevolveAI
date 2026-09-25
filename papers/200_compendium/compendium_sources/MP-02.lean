theorem problem_2_parallelogram_law
    {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E] (x y : E) :
    ‖x + y‖ ^ 2 + ‖x - y‖ ^ 2 = 2 * (‖x‖ ^ 2 + ‖y‖ ^ 2) := by
  exact parallelogram_law_with_norm ℝ x y