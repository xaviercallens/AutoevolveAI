theorem moranFix_harmonic_nat {N : ℕ} {r : ℝ} (hr : 0 < r) {i : ℕ} (h1 : 0 < i) :
    moranUp N r i * moranFix N r (i + 1) + moranDown N r i * moranFix N r (i - 1)
      + (1 - moranUp N r i - moranDown N r i) * moranFix N r i = moranFix N r i := -- proof elided

theorem moran_var_pos_nat {N : ℕ} {r : ℝ} (hN : 0 < N) (hr : 0 < r) {i : ℕ} (h1 : 0 < i)
    (h2 : i < N) :
    0 < moranUp N r i * (moranFix N r (i + 1) - moranFix N r i) ^ 2
      + moranDown N r i * (moranFix N r (i - 1) - moranFix N r i) ^ 2
      + (1 - moranUp N r i - moranDown N r i) * (moranFix N r i - moranFix N r i) ^ 2 := -- proof elided

theorem moranFix_closed {N : ℕ} {r : ℝ} (hr1 : r ≠ 1) (i : ℕ) :
    moranFix N r i = (1 - r⁻¹ ^ i) / (1 - r⁻¹ ^ N) := -- proof elided

theorem moranFix_neutral (N i : ℕ) : moranFix N 1 i = (i : ℝ) / N := -- proof elided

theorem moran_closed_tendsto_neutral {N : ℕ} (hN : 0 < N) (i : ℕ) :
    Tendsto (fun r : ℝ => (1 - r⁻¹ ^ i) / (1 - r⁻¹ ^ N)) (𝓝[≠] 1) (𝓝 ((i : ℝ) / N)) := -- proof elided
