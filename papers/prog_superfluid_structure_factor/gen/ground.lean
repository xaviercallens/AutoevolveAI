theorem trial_energy_le_of_ground (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ)
    (hgs : ∀ x : E, E0 * ‖x‖ ^ 2 ≤ (⟪x, H x⟫_ℂ).re) (ρ : E →ₗ[ℂ] E)
    {f N : ℝ} (hN : 0 < N) (hρψ : ρ ψ ≠ 0)
    (hf : ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = (f : ℂ)) :
    (⟪((‖ρ ψ‖⁻¹ : ℝ) : ℂ) • ρ ψ, H (((‖ρ ψ‖⁻¹ : ℝ) : ℂ) • ρ ψ)⟫_ℂ).re - E0
      ≤ f / (N * (‖ρ ψ‖ ^ 2 / N)) := ... -- proof elided
