/-! Kernel cost of the Newton integer square root used by IV.sqrt (start x = n) vs a log2-seeded start. -/

def isqrtIter : Nat → Nat → Nat → Nat
  | 0, _, x => x
  | k + 1, n, x => let y := (x + n / x) / 2; if y < x then isqrtIter k n y else x

def isqrtA (n : Nat) : Nat := if n = 0 then 0 else isqrtIter 512 n n
def isqrtB (n : Nat) : Nat := if n = 0 then 0 else isqrtIter 512 n (2 ^ (Nat.log2 n / 2 + 1))

def base : Nat := 2 ^ 290 + 12345678901234567890123

def allA : Nat → Bool
  | 0 => true
  | k + 1 => decide (isqrtA (base + k * 1000003) * isqrtA (base + k * 1000003) ≤ base + k * 1000003) && allA k

def allB : Nat → Bool
  | 0 => true
  | k + 1 => decide (isqrtB (base + k * 1000003) * isqrtB (base + k * 1000003) ≤ base + k * 1000003) && allB k

set_option profiler true
set_option maxRecDepth 100000 in
theorem tA : allA 200 = true := by decide +kernel
set_option maxRecDepth 100000 in
theorem tB : allB 200 = true := by decide +kernel
theorem tAB : isqrtA base = isqrtB base := by decide +kernel
