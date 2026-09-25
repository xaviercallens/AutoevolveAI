theorem problem_34_euler_lagrange_stationarity
    {V : Type*} [AddCommGroup V]
    (p_dot F : V) (h_EL : p_dot = F) :
    p_dot - F = 0 := by
  rw [h_EL]; exact sub_self F