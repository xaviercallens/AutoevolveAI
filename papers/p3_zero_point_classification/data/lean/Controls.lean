import Programmes.ZeroPointClass.Basic

/-!
# N1 negative controls for the axiom gate (this file MUST compile with rc 0 and its `#print axioms` MUST show the
# planted `sorryAx` and `ProgZeroPointClass.ctl_cheat`; a gate that only reads the exit code would accept both)
-/

namespace ProgZeroPointClass

/-- A planted false record list: one record whose upper end is positive is claimed all-negative. -/
def ctlList : List Rec := [⟨(2 : ℚ) / 5, (41 : ℚ) / 100, (2 : ℚ) / 5, (-1 : ℚ), (1 : ℚ) / 10, (0 : ℚ), (1 : ℚ)⟩]

theorem ctl_sorry : allNeg ctlList = true := by
  sorry

axiom ctl_cheat : allNeg ctlList = true

theorem ctl_axiom : allNeg ctlList = true := ctl_cheat

/-- The honest version: the planted statement is false. -/
theorem ctl_false : allNeg ctlList = false := by decide +kernel

end ProgZeroPointClass

#print axioms ProgZeroPointClass.ctl_sorry
#print axioms ProgZeroPointClass.ctl_axiom
#print axioms ProgZeroPointClass.ctl_false
