import Triangular.RieszFinite

/-!
# Autoresearch 2026-10-25, H1 / H1b: bilayer (dipolar / indirect) exciton potential

For `d > 0` the classical electron-hole bilayer interaction, in the variable `t = r²`, is
`g_d(t) = 2 (t^{-1/2} - (t + d²)^{-1/2})` (e-e and h-h repel as `1/r`; the cross-layer pair attracts as
`1/√(r² + d²)`). We show it is `AdmissiblePotential` (H1), hence the triangular lattice minimises its energy among
locally finite density-one configurations by upstream's `universal_energy_minimum`, and that the triangular lattice
energy is finite (H1b), so the corollary is not `⊤ ≤ ⊤`.

Negative control: `h_d(t) = t^{-1/2} - 2 (t + d²)^{-1/2}` is not admissible (it is negative at `t = d²`).

Everything is conditional on upstream's theorem (AI-generated, not peer reviewed) and on definition fidelity.
-/

namespace AutoresearchDipolar

open OAI.AtomicTriangular TriangularRiesz

/-- Bilayer exciton potential in the variable `t = r²`. -/
noncomputable def g (d : ℝ) : ℝ → ℝ := fun t => 2 * (t ^ (-(1 / 2 : ℝ)) - (t + d ^ 2) ^ (-(1 / 2 : ℝ)))

/-- Negative control potential. -/
noncomputable def h (d : ℝ) : ℝ → ℝ := fun t => t ^ (-(1 / 2 : ℝ)) - 2 * (t + d ^ 2) ^ (-(1 / 2 : ℝ))

lemma contDiffAt_shift {c t a : ℝ} {n : WithTop ℕ∞} (hc : 0 ≤ c) (ht : 0 < t) :
    ContDiffAt ℝ n (fun x : ℝ => (x + c) ^ a) t := by
  have hne : t + c ≠ 0 := by positivity
  exact (Real.contDiffAt_rpow_const_of_ne (p := a) hne).comp t (contDiffAt_id.add contDiffAt_const)

lemma iteratedDeriv_rpow (a : ℝ) (r : ℕ) (t : ℝ) :
    iteratedDeriv r (fun x : ℝ => x ^ a) t = (descPochhammer ℝ r).eval a * t ^ (a - r) := by
  rw [iteratedDeriv_eq_iterate, Real.iter_deriv_rpow_const]

lemma iteratedDeriv_shift (a c : ℝ) (r : ℕ) (t : ℝ) :
    iteratedDeriv r (fun x : ℝ => (x + c) ^ a) t = (descPochhammer ℝ r).eval a * (t + c) ^ (a - r) := by
  rw [iteratedDeriv_comp_add_const (f := fun x : ℝ => x ^ a)]
  exact iteratedDeriv_rpow a r (t + c)

lemma iteratedDeriv_g (d : ℝ) (r : ℕ) {t : ℝ} (ht : 0 < t) :
    iteratedDeriv r (g d) t =
      2 * ((descPochhammer ℝ r).eval (-(1 / 2 : ℝ)) *
        (t ^ (-(1 / 2 : ℝ) - r) - (t + d ^ 2) ^ (-(1 / 2 : ℝ) - r))) := by
  have h1 : ContDiffAt ℝ r (fun x : ℝ => x ^ (-(1 / 2 : ℝ))) t :=
    Real.contDiffAt_rpow_const_of_ne (ne_of_gt ht)
  have h2 : ContDiffAt ℝ r (fun x : ℝ => (x + d ^ 2) ^ (-(1 / 2 : ℝ))) t :=
    contDiffAt_shift (sq_nonneg d) ht
  have hsub : ContDiffAt ℝ r ((fun x : ℝ => x ^ (-(1 / 2 : ℝ))) - fun x : ℝ => (x + d ^ 2) ^ (-(1 / 2 : ℝ))) t :=
    h1.sub h2
  have hg : g d = fun x => 2 * (((fun x : ℝ => x ^ (-(1 / 2 : ℝ))) - fun x : ℝ => (x + d ^ 2) ^ (-(1 / 2 : ℝ))) x) := by
    funext x; simp [g]
  rw [hg, iteratedDeriv_const_mul _ hsub, iteratedDeriv_sub h1 h2, iteratedDeriv_rpow, iteratedDeriv_shift]
  ring

lemma sign_desc (r : ℕ) :
    (-1 : ℝ) ^ r * (descPochhammer ℝ r).eval (-(1 / 2 : ℝ)) = (ascPochhammer ℝ r).eval (1 / 2 : ℝ) := by
  have hasc := ascPochhammer_eval_neg_eq_descPochhammer (R := ℝ) (-(1 / 2 : ℝ)) r
  rw [neg_neg] at hasc
  exact hasc.symm

