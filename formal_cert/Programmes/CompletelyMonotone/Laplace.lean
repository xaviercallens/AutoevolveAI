import Programmes.CompletelyMonotone.Basic

/-!
# Programme P3: Laplace mixtures are completely monotone (easy direction of Bernstein–Widder)

`laplace` generalises `AutoresearchKeldysh.laplace_admissible`. That lemma assumed every moment
`∫ k^n e^{-c k} m dμ` finite (all `n : ℕ`, all `c > 0`). Here only the exponential integrability
`∫ e^{-c k} m dμ < ∞` for every `c > 0` is assumed (the `n = 0` case); the moments follow from
`u^n e^{-c u} ≤ (n! / (c/2)^n) e^{-(c/2) u}` (`integrable_pow_mul`).

`laplace_measure`: for a measure `μ` on `ℝ` concentrated on `[0, ∞)` with `∫ e^{-c x} dμ < ∞` for all `c > 0`, the
Laplace transform `t ↦ ∫ e^{-t x} dμ(x)` is completely monotone. (The converse direction of Bernstein–Widder, that
every completely monotone function is such a transform, is NOT proved here.)
-/

namespace ProgCM

open MeasureTheory Set Filter Topology IsCompletelyMonotoneOn

section Laplace

variable {α : Type*} [MeasurableSpace α] {μ : Measure α} {k m : α → ℝ}

/-- All moments from exponential integrability. -/
theorem integrable_pow_mul (hk : Measurable k) (hm : Measurable m) (hk0 : ∀ᵐ x ∂μ, 0 ≤ k x)
    (hm0 : ∀ᵐ x ∂μ, 0 ≤ m x) (hint : ∀ c : ℝ, 0 < c → Integrable (fun x => Real.exp (-(c * k x)) * m x) μ)
    (n : ℕ) {c : ℝ} (hc : 0 < c) : Integrable (fun x => k x ^ n * Real.exp (-(c * k x)) * m x) μ := by
  have hc2 : 0 < c / 2 := by linarith
  refine ((hint (c / 2) hc2).const_mul ((n.factorial : ℝ) / (c / 2) ^ n)).mono'
    (by fun_prop : Measurable fun x => k x ^ n * Real.exp (-(c * k x)) * m x).aestronglyMeasurable ?_
  filter_upwards [hk0, hm0] with x hkx hmx
  have hnn : 0 ≤ k x ^ n * Real.exp (-(c * k x)) * m x :=
    mul_nonneg (mul_nonneg (pow_nonneg hkx n) (Real.exp_pos _).le) hmx
  rw [Real.norm_eq_abs, abs_of_nonneg hnn]
  have hsplit : Real.exp (-(c * k x)) = Real.exp (-(c / 2 * k x)) * Real.exp (-(c / 2 * k x)) := by
    rw [← Real.exp_add]
    congr 1
    ring
  have hb := AutoresearchKeldysh.pow_mul_exp_neg_le hkx hc2 n
  calc k x ^ n * Real.exp (-(c * k x)) * m x
      = (k x ^ n * Real.exp (-(c / 2 * k x))) * (Real.exp (-(c / 2 * k x)) * m x) := by
        rw [hsplit]
        ring
    _ ≤ ((n.factorial : ℝ) / (c / 2) ^ n) * (Real.exp (-(c / 2 * k x)) * m x) :=
        mul_le_mul_of_nonneg_right hb (mul_nonneg (Real.exp_pos _).le hmx)

/-- **Laplace mixtures (general).** `t ↦ ∫ e^{-t k(x)} m(x) dμ(x)` is completely monotone on `(0, ∞)` when
`k, m ≥ 0` a.e. are measurable and `e^{-c k} m` is integrable for every `c > 0`. -/
theorem laplace (hk : Measurable k) (hm : Measurable m) (hk0 : ∀ᵐ x ∂μ, 0 ≤ k x) (hm0 : ∀ᵐ x ∂μ, 0 ≤ m x)
    (hint : ∀ c : ℝ, 0 < c → Integrable (fun x => Real.exp (-(c * k x)) * m x) μ) :
    IsCompletelyMonotoneOn (fun t => ∫ x, Real.exp (-(t * k x)) * m x ∂μ) :=
  of_admissible (AutoresearchKeldysh.laplace_admissible (μ := μ) (k := k) (m := m)
    { k_meas := hk
      m_meas := hm
      k_nonneg := hk0
      m_nonneg := hm0
      integrable := fun n _ hc => integrable_pow_mul hk hm hk0 hm0 hint n hc })

/-- The derivatives of a Laplace mixture are the differentiated integrals. -/
theorem laplace_iteratedDeriv (hk : Measurable k) (hm : Measurable m) (hk0 : ∀ᵐ x ∂μ, 0 ≤ k x)
    (hm0 : ∀ᵐ x ∂μ, 0 ≤ m x) (hint : ∀ c : ℝ, 0 < c → Integrable (fun x => Real.exp (-(c * k x)) * m x) μ)
    (n : ℕ) {t : ℝ} (ht : 0 < t) :
    iteratedDeriv n (fun t => ∫ x, Real.exp (-(t * k x)) * m x ∂μ) t =
      ∫ x, (-(k x)) ^ n * Real.exp (-(t * k x)) * m x ∂μ :=
  AutoresearchKeldysh.laplace_iteratedDeriv (μ := μ) (k := k) (m := m)
    { k_meas := hk
      m_meas := hm
      k_nonneg := hk0
      m_nonneg := hm0
      integrable := fun n _ hc => integrable_pow_mul hk hm hk0 hm0 hint n hc } n ht

end Laplace

/-- **Laplace transform of a measure on `[0, ∞)`** (easy direction of Bernstein–Widder). -/
theorem laplace_measure {μ : Measure ℝ} (hμ : ∀ᵐ x ∂μ, 0 ≤ x)
    (hint : ∀ c : ℝ, 0 < c → Integrable (fun x => Real.exp (-(c * x))) μ) :
    IsCompletelyMonotoneOn (fun t => ∫ x, Real.exp (-(t * x)) ∂μ) := by
  have h := laplace (μ := μ) (k := id) (m := fun _ => 1) measurable_id measurable_const hμ
    (Eventually.of_forall fun _ => zero_le_one) (fun c hc => by simpa using hint c hc)
  simpa using h

end ProgCM

#print axioms ProgCM.integrable_pow_mul
#print axioms ProgCM.laplace
#print axioms ProgCM.laplace_iteratedDeriv
#print axioms ProgCM.laplace_measure
