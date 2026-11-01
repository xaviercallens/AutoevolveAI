import Programmes.LowDissE3.Core

/-!
# E3 planted controls (must be CAUGHT by the axiom gate; NEVER import this file, not part of the claim)

Both compile with exit code 0; only `#print axioms` exposes them (`sorryAx`, resp. `LowDissE3.ctl_cheat`).
-/

theorem LowDissE3.ctl_sorry : LowDissE3.etaPlus (1 / 2) 2 1 < LowDissE3.etaPlus (1 / 2) 2 (-1) := sorry

axiom LowDissE3.ctl_cheat : False

theorem LowDissE3.ctl_axiom : LowDissE3.etaPlus (1 / 2) 2 1 < LowDissE3.etaPlus (1 / 2) 2 (-1) :=
  LowDissE3.ctl_cheat.elim

#print axioms LowDissE3.ctl_sorry
#print axioms LowDissE3.ctl_axiom
