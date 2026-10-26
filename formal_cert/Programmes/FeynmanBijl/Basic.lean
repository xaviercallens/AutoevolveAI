import Mathlib.Analysis.InnerProductSpace.Spectrum
import Mathlib.Analysis.InnerProductSpace.Adjoint
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.Tactic

/-!
# Feynman–Bijl single-mode bound in finite dimension (P6, programmes 2026-10-25)

Setting: `E` a finite-dimensional complex inner product space, `H : E →ₗ[ℂ] E` symmetric
(Hermitian), `ψ` with `H ψ = E₀ ψ` (`E₀ : ℝ`), and an arbitrary operator `ρ` (the density
fluctuation `ρ_k`), with Hilbert adjoint `ρ† = LinearMap.adjoint ρ` (`ρ_{-k}` in the physics).

* `double_comm_expect` (key algebraic step, no extra hypotheses):
  `⟪ψ, [ρ†,[H,ρ]] ψ⟫ = A(ρ) + A(ρ†)`, where `A(X) = ⟪Xψ, (H - E₀) Xψ⟫`.
* `excess_eq_half` (needs the k ↔ -k symmetry `A(ρ†) = A(ρ)`, stated as a hypothesis):
  `A(ρ) = f/2`, where `f` is the value of the double commutator (the f-sum).
* `trial_energy_eq` : the normalised trial state `ρψ/‖ρψ‖` has energy
  `E₀ + f/(2 N S)` with `S = ‖ρψ‖²/N`.
* `trial_energy_le_of_ground` (no symmetry, but `ψ` a ground state): excess `≤ f/(N S)`.
* `sector_eigenvalue_le` (variational step): some eigenvector `eᵢ` of `H` with
  `⟪eᵢ, ρψ⟫ ≠ 0` has eigenvalue `λᵢ ≤` the Rayleigh quotient of `ρψ`.
* `feynman_bijl_bound` : with the f-sum rule `f = N ħ² k²/m`, some eigenvalue in the sector excited
  by `ρ` satisfies `λᵢ - E₀ ≤ ħ² k²/(2 m S)`; `feynman_bijl_gap` adds `0 < λᵢ - E₀` when `ψ` is a
  ground state and `ρψ ⊥` the `E₀`-eigenspace; `feynman_bijl_bound_ground` drops the symmetry and
  gets `ħ² k²/(m S)`.
* Bogoliubov: `feynman_sBog_eq` — the Feynman energy computed from `S_B = ε₀/ε_B` is exactly `ε_B`;
  `feynman_le_epsBog_iff` — the Feynman energy from `S` is `≤ ε_B` iff `S ≥ S_B`.

The f-sum rule itself is a hypothesis here (it comes from the canonical commutation relations,
which have no finite-dimensional representation). Novelty is not claimed: this is the textbook
Feynman (1954) / Bijl (1940) argument.
-/

namespace ProgFeynmanBijl

open scoped InnerProductSpace ComplexConjugate
open LinearMap

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E] [FiniteDimensional ℂ E]

/-- Commutator `[A, B] = A B - B A` of linear endomorphisms. -/
def comm (A B : E →ₗ[ℂ] E) : E →ₗ[ℂ] E := A ∘ₗ B - B ∘ₗ A

/-- Excitation functional `A(X) = ⟪Xψ, H Xψ⟫ - E₀ ⟪Xψ, Xψ⟫ = ⟪Xψ, (H - E₀) Xψ⟫`. -/
noncomputable def excess (H : E →ₗ[ℂ] E) (E0 : ℝ) (ψ : E) (X : E →ₗ[ℂ] E) : ℂ :=
  ⟪X ψ, H (X ψ)⟫_ℂ - (E0 : ℂ) * ⟪X ψ, X ψ⟫_ℂ

variable {H : E →ₗ[ℂ] E} {E0 : ℝ} {ψ : E}

omit [FiniteDimensional ℂ E] in
lemma inner_eig_H (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ) (x : E) :
    ⟪ψ, H x⟫_ℂ = (E0 : ℂ) * ⟪ψ, x⟫_ℂ := by
  rw [← hH ψ x, hψ, inner_smul_left, Complex.conj_ofReal]

/-- **Double-commutator identity.** For `H` symmetric and `H ψ = E₀ ψ`, for every operator `ρ`:
`⟪ψ, [ρ†, [H, ρ]] ψ⟫ = A(ρ) + A(ρ†)`. -/
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

