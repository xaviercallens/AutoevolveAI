import Programmes.YukawaBccFcc.Basic

/-!
# M3 planted controls (must be CAUGHT by the axiom gate; never import this file)

Both theorems below state the planted wrong multiplicity `N₇ = 46` (the true value is 48). The file compiles with
rc 0; only `#print axioms` exposes `sorryAx`, resp. `YukawaBccFcc.Controls.ctl_cheat`.
-/

namespace YukawaBccFcc.Controls

/-- Planted `sorry` control. -/
theorem ctl_sorry : YukawaBccFcc.Nc 7 = 46 := by sorry

/-- Planted axiom control. -/
axiom ctl_cheat : YukawaBccFcc.Nc 7 = 46

theorem ctl_axiom : YukawaBccFcc.Nc 7 = 46 := ctl_cheat

#print axioms ctl_sorry
#print axioms ctl_axiom

end YukawaBccFcc.Controls
