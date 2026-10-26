/-- All moments from exponential integrability. -/
theorem integrable_pow_mul (hk : Measurable k) (hm : Measurable m) (hk0 : ∀ᵐ x ∂μ, 0 ≤ k x)
    (hm0 : ∀ᵐ x ∂μ, 0 ≤ m x) (hint : ∀ c : ℝ, 0 < c → Integrable (fun x => Real.exp (-(c * k x)) * m x) μ)
    (n : ℕ) {c : ℝ} (hc : 0 < c) : Integrable (fun x => k x ^ n * Real.exp (-(c * k x)) * m x) μ := -- proof elided

/-- **Laplace mixtures (general).** `t ↦ ∫ e^{-t k(x)} m(x) dμ(x)` is completely monotone on `(0, ∞)` when
`k, m ≥ 0` a.e. are measurable and `e^{-c k} m` is integrable for every `c > 0`. -/
theorem laplace (hk : Measurable k) (hm : Measurable m) (hk0 : ∀ᵐ x ∂μ, 0 ≤ k x) (hm0 : ∀ᵐ x ∂μ, 0 ≤ m x)
    (hint : ∀ c : ℝ, 0 < c → Integrable (fun x => Real.exp (-(c * k x)) * m x) μ) :
    IsCompletelyMonotoneOn (fun t => ∫ x, Real.exp (-(t * k x)) * m x ∂μ) := -- proof elided

/-- **Laplace transform of a measure on `[0, ∞)`** (easy direction of Bernstein–Widder). -/
theorem laplace_measure {μ : Measure ℝ} (hμ : ∀ᵐ x ∂μ, 0 ≤ x)
    (hint : ∀ c : ℝ, 0 < c → Integrable (fun x => Real.exp (-(c * x))) μ) :
    IsCompletelyMonotoneOn (fun t => ∫ x, Real.exp (-(t * x)) ∂μ) := -- proof elided

/-- **Locally uniform limits.** -/
theorem of_tendstoLocallyUniformlyOn {F G : ℕ → ℝ → ℝ} {f : ℝ → ℝ}
    (hF : ∀ k, IsCompletelyMonotoneOn (F k))
    (hG : ∀ n : ℕ, TendstoLocallyUniformlyOn (fun k => iteratedDeriv n (F k)) (G n) atTop (Ioi 0))
    (hf : EqOn f (G 0) (Ioi 0)) :
    IsCompletelyMonotoneOn f ∧ ∀ n : ℕ, EqOn (iteratedDeriv n f) (G n) (Ioi 0) := -- proof elided
