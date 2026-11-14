import Triangular.UniversalOptimality

/-!
# D4: open versus closed disks

Upstream counts points and pair energies in CLOSED disks `closedBall 0 R`. Here the same quantities are defined with
OPEN disks `ball 0 R`, and for every locally finite configuration they coincide:

* `densityOne_iff_open`: `DensityOne C ↔ DensityOneOpen C`;
* `energy_eq_openEnergy`: `energy g C = openEnergy g C` for every `g`;
* `universal_energy_minimum_open`: upstream's theorem holds verbatim with open disks.

Scope: this settles the open/closed question for upstream's observables only (centred disks, `N/(πR²)` density,
`liminf` energy in `[0, ∞]`); it says nothing about other window shapes, `limsup` energies or physical boundary
conditions. The identity is not definitional (pointwise counts differ at boundary radii), and it needs no
local-finiteness hypothesis at all: see `OpenDiskAny.lean` (from the independent verification run).

Human proof: local finiteness makes `C ∩ closedBall 0 R` finite, so the open-disk point set at radius `R` is the
closed-disk set at a slightly smaller radius, and the closed-disk set at `R` is the open-disk set at a slightly larger
radius. The disk-energy functions therefore take each other's values at radii within distance one, and their lower
limits coincide; the counts are squeezed between `N_closed (R - 1)` and `N_closed R`.
-/

namespace TriangularOpenDisk

open OAI.AtomicTriangular Filter Topology Set
open Classical

/-- Points of `C` in the open disk of radius `R`. -/
noncomputable def openDiskPoints (C : Set Plane) (R : ℝ) : Finset Plane :=
  if h : (C ∩ Metric.ball (0 : Plane) R).Finite then h.toFinset else ∅

noncomputable def openDiskCount (C : Set Plane) (R : ℝ) : ℕ := (openDiskPoints C R).card

/-- Centred density one, counted in open disks. -/
def DensityOneOpen (C : Set Plane) : Prop :=
  Tendsto (fun R : ℝ => (openDiskCount C R : ℝ) / (Real.pi * R ^ 2)) atTop (𝓝 1)

noncomputable def openDiskEnergy (g : ℝ → ℝ) (C : Set Plane) (R : ℝ) : ENNReal :=
  (openDiskCount C R : ENNReal)⁻¹ *
    ∑ x ∈ openDiskPoints C R, ∑ y ∈ (openDiskPoints C R).erase x, ENNReal.ofReal (g (‖x - y‖ ^ 2))

/-- Lower energy, counted in open disks. -/
noncomputable def openEnergy (g : ℝ → ℝ) (C : Set Plane) : ENNReal := liminf (openDiskEnergy g C) atTop

/-! ## Radius shifts -/

