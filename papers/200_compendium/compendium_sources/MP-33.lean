theorem problem_33_lorentz_force_orthogonality
    {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]
    (F : V →ₗ[ℝ] V) (h_skew : ∀ x y, ⟪F x, y⟫ = -⟪x, F y⟫) (u : V) :
    ⟪u, F u⟫ = (0 : ℝ) := by
  have h1 := h_skew u u
  have h2 : ⟪F u, u⟫ = ⟪u, F u⟫ := real_inner_comm u (F u)
  linarith