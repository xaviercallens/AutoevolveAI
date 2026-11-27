theorem trial_energy_eq (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ) (ρ : E →ₗ[ℂ] E)
    {f N : ℝ} (hN : 0 < N) (hρψ : ρ ψ ≠ 0)
    (hf : ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = (f : ℂ))
    (hsym : excess H E0 ψ (adjoint ρ) = excess H E0 ψ ρ) :
    (⟪((‖ρ ψ‖⁻¹ : ℝ) : ℂ) • ρ ψ, H (((‖ρ ψ‖⁻¹ : ℝ) : ℂ) • ρ ψ)⟫_ℂ).re - E0
      = f / (2 * N * (‖ρ ψ‖ ^ 2 / N)) := ... -- proof elided
