import Autoresearch.DipolarExciton

/-! Planted controls for the H1/H1b gate: both must be caught by `#print axioms`. -/

namespace AutoresearchDipolarControls

theorem ctl_sorry : (1 : ℕ) = 2 := sorry

axiom ctl_cheat : False

theorem ctl_axiom : (1 : ℕ) = 2 := ctl_cheat.elim

end AutoresearchDipolarControls

#print axioms AutoresearchDipolarControls.ctl_sorry
#print axioms AutoresearchDipolarControls.ctl_axiom
#print axioms AutoresearchDipolar.dipolar_admissible
#print axioms AutoresearchDipolar.triangular_dipolar_optimal
#print axioms AutoresearchDipolar.h_not_admissible
#print axioms AutoresearchDipolar.latticeEnergy_dipolar_lt_top
#print axioms AutoresearchDipolar.diff_le
#print axioms AutoresearchDipolar.g_le
#print axioms AutoresearchDipolar.h_neg_at
