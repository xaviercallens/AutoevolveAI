-- Autoresearch_EnstrophyFlow.lean  sha256 4cd746897f58f7a18eb27e95f703b43d49ec0eb5c5f38753cd5f0bc1a99a8dd4
-- lines 323-328
theorem enstrophy_bound_along_flow (D : ℝ) (N : ℕ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hsol : ∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => u s n) (F kk (fun m => D * kk m ^ 3) (u t) n) t)
    (hbc : ∀ t ∈ Set.Icc (0 : ℝ) T, u t (N + 2) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T,
      2 * D * enstrophy N (u t) ≤ ham3 D N (u 0) + (2 * energy N (u 0)) ^ (3 / 2 : ℝ) := ...
-- lines 338-343
theorem enstrophy_le_along_flow (D : ℝ) (hD : 0 < D) (N : ℕ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hsol : ∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => u s n) (F kk (fun m => D * kk m ^ 3) (u t) n) t)
    (hbc : ∀ t ∈ Set.Icc (0 : ℝ) T, u t (N + 2) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T,
      enstrophy N (u t) ≤ (ham3 D N (u 0) + (2 * energy N (u 0)) ^ (3 / 2 : ℝ)) / (2 * D) := ...
-- lines 351-355
theorem zero_trajectory_is_solution (D : ℝ) (N : ℕ) (T : ℝ) :
    (∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => (fun (_ : ℝ) (_ : ℕ) => (0 : ℂ)) s n)
        (F kk (fun m => D * kk m ^ 3) ((fun (_ : ℝ) (_ : ℕ) => (0 : ℂ)) t) n) t)
    ∧ (∀ t ∈ Set.Icc (0 : ℝ) T, (fun (_ : ℝ) (_ : ℕ) => (0 : ℂ)) t (N + 2) = 0) := ...
