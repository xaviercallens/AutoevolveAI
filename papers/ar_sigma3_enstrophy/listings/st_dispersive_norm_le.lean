-- owner ShellHamiltonian.lean lines 126-131
theorem dispersive_norm_le (q c : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (Hval : ℝ) (hc : ∀ n, |c n| ≤ 1)
    (hH : Hval = ∑ n ∈ Finset.range (N + 2), q n * Complex.normSq (v n)
      + ∑ n ∈ Finset.range (N + 1), c n * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im) :
    ∑ n ∈ Finset.range (N + 2), q n * Complex.normSq (v n)
      ≤ Hval + Real.sqrt (∑ n ∈ Finset.range (N + 2), Complex.normSq (v n))
        * ∑ n ∈ Finset.range (N + 2), Complex.normSq (v n) := ...
