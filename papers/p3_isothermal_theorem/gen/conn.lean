theorem cutPositive_of_strongly_connected {μ : Fin n → ℝ} {W : Fin n → Fin n → ℝ}
    (hμ : ∀ i, 0 < μ i) (hsc : StronglyConnected W) : CutPositive μ W := -- proof elided
