import Autoresearch.Yukawa
import Triangular.AnyDensity

/-!
# Autoresearch 2026-10-25, H2 contribution: planar Yukawa crystals at every density, and screening-length mixtures

Builds on `Autoresearch.Yukawa` (planar Yukawa = 3D-screened Coulomb `e^{-κ r}/r` between particles in a plane; not the
2D Debye–Hückel Green function `K₀(κ r)`) and on `Triangular.AnyDensity` (D2: universal optimality at every density
`ρ > 0`, obtained from upstream's density-one `universal_energy_minimum` by rescaling).

New closure lemmas for upstream's `AdmissiblePotential`:
* `admissible_add`, `admissible_smul` (`c ≥ 0`), `admissible_zero`, `admissible_sum` (finite nonnegative combinations).

Corollaries:
* `yukawa_any_density`, `yukawa_optimal_any_density`, `latticeEnergy_yukawa_rho_lt_top`: at every density `ρ > 0` the
  rescaled triangular lattice `ρ^{-1/2} A` minimises the planar Yukawa energy among locally finite density-`ρ`
  configurations, and that minimum is finite;
* `yukawaMix_admissible`, `triangular_yukawaMix_optimal`, `latticeEnergy_yukawaMix_lt_top`, and the any-density versions:
  the same for every finite mixture `∑ wᵢ e^{-κᵢ r}/r` with `wᵢ ≥ 0`, `κᵢ > 0` (several screening lengths).

Negative control (Lean): the signed combination `g₁ - 2 g₂` is not admissible (negative at `t = 1/4`), so the sign
condition on the weights cannot be dropped.

Everything is conditional on upstream's theorem (AI-generated, not peer reviewed) and on definition fidelity.
Classical model only.
-/

namespace AutoresearchYukawaMix

open OAI.AtomicTriangular TriangularRiesz AutoresearchYukawa TriangularDensity
open scoped Pointwise

/-! ## Closure of `AdmissiblePotential` under nonnegative linear combinations -/

/-- The sum of two admissible potentials is admissible. -/
theorem admissible_add {f h : ℝ → ℝ} (hf : AdmissiblePotential f) (hh : AdmissiblePotential h) :
    AdmissiblePotential (f + h) := by
  refine ⟨hf.1.add hh.1, fun t ht => add_nonneg (hf.2.1 t ht) (hh.2.1 t ht), fun r t ht => ?_⟩
  rw [iteratedDeriv_add (contDiffAt_of_admissible hf ht r) (contDiffAt_of_admissible hh ht r), mul_add]
  exact add_nonneg (hf.2.2 r t ht) (hh.2.2 r t ht)

/-- A nonnegative multiple of an admissible potential is admissible. -/
theorem admissible_smul {f : ℝ → ℝ} (hf : AdmissiblePotential f) {c : ℝ} (hc : 0 ≤ c) :
    AdmissiblePotential (c • f) := by
  refine ⟨hf.1.const_smul c, fun t ht => ?_, fun r t ht => ?_⟩
  · simp only [Pi.smul_apply, smul_eq_mul]
    exact mul_nonneg hc (hf.2.1 t ht)
  · rw [iteratedDeriv_const_smul_field, smul_eq_mul, mul_left_comm]
    exact mul_nonneg hc (hf.2.2 r t ht)

/-- The zero potential is admissible. -/
theorem admissible_zero : AdmissiblePotential (0 : ℝ → ℝ) :=
  admissible_congr (admissible_smul (riesz_admissible (s := 1) one_pos) le_rfl) (fun t _ => by simp)

/-- A finite nonnegative combination of admissible potentials is admissible. -/
theorem admissible_sum {ι : Type*} (s : Finset ι) (w : ι → ℝ) (f : ι → ℝ → ℝ) (hw : ∀ i ∈ s, 0 ≤ w i)
    (hf : ∀ i ∈ s, AdmissiblePotential (f i)) : AdmissiblePotential (∑ i ∈ s, w i • f i) := by
  classical
  induction s using Finset.induction_on with
  | empty => simpa using admissible_zero
  | insert a s ha ih =>
    rw [Finset.sum_insert ha]
    exact admissible_add (admissible_smul (hf a (Finset.mem_insert_self a s)) (hw a (Finset.mem_insert_self a s)))
      (ih (fun i hi => hw i (Finset.mem_insert_of_mem hi)) (fun i hi => hf i (Finset.mem_insert_of_mem hi)))

/-! ## A reusable finiteness criterion -/

/-- If `f ≤ K t^{-3/2}` on `(0, ∞)` with `K ≥ 0`, the triangular lattice energy of `f` is finite. -/
theorem latticeEnergy_lt_top_of_le_riesz3 {f : ℝ → ℝ} {K : ℝ} (hK : 0 ≤ K)
    (hle : ∀ t : ℝ, 0 < t → f t ≤ K * riesz 3 t) : latticeEnergy f < ⊤ := by
  have hR := latticeEnergy_riesz_lt_top (s := 3) (by norm_num)
  have hb : latticeEnergy f ≤ ENNReal.ofReal K * latticeEnergy (riesz 3) := by
    unfold latticeEnergy
    rw [← ENNReal.tsum_mul_left]
    refine ENNReal.tsum_le_tsum fun a => ?_
    have hpos : 0 < ‖a.val‖ ^ 2 := by
      have := a.2.2
      positivity
    rw [← ENNReal.ofReal_mul hK]
    exact ENNReal.ofReal_le_ofReal (hle _ hpos)
  exact lt_of_le_of_lt hb (ENNReal.mul_lt_top ENNReal.ofReal_lt_top hR)

lemma riesz3_rescale {ρ : ℝ} (hρ : 0 < ρ) {t : ℝ} (ht : 0 < t) :
    riesz 3 (ρ⁻¹ * t) = ρ⁻¹ ^ (-(3 / 2 : ℝ)) * riesz 3 t := by
  simp only [riesz]
  exact Real.mul_rpow (inv_pos.2 hρ).le ht.le

/-- Scaling identity: at density `ρ` the planar Yukawa potential is the density-one one at screening `κ/√ρ`, times `√ρ`.
So for a single screening length the every-density result is a reparametrisation (only `κ a`, `a = ρ^{-1/2}`, matters). -/
theorem g_rescale {κ ρ t : ℝ} (hρ : 0 < ρ) (ht : 0 < t) :
    g κ (ρ⁻¹ * t) = Real.sqrt ρ * g (κ / Real.sqrt ρ) t := by
  have hs : 0 < Real.sqrt ρ := Real.sqrt_pos.2 hρ
  have hst : 0 < Real.sqrt t := Real.sqrt_pos.2 ht
  simp only [g]
  rw [Real.sqrt_mul (inv_nonneg.2 hρ.le), Real.sqrt_inv]
  have he : -κ * ((Real.sqrt ρ)⁻¹ * Real.sqrt t) = -(κ / Real.sqrt ρ) * Real.sqrt t := by ring
  rw [he]
  field_simp

/-! ## Single screening length at every density -/

/-- **H2, every density.** At density `ρ > 0`, the rescaled triangular lattice energy bounds the planar Yukawa
energy of every locally finite density-`ρ` configuration. -/
theorem yukawa_any_density {κ : ℝ} (hκ : 0 < κ) {ρ : ℝ} (hρ : 0 < ρ) (C : Set Plane) (hC : LocallyFinite C)
    (hd : DensityRho ρ C) : latticeEnergy (fun t => g κ (ρ⁻¹ * t)) ≤ energy (g κ) C :=
  universal_any_density _ (yukawa_admissible hκ) hρ C hC hd

/-- **H2, every density, optimality form.** `ρ^{-1/2} A` is locally finite, has density `ρ`, and minimises the planar
Yukawa energy among locally finite density-`ρ` configurations. -/
theorem yukawa_optimal_any_density {κ : ℝ} (hκ : 0 < κ) {ρ : ℝ} (hρ : 0 < ρ) :
    LocallyFinite ((Real.sqrt ρ)⁻¹ • A) ∧ DensityRho ρ ((Real.sqrt ρ)⁻¹ • A) ∧
      ∀ C : Set Plane, LocallyFinite C → DensityRho ρ C →
        energy (g κ) ((Real.sqrt ρ)⁻¹ • A) ≤ energy (g κ) C :=
  triangular_optimal_any_density _ (yukawa_admissible hκ) hρ

/-- The minimal energy at density `ρ` is finite (so `yukawa_any_density` is not `⊤ ≤ ⊤`). -/
theorem latticeEnergy_yukawa_rho_lt_top {κ : ℝ} (hκ : 0 < κ) {ρ : ℝ} (hρ : 0 < ρ) :
    latticeEnergy (fun t => g κ (ρ⁻¹ * t)) < ⊤ := by
  refine latticeEnergy_lt_top_of_le_riesz3 (K := 2 / κ ^ 2 * ρ⁻¹ ^ (-(3 / 2 : ℝ)))
    (mul_nonneg (by positivity) (Real.rpow_nonneg (inv_pos.2 hρ).le _)) fun t ht => ?_
  have h1 := g_le hκ (mul_pos (inv_pos.2 hρ) ht)
  rw [riesz3_rescale hρ ht] at h1
  calc g κ (ρ⁻¹ * t) ≤ 2 / κ ^ 2 * (ρ⁻¹ ^ (-(3 / 2 : ℝ)) * riesz 3 t) := h1
    _ = 2 / κ ^ 2 * ρ⁻¹ ^ (-(3 / 2 : ℝ)) * riesz 3 t := by ring

/-! ## Mixtures of screening lengths -/

/-- Finite mixture of planar Yukawa potentials `∑ wᵢ e^{-κᵢ r}/r`, in the variable `t = r²`. -/
noncomputable def yukawaMix {ι : Type*} (s : Finset ι) (w κ : ι → ℝ) : ℝ → ℝ :=
  fun t => ∑ i ∈ s, w i * g (κ i) t

lemma yukawaMix_eq {ι : Type*} (s : Finset ι) (w κ : ι → ℝ) :
    (∑ i ∈ s, w i • g (κ i)) = yukawaMix s w κ := by
  funext t
  simp [yukawaMix, Finset.sum_apply]

/-- **H2, mixtures.** A finite nonnegative mixture of planar Yukawa potentials is admissible. -/
theorem yukawaMix_admissible {ι : Type*} (s : Finset ι) {w κ : ι → ℝ} (hw : ∀ i ∈ s, 0 ≤ w i)
    (hκ : ∀ i ∈ s, 0 < κ i) : AdmissiblePotential (yukawaMix s w κ) := by
  rw [← yukawaMix_eq]
  exact admissible_sum s w (fun i => g (κ i)) hw (fun i hi => yukawa_admissible (hκ i hi))

/-- **H2, mixtures.** The triangular lattice minimises the mixed-Yukawa energy at density one. -/
theorem triangular_yukawaMix_optimal {ι : Type*} (s : Finset ι) {w κ : ι → ℝ} (hw : ∀ i ∈ s, 0 ≤ w i)
    (hκ : ∀ i ∈ s, 0 < κ i) (C : Set Plane) (hC : LocallyFinite C) (hd : DensityOne C) :
    latticeEnergy (yukawaMix s w κ) ≤ energy (yukawaMix s w κ) C :=
  (universal_energy_minimum _ C (yukawaMix_admissible s hw hκ) hC hd).1

lemma yukawaMix_le {ι : Type*} (s : Finset ι) {w κ : ι → ℝ} (hw : ∀ i ∈ s, 0 ≤ w i) (hκ : ∀ i ∈ s, 0 < κ i)
    {t : ℝ} (ht : 0 < t) : yukawaMix s w κ t ≤ (∑ i ∈ s, w i * (2 / κ i ^ 2)) * riesz 3 t := by
  simp only [yukawaMix]
  rw [Finset.sum_mul]
  refine Finset.sum_le_sum fun i hi => ?_
  calc w i * g (κ i) t ≤ w i * (2 / κ i ^ 2 * riesz 3 t) := mul_le_mul_of_nonneg_left (g_le (hκ i hi) ht) (hw i hi)
    _ = w i * (2 / κ i ^ 2) * riesz 3 t := by ring

/-- The mixed-Yukawa triangular lattice energy is finite. -/
theorem latticeEnergy_yukawaMix_lt_top {ι : Type*} (s : Finset ι) {w κ : ι → ℝ} (hw : ∀ i ∈ s, 0 ≤ w i)
    (hκ : ∀ i ∈ s, 0 < κ i) : latticeEnergy (yukawaMix s w κ) < ⊤ := by
  refine latticeEnergy_lt_top_of_le_riesz3 ?_ fun t ht => yukawaMix_le s hw hκ ht
  exact Finset.sum_nonneg fun i hi => mul_nonneg (hw i hi) (by have := hκ i hi; positivity)

/-- **H2, mixtures at every density.** -/
theorem yukawaMix_optimal_any_density {ι : Type*} (s : Finset ι) {w κ : ι → ℝ} (hw : ∀ i ∈ s, 0 ≤ w i)
    (hκ : ∀ i ∈ s, 0 < κ i) {ρ : ℝ} (hρ : 0 < ρ) :
    LocallyFinite ((Real.sqrt ρ)⁻¹ • A) ∧ DensityRho ρ ((Real.sqrt ρ)⁻¹ • A) ∧
      ∀ C : Set Plane, LocallyFinite C → DensityRho ρ C →
        energy (yukawaMix s w κ) ((Real.sqrt ρ)⁻¹ • A) ≤ energy (yukawaMix s w κ) C :=
  triangular_optimal_any_density _ (yukawaMix_admissible s hw hκ) hρ

/-- The mixed-Yukawa minimal energy at density `ρ` is finite. -/
theorem latticeEnergy_yukawaMix_rho_lt_top {ι : Type*} (s : Finset ι) {w κ : ι → ℝ} (hw : ∀ i ∈ s, 0 ≤ w i)
    (hκ : ∀ i ∈ s, 0 < κ i) {ρ : ℝ} (hρ : 0 < ρ) :
    latticeEnergy (fun t => yukawaMix s w κ (ρ⁻¹ * t)) < ⊤ := by
  have hK : 0 ≤ ∑ i ∈ s, w i * (2 / κ i ^ 2) :=
    Finset.sum_nonneg fun i hi => mul_nonneg (hw i hi) (by have := hκ i hi; positivity)
  refine latticeEnergy_lt_top_of_le_riesz3 (K := (∑ i ∈ s, w i * (2 / κ i ^ 2)) * ρ⁻¹ ^ (-(3 / 2 : ℝ)))
    (mul_nonneg hK (Real.rpow_nonneg (inv_pos.2 hρ).le _)) fun t ht => ?_
  have h1 := yukawaMix_le s hw hκ (mul_pos (inv_pos.2 hρ) ht)
  rw [riesz3_rescale hρ ht] at h1
  calc yukawaMix s w κ (ρ⁻¹ * t) ≤ (∑ i ∈ s, w i * (2 / κ i ^ 2)) * (ρ⁻¹ ^ (-(3 / 2 : ℝ)) * riesz 3 t) := h1
    _ = (∑ i ∈ s, w i * (2 / κ i ^ 2)) * ρ⁻¹ ^ (-(3 / 2 : ℝ)) * riesz 3 t := by ring

/-- Readable two-length instance: `w₁ e^{-κ₁ r}/r + w₂ e^{-κ₂ r}/r` is admissible. -/
theorem two_length_admissible {w₁ w₂ κ₁ κ₂ : ℝ} (hw₁ : 0 ≤ w₁) (hw₂ : 0 ≤ w₂) (hκ₁ : 0 < κ₁) (hκ₂ : 0 < κ₂) :
    AdmissiblePotential (fun t => w₁ * g κ₁ t + w₂ * g κ₂ t) :=
  admissible_add (admissible_smul (yukawa_admissible hκ₁) hw₁) (admissible_smul (yukawa_admissible hκ₂) hw₂)

/-! ## Negative control: a signed combination is not admissible -/

/-- `g₁ - 2 g₂` (weights `1, -2`, screening `κ = 1, 2`). -/
noncomputable def signedMix : ℝ → ℝ := fun t => g 1 t - 2 * g 2 t

theorem signedMix_neg : signedMix (1 / 4) < 0 := by
  have hs : Real.sqrt (1 / 4 : ℝ) = 1 / 2 := by
    rw [show (1 / 4 : ℝ) = (1 / 2) ^ 2 by norm_num]
    exact Real.sqrt_sq (by norm_num)
  simp only [signedMix, g, hs]
  have he : Real.exp (-1 * (1 / 2)) = Real.exp (1 / 2) * Real.exp (-2 * (1 / 2)) := by
    rw [← Real.exp_add]; norm_num
  have hsq : Real.exp (1 / 2) * Real.exp (1 / 2) = Real.exp 1 := by
    rw [← Real.exp_add]; norm_num
  have h1 := Real.exp_one_lt_d9
  have hp := Real.exp_pos (1 / 2 : ℝ)
  have hq := Real.exp_pos (-2 * (1 / 2) : ℝ)
  have hlt : Real.exp (1 / 2) < 2 := by nlinarith
  rw [he]
  nlinarith

/-- **Negative control.** The weight-sign hypothesis cannot be dropped. -/
theorem signedMix_not_admissible : ¬ AdmissiblePotential signedMix := by
  intro H
  have := H.2.1 (1 / 4) (by norm_num)
  linarith [signedMix_neg]

end AutoresearchYukawaMix

#print axioms AutoresearchYukawaMix.admissible_add
#print axioms AutoresearchYukawaMix.admissible_smul
#print axioms AutoresearchYukawaMix.admissible_zero
#print axioms AutoresearchYukawaMix.admissible_sum
#print axioms AutoresearchYukawaMix.latticeEnergy_lt_top_of_le_riesz3
#print axioms AutoresearchYukawaMix.g_rescale
#print axioms AutoresearchYukawaMix.yukawa_any_density
#print axioms AutoresearchYukawaMix.yukawa_optimal_any_density
#print axioms AutoresearchYukawaMix.latticeEnergy_yukawa_rho_lt_top
#print axioms AutoresearchYukawaMix.yukawaMix_admissible
#print axioms AutoresearchYukawaMix.triangular_yukawaMix_optimal
#print axioms AutoresearchYukawaMix.latticeEnergy_yukawaMix_lt_top
#print axioms AutoresearchYukawaMix.yukawaMix_optimal_any_density
#print axioms AutoresearchYukawaMix.latticeEnergy_yukawaMix_rho_lt_top
#print axioms AutoresearchYukawaMix.two_length_admissible
#print axioms AutoresearchYukawaMix.signedMix_not_admissible

/-! ## Verifier block (paper stage, 2026-10-25): appended to a verbatim copy of YukawaMix.lean.
Statement pins (exact types re-stated and closed by the claimed theorem), definitional unfoldings, non-vacuity
instances, and a planted sorry of the verifier's own that must surface as sorryAx. -/

namespace VerifierH2Mix

open OAI.AtomicTriangular TriangularRiesz AutoresearchYukawa AutoresearchYukawaMix TriangularDensity
open scoped Pointwise

-- definitional unfoldings: the mixture is exactly the weighted sum of e^{-κ_i √t}/√t
example {ι : Type*} (s : Finset ι) (w κ : ι → ℝ) (t : ℝ) :
    yukawaMix s w κ t = ∑ i ∈ s, w i * (Real.exp (-(κ i) * Real.sqrt t) / Real.sqrt t) := rfl
example (κ t : ℝ) : g κ t = Real.exp (-κ * Real.sqrt t) / Real.sqrt t := rfl
example (ρ : ℝ) (C : Set Plane) : DensityRho ρ C ↔
    Filter.Tendsto (fun R : ℝ => (diskCount C R : ℝ) / (Real.pi * R ^ 2)) Filter.atTop (nhds ρ) := Iff.rfl

-- pointwise check of the screened-Coulomb form at t = r^2
example {κ r : ℝ} (hr : 0 < r) : g κ (r ^ 2) = Real.exp (-κ * r) / r := by
  simp only [g, Real.sqrt_sq hr.le]

-- statement pins
example {κ : ℝ} (hκ : 0 < κ) {ρ : ℝ} (hρ : 0 < ρ) :
    LocallyFinite ((Real.sqrt ρ)⁻¹ • A) ∧ DensityRho ρ ((Real.sqrt ρ)⁻¹ • A) ∧
      ∀ C : Set Plane, LocallyFinite C → DensityRho ρ C →
        energy (g κ) ((Real.sqrt ρ)⁻¹ • A) ≤ energy (g κ) C := yukawa_optimal_any_density hκ hρ
example {ι : Type*} (s : Finset ι) {w κ : ι → ℝ} (hw : ∀ i ∈ s, 0 ≤ w i) (hκ : ∀ i ∈ s, 0 < κ i)
    (C : Set Plane) (hC : LocallyFinite C) (hd : DensityOne C) :
    latticeEnergy (yukawaMix s w κ) ≤ energy (yukawaMix s w κ) C := triangular_yukawaMix_optimal s hw hκ C hC hd
example {ι : Type*} (s : Finset ι) {w κ : ι → ℝ} (hw : ∀ i ∈ s, 0 ≤ w i) (hκ : ∀ i ∈ s, 0 < κ i) :
    latticeEnergy (yukawaMix s w κ) < ⊤ := latticeEnergy_yukawaMix_lt_top s hw hκ

-- non-vacuity: a three-length mixture with weights (1, 2, 1/2) and screenings (1/2, 1, 3)
theorem v_three_length_finite :
    latticeEnergy (yukawaMix (Finset.univ : Finset (Fin 3)) ![1, 2, 1 / 2] ![1 / 2, 1, 3]) < ⊤ :=
  latticeEnergy_yukawaMix_lt_top _ (fun i _ => by fin_cases i <;> norm_num) (fun i _ => by fin_cases i <;> norm_num)

-- the mixture is strictly positive at t = 1 (so the energy is not trivially 0)
theorem v_mix_pos : 0 < yukawaMix (Finset.univ : Finset (Fin 3)) ![1, 2, 1 / 2] ![1 / 2, 1, 3] 1 := by
  simp only [yukawaMix, Fin.sum_univ_three, g, Real.sqrt_one, div_one]
  simp
  positivity

-- planted: must report sorryAx
theorem v_planted : AdmissiblePotential signedMix := sorry
theorem v_planted_use : False := signedMix_not_admissible v_planted

end VerifierH2Mix

#print axioms VerifierH2Mix.v_three_length_finite
#print axioms VerifierH2Mix.v_mix_pos
#print axioms VerifierH2Mix.v_planted
#print axioms VerifierH2Mix.v_planted_use
