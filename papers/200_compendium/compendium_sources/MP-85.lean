theorem problem_85_laughlin_norm_nonneg
    {H : Type*} [NormedAddCommGroup H] [InnerProductSpace ℝ H]
    (Psi : H) :
    0 ≤ ⟪Psi, Psi⟫ :=
  real_inner_self_nonneg