import Mathlib.Tactic
import Mathlib.Analysis.SpecialFunctions.Log.Basic

/-!
# Proposal 4, K1 (2026-10-27): algebraic core of the exergy audit of the "start cold" DAC insight

Statements about a stylised published-type model (van 't Hoff Henry loading + sensible heat, temperature swing
from `Tc` or `T0` up to `Th`), NOT about real plants. The transcendental parts (exp, log enclosures over
parameter boxes) are interval arithmetic outside the kernel (Tier C); this file holds the exact algebra.

* `carnot_in_mem_unit`: heat supplied above ambient has exergy weight `1 - T0/T` in `(0, 1)`
  (the preregistered positive control: an all-`T ≥ T0` path has weights in `(0, 1)`, no refrigeration term).
* `refrig_weight_lt_one`: rejecting heat at `T0/2 < T < T0` costs `T0/T - 1 ∈ (0, 1)` of work per joule.
* `numerator_factor`: `q (T0/Tc - 1) - R (T0 - Tc) = (T0 - Tc) (q/Tc - R)`.
* `co2_term_penalises_cold`: the CO2-only term of the exergy benefit, `A = -q (T0/Tc - 1) + R (T0 - Tc)`, is
  negative whenever `q > R Tc` (refrigeration of the CO2 adsorption heat). This is NOT the sign of the whole
  benefit: the N2 term `λ B` and the sensible term `(1 - r) γ D` can outweigh it, and in the published model's
  own data they do (see results/proposal4/2026-10-27/K1/RESULT.md).
* `benefit_affine_in_r`, `worst_case_full_recovery`: `β(r) = A + λ B + (1 - r) γ D`; if `γ D ≥ 0` then
  `β(1) ≤ β(r)` for every `r ≤ 1` (full recovery is the worst case for a cold start).
* `lambda_threshold_iff`: for `B > 0`, `0 < A + λ B ↔ -A / B < λ` (the closed-form N2 threshold at r = 1).
* `co2_term_facevalue_favours_cold`: the CO2-only face-value term `A_fv = R (T0 - Tc)` is positive.
* `threshold_iff`: for `R D > 0`, `-N + γ R D > 0 ↔ γ > N / (R D)` (the closed-form survival threshold).
* `wmin_pure_pos`, `wmin_pure_strictAnti`: `R T0 log(1/x)` is positive for `0 < x < 1` and decreasing in `x`.
-/

namespace DacExergy

theorem carnot_in_mem_unit {T0 T : ℝ} (h0 : 0 < T0) (hT : T0 < T) :
    0 < 1 - T0 / T ∧ 1 - T0 / T < 1 := by
  have hTpos : 0 < T := lt_trans h0 hT
  constructor
  · have : T0 / T < 1 := (div_lt_one hTpos).mpr hT
    linarith
  · have : 0 < T0 / T := div_pos h0 hTpos
    linarith

theorem refrig_weight_lt_one {T0 T : ℝ} (h0 : 0 < T0) (hlo : T0 / 2 < T) (hhi : T < T0) :
    0 < T0 / T - 1 ∧ T0 / T - 1 < 1 := by
  have hTpos : 0 < T := by linarith
  constructor
  · have : 1 < T0 / T := (one_lt_div hTpos).mpr hhi
    linarith
  · have : T0 / T < 2 := (div_lt_iff₀ hTpos).mpr (by linarith)
    linarith

theorem numerator_factor (q R T0 Tc : ℝ) (hTc : Tc ≠ 0) :
    q * (T0 / Tc - 1) - R * (T0 - Tc) = (T0 - Tc) * (q / Tc - R) := by
  have h : T0 / Tc - 1 = (T0 - Tc) / Tc := by
    rw [sub_div, div_self hTc]
  rw [h, mul_sub, div_eq_mul_inv, div_eq_mul_inv]
  ring

