/-- `t ↦ a t + b` is Bernstein for `a, b ≥ 0`. -/
theorem affine {a b : ℝ} (ha : 0 ≤ a) (hb : 0 ≤ b) : IsBernsteinOn (fun t => a * t + b) := -- proof elided

/-- `t ↦ t^α` is Bernstein for `0 ≤ α ≤ 1`. -/
theorem rpow {α : ℝ} (h0 : 0 ≤ α) (h1 : α ≤ 1) : IsBernsteinOn (fun t => t ^ α) := -- proof elided

/-- `√` is a Bernstein function. -/
theorem sqrt : IsBernsteinOn Real.sqrt := -- proof elided

/-- **Bernstein ∘ Bernstein** (inner function positive) is Bernstein. -/
theorem comp (hf : IsBernsteinOn f) (hg : IsBernsteinOn g) (hpos : ∀ t, 0 < t → 0 < g t) :
    IsBernsteinOn (fun t => f (g t)) := -- proof elided

/-- `t ↦ e^{-a ψ(t)}` is completely monotone for `a ≥ 0` and `ψ` a positive Bernstein function. -/
theorem exp_neg_comp {ψ : ℝ → ℝ} {a : ℝ} (ha : 0 ≤ a) (hψ : IsBernsteinOn ψ) (hpos : ∀ t, 0 < t → 0 < ψ t) :
    IsCompletelyMonotoneOn (fun t => Real.exp (-(a * ψ t))) := -- proof elided

/-- Special case `ψ = √`: `f (√t)` is completely monotone. -/
theorem IsCompletelyMonotoneOn.comp_sqrt {f : ℝ → ℝ} (hf : IsCompletelyMonotoneOn f) :
    IsCompletelyMonotoneOn (fun t => f (Real.sqrt t)) := -- proof elided

/-- **Positive control.** `exp(-κ √t)` is completely monotone (`κ ≥ 0`): a one-line re-derivation of
`AutoresearchYukawa.phi_admissible` (which needed `κ > 0`) via subordination, replacing its bespoke induction. -/
theorem phi_cm {κ : ℝ} (hκ : 0 ≤ κ) : IsCompletelyMonotoneOn (AutoresearchYukawa.phi κ) :=
  ((exp_neg_mul hκ).comp_sqrt).congr' fun t _ => by simp only [AutoresearchYukawa.phi, neg_mul]
