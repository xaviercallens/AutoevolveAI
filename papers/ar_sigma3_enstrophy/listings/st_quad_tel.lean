-- Autoresearch_EnstrophyFlow.lean lines 143-147
theorem quad_tel (k ω q g : ℕ → ℝ) (v : ℕ → ℂ)
    (hw : ∀ n, 2 * q (n + 1) * k n + g n * (2 * ω n - ω (n + 1)) = 2 * q n * k n) :
    ∀ M : ℕ, ∑ n ∈ Finset.range (M + 1), q n * (2 * ((starRingEnd ℂ) (v n) * shellBc k n v).re)
        + ∑ n ∈ Finset.range M, g n * ((2 * ω n - ω (n + 1)) * R v n)
      = -(2 * q M * k M * R v M) := ...
