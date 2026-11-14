theorem feynman_bijl_bound (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ) (ρ : E →ₗ[ℂ] E)
    {N m hbar k S : ℝ} (hN : 0 < N) (hm : 0 < m) (hS : 0 < S) (hSdef : S = ‖ρ ψ‖ ^ 2 / N)
    (hf : ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = ((N * hbar ^ 2 * k ^ 2 / m : ℝ) : ℂ))
    (hsym : excess H E0 ψ (adjoint ρ) = excess H E0 ψ ρ) :
    ∃ i, ⟪hH.eigenvectorBasis rfl i, ρ ψ⟫_ℂ ≠ 0 ∧
      hH.eigenvalues rfl i - E0 ≤ hbar ^ 2 * k ^ 2 / (2 * m * S) := ... -- proof elided
