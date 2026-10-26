theorem excess_eq_half (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ) (ρ : E →ₗ[ℂ] E) {f : ℂ}
    (hf : ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = f)
    (hsym : excess H E0 ψ (adjoint ρ) = excess H E0 ψ ρ) :
    excess H E0 ψ ρ = f / 2 := by
  rw [double_comm_expect hH hψ, hsym] at hf
  rw [← hf]; ring
