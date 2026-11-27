import Programmes.YukawaBccFcc.LemmaA5

/-!
# M3 reject-control witnesses (must COMPILE): the kernel evaluates the tampered checks to `false`

These show that `RejectCell.lean`, `RejectChain.lean` and `RejectN7.lean` fail because the checked statement is false,
not because evaluation got stuck.
-/

namespace YukawaBccFcc.RejectWitness

open YukawaBccFcc

def cellA7bad (j : ℕ) : Bool :=
  decide (0 ≤ C3.getD (j + 1) 0) &&
  decide ((1 / 1000 : ℚ) < polQ (fun _ => 1) Mtab 48 (C3.getD (j + 1) 0) - polQ (fun _ => 1) Ntab 12 (C4.getD j 0)
    - 1 / 10 ^ 18)

theorem cellA7bad_0_false : cellA7bad 0 = false := by decide +kernel

def C1bad : List ℚ := C1.set 500 (C1.getD 500 0 * 101 / 100)

theorem bad_chain_false : chainLo s1 C1bad = false := by decide +kernel

theorem N7_is_48 : Nc 7 = 48 := by decide +kernel

theorem N7_ne_46 : Nc 7 ≠ 46 := by decide +kernel

end YukawaBccFcc.RejectWitness
