theorem problem_26_noether_conserved_charge
    {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    (p X : ℝ → E) (p' X' : E) (t : ℝ)
    (hp : HasDerivAt p p' t) (hX : HasDerivAt X X' t)
    (h_symm : ⟪p t, X'⟫ + ⟪p', X t⟫ = (0 : ℝ)) :
    HasDerivAt (fun s => ⟪p s, X s⟫) (0 : ℝ) t := by
  have h := HasDerivAt.inner ℝ hp hX
  rw [h_symm] at h
  exact h