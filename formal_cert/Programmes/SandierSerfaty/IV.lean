import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic

/-!
# Fixed-point interval arithmetic of the triangular-minimality certificate, in Lean

Proposal 2 (2026-10-26), item A1a. This file transcribes the interval type `IV` of the openai/math certificate
(`verification/core.hpp`, SHA-256 `c7f76596...`): an interval is a pair of integers `(u, v)` read as
`[u / Q, v / Q]` with `Q = 2^144` (`BP = 144`). Products are rounded outward with `floor_q` / `ceil_q`
(here `fq` / `cq`; Lean's `Int` division is Euclidean, which is the floor for the positive divisor `Q`).

Two layers:
* **computation** (`IV.add`, `IV.mul`, `IV.inv`, `IV.rat`, `IV.sqrt`, ...): executable by the kernel
  (`decide +kernel`), written to give the same endpoints as the C++ (checked bit for bit against C++ dumps in
  `Constants.lean`). `IV.mul` takes the min / max of the four endpoint products; the C++ chooses the same two
  products by a nine-way sign case split, so the endpoints coincide (the C++ shortcut for a zero interval also
  returns `[0, 0]`, which is what min / max give).
* **soundness** (`IV.Contains`, `add_sound`, `neg_sound`, `sub_sound`, `mul_sound`, `inv_sound`, `ofInt_sound`,
  `rat_sound`): if real numbers lie in the input intervals, the real result lies in the output interval. These
  are the lemmas through which a kernel-evaluated interval computation becomes a statement about real numbers.

Nothing here is trusted except Lean's kernel and Mathlib.
-/

namespace ProgSandierSerfaty.Cert

/-- `Q = 2^144` (literal, so that the kernel never recomputes the power). -/
def Q : Int := 22300745198530623141535718272648361505980416

theorem Q_eq : Q = 2 ^ 144 := by decide +kernel

theorem Q_pos : 0 < Q := by decide +kernel

/-- An interval `[u / Q, v / Q]` (the C++ `IV`). -/
structure IV where
  u : Int
  v : Int
deriving DecidableEq, Repr

/-- `floor_q`: `⌊a / Q⌋`. -/
def fq (a : Int) : Int := a / Q
/-- `ceil_q`: `⌈a / Q⌉ = -⌊-a / Q⌋`. -/
def cq (a : Int) : Int := -((-a) / Q)

namespace IV

/-- `IV(n)` for an integer `n`: the point `n`. -/
def ofInt (n : Int) : IV := ⟨n * Q, n * Q⟩
def neg (a : IV) : IV := ⟨-a.v, -a.u⟩
def add (a b : IV) : IV := ⟨a.u + b.u, a.v + b.v⟩
def sub (a b : IV) : IV := add a (neg b)
def mul (a b : IV) : IV :=
  ⟨fq (min (min (a.u * b.u) (a.u * b.v)) (min (a.v * b.u) (a.v * b.v))),
   cq (max (max (a.u * b.u) (a.u * b.v)) (max (a.v * b.u) (a.v * b.v)))⟩
/-- `inv` of a positive interval: `[⌊Q²/v⌋, ⌈Q²/u⌉]`. -/
def invPos (a : IV) : IV := ⟨(Q * Q) / a.v, -((-(Q * Q)) / a.u)⟩
/-- The C++ `inv`: positive case, negative case by symmetry; the C++ throws when `0 ∈ a`
(here the junk value `[0,0]`, excluded by the hypotheses of `inv_sound`). -/
def inv (a : IV) : IV :=
  if 0 < a.u then invPos a else if a.v < 0 then neg (invPos (neg a)) else ⟨0, 0⟩
def div (a b : IV) : IV := mul a (inv b)
/-- `rat(n, d)`, `d > 0`: `[⌊nQ/d⌋, ⌈nQ/d⌉]`. -/
def rat (n d : Int) : IV := ⟨(n * Q) / d, -((-(n * Q)) / d)⟩
def hull (a b : IV) : IV := ⟨min a.u b.u, max a.v b.v⟩

/-- Integer square root by Newton's iteration from above (fuel-bounded, structurally recursive, so the
kernel can evaluate it). Used only by the computation layer; its output is compared with the C++ dump. -/
def isqrtIter : Nat → Nat → Nat → Nat
  | 0, _, x => x
  | k + 1, n, x => let y := (x + n / x) / 2; if y < x then isqrtIter k n y else x

