theorem problem_60_atiyah_singer_dirac_index
    (dim_ker dim_coker : ℕ) (h_selfadjoint : dim_ker = dim_coker) :
    (dim_ker : ℤ) - (dim_coker : ℤ) = 0 := by
  rw [h_selfadjoint, sub_self]