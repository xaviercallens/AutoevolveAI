theorem problem_30_hamilton_energy_conservation
    {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]
    (grad_q grad_p dq dp : V)
    (h_dq : dq = grad_p) (h_dp : dp = -grad_q) :
    ⟪grad_q, dq⟫ + ⟪grad_p, dp⟫ = (0 : ℝ) := by
  rw [h_dq, h_dp, inner_neg_right, real_inner_comm grad_p grad_q]
  exact add_neg_cancel ⟪grad_p, grad_q⟫