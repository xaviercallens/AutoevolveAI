import Autoresearch.Yukawa

/-! Planted controls for the H2 gate: both must be caught by `#print axioms`. -/

namespace AutoresearchYukawaControls

theorem ctl_sorry : (1 : ℕ) = 2 := sorry

axiom ctl_cheat : False

theorem ctl_axiom : (1 : ℕ) = 2 := ctl_cheat.elim

end AutoresearchYukawaControls

#print axioms AutoresearchYukawaControls.ctl_sorry
#print axioms AutoresearchYukawaControls.ctl_axiom
#print axioms AutoresearchYukawa.mul_sign
#print axioms AutoresearchYukawa.admissible_mul
#print axioms AutoresearchYukawa.admissible_congr
#print axioms AutoresearchYukawa.phi_sign
#print axioms AutoresearchYukawa.phi_admissible
#print axioms AutoresearchYukawa.yukawa_admissible
#print axioms AutoresearchYukawa.triangular_yukawa_optimal
#print axioms AutoresearchYukawa.c_neg_at_pi
#print axioms AutoresearchYukawa.c_not_admissible
#print axioms AutoresearchYukawa.g_le
#print axioms AutoresearchYukawa.latticeEnergy_yukawa_lt_top
