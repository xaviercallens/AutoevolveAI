theorem moran_fixation_limit {N : ℕ} {r : ℝ} (hN : 0 < N) (hr : 0 < r) (i : Fin (N + 1)) :
    Tendsto (fun n => kPow (moranP N r) n i (Fin.last N)) atTop (𝓝 (moranFix N r i)) ∧
    Tendsto (fun n => kPow (moranP N r) n i 0) atTop (𝓝 (1 - moranFix N r i)) := -- proof elided

theorem moran_fixation_limit_closed {N : ℕ} {r : ℝ} (hN : 0 < N) (hr : 0 < r) (hr1 : r ≠ 1)
    (i : Fin (N + 1)) :
    Tendsto (fun n => kPow (moranP N r) n i (Fin.last N)) atTop
      (𝓝 ((1 - r⁻¹ ^ (i : ℕ)) / (1 - r⁻¹ ^ N))) := -- proof elided

theorem moran_fixation_limit_neutral {N : ℕ} (hN : 0 < N) (i : Fin (N + 1)) :
    Tendsto (fun n => kPow (moranP N 1) n i (Fin.last N)) atTop (𝓝 (((i : ℕ) : ℝ) / N)) := -- proof elided

theorem moran_fixation_unique {N : ℕ} {r : ℝ} (hN : 0 < N) (hr : 0 < r) {g : Fin (N + 1) → ℝ}
    (hg : InteriorHarmonic (moranP N r) g) (g0 : g 0 = 0) (g1 : g (Fin.last N) = 1) :
    ∀ i, g i = moranFix N r i := -- proof elided
