theorem problem_87_adm_positive_mass
    (E P M : ℝ) (h_onshell : E ^ 2 = P ^ 2 + M ^ 2) (_hM : 0 ≤ M) :
    P ^ 2 ≤ E ^ 2 := by
  have : 0 ≤ M ^ 2 := by positivity
  linarith