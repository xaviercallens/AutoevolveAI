-- Autoresearch_EnstrophyFlow.lean lines 338-343
theorem enstrophy_le_along_flow (D : ℝ) (hD : 0 < D) (N : ℕ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hsol : ∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => u s n) (F kk (fun m => D * kk m ^ 3) (u t) n) t)
    (hbc : ∀ t ∈ Set.Icc (0 : ℝ) T, u t (N + 2) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T,
      enstrophy N (u t) ≤ (ham3 D N (u 0) + (2 * energy N (u 0)) ^ (3 / 2 : ℝ)) / (2 * D) := ...