lemma diff_nonneg (c e : ℝ) (hc : 0 ≤ c) (he : e ≤ 0) {t : ℝ} (ht : 0 < t) :
    0 ≤ t ^ e - (t + c) ^ e := by
  have := Real.rpow_le_rpow_of_nonpos ht (by linarith : t ≤ t + c) he
  linarith

/-- **H1.** The bilayer exciton potential is admissible (smooth, nonnegative, completely monotone on `(0, ∞)`). -/
theorem dipolar_admissible {d : ℝ} (_hd : 0 < d) : AdmissiblePotential (g d) := by
  refine ⟨?_, ?_, ?_⟩
  · intro x hx
    have h1 : ContDiffAt ℝ (⊤ : ℕ∞) (fun x : ℝ => x ^ (-(1 / 2 : ℝ))) x :=
      Real.contDiffAt_rpow_const_of_ne (ne_of_gt hx)
    have h2 : ContDiffAt ℝ (⊤ : ℕ∞) (fun x : ℝ => (x + d ^ 2) ^ (-(1 / 2 : ℝ))) x :=
      contDiffAt_shift (sq_nonneg d) hx
    exact (contDiffAt_const.mul (h1.sub h2)).contDiffWithinAt
  · intro t ht
    have := diff_nonneg (d ^ 2) (-(1 / 2 : ℝ)) (sq_nonneg d) (by norm_num) ht
    simp only [g]
    linarith
  · intro r t ht
    rw [iteratedDeriv_g d r ht]
    have hpos := ascPochhammer_pos r (1 / 2 : ℝ) (by norm_num)
    have hdiff := diff_nonneg (d ^ 2) (-(1 / 2 : ℝ) - r) (sq_nonneg d)
      (by have : (0 : ℝ) ≤ r := Nat.cast_nonneg r; linarith) ht
    have hs := sign_desc r
    calc (0 : ℝ) ≤ 2 * ((ascPochhammer ℝ r).eval (1 / 2 : ℝ) *
          (t ^ (-(1 / 2 : ℝ) - r) - (t + d ^ 2) ^ (-(1 / 2 : ℝ) - r))) := by positivity
      _ = (-1 : ℝ) ^ r * (2 * ((descPochhammer ℝ r).eval (-(1 / 2 : ℝ)) *
          (t ^ (-(1 / 2 : ℝ) - r) - (t + d ^ 2) ^ (-(1 / 2 : ℝ) - r)))) := by
        rw [← hs]; ring

/-- **H1 corollary.** The triangular lattice minimises the bilayer exciton energy among locally finite planar
configurations of density one (classical, energies in `[0, ∞]`). -/
theorem triangular_dipolar_optimal {d : ℝ} (hd : 0 < d) (C : Set Plane) (hC : LocallyFinite C)
    (hdens : DensityOne C) : latticeEnergy (g d) ≤ energy (g d) C :=
  (universal_energy_minimum (g d) C (dipolar_admissible hd) hC hdens).1

/-- **Negative control.** `h_d` takes a negative value at `t = d²`. -/
theorem h_neg_at {d : ℝ} (hd : 0 < d) : h d (d ^ 2) < 0 := by
  have hd2 : 0 < d ^ 2 := by positivity
  have hlt : (d ^ 2 + d ^ 2) ^ (-(1 / 2 : ℝ)) > (4 * d ^ 2) ^ (-(1 / 2 : ℝ)) :=
    Real.rpow_lt_rpow_of_neg (by positivity) (by linarith) (by norm_num)
  have h4 : (4 * d ^ 2) ^ (-(1 / 2 : ℝ)) = (1 / 2) * (d ^ 2) ^ (-(1 / 2 : ℝ)) := by
    rw [Real.mul_rpow (by norm_num) hd2.le]
    congr 1
    rw [Real.rpow_neg (by norm_num), ← Real.sqrt_eq_rpow, show (4 : ℝ) = 2 ^ 2 by norm_num,
      Real.sqrt_sq (by norm_num)]
    norm_num
  simp only [h]
  linarith

/-- **Negative control.** `h_d` is not admissible. -/
theorem h_not_admissible {d : ℝ} (hd : 0 < d) : ¬ AdmissiblePotential (h d) := by
  intro H
  have := H.2.1 (d ^ 2) (by positivity)
  linarith [h_neg_at hd]

