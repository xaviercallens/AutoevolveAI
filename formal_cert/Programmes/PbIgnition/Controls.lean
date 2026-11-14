import Mathlib.Tactic
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-!
# Planted negative controls for PbIgnition/Core.lean (each MUST fail to elaborate)

* `ctl_mix_21` : tampered optimum 1/21 instead of 1/20 (false at x = 1/6), same proof script.
* `ctl_coeff_7` : tampered e-e coefficient 7 instead of 4.375 (false at t = 1), same proof script.
* `ctl_wrong_range` : the derivative bound claimed on [0, 2] (false at t = 2), same proof script.
Compiling this file must report an error for each of the three declarations.
-/

namespace PbIgnitionControls

theorem rpow_25_le_sq (t : ℝ) (h0 : 0 ≤ t) (h1 : t ≤ 1) : t ^ (2.5 : ℝ) ≤ t ^ 2 := by
  have h := Real.rpow_le_rpow_of_exponent_ge' h0 h1 (show (0 : ℝ) ≤ 2 by norm_num) (show (2 : ℝ) ≤ 2.5 by norm_num)
  have h2 : t ^ (2 : ℝ) = t ^ 2 := by
    exact_mod_cast Real.rpow_natCast t 2
  rw [h2] at h
  exact h

theorem ctl_mix_21 (x : ℝ) : 21 * (x * (1 - x)) ≤ (1 + 4 * x) ^ 2 := by
  nlinarith [sq_nonneg (6 * x - 1)]

theorem ctl_coeff_7 (t : ℝ) (h0 : 0 ≤ t) (h1 : t ≤ 1) :
    0 < 1 + 2.2 * t + 3 * t ^ 2 - 7 * t ^ (2.5 : ℝ) := by
  have h := rpow_25_le_sq t h0 h1
  nlinarith [h, sq_nonneg t]

theorem ctl_wrong_range (t : ℝ) (h0 : 0 ≤ t) (h1 : t ≤ 2) :
    0 < 1 + 2.2 * t + 3 * t ^ 2 - 4.375 * t ^ (2.5 : ℝ) := by
  have h := rpow_25_le_sq t h0 (by linarith)
  nlinarith [h, sq_nonneg t]

end PbIgnitionControls
