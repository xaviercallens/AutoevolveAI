import Programmes.SandierSerfatyStatement

namespace ProgSandierSerfaty

theorem ctl_sorry : SandierSerfatyStatement := sorry

axiom ctl_cheat : False

theorem ctl_axiom : SandierSerfatyStatement := ctl_cheat.elim

end ProgSandierSerfaty

#print axioms ProgSandierSerfaty.ctl_sorry
#print axioms ProgSandierSerfaty.ctl_axiom
