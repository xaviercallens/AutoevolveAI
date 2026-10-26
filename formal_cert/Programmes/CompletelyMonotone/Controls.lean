import Programmes.CompletelyMonotone.Basic

/-!
# Programme P3: planted controls (must be CAUGHT by the axiom gate; never import this file)

`ctl_sorry` and `ctl_axiom` "prove" a false statement (`cos` is not completely monotone, see
`ProgCM.cos_not_cm`). Both files compile with exit code 0; only `#print axioms` exposes them
(`sorryAx`, resp. `ProgCM.ctl_cheat`).
-/

theorem ProgCM.ctl_sorry : ProgCM.IsCompletelyMonotoneOn Real.cos := sorry

axiom ProgCM.ctl_cheat : False

theorem ProgCM.ctl_axiom : ProgCM.IsCompletelyMonotoneOn Real.cos := ProgCM.ctl_cheat.elim

#print axioms ProgCM.ctl_sorry
#print axioms ProgCM.ctl_axiom