def isqrt (n : Nat) : Nat := if n = 0 then 0 else isqrtIter 512 n n

/-- The C++ `sqrt`: `[isqrt(uQ), isqrt(vQ) + 1]` (the C++ throws when `u ≤ 0`). -/
def sqrt (a : IV) : IV := ⟨(isqrt (a.u * Q).toNat : Int), (isqrt (a.v * Q).toNat : Int) + 1⟩

/-! ## Real semantics -/

/-- `x ∈ [u / Q, v / Q]`. -/
def Contains (a : IV) (x : ℝ) : Prop := (a.u : ℝ) / (Q : ℝ) ≤ x ∧ x ≤ (a.v : ℝ) / (Q : ℝ)

lemma Qr_pos : (0 : ℝ) < (Q : ℝ) := by exact_mod_cast Q_pos

lemma contains_iff (a : IV) (x : ℝ) : a.Contains x ↔ (a.u : ℝ) ≤ x * Q ∧ x * Q ≤ (a.v : ℝ) := by
  unfold Contains
  rw [div_le_iff₀ Qr_pos, le_div_iff₀ Qr_pos]

theorem ofInt_sound (n : Int) : (ofInt n).Contains (n : ℝ) := by
  rw [contains_iff]; simp [ofInt]

theorem neg_sound {a : IV} {x : ℝ} (h : a.Contains x) : (neg a).Contains (-x) := by
  rw [contains_iff] at *; simp only [neg, Int.cast_neg]; constructor <;> nlinarith [h.1, h.2]

theorem add_sound {a b : IV} {x y : ℝ} (ha : a.Contains x) (hb : b.Contains y) : (add a b).Contains (x + y) := by
  rw [contains_iff] at *; simp only [add, Int.cast_add]; constructor <;> nlinarith [ha.1, ha.2, hb.1, hb.2]

theorem sub_sound {a b : IV} {x y : ℝ} (ha : a.Contains x) (hb : b.Contains y) : (sub a b).Contains (x - y) := by
  rw [sub_eq_add_neg]; exact add_sound ha (neg_sound hb)

lemma min_le_mul_of_mem {c d y : ℝ} (a : ℝ) (h1 : c ≤ y) (h2 : y ≤ d) : min (a * c) (a * d) ≤ a * y := by
  rcases le_or_gt 0 a with ha | ha
  · exact (min_le_left _ _).trans (mul_le_mul_of_nonneg_left h1 ha)
  · exact (min_le_right _ _).trans (mul_le_mul_of_nonpos_left h2 ha.le)

lemma mul_le_max_of_mem {c d y : ℝ} (a : ℝ) (h1 : c ≤ y) (h2 : y ≤ d) : a * y ≤ max (a * c) (a * d) := by
  rcases le_or_gt 0 a with ha | ha
  · exact (mul_le_mul_of_nonneg_left h2 ha).trans (le_max_right _ _)
  · exact (mul_le_mul_of_nonpos_left h1 ha.le).trans (le_max_left _ _)

/-- Bilinear enclosure: for `x ∈ [a₁, a₂]`, `y ∈ [b₁, b₂]`, `x y` lies between the min and max of the four
endpoint products. -/
lemma bilinear {a₁ a₂ b₁ b₂ x y : ℝ} (hx1 : a₁ ≤ x) (hx2 : x ≤ a₂) (hy1 : b₁ ≤ y) (hy2 : y ≤ b₂) :
    min (min (a₁ * b₁) (a₁ * b₂)) (min (a₂ * b₁) (a₂ * b₂)) ≤ x * y ∧
      x * y ≤ max (max (a₁ * b₁) (a₁ * b₂)) (max (a₂ * b₁) (a₂ * b₂)) := by
  have hl : min (a₁ * y) (a₂ * y) ≤ x * y := by
    rw [mul_comm a₁, mul_comm a₂, mul_comm x]; exact min_le_mul_of_mem y hx1 hx2
  have hu : x * y ≤ max (a₁ * y) (a₂ * y) := by
    rw [mul_comm a₁, mul_comm a₂, mul_comm x]; exact mul_le_max_of_mem y hx1 hx2
  have l1 := min_le_mul_of_mem a₁ hy1 hy2
  have l2 := min_le_mul_of_mem a₂ hy1 hy2
  have u1 := mul_le_max_of_mem a₁ hy1 hy2
  have u2 := mul_le_max_of_mem a₂ hy1 hy2
  constructor
  · refine le_trans ?_ hl
    rcases min_choice (a₁ * y) (a₂ * y) with h | h <;> rw [h]
    · exact (min_le_left _ _).trans l1
    · exact (min_le_right _ _).trans l2
  · refine hu.trans ?_
    rcases max_choice (a₁ * y) (a₂ * y) with h | h <;> rw [h]
    · exact u1.trans (le_max_left _ _)
    · exact u2.trans (le_max_right _ _)

