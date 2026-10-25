import Autoresearch.DipolarExciton
import Triangular.AnyDensity

/-!
# Autoresearch 2026-10-25, H1 contribution module: bilayer exciton potential at every density, and the
# shifted-difference family

This module extends `Autoresearch.DipolarExciton` (kept unchanged and imported, so its four theorems
`dipolar_admissible`, `triangular_dipolar_optimal`, `latticeEnergy_dipolar_lt_top`, `h_not_admissible` keep the status
they were verified with). New here:

* `shiftDiff s c t = t^{-s/2} - (t + c)^{-s/2}` (in `t = r²`: `r^{-s} - (r² + c)^{-s/2}`) is `AdmissiblePotential`
  for every `s > 0` and `c ≥ 0` (`shiftDiff_admissible`); the bilayer exciton potential is `g d = 2 · shiftDiff 1 (d²)`
  (`g_eq_shiftDiff`). Negative control: for `c < 0`, `shiftDiff s c` is not admissible (`shiftDiff_not_admissible_of_neg`).
* Every density `ρ > 0`: the rescaled triangular lattice `ρ^{-1/2} A` has density `ρ` and minimises the energy of
  `g d` (and of `shiftDiff s c`) among all locally finite density-`ρ` configurations
  (`triangular_dipolar_optimal_any_density`, `triangular_shiftDiff_optimal_any_density`), via D2
  `TriangularDensity.triangular_optimal_any_density`.
* Non-vacuity at every density: `energy (g d) (ρ^{-1/2} A) < ⊤` (`energy_dipolar_any_density_lt_top`), so the
  every-density statement is not `⊤ ≤ ⊤`.

Scope. Classical point particles (no kinetic or zero-point energy); rigid dipoles perpendicular to the layers for `g d`.
For `s ≠ 1` the `shiftDiff` family is a mathematical generalisation only; no physical multipole model is claimed.
The complete-monotonicity step is elementary (Bernstein). Every optimality statement is conditional on upstream
`OAI.AtomicTriangular.universal_energy_minimum` (openai/math, AI-generated, not peer reviewed) and on the fidelity of its
definitions (`energy` = liminf of disk averages, `LocallyFinite`, `DensityOne`).
-/

namespace AutoresearchDipolarMultipolar

open OAI.AtomicTriangular TriangularRiesz
open scoped Pointwise

/-! ## The shifted-difference family -/

/-- Shifted difference of Riesz potentials in the variable `t = r²`. -/
noncomputable def shiftDiff (s c : ℝ) : ℝ → ℝ := fun t => t ^ (-(s / 2)) - (t + c) ^ (-(s / 2))

lemma sign_desc_gen (r : ℕ) (a : ℝ) :
    (-1 : ℝ) ^ r * (descPochhammer ℝ r).eval (-a) = (ascPochhammer ℝ r).eval a := by
  have hasc := ascPochhammer_eval_neg_eq_descPochhammer (R := ℝ) (-a) r
  rw [neg_neg] at hasc
  exact hasc.symm

lemma iteratedDeriv_shiftDiff (s c : ℝ) (hc : 0 ≤ c) (r : ℕ) {t : ℝ} (ht : 0 < t) :
    iteratedDeriv r (shiftDiff s c) t =
      (descPochhammer ℝ r).eval (-(s / 2)) * (t ^ (-(s / 2) - r) - (t + c) ^ (-(s / 2) - r)) := by
  have h1 : ContDiffAt ℝ r (fun x : ℝ => x ^ (-(s / 2))) t :=
    Real.contDiffAt_rpow_const_of_ne (ne_of_gt ht)
  have h2 : ContDiffAt ℝ r (fun x : ℝ => (x + c) ^ (-(s / 2))) t :=
    AutoresearchDipolar.contDiffAt_shift hc ht
  have hf : shiftDiff s c = (fun x : ℝ => x ^ (-(s / 2))) - fun x : ℝ => (x + c) ^ (-(s / 2)) := by
    funext x; simp [shiftDiff]
  rw [hf, iteratedDeriv_sub h1 h2, AutoresearchDipolar.iteratedDeriv_rpow, AutoresearchDipolar.iteratedDeriv_shift]
  ring

