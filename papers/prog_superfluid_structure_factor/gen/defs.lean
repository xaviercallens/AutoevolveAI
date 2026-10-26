def comm (A B : E →ₗ[ℂ] E) : E →ₗ[ℂ] E := A ∘ₗ B - B ∘ₗ A

noncomputable def excess (H : E →ₗ[ℂ] E) (E0 : ℝ) (ψ : E) (X : E →ₗ[ℂ] E) : ℂ :=
  ⟪X ψ, H (X ψ)⟫_ℂ - (E0 : ℂ) * ⟪X ψ, X ψ⟫_ℂ
