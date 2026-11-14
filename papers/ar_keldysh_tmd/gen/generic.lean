theorem laplace_admissible (h : MixtureData μ k m) :
    AdmissiblePotential (fun t => ∫ x, Real.exp (-(t * k x)) * m x ∂μ) := -- proof elided

theorem laplace_iteratedDeriv (h : MixtureData μ k m) (n : ℕ) {t : ℝ} (ht : 0 < t) :
    iteratedDeriv n (fun t => ∫ x, Real.exp (-(t * k x)) * m x ∂μ) t =
      ∫ x, (-(k x)) ^ n * Real.exp (-(t * k x)) * m x ∂μ := -- proof elided

theorem expNeg_admissible {ε : ℝ} (hε : 0 ≤ ε) : AdmissiblePotential (fun t => Real.exp (-(ε * t))) := -- proof elided

theorem signedMix_not_admissible : ¬ AdmissiblePotential signedMix := -- proof elided
