/-
Cross-survey BAO consistency exercise (slug eboss_vs_desi): kernel-verified
algebraic skeleton of the TENSION STATISTIC actually evaluated in
scripts/eboss_vs_desi/bao_lib.py::tension and fit_eboss_vs_desi.py.

The fit compares two independent flat-ΛCDM posteriors, SDSS/eBOSS DR16 (S)
and DESI DR2 (D), each summarised by its posterior mean p = (Ωₘ, h r_d) and
its 2×2 posterior covariance C. The preregistered statistic is DESI's
eq.(18)-type Gaussian parameter-difference chi-square

    dp = p_S − p_D,   C = C_S + C_D,   χ² = dpᵀ C⁻¹ dp,   (2 dof → PTE → N_σ)

(bao_lib.py lines 477-479: `dp = p1 - p2; C = c1 + c2; chi2 = dp @ solve(C, dp)`),
together with the per-parameter 1D pulls |dp_k| / √(C_kk).

Scope, deliberately (same policy as BAO_FlatLCDM.lean / DESI_DR2_wCDM.lean):
exact facts about the STATISTIC, not a theorem "about the sky":
  * the 1D squared pull (μ₁−μ₂)²/(σ₁²+σ₂²) is symmetric in the two surveys,
    nonnegative, and zero iff the two means coincide;
  * for a symmetric 2×2 covariance C = [[a,b],[b,c]] the closed form
    (c d₁² − 2b d₁d₂ + a d₂²)/(ac − b²) IS Mathlib's `d ⬝ᵥ (C⁻¹ *ᵥ d)`
    (so nothing below is about an ad-hoc formula: it is the matrix expression
    the code evaluates via `np.linalg.solve`);
  * whenever C is positive definite (a > 0, ac − b² > 0: Sylvester), χ² ≥ 0,
    and χ² = 0 iff dp = 0 -- the property that makes "N_σ" a distance;
  * the two-survey statistic is symmetric under swapping S ↔ D (the fit's
    N_σ does not depend on which survey is called "1");
  * the sum of two positive-definite 2×2 covariances is positive definite, so
    the inverse taken by `np.linalg.solve` in the fit exists whenever both
    posterior covariances are PD.
Literature: docs/literature/EBOSS_VS_DESI_LITERATURE_REVIEW_2026.md.
Numbers from the fit (results/eboss_vs_desi/fit.json): χ² = 1.932, 2 dof,
PTE = 0.381, N_σ = 0.877; nothing numeric is asserted here.
-/
import Mathlib.Analysis.Real.Sqrt
import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp

namespace ANSE.BAOConsistency

open Matrix

/-! ### 1D Gaussian pull -/

/-- Squared 1D Gaussian difference statistic between two independent
measurements `μ₁ ± σ₁` and `μ₂ ± σ₂`: `(μ₁ − μ₂)² / (σ₁² + σ₂²)`. Its square
root is the per-parameter `one_d_sigma` value reported by
`bao_lib.tension` (there `C_kk = σ₁ₖ² + σ₂ₖ²` because `C = C_S + C_D`). -/
noncomputable def tension1D (μ1 σ1 μ2 σ2 : ℝ) : ℝ := (μ1 - μ2) ^ 2 / (σ1 ^ 2 + σ2 ^ 2)

/-- Swapping the two surveys leaves the 1D statistic unchanged (no hypotheses
at all: it is an identity of real expressions, even where the denominator is 0). -/
theorem tension1D_symm (μ1 σ1 μ2 σ2 : ℝ) :
    tension1D μ1 σ1 μ2 σ2 = tension1D μ2 σ2 μ1 σ1 := by
  unfold tension1D
  ring

/-- The 1D statistic is never negative (again with no hypotheses: in Lean
`x / 0 = 0`, and otherwise it is a square over a sum of squares). -/
theorem tension1D_nonneg (μ1 σ1 μ2 σ2 : ℝ) : 0 ≤ tension1D μ1 σ1 μ2 σ2 := by
  unfold tension1D
  positivity

