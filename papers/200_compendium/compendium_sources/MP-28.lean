theorem problem_28_einstein_field_vacuum
    {V : Type*} [AddCommGroup V] [Module ℝ V]
    (Ric g G : V →ₗ[ℝ] V →ₗ[ℝ] ℝ) (R : ℝ)
    (hG : ∀ X Y, G X Y = Ric X Y - (1 / 2 * R) * g X Y)
    (h_vacuum_ricci : Ric = 0) (h_vacuum_scalar : R = 0) :
    ∀ X Y, G X Y = 0 := by
  intro X Y; rw [hG, h_vacuum_ricci, h_vacuum_scalar]; simp