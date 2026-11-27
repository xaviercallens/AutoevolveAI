/-! Kernel cost of the per-point work of `cs()` mode 0 (m = 1 lattice sum, exact Int): norm and Re((2n+k + i√3 k)^6)
numerator for the points of one row n, k ∈ [-256, 256] (513 points), summed (grouping by norm omitted here). -/

def re6 (n k : Int) : Int :=
  let ar := 2 * n + k
  let bi := k
  let ar2 := ar * ar
  let bi2 := bi * bi
  ar2 * ar2 * ar2 - 45 * ar2 * ar2 * bi2 + 135 * ar2 * bi2 * bi2 - 27 * bi2 * bi2 * bi2

def rowSum (n : Int) : Nat → Int → Int
  | 0, acc => acc
  | j + 1, acc => rowSum n j (acc + 2 * re6 n ((j : Int) - 256) + (n * n + n * ((j : Int) - 256) + ((j : Int) - 256) ^ 2))

set_option profiler true
set_option maxRecDepth 100000 in
theorem row100 : rowSum 100 513 0 ≠ 0 := by decide +kernel
set_option maxRecDepth 100000 in
theorem row200 : rowSum 200 513 0 ≠ 0 := by decide +kernel
