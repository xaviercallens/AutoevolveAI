import Triangular.Riesz
import Triangular.RieszFinite
import Triangular.AnyDensity

/-!
# Controls and statement checks for D1/D1b/D2

The first three sections are kernel facts first written by the independent verification runs
(`results/discovery/D1/verification.md`, `D2/verification.md`), kept here so they ship with the release.
The last section (homogeneity of the Riesz corollary) was added by the producer after the pre-publication review.
-/

namespace TriangularControls

open OAI.AtomicTriangular TriangularDensity
open scoped ContDiff

/-! ## Statement shape (D1 verifier) -/

/-- `riesz s (r²) = r^{-s}` for `r > 0`: the potential is the Riesz kernel in the distance. -/
theorem riesz_sq (s r : ℝ) (hr : 0 < r) : TriangularRiesz.riesz s (r ^ 2) = r ^ (-s) := by
  unfold TriangularRiesz.riesz
  rw [← Real.rpow_natCast, ← Real.rpow_mul hr.le]
  congr 1
  push_cast
  ring

/-- Upstream's smoothness order `(⊤ : ℕ∞)` is `C^∞`, not analytic. -/
theorem smoothness_order_is_infty : (((⊤ : ℕ∞)) : WithTop ℕ∞) = ∞ := rfl

/-! ## Negative control (D1 verifier): `riesz (-2) = t` is not admissible -/

theorem riesz_neg_two_not_admissible : ¬ AdmissiblePotential (TriangularRiesz.riesz (-2)) := by
  intro h
  have h3 := h.2.2 1 1 one_pos
  have hfun : TriangularRiesz.riesz (-2) = fun t => t := by
    funext t
    unfold TriangularRiesz.riesz
    norm_num
  rw [hfun] at h3
  simp at h3 <;> linarith

/-! ## Density-one reduction (D2 verifier) -/

theorem densityRho_one_iff (C : Set Plane) : DensityRho 1 C ↔ DensityOne C := Iff.rfl

theorem rho_one (h : ℝ → ℝ) (hh : AdmissiblePotential h) (C : Set Plane) (hC : LocallyFinite C)
    (hd : DensityOne C) : latticeEnergy h ≤ energy h C := by
  have := universal_any_density h hh one_pos C hC hd
  simpa using this

/-! ## Homogeneity of the Riesz corollary (producer, post-review) -/

/-- The rescaled Riesz lattice energy is `ρ^{s/2}` times the density-one one, in `[0, ∞]`. -/
theorem riesz_lattice_homogeneous (s : ℝ) {ρ : ℝ} (hρ : 0 < ρ) :
    latticeEnergy (fun t => TriangularRiesz.riesz s (ρ⁻¹ * t)) =
      ENNReal.ofReal (ρ ^ (s / 2)) * latticeEnergy (TriangularRiesz.riesz s) := by
  unfold latticeEnergy
  rw [← ENNReal.tsum_mul_left]
  congr 1
  funext a
  rw [← ENNReal.ofReal_mul (Real.rpow_nonneg hρ.le _)]
  congr 1
  unfold TriangularRiesz.riesz
  beta_reduce
  rw [Real.mul_rpow (inv_nonneg.2 hρ.le) (sq_nonneg _), Real.inv_rpow hρ.le, ← Real.rpow_neg hρ.le, neg_neg]

/-- **Corollary (Riesz at every density).** `ρ^{s/2} Σ_{a ∈ A \ 0} |a|^{-s} ≤ E_s(C)` for density-`ρ` configurations. -/
theorem riesz_any_density_homogeneous {s : ℝ} (hs : 0 < s) {ρ : ℝ} (hρ : 0 < ρ) (C : Set Plane)
    (hC : LocallyFinite C) (hd : DensityRho ρ C) :
    ENNReal.ofReal (ρ ^ (s / 2)) * latticeEnergy (TriangularRiesz.riesz s) ≤ energy (TriangularRiesz.riesz s) C := by
  rw [← riesz_lattice_homogeneous s hρ]
  exact riesz_any_density hs hρ C hC hd

end TriangularControls
