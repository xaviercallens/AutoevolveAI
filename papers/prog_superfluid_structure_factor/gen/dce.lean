theorem double_comm_expect (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ) (ρ : E →ₗ[ℂ] E) :
    ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = excess H E0 ψ ρ + excess H E0 ψ (adjoint ρ) := by
  have h1 : ⟪ψ, adjoint ρ (H (ρ ψ))⟫_ℂ = ⟪ρ ψ, H (ρ ψ)⟫_ℂ := adjoint_inner_right ρ ψ _
  have h2 : ⟪ψ, adjoint ρ (ρ (H ψ))⟫_ℂ = (E0 : ℂ) * ⟪ρ ψ, ρ ψ⟫_ℂ := by
    rw [adjoint_inner_right, hψ, map_smul, inner_smul_right]
  have h3 : ⟪ψ, H (ρ (adjoint ρ ψ))⟫_ℂ = (E0 : ℂ) * ⟪adjoint ρ ψ, adjoint ρ ψ⟫_ℂ := by
    rw [inner_eig_H hH hψ, ← adjoint_inner_left ρ (adjoint ρ ψ) ψ]
  have h4 : ⟪ψ, ρ (H (adjoint ρ ψ))⟫_ℂ = ⟪adjoint ρ ψ, H (adjoint ρ ψ)⟫_ℂ :=
    (adjoint_inner_left ρ _ ψ).symm
  simp only [comm, LinearMap.sub_apply, LinearMap.comp_apply, map_sub, inner_sub_right]
  rw [h1, h2, h3, h4]
  unfold excess
  ring