/-- With `σ1 > 0` the 1D statistic vanishes exactly when the two central
values agree. (The case `σ1 = 0 < σ2` follows by first applying
`tension1D_symm`; it is not stated separately here.) -/
theorem tension1D_eq_zero_iff {μ1 σ1 μ2 σ2 : ℝ} (hσ : 0 < σ1) :
    tension1D μ1 σ1 μ2 σ2 = 0 ↔ μ1 = μ2 := by
  unfold tension1D
  have hden : σ1 ^ 2 + σ2 ^ 2 ≠ 0 := by positivity
  rw [div_eq_zero_iff]
  constructor
  · rintro (hnum | hd)
    · have h := (pow_eq_zero_iff two_ne_zero).mp hnum
      linarith
    · exact absurd hd hden
  · intro h
    left
    rw [h]
    ring

/-! ### 2-parameter chi-square with the full 2×2 covariance -/

/-- Closed form of `dᵀ C⁻¹ d` for the symmetric 2×2 covariance
`C = [[a, b], [b, c]]` and difference vector `d = (d₁, d₂)`:
`(c d₁² − 2 b d₁ d₂ + a d₂²) / (a c − b²)`. This is the quantity
`dp @ np.linalg.solve(C, dp)` in `bao_lib.tension`, specialised to the 2×2 case
`(Ωₘ, h r_d)` used by the fit. `chi2_eq_dotProduct_inv_mulVec` below proves it
equals Mathlib's own matrix expression, so this definition hides nothing. -/
noncomputable def chi2 (a b c d1 d2 : ℝ) : ℝ :=
  (c * d1 ^ 2 - 2 * b * d1 * d2 + a * d2 ^ 2) / (a * c - b ^ 2)

/-- The closed form agrees with Mathlib's `Matrix` inverse: for
`C = !![a, b; b, c]` with `det C = a c − b² ≠ 0`,
`![d₁, d₂] ⬝ᵥ (C⁻¹ *ᵥ ![d₁, d₂]) = chi2 a b c d₁ d₂`. -/
theorem chi2_eq_dotProduct_inv_mulVec (a b c d1 d2 : ℝ) (hdet : a * c - b ^ 2 ≠ 0) :
    ![d1, d2] ⬝ᵥ ((!![a, b; b, c])⁻¹ *ᵥ ![d1, d2]) = chi2 a b c d1 d2 := by
  have hinv : (!![a, b; b, c])⁻¹ =
      !![c / (a * c - b ^ 2), -b / (a * c - b ^ 2);
         -b / (a * c - b ^ 2), a / (a * c - b ^ 2)] := by
    apply Matrix.inv_eq_right_inv
    rw [Matrix.mul_fin_two, Matrix.one_fin_two]
    ext i j
    fin_cases i <;> fin_cases j <;> simp [Matrix.of_apply] <;> field_simp <;> ring
  rw [hinv]
  simp [chi2, Matrix.mulVec, dotProduct, Fin.sum_univ_two]
  field_simp
  ring

/-- For a positive-definite covariance (`a > 0` and `a c − b² > 0`, Sylvester's
criterion for a symmetric 2×2 matrix) the chi-square is nonnegative for every
difference vector. -/
theorem chi2_nonneg {a b c : ℝ} (ha : 0 < a) (hdet : 0 < a * c - b ^ 2) (d1 d2 : ℝ) :
    0 ≤ chi2 a b c d1 d2 := by
  unfold chi2
  apply div_nonneg _ hdet.le
  have key : a * (c * d1 ^ 2 - 2 * b * d1 * d2 + a * d2 ^ 2)
      = (a * d2 - b * d1) ^ 2 + (a * c - b ^ 2) * d1 ^ 2 := by ring
  have hprod : 0 ≤ a * (c * d1 ^ 2 - 2 * b * d1 * d2 + a * d2 ^ 2) := by
    rw [key]
    have h1 : 0 ≤ (a * d2 - b * d1) ^ 2 := sq_nonneg _
    have h2 : 0 ≤ (a * c - b ^ 2) * d1 ^ 2 := mul_nonneg hdet.le (sq_nonneg _)
    linarith
  by_contra hneg
  have := mul_neg_of_pos_of_neg ha (not_le.mp hneg)
  linarith