/-- Key inequality: `t^{-1/2} - (t+c)^{-1/2} ≤ (c/2) t^{-3/2}`. -/
lemma diff_le (c : ℝ) (hc : 0 ≤ c) {t : ℝ} (ht : 0 < t) :
    t ^ (-(1 / 2 : ℝ)) - (t + c) ^ (-(1 / 2 : ℝ)) ≤ c / 2 * t ^ (-(3 / 2 : ℝ)) := by
  have htc : 0 < t + c := by linarith
  set a := t ^ (-(1 / 2 : ℝ)) with ha
  set b := (t + c) ^ (-(1 / 2 : ℝ)) with hb
  have ha0 : 0 < a := Real.rpow_pos_of_pos ht _
  have hb0 : 0 < b := Real.rpow_pos_of_pos htc _
  have hba : b ≤ a := Real.rpow_le_rpow_of_nonpos ht (by linarith) (by norm_num)
  have hsq : ∀ x : ℝ, 0 < x → (x ^ (-(1 / 2 : ℝ))) ^ 2 * x = 1 := by
    intro x hx
    rw [← Real.rpow_natCast, ← Real.rpow_mul hx.le]
    norm_num
    rw [Real.rpow_neg_one]
    field_simp
  have ha2 : a ^ 2 * t = 1 := hsq t ht
  have hb2 : b ^ 2 * (t + c) = 1 := hsq (t + c) htc
  have ha3 : t ^ (-(3 / 2 : ℝ)) = a ^ 3 := by
    rw [ha, ← Real.rpow_natCast, ← Real.rpow_mul ht.le]
    norm_num
  rw [ha3]
  -- (a - b)(a + b) = c a² b²
  have hkey : (a - b) * (a + b) = c * a ^ 2 * b ^ 2 := by
    have : a ^ 2 - b ^ 2 = a ^ 2 * b ^ 2 * ((t + c) - t) := by
      have e1 : a ^ 2 = a ^ 2 * (b ^ 2 * (t + c)) := by rw [hb2, mul_one]
      have e2 : b ^ 2 = b ^ 2 * (a ^ 2 * t) := by rw [ha2, mul_one]
      calc a ^ 2 - b ^ 2 = a ^ 2 * (b ^ 2 * (t + c)) - b ^ 2 * (a ^ 2 * t) := by rw [← e1, ← e2]
        _ = a ^ 2 * b ^ 2 * ((t + c) - t) := by ring
    nlinarith [this]
  have hab : 0 < a + b := by linarith
  have hgoal : 2 * ((a - b) * (a + b)) ≤ c * a ^ 3 * (a + b) := by
    rw [hkey]
    have : 2 * b ^ 2 ≤ a * (a + b) := by nlinarith
    have hca : 0 ≤ c * a ^ 2 := by positivity
    nlinarith [mul_le_mul_of_nonneg_left this hca]
  have : 2 * (a - b) ≤ c * a ^ 3 := by
    have h' : (2 * (a - b)) * (a + b) ≤ (c * a ^ 3) * (a + b) := by linarith
    exact le_of_mul_le_mul_right h' hab
  linarith

/-- Pointwise bound `g_d(t) ≤ d² · t^{-3/2}`. -/
lemma g_le (d : ℝ) {t : ℝ} (ht : 0 < t) : g d t ≤ d ^ 2 * riesz 3 t := by
  have := diff_le (d ^ 2) (sq_nonneg d) ht
  simp only [g, riesz]
  have e : (-(3 / 2 : ℝ)) = -((3 : ℝ) / 2) := by norm_num
  rw [← e]
  linarith

/-- **H1b.** The triangular-lattice energy of the bilayer exciton potential is finite. -/
theorem latticeEnergy_dipolar_lt_top (d : ℝ) : latticeEnergy (g d) < ⊤ := by
  have hR := latticeEnergy_riesz_lt_top (s := 3) (by norm_num)
  have hle : latticeEnergy (g d) ≤ ENNReal.ofReal (d ^ 2) * latticeEnergy (riesz 3) := by
    unfold latticeEnergy
    rw [← ENNReal.tsum_mul_left]
    refine ENNReal.tsum_le_tsum fun a => ?_
    have hpos : 0 < ‖a.val‖ ^ 2 := by
      have := a.2.2
      positivity
    rw [← ENNReal.ofReal_mul (sq_nonneg d)]
    exact ENNReal.ofReal_le_ofReal (g_le d hpos)
  exact lt_of_le_of_lt hle (ENNReal.mul_lt_top ENNReal.ofReal_lt_top hR)

end AutoresearchDipolar

#print axioms AutoresearchDipolar.dipolar_admissible
#print axioms AutoresearchDipolar.triangular_dipolar_optimal
#print axioms AutoresearchDipolar.h_not_admissible
#print axioms AutoresearchDipolar.latticeEnergy_dipolar_lt_top
