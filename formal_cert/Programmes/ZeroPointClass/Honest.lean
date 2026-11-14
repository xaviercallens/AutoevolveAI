import Programmes.ZeroPointClass.Basic

namespace ProgZeroPointClass

def rInH : Rec := ⟨((2 : ℚ) / 5), ((2 : ℚ) / 5), ((2 : ℚ) / 5), ((-345994269 : ℚ) / 500000000), ((-117362513 : ℚ) / 200000000), ((-7166998609 : ℚ) / 250000000), ((-895822827 : ℚ) / 31250000)⟩
def rTH : Rec := ⟨((93 : ℚ) / 250), ((93 : ℚ) / 250), ((93 : ℚ) / 250), ((-13958737 : ℚ) / 200000000), ((85118003 : ℚ) / 500000000), ((-25307802999 : ℚ) / 1000000000), ((-25305367041 : ℚ) / 1000000000)⟩
def rPH : Rec := ⟨((93 : ℚ) / 250), ((93 : ℚ) / 250), ((93 : ℚ) / 250), ((13958737 : ℚ) / 200000000), ((85118003 : ℚ) / 500000000), ((-25307802999 : ℚ) / 1000000000), ((-25305367041 : ℚ) / 1000000000)⟩

theorem inside_not_pos : allPos [rInH] = false := by decide +kernel
theorem inside_is_neg : allNeg [rInH] = true := by decide +kernel
theorem tampered_not_pos : allPos [rTH] = false := by decide +kernel
theorem untampered_pos : allPos [rPH] = true := by decide +kernel

end ProgZeroPointClass

#print axioms ProgZeroPointClass.inside_not_pos
#print axioms ProgZeroPointClass.inside_is_neg
#print axioms ProgZeroPointClass.tampered_not_pos
#print axioms ProgZeroPointClass.untampered_pos
