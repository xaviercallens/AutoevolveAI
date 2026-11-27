-- Autoresearch_EnstrophyFlow.lean lines 159-163
theorem rate_zero (k ω q g : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ)
    (hg : ∀ n, g (n + 1) * (2 * k n) = g n * k (n + 1))
    (hw : ∀ n, 2 * q (n + 1) * k n + g n * (2 * ω n - ω (n + 1)) = 2 * q n * k n)
    (hbc : v (N + 2) = 0) :
    dHam q g N v (F k ω v) = 0 := ...