/-- For a positive-definite covariance the chi-square vanishes exactly when the
two parameter vectors coincide (`d₁ = d₂ = 0`): the statistic is a genuine
distance, zero only for identical (Ωₘ, h r_d) posteriors means. -/
theorem chi2_eq_zero_iff {a b c : ℝ} (ha : 0 < a) (hdet : 0 < a * c - b ^ 2) (d1 d2 : ℝ) :
    chi2 a b c d1 d2 = 0 ↔ d1 = 0 ∧ d2 = 0 := by
  unfold chi2
  rw [div_eq_zero_iff]
  constructor
  · rintro (hnum | hd)
    · have key : (a * d2 - b * d1) ^ 2 + (a * c - b ^ 2) * d1 ^ 2 = 0 := by
        have h0 : a * (c * d1 ^ 2 - 2 * b * d1 * d2 + a * d2 ^ 2) = 0 := by
          rw [hnum, mul_zero]
        calc (a * d2 - b * d1) ^ 2 + (a * c - b ^ 2) * d1 ^ 2
            = a * (c * d1 ^ 2 - 2 * b * d1 * d2 + a * d2 ^ 2) := by ring
          _ = 0 := h0
      have hsq1 : 0 ≤ (a * d2 - b * d1) ^ 2 := sq_nonneg _
      have hsq2 : 0 ≤ (a * c - b ^ 2) * d1 ^ 2 := mul_nonneg hdet.le (sq_nonneg _)
      have h2' : (a * c - b ^ 2) * d1 ^ 2 = 0 := by linarith
      have hd1sq : d1 ^ 2 = 0 := by
        rcases mul_eq_zero.mp h2' with h | h
        · exact absurd h hdet.ne'
        · exact h
      have hd1 : d1 = 0 := (pow_eq_zero_iff two_ne_zero).mp hd1sq
      have h1' : (a * d2 - b * d1) ^ 2 = 0 := by linarith
      have hlin : a * d2 - b * d1 = 0 := (pow_eq_zero_iff two_ne_zero).mp h1'
      have hd2 : d2 = 0 := by
        rw [hd1, mul_zero, sub_zero] at hlin
        rcases mul_eq_zero.mp hlin with h | h
        · exact absurd h ha.ne'
        · exact h
      exact ⟨hd1, hd2⟩
    · exact absurd hd hdet.ne'
  · rintro ⟨rfl, rfl⟩
    left
    ring

/-! ### The two-survey statistic as the fit computes it -/

/-- `bao_lib.tension` specialised to the fit: survey S has posterior mean
`(mS1, mS2)` and covariance `[[aS, bS], [bS, cS]]`, survey D likewise;
`dp = p_S − p_D`, `C = C_S + C_D`, statistic `dpᵀ C⁻¹ dp`. -/
noncomputable def surveyTension (mS1 mS2 aS bS cS mD1 mD2 aD bD cD : ℝ) : ℝ :=
  chi2 (aS + aD) (bS + bD) (cS + cD) (mS1 - mD1) (mS2 - mD2)

/-- The statistic does not depend on which survey is labelled "1": swapping
SDSS and DESI DR2 gives the same χ² (hence the same PTE and N_σ). No
hypotheses: it is an identity of real expressions. -/
theorem surveyTension_symm (mS1 mS2 aS bS cS mD1 mD2 aD bD cD : ℝ) :
    surveyTension mS1 mS2 aS bS cS mD1 mD2 aD bD cD
      = surveyTension mD1 mD2 aD bD cD mS1 mS2 aS bS cS := by
  unfold surveyTension chi2
  ring

