theorem problem_56_kitaev_toric_code_commutativity
    {A : Type*} [Ring A] (As Bp : A) (h_comm : As * Bp = Bp * As) :
    As * Bp - Bp * As = 0 := by
  rw [h_comm, sub_self]