/-- With the k ↔ -k symmetry `A(ρ†) = A(ρ)`, the excitation functional is half the f-sum. -/
theorem excess_eq_half (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ) (ρ : E →ₗ[ℂ] E) {f : ℂ}
    (hf : ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = f)
    (hsym : excess H E0 ψ (adjoint ρ) = excess H E0 ψ ρ) :
    excess H E0 ψ ρ = f / 2 := by
  rw [double_comm_expect hH hψ, hsym] at hf
  rw [← hf]; ring

omit [FiniteDimensional ℂ E] in
/-- Real part of the excitation functional: `re A(X) = re⟪Xψ, H Xψ⟫ - E₀ ‖Xψ‖²`. -/
lemma excess_re (X : E →ₗ[ℂ] E) :
    (excess H E0 ψ X).re = (⟪X ψ, H (X ψ)⟫_ℂ).re - E0 * ‖X ψ‖ ^ 2 := by
  unfold excess
  rw [inner_self_eq_norm_sq_to_K, Complex.sub_re, Complex.re_ofReal_mul]
  norm_cast

omit [FiniteDimensional ℂ E] in
/-- Rayleigh quotient of the normalised vector: `re⟪x̂, H x̂⟫ = re⟪x, H x⟫ / ‖x‖²`. -/
lemma rayleigh_normalised (x : E) :
    (⟪((‖x‖⁻¹ : ℝ) : ℂ) • x, H (((‖x‖⁻¹ : ℝ) : ℂ) • x)⟫_ℂ).re = (⟪x, H x⟫_ℂ).re / ‖x‖ ^ 2 := by
  rw [map_smul, inner_smul_left, inner_smul_right, Complex.conj_ofReal, ← mul_assoc,
    ← Complex.ofReal_mul, Complex.re_ofReal_mul]
  field_simp

/-- **Trial-state energy (Feynman–Bijl).** With the symmetry hypothesis, `N > 0`, `ρψ ≠ 0`,
`S = ‖ρψ‖²/N` and `f` the value of the double commutator (taken real), the normalised trial
state `ρψ/‖ρψ‖` has energy `E₀ + f/(2 N S)`. -/
theorem trial_energy_eq (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ) (ρ : E →ₗ[ℂ] E)
    {f N : ℝ} (hN : 0 < N) (hρψ : ρ ψ ≠ 0)
    (hf : ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = (f : ℂ))
    (hsym : excess H E0 ψ (adjoint ρ) = excess H E0 ψ ρ) :
    (⟪((‖ρ ψ‖⁻¹ : ℝ) : ℂ) • ρ ψ, H (((‖ρ ψ‖⁻¹ : ℝ) : ℂ) • ρ ψ)⟫_ℂ).re - E0
      = f / (2 * N * (‖ρ ψ‖ ^ 2 / N)) := by
  have hA := congrArg Complex.re (excess_eq_half hH hψ ρ hf hsym)
  rw [excess_re] at hA
  have h2 : (((f : ℂ) / 2).re) = f / 2 := by
    rw [Complex.div_ofNat_re, Complex.ofReal_re]
  rw [h2] at hA
  have hn : 0 < ‖ρ ψ‖ := norm_pos_iff.mpr hρψ
  rw [rayleigh_normalised]
  field_simp
  linarith

