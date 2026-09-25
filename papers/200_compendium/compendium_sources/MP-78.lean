theorem problem_78_wheeler_dewitt_constraint
    {H : Type*} [NormedAddCommGroup H] [InnerProductSpace ℝ H]
    (H_op : H →L[ℝ] H) (Psi : H) (hWDW : H_op Psi = 0) :
    ⟪Psi, H_op Psi⟫ = (0 : ℝ) := by
  rw [hWDW]
  exact inner_zero_right Psi