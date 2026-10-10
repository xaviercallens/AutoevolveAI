import Triangular.Riesz

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

/-- Riesz `s`-energy optimality of the rescaled triangular lattice at every density (D1 + D2). -/
theorem riesz_any_density {s : ℝ} (hs : 0 < s) {ρ : ℝ} (hρ : 0 < ρ) (C : Set Plane) (hC : LocallyFinite C)
    (hd : DensityRho ρ C) :
    latticeEnergy (fun t => TriangularRiesz.riesz s (ρ⁻¹ * t)) ≤ energy (TriangularRiesz.riesz s) C :=
  universal_any_density _ (TriangularRiesz.riesz_admissible hs) hρ C hC hd

end TriangularDensity
