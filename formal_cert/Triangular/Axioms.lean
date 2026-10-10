import Triangular.Riesz
import Triangular.RieszFinite
import Triangular.AnyDensity
import Triangular.Controls

/-! Axiom audit of the D1 corollary, with planted controls. -/

#print axioms TriangularRiesz.riesz_admissible
#print axioms TriangularRiesz.triangular_riesz_optimal
#print axioms OAI.AtomicTriangular.universal_energy_minimum
#print axioms TriangularRiesz.norm_sq_triangularPoint
#print axioms TriangularRiesz.latticeEnergy_riesz_lt_top
#print axioms OAI.SevenEighths.LatticeSummability.summable_normForm_neg_rpow
#print axioms TriangularDensity.universal_any_density
#print axioms TriangularDensity.riesz_any_density
#print axioms TriangularDensity.scaled_density
#print axioms TriangularDensity.attained
#print axioms TriangularDensity.triangular_optimal_any_density
#print axioms TriangularDensity.unscaled_false
#print axioms TriangularControls.riesz_sq
#print axioms TriangularControls.riesz_neg_two_not_admissible
#print axioms TriangularControls.rho_one
#print axioms TriangularControls.riesz_lattice_homogeneous
#print axioms TriangularControls.riesz_any_density_homogeneous

theorem ctl_sorry : TriangularRiesz.riesz 1 1 = 0 := by sorry
axiom ctl_cheat : False
theorem ctl_axiom : TriangularRiesz.riesz 1 1 = 0 := ctl_cheat.elim
#print axioms ctl_sorry
#print axioms ctl_axiom
