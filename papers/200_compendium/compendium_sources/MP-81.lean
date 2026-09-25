theorem problem_81_symplectic_form_preservation
    {V : Type*} [AddCommGroup V]
    (omega : V → V →+ ℝ) (h_skew : ∀ u v, omega u v = - omega v u) (u : V) :
    omega u u = 0 := by
  have h := h_skew u u
  linarith