import Programmes.ZeroPointClass.Basic

namespace ProgZeroPointClass

/-- MUST FAIL: the real record at a = 2/5 (inside the window) claimed positive. -/
def rIn : Rec := ⟨((2 : ℚ) / 5), ((2 : ℚ) / 5), ((2 : ℚ) / 5), ((-345994269 : ℚ) / 500000000), ((-117362513 : ℚ) / 200000000), ((-7166998609 : ℚ) / 250000000), ((-895822827 : ℚ) / 31250000)⟩

theorem inside_claimed_pos : allPos [rIn] = true := by decide +kernel

end ProgZeroPointClass
