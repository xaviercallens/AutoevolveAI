theorem problem_35_heisenberg_uncertainty_bound
    {H : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H] (u v : H) :
    ‖@inner ℂ H _ u v‖ ≤ ‖u‖ * ‖v‖ :=
  norm_inner_le_norm u v