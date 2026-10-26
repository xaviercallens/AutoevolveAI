import Programmes.SandierSerfatyStatement

/-!
# P1 S3 planted controls (must be CAUGHT by the axiom gate; never import this file)

`ctl_sorry` and `ctl_axiom` "prove" the Sandier–Serfaty statement. This file compiles with exit code 0; only
`#print axioms` exposes the cheats (`sorryAx`, resp. `ProgSandierSerfaty.ctl_cheat`). A gate that accepted either
would be useless for this statement.
-/

namespace ProgSandierSerfaty

theorem ctl_sorry : SandierSerfatyStatement := sorry

axiom ctl_cheat : False

theorem ctl_axiom : SandierSerfatyStatement := ctl_cheat.elim

end ProgSandierSerfaty

#print axioms ProgSandierSerfaty.ctl_sorry
#print axioms ProgSandierSerfaty.ctl_axiom
