theorem problem_68_carter_constant_conservation
    {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]
    (u : V) (T_op : V →L[ℝ] V)
    (h_skew : ⟪u, T_op u⟫ = -⟪u, T_op u⟫) :
    ⟪u, T_op u⟫ = (0 : ℝ) := by
  linarith