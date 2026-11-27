import Autoresearch.DyadicHilbert

/-!
# In-kernel definition check for H6: the recorded N = 4 witness `w4`

`w4t0..w4t2` are `sign(best_inputs_N4.npz)` (results/openai_math/hypotheses/H5/best_inputs_N4.npz,
`np.where(x >= 0, 1, -1)`), the committed N = 4 witness whose exact ratio was recorded as 5/2 with
(H, T) = (9/4, 1/4) in results/openai_math/hypotheses/night_2026-10-07/H5/verify_tensor.json.
Evaluating the Lean definitions on it by `decide` (kernel reduction only, no compiled-code evaluation) reproduces those
numbers: T = -1024 = -(1/4)·8^4, H = 9216 = (9/4)·8^4, R = 5/2.
A second check evaluates `S 4 (g2 ⊗ g2)` directly by `decide` (10240 = (5/2)·8^4), independently of the
product rule, which predicts the same value.
-/

namespace AutoresearchDyadic

def w4t0 : List (List ℤ) := [[1, -1, 1, -1, 1, 1, -1, 1, 1, -1, 1, 1, 1, -1, 1, 1], [1, -1, -1, 1, -1, -1, -1, 1, 1, -1, -1, -1, -1, 1, 1, 1], [1, 1, -1, -1, -1, 1, 1, 1, -1, -1, 1, -1, -1, -1, -1, 1], [-1, -1, -1, -1, -1, 1, -1, -1, 1, 1, 1, -1, -1, -1, 1, -1], [-1, -1, 1, 1, 1, -1, -1, -1, -1, -1, 1, -1, -1, -1, -1, 1], [-1, -1, -1, -1, -1, 1, -1, -1, -1, -1, -1, 1, 1, 1, -1, 1], [-1, 1, 1, -1, 1, 1, 1, -1, 1, -1, -1, -1, -1, 1, 1, 1], [1, -1, 1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1, 1, -1, -1], [1, -1, 1, -1, -1, -1, 1, -1, -1, 1, -1, -1, 1, -1, 1, 1], [-1, 1, 1, -1, -1, -1, -1, 1, 1, -1, -1, -1, 1, -1, -1, -1], [1, 1, -1, -1, 1, -1, -1, -1, 1, 1, -1, 1, -1, -1, -1, 1], [-1, -1, -1, -1, 1, -1, 1, 1, -1, -1, -1, 1, -1, -1, 1, -1], [1, 1, -1, -1, 1, -1, -1, -1, -1, -1, 1, -1, 1, 1, 1, -1], [1, 1, 1, 1, -1, 1, -1, -1, -1, -1, -1, 1, -1, -1, 1, -1], [-1, 1, 1, -1, -1, -1, -1, 1, -1, 1, 1, 1, -1, 1, 1, 1], [1, -1, 1, -1, -1, -1, 1, -1, 1, -1, 1, 1, -1, 1, -1, -1]]
def w4t1 : List (List ℤ) := [[-1, -1, 1, -1, 1, 1, -1, -1, 1, 1, -1, 1, 1, 1, -1, 1], [-1, -1, -1, 1, -1, -1, -1, -1, 1, 1, 1, -1, -1, -1, -1, 1], [1, -1, 1, 1, 1, -1, -1, 1, -1, 1, -1, -1, 1, -1, 1, 1], [-1, 1, 1, 1, 1, -1, 1, -1, 1, -1, -1, -1, 1, -1, -1, -1], [-1, 1, -1, -1, -1, 1, 1, -1, -1, 1, -1, -1, 1, -1, 1, 1], [-1, 1, 1, 1, 1, -1, 1, -1, -1, 1, 1, 1, -1, 1, 1, 1], [1, 1, 1, -1, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, -1, 1], [1, 1, -1, 1, -1, -1, 1, 1, 1, 1, -1, 1, 1, 1, -1, 1], [1, 1, 1, -1, -1, -1, -1, -1, 1, 1, 1, -1, 1, 1, 1, -1], [1, 1, -1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, -1, 1, -1], [1, -1, -1, -1, 1, -1, 1, -1, 1, -1, -1, -1, -1, 1, 1, 1], [1, -1, 1, 1, -1, 1, 1, -1, 1, -1, 1, 1, 1, -1, 1, 1], [1, -1, 1, 1, -1, 1, 1, -1, -1, 1, -1, -1, -1, 1, -1, -1], [-1, 1, 1, 1, -1, 1, -1, 1, 1, -1, -1, -1, -1, 1, 1, 1], [1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, 1, -1, -1, -1, 1], [-1, -1, 1, -1, -1, -1, 1, 1, 1, 1, -1, 1, -1, -1, 1, -1]]
def w4t2 : List (List ℤ) := [[-1, 1, 1, -1, 1, 1, 1, 1, -1, -1, 1, -1, 1, 1, -1, -1], [1, -1, 1, -1, 1, 1, -1, -1, 1, 1, 1, -1, 1, 1, 1, 1], [-1, -1, 1, 1, 1, -1, -1, 1, -1, 1, 1, 1, 1, -1, 1, -1], [1, 1, 1, 1, 1, -1, 1, -1, 1, -1, 1, 1, 1, -1, -1, 1], [1, 1, -1, -1, -1, 1, 1, -1, -1, 1, 1, 1, 1, -1, 1, -1], [1, 1, 1, 1, 1, -1, 1, -1, -1, 1, -1, -1, -1, 1, 1, -1], [-1, 1, -1, 1, -1, -1, 1, 1, 1, 1, 1, -1, 1, 1, 1, 1], [1, -1, -1, 1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, -1, -1], [1, -1, -1, 1, 1, 1, 1, 1, 1, 1, -1, 1, 1, 1, -1, -1], [-1, 1, -1, 1, 1, 1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1], [1, 1, -1, -1, 1, -1, -1, 1, 1, -1, -1, -1, 1, -1, 1, -1], [-1, -1, -1, -1, 1, -1, 1, -1, -1, 1, -1, -1, 1, -1, -1, 1], [-1, -1, 1, 1, -1, 1, 1, -1, 1, -1, -1, -1, 1, -1, 1, -1], [-1, -1, -1, -1, 1, -1, 1, -1, 1, -1, 1, 1, -1, 1, 1, -1], [-1, 1, 1, -1, -1, -1, -1, -1, 1, 1, -1, 1, 1, 1, -1, -1], [-1, 1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, -1, -1, -1]]

