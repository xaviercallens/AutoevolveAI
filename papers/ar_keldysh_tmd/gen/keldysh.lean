lemma erfcx_le_one {x : ℝ} (hx : 0 ≤ x) : erfcx x ≤ 1 := -- proof elided

lemma erfcx_le_inv {x : ℝ} (hx : 0 < x) : erfcx x ≤ 1 / (Real.sqrt Real.pi * x) := -- proof elided

lemma w_le {r0 : ℝ} (hr0 : 0 < r0) (a : ℝ) : w r0 a ≤ 1 / r0 := -- proof elided

lemma w_le_sqrt {r0 a : ℝ} (hr0 : 0 < r0) (ha : 0 < a) :
    w r0 a ≤ 1 / (Real.sqrt Real.pi * Real.sqrt a) := -- proof elided

lemma keldysh_integrable {r0 : ℝ} (hr0 : 0 < r0) (n : ℕ) {c : ℝ} (hc : 0 < c) :
    IntegrableOn (fun a => (1 / (4 * a)) ^ n * Real.exp (-(c * (1 / (4 * a)))) * (w r0 a / (2 * a)))
      (Ioi 0) := -- proof elided

lemma hasDerivAt_G (h : MixtureData μ k m) (n : ℕ) {t : ℝ} (ht : 0 < t) :
    HasDerivAt (G μ k m n) (G μ k m (n + 1) t) t := -- proof elided

lemma G_sign (h : MixtureData μ k m) (n : ℕ) (t : ℝ) : 0 ≤ (-1 : ℝ) ^ n * G μ k m n t := -- proof elided

theorem keldysh_admissible {r0 : ℝ} (hr0 : 0 < r0) : AdmissiblePotential (keldysh r0) := -- proof elided

theorem keldysh_pos {r0 t : ℝ} (hr0 : 0 < r0) (ht : 0 < t) : 0 < keldysh r0 t := -- proof elided
