-- owner ShellHamiltonian.lean lines 84-87
theorem cubic_bound (c : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (hc : ∀ n, |c n| ≤ 1) :
    |∑ n ∈ Finset.range (N + 1), c n * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im|
      ≤ Real.sqrt (∑ n ∈ Finset.range (N + 2), Complex.normSq (v n))
        * ∑ n ∈ Finset.range (N + 2), Complex.normSq (v n) := ...
