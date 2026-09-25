theorem problem_21_picard_lindelof {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E]
    {f : ℝ → E → E} {tmin tmax : ℝ} {t₀ : Set.Icc tmin tmax} {x₀ : E} {a L K : ℝ≥0}
    (hf : IsPicardLindelof f t₀ x₀ a 0 L K) :
    ∃ α : ℝ → E, α t₀ = x₀ ∧ ∀ t ∈ Icc tmin tmax, HasDerivWithinAt α (f t (α t)) (Icc tmin tmax) t :=
  IsPicardLindelof.exists_eq_forall_mem_Icc_hasDerivWithinAt₀ hf