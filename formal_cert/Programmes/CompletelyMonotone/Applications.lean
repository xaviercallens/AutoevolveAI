import Programmes.CompletelyMonotone.Corollaries

/-!
# Programme P3, WORK2: applications of the completely monotone / Bernstein library

Part 1 (`H1_*`, `H2_*`, `H3_*`): the original autoresearch admissibility theorems (H1 dipolar, H2 Yukawa, H3L
Keldysh), restated with the *exact original statement* (conclusion `AdmissiblePotential`) and re-proved from the
library only. Hypotheses are the original ones or weaker.

Part 2: new potentials that follow from the library in a few lines.
* `screenedDipolar_cm`: Yukawa-screened bilayer exciton `2 (g_κ(t) - g_κ(t + d²))`, `κ ≥ 0`.
* `yukawaSpectrum_cm`: continuous Yukawa mixture `∫_{κ>0} m(κ) e^{-κ r}/r dκ` with a nonnegative spectral density.
* `secondDiff_cm`: `f(t) - 2 f(t + c) + f(t + 2 c)` is completely monotone (equally spaced in `t = r²`, NOT equally
  spaced layers).

Part 3 (negative result): the CHARGE-quadrupole combination `t^{-1/2} - 2 (t + c)^{-1/2} + (t + 4 c)^{-1/2}` (the field of
one `+1, -2, +1` quadrupole in equally spaced layers on a single test charge) is NOT completely monotone
(`quadrupole_not_cm`). It is NOT the exciton-exciton interaction.

Part 4: the exciton-exciton interaction of two aligned `+1, -2, +1` quadrupoles, `2 (3 f(t) - 4 f(t+c) + f(t+4c))`, IS
completely monotone for every completely monotone pair potential `f` (`quadrupolarPair_cm`).

Physical corollaries (triangular optimality) are conditional on upstream `OAI.AtomicTriangular.universal_energy_minimum`
(openai/math, AI-generated, not peer reviewed).
-/

namespace ProgCM.Applications

open Set Filter Topology MeasureTheory IsCompletelyMonotoneOn
open OAI.AtomicTriangular (AdmissiblePotential)

/-! ### Part 1: the original theorems, re-derived -/

/-- **H2** (original statement of `AutoresearchYukawa.yukawa_admissible`). -/
theorem H2_yukawa_admissible {κ : ℝ} (hκ : 0 < κ) : AdmissiblePotential (AutoresearchYukawa.g κ) :=
  (((riesz_cm zero_le_one).mul (phi_cm hκ.le)).congr (AutoresearchYukawa.g_eqOn κ)).admissible