/-- **Shifted-difference lemma.** For every `s > 0` and `c ≥ 0`, `t ↦ t^{-s/2} - (t + c)^{-s/2}` is admissible
(smooth on `(0, ∞)`, nonnegative, completely monotone). The case `c > 0` asked for in the task is included. -/
theorem shiftDiff_admissible {s c : ℝ} (hs : 0 < s) (hc : 0 ≤ c) : AdmissiblePotential (shiftDiff s c) := by
  refine ⟨?_, ?_, ?_⟩
  · intro x hx
    have h1 : ContDiffAt ℝ (⊤ : ℕ∞) (fun x : ℝ => x ^ (-(s / 2))) x :=
      Real.contDiffAt_rpow_const_of_ne (ne_of_gt hx)
    have h2 : ContDiffAt ℝ (⊤ : ℕ∞) (fun x : ℝ => (x + c) ^ (-(s / 2))) x :=
      AutoresearchDipolar.contDiffAt_shift hc hx
    exact (h1.sub h2).contDiffWithinAt
  · intro t ht
    have := AutoresearchDipolar.diff_nonneg c (-(s / 2)) hc (by linarith) ht
    simpa [shiftDiff] using this
  · intro r t ht
    rw [iteratedDeriv_shiftDiff s c hc r ht]
    have hpos := ascPochhammer_pos r (s / 2) (by linarith)
    have hdiff := AutoresearchDipolar.diff_nonneg c (-(s / 2) - r) hc
      (by have : (0 : ℝ) ≤ r := Nat.cast_nonneg r; linarith) ht
    have hsg := sign_desc_gen r (s / 2)
    calc (0 : ℝ) ≤ (ascPochhammer ℝ r).eval (s / 2) *
          (t ^ (-(s / 2) - r) - (t + c) ^ (-(s / 2) - r)) := by positivity
      _ = (-1 : ℝ) ^ r * ((descPochhammer ℝ r).eval (-(s / 2)) *
          (t ^ (-(s / 2) - r) - (t + c) ^ (-(s / 2) - r))) := by
        rw [← hsg]; ring

/-- Admissibility is preserved by nonnegative constant multiples. -/
lemma admissible_const_mul {f : ℝ → ℝ} (hf : AdmissiblePotential f) {k : ℝ} (hk : 0 ≤ k) :
    AdmissiblePotential (fun t => k * f t) := by
  obtain ⟨h1, h2, h3⟩ := hf
  refine ⟨contDiffOn_const.mul h1, fun t ht => mul_nonneg hk (h2 t ht), ?_⟩
  intro r t ht
  have hcd : ContDiffAt ℝ r f t :=
    ((h1.contDiffAt (Ioi_mem_nhds ht)).of_le (by exact_mod_cast le_top))
  rw [iteratedDeriv_const_mul _ hcd]
  have := h3 r t ht
  calc (0 : ℝ) ≤ k * ((-1 : ℝ) ^ r * iteratedDeriv r f t) := mul_nonneg hk this
    _ = (-1 : ℝ) ^ r * (k * iteratedDeriv r f t) := by ring

/-- The bilayer exciton potential is twice the `s = 1`, `c = d²` shifted difference. -/
lemma g_eq_shiftDiff (d : ℝ) : AutoresearchDipolar.g d = fun t => 2 * shiftDiff 1 (d ^ 2) t := by
  funext t
  simp only [AutoresearchDipolar.g, shiftDiff]

