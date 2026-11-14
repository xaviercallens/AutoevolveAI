import Autoresearch.DipolarExcitonMultipolar

/-! Stage-4 independent audit (H1). Not a claimed module: it contains a planted `sorry`, a planted axiom and
statement probes. Expected: `audit_sorry` -> sorryAx, `audit_axiom` -> audit_cheat, every claimed theorem within
propext / Classical.choice / Quot.sound. -/

namespace DipolarAuditH1

open OAI.AtomicTriangular TriangularRiesz

theorem audit_sorry : (2 : ℕ) + 2 = 5 := sorry

axiom audit_cheat : (0 : ℝ) = 1

theorem audit_axiom : (3 : ℕ) = 4 := by
  exfalso
  have := audit_cheat
  norm_num at this

/-- Probe: the Step-1 identity g d t = 2 (1/√t - 1/√(t+d²)) for t > 0 (paper files it at Tier C). -/
theorem audit_g_sqrt (d t : ℝ) (ht : 0 < t) :
    AutoresearchDipolar.g d t = 2 * (1 / Real.sqrt t - 1 / Real.sqrt (t + d ^ 2)) := by
  have h2 : 0 ≤ t + d ^ 2 := by positivity
  simp only [AutoresearchDipolar.g, Real.sqrt_eq_rpow, one_div, Real.rpow_neg ht.le, Real.rpow_neg h2]

/-- Probe: the density-one corollary for the general family really applies at d = 0 boundary (g 0 = 0). -/
theorem audit_g_zero (t : ℝ) (ht : 0 < t) : AutoresearchDipolar.g 0 t = 0 := by
  simp [AutoresearchDipolar.g]

end DipolarAuditH1

#check @AutoresearchDipolar.dipolar_admissible
#check @AutoresearchDipolar.triangular_dipolar_optimal
#check @AutoresearchDipolar.latticeEnergy_dipolar_lt_top
#check @AutoresearchDipolar.h_not_admissible
#check @AutoresearchDipolarMultipolar.shiftDiff_admissible
#check @AutoresearchDipolarMultipolar.shiftDiff_not_admissible_of_neg
#check @AutoresearchDipolarMultipolar.triangular_dipolar_optimal_any_density
#check @AutoresearchDipolarMultipolar.energy_dipolar_any_density_lt_top
#check @OAI.AtomicTriangular.AdmissiblePotential
#print OAI.AtomicTriangular.AdmissiblePotential
#print TriangularDensity.DensityRho
#print OAI.AtomicTriangular.DensityOne
#print OAI.TriangularUniversal.DensityOne
#print OAI.TriangularUniversal.AdmissiblePotential
#print OAI.AtomicTriangular.energy
#print OAI.AtomicTriangular.latticeEnergy
#print OAI.AtomicTriangular.LocallyFinite
#print OAI.AtomicTriangular.diskCount
#print OAI.TriangularUniversal.energy
#print OAI.TriangularUniversal.LocallyFinite
#print OAI.TriangularUniversal.diskCount
#print axioms AutoresearchDipolarMultipolar.g_eq_shiftDiff
#print axioms AutoresearchDipolarMultipolar.shiftDiff_neg_of_neg
#check @OAI.AtomicTriangular.universal_energy_minimum
#print axioms DipolarAuditH1.audit_sorry
#print axioms DipolarAuditH1.audit_axiom
#print axioms DipolarAuditH1.audit_g_sqrt
#print axioms DipolarAuditH1.audit_g_zero
#print axioms AutoresearchDipolar.dipolar_admissible
#print axioms AutoresearchDipolar.triangular_dipolar_optimal
#print axioms AutoresearchDipolar.latticeEnergy_dipolar_lt_top
#print axioms AutoresearchDipolar.h_not_admissible
#print axioms AutoresearchDipolarMultipolar.shiftDiff_admissible
#print axioms AutoresearchDipolarMultipolar.admissible_const_mul
#print axioms AutoresearchDipolarMultipolar.dipolar_admissible_all
#print axioms AutoresearchDipolarMultipolar.shiftDiff_not_admissible_of_neg
#print axioms AutoresearchDipolarMultipolar.triangular_dipolar_optimal_any_density
#print axioms AutoresearchDipolarMultipolar.triangular_shiftDiff_optimal_any_density
#print axioms AutoresearchDipolarMultipolar.triangular_shiftDiff_optimal
#print axioms AutoresearchDipolarMultipolar.g_scaled_le
#print axioms AutoresearchDipolarMultipolar.latticeEnergy_dipolar_scaled_lt_top
#print axioms AutoresearchDipolarMultipolar.energy_dipolar_any_density_lt_top
