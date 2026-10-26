/-! Variant: N independent interval multiplications (no data dependence between steps). -/

def Q : Int := 22300745198530623141535718272648361505980416

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

def y0 : IV := ⟨Q - Q / 1000 - 1, Q - Q / 1000 + 1⟩

def one (i : Nat) : Bool :=
  let x : IV := ⟨Q / 2 + (i : Int) * 12345678901234567, Q / 2 + (i : Int) * 12345678901234567 + 7⟩
  let r := (((x.mul y0).mul y0).mul y0).mul y0
  decide (r.u ≤ r.v)

def allUpTo : Nat → Bool
  | 0 => true
  | n + 1 => one n && allUpTo n

set_option maxRecDepth 100000 in
theorem b2500 : allUpTo 2500 = true := by decide +kernel
