theorem problem_42_geodesic_velocity_norm_conservation
    {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]
    (u a : V) (h_geodesic : a = 0) :
    ⟪u, a⟫ = (0 : ℝ) := by
  rw [h_geodesic]; exact inner_zero_right u