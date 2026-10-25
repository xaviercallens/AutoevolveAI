import Triangular.RieszFinite

/-!
# Autoresearch 2026-10-25, H2: Yukawa / Debye–Hückel interaction

For `κ > 0` the screened-Coulomb (Yukawa, Debye–Hückel) pair interaction `e^{-κ r} / r`, written in the variable
`t = r²`, is `g_κ(t) = exp(-κ √t) / √t`. We show it is `AdmissiblePotential`, hence the triangular lattice minimises
its energy among locally finite density-one planar configurations by upstream's `universal_energy_minimum`, and that
the triangular lattice energy is finite, so the corollary is not `⊤ ≤ ⊤`.

Reusable infrastructure proved on the way:
* `mul_sign` (pointwise Leibniz sign lemma) and `admissible_mul`: the product of admissible potentials is admissible;
* `admissible_congr`: admissibility only depends on the values on `(0, ∞)`;
* `phi_admissible`: `exp(-κ √t)` is admissible, by strong induction from `φ' = -(κ/2) t^{-1/2} φ` and Leibniz.

Negative control: `exp(-κ √t) cos t` is not admissible (negative at `t = π`).

Everything is conditional on upstream's theorem (AI-generated, not peer reviewed) and on definition fidelity.
-/

namespace AutoresearchYukawa

open OAI.AtomicTriangular TriangularRiesz

/-- `φ_κ(t) = exp(-κ √t)`. -/
noncomputable def phi (κ : ℝ) : ℝ → ℝ := fun t => Real.exp (-κ * Real.sqrt t)

/-- Yukawa / Debye–Hückel potential in the variable `t = r²`. -/
noncomputable def g (κ : ℝ) : ℝ → ℝ := fun t => Real.exp (-κ * Real.sqrt t) / Real.sqrt t

/-- Negative control potential. -/
noncomputable def c (κ : ℝ) : ℝ → ℝ := fun t => Real.exp (-κ * Real.sqrt t) * Real.cos t

