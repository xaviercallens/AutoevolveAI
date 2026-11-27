theorem moranFix_card_harmonic {μ : Fin n → ℝ} {W : Fin n → Fin n → ℝ} {r : ℝ} (hn : 0 < n)
    (hr : 0 < r) (hμ : ∀ i, 0 < μ i) (hW : RowStochastic W) (hstat : ∀ j, ∑ i, μ i * W i j = μ j)
    {S : Finset (Fin n)} (hS : 0 < S.card) :
    ∑ T, bdK μ W r S T * moranFix n r T.card = moranFix n r S.card := -- proof elided

theorem moranFix_card_var_pos {μ : Fin n → ℝ} {W : Fin n → Fin n → ℝ} {r : ℝ} (hn : 0 < n)
    (hr : 0 < r) (hμ : ∀ i, 0 < μ i) (hW : RowStochastic W) {S : Finset (Fin n)}
    {i0 j0 : Fin n} (hi0 : i0 ∈ S) (hj0 : j0 ∉ S) (hw : 0 < μ i0 * W i0 j0) :
    0 < ∑ T, bdK μ W r S T * (moranFix n r T.card - moranFix n r S.card) ^ 2 := -- proof elided