theorem w4_pm1_0 : PM1 (n := 4) (ofTable w4t0) := PM1_of_check _ (by decide)
theorem w4_pm1_1 : PM1 (n := 4) (ofTable w4t1) := PM1_of_check _ (by decide)
theorem w4_pm1_2 : PM1 (n := 4) (ofTable w4t2) := PM1_of_check _ (by decide)

theorem w4_T : T 4 (ofTable w4t0) (ofTable w4t1) (ofTable w4t2) = -1024 := by decide

theorem w4_H : H 4 (ofTable w4t0) (ofTable w4t1) (ofTable w4t2) = 9216 := by decide

/-- The recorded N = 4 witness has ratio exactly 5/2 under the Lean definitions. -/
theorem w4_R : R 4 (ofTable w4t0) (ofTable w4t1) (ofTable w4t2) = 5 / 2 := by
  unfold R S
  rw [w4_T, w4_H]
  norm_num

/-- Direct kernel evaluation of `S(g2 ⊗ g2)` (no product rule): 10240 = (5/2)·8^4. -/
theorem g2g2_S_direct : S (2 + 2) (tensor (g2 0) (g2 0)) (tensor (g2 1) (g2 1)) (tensor (g2 2) (g2 2)) = 10240 := by
  decide

/-- The product rule gives the same value. -/
theorem g2g2_S_rule : S (2 + 2) (tensor (g2 0) (g2 0)) (tensor (g2 1) (g2 1)) (tensor (g2 2) (g2 2)) = 10240 := by
  rw [S_tensor _ _ _ _ _ _ (g2_pm1 0) (g2_pm1 1) (g2_pm1 2)]
  simp only [S, g2_T, g2_H]
  norm_num

end AutoresearchDyadic

#print axioms AutoresearchDyadic.w4_pm1_0
#print axioms AutoresearchDyadic.w4_R
#print axioms AutoresearchDyadic.g2g2_S_direct
#print axioms AutoresearchDyadic.g2g2_S_rule
