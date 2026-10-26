/-- Only the values on `(0, ∞)` matter. -/
theorem congr (hf : IsCompletelyMonotoneOn f) (heq : EqOn f g (Ioi 0)) : IsCompletelyMonotoneOn g := -- proof elided

/-- A nonnegative multiple. -/
theorem const_mul (hf : IsCompletelyMonotoneOn f) {c : ℝ} (hc : 0 ≤ c) :
    IsCompletelyMonotoneOn (fun t => c * f t) := -- proof elided

/-- The sum of two completely monotone functions. -/
theorem add (hf : IsCompletelyMonotoneOn f) (hg : IsCompletelyMonotoneOn g) :
    IsCompletelyMonotoneOn (f + g) := -- proof elided

/-- **Product (Leibniz).** The product of two completely monotone functions is completely monotone. -/
theorem mul (hf : IsCompletelyMonotoneOn f) (hg : IsCompletelyMonotoneOn g) :
    IsCompletelyMonotoneOn (f * g) :=
  ⟨hf.1.mul hg.1, fun n t ht => AutoresearchYukawa.mul_sign n (hf.contDiffAt ht n) (hg.contDiffAt ht n)
    (fun i _ => hf.2 i t ht) (fun i _ => hg.2 i t ht)⟩

/-- **Translation.** `t ↦ f (t + c)` is completely monotone for `c ≥ 0`. -/
theorem comp_add_const (hf : IsCompletelyMonotoneOn f) {c : ℝ} (hc : 0 ≤ c) :
    IsCompletelyMonotoneOn (fun t => f (t + c)) := -- proof elided

/-- **Derivative.** `-f'` is completely monotone. -/
theorem neg_deriv (hf : IsCompletelyMonotoneOn f) : IsCompletelyMonotoneOn (fun t => -deriv f t) := -- proof elided

/-- Each `(-1)^n f^{(n)}` is antitone on `(0, ∞)`. -/
theorem antitoneOn_sign (hf : IsCompletelyMonotoneOn f) (n : ℕ) :
    AntitoneOn (fun t => (-1 : ℝ) ^ n * iteratedDeriv n f t) (Ioi 0) := -- proof elided

/-- **Difference of a translate.** `t ↦ f t - f (t + c)` is completely monotone for `c ≥ 0`. -/
theorem sub_comp_add_const (hf : IsCompletelyMonotoneOn f) {c : ℝ} (hc : 0 ≤ c) :
    IsCompletelyMonotoneOn (fun t => f t - f (t + c)) := by
  have hs := hf.comp_add_const hc
  refine ⟨hf.1.sub hs.1, fun n t ht => ?_⟩
  have htc : 0 < t + c := by linarith
  have e : iteratedDeriv n (fun t => f t - f (t + c)) t =
      iteratedDeriv n f t - iteratedDeriv n f (t + c) := by
    have h := iteratedDeriv_sub (hf.contDiffAt ht n) (hs.contDiffAt ht n)
    rw [iteratedDeriv_comp_add_const] at h
    exact h
  rw [e, mul_sub, sub_nonneg]
  exact hf.antitoneOn_sign n ht htc (by linarith)

/-- **Finite nonnegative combinations.** -/
theorem sum {ι : Type*} (s : Finset ι) (w : ι → ℝ) (F : ι → ℝ → ℝ) (hw : ∀ i ∈ s, 0 ≤ w i)
    (hF : ∀ i ∈ s, IsCompletelyMonotoneOn (F i)) :
    IsCompletelyMonotoneOn (fun t => ∑ i ∈ s, w i * F i t) := -- proof elided

/-- `e^{-a t}` is completely monotone for `a ≥ 0`. -/
theorem exp_neg_mul {a : ℝ} (ha : 0 ≤ a) : IsCompletelyMonotoneOn (fun t => Real.exp (-(a * t))) :=
  of_admissible (AutoresearchKeldysh.expNeg_admissible ha)

/-- `t^{-s}` is completely monotone for `s ≥ 0`. -/
theorem rpow_neg {s : ℝ} (hs : 0 ≤ s) : IsCompletelyMonotoneOn (fun t => t ^ (-s)) := -- proof elided
