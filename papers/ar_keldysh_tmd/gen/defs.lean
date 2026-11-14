structure MixtureData (μ : Measure α) (k m : α → ℝ) : Prop where
  k_meas : Measurable k
  m_meas : Measurable m
  k_nonneg : ∀ᵐ x ∂μ, 0 ≤ k x
  m_nonneg : ∀ᵐ x ∂μ, 0 ≤ m x
  integrable : ∀ (n : ℕ) (c : ℝ), 0 < c → Integrable (fun x => k x ^ n * Real.exp (-(c * k x)) * m x) μ

noncomputable def erfcx (x : ℝ) : ℝ :=
  2 / Real.sqrt Real.pi * ∫ y in Ioi (0 : ℝ), Real.exp (-(y ^ 2 + 2 * x * y))

noncomputable def w (r0 a : ℝ) : ℝ := 1 / r0 * erfcx (Real.sqrt a / r0)

noncomputable def keldysh (r0 t : ℝ) : ℝ :=
  ∫ a in Ioi (0 : ℝ), w r0 a / (2 * a) * Real.exp (-t / (4 * a))

noncomputable def keldyshReg (r0 ε t : ℝ) : ℝ := keldysh r0 t * Real.exp (-(ε * t))

noncomputable def signedMix (t : ℝ) : ℝ := Real.exp (-t) - 2 * Real.exp (-(2 * t))
