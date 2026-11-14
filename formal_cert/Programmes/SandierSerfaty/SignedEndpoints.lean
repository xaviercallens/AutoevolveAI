import Mathlib.MeasureTheory.Integral.IntervalIntegral.Basic
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Analysis.Real.Pi.Bounds

/-!
# Two steps of the reduction of "Triangular minimality for planar Coulomb renormalized energy", in Lean

Proposal 2 (2026-10-26), item A1b.

* `signed_endpoints` is Lemma `dual:signed-endpoints` of Section 3 (`build/sections/03-geometry.tex`,
  lines 567-611 of SHA-256 `1b8446c6...`), complete: for an even, locally integrable `G(d, ·)` with
  `g_d(x) = ∫₀ˣ G(d,s) ds`, the two scalar inputs (dual:scalar-input)
  `2 g_d(x) ≥ K (x ≥ 0)` and `∫₀^∞ max{0, -G(d,s)} ds ≤ -K` imply
  `g_d(d tan α) + g_d(d tan β) ≥ K` for every signed pair `|α|, |β| < π/2`, `α + β > 0`.
  The integral of the negative part is a `lintegral` (`∫⁻`, values in `[0, ∞]`), so no integrability hypothesis
  on it is needed and the Bochner junk value cannot enter. These two scalar inputs are exactly what the
  certificate's `global_grid` stage (outer and negative-part assertions, plus the exterior formula) is meant to
  certify; that bridge is not formalized here.
* `assembly_algebra` is the final algebraic step of Proposition `dual:assembly` (compatible tori): from the sector
  bounds `J(S) ≥ K + λ A(S) + μ θ(S)`, total area `N`, total angle `2πN`, at most `6N` sectors and `K ≤ 0`,
  `Σ J(S) ≥ N(6K + λ + 2πμ)`. The geometric inputs (Voronoi sectors, the dual identity) are hypotheses here.
* `b_lt_dstar`: the certificate's lower distance `b = 0.28209` satisfies `b < d_* = 1/(2√π)` (Section 7).

These lemmas are generic real analysis: they do not use the definitions of `SandierSerfatyStatement.lean`
(electric fields, `W`, cutoffs), because the manuscript states them for an abstract `G`.
-/

namespace ProgSandierSerfaty.Reduction

open MeasureTheory Set intervalIntegral Real

/-- The sector primitive `g_d(x) = ∫₀ˣ G(d,s) ds`. -/
noncomputable def gPrim (G : ℝ → ℝ → ℝ) (d x : ℝ) : ℝ := ∫ s in (0 : ℝ)..x, G d s

lemma gPrim_neg (G : ℝ → ℝ → ℝ) (d : ℝ) (heven : ∀ s, G d (-s) = G d s) (x : ℝ) :
    gPrim G d (-x) = -gPrim G d x := by
  unfold gPrim
  have h1 : (∫ s in (0 : ℝ)..(-x), G d s) = ∫ s in (0 : ℝ)..(-x), G d (-s) := by
    congr 1; funext s; rw [heven]
  rw [h1, intervalIntegral.integral_comp_neg, neg_neg, neg_zero, intervalIntegral.integral_symm]

lemma tan_nonneg_of {α : ℝ} (h0 : 0 ≤ α) (h1 : α < π / 2) : 0 ≤ Real.tan α := by
  have hpi : 0 < π / 2 := by positivity
  rcases h0.lt_or_eq with h | h
  · have := strictMonoOn_tan (a := 0) (b := α) ⟨by linarith, hpi⟩ ⟨by linarith, h1⟩ h
    rw [Real.tan_zero] at this; exact this.le
  · rw [← h, Real.tan_zero]