lemma fq_mul_le (m : Int) : ((fq m : Int) : ℝ) * Q ≤ (m : ℝ) := by
  have := Int.ediv_mul_le m (Int.ne_of_gt Q_pos)
  exact_mod_cast this

lemma le_cq_mul (m : Int) : (m : ℝ) ≤ ((cq m : Int) : ℝ) * Q := by
  have := Int.ediv_mul_le (-m) (Int.ne_of_gt Q_pos)
  have h : (m : Int) ≤ cq m * Q := by unfold cq; linarith
  exact_mod_cast h

theorem mul_sound {a b : IV} {x y : ℝ} (ha : a.Contains x) (hb : b.Contains y) : (mul a b).Contains (x * y) := by
  rw [contains_iff] at *
  have q := Qr_pos
  obtain ⟨lo, hi⟩ := bilinear ha.1 ha.2 hb.1 hb.2
  have e : x * Q * (y * Q) = x * y * Q * Q := by ring
  rw [e] at lo hi
  have hlo := fq_mul_le (min (min (a.u * b.u) (a.u * b.v)) (min (a.v * b.u) (a.v * b.v)))
  have hhi := le_cq_mul (max (max (a.u * b.u) (a.u * b.v)) (max (a.v * b.u) (a.v * b.v)))
  push_cast at hlo hhi
  simp only [mul]
  constructor
  · have : ((fq (min (min (a.u * b.u) (a.u * b.v)) (min (a.v * b.u) (a.v * b.v))) : Int) : ℝ) * Q ≤ x * y * Q * Q :=
      hlo.trans lo
    nlinarith
  · have : x * y * Q * Q ≤ ((cq (max (max (a.u * b.u) (a.u * b.v)) (max (a.v * b.u) (a.v * b.v))) : Int) : ℝ) * Q :=
      hi.trans hhi
    nlinarith