/-- The open disk of radius `R` meets `C` in the same points as a closed disk of radius `R - δ`, `0 < δ < 1`. -/
lemma open_eq_closed_shift {C : Set Plane} (hC : LocallyFinite C) (R : ℝ) :
    ∃ δ : ℝ, 0 < δ ∧ δ < 1 ∧ C ∩ Metric.ball (0 : Plane) R = C ∩ Metric.closedBall (0 : Plane) (R - δ) := by
  classical
  set T : Finset Plane := (hC R).toFinset.filter (fun x => ‖x‖ < R) with hT
  by_cases hne : T.Nonempty
  · set m := T.sup' hne (fun x => ‖x‖) with hm
    have hmR : m < R := by
      rw [hm, Finset.sup'_lt_iff]
      intro x hx
      exact (Finset.mem_filter.1 hx).2
    refine ⟨min (1 / 2) ((R - m) / 2), lt_min (by norm_num) (by linarith), lt_of_le_of_lt (min_le_left _ _) (by norm_num), ?_⟩
    ext x
    simp only [Set.mem_inter_iff, Metric.mem_ball, Metric.mem_closedBall, dist_zero_right]
    constructor
    · rintro ⟨hx, hxR⟩
      refine ⟨hx, ?_⟩
      have hxT : x ∈ T := by
        rw [hT, Finset.mem_filter, Set.Finite.mem_toFinset]
        exact ⟨⟨hx, by rw [Metric.mem_closedBall, dist_zero_right]; exact hxR.le⟩, hxR⟩
      have h1 : ‖x‖ ≤ m := Finset.le_sup' (fun x => ‖x‖) hxT
      have h2 : min (1 / 2) ((R - m) / 2) ≤ (R - m) / 2 := min_le_right _ _
      linarith
    · rintro ⟨hx, hxR⟩
      refine ⟨hx, ?_⟩
      have : 0 < min (1 / 2 : ℝ) ((R - m) / 2) := lt_min (by norm_num) (by linarith)
      linarith
  · refine ⟨1 / 2, by norm_num, by norm_num, ?_⟩
    ext x
    simp only [Set.mem_inter_iff, Metric.mem_ball, Metric.mem_closedBall, dist_zero_right]
    constructor
    · rintro ⟨hx, hxR⟩
      exfalso
      apply hne
      refine ⟨x, ?_⟩
      rw [hT, Finset.mem_filter, Set.Finite.mem_toFinset]
      exact ⟨⟨hx, by rw [Metric.mem_closedBall, dist_zero_right]; exact hxR.le⟩, hxR⟩
    · rintro ⟨hx, hxR⟩
      exfalso
      apply hne
      refine ⟨x, ?_⟩
      rw [hT, Finset.mem_filter, Set.Finite.mem_toFinset]
      exact ⟨⟨hx, by rw [Metric.mem_closedBall, dist_zero_right]; linarith⟩, by linarith⟩

/-- The closed disk of radius `R` meets `C` in the same points as an open disk of radius `R + δ`, `0 < δ < 1`. -/
lemma closed_eq_open_shift {C : Set Plane} (hC : LocallyFinite C) (R : ℝ) :
    ∃ δ : ℝ, 0 < δ ∧ δ < 1 ∧ C ∩ Metric.closedBall (0 : Plane) R = C ∩ Metric.ball (0 : Plane) (R + δ) := by
  classical
  set T : Finset Plane := (hC (R + 1)).toFinset.filter (fun x => R < ‖x‖) with hT
  by_cases hne : T.Nonempty
  · set m := T.inf' hne (fun x => ‖x‖) with hm
    have hmR : R < m := by
      rw [hm, Finset.lt_inf'_iff]
      intro x hx
      exact (Finset.mem_filter.1 hx).2
    refine ⟨min (1 / 2) ((m - R) / 2), lt_min (by norm_num) (by linarith), lt_of_le_of_lt (min_le_left _ _) (by norm_num), ?_⟩
    ext x
    simp only [Set.mem_inter_iff, Metric.mem_ball, Metric.mem_closedBall, dist_zero_right]
    constructor
    · rintro ⟨hx, hxR⟩
      have : 0 < min (1 / 2 : ℝ) ((m - R) / 2) := lt_min (by norm_num) (by linarith)
      exact ⟨hx, by linarith⟩
    · rintro ⟨hx, hxR⟩
      refine ⟨hx, ?_⟩
      by_contra hgt
      push_neg at hgt
      have h12 : min (1 / 2 : ℝ) ((m - R) / 2) ≤ 1 / 2 := min_le_left _ _
      have hxT : x ∈ T := by
        rw [hT, Finset.mem_filter, Set.Finite.mem_toFinset]
        exact ⟨⟨hx, by rw [Metric.mem_closedBall, dist_zero_right]; linarith⟩, hgt⟩
      have h1 : m ≤ ‖x‖ := Finset.inf'_le (fun x => ‖x‖) hxT
      have h2 : min (1 / 2) ((m - R) / 2) ≤ (m - R) / 2 := min_le_right _ _
      linarith
  · refine ⟨1 / 2, by norm_num, by norm_num, ?_⟩
    ext x
    simp only [Set.mem_inter_iff, Metric.mem_ball, Metric.mem_closedBall, dist_zero_right]
    constructor
    · rintro ⟨hx, hxR⟩
      exact ⟨hx, by linarith⟩
    · rintro ⟨hx, hxR⟩
      refine ⟨hx, ?_⟩
      by_contra hgt
      push_neg at hgt
      apply hne
      refine ⟨x, ?_⟩
      rw [hT, Finset.mem_filter, Set.Finite.mem_toFinset]
      exact ⟨⟨hx, by rw [Metric.mem_closedBall, dist_zero_right]; linarith⟩, hgt⟩

/-! ## Point sets, counts and energies at shifted radii -/

lemma openDiskPoints_eq {C : Set Plane} (hC : LocallyFinite C) {R R' : ℝ}
    (h : C ∩ Metric.ball (0 : Plane) R = C ∩ Metric.closedBall (0 : Plane) R') :
    openDiskPoints C R = diskPoints C R' := by
  have hfin : (C ∩ Metric.ball (0 : Plane) R).Finite := by rw [h]; exact hC R'
  unfold openDiskPoints diskPoints OAI.TriangularUniversal.diskPoints
  rw [dif_pos hfin, dif_pos (hC R')]
  ext x
  simp only [Set.Finite.mem_toFinset]
  rw [h]

lemma openDiskEnergy_eq {g : ℝ → ℝ} {C : Set Plane} (hC : LocallyFinite C) {R R' : ℝ}
    (h : C ∩ Metric.ball (0 : Plane) R = C ∩ Metric.closedBall (0 : Plane) R') :
    openDiskEnergy g C R = diskEnergy g C R' := by
  unfold openDiskEnergy openDiskCount diskEnergy OAI.TriangularUniversal.diskEnergy
  rw [show OAI.TriangularUniversal.diskCount C R' = diskCount C R' from rfl,
    show OAI.TriangularUniversal.diskPoints C R' = diskPoints C R' from rfl, openDiskPoints_eq hC h]
  rfl

/-! ## Lower limits under a reparametrisation of the radius -/

lemma liminf_le_liminf_comp (u : ℝ → ENNReal) {φ : ℝ → ℝ} (hφ : Tendsto φ atTop atTop) :
    liminf u atTop ≤ liminf (u ∘ φ) atTop := by
  have h : liminf (u ∘ φ) atTop = liminf u (map φ atTop) := by
    unfold Filter.liminf
    rw [← Filter.map_map]
  rw [h]
  exact liminf_le_liminf_of_le hφ

/-- **D4, energy.** The lower energy is the same with open and with closed disks. -/
theorem energy_eq_openEnergy (g : ℝ → ℝ) {C : Set Plane} (hC : LocallyFinite C) :
    energy g C = openEnergy g C := by
  choose δ hδ0 hδ1 hδ using open_eq_closed_shift hC
  choose ε hε0 hε1 hε using closed_eq_open_shift hC
  have hφ : Tendsto (fun R => R - δ R) atTop atTop :=
    tendsto_atTop_mono (fun R => show id R + -1 ≤ R - δ R by simp only [id]; linarith [hδ1 R])
      (tendsto_atTop_add_const_right _ (-1) tendsto_id)
  have hψ : Tendsto (fun R => R + ε R) atTop atTop :=
    tendsto_atTop_mono (fun R => show id R ≤ R + ε R by simp only [id]; linarith [hε0 R]) tendsto_id
  have e1 : openDiskEnergy g C = diskEnergy g C ∘ (fun R => R - δ R) := by
    funext R
    exact openDiskEnergy_eq hC (hδ R)
  have e2 : diskEnergy g C = openDiskEnergy g C ∘ (fun R => R + ε R) := by
    funext R
    exact (openDiskEnergy_eq hC (hε R).symm).symm
  apply le_antisymm
  · unfold energy OAI.TriangularUniversal.energy openEnergy
    rw [show OAI.TriangularUniversal.diskEnergy g C = diskEnergy g C from rfl, e1]
    exact liminf_le_liminf_comp _ hφ
  · unfold energy OAI.TriangularUniversal.energy openEnergy
    rw [show OAI.TriangularUniversal.diskEnergy g C = diskEnergy g C from rfl, e2]
    exact liminf_le_liminf_comp _ hψ

/-! ## Densities -/

lemma diskCount_mono {C : Set Plane} (hC : LocallyFinite C) {R R' : ℝ} (h : R ≤ R') :
    diskCount C R ≤ diskCount C R' := by
  unfold diskCount OAI.TriangularUniversal.diskCount
  apply Finset.card_le_card
  intro x
  unfold OAI.TriangularUniversal.diskPoints
  rw [dif_pos (hC R), dif_pos (hC R')]
  simp only [Set.Finite.mem_toFinset, Set.mem_inter_iff, Metric.mem_closedBall]
  exact fun ⟨hx, hr⟩ => ⟨hx, hr.trans h⟩

lemma openDiskCount_eq {C : Set Plane} (hC : LocallyFinite C) {R R' : ℝ}
    (h : C ∩ Metric.ball (0 : Plane) R = C ∩ Metric.closedBall (0 : Plane) R') :
    openDiskCount C R = diskCount C R' := by
  unfold openDiskCount
  rw [openDiskPoints_eq hC h]
  rfl

/-- `f (R - 1) / (π R²) → 1` when `f R / (π R²) → 1`. -/
lemma tendsto_shift_ratio {f : ℝ → ℝ} (c : ℝ)
    (hf : Tendsto (fun R : ℝ => f R / (Real.pi * R ^ 2)) atTop (𝓝 1)) :
    Tendsto (fun R : ℝ => f (R + c) / (Real.pi * R ^ 2)) atTop (𝓝 1) := by
  have h1 : Tendsto (fun R : ℝ => f (R + c) / (Real.pi * (R + c) ^ 2)) atTop (𝓝 1) :=
    hf.comp (tendsto_atTop_add_const_right _ c tendsto_id)
  have h2 : Tendsto (fun R : ℝ => (R + c) ^ 2 / R ^ 2) atTop (𝓝 1) := by
    have h3 : Tendsto (fun R : ℝ => (1 + c / R) ^ 2) atTop (𝓝 ((1 + 0) ^ 2)) :=
      ((tendsto_const_nhds.add (tendsto_const_nhds.div_atTop tendsto_id))).pow 2
    rw [show ((1 : ℝ) + 0) ^ 2 = 1 by norm_num] at h3
    refine h3.congr' ?_
    filter_upwards [eventually_gt_atTop (0 : ℝ)] with R hR
    field_simp
  have := h1.mul h2
  rw [mul_one] at this
  refine this.congr' ?_
  filter_upwards [eventually_gt_atTop (|c| + 1)] with R hR
  have hR0 : 0 < R := by linarith [abs_nonneg c]
  have hRc : R + c ≠ 0 := by
    have : -c ≤ |c| := neg_le_abs c
    intro h0
    linarith
  field_simp

lemma squeeze_density {f lo hi : ℝ → ℝ} (hlo : ∀ᶠ R in atTop, lo R ≤ f R) (hhi : ∀ᶠ R in atTop, f R ≤ hi R)
    (h1 : Tendsto (fun R : ℝ => lo R / (Real.pi * R ^ 2)) atTop (𝓝 1))
    (h2 : Tendsto (fun R : ℝ => hi R / (Real.pi * R ^ 2)) atTop (𝓝 1)) :
    Tendsto (fun R : ℝ => f R / (Real.pi * R ^ 2)) atTop (𝓝 1) := by
  refine tendsto_of_tendsto_of_tendsto_of_le_of_le' h1 h2 ?_ ?_
  · filter_upwards [hlo, eventually_gt_atTop (0 : ℝ)] with R h hR
    exact div_le_div_of_nonneg_right h (by positivity)
  · filter_upwards [hhi, eventually_gt_atTop (0 : ℝ)] with R h hR
    exact div_le_div_of_nonneg_right h (by positivity)

/-- **D4, density.** Centred density one is the same with open and with closed disks. -/
theorem densityOne_iff_open {C : Set Plane} (hC : LocallyFinite C) : DensityOne C ↔ DensityOneOpen C := by
  choose δ hδ0 hδ1 hδ using open_eq_closed_shift hC
  choose ε hε0 hε1 hε using closed_eq_open_shift hC
  -- N_closed (R - 1) ≤ N_open R ≤ N_closed R
  have lo : ∀ R, (diskCount C (R + -1) : ℝ) ≤ openDiskCount C R := fun R => by
    rw [openDiskCount_eq hC (hδ R)]
    have hle : R + -1 ≤ R - δ R := by linarith [hδ1 R]
    exact Nat.cast_le.mpr (diskCount_mono hC hle)
  have hi : ∀ R, (openDiskCount C R : ℝ) ≤ diskCount C R := fun R => by
    rw [openDiskCount_eq hC (hδ R)]
    exact_mod_cast diskCount_mono hC (by linarith [hδ0 R])
  -- N_open R ≤ N_closed R ≤ N_open (R + 1)
  have hi' : ∀ R, (diskCount C R : ℝ) ≤ openDiskCount C (R + 1) := fun R => by
    have e : openDiskCount C (R + 1) = diskCount C (R + 1 - δ (R + 1)) := openDiskCount_eq hC (hδ (R + 1))
    rw [e]
    exact_mod_cast diskCount_mono hC (by linarith [hδ1 (R + 1)])
  constructor
  · intro hd
    unfold DensityOneOpen
    unfold DensityOne OAI.TriangularUniversal.DensityOne at hd
    exact squeeze_density (Eventually.of_forall lo) (Eventually.of_forall hi) (tendsto_shift_ratio (-1) hd) hd
  · intro hd
    unfold DensityOne OAI.TriangularUniversal.DensityOne
    unfold DensityOneOpen at hd
    exact squeeze_density (Eventually.of_forall hi)
      (Eventually.of_forall hi') hd (tendsto_shift_ratio 1 hd)

/-- **D4.** Upstream's universal optimality theorem, verbatim with open disks. -/
theorem universal_energy_minimum_open (g : ℝ → ℝ) (C : Set Plane) (hg : AdmissiblePotential g)
    (hC : LocallyFinite C) (hd : DensityOneOpen C) :
    latticeEnergy g ≤ openEnergy g C ∧ latticeEnergy g = openEnergy g A := by
  have hA : LocallyFinite A := TriangularDensity.A_lf
  have h := universal_energy_minimum g C hg hC ((densityOne_iff_open hC).2 hd)
  rw [← energy_eq_openEnergy g hC, ← energy_eq_openEnergy g hA]
  exact h

/-- Non-vacuity: the triangular lattice itself has open-disk density one, so the open-disk hypothesis is satisfiable
and the theorem above is attained by `A`. -/
theorem A_densityOneOpen : DensityOneOpen A :=
  (densityOne_iff_open TriangularDensity.A_lf).1 TriangularDensity.A_d1

end TriangularOpenDisk
