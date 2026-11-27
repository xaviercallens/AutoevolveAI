theorem up_eq (μ : Fin n → ℝ) (W : Fin n → Fin n → ℝ) (r : ℝ) (S : Finset (Fin n)) :
    upP μ W r S = r * cutOut μ W S / totFit μ r S := -- proof elided

theorem down_eq (μ : Fin n → ℝ) (W : Fin n → Fin n → ℝ) (r : ℝ) (S : Finset (Fin n)) :
    downP μ W r S = cutIn μ W S / totFit μ r S := -- proof elided

theorem cut_balance {μ : Fin n → ℝ} {W : Fin n → Fin n → ℝ} (hrow : ∀ i, ∑ j, W i j = 1)
    (hstat : ∀ j, ∑ i, μ i * W i j = μ j) (S : Finset (Fin n)) : cutOut μ W S = cutIn μ W S := -- proof elided

theorem forward_bias {μ : Fin n → ℝ} {W : Fin n → Fin n → ℝ} (r : ℝ) (hrow : ∀ i, ∑ j, W i j = 1)
    (hstat : ∀ j, ∑ i, μ i * W i j = μ j) (S : Finset (Fin n)) :
    upP μ W r S = r * downP μ W r S := -- proof elided