theorem invPos_sound {a : IV} {x : ℝ} (hu : 0 < a.u) (ha : a.Contains x) : (invPos a).Contains x⁻¹ := by
  rw [contains_iff] at *
  have q := Qr_pos
  have hu' : (0 : ℝ) < a.u := by exact_mod_cast hu
  have hx : 0 < x * Q := lt_of_lt_of_le hu' ha.1
  have hx0 : 0 < x := by nlinarith
  have hv : 0 < a.v := by have : (a.u : ℝ) ≤ a.v := ha.1.trans ha.2; exact_mod_cast hu'.trans_le this
  have hv' : (0 : ℝ) < a.v := by exact_mod_cast hv
  have h1 := Int.ediv_mul_le (Q * Q) (Int.ne_of_gt hv)
  have h2 := Int.ediv_mul_le (-(Q * Q)) (Int.ne_of_gt hu)
  have h1' : (((Q * Q) / a.v : Int) : ℝ) * a.v ≤ (Q : ℝ) * Q := by exact_mod_cast h1
  have h2' : ((-(Q * Q)) / a.u : Int) * (a.u : ℝ) ≤ -((Q : ℝ) * Q) := by exact_mod_cast h2
  simp only [invPos]
  push_cast
  have hxinv : x⁻¹ * x = 1 := inv_mul_cancel₀ hx0.ne'
  constructor
  · -- ⌊Q²/v⌋ ≤ x⁻¹ Q  ⟸  ⌊Q²/v⌋ v ≤ Q² and x Q ≤ v
    by_contra hc
    push_neg at hc
    have : x⁻¹ * Q * (x * Q) < (((Q * Q) / a.v : Int) : ℝ) * a.v := by
      calc x⁻¹ * Q * (x * Q) < (((Q * Q) / a.v : Int) : ℝ) * (x * Q) := by
            exact mul_lt_mul_of_pos_right hc hx
        _ ≤ (((Q * Q) / a.v : Int) : ℝ) * a.v := by
            apply mul_le_mul_of_nonneg_left ha.2
            have : x⁻¹ * Q ≥ 0 := by positivity
            linarith
    have e : x⁻¹ * Q * (x * Q) = (Q : ℝ) * Q := by rw [show x⁻¹ * Q * (x * Q) = (x⁻¹ * x) * (Q * Q) by ring, hxinv, one_mul]
    linarith
  · by_contra hc
    push_neg at hc
    -- -⌊-Q²/u⌋ < x⁻¹ Q
    have hpos : (0 : ℝ) ≤ -(((-(Q * Q)) / a.u : Int) : ℝ) := by
      have : -((Q : ℝ) * Q) < 0 := by nlinarith
      nlinarith
    have : (Q : ℝ) * Q < x⁻¹ * Q * (x * Q) := by
      calc (Q : ℝ) * Q ≤ -(((-(Q * Q)) / a.u : Int) : ℝ) * a.u := by linarith
        _ ≤ -(((-(Q * Q)) / a.u : Int) : ℝ) * (x * Q) := mul_le_mul_of_nonneg_left ha.1 hpos
        _ < x⁻¹ * Q * (x * Q) := mul_lt_mul_of_pos_right hc hx
    have e : x⁻¹ * Q * (x * Q) = (Q : ℝ) * Q := by rw [show x⁻¹ * Q * (x * Q) = (x⁻¹ * x) * (Q * Q) by ring, hxinv, one_mul]
    linarith

theorem inv_sound {a : IV} {x : ℝ} (h0 : 0 < a.u ∨ a.v < 0) (ha : a.Contains x) : (inv a).Contains x⁻¹ := by
  unfold inv
  rcases h0 with h | h
  · rw [if_pos h]; exact invPos_sound h ha
  · by_cases h' : 0 < a.u
    · rw [if_pos h']; exact invPos_sound h' ha
    · rw [if_neg h', if_pos h]
      have hn : 0 < (neg a).u := by simp [neg]; omega
      have := neg_sound (invPos_sound hn (neg_sound ha))
      rwa [inv_neg, neg_neg] at this

theorem div_sound {a b : IV} {x y : ℝ} (h0 : 0 < b.u ∨ b.v < 0) (ha : a.Contains x) (hb : b.Contains y) :
    (div a b).Contains (x / y) := by
  rw [div_eq_mul_inv]; exact mul_sound ha (inv_sound h0 hb)

theorem rat_sound (n d : Int) (hd : 0 < d) : (rat n d).Contains ((n : ℝ) / d) := by
  rw [contains_iff]
  have hd' : (0 : ℝ) < d := by exact_mod_cast hd
  have h1 := Int.ediv_mul_le (n * Q) (Int.ne_of_gt hd)
  have h2 := Int.ediv_mul_le (-(n * Q)) (Int.ne_of_gt hd)
  have h1' : (((n * Q) / d : Int) : ℝ) * d ≤ n * Q := by exact_mod_cast h1
  have h2' : (((-(n * Q)) / d : Int) : ℝ) * d ≤ -(n * Q) := by exact_mod_cast h2
  simp only [rat]; push_cast
  constructor
  · rw [show (n : ℝ) / d * Q = (n * Q) / d by ring, le_div_iff₀ hd']; exact h1'
  · rw [show (n : ℝ) / d * Q = (n * Q) / d by ring, div_le_iff₀ hd']; linarith

theorem hull_sound_left {a b : IV} {x : ℝ} (ha : a.Contains x) : (hull a b).Contains x := by
  rw [contains_iff] at *; simp only [hull]; push_cast
  exact ⟨(min_le_left _ _).trans ha.1, ha.2.trans (le_max_left _ _)⟩

end IV

end ProgSandierSerfaty.Cert
