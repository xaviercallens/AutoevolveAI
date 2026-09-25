theorem problem_59_onsager_reciprocal_symmetry
    {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]
    (L : V →ₗ[ℝ] V) (h_symm : ∀ x y, ⟪L x, y⟫ = ⟪x, L y⟫) (x y : V) :
    ⟪L x, y⟫ - ⟪x, L y⟫ = 0 := by
  rw [h_symm x y, sub_self]