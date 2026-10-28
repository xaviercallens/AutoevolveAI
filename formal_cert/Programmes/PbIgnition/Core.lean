import Mathlib.Tactic
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-!
# E1 (proposal 4): two exact facts used by the certified p-11B ideal-ignition analysis

Model: Wurzel & Hsu, arXiv 2105.10954, eqs (6), (41), (D1)-(D4); bremsstrahlung bracket
gamma(t) = Zeff (1 + 1.78 t^1.34) + 2.12 t (1 + 1.1 t + t^2 - 1.25 t^2.5)  (W-H eq D2 = Ochs-Fisch eq 14).

* `optimal_mix` : with boron fraction `x = n_B/n_i`, `n_p n_B / n_e^2 = x(1-x)/(1+4x)^2 ≤ 1/20`, equality iff
  `x = 1/6` (W-H footnote 138, k_p = 1/2, k_B = 1/10).
* `ee_term_deriv_pos` : the derivative of the electron-electron term t(1 + 1.1t + t^2 - 1.25 t^2.5), namely
  `1 + 2.2 t + 3 t^2 - 4.375 t^2.5`, is positive for `t ∈ [0,1]`; with the obviously increasing
  `Zeff (1 + 1.78 t^1.34)` this gives that `sqrt(T_e) gamma(T_e/m_e c^2)` increases in `T_e ≤ m_e c^2`, so
  P_B increases with `T_e/T_i` (the calculus step derivative > 0 ⇒ monotone is NOT formalised here; Tier C).

These are statements about the model's formulas only, not about any plasma or device.
-/

namespace PbIgnition

theorem optimal_mix (x : ℝ) : 20 * (x * (1 - x)) ≤ (1 + 4 * x) ^ 2 := by
  nlinarith [sq_nonneg (6 * x - 1)]

theorem optimal_mix_eq (x : ℝ) : 20 * (x * (1 - x)) = (1 + 4 * x) ^ 2 ↔ x = 1 / 6 := by
  constructor
  · intro h
    have h2 : (6 * x - 1) ^ 2 = 0 := by nlinarith
    have : 6 * x - 1 = 0 := by
      rcases sq_eq_zero_iff.mp h2 with h3
      exact h3
    linarith
  · intro h
    subst h
    norm_num

/-- `t^(5/2) ≤ t^2` on `[0,1]`. -/
theorem rpow_25_le_sq (t : ℝ) (h0 : 0 ≤ t) (h1 : t ≤ 1) : t ^ (2.5 : ℝ) ≤ t ^ 2 := by
  have h := Real.rpow_le_rpow_of_exponent_ge' h0 h1 (show (0 : ℝ) ≤ 2 by norm_num) (show (2 : ℝ) ≤ 2.5 by norm_num)
  have h2 : t ^ (2 : ℝ) = t ^ 2 := by
    exact_mod_cast Real.rpow_natCast t 2
  rw [h2] at h
  exact h

theorem ee_term_deriv_pos (t : ℝ) (h0 : 0 ≤ t) (h1 : t ≤ 1) :
    0 < 1 + 2.2 * t + 3 * t ^ 2 - 4.375 * t ^ (2.5 : ℝ) := by
  have h := rpow_25_le_sq t h0 h1
  nlinarith [h, sq_nonneg t]

end PbIgnition

#print axioms PbIgnition.optimal_mix
#print axioms PbIgnition.optimal_mix_eq
#print axioms PbIgnition.rpow_25_le_sq
#print axioms PbIgnition.ee_term_deriv_pos