/-- **(P, pointwise).** Leibniz sign lemma: if `f` and `h` have alternating-sign derivatives up to order `r` at `t`,
so does `f * h` at order `r`. -/
lemma mul_sign {f h : ℝ → ℝ} {t : ℝ} (r : ℕ) (hf : ContDiffAt ℝ r f t) (hh : ContDiffAt ℝ r h t)
    (Hf : ∀ i ≤ r, 0 ≤ (-1 : ℝ) ^ i * iteratedDeriv i f t)
    (Hh : ∀ i ≤ r, 0 ≤ (-1 : ℝ) ^ i * iteratedDeriv i h t) :
    0 ≤ (-1 : ℝ) ^ r * iteratedDeriv r (f * h) t := by
  rw [iteratedDeriv_mul hf hh, Finset.mul_sum]
  refine Finset.sum_nonneg fun i hi => ?_
  have hir : i ≤ r := Nat.lt_succ_iff.mp (Finset.mem_range.mp hi)
  have hpow : (-1 : ℝ) ^ r = (-1) ^ i * (-1) ^ (r - i) := by
    rw [← pow_add, Nat.add_sub_cancel' hir]
  have h1 := Hf i hir
  have h2 := Hh (r - i) (Nat.sub_le r i)
  have hc : (0 : ℝ) ≤ (r.choose i : ℝ) := Nat.cast_nonneg _
  calc (0 : ℝ) ≤ (r.choose i : ℝ) *
        (((-1) ^ i * iteratedDeriv i f t) * ((-1) ^ (r - i) * iteratedDeriv (r - i) h t)) :=
        mul_nonneg hc (mul_nonneg h1 h2)
    _ = (-1 : ℝ) ^ r * ((r.choose i : ℝ) * iteratedDeriv i f t * iteratedDeriv (r - i) h t) := by
        rw [hpow]; ring

lemma contDiffAt_of_admissible {f : ℝ → ℝ} (hf : AdmissiblePotential f) {t : ℝ} (ht : 0 < t) (n : ℕ) :
    ContDiffAt ℝ n f t :=
  (hf.1.contDiffAt (Ioi_mem_nhds ht)).of_le (by exact_mod_cast le_top)

/-- **(P).** The product of two admissible potentials is admissible. -/
theorem admissible_mul {f h : ℝ → ℝ} (hf : AdmissiblePotential f) (hh : AdmissiblePotential h) :
    AdmissiblePotential (f * h) := by
  refine ⟨hf.1.mul hh.1, fun t ht => mul_nonneg (hf.2.1 t ht) (hh.2.1 t ht), fun r t ht => ?_⟩
  exact mul_sign r (contDiffAt_of_admissible hf ht r) (contDiffAt_of_admissible hh ht r)
    (fun i _ => hf.2.2 i t ht) (fun i _ => hh.2.2 i t ht)

/-- Admissibility only depends on the values on `(0, ∞)`. -/
theorem admissible_congr {f h : ℝ → ℝ} (hf : AdmissiblePotential f) (heq : Set.EqOn f h (Set.Ioi 0)) :
    AdmissiblePotential h := by
  refine ⟨hf.1.congr (fun x hx => (heq hx).symm), fun t ht => ?_, fun r t ht => ?_⟩
  · rw [← heq ht]; exact hf.2.1 t ht
  · rw [← heq.iteratedDeriv_of_isOpen isOpen_Ioi r ht]
    exact hf.2.2 r t ht

lemma riesz_one_eq {t : ℝ} (ht : 0 < t) : riesz 1 t = (Real.sqrt t)⁻¹ := by
  simp only [riesz]
  rw [Real.sqrt_eq_rpow, ← Real.rpow_neg ht.le]

lemma phi_contDiffAt (κ : ℝ) {t : ℝ} (ht : 0 < t) {n : WithTop ℕ∞} : ContDiffAt ℝ n (phi κ) t :=
  Real.contDiff_exp.contDiffAt.comp t (contDiffAt_const.mul (Real.contDiffAt_sqrt ht.ne'))

lemma phi_hasDerivAt (κ : ℝ) {t : ℝ} (ht : 0 < t) :
    HasDerivAt (phi κ) (-(κ / 2) * (riesz 1 t * phi κ t)) t := by
  have h1 : HasDerivAt (fun x => -κ * Real.sqrt x) (-κ * (1 / (2 * Real.sqrt t))) t :=
    (Real.hasDerivAt_sqrt ht.ne').const_mul (-κ)
  have h2 := h1.exp
  show HasDerivAt (fun x => Real.exp (-κ * Real.sqrt x)) _ t
  convert h2 using 1
  rw [riesz_one_eq ht]
  simp only [phi]
  ring

/-- Signs of the derivatives of `φ_κ`, by strong induction (Leibniz on `φ' = -(κ/2) t^{-1/2} φ`). -/
lemma phi_sign {κ : ℝ} (hκ : 0 < κ) :
    ∀ n : ℕ, ∀ m ≤ n, ∀ t : ℝ, 0 < t → 0 ≤ (-1 : ℝ) ^ m * iteratedDeriv m (phi κ) t := by
  intro n
  induction n with
  | zero =>
    intro m hm t _
    rw [Nat.le_zero.mp hm]
    simp only [pow_zero, one_mul, iteratedDeriv_zero, phi]
    exact (Real.exp_pos _).le
  | succ n ih =>
    intro m hm t ht
    rcases Nat.lt_or_eq_of_le hm with hlt | rfl
    · exact ih m (Nat.lt_succ_iff.mp hlt) t ht
    · have hEq : Set.EqOn (deriv (phi κ)) (fun x => -(κ / 2) * (riesz 1 x * phi κ x)) (Set.Ioi 0) :=
        fun x hx => (phi_hasDerivAt κ hx).deriv
      rw [iteratedDeriv_succ', hEq.iteratedDeriv_of_isOpen isOpen_Ioi n ht, iteratedDeriv_const_mul_field]
      have hR := riesz_admissible (s := 1) one_pos
      have key : 0 ≤ (-1 : ℝ) ^ n * iteratedDeriv n (fun x => riesz 1 x * phi κ x) t :=
        mul_sign n (contDiffAt_of_admissible hR ht n) (phi_contDiffAt κ ht)
          (fun i _ => hR.2.2 i t ht) (fun i hi => ih i hi t ht)
      have hk : (0 : ℝ) ≤ κ / 2 := by positivity
      calc (0 : ℝ) ≤ κ / 2 * ((-1 : ℝ) ^ n * iteratedDeriv n (fun x => riesz 1 x * phi κ x) t) :=
            mul_nonneg hk key
        _ = (-1 : ℝ) ^ (n + 1) * (-(κ / 2) * iteratedDeriv n (fun x => riesz 1 x * phi κ x) t) := by
            ring

/-- **(E).** `exp(-κ √t)` is admissible for `κ > 0`. -/
theorem phi_admissible {κ : ℝ} (hκ : 0 < κ) : AdmissiblePotential (phi κ) :=
  ⟨fun _ hx => (phi_contDiffAt κ hx).contDiffWithinAt, fun _ _ => (Real.exp_pos _).le,
    fun r t ht => phi_sign hκ r r le_rfl t ht⟩

lemma g_eqOn (κ : ℝ) : Set.EqOn (riesz 1 * phi κ) (g κ) (Set.Ioi 0) := by
  intro t ht
  simp only [Pi.mul_apply]
  rw [riesz_one_eq ht]
  simp only [phi, g]
  ring

/-- **H2.** The Yukawa / Debye–Hückel potential is admissible for `κ > 0`. -/
theorem yukawa_admissible {κ : ℝ} (hκ : 0 < κ) : AdmissiblePotential (g κ) :=
  admissible_congr (admissible_mul (riesz_admissible (s := 1) one_pos) (phi_admissible hκ)) (g_eqOn κ)

/-- **H2 corollary.** The triangular lattice minimises the Yukawa energy among locally finite planar configurations
of density one (classical, energies in `[0, ∞]`). -/
theorem triangular_yukawa_optimal {κ : ℝ} (hκ : 0 < κ) (C : Set Plane) (hC : LocallyFinite C)
    (hdens : DensityOne C) : latticeEnergy (g κ) ≤ energy (g κ) C :=
  (universal_energy_minimum (g κ) C (yukawa_admissible hκ) hC hdens).1

/-- **Negative control.** `c_κ` is negative at `t = π`. -/
theorem c_neg_at_pi (κ : ℝ) : c κ Real.pi < 0 := by
  simp only [c, Real.cos_pi]
  have := Real.exp_pos (-κ * Real.sqrt Real.pi)
  linarith

/-- **Negative control.** `exp(-κ √t) cos t` is not admissible. -/
theorem c_not_admissible (κ : ℝ) : ¬ AdmissiblePotential (c κ) := by
  intro H
  have := H.2.1 Real.pi Real.pi_pos
  linarith [c_neg_at_pi κ]

lemma riesz_three_eq {t : ℝ} (ht : 0 < t) : riesz 3 t = ((Real.sqrt t) ^ 3)⁻¹ := by
  simp only [riesz]
  rw [Real.sqrt_eq_rpow, ← Real.rpow_natCast, ← Real.rpow_mul ht.le, ← Real.rpow_neg ht.le]
  norm_num

/-- Pointwise bound `g_κ(t) ≤ (2/κ²) t^{-3/2}` from `exp x ≥ x²/2`. -/
lemma g_le {κ : ℝ} (hκ : 0 < κ) {t : ℝ} (ht : 0 < t) : g κ t ≤ 2 / κ ^ 2 * riesz 3 t := by
  rw [riesz_three_eq ht]
  simp only [g]
  have hs0 : 0 < Real.sqrt t := Real.sqrt_pos.mpr ht
  set s := Real.sqrt t with hs
  have hx : 0 ≤ κ * s := by positivity
  have hq := Real.quadratic_le_exp_of_nonneg hx
  have h1 : (κ * s) ^ 2 / 2 ≤ Real.exp (κ * s) := by nlinarith
  have hpos : 0 < (κ * s) ^ 2 / 2 := by positivity
  have h2 : (Real.exp (κ * s))⁻¹ ≤ ((κ * s) ^ 2 / 2)⁻¹ := inv_anti₀ hpos h1
  rw [neg_mul, Real.exp_neg]
  calc (Real.exp (κ * s))⁻¹ / s ≤ ((κ * s) ^ 2 / 2)⁻¹ / s := div_le_div_of_nonneg_right h2 hs0.le
    _ = 2 / κ ^ 2 * (s ^ 3)⁻¹ := by field_simp

/-- **H2b.** The triangular-lattice Yukawa energy is finite. -/
theorem latticeEnergy_yukawa_lt_top {κ : ℝ} (hκ : 0 < κ) : latticeEnergy (g κ) < ⊤ := by
  have hR := latticeEnergy_riesz_lt_top (s := 3) (by norm_num)
  have hle : latticeEnergy (g κ) ≤ ENNReal.ofReal (2 / κ ^ 2) * latticeEnergy (riesz 3) := by
    unfold latticeEnergy
    rw [← ENNReal.tsum_mul_left]
    refine ENNReal.tsum_le_tsum fun a => ?_
    have hpos : 0 < ‖a.val‖ ^ 2 := by
      have := a.2.2
      positivity
    rw [← ENNReal.ofReal_mul (by positivity)]
    exact ENNReal.ofReal_le_ofReal (g_le hκ hpos)
  exact lt_of_le_of_lt hle (ENNReal.mul_lt_top ENNReal.ofReal_lt_top hR)

end AutoresearchYukawa

#print axioms AutoresearchYukawa.mul_sign
#print axioms AutoresearchYukawa.admissible_mul
#print axioms AutoresearchYukawa.admissible_congr
#print axioms AutoresearchYukawa.phi_admissible
#print axioms AutoresearchYukawa.yukawa_admissible
#print axioms AutoresearchYukawa.triangular_yukawa_optimal
#print axioms AutoresearchYukawa.c_not_admissible
#print axioms AutoresearchYukawa.latticeEnergy_yukawa_lt_top
