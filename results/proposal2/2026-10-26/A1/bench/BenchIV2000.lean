import Programmes.SandierSerfaty.IV
open ProgSandierSerfaty.Cert ProgSandierSerfaty.Cert.IV

def bx0 : IV := ⟨Q / 2, Q / 2 + 7⟩
def by0 : IV := ⟨Q - Q / 1000 - 1, Q - Q / 1000 + 1⟩
def bz0 : IV := ⟨3 * Q + 11, 3 * Q + 13⟩

def bone (i : Nat) : Bool :=
  let x : IV := ⟨bx0.u + (i : Int) * 12345678901234567, bx0.v + (i : Int) * 12345678901234567⟩
  let r := div (mul (mul (mul (mul x by0) by0) by0) by0) bz0
  decide (r.u ≤ r.v)

def ball : Nat → Bool
  | 0 => true
  | n + 1 => bone n && ball n

set_option maxRecDepth 1000000 in
theorem bench_2000 : ball 2000 = true := by decide +kernel
