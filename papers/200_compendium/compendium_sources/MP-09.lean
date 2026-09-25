theorem problem_9_markov_chebyshev_pointwise
    (x ε : ℝ) (_hε : 0 < ε) (hx : 0 ≤ x) :
    (if x ≥ ε then ε else 0) ≤ x := by
  split_ifs with h
  · exact h
  · exact hx