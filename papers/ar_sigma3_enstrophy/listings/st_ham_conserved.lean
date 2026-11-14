-- Autoresearch_EnstrophyFlow.lean lines 287-293
theorem ham_conserved (k ω : ℕ → ℝ) (N : ℕ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hsol : ∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => u s n) (F k ω (u t) n) t)
    (hbc : ∀ t ∈ Set.Icc (0 : ℝ) T, u t (N + 2) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T,
      hamG (fun n => (1 / 2 : ℝ) ^ n * ω n) (fun n => (1 / 2 : ℝ) ^ n * k n) N (u t)
        = hamG (fun n => (1 / 2 : ℝ) ^ n * ω n) (fun n => (1 / 2 : ℝ) ^ n * k n) N (u 0) := ...
