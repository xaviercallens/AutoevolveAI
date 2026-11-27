import Triangular.OpenDisk

/-!
# D4, strengthened: the open/closed identities need no hypothesis on the configuration

Written by the independent D4 verification run (results/discovery/D4/verification.md) and merged by the producer.
If C is not locally finite, beyond the first radius where a closed disk meets C in infinitely many points both
upstream's diskPoints and openDiskPoints are empty, so the energies agree eventually and both density statements are
false. The controls ctl_open / ctl_closed show the identity is not definitional: for a single point on the unit
circle the open and closed counts differ at R = 1.
-/

namespace TriangularOpenDiskAny

open OAI.AtomicTriangular TriangularOpenDisk Filter Topology Set

/-- Without local finiteness the energy identity still holds: beyond the first radius `R0` where the closed disk is
infinite, both upstream's `diskPoints` and `openDiskPoints` return `∅`, so the two energy functions agree eventually. -/
theorem energy_eq_openEnergy_any (g : ℝ → ℝ) (C : Set Plane) : energy g C = openEnergy g C := by
  by_cases hC : OAI.AtomicTriangular.LocallyFinite C
  · exact energy_eq_openEnergy g hC
  · unfold OAI.AtomicTriangular.LocallyFinite OAI.TriangularUniversal.LocallyFinite at hC
    push_neg at hC
    obtain ⟨R0, hR0⟩ := hC
    have hev : ∀ᶠ R in atTop, openDiskEnergy g C R = OAI.TriangularUniversal.diskEnergy g C R := by
      filter_upwards [eventually_gt_atTop R0] with R hR
      have h1 : ¬ (C ∩ Metric.closedBall (0 : Plane) R).Finite := fun h =>
        hR0 (h.subset (inter_subset_inter_right _ (Metric.closedBall_subset_closedBall hR.le)))
      have h2 : ¬ (C ∩ Metric.ball (0 : Plane) R).Finite := fun h =>
        hR0 (h.subset (inter_subset_inter_right _ (Metric.closedBall_subset_ball hR)))
      unfold openDiskEnergy openDiskCount openDiskPoints OAI.TriangularUniversal.diskEnergy
        OAI.TriangularUniversal.diskCount OAI.TriangularUniversal.diskPoints
      rw [dif_neg h1, dif_neg h2]
    unfold energy OAI.TriangularUniversal.energy openEnergy
    exact (Filter.liminf_congr hev).symm

/-- Without local finiteness the density equivalence still holds (both sides are false). -/
theorem densityOne_iff_open_any (C : Set Plane) : DensityOne C ↔ DensityOneOpen C := by
  by_cases hC : OAI.AtomicTriangular.LocallyFinite C
  · exact densityOne_iff_open hC
  · unfold OAI.AtomicTriangular.LocallyFinite OAI.TriangularUniversal.LocallyFinite at hC
    push_neg at hC
    obtain ⟨R0, hR0⟩ := hC
    have hc : ∀ᶠ R in atTop, (diskCount C R : ℝ) / (Real.pi * R ^ 2) = 0 := by
      filter_upwards [eventually_gt_atTop R0] with R hR
      have h1 : ¬ (C ∩ Metric.closedBall (0 : Plane) R).Finite := fun h =>
        hR0 (h.subset (inter_subset_inter_right _ (Metric.closedBall_subset_closedBall hR.le)))
      unfold diskCount OAI.TriangularUniversal.diskCount OAI.TriangularUniversal.diskPoints
      rw [dif_neg h1]
      simp
    have ho : ∀ᶠ R in atTop, (openDiskCount C R : ℝ) / (Real.pi * R ^ 2) = 0 := by
      filter_upwards [eventually_gt_atTop R0] with R hR
      have h2 : ¬ (C ∩ Metric.ball (0 : Plane) R).Finite := fun h =>
        hR0 (h.subset (inter_subset_inter_right _ (Metric.closedBall_subset_ball hR)))
      unfold openDiskCount openDiskPoints
      rw [dif_neg h2]
      simp
    constructor
    · intro hd
      unfold DensityOne OAI.TriangularUniversal.DensityOne at hd
      have h0 := tendsto_nhds_unique (hd.congr' hc) tendsto_const_nhds
      norm_num at h0
    · intro hd
      unfold DensityOneOpen at hd
      have h0 := tendsto_nhds_unique (hd.congr' ho) tendsto_const_nhds
      norm_num at h0

/-- Control: the identity is not definitional; pointwise counts differ for a point on the boundary circle. -/
noncomputable def e : Plane := EuclideanSpace.single 0 1

lemma norm_e : ‖e‖ = 1 := by simp [e]

lemma ctl_open : openDiskCount {e} 1 = 0 := by
  have hs : ({e} : Set Plane) ∩ Metric.ball 0 1 = ∅ := by
    ext x
    simp only [Set.mem_inter_iff, Set.mem_singleton_iff, Metric.mem_ball, dist_zero_right,
      Set.mem_empty_iff_false, iff_false, not_and]
    intro hx
    rw [hx, norm_e]
    norm_num
  unfold openDiskCount openDiskPoints
  split_ifs with h
  · rw [Finset.card_eq_zero, Set.Finite.toFinset_eq_empty]
    exact hs
  · rfl

lemma ctl_closed : diskCount {e} 1 = 1 := by
  have hs : ({e} : Set Plane) ∩ Metric.closedBall 0 1 = {e} := by
    ext x
    simp only [Set.mem_inter_iff, Set.mem_singleton_iff, Metric.mem_closedBall, dist_zero_right,
      and_iff_left_iff_imp]
    intro hx
    rw [hx, norm_e]
  unfold diskCount OAI.TriangularUniversal.diskCount OAI.TriangularUniversal.diskPoints
  rw [dif_pos (by rw [hs]; exact Set.finite_singleton e)]
  rw [Finset.card_eq_one]
  refine ⟨e, ?_⟩
  ext x
  rw [Set.Finite.mem_toFinset, hs]
  simp

end TriangularOpenDiskAny
