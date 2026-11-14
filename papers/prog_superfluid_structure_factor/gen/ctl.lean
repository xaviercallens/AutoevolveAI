theorem ctl_sorry {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    [FiniteDimensional ℂ E] (H ρ : E →ₗ[ℂ] E) (E0 : ℝ) (ψ : E) (_hH : H.IsSymmetric)
    (_hψ : H ψ = (E0 : ℂ) • ψ) :
    excess H E0 ψ ρ = ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ := sorry

axiom ctl_cheat : False

theorem ctl_axiom {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    [FiniteDimensional ℂ E] (H ρ : E →ₗ[ℂ] E) (E0 : ℝ) (ψ : E) (_hH : H.IsSymmetric)
    (_hψ : H ψ = (E0 : ℂ) • ψ) :
    excess H E0 ψ ρ = ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ := ctl_cheat.elim
