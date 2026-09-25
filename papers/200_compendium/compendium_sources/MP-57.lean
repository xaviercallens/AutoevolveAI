theorem problem_57_kdv_soliton_momentum_conservation
    {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    (u u_dot : E) (h_ortho : ⟪u, u_dot⟫ = 0) :
    2 * ⟪u, u_dot⟫ = 0 := by
  rw [h_ortho, mul_zero]