import Triangular.AnyDensity

/-!
# D3: universal optimality in the sense of Cohn–Kumar–Miller–Radchenko–Viazovska, and non-uniqueness

`UniversallyOptimal ρ C` transcribes Definition 1.3 of CKMRV (Ann. Math. 196, 2022) in upstream's notions of
density and lower energy: `C` has density `ρ` and minimises the `g`-energy among all locally finite density-`ρ`
configurations, for every admissible (smooth, completely monotone) `g` of squared distance.

* `triangular_universally_optimal`: `ρ^{-1/2} A` is universally optimal for every `ρ > 0`
  (conditional on upstream's `universal_energy_minimum`).
* `vacancy_energy`: the lattice with one point removed, `A \ {0}`, has the same energy for every admissible `g`.
* `vacancy_not_isometric_image`: `A \ {0}` is not an isometric image of `A`.
* `universal_optimum_not_unique`: so universal optima are not unique up to isometry among all configurations. This is
  the remark after CKMRV Theorem 1.4 ("removing a single particle changes neither the density nor the energy"), and it
  shows that "the minimiser is the triangular lattice" is false in this formulation; only the minimum *value* is
  determined.
-/

namespace TriangularUniversalOptimality

open OAI.AtomicTriangular TriangularDensity Filter Topology Set
open scoped Pointwise

/-- CKMRV Definition 1.3, in upstream's density and lower-energy notions. -/
def UniversallyOptimal (ρ : ℝ) (C : Set Plane) : Prop :=
  LocallyFinite C ∧ DensityRho ρ C ∧
    ∀ g : ℝ → ℝ, AdmissiblePotential g → ∀ C' : Set Plane, LocallyFinite C' → DensityRho ρ C' →
      energy g C ≤ energy g C'

/-- **Universal optimality of the triangular lattice at every density** (conditional on upstream). -/
theorem triangular_universally_optimal {ρ : ℝ} (hρ : 0 < ρ) :
    UniversallyOptimal ρ ((Real.sqrt ρ)⁻¹ • A) := by
  refine ⟨locallyFinite_smul (inv_pos.2 (Real.sqrt_pos.2 hρ)) A_lf, scaled_density hρ, ?_⟩
  intro g hg C' hC' hd
  exact (triangular_optimal_any_density g hg hρ).2.2 C' hC' hd

/-! ## The vacancy configuration -/

/-- The triangular lattice with the point at the origin removed. -/
def vacancy : Set Plane := A \ {0}

lemma zero_mem_A : (0 : Plane) ∈ A := ⟨(0, 0), by simp [triangularPoint]⟩

lemma vacancy_lf : LocallyFinite vacancy := by
  intro R
  exact (A_lf R).subset (Set.inter_subset_inter_left _ Set.diff_subset)

lemma diskPoints_vacancy (R : ℝ) : diskPoints vacancy R = (diskPoints A R).erase 0 := by
  unfold diskPoints OAI.TriangularUniversal.diskPoints
  rw [dif_pos (vacancy_lf R), dif_pos (A_lf R)]
  ext x
  simp only [Set.Finite.mem_toFinset, Finset.mem_erase, vacancy, Set.mem_inter_iff, Set.mem_diff,
    Set.mem_singleton_iff]
  tauto

lemma zero_mem_diskPoints {R : ℝ} (hR : 0 ≤ R) : (0 : Plane) ∈ diskPoints A R := by
  unfold diskPoints OAI.TriangularUniversal.diskPoints
  rw [dif_pos (A_lf R)]
  simp only [Set.Finite.mem_toFinset]
  exact ⟨zero_mem_A, Metric.mem_closedBall_self hR⟩

lemma diskCount_vacancy {R : ℝ} (hR : 0 ≤ R) : diskCount vacancy R = diskCount A R - 1 := by
  unfold diskCount OAI.TriangularUniversal.diskCount
  rw [show OAI.TriangularUniversal.diskPoints vacancy R = diskPoints vacancy R from rfl, diskPoints_vacancy,
    Finset.card_erase_of_mem (zero_mem_diskPoints hR)]
  rfl

lemma one_le_diskCount {R : ℝ} (hR : 0 ≤ R) : 1 ≤ diskCount A R :=
  Finset.card_pos.2 ⟨0, zero_mem_diskPoints hR⟩

lemma tendsto_inv_area : Tendsto (fun R : ℝ => 1 / (Real.pi * R ^ 2)) atTop (𝓝 0) := by
  have h : Tendsto (fun R : ℝ => Real.pi * R ^ 2) atTop atTop :=
    (tendsto_pow_atTop two_ne_zero).const_mul_atTop Real.pi_pos
  simpa [one_div] using h.inv_tendsto_atTop

lemma vacancy_density : DensityOne vacancy := by
  have h := A_d1.sub tendsto_inv_area
  rw [sub_zero] at h
  unfold DensityOne OAI.TriangularUniversal.DensityOne
  refine h.congr' ?_
  filter_upwards [eventually_ge_atTop (0 : ℝ)] with R hR
  rw [show OAI.TriangularUniversal.diskCount vacancy R = diskCount vacancy R from rfl, diskCount_vacancy hR,
    Nat.cast_sub (one_le_diskCount hR)]
  show (diskCount A R : ℝ) / (Real.pi * R ^ 2) - 1 / (Real.pi * R ^ 2) =
    ((diskCount A R : ℝ) - ((1 : ℕ) : ℝ)) / (Real.pi * R ^ 2)
  rw [Nat.cast_one, sub_div]

lemma count_tendsto : Tendsto (fun R : ℝ => (diskCount A R : ℝ)) atTop atTop := by
  have hg : Tendsto (fun R : ℝ => Real.pi * R ^ 2) atTop atTop :=
    (tendsto_pow_atTop two_ne_zero).const_mul_atTop Real.pi_pos
  have h := (show DensityOne A from A_d1).pos_mul_atTop one_pos hg
  refine h.congr' ?_
  filter_upwards [eventually_gt_atTop (0 : ℝ)] with R hR
  have : Real.pi * R ^ 2 ≠ 0 := by positivity
  exact div_mul_cancel₀ _ this

/-- The correction factor `N / (N - 1)`. -/
noncomputable def corr (R : ℝ) : ENNReal :=
  ENNReal.ofReal ((diskCount A R : ℝ) / ((diskCount A R : ℝ) - 1))

lemma corr_tendsto : Tendsto corr atTop (𝓝 1) := by
  have h1 : Tendsto (fun R : ℝ => (diskCount A R : ℝ) + (-1)) atTop atTop :=
    tendsto_atTop_add_const_right _ _ count_tendsto
  have h2 : Tendsto (fun R : ℝ => 1 + ((diskCount A R : ℝ) + (-1))⁻¹) atTop (𝓝 (1 + 0)) :=
    tendsto_const_nhds.add h1.inv_tendsto_atTop
  rw [add_zero] at h2
  have h3 : Tendsto (fun R : ℝ => (diskCount A R : ℝ) / ((diskCount A R : ℝ) - 1)) atTop (𝓝 1) := by
    refine h2.congr' ?_
    filter_upwards [count_tendsto.eventually_ge_atTop 2] with R hR
    have hne : (diskCount A R : ℝ) - 1 ≠ 0 := by linarith
    rw [← sub_eq_add_neg]
    field_simp
    ring
  have := ENNReal.tendsto_ofReal h3
  rwa [ENNReal.ofReal_one] at this

lemma pair_sum_le (g : ℝ → ℝ) (R : ℝ) :
    ∑ x ∈ diskPoints vacancy R, ∑ y ∈ (diskPoints vacancy R).erase x, ENNReal.ofReal (g (‖x - y‖ ^ 2)) ≤
      ∑ x ∈ diskPoints A R, ∑ y ∈ (diskPoints A R).erase x, ENNReal.ofReal (g (‖x - y‖ ^ 2)) := by
  rw [diskPoints_vacancy]
  calc ∑ x ∈ (diskPoints A R).erase 0, ∑ y ∈ ((diskPoints A R).erase 0).erase x, ENNReal.ofReal (g (‖x - y‖ ^ 2))
      ≤ ∑ x ∈ (diskPoints A R).erase 0, ∑ y ∈ (diskPoints A R).erase x, ENNReal.ofReal (g (‖x - y‖ ^ 2)) :=
        Finset.sum_le_sum fun x _ =>
          Finset.sum_le_sum_of_subset (Finset.erase_subset_erase x (Finset.erase_subset 0 _))
    _ ≤ ∑ x ∈ diskPoints A R, ∑ y ∈ (diskPoints A R).erase x, ENNReal.ofReal (g (‖x - y‖ ^ 2)) :=
        Finset.sum_le_sum_of_subset (Finset.erase_subset 0 _)

lemma coeff_eq {N : ℕ} (hN : 2 ≤ N) :
    (((N - 1 : ℕ) : ENNReal))⁻¹ = ENNReal.ofReal ((N : ℝ) / ((N : ℝ) - 1)) * ((N : ENNReal))⁻¹ := by
  have hN1 : (0 : ℝ) < (N : ℝ) - 1 := by
    have : (2 : ℝ) ≤ N := by exact_mod_cast hN
    linarith
  have hN0 : (0 : ℝ) < (N : ℝ) := by linarith
  rw [show ((N - 1 : ℕ) : ENNReal) = ENNReal.ofReal ((N : ℝ) - 1) by
        rw [← ENNReal.ofReal_natCast, Nat.cast_sub (by omega : 1 ≤ N), Nat.cast_one],
      show (N : ENNReal) = ENNReal.ofReal (N : ℝ) from (ENNReal.ofReal_natCast N).symm,
      ← ENNReal.ofReal_inv_of_pos hN1, ← ENNReal.ofReal_inv_of_pos hN0,
      ← ENNReal.ofReal_mul (div_nonneg hN0.le hN1.le)]
  congr 1
  field_simp

lemma diskEnergy_vacancy_le (g : ℝ → ℝ) :
    ∀ᶠ R in atTop, diskEnergy g vacancy R ≤ corr R * diskEnergy g A R := by
  filter_upwards [eventually_ge_atTop (0 : ℝ), count_tendsto.eventually_ge_atTop 2] with R hR hN
  have hN' : 2 ≤ diskCount A R := by exact_mod_cast hN
  unfold diskEnergy OAI.TriangularUniversal.diskEnergy
  rw [show OAI.TriangularUniversal.diskCount vacancy R = diskCount vacancy R from rfl, diskCount_vacancy hR,
    show OAI.TriangularUniversal.diskPoints vacancy R = diskPoints vacancy R from rfl,
    show OAI.TriangularUniversal.diskPoints A R = diskPoints A R from rfl,
    show OAI.TriangularUniversal.diskCount A R = diskCount A R from rfl, coeff_eq hN', mul_assoc]
  unfold corr
  exact mul_le_mul_left' (mul_le_mul_left' (pair_sum_le g R) _) _

/-- **The vacancy configuration is also a minimiser**, for every admissible `g`. -/
theorem vacancy_energy (g : ℝ → ℝ) (hg : AdmissiblePotential g) : energy g vacancy = latticeEnergy g := by
  apply le_antisymm
  · have hA := (universal_energy_minimum g A hg A_lf A_d1).2
    have hc := corr_tendsto
    calc energy g vacancy = liminf (diskEnergy g vacancy) atTop := rfl
      _ ≤ liminf (corr * diskEnergy g A) atTop := liminf_le_liminf (diskEnergy_vacancy_le g)
      _ ≤ limsup corr atTop * liminf (diskEnergy g A) atTop := by
          apply ENNReal.liminf_mul_le <;> left <;> rw [hc.limsup_eq] <;> simp
      _ = latticeEnergy g := by
          rw [hc.limsup_eq, one_mul, hA]
          rfl
  · exact (universal_energy_minimum g vacancy hg vacancy_lf vacancy_density).1

/-! ## The vacancy configuration is not an isometric copy of the lattice -/

lemma triangularPoint_comb (x y : ℤ × ℤ) :
    triangularPoint (2 * x.1 - y.1, 2 * x.2 - y.2) = (2 : ℝ) • triangularPoint x - triangularPoint y := by
  unfold triangularPoint
  ext i
  fin_cases i <;> simp [EuclideanSpace.single_apply] <;> ring

lemma A_comb {a b : Plane} (ha : a ∈ A) (hb : b ∈ A) : (2 : ℝ) • a - b ∈ A := by
  obtain ⟨x, rfl⟩ := ha
  obtain ⟨y, rfl⟩ := hb
  exact ⟨_, triangularPoint_comb x y⟩

theorem vacancy_not_isometric_image : ¬ ∃ f : Plane → Plane, Isometry f ∧ f '' A = vacancy := by
  rintro ⟨f, hf, hfA⟩
  set φ := hf.affineIsometryOfStrictConvexSpace
  have hφ : ∀ p, φ p = f p := fun p => rfl
  have key : ∀ a b : Plane, f ((2 : ℝ) • a - b) = (2 : ℝ) • f a - f b := by
    intro a b
    have h := φ.toAffineMap.map_vadd a (a - b)
    have h2 := φ.toAffineMap.linearMap_vsub a b
    simp only [vadd_eq_add, vsub_eq_sub, AffineIsometry.coe_toAffineMap, hφ] at h h2
    rw [show (2 : ℝ) • a - b = (a - b) + a by module, h, h2]
    module
  have hp : triangularPoint (1, 0) ∈ vacancy := by
    refine ⟨⟨(1, 0), rfl⟩, ?_⟩
    intro h0
    have := TriangularRiesz.norm_sq_triangularPoint 1 0
    simp only [Set.mem_singleton_iff] at h0
    rw [h0, norm_zero] at this
    have hb := TriangularRiesz.b_pos
    norm_num at this
    exact absurd this (by positivity)
  have hq : triangularPoint (2, 0) ∈ vacancy := by
    refine ⟨⟨(2, 0), rfl⟩, ?_⟩
    intro h0
    have := TriangularRiesz.norm_sq_triangularPoint 2 0
    simp only [Set.mem_singleton_iff] at h0
    rw [h0, norm_zero] at this
    have hb := TriangularRiesz.b_pos
    norm_num at this
    exact absurd this (by positivity)
  rw [← hfA] at hp hq
  obtain ⟨a, ha, hfa⟩ := hp
  obtain ⟨b, hb, hfb⟩ := hq
  have h0 : f ((2 : ℝ) • a - b) = 0 := by
    rw [key, hfa, hfb, ← triangularPoint_comb]
    simp [triangularPoint]
  have hmem : (0 : Plane) ∈ f '' A := ⟨_, A_comb ha hb, h0⟩
  rw [hfA] at hmem
  exact hmem.2 rfl

/-- `A \ {0}` is universally optimal at density one. -/
theorem vacancy_universally_optimal : UniversallyOptimal 1 vacancy := by
  refine ⟨vacancy_lf, vacancy_density, ?_⟩
  intro g hg C' hC' hd
  rw [vacancy_energy g hg]
  exact (universal_energy_minimum g C' hg hC' hd).1

/-- **Non-uniqueness.** There is a universal optimum at density one that is not an isometric copy of the triangular
lattice: the minimiser is not determined, only the minimum value. -/
theorem universal_optimum_not_unique :
    ∃ C : Set Plane, UniversallyOptimal 1 C ∧ ¬ ∃ f : Plane → Plane, Isometry f ∧ f '' A = C :=
  ⟨vacancy, vacancy_universally_optimal, vacancy_not_isometric_image⟩

end TriangularUniversalOptimality
