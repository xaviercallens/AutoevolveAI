theorem problem_31_second_law_thermodynamics
    (S : ℝ → ℝ) (h_mono : Monotone S) (t₁ t₂ : ℝ) (h_time : t₁ ≤ t₂) :
    S t₁ ≤ S t₂ :=
  h_mono h_time