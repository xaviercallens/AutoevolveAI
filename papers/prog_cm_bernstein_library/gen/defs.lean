/-- `f` is completely monotone on `(0, ∞)`: `C^∞` there, and `(-1)^n f^{(n)} ≥ 0` there for every `n`. -/
def IsCompletelyMonotoneOn (f : ℝ → ℝ) : Prop :=
  ContDiffOn ℝ (⊤ : ℕ∞) f (Set.Ioi 0) ∧
  ∀ (n : ℕ) (t : ℝ), 0 < t → 0 ≤ (-1 : ℝ) ^ n * iteratedDeriv n f t

/-- **Bridge (exact equivalence).** Complete monotonicity on `(0, ∞)` is upstream's `AdmissiblePotential`. -/
theorem isCompletelyMonotoneOn_iff_admissible {f : ℝ → ℝ} :
    IsCompletelyMonotoneOn f ↔ OAI.AtomicTriangular.AdmissiblePotential f := by
  constructor
  · intro h
    refine ⟨h.1, fun t ht => ?_, h.2⟩
    simpa using h.2 0 t ht
  · intro h
    exact ⟨h.1, h.2.2⟩

/-- `g` is a Bernstein function on `(0, ∞)`: `C^∞`, nonnegative, with completely monotone derivative. -/
def IsBernsteinOn (g : ℝ → ℝ) : Prop :=
  ContDiffOn ℝ (⊤ : ℕ∞) g (Set.Ioi 0) ∧ (∀ t : ℝ, 0 < t → 0 ≤ g t) ∧ IsCompletelyMonotoneOn (deriv g)
