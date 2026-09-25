theorem problem_27_schrodinger_unitary_evolution
    {H : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
    (U : H ≃ₗᵢ[ℂ] H) (ψ₁ ψ₂ : H) :
    @inner ℂ H _ (U ψ₁) (U ψ₂) = @inner ℂ H _ ψ₁ ψ₂ ∧ ‖U ψ₁‖ = ‖ψ₁‖ := by
  exact ⟨LinearIsometryEquiv.inner_map_map U ψ₁ ψ₂, LinearIsometryEquiv.norm_map U ψ₁⟩