/-- If both posterior covariances are positive definite (Sylvester: `a > 0`,
`a c − b² > 0`), so is their sum `C_S + C_D` -- the matrix the fit inverts.
Hence `chi2_nonneg` / `chi2_eq_zero_iff` apply to `surveyTension` whenever the
two input posteriors are individually non-degenerate. -/
theorem posdef_add {aS bS cS aD bD cD : ℝ}
    (haS : 0 < aS) (hdS : 0 < aS * cS - bS ^ 2)
    (haD : 0 < aD) (hdD : 0 < aD * cD - bD ^ 2) :
    0 < aS + aD ∧ 0 < (aS + aD) * (cS + cD) - (bS + bD) ^ 2 := by
  refine ⟨by linarith, ?_⟩
  have hS' : 0 ≤ aS ^ 2 * (aD * cD - bD ^ 2) := mul_nonneg (sq_nonneg _) hdD.le
  have hD' : 0 ≤ aD ^ 2 * (aS * cS - bS ^ 2) := mul_nonneg (sq_nonneg _) hdS.le
  have hsq : 0 ≤ (aS * bD - aD * bS) ^ 2 := sq_nonneg _
  have hident : aS * aD * (aS * cD + aD * cS - 2 * bS * bD)
      = aS ^ 2 * (aD * cD - bD ^ 2) + aD ^ 2 * (aS * cS - bS ^ 2)
        + (aS * bD - aD * bS) ^ 2 := by ring
  have hx : 0 ≤ aS * aD * (aS * cD + aD * cS - 2 * bS * bD) := by
    rw [hident]; linarith
  have hpos : 0 < aS * aD := mul_pos haS haD
  have hcross : 0 ≤ aS * cD + aD * cS - 2 * bS * bD := by
    by_contra hneg
    have := mul_neg_of_pos_of_neg hpos (not_le.mp hneg)
    linarith
  have hexp : (aS + aD) * (cS + cD) - (bS + bD) ^ 2
      = (aS * cS - bS ^ 2) + (aD * cD - bD ^ 2)
        + (aS * cD + aD * cS - 2 * bS * bD) := by ring
  rw [hexp]
  linarith

/-- Corollary in the fit's own terms: with both posterior covariances PD the
two-survey statistic is nonnegative and vanishes iff the two posterior means
agree in both parameters. -/
theorem surveyTension_nonneg_and_zero_iff {mS1 mS2 aS bS cS mD1 mD2 aD bD cD : ℝ}
    (haS : 0 < aS) (hdS : 0 < aS * cS - bS ^ 2)
    (haD : 0 < aD) (hdD : 0 < aD * cD - bD ^ 2) :
    0 ≤ surveyTension mS1 mS2 aS bS cS mD1 mD2 aD bD cD ∧
      (surveyTension mS1 mS2 aS bS cS mD1 mD2 aD bD cD = 0 ↔ mS1 = mD1 ∧ mS2 = mD2) := by
  obtain ⟨ha, hdet⟩ := posdef_add haS hdS haD hdD
  unfold surveyTension
  refine ⟨chi2_nonneg ha hdet _ _, ?_⟩
  rw [chi2_eq_zero_iff ha hdet, sub_eq_zero, sub_eq_zero]

-- Axiom footprint, checked as part of this file's own compilation (Elenchus
-- NO_FOOTPRINT rule): every theorem this file is gated on appears here.
#print axioms tension1D_symm
#print axioms tension1D_nonneg
#print axioms tension1D_eq_zero_iff
#print axioms chi2_eq_dotProduct_inv_mulVec
#print axioms chi2_nonneg
#print axioms chi2_eq_zero_iff
#print axioms surveyTension_symm
#print axioms posdef_add
#print axioms surveyTension_nonneg_and_zero_iff

end ANSE.BAOConsistency
