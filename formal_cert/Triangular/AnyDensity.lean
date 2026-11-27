import Triangular.Riesz
import Triangular.RieszFinite

/-!
# D2: universal optimality at every density

From upstream's density-one theorem `OAI.AtomicTriangular.universal_energy_minimum`: for every `ρ > 0`, every admissible
potential `h` and every locally finite configuration `C` of density `ρ`,
`Σ_{x ∈ A \ 0} h(‖x‖²/ρ) ≤ energy h C`, i.e. the triangular lattice rescaled to density `ρ` (`ρ^{-1/2} A`) is optimal.
Proof: `√ρ • C` has density one, `t ↦ h(t/ρ)` is admissible, and energies transform under scaling.
-/

namespace TriangularDensity

open OAI.AtomicTriangular Filter Topology Set
open scoped Pointwise

/-- `C` has density `ρ`. -/
def DensityRho (ρ : ℝ) (C : Set Plane) : Prop :=
  Tendsto (fun R : ℝ => (diskCount C R : ℝ) / (Real.pi * R ^ 2)) atTop (𝓝 ρ)

lemma iterate_deriv_comp_mul (f : ℝ → ℝ) (c : ℝ) :
    ∀ r : ℕ, deriv^[r] (fun t => f (c * t)) = fun t => c ^ r * deriv^[r] f (c * t)
  | 0 => by funext t; simp
  | r + 1 => by
    rw [Function.iterate_succ_apply', iterate_deriv_comp_mul f c r]
    funext t
    rw [deriv_const_mul_field']
    have h := deriv_comp_mul_left (𝕜 := ℝ) (f := deriv^[r] f) (c := c) (x := t)
    simp only [smul_eq_mul] at h
    show c ^ r * deriv (fun x => deriv^[r] f (c * x)) t = c ^ (r + 1) * deriv^[r + 1] f (c * t)
    rw [h, Function.iterate_succ_apply']
    ring

lemma admissible_comp_mul {g : ℝ → ℝ} (hg : AdmissiblePotential g) {c : ℝ} (hc : 0 < c) :
    AdmissiblePotential (fun t => g (c * t)) := by
  obtain ⟨h1, h2, h3⟩ := hg
  refine ⟨?_, ?_, ?_⟩
  · exact h1.comp (contDiff_const.mul contDiff_id).contDiffOn (fun t ht => mul_pos hc ht)
  · intro t ht
    exact h2 _ (mul_pos hc ht)
  · intro r t ht
    rw [iteratedDeriv_eq_iterate, iterate_deriv_comp_mul]
    have := h3 r (c * t) (mul_pos hc ht)
    rw [iteratedDeriv_eq_iterate] at this
    have hcr : 0 ≤ c ^ r := pow_nonneg hc.le r
    calc (0 : ℝ) ≤ c ^ r * ((-1) ^ r * deriv^[r] g (c * t)) := mul_nonneg hcr this
      _ = (-1) ^ r * (c ^ r * deriv^[r] g (c * t)) := by ring

/-! ## Scaling a configuration -/

lemma inter_ball_smul {c : ℝ} (hc : 0 < c) (C : Set Plane) (R : ℝ) :
    (c • C) ∩ Metric.closedBall (0 : Plane) R = (fun x => c • x) '' (C ∩ Metric.closedBall (0 : Plane) (R / c)) := by
  ext x
  simp only [Set.mem_inter_iff, Metric.mem_closedBall, dist_zero_right, Set.mem_image, Set.mem_smul_set]
  constructor
  · rintro ⟨⟨y, hy, rfl⟩, hn⟩
    refine ⟨y, ⟨hy, ?_⟩, rfl⟩
    rw [norm_smul, Real.norm_of_nonneg hc.le] at hn
    rw [le_div_iff₀ hc]; linarith
  · rintro ⟨y, ⟨hy, hn⟩, rfl⟩
    refine ⟨⟨y, hy, rfl⟩, ?_⟩
    rw [norm_smul, Real.norm_of_nonneg hc.le]
    rw [le_div_iff₀ hc] at hn; linarith

lemma locallyFinite_smul {c : ℝ} (hc : 0 < c) {C : Set Plane} (hC : LocallyFinite C) : LocallyFinite (c • C) := by
  intro R
  rw [inter_ball_smul hc]
  exact (hC (R / c)).image _

lemma smul_injective {c : ℝ} (hc : 0 < c) : Function.Injective (fun x : Plane => c • x) :=
  smul_right_injective _ hc.ne'

lemma diskPoints_smul {c : ℝ} (hc : 0 < c) {C : Set Plane} (hC : LocallyFinite C) (R : ℝ) :
    diskPoints (c • C) R = (diskPoints C (R / c)).image (fun x => c • x) := by
  unfold diskPoints OAI.TriangularUniversal.diskPoints
  rw [dif_pos (locallyFinite_smul hc hC R), dif_pos (hC (R / c))]
  ext x
  simp only [Set.Finite.mem_toFinset, Finset.mem_image]
  rw [inter_ball_smul hc]
  simp only [Set.mem_image]

lemma diskCount_smul {c : ℝ} (hc : 0 < c) {C : Set Plane} (hC : LocallyFinite C) (R : ℝ) :
    diskCount (c • C) R = diskCount C (R / c) := by
  unfold diskCount OAI.TriangularUniversal.diskCount
  rw [show OAI.TriangularUniversal.diskPoints (c • C) R = diskPoints (c • C) R from rfl, diskPoints_smul hc hC,
    Finset.card_image_of_injective _ (smul_injective hc)]

lemma density_smul {ρ : ℝ} (hρ : 0 < ρ) {C : Set Plane} (hC : LocallyFinite C) (hd : DensityRho ρ C) :
    DensityOne (Real.sqrt ρ • C) := by
  have hs : 0 < Real.sqrt ρ := Real.sqrt_pos.2 hρ
  have hsq : Real.sqrt ρ ^ 2 = ρ := Real.sq_sqrt hρ.le
  have ht : Tendsto (fun R : ℝ => R / Real.sqrt ρ) atTop atTop := tendsto_id.atTop_div_const hs
  have h1 := (hd.comp ht).const_mul ρ⁻¹
  rw [inv_mul_cancel₀ hρ.ne'] at h1
  unfold DensityOne OAI.TriangularUniversal.DensityOne
  refine h1.congr' ?_
  filter_upwards [eventually_gt_atTop (0 : ℝ)] with R hR
  simp only [Function.comp_apply]
  rw [show OAI.TriangularUniversal.diskCount (Real.sqrt ρ • C) R = diskCount (Real.sqrt ρ • C) R from rfl,
    diskCount_smul hs hC]
  show ρ⁻¹ * ((diskCount C (R / Real.sqrt ρ) : ℝ) / (Real.pi * (R / Real.sqrt ρ) ^ 2)) =
    (diskCount C (R / Real.sqrt ρ) : ℝ) / (Real.pi * R ^ 2)
  rw [div_pow, hsq]
  field_simp

lemma diskEnergy_smul {c : ℝ} (hc : 0 < c) (g : ℝ → ℝ) {C : Set Plane} (hC : LocallyFinite C) (R : ℝ) :
    diskEnergy g (c • C) R = diskEnergy (fun t => g (c ^ 2 * t)) C (R / c) := by
  unfold diskEnergy OAI.TriangularUniversal.diskEnergy
  rw [show OAI.TriangularUniversal.diskPoints (c • C) R = diskPoints (c • C) R from rfl,
    show OAI.TriangularUniversal.diskCount (c • C) R = diskCount (c • C) R from rfl, diskCount_smul hc hC,
    diskPoints_smul hc hC]
  congr 1
  rw [Finset.sum_image (fun x _ y _ h => smul_injective hc h)]
  apply Finset.sum_congr rfl
  intro x _
  rw [← Finset.image_erase (smul_injective hc), Finset.sum_image (fun x _ y _ h => smul_injective hc h)]
  apply Finset.sum_congr rfl
  intro y _
  congr 2
  rw [← smul_sub, norm_smul, Real.norm_of_nonneg hc.le, mul_pow]

lemma liminf_comp_div {c : ℝ} (hc : 0 < c) (F : ℝ → ENNReal) :
    liminf (fun R => F (R / c)) atTop = liminf F atTop := by
  have hmap : map (fun R : ℝ => R / c) atTop = atTop := by
    have h1 := (OrderIso.mulLeft₀ c⁻¹ (inv_pos.2 hc)).map_atTop
    have h2 : ((OrderIso.mulLeft₀ c⁻¹ (inv_pos.2 hc)) : ℝ → ℝ) = fun R => R / c := by
      funext R
      exact (div_eq_inv_mul R c).symm
    rw [← h2]
    exact h1
  rw [show (fun R => F (R / c)) = F ∘ (fun R : ℝ => R / c) from rfl]
  unfold Filter.liminf
  rw [← Filter.map_map, hmap]

lemma energy_smul {c : ℝ} (hc : 0 < c) (g : ℝ → ℝ) {C : Set Plane} (hC : LocallyFinite C) :
    energy g (c • C) = energy (fun t => g (c ^ 2 * t)) C := by
  unfold energy OAI.TriangularUniversal.energy
  rw [show OAI.TriangularUniversal.diskEnergy g (c • C) = fun R => diskEnergy g (c • C) R from rfl]
  simp_rw [diskEnergy_smul hc g hC]
  exact liminf_comp_div hc (diskEnergy (fun t => g (c ^ 2 * t)) C)

/-- **D2.** Universal optimality at every density `ρ > 0`. -/
theorem universal_any_density (h : ℝ → ℝ) (hh : AdmissiblePotential h) {ρ : ℝ} (hρ : 0 < ρ) (C : Set Plane)
    (hC : LocallyFinite C) (hd : DensityRho ρ C) :
    latticeEnergy (fun t => h (ρ⁻¹ * t)) ≤ energy h C := by
  have hs : 0 < Real.sqrt ρ := Real.sqrt_pos.2 hρ
  have hg := admissible_comp_mul hh (inv_pos.2 hρ)
  have key := (universal_energy_minimum (fun t => h (ρ⁻¹ * t)) (Real.sqrt ρ • C) hg (locallyFinite_smul hs hC)
    (density_smul hρ hC hd)).1
  rw [energy_smul hs _ hC] at key
  have e : (fun t => (fun t => h (ρ⁻¹ * t)) (Real.sqrt ρ ^ 2 * t)) = h := by
    funext t
    simp only
    rw [Real.sq_sqrt hρ.le, ← mul_assoc, inv_mul_cancel₀ hρ.ne', one_mul]
  rw [e] at key
  exact key

/-- Riesz `s`-energy optimality of the rescaled triangular lattice at every density (D1 + D2); informative for `s > 2`
(for `s ≤ 2` the lattice side is `∞`). -/
theorem riesz_any_density {s : ℝ} (hs : 0 < s) {ρ : ℝ} (hρ : 0 < ρ) (C : Set Plane) (hC : LocallyFinite C)
    (hd : DensityRho ρ C) :
    latticeEnergy (fun t => TriangularRiesz.riesz s (ρ⁻¹ * t)) ≤ energy (TriangularRiesz.riesz s) C :=
  universal_any_density _ (TriangularRiesz.riesz_admissible hs) hρ C hC hd

/-! ## Sharpness, non-vacuity and a negative control

Contributed by the independent D2 verification run (`results/discovery/D2/verification.md`): the hypothesis `DensityRho ρ`
is satisfiable (by `ρ^{-1/2} A`), that configuration attains the bound, so `universal_any_density` is an optimality
statement; and without the `ρ⁻¹` rescaling the claim is false (density `1/4`, Riesz `s = 4`). -/

/-! ## Non-vacuity and sharpness: ρ^{-1/2} A has density ρ and attains the bound -/
lemma A_lf : LocallyFinite A := by
  rw [OAI.AtomicTriangular.A_eq_support]; exact OAI.TriangularUniversal.triangular_locallyFinite

lemma A_d1 : DensityOne A := by
  rw [OAI.AtomicTriangular.A_eq_support]; exact OAI.TriangularUniversal.triangular_densityOne

theorem scaled_density {ρ : ℝ} (hρ : 0 < ρ) : DensityRho ρ ((Real.sqrt ρ)⁻¹ • A) := by
  have hs : 0 < Real.sqrt ρ := Real.sqrt_pos.2 hρ
  have hc : 0 < (Real.sqrt ρ)⁻¹ := inv_pos.2 hs
  have hsq : Real.sqrt ρ ^ 2 = ρ := Real.sq_sqrt hρ.le
  have ht : Tendsto (fun R : ℝ => R / (Real.sqrt ρ)⁻¹) atTop atTop := tendsto_id.atTop_div_const hc
  have h1 := ((show DensityOne A from A_d1).comp ht).const_mul ρ
  rw [mul_one] at h1
  unfold DensityRho
  refine h1.congr' ?_
  filter_upwards [eventually_gt_atTop (0 : ℝ)] with R hR
  simp only [Function.comp_apply]
  rw [diskCount_smul hc A_lf]
  rw [div_inv_eq_mul, mul_pow, hsq]
  field_simp

theorem attained (h : ℝ → ℝ) (hh : AdmissiblePotential h) {ρ : ℝ} (hρ : 0 < ρ) :
    energy h ((Real.sqrt ρ)⁻¹ • A) = latticeEnergy (fun t => h (ρ⁻¹ * t)) := by
  have hs : 0 < Real.sqrt ρ := Real.sqrt_pos.2 hρ
  rw [energy_smul (inv_pos.2 hs) h A_lf, inv_pow, Real.sq_sqrt hρ.le]
  exact ((universal_energy_minimum _ A (admissible_comp_mul hh (inv_pos.2 hρ)) A_lf A_d1).2).symm


/-! ## Negative control: the UNscaled claim at density 1/4 is false (Riesz s = 4) -/
theorem unscaled_false :
    ¬ (∀ C : Set Plane, LocallyFinite C → DensityRho (1 / 4) C →
        latticeEnergy (TriangularRiesz.riesz 4) ≤ energy (TriangularRiesz.riesz 4) C) := by
  intro H
  have hρ : (0 : ℝ) < 1 / 4 := by norm_num
  have key := H _ (locallyFinite_smul (inv_pos.2 (Real.sqrt_pos.2 hρ)) A_lf) (scaled_density hρ)
  rw [attained _ (TriangularRiesz.riesz_admissible (by norm_num)) hρ] at key
  -- key : Σ ofReal(t^{-2}) ≤ Σ ofReal((4t)^{-2}); but (4t)^{-2} < t^{-2} termwise and the sum is finite
  have hfin := TriangularRiesz.latticeEnergy_riesz_lt_top (s := 4) (by norm_num)
  have hpt : (OAI.AtomicTriangular.triangularPoint (1, 0)) ∈ A ∧ OAI.AtomicTriangular.triangularPoint (1, 0) ≠ 0 := by
    refine ⟨⟨(1, 0), rfl⟩, ?_⟩
    intro h0
    have := TriangularRiesz.norm_sq_triangularPoint 1 0
    rw [h0, norm_zero] at this
    have hb := TriangularRiesz.b_pos
    norm_num at this
    exact absurd this (by positivity)
  have hle : ∀ a : {x : Plane // x ∈ A ∧ x ≠ 0},
      ENNReal.ofReal (TriangularRiesz.riesz 4 ((1 / 4 : ℝ)⁻¹ * ‖a.val‖ ^ 2)) ≤
        ENNReal.ofReal (TriangularRiesz.riesz 4 (‖a.val‖ ^ 2)) := by
    intro a
    apply ENNReal.ofReal_le_ofReal
    have hp : 0 < ‖a.val‖ ^ 2 := by have := norm_pos_iff.2 a.2.2; positivity
    unfold TriangularRiesz.riesz
    apply Real.rpow_le_rpow_of_nonpos hp (by nlinarith) (by norm_num)
  have hlt : ∀ a : {x : Plane // x ∈ A ∧ x ≠ 0},
      ENNReal.ofReal (TriangularRiesz.riesz 4 ((1 / 4 : ℝ)⁻¹ * ‖a.val‖ ^ 2)) <
        ENNReal.ofReal (TriangularRiesz.riesz 4 (‖a.val‖ ^ 2)) := by
    intro a
    have hp : 0 < ‖a.val‖ ^ 2 := by have := norm_pos_iff.2 a.2.2; positivity
    rw [ENNReal.ofReal_lt_ofReal_iff (by unfold TriangularRiesz.riesz; exact Real.rpow_pos_of_pos hp _)]
    unfold TriangularRiesz.riesz
    exact Real.rpow_lt_rpow_of_neg hp (by nlinarith) (by norm_num)
  have hfin2 : latticeEnergy (fun t => TriangularRiesz.riesz 4 ((1 / 4 : ℝ)⁻¹ * t)) ≠ ⊤ :=
    ne_top_of_le_ne_top hfin.ne (ENNReal.tsum_le_tsum hle)
  have strict := ENNReal.tsum_lt_tsum hfin2 hle (hlt ⟨_, hpt⟩)
  exact absurd key (not_le.2 strict)


/-- **D2, optimality form.** At every density `ρ > 0` the rescaled lattice `ρ^{-1/2} A` has density `ρ`, and its energy is
`≤` that of every locally finite density-`ρ` configuration. -/
theorem triangular_optimal_any_density (h : ℝ → ℝ) (hh : AdmissiblePotential h) {ρ : ℝ} (hρ : 0 < ρ) :
    LocallyFinite ((Real.sqrt ρ)⁻¹ • A) ∧ DensityRho ρ ((Real.sqrt ρ)⁻¹ • A) ∧
      ∀ C : Set Plane, LocallyFinite C → DensityRho ρ C → energy h ((Real.sqrt ρ)⁻¹ • A) ≤ energy h C :=
  ⟨locallyFinite_smul (inv_pos.2 (Real.sqrt_pos.2 hρ)) A_lf, scaled_density hρ, fun C hC hd => by
    rw [attained h hh hρ]; exact universal_any_density h hh hρ C hC hd⟩

end TriangularDensity
