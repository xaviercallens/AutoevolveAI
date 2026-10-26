/-! Variant: explicit Nat.rec loop, literal Q, Int-only comparison via Int.decLe avoided (use Nat-level). -/

def Q : Int := 22300745198530623141535718272648361505980416

structure IV where
  u : Int
  v : Int

def fq (a : Int) : Int := a / Q
def cq (a : Int) : Int := -((-a) / Q)

-- min/max via Bool comparisons
@[inline] def imin (a b : Int) : Int := if a ≤ b then a else b
@[inline] def imax (a b : Int) : Int := if a ≤ b then b else a

def IV.mul (a b : IV) : IV :=
  let p1 := a.u * b.u
  let p2 := a.u * b.v
  let p3 := a.v * b.u
  let p4 := a.v * b.v
  ⟨fq (imin (imin p1 p2) (imin p3 p4)), cq (imax (imax p1 p2) (imax p3 p4))⟩

def IV.add (a b : IV) : IV := ⟨a.u + b.u, a.v + b.v⟩

def y0 : IV := ⟨Q - Q / 1000 - 1, Q - Q / 1000 + 1⟩
def c0 : IV := ⟨Q / 1000, Q / 1000 + 1⟩

def step (x : IV) : IV := (x.mul y0).add c0

def iterR (n : Nat) (x : IV) : IV :=
  Nat.rec (motive := fun _ => IV → IV) (fun x => x) (fun _ f x => f (step x)) n x

def ok (n : Nat) : Bool := let r := iterR n ⟨Q / 2, Q / 2⟩; decide (r.u ≤ r.v) && decide (0 < r.u)

theorem b10000 : ok 10000 = true := by decide +kernel
