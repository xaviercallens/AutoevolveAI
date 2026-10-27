import Programmes.YukawaBccFcc.Chains

/-!
# M3 REJECT control (must FAIL to compile): tampered table entry

Entry 500 of the FCC lower chain `C1` is raised by 1 % (it would then over-estimate `exp(-π a² (1 + 500/10⁴))`).
The kernel chain check must reject the tampered table.
-/

namespace YukawaBccFcc.RejectChain

open YukawaBccFcc

def C1bad : List ℚ := C1.set 500 (C1.getD 500 0 * 101 / 100)

theorem bad_chain : chainLo s1 C1bad = true := by decide +kernel

end YukawaBccFcc.RejectChain
