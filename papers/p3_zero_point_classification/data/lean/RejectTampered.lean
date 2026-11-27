import Programmes.ZeroPointClass.Basic

namespace ProgZeroPointClass

/-- MUST FAIL: the real positive record at a = 93/250 with the sign of qlo flipped. -/
def rT : Rec := ⟨((93 : ℚ) / 250), ((93 : ℚ) / 250), ((93 : ℚ) / 250), ((-13958737 : ℚ) / 200000000), ((85118003 : ℚ) / 500000000), ((-25307802999 : ℚ) / 1000000000), ((-25305367041 : ℚ) / 1000000000)⟩

theorem tampered_claimed_pos : allPos [rT] = true := by decide +kernel

end ProgZeroPointClass