/-- Consistency check: `dipolar_admissible` re-derived from the general lemma, for every real `d`
(the `0 < d` hypothesis of the original is not needed). -/
theorem dipolar_admissible_all (d : ℝ) : AdmissiblePotential (AutoresearchDipolar.g d) := by
  rw [g_eq_shiftDiff]
  exact admissible_const_mul (shiftDiff_admissible (by norm_num) (sq_nonneg d)) (by norm_num)

/-- **Negative control.** For `c < 0` the shifted difference takes a negative value at `t = -2c > 0`. -/
theorem shiftDiff_neg_of_neg {s c : ℝ} (hs : 0 < s) (hc : c < 0) : shiftDiff s c (-2 * c) < 0 := by
  have h1 : 0 < -2 * c + c := by linarith
  have hlt : (-2 * c) ^ (-(s / 2)) < (-2 * c + c) ^ (-(s / 2)) :=
    Real.rpow_lt_rpow_of_neg h1 (by linarith) (by linarith)
  simp only [shiftDiff]
  linarith

/-- **Negative control.** For `s > 0`, `c < 0`, `shiftDiff s c` is not admissible: the sign of `c` matters. -/
theorem shiftDiff_not_admissible_of_neg {s c : ℝ} (hs : 0 < s) (hc : c < 0) :
    ¬ AdmissiblePotential (shiftDiff s c) := by
  intro H
  have := H.2.1 (-2 * c) (by linarith)
  linarith [shiftDiff_neg_of_neg hs hc]

/-! ## Every density -/

/-- **H1, every density.** For `d > 0` and `ρ > 0` the rescaled triangular lattice `ρ^{-1/2} A` is locally finite,
has density `ρ`, and its bilayer-exciton energy is `≤` that of every locally finite density-`ρ` configuration. -/
theorem triangular_dipolar_optimal_any_density {d : ℝ} (hd : 0 < d) {ρ : ℝ} (hρ : 0 < ρ) :
    LocallyFinite ((Real.sqrt ρ)⁻¹ • A) ∧ TriangularDensity.DensityRho ρ ((Real.sqrt ρ)⁻¹ • A) ∧
      ∀ C : Set Plane, LocallyFinite C → TriangularDensity.DensityRho ρ C →
        energy (AutoresearchDipolar.g d) ((Real.sqrt ρ)⁻¹ • A) ≤ energy (AutoresearchDipolar.g d) C :=
  TriangularDensity.triangular_optimal_any_density _ (AutoresearchDipolar.dipolar_admissible hd) hρ

/-- **Shifted-difference family, every density.** Same conclusion for `shiftDiff s c`, `s > 0`, `c ≥ 0`. -/
theorem triangular_shiftDiff_optimal_any_density {s c : ℝ} (hs : 0 < s) (hc : 0 ≤ c) {ρ : ℝ} (hρ : 0 < ρ) :
    LocallyFinite ((Real.sqrt ρ)⁻¹ • A) ∧ TriangularDensity.DensityRho ρ ((Real.sqrt ρ)⁻¹ • A) ∧
      ∀ C : Set Plane, LocallyFinite C → TriangularDensity.DensityRho ρ C →
        energy (shiftDiff s c) ((Real.sqrt ρ)⁻¹ • A) ≤ energy (shiftDiff s c) C :=
  TriangularDensity.triangular_optimal_any_density _ (shiftDiff_admissible hs hc) hρ

/-- **Shifted-difference family, density one.** -/
theorem triangular_shiftDiff_optimal {s c : ℝ} (hs : 0 < s) (hc : 0 ≤ c) (C : Set Plane) (hC : LocallyFinite C)
    (hdens : DensityOne C) : latticeEnergy (shiftDiff s c) ≤ energy (shiftDiff s c) C :=
  (universal_energy_minimum (shiftDiff s c) C (shiftDiff_admissible hs hc) hC hdens).1

/-! ## Non-vacuity at every density -/