/-- If `ψ` is a ground state (`E₀ ‖x‖² ≤ re⟪x, H x⟫` for all `x`), both terms of the
double-commutator identity are non-negative, so without any symmetry hypothesis the excess of
the trial state is at most `f/(N S)` (half as strong as `trial_energy_eq`). -/
theorem trial_energy_le_of_ground (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ)
    (hgs : ∀ x : E, E0 * ‖x‖ ^ 2 ≤ (⟪x, H x⟫_ℂ).re) (ρ : E →ₗ[ℂ] E)
    {f N : ℝ} (hN : 0 < N) (hρψ : ρ ψ ≠ 0)
    (hf : ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = (f : ℂ)) :
    (⟪((‖ρ ψ‖⁻¹ : ℝ) : ℂ) • ρ ψ, H (((‖ρ ψ‖⁻¹ : ℝ) : ℂ) • ρ ψ)⟫_ℂ).re - E0
      ≤ f / (N * (‖ρ ψ‖ ^ 2 / N)) := by
  have hdc := congrArg Complex.re (double_comm_expect hH hψ ρ)
  rw [hf, Complex.add_re, excess_re, excess_re, Complex.ofReal_re] at hdc
  have hB := hgs (adjoint ρ ψ)
  have hn : 0 < ‖ρ ψ‖ := norm_pos_iff.mpr hρψ
  rw [rayleigh_normalised, div_sub' (by positivity), div_le_div_iff₀ (by positivity) (by positivity)]
  field_simp
  nlinarith

/-- Weighted-mean lemma: some index with positive weight has value at most the weighted mean. -/
lemma exists_le_weighted_mean {ι : Type*} [Fintype ι] (w l : ι → ℝ) (hw : ∀ i, 0 ≤ w i)
    (hpos : 0 < ∑ i, w i) : ∃ i, 0 < w i ∧ l i * ∑ j, w j ≤ ∑ j, w j * l j := by
  by_contra h
  simp only [not_exists, not_and, not_le] at h
  obtain ⟨i0, -, hi0⟩ := Finset.exists_lt_of_sum_lt (s := Finset.univ) (f := fun _ => (0 : ℝ))
    (g := w) (by simpa using hpos)
  have hlt : ∑ i, w i * (∑ j, w j * l j) < ∑ i, w i * (l i * ∑ j, w j) := by
    apply Finset.sum_lt_sum
    · intro i _
      rcases (hw i).eq_or_lt with h0 | h0
      · rw [← h0]; simp
      · exact (mul_lt_mul_of_pos_left (h i h0) h0).le
    · exact ⟨i0, Finset.mem_univ _, mul_lt_mul_of_pos_left (h i0 hi0) hi0⟩
  have e1 : ∑ i, w i * (∑ j, w j * l j) = (∑ j, w j) * (∑ j, w j * l j) := by
    rw [Finset.sum_mul]
  have e2 : ∑ i, w i * (l i * ∑ j, w j) = (∑ j, w j) * (∑ j, w j * l j) := by
    rw [mul_comm, Finset.sum_mul]
    apply Finset.sum_congr rfl
    intro i _; ring
  rw [e1, e2] at hlt
  exact lt_irrefl _ hlt

/-- Spectral (Rayleigh) expansion: `re⟪x, H x⟫ = ∑ᵢ λᵢ ‖⟪eᵢ, x⟫‖²` in an orthonormal eigenbasis. -/
lemma rayleigh_expansion (hH : H.IsSymmetric) (x : E) :
    (⟪x, H x⟫_ℂ).re = ∑ i, ‖⟪hH.eigenvectorBasis rfl i, x⟫_ℂ‖ ^ 2 * hH.eigenvalues rfl i := by
  set b := hH.eigenvectorBasis (n := Module.finrank ℂ E) rfl
  rw [← b.sum_inner_mul_inner x (H x), Complex.re_sum]
  apply Finset.sum_congr rfl
  intro i _
  have hb : ⟪b i, H x⟫_ℂ = (hH.eigenvalues rfl i : ℂ) * ⟪b i, x⟫_ℂ := by
    rw [← hH (b i) x, hH.apply_eigenvectorBasis, inner_smul_left, RCLike.conj_ofReal]
    rfl
  rw [hb, ← inner_conj_symm x (b i), mul_left_comm, RCLike.conj_mul, ← RCLike.ofReal_pow]
  have key : ∀ a c : ℝ, ((a : ℂ) * (c : ℂ)).re = c * a := fun a c => by
    rw [Complex.re_ofReal_mul, Complex.ofReal_re, mul_comm]
  exact key _ _

/-- **Variational step in the sector excited by `φ`.** For `φ ≠ 0` some orthonormal eigenvector
`eᵢ` of `H` with `⟪eᵢ, φ⟫ ≠ 0` has eigenvalue `λᵢ ≤ re⟪φ, H φ⟫ / ‖φ‖²`. -/
theorem sector_eigenvalue_le (hH : H.IsSymmetric) (φ : E) (hφ : φ ≠ 0) :
    ∃ i, ⟪hH.eigenvectorBasis rfl i, φ⟫_ℂ ≠ 0 ∧
      hH.eigenvalues rfl i ≤ (⟪φ, H φ⟫_ℂ).re / ‖φ‖ ^ 2 := by
  set b := hH.eigenvectorBasis (n := Module.finrank ℂ E) rfl
  have hW : ∑ i, ‖⟪b i, φ⟫_ℂ‖ ^ 2 = ‖φ‖ ^ 2 := b.sum_sq_norm_inner_right φ
  have hn : 0 < ‖φ‖ := norm_pos_iff.mpr hφ
  obtain ⟨i, hi, hle⟩ := exists_le_weighted_mean (fun i => ‖⟪b i, φ⟫_ℂ‖ ^ 2)
    (fun i => hH.eigenvalues rfl i) (fun i => by positivity) (by rw [hW]; positivity)
  refine ⟨i, ?_, ?_⟩
  · intro h0; simp [h0] at hi
  · rw [hW, ← rayleigh_expansion hH φ] at hle
    rw [le_div_iff₀ (by positivity)]
    exact hle

/-- **Feynman–Bijl bound.** Hypotheses: `H` symmetric, `H ψ = E₀ ψ`; the f-sum rule
`⟪ψ, [ρ†,[H,ρ]] ψ⟫ = N ħ² k²/m`; the k ↔ -k symmetry `A(ρ†) = A(ρ)`; `N, m, ħ > 0`; and
`S = ‖ρψ‖²/N > 0`. Conclusion: some orthonormal eigenvector `eᵢ` of `H` in the sector excited by
`ρ` (`⟪eᵢ, ρψ⟫ ≠ 0`) has `λᵢ - E₀ ≤ ħ² k²/(2 m S)`. -/
theorem feynman_bijl_bound (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ) (ρ : E →ₗ[ℂ] E)
    {N m hbar k S : ℝ} (hN : 0 < N) (hm : 0 < m) (hS : 0 < S) (hSdef : S = ‖ρ ψ‖ ^ 2 / N)
    (hf : ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = ((N * hbar ^ 2 * k ^ 2 / m : ℝ) : ℂ))
    (hsym : excess H E0 ψ (adjoint ρ) = excess H E0 ψ ρ) :
    ∃ i, ⟪hH.eigenvectorBasis rfl i, ρ ψ⟫_ℂ ≠ 0 ∧
      hH.eigenvalues rfl i - E0 ≤ hbar ^ 2 * k ^ 2 / (2 * m * S) := by
  have hρψ : ρ ψ ≠ 0 := by
    intro h0; rw [h0, norm_zero] at hSdef; simp at hSdef; linarith
  have htrial := trial_energy_eq hH hψ ρ hN hρψ hf hsym
  rw [rayleigh_normalised, ← hSdef] at htrial
  obtain ⟨i, hi, hle⟩ := sector_eigenvalue_le hH (ρ ψ) hρψ
  refine ⟨i, hi, ?_⟩
  have hval : N * hbar ^ 2 * k ^ 2 / m / (2 * N * S) = hbar ^ 2 * k ^ 2 / (2 * m * S) := by
    field_simp
  linarith

/-- **Symmetry-free variant.** If instead of the k ↔ -k symmetry `ψ` is a ground state
(`E₀ ‖x‖² ≤ re⟪x, H x⟫` for all `x`), the same f-sum rule gives the weaker bound
`λᵢ - E₀ ≤ ħ² k²/(m S)` (no factor 2) for some eigenvector in the sector excited by `ρ`. -/
theorem feynman_bijl_bound_ground (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ)
    (hgs : ∀ x : E, E0 * ‖x‖ ^ 2 ≤ (⟪x, H x⟫_ℂ).re) (ρ : E →ₗ[ℂ] E)
    {N m hbar k S : ℝ} (hN : 0 < N) (hm : 0 < m) (hS : 0 < S) (hSdef : S = ‖ρ ψ‖ ^ 2 / N)
    (hf : ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = ((N * hbar ^ 2 * k ^ 2 / m : ℝ) : ℂ)) :
    ∃ i, ⟪hH.eigenvectorBasis rfl i, ρ ψ⟫_ℂ ≠ 0 ∧
      hH.eigenvalues rfl i - E0 ≤ hbar ^ 2 * k ^ 2 / (m * S) := by
  have hρψ : ρ ψ ≠ 0 := by
    intro h0; rw [h0, norm_zero] at hSdef; simp at hSdef; linarith
  have htrial := trial_energy_le_of_ground hH hψ hgs ρ hN hρψ hf
  rw [rayleigh_normalised, ← hSdef] at htrial
  obtain ⟨i, hi, hle⟩ := sector_eigenvalue_le hH (ρ ψ) hρψ
  refine ⟨i, hi, ?_⟩
  have hval : N * hbar ^ 2 * k ^ 2 / m / (N * S) = hbar ^ 2 * k ^ 2 / (m * S) := by
    field_simp
  linarith

/-- **Gap form.** Add to `feynman_bijl_bound` that `ψ` is a ground state and that `ρψ` is
orthogonal to the whole `E₀`-eigenspace (for `k ≠ 0` this is what momentum conservation gives
physically; here it is a hypothesis). Then the eigenvalue found is a genuine excitation:
`0 < λᵢ - E₀ ≤ ħ² k²/(2 m S)`. -/
theorem feynman_bijl_gap (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ)
    (hgs : ∀ x : E, E0 * ‖x‖ ^ 2 ≤ (⟪x, H x⟫_ℂ).re) (ρ : E →ₗ[ℂ] E)
    (horth : ∀ v : E, H v = (E0 : ℂ) • v → ⟪v, ρ ψ⟫_ℂ = 0)
    {N m hbar k S : ℝ} (hN : 0 < N) (hm : 0 < m) (hS : 0 < S) (hSdef : S = ‖ρ ψ‖ ^ 2 / N)
    (hf : ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = ((N * hbar ^ 2 * k ^ 2 / m : ℝ) : ℂ))
    (hsym : excess H E0 ψ (adjoint ρ) = excess H E0 ψ ρ) :
    ∃ i, ⟪hH.eigenvectorBasis rfl i, ρ ψ⟫_ℂ ≠ 0 ∧
      0 < hH.eigenvalues rfl i - E0 ∧
      hH.eigenvalues rfl i - E0 ≤ hbar ^ 2 * k ^ 2 / (2 * m * S) := by
  obtain ⟨i, hi, hle⟩ := feynman_bijl_bound hH hψ ρ hN hm hS hSdef hf hsym
  refine ⟨i, hi, ?_, hle⟩
  set b := hH.eigenvectorBasis (n := Module.finrank ℂ E) rfl
  have hb1 : ‖b i‖ = 1 := b.orthonormal.1 i
  have hre : (⟪b i, H (b i)⟫_ℂ).re = hH.eigenvalues rfl i := by
    rw [hH.apply_eigenvectorBasis, inner_smul_right, inner_self_eq_norm_sq_to_K, hb1]
    simp
  have hge : E0 ≤ hH.eigenvalues rfl i := by
    have := hgs (b i); rw [hb1, hre] at this; linarith
  have hne : hH.eigenvalues rfl i ≠ E0 := by
    intro heq
    apply hi
    apply horth
    rw [hH.apply_eigenvectorBasis, heq]
    rfl
  have : E0 < hH.eigenvalues rfl i := lt_of_le_of_ne hge (Ne.symm hne)
  linarith

/-! ## Bogoliubov gas (connection to H8)

Variables as in H8: `hc = ħ c`, `ks = k* = 2 m c/ħ`, free energy `ε₀ = ħ²k²/2m = hc k²/ks`,
`ε_B = √((hc k)² + (hc k²/ks)²)`, `S_B = ε₀/ε_B`. The Feynman energy from a structure factor
`S` is `ε_F(S) = ε₀/S = ħ²k²/(2 m S)`. -/

/-- Free-particle energy `ε₀ = hc k²/ks`. -/
noncomputable def epsFree (hc ks k : ℝ) : ℝ := hc * k ^ 2 / ks

/-- Bogoliubov energy `ε_B = √((hc k)² + (hc k²/ks)²)`. -/
noncomputable def epsBog (hc ks k : ℝ) : ℝ := Real.sqrt ((hc * k) ^ 2 + (hc * k ^ 2 / ks) ^ 2)

/-- Bogoliubov (Bijl–Feynman) structure factor `S_B = ε₀/ε_B`. -/
noncomputable def sBog (hc ks k : ℝ) : ℝ := epsFree hc ks k / epsBog hc ks k

/-- Units check: with `hc = ħ c` and `ks = 2 m c/ħ`, `ε₀ = ħ² k²/(2 m)`. -/
theorem epsFree_units {hbar m c k : ℝ} (hh : 0 < hbar) (hm : 0 < m) (hc : 0 < c) :
    epsFree (hbar * c) (2 * m * c / hbar) k = hbar ^ 2 * k ^ 2 / (2 * m) := by
  unfold epsFree
  field_simp

lemma epsBog_pos {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) : 0 < epsBog hc ks k := by
  unfold epsBog; apply Real.sqrt_pos.mpr; positivity

lemma sBog_pos {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) : 0 < sBog hc ks k := by
  unfold sBog epsFree
  have := epsBog_pos (ks := ks) hhc hk
  positivity

/-- **Bogoliubov saturates Feynman.** The Feynman energy `ε₀/S_B` computed from the Bogoliubov
structure factor is exactly `ε_B`. -/
theorem feynman_sBog_eq {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    epsFree hc ks k / sBog hc ks k = epsBog hc ks k := by
  have h1 : epsFree hc ks k ≠ 0 := by unfold epsFree; positivity
  have h2 : epsBog hc ks k ≠ 0 := (epsBog_pos hhc hk).ne'
  unfold sBog
  field_simp

/-- **Comparison.** For a structure factor `S > 0`, the Feynman energy `ε₀/S` is at most `ε_B`
iff `S ≥ S_B`. -/
theorem feynman_le_epsBog_iff {hc ks k S : ℝ} (hhc : 0 < hc) (hk : 0 < k)
    (hS : 0 < S) : epsFree hc ks k / S ≤ epsBog hc ks k ↔ sBog hc ks k ≤ S := by
  have hB := epsBog_pos (ks := ks) hhc hk
  unfold sBog
  rw [div_le_iff₀ hS, div_le_iff₀ hB, mul_comm]

/-- Closed form (as in H8, re-proved here on the pinned stack): `S_B² = k²/(ks² + k²)`. -/
theorem sBog_sq {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ^ 2 = k ^ 2 / (ks ^ 2 + k ^ 2) := by
  have hpos : 0 ≤ (hc * k) ^ 2 + (hc * k ^ 2 / ks) ^ 2 := by positivity
  unfold sBog epsBog epsFree
  rw [div_pow, Real.sq_sqrt hpos]
  have h1 : hc ≠ 0 := ne_of_gt hhc
  have h2 : k ≠ 0 := ne_of_gt hk
  have h3 : ks ≠ 0 := ne_of_gt hks
  have h4 : ks ^ 2 + k ^ 2 ≠ 0 := by positivity
  field_simp

/-- H8 bound, re-proved on the pinned stack: `S_B(k) ≤ √(k/(2 ks))`. -/
theorem sBog_le_sqrt {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ≤ Real.sqrt (k / (2 * ks)) := by
  rw [← Real.sqrt_sq (sBog_pos hhc hk hks).le]
  apply Real.sqrt_le_sqrt
  rw [sBog_sq hhc hk hks, div_le_div_iff₀ (by positivity) (by positivity)]
  nlinarith [mul_nonneg hk.le (sq_nonneg (k - ks))]

/-- Physical-units form: `ħ² k²/(2 m S_B) = ε_B` with `hc = ħ c`, `ks = 2 m c/ħ`. -/
theorem feynman_sBog_units {hbar m c k : ℝ} (hh : 0 < hbar) (hm : 0 < m) (hc : 0 < c)
    (hk : 0 < k) :
    hbar ^ 2 * k ^ 2 / (2 * m * sBog (hbar * c) (2 * m * c / hbar) k)
      = epsBog (hbar * c) (2 * m * c / hbar) k := by
  have hks : 0 < 2 * m * c / hbar := by positivity
  rw [← feynman_sBog_eq (by positivity) hk hks, epsFree_units hh hm hc]
  have := sBog_pos (by positivity : 0 < hbar * c) hk hks
  field_simp

end ProgFeynmanBijl

#print axioms ProgFeynmanBijl.inner_eig_H
#print axioms ProgFeynmanBijl.epsBog_pos
#print axioms ProgFeynmanBijl.sBog_pos
#print axioms ProgFeynmanBijl.double_comm_expect
#print axioms ProgFeynmanBijl.excess_eq_half
#print axioms ProgFeynmanBijl.excess_re
#print axioms ProgFeynmanBijl.rayleigh_normalised
#print axioms ProgFeynmanBijl.trial_energy_eq
#print axioms ProgFeynmanBijl.trial_energy_le_of_ground
#print axioms ProgFeynmanBijl.exists_le_weighted_mean
#print axioms ProgFeynmanBijl.rayleigh_expansion
#print axioms ProgFeynmanBijl.sector_eigenvalue_le
#print axioms ProgFeynmanBijl.feynman_bijl_bound
#print axioms ProgFeynmanBijl.feynman_bijl_bound_ground
#print axioms ProgFeynmanBijl.feynman_bijl_gap
#print axioms ProgFeynmanBijl.epsFree_units
#print axioms ProgFeynmanBijl.feynman_sBog_eq
#print axioms ProgFeynmanBijl.feynman_le_epsBog_iff
#print axioms ProgFeynmanBijl.sBog_sq
#print axioms ProgFeynmanBijl.sBog_le_sqrt
#print axioms ProgFeynmanBijl.feynman_sBog_units
