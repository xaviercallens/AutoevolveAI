theorem problem_7_discrete_gronwall
    (E : ℕ → ℝ) (α : ℝ) (hα : 0 ≤ α) (_hE : ∀ n, 0 ≤ E n)
    (h_step : ∀ n, E (n + 1) ≤ (1 + α) * E n) :
    ∀ n, E n ≤ (1 + α) ^ n * E 0 := by
  intro n
  induction n with
  | zero => simp
  | succ k ih =>
    calc
      E (k + 1) ≤ (1 + α) * E k := h_step k
      _ ≤ (1 + α) * ((1 + α) ^ k * E 0) := mul_le_mul_of_nonneg_left ih (by linarith)
      _ = (1 + α) ^ (k + 1) * E 0 := by rw [pow_succ', mul_assoc]