/-- The core estimate: for `0 < u ≤ v`, `∫ᵤᵛ G ≥ K` when the negative part has `∫₀^∞ G⁻ ≤ -K`. -/
lemma integral_ge_of_negPart {f : ℝ → ℝ} {K u v : ℝ} (hK : K ≤ 0) (hu : 0 < u) (huv : u ≤ v)
    (hf : IntervalIntegrable f volume u v)
    (hneg : ∫⁻ s in Ioi 0, ENNReal.ofReal (-f s) ≤ ENNReal.ofReal (-K)) :
    K ≤ ∫ s in u..v, f s := by
  rw [intervalIntegral.integral_of_le huv]
  have hI : Integrable f (volume.restrict (Ioc u v)) := hf.1
  have hN : Integrable (fun s => max (-f s) 0) (volume.restrict (Ioc u v)) := hI.neg_part
  have hle : ∫ s in Ioc u v, -(max (-f s) 0) ≤ ∫ s in Ioc u v, f s :=
    integral_mono hN.neg hI (fun s => by simp only; rcases le_total (-f s) 0 with h | h <;> simp [h] <;> linarith)
  rw [MeasureTheory.integral_neg] at hle
  have hlin : ∫ s in Ioc u v, max (-f s) 0 =
      (∫⁻ s in Ioc u v, ENNReal.ofReal (max (-f s) 0)).toReal :=
    integral_eq_lintegral_of_nonneg_ae (Filter.Eventually.of_forall (fun s => le_max_right _ _))
      hN.aestronglyMeasurable
  have hofr : ∀ s, ENNReal.ofReal (max (-f s) 0) = ENNReal.ofReal (-f s) := by
    intro s
    rcases le_total (-f s) 0 with h | h
    · rw [max_eq_right h, ENNReal.ofReal_zero, ENNReal.ofReal_of_nonpos h]
    · rw [max_eq_left h]
  simp_rw [hofr] at hlin
  have hsub : Ioc u v ⊆ Ioi (0 : ℝ) := fun s hs => lt_trans hu hs.1
  have hmono : ∫⁻ s in Ioc u v, ENNReal.ofReal (-f s) ≤ ENNReal.ofReal (-K) :=
    (lintegral_mono_set hsub).trans hneg
  have htr : (∫⁻ s in Ioc u v, ENNReal.ofReal (-f s)).toReal ≤ -K := by
    have := ENNReal.toReal_mono ENNReal.ofReal_ne_top hmono
    rwa [ENNReal.toReal_ofReal (by linarith)] at this
  linarith