theorem co2_term_penalises_cold {q R T0 Tc : ℝ} (hTc : 0 < Tc) (hlt : Tc < T0) (hq : R * Tc < q) :
    -(q * (T0 / Tc - 1)) + R * (T0 - Tc) < 0 := by
  have h := numerator_factor q R T0 Tc hTc.ne'
  have h1 : 0 < T0 - Tc := by linarith
  have h2 : 0 < q / Tc - R := by
    rw [sub_pos, lt_div_iff₀ hTc]
    linarith
  have h3 : 0 < (T0 - Tc) * (q / Tc - R) := mul_pos h1 h2
  linarith

theorem co2_term_facevalue_favours_cold {R T0 Tc : ℝ} (hR : 0 < R) (hlt : Tc < T0) :
    0 < R * (T0 - Tc) := mul_pos hR (by linarith)

theorem threshold_iff {N R D γ : ℝ} (hRD : 0 < R * D) :
    0 < -N + γ * (R * D) ↔ N / (R * D) < γ := by
  rw [div_lt_iff₀ hRD]
  constructor <;> intro h <;> linarith

theorem wmin_pure_pos {R T0 x : ℝ} (hR : 0 < R) (hT : 0 < T0) (hx0 : 0 < x) (hx1 : x < 1) :
    0 < R * T0 * Real.log (1 / x) := by
  have : 0 < Real.log (1 / x) := Real.log_pos (by rw [lt_div_iff₀ hx0]; linarith)
  positivity

theorem wmin_pure_strictAnti {R T0 x y : ℝ} (hR : 0 < R) (hT : 0 < T0) (hx0 : 0 < x) (hxy : x < y) :
    R * T0 * Real.log (1 / y) < R * T0 * Real.log (1 / x) := by
  have hy0 : 0 < y := lt_trans hx0 hxy
  have : Real.log (1 / y) < Real.log (1 / x) :=
    Real.log_lt_log (by positivity) (one_div_lt_one_div_of_lt hx0 hxy)
  have hRT : 0 < R * T0 := mul_pos hR hT
  nlinarith

theorem benefit_affine_in_r (A B D lam gam r : ℝ) :
    A + lam * B + (1 - r) * gam * D = (A + lam * B) + (1 - r) * (gam * D) := by ring

theorem worst_case_full_recovery {A B D lam gam r : ℝ} (hgD : 0 ≤ gam * D) (hr : r ≤ 1) :
    A + lam * B + (1 - 1) * gam * D ≤ A + lam * B + (1 - r) * gam * D := by
  have h1 : 0 ≤ 1 - r := by linarith
  have h2 : 0 ≤ (1 - r) * (gam * D) := mul_nonneg h1 hgD
  nlinarith

theorem lambda_threshold_iff {A B lam : ℝ} (hB : 0 < B) :
    0 < A + lam * B ↔ -A / B < lam := by
  rw [div_lt_iff₀ hB]
  constructor <;> intro h <;> linarith

/-- Rational instance (R = 8.314 J/(mol K), q = 40 kJ/mol, Tc = 200 K, T0 = 298.15 K): the full-recovery
CO2-only exergy term of a cold start is negative. -/
theorem instance_r1 :
    -((40000 : ℝ) * ((29815 / 100) / 200 - 1)) + (4157 / 500) * ((29815 / 100) - 200) < 0 := by
  norm_num

end DacExergy

#print axioms DacExergy.carnot_in_mem_unit
#print axioms DacExergy.refrig_weight_lt_one
#print axioms DacExergy.numerator_factor
#print axioms DacExergy.co2_term_penalises_cold
#print axioms DacExergy.benefit_affine_in_r
#print axioms DacExergy.worst_case_full_recovery
#print axioms DacExergy.lambda_threshold_iff
#print axioms DacExergy.co2_term_facevalue_favours_cold
#print axioms DacExergy.threshold_iff
#print axioms DacExergy.wmin_pure_pos
#print axioms DacExergy.wmin_pure_strictAnti
#print axioms DacExergy.instance_r1
