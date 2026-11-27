import Programmes.DacExergy.Core

/-!
# K1 planted controls (must be CAUGHT by the axiom gate; never import this file)

Each "proves" the FALSE claim that the CO2-only exergy term of the rational instance is positive
(`DacExergy.instance_r1` kernel-checks that it is negative). Both compile with exit
code 0; only `#print axioms` exposes them (`sorryAx`, resp. `DacExergy.ctl_cheat`).
-/

theorem DacExergy.ctl_sorry :
    0 < -((40000 : ℝ) * ((29815 / 100) / 200 - 1)) + (4157 / 500) * ((29815 / 100) - 200) := sorry

axiom DacExergy.ctl_cheat : False

theorem DacExergy.ctl_axiom :
    0 < -((40000 : ℝ) * ((29815 / 100) / 200 - 1)) + (4157 / 500) * ((29815 / 100) - 200) :=
  DacExergy.ctl_cheat.elim

#print axioms DacExergy.ctl_sorry
#print axioms DacExergy.ctl_axiom
