import Triangular.Riesz
import OAI.NumberTheory.DirichletL.LatticeSummability

/-!
# D1b: the Riesz `s`-energy of the triangular lattice is finite for `s > 2`

So `TriangularRiesz.triangular_riesz_optimal` is not the trivial `⊤ ≤ ⊤` there. Ingredients:
`‖triangularPoint (j, k)‖² = (1/b) (j² + jk + k²)` with `b = √3/2`, reindexing through the injective
`triangularPoint`, and openai/math's `summable_normForm_neg_rpow` for `x² - xy + y²` after `k ↦ -k`.
-/

namespace TriangularRiesz

open OAI.AtomicTriangular OAI.SevenEighths

lemma b_pos : 0 < b := by unfold b; positivity

lemma b_sq : b ^ 2 = 3 / 4 := by
  unfold b
  rw [div_pow, Real.sq_sqrt (by norm_num)]
  norm_num

/-- The squared norm of a lattice point. -/
lemma norm_sq_triangularPoint (j k : ℤ) :
    ‖triangularPoint (j, k)‖ ^ 2 = (1 / b) * ((j : ℝ) ^ 2 + (j : ℝ) * k + (k : ℝ) ^ 2) := by
  rw [EuclideanSpace.real_norm_sq_eq]
  simp only [triangularPoint, Fin.sum_univ_two, PiLp.smul_apply, PiLp.add_apply, EuclideanSpace.single_apply,
    smul_eq_mul]
  norm_num
  have hb := b_pos
  have hsb : (Real.sqrt b) ^ 2 = b := Real.sq_sqrt hb.le
  have hb2 := b_sq
  field_simp
  rw [hsb, hb2]
  ring

/-- A chosen index of a lattice point. -/
noncomputable def toIdx (a : {x : Plane // x ∈ A ∧ x ≠ 0}) : ℤ × ℤ := Classical.choose a.2.1

lemma toIdx_spec (a : {x : Plane // x ∈ A ∧ x ≠ 0}) : triangularPoint (toIdx a) = a.val :=
  Classical.choose_spec a.2.1

lemma toIdx_injective : Function.Injective toIdx := by
  intro a a' h
  apply Subtype.ext
  rw [← toIdx_spec a, ← toIdx_spec a', h]

/-- **D1b.** For every `s > 2` the Riesz `s`-energy of the density-one triangular lattice is finite. -/
theorem latticeEnergy_riesz_lt_top {s : ℝ} (hs : 2 < s) : latticeEnergy (riesz s) < ⊤ := by
  have hσ : 1 < s / 2 := by linarith
  set Q : ℤ × ℤ → ℝ := fun jk => (jk.1 : ℝ) ^ 2 + (jk.1 : ℝ) * jk.2 + (jk.2 : ℝ) ^ 2 with hQ
  have hQ0 : ∀ jk, 0 ≤ Q jk := by
    intro jk
    simp only [hQ]
    nlinarith [sq_nonneg ((jk.1 : ℝ) + jk.2), sq_nonneg (jk.1 : ℝ), sq_nonneg (jk.2 : ℝ)]
  -- Σ Q^(-σ) over ℤ² from openai/math, via (j,k) ↦ (j,-k)
  have hQsum : Summable (fun jk : ℤ × ℤ => Q jk ^ (-(s / 2))) := by
    have hn := LatticeSummability.summable_normForm_neg_rpow hσ
    let e : ℤ × ℤ ≃ ℤ × ℤ := Equiv.prodCongr (Equiv.refl ℤ) (Equiv.neg ℤ)
    have := (e.summable_iff).2 hn
    convert this using 2 with jk
    simp only [e, Function.comp_apply, Equiv.prodCongr_apply, Equiv.coe_refl, id_eq, Prod.map_fst, Prod.map_snd,
      Equiv.neg_apply, EisensteinTheta.normForm, hQ]
    push_cast
    ring_nf
  have hh : Summable (fun jk : ℤ × ℤ => ((1 / b) * Q jk) ^ (-(s / 2))) := by
    have : (fun jk : ℤ × ℤ => ((1 / b) * Q jk) ^ (-(s / 2))) =
        fun jk => (1 / b) ^ (-(s / 2)) * Q jk ^ (-(s / 2)) := by
      funext jk
      rw [Real.mul_rpow (by have := b_pos; positivity) (hQ0 jk)]
    rw [this]
    exact hQsum.mul_left _
  set f : {x : Plane // x ∈ A ∧ x ≠ 0} → ℝ := fun a => riesz s (‖a.val‖ ^ 2) with hf
  have hf0 : ∀ a, 0 ≤ f a := fun a => Real.rpow_nonneg (sq_nonneg _) _
  have hfsum : Summable f := by
    have := hh.comp_injective toIdx_injective
    convert this using 1
    funext a
    simp only [hf, Function.comp_apply, riesz]
    rw [← toIdx_spec a]
    obtain ⟨j, k⟩ := toIdx a
    rw [norm_sq_triangularPoint]
  unfold latticeEnergy
  rw [show (fun a : {x : Plane // x ∈ A ∧ x ≠ 0} => ENNReal.ofReal (riesz s (‖a.val‖ ^ 2))) = fun a => ENNReal.ofReal (f a) from rfl]
  rw [← ENNReal.ofReal_tsum_of_nonneg hf0 hfsum]
  exact ENNReal.ofReal_lt_top

end TriangularRiesz
