import Mathlib.Tactic

/-!
# LR-IND (Proposal 5): scalar inputs of the LRC(10) reduction (Sungkawichai–Trakulthongchai)

Sungkawichai–Trakulthongchai, arXiv 2604.23906 v2, Proposition 2.7 with k = 10: if LRC(9) holds and
J(10, p) = ∅ for every p in a set of primes P with `∏ P ≥ B_10`, then LRC(10) holds, where
(Lemma 2.6 = Rosenfeld Cor. 3, from Malikiosis–Santos–Schymura)

  `B_k = ( C(k+1, 2)^(k-1) / k )^k`,  so  `B_10 = (55^9 / 10)^10`.

This file checks only the scalar inputs, in the kernel:
* `P10` (Table 1, k = 10) has 61 distinct entries, all prime and all `> 110 = k^2 + k`;
* `11 = k + 1` is prime (Prop. 1.4 / 4.4 hypothesis);
* `B_10 ≤ ∏ P10` (exact, as `55^90 ≤ 10^10 * ∏ P10` in ℕ and as a rational inequality).

Not formalised: J(10, p) = ∅ (a Tier C computation), Lemma 2.6, Prop. 2.7, LRC(9).
-/

namespace LonelyRunnerInd

/-- Table 1 of arXiv 2604.23906 v2, row k = 10. -/
def P10 : List ℕ :=
  [127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
   233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349,
   353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463,
   467]

theorem P10_length : P10.length = 61 := by decide

theorem P10_nodup : P10.Nodup := by decide

theorem P10_gt_k2k : ∀ p ∈ P10, 10 ^ 2 + 10 < p := by decide

theorem P10_prime : ∀ p ∈ P10, p.Prime := by
  simp only [P10, List.forall_mem_cons, List.not_mem_nil, IsEmpty.forall_iff, implies_true, and_true]
  norm_num

theorem k_succ_prime : (10 + 1).Prime := by norm_num

/-- `C(11, 2) = 55`. -/
theorem choose_11_2 : Nat.choose 11 2 = 55 := by decide

/-- The product bound in ℕ: `55^90 ≤ 10^10 * ∏ P10`, i.e. `B_10 ≤ ∏ P10`. -/
theorem B10_le_prod_nat : 55 ^ 90 ≤ 10 ^ 10 * P10.prod := by decide

/-- The same bound in ℚ, in the paper's form `((C(11,2))^9 / 10)^10 ≤ ∏ P10`. -/
theorem B10_le_prod : (((Nat.choose 11 2 : ℚ) ^ 9 / 10) ^ 10) ≤ (P10.prod : ℚ) := by
  rw [choose_11_2]
  have h : ((55 : ℚ) ^ 90) ≤ (10 : ℚ) ^ 10 * (P10.prod : ℚ) := by exact_mod_cast B10_le_prod_nat
  rw [div_pow, ← pow_mul, div_le_iff₀ (by positivity)]
  simp only [Nat.cast_ofNat, show 9 * 10 = 90 from rfl]
  linarith [h]

/-- The bound is not vacuous: dropping the largest prime 467 breaks it (the margin is about 5.08 nats, less than ln 467 = 6.15). -/
theorem B10_not_le_prod_without_467 : ¬ (55 ^ 90 ≤ 10 ^ 10 * (P10.prod / 467)) := by decide

end LonelyRunnerInd
