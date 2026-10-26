theorem feynman_bijl_bound_ground (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ)
    (hgs : ∀ x : E, E0 * ‖x‖ ^ 2 ≤ (⟪x, H x⟫_ℂ).re) (ρ : E →ₗ[ℂ] E)
    {N m hbar k S : ℝ} (hN : 0 < N) (hm : 0 < m) (hS : 0 < S) (hSdef : S = ‖ρ ψ‖ ^ 2 / N)
    (hf : ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = ((N * hbar ^ 2 * k ^ 2 / m : ℝ) : ℂ)) :
    ∃ i, ⟪hH.eigenvectorBasis rfl i, ρ ψ⟫_ℂ ≠ 0 ∧
      hH.eigenvalues rfl i - E0 ≤ hbar ^ 2 * k ^ 2 / (m * S) := ... -- proof elided
