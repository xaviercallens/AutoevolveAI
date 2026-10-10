import Triangular.Riesz
import Triangular.RieszFinite

/-! Axiom audit of the D1 corollary, with planted controls. -/

#print axioms TriangularRiesz.riesz_admissible
#print axioms TriangularRiesz.triangular_riesz_optimal
#print axioms OAI.AtomicTriangular.universal_energy_minimum
#print axioms TriangularRiesz.norm_sq_triangularPoint
#print axioms TriangularRiesz.latticeEnergy_riesz_lt_top
#print axioms OAI.SevenEighths.LatticeSummability.summable_normForm_neg_rpow

theorem ctl_sorry : TriangularRiesz.riesz 1 1 = 0 := by sorry
axiom ctl_cheat : False
theorem ctl_axiom : TriangularRiesz.riesz 1 1 = 0 := ctl_cheat.elim
#print axioms ctl_sorry
#print axioms ctl_axiom
