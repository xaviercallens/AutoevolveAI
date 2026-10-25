-- Autoresearch_EnstrophyFlow.lean lines 351-355
theorem zero_trajectory_is_solution (D : ℝ) (N : ℕ) (T : ℝ) :
    (∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => (fun (_ : ℝ) (_ : ℕ) => (0 : ℂ)) s n)
        (F kk (fun m => D * kk m ^ 3) ((fun (_ : ℝ) (_ : ℕ) => (0 : ℂ)) t) n) t)
    ∧ (∀ t ∈ Set.Icc (0 : ℝ) T, (fun (_ : ℝ) (_ : ℕ) => (0 : ℂ)) t (N + 2) = 0) := ...
