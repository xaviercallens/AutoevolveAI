import Autoresearch.DipolarExcitonMultipolar

/-! Planted controls for the H1 contribution gate: `ctl_sorry` and `ctl_axiom` must be flagged by `#print axioms`
(`sorryAx`, planted axiom); every claimed theorem must show only `propext`, `Classical.choice`, `Quot.sound`. -/

namespace AutoresearchDipolarMultipolarControls

theorem ctl_sorry : (1 : ℕ) = 2 := sorry

axiom ctl_cheat : False

theorem ctl_axiom : (1 : ℕ) = 2 := ctl_cheat.elim

end AutoresearchDipolarMultipolarControls

#print axioms AutoresearchDipolarMultipolarControls.ctl_sorry
#print axioms AutoresearchDipolarMultipolarControls.ctl_axiom
#print axioms AutoresearchDipolar.dipolar_admissible
#print axioms AutoresearchDipolar.triangular_dipolar_optimal
#print axioms AutoresearchDipolar.latticeEnergy_dipolar_lt_top
#print axioms AutoresearchDipolar.h_not_admissible
#print axioms AutoresearchDipolarMultipolar.shiftDiff_admissible
#print axioms AutoresearchDipolarMultipolar.admissible_const_mul
#print axioms AutoresearchDipolarMultipolar.g_eq_shiftDiff
#print axioms AutoresearchDipolarMultipolar.dipolar_admissible_all
#print axioms AutoresearchDipolarMultipolar.shiftDiff_neg_of_neg
#print axioms AutoresearchDipolarMultipolar.shiftDiff_not_admissible_of_neg
#print axioms AutoresearchDipolarMultipolar.triangular_dipolar_optimal_any_density
#print axioms AutoresearchDipolarMultipolar.triangular_shiftDiff_optimal_any_density
#print axioms AutoresearchDipolarMultipolar.triangular_shiftDiff_optimal
#print axioms AutoresearchDipolarMultipolar.g_scaled_le
#print axioms AutoresearchDipolarMultipolar.latticeEnergy_dipolar_scaled_lt_top
#print axioms AutoresearchDipolarMultipolar.energy_dipolar_any_density_lt_top
#print axioms TriangularDensity.triangular_optimal_any_density
#print axioms OAI.AtomicTriangular.universal_energy_minimum
