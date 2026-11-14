-- Autoresearch_EnstrophyFlow.lean lines 255-257
theorem hasDerivAt_hamG (q g : ℕ → ℝ) (N : ℕ) (u : ℝ → ℕ → ℂ) (u' : ℕ → ℂ) (t : ℝ)
    (hu : ∀ n, n < N + 2 → HasDerivAt (fun s => u s n) (u' n) t) :
    HasDerivAt (fun s => hamG q g N (u s)) (dHam q g N (u t) u') t := ...
