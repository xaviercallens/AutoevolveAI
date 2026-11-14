theorem symmetry_needed {e0 e1 : E} (h0 : ‖e0‖ = 1) (h1 : ‖e1‖ = 1) (h01 : ⟪e0, e1⟫_ℂ = 0) :
    (ketBra e1 e1).IsSymmetric ∧ ketBra e1 e1 e0 = ((0 : ℝ) : ℂ) • e0 ∧
    ⟪e0, comm (adjoint (ketBra e1 e0)) (comm (ketBra e1 e1) (ketBra e1 e0)) e0⟫_ℂ = 1 ∧
    excess (ketBra e1 e1) 0 e0 (ketBra e1 e0) = 1 ∧
    excess (ketBra e1 e1) 0 e0 (ketBra e1 e0) ≠
      ⟪e0, comm (adjoint (ketBra e1 e0)) (comm (ketBra e1 e1) (ketBra e1 e0)) e0⟫_ℂ / 2 := ... -- proof elided

theorem symmetry_needed_fin2 :
    ∃ (H ρ : EuclideanSpace ℂ (Fin 2) →ₗ[ℂ] EuclideanSpace ℂ (Fin 2))
      (ψ : EuclideanSpace ℂ (Fin 2)),
      H.IsSymmetric ∧ H ψ = ((0 : ℝ) : ℂ) • ψ ∧ ‖ψ‖ = 1 ∧
      ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = 1 ∧ excess H 0 ψ ρ = 1 := ... -- proof elided
