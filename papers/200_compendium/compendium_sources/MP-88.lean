theorem problem_88_mermin_wagner_no_ssb
    (M_sq : ℝ) (h_nonneg : 0 ≤ M_sq)
    (h_bound : ∀ (eps : ℝ), 0 < eps → M_sq ≤ eps) :
    M_sq = 0 := by
  apply le_antisymm
  · apply le_of_forall_pos_le_add
    intro eps h_eps
    have := h_bound eps h_eps
    linarith
  · exact h_nonneg