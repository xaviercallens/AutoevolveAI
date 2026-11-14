-- Autoresearch_EnstrophyFlow.lean  sha256 4cd746897f58f7a18eb27e95f703b43d49ec0eb5c5f38753cd5f0bc1a99a8dd4
-- lines 40-40
noncomputable def kk (n : ℕ) : ℝ := (2 : ℝ) ^ n
-- lines 43-44
noncomputable def energy (N : ℕ) (v : ℕ → ℂ) : ℝ :=
  (1 / 2) * ∑ n ∈ Finset.range (N + 2), Complex.normSq (v n)
-- lines 47-48
noncomputable def enstrophy (N : ℕ) (v : ℕ → ℂ) : ℝ :=
  (1 / 2) * ∑ n ∈ Finset.range (N + 2), kk n ^ 2 * Complex.normSq (v n)
-- lines 52-55
noncomputable def ham3 (D : ℝ) (N : ℕ) (v : ℕ → ℂ) : ℝ :=
  ∑ n ∈ Finset.range (N + 2), (1 / 2 : ℝ) ^ n * (D * kk n ^ 3) * Complex.normSq (v n)
    + ∑ n ∈ Finset.range (N + 1),
        ((1 / 2 : ℝ) ^ n * kk n) * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im
-- lines 91-92
noncomputable def F (k ω : ℕ → ℝ) (v : ℕ → ℂ) (n : ℕ) : ℂ :=
  shellBc k n v - Complex.I * (ω n : ℂ) * v n
-- lines 95-96
noncomputable def R (v : ℕ → ℂ) (n : ℕ) : ℝ :=
  ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).re
-- lines 99-102
noncomputable def hamG (q g : ℕ → ℝ) (N : ℕ) (v : ℕ → ℂ) : ℝ :=
  ∑ n ∈ Finset.range (N + 2), q n * Complex.normSq (v n)
    + ∑ n ∈ Finset.range (N + 1),
        g n * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im
-- lines 105-109
noncomputable def dHam (q g : ℕ → ℝ) (N : ℕ) (v w : ℕ → ℂ) : ℝ :=
  ∑ n ∈ Finset.range (N + 2), q n * (2 * ((starRingEnd ℂ) (v n) * w n).re)
    + ∑ n ∈ Finset.range (N + 1), g n *
        (2 * (starRingEnd ℂ) (v n) * (starRingEnd ℂ) (w n) * v (n + 1)
          + (starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * w (n + 1)).im
