import Triangular.RieszFinite

open OAI.AtomicTriangular OAI.SevenEighths TriangularRiesz

-- negative control (b): the producer's D1b proof transplanted to s = 2 (must fail: the sum diverges)
theorem ctl_b_sameproof : latticeEnergy (riesz 2) < ⊤ := by
  have hσ : 1 < (2:ℝ) / 2 := by linarith
  set Q : ℤ × ℤ → ℝ := fun jk => (jk.1 : ℝ) ^ 2 + (jk.1 : ℝ) * jk.2 + (jk.2 : ℝ) ^ 2 with hQ
  have hQsum : Summable (fun jk : ℤ × ℤ => Q jk ^ (-((2:ℝ) / 2))) := by
    have hn := LatticeSummability.summable_normForm_neg_rpow hσ
    let e : ℤ × ℤ ≃ ℤ × ℤ := Equiv.prodCongr (Equiv.refl ℤ) (Equiv.neg ℤ)
    have := (e.summable_iff).2 hn
    convert this using 2 with jk
    simp only [e, Function.comp_apply, Equiv.prodCongr_apply, Equiv.coe_refl, id_eq, Prod.map_fst, Prod.map_snd,
      Equiv.neg_apply, EisensteinTheta.normForm, hQ]
    push_cast
    ring_nf
  sorry
