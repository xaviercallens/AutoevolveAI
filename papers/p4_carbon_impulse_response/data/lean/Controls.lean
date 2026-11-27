import Programmes.CarbonK3.Core

/-!
# K3 planted controls (must be CAUGHT by the axiom gate; never import this file)

Each "proves" the FALSE claim that `h(t) = 1 - exp(-t)` (one negative coefficient) is completely monotone on (0, inf)
(`CarbonK3.neg_ctl_not_cm` kernel-checks the negation). Both compile with exit code 0; only `#print axioms` exposes
them (`sorryAx`, resp. `CarbonK3.ctl_cheat`).
-/

theorem CarbonK3.ctl_sorry :
    ProgCM.IsCompletelyMonotoneOn (CarbonK3.irf (n := 1) 1 (fun _ => -1) (fun _ => 1)) := sorry

axiom CarbonK3.ctl_cheat : False

theorem CarbonK3.ctl_axiom :
    ProgCM.IsCompletelyMonotoneOn (CarbonK3.irf (n := 1) 1 (fun _ => -1) (fun _ => 1)) :=
  CarbonK3.ctl_cheat.elim

#print axioms CarbonK3.ctl_sorry
#print axioms CarbonK3.ctl_axiom
