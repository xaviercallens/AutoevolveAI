import Programmes.ZeroPointPhys.Basic

/-! N2 axiom-gate controls: these compile (rc 0) but `#print axioms` must expose `sorryAx` and the planted axiom. -/

namespace ProgZeroPointPhysCtl

theorem ctl_sorry : (4463084749303 / 1000000000000 : ℝ) < 0 := by
  sorry

axiom ctl_cheat : (4463084749303 / 1000000000000 : ℝ) < 0

theorem ctl_axiom : (4463084749303 / 1000000000000 : ℝ) < 0 := ctl_cheat

end ProgZeroPointPhysCtl

#print axioms ProgZeroPointPhysCtl.ctl_sorry
#print axioms ProgZeroPointPhysCtl.ctl_axiom
