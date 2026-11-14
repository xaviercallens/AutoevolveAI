-- Autoresearch_EnstrophyFlow.lean lines 272-275
theorem const_on_Icc (Φ : (ℕ → ℂ) → ℝ) (Φ' : (ℕ → ℂ) → ℝ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hd : ∀ t ∈ Set.Icc (0 : ℝ) T, HasDerivAt (fun s => Φ (u s)) (Φ' (u t)) t)
    (hz : ∀ t ∈ Set.Icc (0 : ℝ) T, Φ' (u t) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T, Φ (u t) = Φ (u 0) := ...
