import Programmes.FeynmanBijl.NegativeControls

/-!
# P6 Feynman–Bijl: positive control (non-vacuity and sharpness of `feynman_bijl_gap`)

All hypotheses of `feynman_bijl_gap` hold together on a two-level instance, and there the bound is
attained. Take orthonormal `e₀, e₁`, `H = |e₁⟩⟨e₁|`, ground state `ψ = e₀` (`E₀ = 0`) and the
Hermitian `ρ = |e₁⟩⟨e₀| + |e₀⟩⟨e₁|`, so that `ρψ = e₁ ⊥` the `E₀`-eigenspace. With
`N = ħ = k = 1` and `m = 1/2`, the f-sum is `2 = N ħ² k²/m` and `S = ‖ρψ‖²/N = 1`, so
`ħ²k²/(2 m S) = 1`. And `ρψ = e₁` is an eigenvector with eigenvalue exactly `1 = E₀ + ħ²k²/(2 m S)`.
-/

namespace ProgFeynmanBijl

open scoped InnerProductSpace ComplexConjugate
open LinearMap

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E] [FiniteDimensional ℂ E]

/-- Every hypothesis of `feynman_bijl_gap` holds on the two-level instance, and `ρψ` is an
eigenvector whose eigenvalue equals the Feynman–Bijl bound (sharpness). -/
theorem gap_witness {e0 e1 : E} (h0 : ‖e0‖ = 1) (h1 : ‖e1‖ = 1) (h01 : ⟪e0, e1⟫_ℂ = 0) :
    (ketBra e1 e1).IsSymmetric ∧
    ketBra e1 e1 e0 = ((0 : ℝ) : ℂ) • e0 ∧
    (∀ x : E, (0 : ℝ) * ‖x‖ ^ 2 ≤ (⟪x, ketBra e1 e1 x⟫_ℂ).re) ∧
    (∀ v : E, ketBra e1 e1 v = ((0 : ℝ) : ℂ) • v →
      ⟪v, (ketBra e1 e0 + ketBra e0 e1) e0⟫_ℂ = 0) ∧
    (1 : ℝ) = ‖(ketBra e1 e0 + ketBra e0 e1) e0‖ ^ 2 / 1 ∧
    ⟪e0, comm (adjoint (ketBra e1 e0 + ketBra e0 e1))
        (comm (ketBra e1 e1) (ketBra e1 e0 + ketBra e0 e1)) e0⟫_ℂ
      = (((1 : ℝ) * 1 ^ 2 * 1 ^ 2 / (1 / 2) : ℝ) : ℂ) ∧
    excess (ketBra e1 e1) 0 e0 (adjoint (ketBra e1 e0 + ketBra e0 e1))
      = excess (ketBra e1 e1) 0 e0 (ketBra e1 e0 + ketBra e0 e1) ∧
    ketBra e1 e1 ((ketBra e1 e0 + ketBra e0 e1) e0)
      = (((1 : ℝ) ^ 2 * 1 ^ 2 / (2 * (1 / 2) * 1) : ℝ) : ℂ) • ((ketBra e1 e0 + ketBra e0 e1) e0) := by
  have h10 : ⟪e1, e0⟫_ℂ = 0 := by rw [← inner_conj_symm, h01, map_zero]
  have n0 : ⟪e0, e0⟫_ℂ = 1 := by rw [inner_self_eq_norm_sq_to_K, h0]; norm_num
  have n1 : ⟪e1, e1⟫_ℂ = 1 := by rw [inner_self_eq_norm_sq_to_K, h1]; norm_num
  have hS := ketBra_self_symm e1
  have hψ : ketBra e1 e1 e0 = ((0 : ℝ) : ℂ) • e0 := by
    rw [ketBra_apply, h10, zero_smul, Complex.ofReal_zero, zero_smul]
  set ρ := ketBra e1 e0 + ketBra e0 e1 with hρdef
  have hρψ : ρ e0 = e1 := by
    rw [hρdef, LinearMap.add_apply, ketBra_apply, ketBra_apply, n0, h10, one_smul, zero_smul,
      add_zero]
  have hρsym : ρ.IsSymmetric := by
    intro x y
    simp only [hρdef, LinearMap.add_apply, ketBra_apply, inner_add_left, inner_add_right,
      inner_smul_left, inner_smul_right, inner_conj_symm]
    ring
  have hadj : adjoint ρ = ρ := ((LinearMap.eq_adjoint_iff ρ ρ).mpr hρsym).symm
  have hA : excess (ketBra e1 e1) 0 e0 ρ = 1 := by
    unfold excess
    rw [hρψ, ketBra_apply, n1, one_smul, n1]
    simp
  refine ⟨hS, hψ, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro x
    rw [ketBra_apply, inner_smul_right, ← inner_conj_symm x e1, Complex.mul_conj,
      Complex.ofReal_re, zero_mul]
    exact Complex.normSq_nonneg _
  · intro v hv
    rw [hρψ, ← inner_conj_symm]
    rw [ketBra_apply, Complex.ofReal_zero, zero_smul, smul_eq_zero] at hv
    rcases hv with hv | hv
    · rw [hv, map_zero]
    · rw [hv, norm_zero] at h1; norm_num at h1
  · rw [hρψ, h1]; norm_num
  · rw [double_comm_expect hS hψ ρ, hadj, hA]; norm_num
  · rw [hadj]
  · rw [hρψ, ketBra_apply, n1]; norm_num

/-- Instantiating `feynman_bijl_gap` on the witness: its conclusion is reached
(`0 < λᵢ - E₀ ≤ 1`), so the theorem's hypotheses are jointly satisfiable. -/
theorem gap_witness_applies {e0 e1 : E} (h0 : ‖e0‖ = 1) (h1 : ‖e1‖ = 1) (h01 : ⟪e0, e1⟫_ℂ = 0) :
    ∃ i, ⟪(ketBra_self_symm e1).eigenvectorBasis rfl i,
          (ketBra e1 e0 + ketBra e0 e1) e0⟫_ℂ ≠ 0 ∧
      0 < (ketBra_self_symm e1).eigenvalues rfl i - 0 ∧
      (ketBra_self_symm e1).eigenvalues rfl i - 0 ≤ (1 : ℝ) ^ 2 * 1 ^ 2 / (2 * (1 / 2) * 1) := by
  obtain ⟨_, hψ, hgs, horth, hSdef, hf, hsym, -⟩ := gap_witness h0 h1 h01
  exact feynman_bijl_gap (ketBra_self_symm e1) hψ hgs _ horth (by norm_num) (by norm_num)
    (by norm_num) hSdef hf hsym

/-- The orthonormal pair needed by `gap_witness` exists (in `ℂ²`), so the witness is not empty. -/
theorem orthonormal_pair_fin2 :
    ∃ e0 e1 : EuclideanSpace ℂ (Fin 2), ‖e0‖ = 1 ∧ ‖e1‖ = 1 ∧ ⟪e0, e1⟫_ℂ = 0 :=
  ⟨EuclideanSpace.single 0 1, EuclideanSpace.single 1 1, by simp, by simp,
    by simp [EuclideanSpace.inner_single_left]⟩

end ProgFeynmanBijl

#print axioms ProgFeynmanBijl.gap_witness
#print axioms ProgFeynmanBijl.gap_witness_applies
#print axioms ProgFeynmanBijl.orthonormal_pair_fin2
