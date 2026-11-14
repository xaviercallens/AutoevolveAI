/-! Kernel throughput benchmark for 144-bit fixed-point interval multiplication (core Lean, no Mathlib). -/

def Q : Int := 2 ^ 144

structure IV where
  u : Int
  v : Int

def fq (a : Int) : Int := a / Q
def cq (a : Int) : Int := -((-a) / Q)

def IV.mul (a b : IV) : IV :=
  let p1 := a.u * b.u
  let p2 := a.u * b.v
  let p3 := a.v * b.u
  let p4 := a.v * b.v
  ⟨fq (min (min p1 p2) (min p3 p4)), cq (max (max p1 p2) (max p3 p4))⟩

def IV.add (a b : IV) : IV := ⟨a.u + b.u, a.v + b.v⟩

def iter : Nat → IV → IV → IV → IV
  | 0, x, _, _ => x
  | n + 1, x, y, c => iter n ((x.mul y).add c) y c

-- y ≈ 0.999..., c ≈ 0.001 so x stays bounded.
def y0 : IV := ⟨Q - Q / 1000 - 1, Q - Q / 1000 + 1⟩
def c0 : IV := ⟨Q / 1000, Q / 1000 + 1⟩

def ok (n : Nat) : Bool := let r := iter n ⟨Q / 2, Q / 2⟩ y0 c0; decide (r.u ≤ r.v) && decide (0 < r.u)

set_option maxRecDepth 100000 in
theorem b1000 : ok 1000 = true := by decide +kernel
set_option maxRecDepth 100000 in
theorem b10000 : ok 10000 = true := by decide +kernel
#print axioms b10000
