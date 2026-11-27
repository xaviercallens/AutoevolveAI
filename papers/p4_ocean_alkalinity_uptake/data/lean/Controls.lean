import Programmes.CarbonateK2.Core

/-!
# K2 planted controls (must be CAUGHT by the axiom gate; never import this file)

Each "proves" the FALSE claim that the retardation factor of the Jessen sum-CEC instance is below 50
(`CarbonateK2.jessen_R_sum` kernel-checks `58 < R`). Both compile with exit code 0; only `#print axioms`
exposes them (`sorryAx`, resp. `CarbonateK2.ctl_cheat`).
-/

theorem CarbonateK2.ctl_sorry : CarbonateK2.retard (56 / 100) < 50 := sorry

axiom CarbonateK2.ctl_cheat : False

theorem CarbonateK2.ctl_axiom : CarbonateK2.retard (56 / 100) < 50 := CarbonateK2.ctl_cheat.elim

#print axioms CarbonateK2.ctl_sorry
#print axioms CarbonateK2.ctl_axiom
