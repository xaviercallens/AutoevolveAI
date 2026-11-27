-- Autoresearch_EnstrophyFlow.lean  sha256 4cd746897f58f7a18eb27e95f703b43d49ec0eb5c5f38753cd5f0bc1a99a8dd4
-- lines 70-71
theorem enstrophy_bound (D : ℝ) (N : ℕ) (v : ℕ → ℂ) :
    2 * D * enstrophy N v ≤ ham3 D N v + (2 * energy N v) ^ (3 / 2 : ℝ) := ...
-- lines 188-190
theorem cross_weights_ok (k ω : ℕ → ℝ) (n : ℕ) :
    2 * ((1 / 2 : ℝ) ^ (n + 1) * ω (n + 1)) * k n + ((1 / 2 : ℝ) ^ n * k n) * (2 * ω n - ω (n + 1))
      = 2 * ((1 / 2 : ℝ) ^ n * ω n) * k n := ...
-- lines 159-163
theorem rate_zero (k ω q g : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ)
    (hg : ∀ n, g (n + 1) * (2 * k n) = g n * k (n + 1))
    (hw : ∀ n, 2 * q (n + 1) * k n + g n * (2 * ω n - ω (n + 1)) = 2 * q n * k n)
    (hbc : v (N + 2) = 0) :
    dHam q g N v (F k ω v) = 0 := ...
-- lines 195-196
theorem ham_rate_zero (k ω : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (hbc : v (N + 2) = 0) :
    dHam (fun n => (1 / 2 : ℝ) ^ n * ω n) (fun n => (1 / 2 : ℝ) ^ n * k n) N v (F k ω v) = 0 := ...
-- lines 200-201
theorem energy_rate_zero (k ω : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (hbc : v (N + 2) = 0) :
    ∑ n ∈ Finset.range (N + 2), 2 * ((starRingEnd ℂ) (v n) * F k ω v n).re = 0 := ...
-- lines 255-257
theorem hasDerivAt_hamG (q g : ℕ → ℝ) (N : ℕ) (u : ℝ → ℕ → ℂ) (u' : ℕ → ℂ) (t : ℝ)
    (hu : ∀ n, n < N + 2 → HasDerivAt (fun s => u s n) (u' n) t) :
    HasDerivAt (fun s => hamG q g N (u s)) (dHam q g N (u t) u') t := ...
-- lines 272-275
theorem const_on_Icc (Φ : (ℕ → ℂ) → ℝ) (Φ' : (ℕ → ℂ) → ℝ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hd : ∀ t ∈ Set.Icc (0 : ℝ) T, HasDerivAt (fun s => Φ (u s)) (Φ' (u t)) t)
    (hz : ∀ t ∈ Set.Icc (0 : ℝ) T, Φ' (u t) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T, Φ (u t) = Φ (u 0) := ...
-- lines 287-293
theorem ham_conserved (k ω : ℕ → ℝ) (N : ℕ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hsol : ∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => u s n) (F k ω (u t) n) t)
    (hbc : ∀ t ∈ Set.Icc (0 : ℝ) T, u t (N + 2) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T,
      hamG (fun n => (1 / 2 : ℝ) ^ n * ω n) (fun n => (1 / 2 : ℝ) ^ n * k n) N (u t)
        = hamG (fun n => (1 / 2 : ℝ) ^ n * ω n) (fun n => (1 / 2 : ℝ) ^ n * k n) N (u 0) := ...
