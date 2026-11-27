theorem rot120_comm_symm (p q r s : ℝ) (hs : s ^ 2 = 3 / 4)
    (h11 : -1 / 2 * p + -s * q = p * (-1 / 2) + q * s)
    (h12 : -1 / 2 * q + -s * r = p * -s + q * (-1 / 2)) :
    q = 0 ∧ r = p := ... -- proof elided

theorem rot120_fixed_vec (g1 g2 s : ℝ) (hs : s ^ 2 = 3 / 4)
    (e1 : -1 / 2 * g1 + -s * g2 = g1) (e2 : s * g1 + -1 / 2 * g2 = g2) :
    g1 = 0 ∧ g2 = 0 := by
  have h1 : g1 = 0 := by linear_combination (s * e2 - 3 / 2 * e1 - g1 * hs) / 3
  refine ⟨h1, ?_⟩
  linear_combination (-(s * e1) - 3 / 2 * e2 - g2 * hs) / 3
