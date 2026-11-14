import Programmes.YukawaBccFcc.LemmaA5

namespace YukawaBccFcc

/-! REJECT control (must fail to compile): Lemma A.5 (A.7) cell table with a tampered margin 1/1000. -/
def cellA7bad (j : ℕ) : Bool :=
  decide (0 ≤ C3.getD (j + 1) 0) &&
  decide ((1 / 1000 : ℚ) < polQ (fun _ => 1) Mtab 48 (C3.getD (j + 1) 0) - polQ (fun _ => 1) Ntab 12 (C4.getD j 0)
    - 1 / 10 ^ 18)

theorem cellA7bad_0 : cellA7bad 0 = true := by decide +kernel

end YukawaBccFcc
