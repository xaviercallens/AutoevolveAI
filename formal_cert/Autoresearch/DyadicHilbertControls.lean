import Autoresearch.DyadicHilbert

/-! Planted controls for the H6 gate: both must be caught by `#print axioms`. -/

namespace AutoresearchDyadicControls

theorem ctl_sorry : (1 : ℕ) = 2 := sorry

axiom ctl_cheat : False

theorem ctl_axiom : (1 : ℕ) = 2 := ctl_cheat.elim

end AutoresearchDyadicControls

#print axioms AutoresearchDyadicControls.ctl_sorry
#print axioms AutoresearchDyadicControls.ctl_axiom
#print axioms AutoresearchDyadic.T_cmul
#print axioms AutoresearchDyadic.H_cmul
#print axioms AutoresearchDyadic.T_tensor
#print axioms AutoresearchDyadic.L0_tensor
#print axioms AutoresearchDyadic.H_tensor
#print axioms AutoresearchDyadic.S_tensor
#print axioms AutoresearchDyadic.product_rule
#print axioms AutoresearchDyadic.g2_pm1
#print axioms AutoresearchDyadic.g2_T
#print axioms AutoresearchDyadic.g2_H
#print axioms AutoresearchDyadic.g2_R
#print axioms AutoresearchDyadic.gpow_pm1
#print axioms AutoresearchDyadic.gpow_R
#print axioms AutoresearchDyadic.gpow4_R
#print axioms AutoresearchDyadic.sup_ge_three
#print axioms AutoresearchDyadic.wrong_rule_refuted
