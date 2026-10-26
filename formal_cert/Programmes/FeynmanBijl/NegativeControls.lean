import Programmes.FeynmanBijl.Basic

/-!
# P6 Feynman–Bijl: genuine negative control (a kernel-checked counterexample)

`excess_eq_half` needs the k ↔ -k symmetry hypothesis `A(ρ†) = A(ρ)`. This file shows it cannot be
dropped: with orthonormal `e₀, e₁`, `H = |e₁⟩⟨e₁|`, ground state `ψ = e₀` (`E₀ = 0`) and the
one-sided "raising" operator `ρ = |e₁⟩⟨e₀|`, the double commutator has value `1` while
`A(ρ) = 1 ≠ 1/2`, because `ρ† ψ = 0` gives `A(ρ†) = 0`. A concrete instance on
`EuclideanSpace ℂ (Fin 2)` is given by `symmetry_needed_fin2`.
-/

namespace ProgFeynmanBijl

open scoped InnerProductSpace ComplexConjugate
open LinearMap

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E] [FiniteDimensional ℂ E]

/-- The rank-one operator `|v⟩⟨u| : x ↦ ⟪u, x⟫ v`. -/
noncomputable def ketBra (v u : E) : E →ₗ[ℂ] E := (innerₛₗ ℂ u).smulRight v

omit [FiniteDimensional ℂ E] in
lemma ketBra_apply (v u x : E) : ketBra v u x = ⟪u, x⟫_ℂ • v := rfl

omit [FiniteDimensional ℂ E] in
lemma ketBra_self_symm (v : E) : (ketBra v v).IsSymmetric := by
  intro x y
  rw [ketBra_apply, ketBra_apply, inner_smul_left, inner_smul_right, inner_conj_symm]
  ring

/-- **Negative control.** Without the symmetry hypothesis, `A(ρ) = f/2` fails. -/
theorem symmetry_needed {e0 e1 : E} (h0 : ‖e0‖ = 1) (h1 : ‖e1‖ = 1) (h01 : ⟪e0, e1⟫_ℂ = 0) :
    (ketBra e1 e1).IsSymmetric ∧ ketBra e1 e1 e0 = ((0 : ℝ) : ℂ) • e0 ∧
    ⟪e0, comm (adjoint (ketBra e1 e0)) (comm (ketBra e1 e1) (ketBra e1 e0)) e0⟫_ℂ = 1 ∧
    excess (ketBra e1 e1) 0 e0 (ketBra e1 e0) = 1 ∧
    excess (ketBra e1 e1) 0 e0 (ketBra e1 e0) ≠
      ⟪e0, comm (adjoint (ketBra e1 e0)) (comm (ketBra e1 e1) (ketBra e1 e0)) e0⟫_ℂ / 2 := by
  have h10 : ⟪e1, e0⟫_ℂ = 0 := by rw [← inner_conj_symm, h01, map_zero]
  have n0 : ⟪e0, e0⟫_ℂ = 1 := by rw [inner_self_eq_norm_sq_to_K, h0]; norm_num
  have n1 : ⟪e1, e1⟫_ℂ = 1 := by rw [inner_self_eq_norm_sq_to_K, h1]; norm_num
  have hS := ketBra_self_symm e1
  have hψ : ketBra e1 e1 e0 = ((0 : ℝ) : ℂ) • e0 := by
    rw [ketBra_apply, h10, zero_smul, Complex.ofReal_zero, zero_smul]
  -- ρ† ψ = 0
  have hadj : adjoint (ketBra e1 e0) e0 = 0 := by
    rw [← inner_self_eq_zero (𝕜 := ℂ), adjoint_inner_left, ketBra_apply, inner_smul_right, h01,
      mul_zero]
  have hA : excess (ketBra e1 e1) 0 e0 (ketBra e1 e0) = 1 := by
    unfold excess
    rw [ketBra_apply e1 e0 e0, n0, one_smul, ketBra_apply, n1, one_smul, n1]
    simp
  have hAd : excess (ketBra e1 e1) 0 e0 (adjoint (ketBra e1 e0)) = 0 := by
    unfold excess
    rw [hadj]; simp
  have hdc := double_comm_expect hS hψ (ketBra e1 e0)
  rw [hA, hAd, add_zero] at hdc
  refine ⟨hS, hψ, hdc, hA, ?_⟩
  rw [hA, hdc]
  norm_num

/-- Concrete instance on `ℂ²` (`EuclideanSpace ℂ (Fin 2)`), standard basis vectors. -/
theorem symmetry_needed_fin2 :
    ∃ (H ρ : EuclideanSpace ℂ (Fin 2) →ₗ[ℂ] EuclideanSpace ℂ (Fin 2))
      (ψ : EuclideanSpace ℂ (Fin 2)),
      H.IsSymmetric ∧ H ψ = ((0 : ℝ) : ℂ) • ψ ∧ ‖ψ‖ = 1 ∧
      ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = 1 ∧ excess H 0 ψ ρ = 1 := by
  have h0 : ‖EuclideanSpace.single (0 : Fin 2) (1 : ℂ)‖ = 1 := by simp
  have h1 : ‖EuclideanSpace.single (1 : Fin 2) (1 : ℂ)‖ = 1 := by simp
  have h01 : ⟪EuclideanSpace.single (0 : Fin 2) (1 : ℂ),
      EuclideanSpace.single (1 : Fin 2) (1 : ℂ)⟫_ℂ = 0 := by
    simp [EuclideanSpace.inner_single_left]
  obtain ⟨hS, hψ, hdc, hA, -⟩ := symmetry_needed h0 h1 h01
  exact ⟨_, _, _, hS, hψ, h0, hdc, hA⟩

end ProgFeynmanBijl

#print axioms ProgFeynmanBijl.ketBra_apply
#print axioms ProgFeynmanBijl.ketBra_self_symm
#print axioms ProgFeynmanBijl.symmetry_needed
#print axioms ProgFeynmanBijl.symmetry_needed_fin2
