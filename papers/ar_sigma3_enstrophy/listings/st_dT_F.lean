-- Autoresearch_EnstrophyFlow.lean lines 124-127
theorem dT_F (k ω : ℕ → ℝ) (v : ℕ → ℂ) (n : ℕ) :
    (2 * (starRingEnd ℂ) (v n) * (starRingEnd ℂ) (F k ω v n) * v (n + 1)
        + (starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * F k ω v (n + 1)).im
      = dT k v n + (2 * ω n - ω (n + 1)) * R v n := ...
