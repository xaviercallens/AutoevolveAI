theorem problem_67_tov_hydrostatic_monotonicity
    (r₁ r₂ : ℝ) (P : ℝ → ℝ) (hP : ∀ x y, x ≤ y → P y ≤ P x) (hr : r₁ ≤ r₂) :
    P r₂ ≤ P r₁ :=
  hP r₁ r₂ hr