/-- Pointwise bound at density `ρ`: `g_d(t/ρ) ≤ d² ρ^{3/2} t^{-3/2}`. -/
lemma g_scaled_le (d : ℝ) {ρ : ℝ} (hρ : 0 < ρ) {t : ℝ} (ht : 0 < t) :
    AutoresearchDipolar.g d (ρ⁻¹ * t) ≤ (d ^ 2 * (ρ⁻¹) ^ (-((3 : ℝ) / 2))) * riesz 3 t := by
  have h := AutoresearchDipolar.g_le d (mul_pos (inv_pos.2 hρ) ht)
  have e : riesz 3 (ρ⁻¹ * t) = (ρ⁻¹) ^ (-((3 : ℝ) / 2)) * riesz 3 t := by
    simp only [riesz]
    exact Real.mul_rpow (inv_pos.2 hρ).le ht.le
  rw [e] at h
  linarith

/-- The lattice side at density `ρ` is finite. -/
theorem latticeEnergy_dipolar_scaled_lt_top (d : ℝ) {ρ : ℝ} (hρ : 0 < ρ) :
    latticeEnergy (fun t => AutoresearchDipolar.g d (ρ⁻¹ * t)) < ⊤ := by
  have hR := latticeEnergy_riesz_lt_top (s := 3) (by norm_num)
  set K : ℝ := d ^ 2 * (ρ⁻¹) ^ (-((3 : ℝ) / 2)) with hK
  have hK0 : 0 ≤ K := mul_nonneg (sq_nonneg d) (Real.rpow_nonneg (inv_pos.2 hρ).le _)
  have hle : latticeEnergy (fun t => AutoresearchDipolar.g d (ρ⁻¹ * t)) ≤
      ENNReal.ofReal K * latticeEnergy (riesz 3) := by
    unfold latticeEnergy
    rw [← ENNReal.tsum_mul_left]
    refine ENNReal.tsum_le_tsum fun a => ?_
    have hpos : 0 < ‖a.val‖ ^ 2 := by
      have := a.2.2
      positivity
    rw [← ENNReal.ofReal_mul hK0]
    exact ENNReal.ofReal_le_ofReal (g_scaled_le d hρ hpos)
  exact lt_of_le_of_lt hle (ENNReal.mul_lt_top ENNReal.ofReal_lt_top hR)

/-- **H1b, every density.** The bilayer-exciton energy of the optimal density-`ρ` configuration `ρ^{-1/2} A` is
finite, so `triangular_dipolar_optimal_any_density` is not the trivial `⊤ ≤ ⊤`. -/
theorem energy_dipolar_any_density_lt_top {d : ℝ} (hd : 0 < d) {ρ : ℝ} (hρ : 0 < ρ) :
    energy (AutoresearchDipolar.g d) ((Real.sqrt ρ)⁻¹ • A) < ⊤ := by
  rw [TriangularDensity.attained _ (AutoresearchDipolar.dipolar_admissible hd) hρ]
  exact latticeEnergy_dipolar_scaled_lt_top d hρ

end AutoresearchDipolarMultipolar

#print axioms AutoresearchDipolarMultipolar.shiftDiff_admissible
#print axioms AutoresearchDipolarMultipolar.admissible_const_mul
#print axioms AutoresearchDipolarMultipolar.g_eq_shiftDiff
#print axioms AutoresearchDipolarMultipolar.dipolar_admissible_all
#print axioms AutoresearchDipolarMultipolar.shiftDiff_not_admissible_of_neg
#print axioms AutoresearchDipolarMultipolar.triangular_dipolar_optimal_any_density
#print axioms AutoresearchDipolarMultipolar.triangular_shiftDiff_optimal_any_density
#print axioms AutoresearchDipolarMultipolar.triangular_shiftDiff_optimal
#print axioms AutoresearchDipolarMultipolar.latticeEnergy_dipolar_scaled_lt_top
#print axioms AutoresearchDipolarMultipolar.energy_dipolar_any_density_lt_top