/-- **Lemma dual:signed-endpoints** (manuscript Section 3). -/
theorem signed_endpoints (G : ℝ → ℝ → ℝ) (K d₀ : ℝ) (hK : K < 0) (hd₀ : 0 < d₀)
    (heven : ∀ d, d₀ ≤ d → ∀ s, G d (-s) = G d s)
    (hint : ∀ d, d₀ ≤ d → ∀ a b : ℝ, IntervalIntegrable (G d) volume a b)
    (hpos : ∀ d, d₀ ≤ d → ∀ x, 0 ≤ x → K ≤ 2 * gPrim G d x)
    (hneg : ∀ d, d₀ ≤ d → ∫⁻ s in Ioi 0, ENNReal.ofReal (-G d s) ≤ ENNReal.ofReal (-K)) :
    ∀ d, d₀ ≤ d → ∀ α β : ℝ, |α| < π / 2 → |β| < π / 2 → 0 < α + β →
      K ≤ gPrim G d (d * Real.tan α) + gPrim G d (d * Real.tan β) := by
  intro d hd α β hα hβ hαβ
  have hdpos : 0 < d := lt_of_lt_of_le hd₀ hd
  obtain ⟨hα1, hα2⟩ := abs_lt.mp hα
  obtain ⟨hβ1, hβ2⟩ := abs_lt.mp hβ
  -- the mixed-sign case, with `a < 0 < b`, `a + b > 0`
  have mixed : ∀ a b : ℝ, -(π / 2) < a → a < 0 → b < π / 2 → 0 < a + b →
      K ≤ gPrim G d (d * Real.tan a) + gPrim G d (d * Real.tan b) := by
    intro a b ha1 ha0 hb2 hab
    have hlt : Real.tan (-a) < Real.tan b :=
      strictMonoOn_tan ⟨by linarith, by linarith⟩ ⟨by linarith, hb2⟩ (by linarith)
    have hta : 0 < Real.tan (-a) := by
      have := strictMonoOn_tan (a := 0) (b := -a) ⟨by linarith, by positivity⟩ ⟨by linarith, by linarith⟩
        (by linarith)
      rwa [Real.tan_zero] at this
    set u := d * Real.tan (-a)
    set v := d * Real.tan b
    have hu : 0 < u := mul_pos hdpos hta
    have huv : u ≤ v := (mul_lt_mul_of_pos_left hlt hdpos).le
    have hfirst : d * Real.tan a = -u := by simp only [u, Real.tan_neg]; ring
    rw [hfirst, gPrim_neg G d (heven d hd)]
    have hsplit : gPrim G d v - gPrim G d u = ∫ s in u..v, G d s :=
      intervalIntegral.integral_interval_sub_left (hint d hd 0 v) (hint d hd 0 u)
    have := integral_ge_of_negPart hK.le hu huv (hint d hd u v) (hneg d hd)
    linarith
  rcases lt_or_ge α 0 with ha | ha
  · exact mixed α β hα1 ha hβ2 hαβ
  rcases lt_or_ge β 0 with hb | hb
  · have := mixed β α hβ1 hb hα2 (by linarith)
    linarith
  · have h1 := hpos d hd (d * Real.tan α) (mul_nonneg hdpos.le (tan_nonneg_of ha hα2))
    have h2 := hpos d hd (d * Real.tan β) (mul_nonneg hdpos.le (tan_nonneg_of hb hβ2))
    linarith

/-- **Proposition dual:assembly, final algebraic step** (compatible tori). -/
theorem assembly_algebra {ι : Type*} (S : Finset ι) (J A θ : ι → ℝ) (K lam mu : ℝ) (N : ℕ)
    (hK : K ≤ 0) (hJ : ∀ i ∈ S, K + lam * A i + mu * θ i ≤ J i)
    (hA : ∑ i ∈ S, A i = N) (hθ : ∑ i ∈ S, θ i = 2 * π * N) (hcard : S.card ≤ 6 * N) :
    (N : ℝ) * (6 * K + lam + 2 * π * mu) ≤ ∑ i ∈ S, J i := by
  have h1 : ∑ i ∈ S, (K + lam * A i + mu * θ i) ≤ ∑ i ∈ S, J i := Finset.sum_le_sum hJ
  rw [Finset.sum_add_distrib, Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.mul_sum, hA, hθ,
    Finset.sum_const, nsmul_eq_mul] at h1
  have hc : (S.card : ℝ) ≤ 6 * N := by exact_mod_cast hcard
  have : (6 * N : ℝ) * K ≤ S.card * K := mul_le_mul_of_nonpos_right hc hK
  nlinarith

/-- Section 7: `b = 0.28209 < d_* = 1/(2√π)`. -/
theorem b_lt_dstar : (0.28209 : ℝ) < 1 / (2 * Real.sqrt π) := by
  have hs : 0 < Real.sqrt π := Real.sqrt_pos.2 Real.pi_pos
  have hsq : Real.sqrt π ^ 2 = π := Real.sq_sqrt Real.pi_pos.le
  have hpi := Real.pi_lt_d6
  rw [lt_div_iff₀ (by positivity)]
  -- (2 b √π)² = 4 b² π < 1
  have h4 : (2 * Real.sqrt π * 0.28209) ^ 2 < 1 := by
    rw [mul_pow, mul_pow, hsq]; nlinarith
  nlinarith [sq_nonneg (2 * Real.sqrt π * 0.28209 - 1)]

end ProgSandierSerfaty.Reduction
