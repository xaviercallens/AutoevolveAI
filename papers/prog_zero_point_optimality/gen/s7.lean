theorem deriv_at_one_of_inversion (f : ℝ → ℝ) (d : ℝ) (hf : HasDerivAt f d 1)
    (hinv : ∀ α : ℝ, 0 < α → f (1 / α) = α * f α) : d = -f 1 / 2 := ... -- proof elided
