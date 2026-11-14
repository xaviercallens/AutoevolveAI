import Programmes.LowDissE3.Core

/-!
# E3 controls that must PASS (positive) or must FAIL as stated (negative, kernel-checked refutations of perturbed data)

* `esposito_sandwich` (positive control P1): at `P̃ = 1` (`K = 2`) the efficiency bound over all `ζ ∈ [-1,1]` lies in
  `[1/2, 1/(2-c)]`, i.e. `η_C/2 ≤ η* ≤ η_C/(2-η_C)` (Esposito et al. 2010 EMP bounds, in units `η/η_C`), attained at the
  endpoints `ζ = ∓1`.
* `inst_*` : exact rational instance `c = 48/49`, `K = 2` (roots `5/7` at `ζ = -1` and `1/5` at `ζ = 1`).
* `pert_*` (negative control N1): the perturbed quadratic `Gp(ζ,w) = G(-ζ,w)` (the factor `(1-ζ)+(1+ζ)w` replaced by
  `(1+ζ)+(1-ζ)w`) has roots INCREASING in `ζ` on the same rational instance, so the conclusion `w₂ < w₁` of
  `root_strict_anti` fails for it, and its `η̃` DEcreases from `ζ=-1` to `ζ=1`.
-/

namespace LowDissE3

theorem inst_root_neg : G (48 / 49) 2 (-1) (5 / 7) = 0 := by unfold G; norm_num
theorem inst_root_pos : G (48 / 49) 2 1 (1 / 5) = 0 := by unfold G; norm_num

theorem inst_eta_neg : etaPlus (48 / 49) 2 (-1) = 1 / 2 := by
  have := root_unique (c := 48 / 49) (K := 2) (by norm_num) (by norm_num) (by norm_num)
    (by norm_num) (by norm_num) (w := 5 / 7) (by norm_num) inst_root_neg
  unfold etaPlus; rw [← this]; norm_num

theorem inst_eta_pos : etaPlus (48 / 49) 2 1 = 49 / 50 := by
  have := root_unique (c := 48 / 49) (K := 2) (by norm_num) (by norm_num) (by norm_num)
    (by norm_num) (by norm_num) (w := 1 / 5) (by norm_num) inst_root_pos
  unfold etaPlus; rw [← this]; norm_num

/-- Perturbed quadratic of negative control N1. -/
noncomputable def Gp (c K ζ w : ℝ) : ℝ := G c K (-ζ) w

/-- Perturbed roots on the rational instance: `1/5` at `ζ = -1`, `5/7` at `ζ = 1`. -/
theorem pert_root_at_neg : Gp (48 / 49) 2 (-1) (1 / 5) = 0 := by unfold Gp G; norm_num
theorem pert_root_at_pos : Gp (48 / 49) 2 1 (5 / 7) = 0 := by unfold Gp G; norm_num

/-- The perturbed roots increase with `ζ` (`1/5 < 5/7`), the opposite of `root_strict_anti`'s conclusion. -/
theorem pert_roots_increase : (1 / 5 : ℝ) < 5 / 7 := by norm_num

/-- The perturbed efficiency decreases: `η̃'(ζ=-1) = 49/50 > 1/2 = η̃'(ζ=1)`; monotonicity FAILS for the perturbed formula. -/
theorem pert_eta_not_mono :
    ¬ (etaPlus (48 / 49) 2 (-(-1)) ≤ etaPlus (48 / 49) 2 (-(1))) := by
  have h1 : etaPlus (48 / 49) 2 (-(-1 : ℝ)) = 49 / 50 := by
    rw [neg_neg]; exact inst_eta_pos
  have h2 : etaPlus (48 / 49) 2 (-(1 : ℝ)) = 1 / 2 := inst_eta_neg
  rw [h1, h2]; norm_num

/-- Positive control P1: Esposito et al. EMP sandwich at `P̃ = 1`. -/
theorem esposito_sandwich {c ζ : ℝ} (hc0 : 0 < c) (hc1 : c < 1) (h1 : -1 ≤ ζ) (h2 : ζ ≤ 1) :
    1 / 2 ≤ etaPlus c 2 ζ ∧ etaPlus c 2 ζ ≤ 1 / (2 - c) := by
  have hK : (1 : ℝ) < 2 := by norm_num
  have hlo : etaPlus c 2 (-1) = 1 / 2 := by
    have hpos : 0 < 1 - c / 2 := by linarith
    have hr : G c 2 (-1) (Real.sqrt (1 - c / 2)) = 0 := by
      have := Real.sq_sqrt hpos.le
      unfold G; nlinarith
    have := root_unique (c := c) (K := 2) hc0 hc1 hK (by norm_num) (by norm_num)
      (Real.sqrt_nonneg _) hr
    unfold etaPlus; rw [← this, Real.sq_sqrt hpos.le]
    field_simp; ring
  constructor
  · rw [← hlo]; exact etaPlus_mono hc0 hc1 hK le_rfl h1 h2
  · have := etaPlus_le_one_value hc0 hc1 hK h1 h2
    have e : ((2 : ℝ) - 1) / (2 - c) = 1 / (2 - c) := by norm_num
    rw [e] at this; exact this

end LowDissE3
