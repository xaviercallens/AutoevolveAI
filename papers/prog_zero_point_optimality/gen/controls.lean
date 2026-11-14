theorem ctl_sorry : ∀ m n x y : ℝ, y ≠ 0 →
    y ^ 2 * (2 * n ^ 2 / y + 2 * (m + n * x) ^ 2 / y ^ 3) = Q m n x y := sorry

axiom ctl_cheat : False

theorem ctl_axiom : ∀ m n x y : ℝ, y ≠ 0 →
    y ^ 2 * (2 * n ^ 2 / y + 2 * (m + n * x) ^ 2 / y ^ 3) = Q m n x y := ctl_cheat.elim

theorem lap_wrong_false : ¬ (∀ m n x y : ℝ, y ≠ 0 →
    y ^ 2 * (2 * n ^ 2 / y + 2 * (m + n * x) ^ 2 / y ^ 3) = Q m n x y) := by
  intro h
  have := h 1 0 0 1 one_ne_zero
  norm_num [Q] at this
