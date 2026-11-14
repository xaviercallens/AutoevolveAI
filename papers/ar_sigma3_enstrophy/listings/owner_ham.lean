-- ShellHamiltonian.lean  sha256 5755576ed170a56115ea20d3712fc514e3cfbe27950cfeba934daa2fa22ef882
-- lines 72-73
theorem weights_ok (k : ℕ → ℝ) (n : ℕ) :
    ((1 / 2 : ℝ) ^ (n + 1) * k (n + 1)) * (2 * k n) = ((1 / 2 : ℝ) ^ n * k n) * k (n + 1) := ...
-- lines 84-87
theorem cubic_bound (c : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (hc : ∀ n, |c n| ≤ 1) :
    |∑ n ∈ Finset.range (N + 1), c n * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im|
      ≤ Real.sqrt (∑ n ∈ Finset.range (N + 2), Complex.normSq (v n))
        * ∑ n ∈ Finset.range (N + 2), Complex.normSq (v n) := ...
-- lines 126-131
theorem dispersive_norm_le (q c : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (Hval : ℝ) (hc : ∀ n, |c n| ≤ 1)
    (hH : Hval = ∑ n ∈ Finset.range (N + 2), q n * Complex.normSq (v n)
      + ∑ n ∈ Finset.range (N + 1), c n * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im) :
    ∑ n ∈ Finset.range (N + 2), q n * Complex.normSq (v n)
      ≤ Hval + Real.sqrt (∑ n ∈ Finset.range (N + 2), Complex.normSq (v n))
        * ∑ n ∈ Finset.range (N + 2), Complex.normSq (v n) := ...
