theorem problem_24_spectral_theorem {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    [FiniteDimensional ℝ E] {n : ℕ} (hn : Module.finrank ℝ E = n) (T : E →ₗ[ℝ] E) (hT : T.IsSymmetric) :
    ∃ (b : OrthonormalBasis (Fin n) ℝ E), ∀ i, HasEigenvector T (hT.eigenvalues hn i) (b i) :=
  ⟨hT.eigenvectorBasis hn, hT.hasEigenvector_eigenvectorBasis hn⟩