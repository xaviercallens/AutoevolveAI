theorem problem_39_incompressible_solenoidal_flow
    {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    (u grad_phi : E) (h_ortho : ⟪u, grad_phi⟫ = (0 : ℝ)) :
    ⟪u + grad_phi, u + grad_phi⟫ = ⟪u, u⟫ + ⟪grad_phi, grad_phi⟫ := by
  rw [inner_add_left, inner_add_right, inner_add_right]
  have h_ortho2 : ⟪grad_phi, u⟫ = (0 : ℝ) := by
    rw [real_inner_comm, h_ortho]
  rw [h_ortho, h_ortho2]
  ring