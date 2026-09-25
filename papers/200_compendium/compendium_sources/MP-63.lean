theorem problem_63_penrose_cosmic_censorship
    (M A : ℝ) (_hA : 0 ≤ A) (h_penrose : Real.sqrt (A / (16 * Real.pi)) ≤ M) :
    0 ≤ M - Real.sqrt (A / (16 * Real.pi)) := by
  linarith