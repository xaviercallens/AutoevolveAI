/-
DESI DR2 BAO exercise (slug desi_dr2_bao): kernel-verified algebraic/analytic
skeleton of the flat-wCDM background used in scripts/desi_dr2_bao/dr2_model.py.

The fitted model (dr2_model.e_of_z with orad = 0, the preregistered primary
model) is
    E(z)² = Ωₘ (1+z)³ + (1-Ωₘ) (1+z)^{3(1+w)},        E(z) = H(z)/H₀,
with flatness (Ω_DE = 1-Ωₘ) already substituted, and the comoving distance in
units of c/H₀ is  D_C(z) = ∫₀ᶻ dt / E(t)  (dr2_model.predict_quad / predict_gl,
up to the prefactor c/(100 km s⁻¹ Mpc⁻¹) and the 1/(h r_d) normalisation).
The fit's prior box is 0.01 < Ωₘ < 0.99 and -3 ≤ w ≤ 1 (dr2_model.PRIOR_*).

Scope, deliberately (same policy as BAO_FlatLCDM.lean): exact facts about the
MODEL, not a theorem "solving cosmology":
  * E(z)² > 0 (hence E(z) > 0) on the whole prior box, for every real w --
    so 1/E, the comoving-distance integrand, is always well defined;
  * at w = -1 the wCDM E(z) is DEFINITIONALLY the flat-ΛCDM E(z) of
    ANSE.BAO_FlatLCDM (the DR1 exercise), so the two fits nest exactly;
  * for w ≥ -1 (the non-phantom half of the prior, which contains the DR2
    best fit w ≈ -0.916) E(z) is strictly increasing in z;
  * for EVERY real w in the prior, D_C(z) is strictly increasing in z ≥ 0
    (integral of a continuous, strictly positive integrand).
The exponent 3(1+w) is a real power (Real.rpow), exactly as `zp1 ** (3*(1+w))`
in numpy; nothing is restricted to integer w.
-/
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Analysis.SpecialFunctions.Pow.Continuity
import Mathlib.MeasureTheory.Integral.IntervalIntegral.Basic
import Mathlib.Topology.Algebra.GroupWithZero
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import ANSE.BAO_FlatLCDM

namespace ANSE.DESIDR2wCDM

open Real MeasureTheory

/-- `E(z)² = Ωₘ(1+z)³ + (1-Ωₘ)(1+z)^{3(1+w)}` for flat wCDM (no radiation), the
exact expression under the square root in `dr2_model.e_of_z` (orad = 0). The
exponent `3 * (1 + w)` is a real number, so `^` here is `Real.rpow`. -/
noncomputable def E2 (Om w z : ℝ) : ℝ :=
  Om * (1 + z) ^ 3 + (1 - Om) * (1 + z) ^ (3 * (1 + w))

/-- Dimensionless flat-wCDM expansion rate `E(z) = H(z)/H₀ = √(E2)`. -/
noncomputable def E (Om w z : ℝ) : ℝ := Real.sqrt (E2 Om w z)

/-- Dimensionless comoving distance `D_C(z) = ∫₀ᶻ dt / E(t)` (in units of c/H₀),
the quantity `dr2_model.predict_quad` integrates with `scipy.integrate.quad`
and `predict_gl` with Gauss–Legendre. -/
noncomputable def Dc (Om w z : ℝ) : ℝ := ∫ t in (0:ℝ)..z, (E Om w t)⁻¹

