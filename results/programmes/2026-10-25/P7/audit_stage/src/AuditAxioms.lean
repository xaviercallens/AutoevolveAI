import Autoresearch.PopGenWrightFisher
import Programmes.PopGen.WrightFisherFixation
import Programmes.PopGen.MoranFixation
import Programmes.PopGen.Price

/-! Auditor's own axiom audit and statement display (P7 audit, not the producer). -/

open ProgPopGen ProgPopGen.Price Filter Topology

#check @ProgPopGen.fixation_limit
#check @ProgPopGen.harmonic_unique_of_var
#check @ProgPopGen.wright_fisher_fixation_limit
#check @ProgPopGen.moran_fixation_limit
#check @ProgPopGen.moran_fixation_limit_closed
#check @ProgPopGen.moran_fixation_limit_neutral
#check @ProgPopGen.moran_fixation_unique
#check @ProgPopGen.moran_closed_tendsto_neutral
#check @ProgPopGen.Price.price_equation
#check @ProgPopGen.Price.fisher_haploid_div
#check @ProgPopGen.Price.fisher_haploid_pos
#check @ProgPopGen.Price.Alix.aurelia_mean_fitness_increment

#print axioms ProgPopGen.fixation_limit
#print axioms ProgPopGen.harmonic_unique_of_var
#print axioms ProgPopGen.interiorMass_tendsto_zero
#print axioms ProgPopGen.mass_split
#print axioms ProgPopGen.kPow_last_mono
#print axioms ProgPopGen.ctl_neg_identity_no_absorption
#print axioms ProgPopGen.wright_fisher_fixation_limit
#print axioms ProgPopGen.wright_fisher_fixation_mono
#print axioms ProgPopGen.ctl_pos_wf_two_steps
#print axioms ProgPopGen.moranFix_harmonic_nat
#print axioms ProgPopGen.moran_var_pos_nat
#print axioms ProgPopGen.moranFix_closed
#print axioms ProgPopGen.moranFix_neutral
#print axioms ProgPopGen.moran_closed_tendsto_neutral
#print axioms ProgPopGen.moran_stay_nonneg
#print axioms ProgPopGen.ctl_pos_moranFix_N3
#print axioms ProgPopGen.ctl_neg_flipped_value
#print axioms ProgPopGen.ctl_neg_flipped_not_harmonic
#print axioms ProgPopGen.ctl_neg_neutral_not_harmonic
#print axioms ProgPopGen.moran_fixation_limit
#print axioms ProgPopGen.moran_fixation_limit_closed
#print axioms ProgPopGen.moran_fixation_limit_neutral
#print axioms ProgPopGen.moran_fixation_unique
#print axioms ProgPopGen.ctl_neg_wrong_limits
#print axioms ProgPopGen.Price.price_equation
#print axioms ProgPopGen.Price.wcov_eq_moment
#print axioms ProgPopGen.Price.price_equation_pos
#print axioms ProgPopGen.Price.fisher_haploid
#print axioms ProgPopGen.Price.fisher_haploid_div
#print axioms ProgPopGen.Price.fisher_haploid_nondecreasing
#print axioms ProgPopGen.Price.fisher_haploid_pos
#print axioms ProgPopGen.Price.Alix.aurelia_mean_fitness_increment
#print axioms ProgPopGen.Price.Alix.kal_increment_is_variance
#print axioms ProgPopGen.Price.ctl_pos_three_types
#print axioms ProgPopGen.Price.ctl_neg_transmission_bias
#print axioms ProgPopGen.Price.ctl_neg_missing_wbar

/-- Auditor's own non-vacuity instance: N = 2, r = 2, i = 1 limit is 2/3, derived from the claimed theorem. -/
theorem audit_moran_N2 :
    Tendsto (fun n => kPow (moranP 2 2) n 1 (Fin.last 2)) atTop (𝓝 (2 / 3)) := by
  have h := (moran_fixation_limit (N := 2) (r := 2) (by norm_num) (by norm_num) 1).1
  have hv : moranFix 2 2 ((1 : Fin 3) : ℕ) = 2 / 3 := by
    rw [show ((1 : Fin 3) : ℕ) = 1 from rfl]
    norm_num [moranFix, geomS, Finset.sum_range_succ]
  rwa [hv] at h

/-- Auditor's own direct check of the Moran kernel row at N = 2, r = 2, i = 1 (entries 1/6, 1/2, 1/3). -/
theorem audit_moran_row :
    moranP 2 2 1 0 = 1 / 6 ∧ moranP 2 2 1 1 = 1 / 2 ∧ moranP 2 2 1 2 = 1 / 3 := by
  refine ⟨?_, ?_, ?_⟩ <;> norm_num [moranP, bdP, moranUp, moranDown]

#print axioms audit_moran_N2
#print axioms audit_moran_row
