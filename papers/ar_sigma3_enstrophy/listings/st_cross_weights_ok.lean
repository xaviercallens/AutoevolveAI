-- Autoresearch_EnstrophyFlow.lean lines 188-190
theorem cross_weights_ok (k ω : ℕ → ℝ) (n : ℕ) :
    2 * ((1 / 2 : ℝ) ^ (n + 1) * ω (n + 1)) * k n + ((1 / 2 : ℝ) ^ n * k n) * (2 * ω n - ω (n + 1))
      = 2 * ((1 / 2 : ℝ) ^ n * ω n) * k n := ...
