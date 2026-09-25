theorem problem_3_banach_contraction_unique_fixed_point
    {X : Type*} [MetricSpace X] [CompleteSpace X] [Nonempty X]
    {c : ℝ≥0} (hc : c < 1) {T : X → X} (hT : LipschitzWith c T) :
    ∃! x : X, T x = x := by
  have hcon : ContractingWith c T := ⟨hc, hT⟩
  use hcon.fixedPoint
  dsimp
  refine ⟨hcon.fixedPoint_isFixedPt, ?_⟩
  intro y hy
  exact hcon.fixedPoint_unique hy