/-- **H1** (statement of `AutoresearchDipolar.dipolar_admissible_all`; the original `dipolar_admissible` needed `0 < d`). -/
theorem H1_dipolar_admissible (d : ℝ) : AdmissiblePotential (AutoresearchDipolar.g d) :=
  ((((rpow_neg (by norm_num : (0 : ℝ) ≤ 1 / 2)).sub_comp_add_const (sq_nonneg d)).const_mul
    zero_le_two).congr' fun _ _ => rfl).admissible

/-- **H3L** (original statement of `AutoresearchKeldysh.keldysh_admissible`). -/
theorem H3_keldysh_admissible {r0 : ℝ} (hr0 : 0 < r0) : AdmissiblePotential (AutoresearchKeldysh.keldysh r0) :=
  (keldysh_cm hr0).admissible

/-! ### Part 2: new potentials -/

/-- Yukawa-screened bilayer exciton: `2 (e^{-κ r}/r - e^{-κ √(r²+d²)}/√(r²+d²))` in `t = r²`. -/
noncomputable def screenedDipolar (κ d : ℝ) : ℝ → ℝ := fun t =>
  2 * (AutoresearchYukawa.g κ t - AutoresearchYukawa.g κ (t + d ^ 2))

/-- The screened bilayer exciton potential is completely monotone (`κ ≥ 0`, every `d`). -/
theorem screenedDipolar_cm {κ : ℝ} (hκ : 0 ≤ κ) (d : ℝ) : IsCompletelyMonotoneOn (screenedDipolar κ d) :=
  ((yukawa_cm hκ).sub_comp_add_const (sq_nonneg d)).const_mul zero_le_two

/-- Triangular optimality for the screened bilayer exciton (conditional on upstream). -/
theorem triangular_screenedDipolar_optimal {κ : ℝ} (hκ : 0 ≤ κ) (d : ℝ) (C : Set OAI.AtomicTriangular.Plane)
    (hC : OAI.AtomicTriangular.LocallyFinite C) (hd : OAI.AtomicTriangular.DensityOne C) :
    OAI.AtomicTriangular.latticeEnergy (screenedDipolar κ d) ≤ OAI.AtomicTriangular.energy (screenedDipolar κ d) C :=
  triangular_optimal (screenedDipolar_cm hκ d) C hC hd

/-- Continuous Yukawa mixture with spectral density `m` on `κ > 0`: `∫_{κ>0} m(κ) e^{-κ r}/r dκ` in `t = r²`. -/
noncomputable def yukawaSpectrum (m : ℝ → ℝ) (t : ℝ) : ℝ :=
  ∫ κ in Ioi (0 : ℝ), m κ * AutoresearchYukawa.g κ t

/-- **Yukawa mixtures with a nonnegative spectral density are completely monotone**, provided
`e^{-cκ} m(κ)` is integrable on `(0, ∞)` for every `c > 0`. Proof: `t^{-1/2} · (Laplace(m) ∘ √)`. -/
theorem yukawaSpectrum_cm {m : ℝ → ℝ} (hm : Measurable m) (hm0 : ∀ κ, 0 < κ → 0 ≤ m κ)
    (hint : ∀ c : ℝ, 0 < c → IntegrableOn (fun κ => Real.exp (-(c * κ)) * m κ) (Ioi 0)) :
    IsCompletelyMonotoneOn (yukawaSpectrum m) := by
  have hL : IsCompletelyMonotoneOn
      (fun s => ∫ κ, Real.exp (-(s * id κ)) * m κ ∂(volume.restrict (Ioi (0 : ℝ)))) :=
    laplace measurable_id hm ((ae_restrict_iff' measurableSet_Ioi).mpr (Eventually.of_forall fun κ hκ => le_of_lt hκ))
      ((ae_restrict_iff' measurableSet_Ioi).mpr (Eventually.of_forall hm0)) hint
  refine ((riesz_cm zero_le_one).mul hL.comp_sqrt).congr' fun t ht => ?_
  simp only [Pi.mul_apply, yukawaSpectrum, AutoresearchYukawa.riesz_one_eq ht]
  rw [← integral_const_mul]
  refine setIntegral_congr_fun measurableSet_Ioi fun κ _ => ?_
  simp only [AutoresearchYukawa.g, id]
  rw [show -κ * Real.sqrt t = -(Real.sqrt t * κ) by ring]
  ring

/-- Triangular optimality for a Yukawa mixture with a nonnegative spectral density (conditional on upstream). -/
theorem triangular_yukawaSpectrum_optimal {m : ℝ → ℝ} (hm : Measurable m) (hm0 : ∀ κ, 0 < κ → 0 ≤ m κ)
    (hint : ∀ c : ℝ, 0 < c → IntegrableOn (fun κ => Real.exp (-(c * κ)) * m κ) (Ioi 0))
    (C : Set OAI.AtomicTriangular.Plane) (hC : OAI.AtomicTriangular.LocallyFinite C)
    (hd : OAI.AtomicTriangular.DensityOne C) :
    OAI.AtomicTriangular.latticeEnergy (yukawaSpectrum m) ≤ OAI.AtomicTriangular.energy (yukawaSpectrum m) C :=
  triangular_optimal (yukawaSpectrum_cm hm hm0 hint) C hC hd

/-- Instance: the exponential spectral density `m(κ) = e^{-κ}` (the hypothesis of `yukawaSpectrum_cm` holds). -/
theorem yukawaExpSpectrum_cm : IsCompletelyMonotoneOn (yukawaSpectrum fun κ => Real.exp (-κ)) := by
  refine yukawaSpectrum_cm (by fun_prop) (fun κ _ => (Real.exp_pos _).le) fun c hc => ?_
  have h : IntegrableOn (fun κ : ℝ => Real.exp (-(c + 1) * κ)) (Ioi 0) :=
    integrableOn_exp_mul_Ioi (by linarith) 0
  refine h.congr_fun (fun κ _ => ?_) measurableSet_Ioi
  simp only []
  rw [← Real.exp_add]
  congr 1
  ring

/-- Second difference in `t = r²` (shifts `0, c, 2c`): completely monotone for completely monotone `f`.
This is NOT the equally spaced-layer quadrupole (shifts `0, d², 4d²`); see Part 3 and Part 4 (`quadrupolarPair_cm`). -/
theorem secondDiff_cm {f : ℝ → ℝ} (hf : IsCompletelyMonotoneOn f) {c : ℝ} (hc : 0 ≤ c) :
    IsCompletelyMonotoneOn (fun t => f t - 2 * f (t + c) + f (t + 2 * c)) :=
  ((hf.sub_comp_add_const hc).sub_comp_add_const hc).congr' fun t _ => by
    show f t - f (t + c) - (f (t + c) - f (t + c + c)) = _
    rw [show t + c + c = t + 2 * c by ring]
    ring

/-! ### Part 3: the charge-quadrupole combination (one quadrupole's field on a test charge) is not completely monotone -/

/-- The charges `+1, -2, +1` in layers `0, d, 2d` give shifts `0, d², 4d²` in `t = r²`; unit case `d = 1`. -/
noncomputable def quadrupole (t : ℝ) : ℝ := t ^ (-(1 / 2 : ℝ)) - 2 * (t + 1) ^ (-(1 / 2 : ℝ)) + (t + 4) ^ (-(1 / 2 : ℝ))

theorem quadrupole_neg_at_three : quadrupole 3 < 0 := by
  have e : ∀ x : ℝ, 0 < x → x ^ (-(1 / 2 : ℝ)) = (Real.sqrt x)⁻¹ := fun x hx => by
    rw [Real.rpow_neg hx.le, ← Real.sqrt_eq_rpow]
  unfold quadrupole
  rw [e 3 (by norm_num), e (3 + 1) (by norm_num), e (3 + 4) (by norm_num)]
  have h4 : Real.sqrt (3 + 1) = 2 := by
    rw [show (3 : ℝ) + 1 = 2 ^ 2 by norm_num]
    exact Real.sqrt_sq (by norm_num)
  have h3 : (17 / 10 : ℝ) < Real.sqrt 3 := Real.lt_sqrt_of_sq_lt (by norm_num)
  have h7 : (26 / 10 : ℝ) < Real.sqrt (3 + 4) := Real.lt_sqrt_of_sq_lt (by norm_num)
  have i3 : (Real.sqrt 3)⁻¹ < 10 / 17 := by
    rw [inv_lt_comm₀ (by linarith) (by norm_num)]
    simpa using h3
  have i7 : (Real.sqrt (3 + 4))⁻¹ < 10 / 26 := by
    rw [inv_lt_comm₀ (lt_trans (by norm_num) h7) (by norm_num)]
    simpa using h7
  rw [h4]
  norm_num at i3 i7 ⊢
  linarith

/-- **Negative result.** The (unit) charge-quadrupole combination is not completely monotone. -/
theorem quadrupole_not_cm : ¬ IsCompletelyMonotoneOn quadrupole := fun h => by
  have := h.nonneg (t := 3) (by norm_num)
  linarith [quadrupole_neg_at_three]

/-- The same combination at a general layer spacing: `c = d²` (shifts `0, c, 4c`). -/
noncomputable def quadrupoleC (c t : ℝ) : ℝ :=
  t ^ (-(1 / 2 : ℝ)) - 2 * (t + c) ^ (-(1 / 2 : ℝ)) + (t + 4 * c) ^ (-(1 / 2 : ℝ))

/-- **Negative result at every layer spacing** `c > 0`: reduced to `c = 1` by the scaling `t ↦ c t`
(`comp_affine`). -/
theorem quadrupoleC_not_cm {c : ℝ} (hc : 0 < c) : ¬ IsCompletelyMonotoneOn (quadrupoleC c) := fun h => by
  have h1 := (h.comp_affine hc (le_refl 0)).const_mul (Real.sqrt_nonneg c)
  refine quadrupole_not_cm (h1.congr' fun s hs => ?_)
  have hk : Real.sqrt c * c ^ (-(1 / 2 : ℝ)) = 1 := by
    rw [Real.sqrt_eq_rpow, ← Real.rpow_add hc]
    norm_num
  have e1 : (c * s + 0) ^ (-(1 / 2 : ℝ)) = c ^ (-(1 / 2 : ℝ)) * s ^ (-(1 / 2 : ℝ)) := by
    rw [add_zero, Real.mul_rpow hc.le hs.le]
  have e2 : (c * s + 0 + c) ^ (-(1 / 2 : ℝ)) = c ^ (-(1 / 2 : ℝ)) * (s + 1) ^ (-(1 / 2 : ℝ)) := by
    rw [show c * s + 0 + c = c * (s + 1) by ring, Real.mul_rpow hc.le (by linarith)]
  have e3 : (c * s + 0 + 4 * c) ^ (-(1 / 2 : ℝ)) = c ^ (-(1 / 2 : ℝ)) * (s + 4) ^ (-(1 / 2 : ℝ)) := by
    rw [show c * s + 0 + 4 * c = c * (s + 4) by ring, Real.mul_rpow hc.le (by linarith)]
  simp only [quadrupoleC, quadrupole, e1, e2, e3]
  linear_combination (s ^ (-(1 / 2 : ℝ)) - 2 * (s + 1) ^ (-(1 / 2 : ℝ)) + (s + 4) ^ (-(1 / 2 : ℝ))) * hk

/-! ### Part 4: the exciton-exciton interaction of two aligned quadrupoles IS completely monotone

Two aligned `+1, -2, +1` quadrupoles (layers `0, d, 2d`, in-plane distance `r`, `c = d²`, pair interaction `f(r² + Δz²)`)
interact by `Σ qᵢ qⱼ f(t + Δz²)`: `Δz = 0` contributes `1 + 4 + 1 = 6`, `|Δz| = d` contributes `4 · (-2) = -8`,
`|Δz| = 2d` contributes `2 · 1 = 2`, i.e. `2 (3 f(t) - 4 f(t + c) + f(t + 4 c))`. With `g = f - f(· + c)` this equals
`Δ_c g + Δ_{2c} g + Δ_{3c} g` (`Δ_a h = h - h(· + a)`), a sum of three completely monotone functions. (The charge
-quadrupole combination of Part 3 is a different object: one quadrupole's field on a single test charge.) -/

/-- Pair interaction of two aligned `+1, -2, +1` quadrupoles for a pair potential `f` (in `t = r²`, `c = d²`). -/
noncomputable def quadrupolarPair (f : ℝ → ℝ) (c t : ℝ) : ℝ := 2 * (3 * f t - 4 * f (t + c) + f (t + 4 * c))

/-- **Quadrupolar exciton-exciton interaction** is completely monotone for every completely monotone pair potential. -/
theorem quadrupolarPair_cm {f : ℝ → ℝ} (hf : IsCompletelyMonotoneOn f) {c : ℝ} (hc : 0 ≤ c) :
    IsCompletelyMonotoneOn (quadrupolarPair f c) := by
  have hg := hf.sub_comp_add_const hc
  have h1 := hg.sub_comp_add_const hc
  have h2 := hg.sub_comp_add_const (by linarith : (0 : ℝ) ≤ 2 * c)
  have h3 := hg.sub_comp_add_const (by linarith : (0 : ℝ) ≤ 3 * c)
  refine (((h1.add h2).add h3).const_mul zero_le_two).congr' fun t _ => ?_
  simp only [quadrupolarPair, Pi.add_apply]
  ring_nf

/-- Unscreened (Coulomb pair potential `t^{-1/2}`) quadrupolar exciton interaction, `c = d²`. -/
theorem quadrupolarCoulomb_cm (d : ℝ) :
    IsCompletelyMonotoneOn (quadrupolarPair (fun t => t ^ (-(1 / 2 : ℝ))) (d ^ 2)) :=
  quadrupolarPair_cm (rpow_neg (by norm_num : (0 : ℝ) ≤ 1 / 2)) (sq_nonneg d)

/-- Yukawa-screened quadrupolar exciton interaction (`κ ≥ 0`), `c = d²`. -/
theorem quadrupolarYukawa_cm {κ : ℝ} (hκ : 0 ≤ κ) (d : ℝ) :
    IsCompletelyMonotoneOn (quadrupolarPair (AutoresearchYukawa.g κ) (d ^ 2)) :=
  quadrupolarPair_cm (yukawa_cm hκ) (sq_nonneg d)

/-- Triangular optimality for the Coulomb quadrupolar interaction (conditional on upstream). -/
theorem triangular_quadrupolarCoulomb_optimal (d : ℝ) (C : Set OAI.AtomicTriangular.Plane)
    (hC : OAI.AtomicTriangular.LocallyFinite C) (hd : OAI.AtomicTriangular.DensityOne C) :
    OAI.AtomicTriangular.latticeEnergy (quadrupolarPair (fun t => t ^ (-(1 / 2 : ℝ))) (d ^ 2)) ≤
      OAI.AtomicTriangular.energy (quadrupolarPair (fun t => t ^ (-(1 / 2 : ℝ))) (d ^ 2)) C :=
  triangular_optimal (quadrupolarCoulomb_cm d) C hC hd

end ProgCM.Applications

#print axioms ProgCM.Applications.quadrupoleC_not_cm
#print axioms ProgCM.Applications.H2_yukawa_admissible
#print axioms ProgCM.Applications.H1_dipolar_admissible
#print axioms ProgCM.Applications.H3_keldysh_admissible
#print axioms ProgCM.Applications.screenedDipolar_cm
#print axioms ProgCM.Applications.triangular_screenedDipolar_optimal
#print axioms ProgCM.Applications.yukawaSpectrum_cm
#print axioms ProgCM.Applications.triangular_yukawaSpectrum_optimal
#print axioms ProgCM.Applications.yukawaExpSpectrum_cm
#print axioms ProgCM.Applications.secondDiff_cm
#print axioms ProgCM.Applications.quadrupole_neg_at_three
#print axioms ProgCM.Applications.quadrupole_not_cm
#print axioms ProgCM.Applications.quadrupolarPair_cm
#print axioms ProgCM.Applications.quadrupolarCoulomb_cm
#print axioms ProgCM.Applications.quadrupolarYukawa_cm
#print axioms ProgCM.Applications.triangular_quadrupolarCoulomb_optimal
