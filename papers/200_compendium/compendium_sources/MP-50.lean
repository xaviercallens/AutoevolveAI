theorem problem_50_bell_chsh_discrete_bound
    (A A' B B' : ℝ)
    (hA : A = 1 ∨ A = -1) (hA' : A' = 1 ∨ A' = -1)
    (hB : B = 1 ∨ B = -1) (hB' : B' = 1 ∨ B' = -1) :
    A * B - A * B' + A' * B + A' * B' = 2 ∨ A * B - A * B' + A' * B + A' * B' = -2 := by
  rcases hA with rfl | rfl <;>
  rcases hA' with rfl | rfl <;>
  rcases hB with rfl | rfl <;>
  rcases hB' with rfl | rfl <;>
  norm_num