/-- `E(z)² > 0` for `z ≥ 0`, `0 < Ωₘ < 1` and EVERY real `w` (in particular on
the whole fit prior `-3 ≤ w ≤ 1`, phantom side included): both terms are
strictly positive because `(1+z) ≥ 1 > 0` and a positive base raised to any
real power is positive. -/
theorem E2_pos {Om w z : ℝ} (hOm0 : 0 < Om) (hOm1 : Om < 1) (hz : 0 ≤ z) :
    0 < E2 Om w z := by
  unfold E2
  have h1 : (0:ℝ) < 1 + z := by linarith
  have hr : 0 < (1 + z) ^ (3 * (1 + w)) := Real.rpow_pos_of_pos h1 _
  have hc : 0 < (1 + z) ^ 3 := pow_pos h1 3
  have hOm1' : 0 < 1 - Om := sub_pos.mpr hOm1
  nlinarith [mul_pos hOm0 hc, mul_pos hOm1' hr]

/-- `E(z) > 0` on the same domain: the expansion rate never vanishes or turns
imaginary, so `1/E(z)`, the comoving-distance integrand, is well defined for
every parameter point the sampler can visit. -/
theorem E_pos {Om w z : ℝ} (hOm0 : 0 < Om) (hOm1 : Om < 1) (hz : 0 ≤ z) :
    0 < E Om w z := by
  unfold E
  rw [Real.sqrt_pos]
  exact E2_pos hOm0 hOm1 hz

/-- Nesting: at `w = -1` the wCDM expansion rate is EXACTLY the flat-ΛCDM
expansion rate `ANSE.BAOFlatLCDM.E` of the DR1 exercise (BAO_FlatLCDM.lean),
for every `Ωₘ` and every `z` (no positivity hypotheses needed, since
`(1+z)^0 = 1` as a real power). This is the identity that makes the ΛCDM and
wCDM fits of this exercise nested models. -/
theorem E_w_neg_one (Om z : ℝ) : E Om (-1) z = ANSE.BAOFlatLCDM.E Om z := by
  unfold E E2 ANSE.BAOFlatLCDM.E
  have h0 : (3:ℝ) * (1 + -1) = 0 := by norm_num
  rw [h0, Real.rpow_zero, mul_one]

/-- On the non-phantom half of the prior, `w ≥ -1`, `E` is strictly increasing
on `[0, ∞)`: the matter term grows strictly and the dark-energy term
(exponent `3(1+w) ≥ 0`) is non-decreasing. (For `w < -1` the dark-energy term
DEcreases with `z`, so no such theorem is claimed there; the DR2 best fit
`w ≈ -0.92` lies inside the hypothesis.) -/
theorem E_strictMonoOn_of_neg_one_le {Om w : ℝ} (hOm0 : 0 < Om) (hOm1 : Om < 1)
    (hw : -1 ≤ w) : StrictMonoOn (E Om w) (Set.Ici (0 : ℝ)) := by
  intro z1 hz1 z2 hz2 hlt
  simp only [Set.mem_Ici] at hz1 hz2
  have hargnn : 0 ≤ E2 Om w z1 := (E2_pos hOm0 hOm1 hz1).le
  unfold E
  apply Real.sqrt_lt_sqrt hargnn
  unfold E2
  have h1 : (0:ℝ) < 1 + z1 := by linarith
  have hcube : (1 + z1) ^ 3 < (1 + z2) ^ 3 := by
    nlinarith [sq_nonneg (z2 - z1), sq_nonneg (1 + z1), sq_nonneg (1 + z2)]
  have hp : (0:ℝ) ≤ 3 * (1 + w) := by linarith
  have hr : (1 + z1) ^ (3 * (1 + w)) ≤ (1 + z2) ^ (3 * (1 + w)) :=
    Real.rpow_le_rpow h1.le (by linarith) hp
  have hm := mul_lt_mul_of_pos_left hcube hOm0
  have hd := mul_le_mul_of_nonneg_left hr (sub_pos.mpr hOm1).le
  linarith

/-- The integrand `1/E(t)` is continuous on `[0, ∞)` for every real `w`
(`E` is the square root of a sum of a polynomial and a real power with base
`1 + t ≥ 1`, and never vanishes there by `E_pos`). -/
theorem invE_continuousOn {Om w : ℝ} (hOm0 : 0 < Om) (hOm1 : Om < 1) :
    ContinuousOn (fun t => (E Om w t)⁻¹) (Set.Ici (0 : ℝ)) := by
  have hbase : ContinuousOn (fun t : ℝ => 1 + t) (Set.Ici (0 : ℝ)) :=
    (continuous_const.add continuous_id).continuousOn
  have hE2 : ContinuousOn (fun t => E2 Om w t) (Set.Ici (0 : ℝ)) := by
    unfold E2
    apply ContinuousOn.add
    · exact continuousOn_const.mul (hbase.pow 3)
    · apply continuousOn_const.mul
      apply hbase.rpow_const
      intro x hx
      left
      simp only [Set.mem_Ici] at hx
      linarith
  have hE : ContinuousOn (fun t => E Om w t) (Set.Ici (0 : ℝ)) := by
    unfold E
    exact hE2.sqrt
  apply hE.inv₀
  intro x hx
  simp only [Set.mem_Ici] at hx
  exact (E_pos hOm0 hOm1 hx).ne'

/-- Comoving distance is strictly increasing in redshift on `[0, ∞)` for
`0 < Ωₘ < 1` and EVERY real `w` (phantom values included): the difference
`D_C(z₂) - D_C(z₁)` is the integral over `[z₁, z₂]` of a continuous, strictly
positive integrand. This is the qualitative fact behind using `D_M/r_d` as a
distance ladder in the fit: farther redshift, larger comoving distance,
regardless of where in the prior box the sampler is. -/
theorem Dc_strictMonoOn {Om w : ℝ} (hOm0 : 0 < Om) (hOm1 : Om < 1) :
    StrictMonoOn (Dc Om w) (Set.Ici (0 : ℝ)) := by
  intro z1 hz1 z2 hz2 hlt
  simp only [Set.mem_Ici] at hz1 hz2
  have hcont := invE_continuousOn (w := w) hOm0 hOm1
  have hint : ∀ a b : ℝ, 0 ≤ a → 0 ≤ b →
      IntervalIntegrable (fun t => (E Om w t)⁻¹) volume a b := by
    intro a b ha hb
    apply ContinuousOn.intervalIntegrable
    apply hcont.mono
    intro x hx
    rw [Set.mem_uIcc] at hx
    simp only [Set.mem_Ici]
    rcases hx with ⟨h, _⟩ | ⟨h, _⟩ <;> linarith
  have h01 := hint 0 z1 le_rfl hz1
  have h02 := hint 0 z2 le_rfl hz2
  have h12 := hint z1 z2 hz1 hz2
  have hsub : Dc Om w z2 - Dc Om w z1 = ∫ t in z1..z2, (E Om w t)⁻¹ := by
    unfold Dc
    exact intervalIntegral.integral_interval_sub_left h02 h01
  have hpos : 0 < ∫ t in z1..z2, (E Om w t)⁻¹ := by
    apply intervalIntegral.intervalIntegral_pos_of_pos_on h12 _ hlt
    intro x hx
    have hx0 : 0 ≤ x := by linarith [hx.1]
    exact inv_pos.mpr (E_pos hOm0 hOm1 hx0)
  show Dc Om w z1 < Dc Om w z2
  linarith

-- Axiom footprint, checked as part of this file's own compilation (Elenchus
-- NO_FOOTPRINT rule, LL.md §11b): every theorem this file is gated on.
#print axioms E2_pos
#print axioms E_pos
#print axioms E_w_neg_one
#print axioms E_strictMonoOn_of_neg_one_le
#print axioms invE_continuousOn
#print axioms Dc_strictMonoOn



theorem E2_pos_zgtm1 {Om w z : ℝ} (hOm0 : 0 < Om) (hOm1 : Om < 1) (hz : -1 < z) :
    0 < E2 Om w z := by
  unfold E2
  have h1 : (0:ℝ) < 1 + z := by linarith
  have hr : 0 < (1 + z) ^ (3 * (1 + w)) := Real.rpow_pos_of_pos h1 _
  have hc : 0 < (1 + z) ^ 3 := pow_pos h1 3
  have hOm1' : 0 < 1 - Om := sub_pos.mpr hOm1
  nlinarith [mul_pos hOm0 hc, mul_pos hOm1' hr]

theorem E_pos_zgtm1 {Om w z : ℝ} (hOm0 : 0 < Om) (hOm1 : Om < 1) (hz : -1 < z) :
    0 < E Om w z := by
  unfold E
  rw [Real.sqrt_pos]
  exact E2_pos_zgtm1 hOm0 hOm1 hz

#print axioms ANSE.DESIDR2wCDM.E2_pos_zgtm1
#print axioms ANSE.DESIDR2wCDM.E_pos_zgtm1

end ANSE.DESIDR2wCDM
