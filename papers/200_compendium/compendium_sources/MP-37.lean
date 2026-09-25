theorem problem_37_ehrenfest_constant_of_motion
    {A : Type*} [Ring A] (H O : A) (h_comm : H * O = O * H) :
    H * O - O * H = 0 := by
  rw [h_comm]; exact sub_self (O * H)