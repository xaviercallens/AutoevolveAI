import Programmes.YukawaBccFcc.Basic

/-!
# M3 REJECT control (must FAIL to compile): planted wrong multiplicity `N₇ = 46` (true value 48)
-/

namespace YukawaBccFcc.RejectN7

theorem bad_N7 : YukawaBccFcc.Nc 7 = 46 := by decide +kernel

end YukawaBccFcc.RejectN7
