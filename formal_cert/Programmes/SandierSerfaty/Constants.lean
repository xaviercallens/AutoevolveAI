import Programmes.SandierSerfaty.IV
import Mathlib.Analysis.SpecialFunctions.Log.Deriv
import Mathlib.Analysis.SpecialFunctions.Complex.Arctan
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Arctan
import Mathlib.Analysis.SpecificLimits.Basic

/-!
# Stage `init_constants` of the triangular-minimality certificate, kernel-checked

The C++ stage `init_constants()` (`verification/core.hpp`) produces five intervals: `ln2`, `pi`, `p`, `R`, `a`.

* **Level L1 (re-execution).** `ln2Comp`, `piComp`, `pComp`, `RComp`, `aComp` transcribe the C++ loops
  (200-term `atanh(1/3)` series for `log 2`, Machin's formula with 150 terms per arctangent for `π`,
  `p = √(2/√3)/2`, `R = 2p/√3`, `a = 2p`) with the interval operations of `IV.lean`. The theorems `*_comp_eq`
  show, by kernel evaluation, that they give exactly the integer endpoints printed by the C++ binary
  (dump driver `results/proposal2/2026-10-26/A1/cpp/dump_driver.cpp`, unmodified corpus headers).
* **Level L2 (real statement).** `log_two_mem`, `pi_mem`, `p_mem`, `R_mem`, `a_mem`: the real numbers
  `log 2`, `π`, `√(2/√3)/2`, `2(√(2/√3)/2)/√3`, `√(2/√3)` lie in the C++ intervals. These are the manuscript's
  enclosures (comp:logarithm), (comp:pi) and the lattice constants `p`, `R₀`, `a`. They are proved from Mathlib
  (`Real.abs_log_sub_add_sum_range_le`, `Real.hasSum_arctan`, `Real.four_mul_arctan_inv_5_sub_arctan_inv_239`,
  `p⁴ = 1/12`) plus a kernel-decided rational comparison, independently of the C++ algorithm: the L2 proof checks
  the C++ *output*, not its program.
-/

namespace ProgSandierSerfaty.Cert

open IV

/-! ## L1: transcription of `init_constants` -/

def oneI : IV := ofInt 1
def zeroI : IV := ofInt 0

/-- `for i < 200: acc += vv/(2i+1); vv = vv/9`. -/
def ln2Loop : Nat → Nat → IV → IV → IV
  | 0, _, _, acc => acc
  | k + 1, i, vv, acc => ln2Loop k (i + 1) (div vv (ofInt 9)) (add acc (div vv (ofInt (2 * (i : Int) + 1))))

/-- `ln2 = 2*acc + IV(-1,1)` with `vv = one/3`. -/
def ln2Comp : IV := add (mul (ofInt 2) (ln2Loop 200 0 (div oneI (ofInt 3)) zeroI)) ⟨-1, 1⟩

/-- `for j < 150: ac += (±1)*term/(2j+1); term = term/(q*q)`. -/
def atanLoop (q : Int) : Nat → Nat → IV → IV → IV
  | 0, _, _, ac => ac
  | k + 1, j, term, ac =>
    atanLoop q k (j + 1) (div term (ofInt (q * q)))
      (add ac (div (mul (ofInt (if j % 2 = 1 then -1 else 1)) term) (ofInt (2 * (j : Int) + 1))))

def atanComp (q : Int) : IV := add (atanLoop q 150 0 (div oneI (ofInt q)) zeroI) ⟨-2, 2⟩

/-- `pi = 0; pi += 16*ac(5); pi += -4*ac(239)`. -/
def piComp : IV := add (add zeroI (mul (ofInt 16) (atanComp 5))) (mul (ofInt (-4)) (atanComp 239))

def pComp : IV := div (IV.sqrt (div (ofInt 2) (IV.sqrt (rat 3 1)))) (ofInt 2)
def RComp : IV := div (mul (ofInt 2) pComp) (IV.sqrt (rat 3 1))
def aComp : IV := mul (ofInt 2) pComp

/-! The C++ endpoints (dump of the unmodified certificate code). -/

def ln2C : IV := ⟨15457698658747239244624307340191628289589443, 15457698658747239244624307340191628289589853⟩
def piC : IV := ⟨70059857285281660787732012935536363654389216, 70059857285281660787732012935536363654392368⟩
def pC : IV := ⟨11981855123799615759427419310922444945649341, 11981855123799615759427419310922444945649343⟩
def RC : IV := ⟨13835454562233609797780846941716875314304477, 13835454562233609797780846941716875314304482⟩
def aC : IV := ⟨23963710247599231518854838621844889891298682, 23963710247599231518854838621844889891298686⟩

set_option maxRecDepth 100000 in
theorem ln2_comp_eq : ln2Comp = ln2C := by decide +kernel
set_option maxRecDepth 100000 in
theorem pi_comp_eq : piComp = piC := by decide +kernel
set_option maxRecDepth 100000 in
theorem p_comp_eq : pComp = pC := by decide +kernel
set_option maxRecDepth 100000 in
theorem R_comp_eq : RComp = RC := by decide +kernel
set_option maxRecDepth 100000 in
theorem a_comp_eq : aComp = aC := by decide +kernel

/-! ## L2: the real numbers lie in the C++ intervals -/

/-- Partial sums `∑_{i<n} (1/2)^(i+1)/(i+1)` of `-log(1 - 1/2)`. -/
def lnS : ℕ → ℚ
  | 0 => 0
  | n + 1 => lnS n + (1 / 2 : ℚ) ^ (n + 1) / (n + 1)

lemma lnS_cast (n : ℕ) : ((lnS n : ℚ) : ℝ) = ∑ i ∈ Finset.range n, (1 / 2 : ℝ) ^ (i + 1) / (i + 1) := by
  induction n with
  | zero => simp [lnS]
  | succ n ih => rw [Finset.sum_range_succ, ← ih]; simp only [lnS]; push_cast; ring

lemma contains_of_rat {a : IV} {x : ℝ} {lo hi : ℚ} (h1 : ((a.u : ℚ) / (Q : ℚ)) ≤ lo) (h2 : hi ≤ (a.v : ℚ) / (Q : ℚ))
    (hx1 : (lo : ℝ) ≤ x) (hx2 : x ≤ (hi : ℝ)) : a.Contains x := by
  unfold IV.Contains
  constructor
  · have : (((a.u : ℚ) / (Q : ℚ) : ℚ) : ℝ) ≤ (lo : ℝ) := by exact_mod_cast h1
    push_cast at this; linarith
  · have : ((hi : ℚ) : ℝ) ≤ (((a.v : ℚ) / (Q : ℚ) : ℚ) : ℝ) := by exact_mod_cast h2
    push_cast at this; linarith

theorem lnS_check : ((ln2C.u : ℚ) / (Q : ℚ)) ≤ lnS 160 - (1 / 2) ^ 160 ∧
    lnS 160 + (1 / 2) ^ 160 ≤ (ln2C.v : ℚ) / (Q : ℚ) := by decide +kernel

/-- (comp:logarithm): `log 2 ∈ ln2`. -/
theorem log_two_mem : ln2C.Contains (Real.log 2) := by
  have h := Real.abs_log_sub_add_sum_range_le (x := 1 / 2) (by norm_num [abs_of_pos]) 160
  rw [← lnS_cast] at h
  have hl : Real.log (1 - 1 / 2) = -Real.log 2 := by
    rw [show (1 : ℝ) - 1 / 2 = 2⁻¹ by norm_num, Real.log_inv]
  rw [hl, show |(1 / 2 : ℝ)| = 1 / 2 by norm_num [abs_of_pos]] at h
  have he : (1 / 2 : ℝ) ^ (160 + 1) / (1 - 1 / 2) = (((1 / 2 : ℚ) ^ 160 : ℚ) : ℝ) := by push_cast; ring
  rw [he] at h
  obtain ⟨h1, h2⟩ := abs_le.mp h
  refine contains_of_rat lnS_check.1 lnS_check.2 ?_ ?_ <;> push_cast <;> linarith

/-- Partial sums of the arctangent series. -/
def atS (x : ℚ) : ℕ → ℚ
  | 0 => 0
  | n + 1 => atS x n + (-1) ^ n * x ^ (2 * n + 1) / (2 * n + 1)

lemma atS_cast (x : ℚ) (n : ℕ) : ((atS x n : ℚ) : ℝ) =
    ∑ i ∈ Finset.range n, (-1 : ℝ) ^ i * (x : ℝ) ^ (2 * i + 1) / ((2 * i + 1 : ℕ) : ℝ) := by
  induction n with
  | zero => simp [atS]
  | succ n ih => rw [Finset.sum_range_succ, ← ih]; simp only [atS]; push_cast; ring

/-- Geometric tail bound for the arctangent series on `0 ≤ x < 1`. -/
lemma arctan_tail {x : ℝ} (h0 : 0 ≤ x) (h1 : x < 1) (N : ℕ) :
    |Real.arctan x - ∑ i ∈ Finset.range N, (-1 : ℝ) ^ i * x ^ (2 * i + 1) / ((2 * i + 1 : ℕ) : ℝ)| ≤
      x ^ (2 * N + 1) * (1 - x ^ 2)⁻¹ := by
  have hs := Real.hasSum_arctan (x := x) (by rw [Real.norm_eq_abs, abs_of_nonneg h0]; exact h1)
  have ht := (hasSum_nat_add_iff' N).mpr hs
  have hx2 : x ^ 2 < 1 := by nlinarith
  have hg : HasSum (fun n : ℕ => x ^ (2 * N + 1) * (x ^ 2) ^ n) (x ^ (2 * N + 1) * (1 - x ^ 2)⁻¹) :=
    (hasSum_geometric_of_lt_one (by positivity) hx2).mul_left _
  have hb : ∀ n : ℕ, |(-1 : ℝ) ^ (n + N) * x ^ (2 * (n + N) + 1) / ((2 * (n + N) + 1 : ℕ) : ℝ)| ≤
      x ^ (2 * N + 1) * (x ^ 2) ^ n := by
    intro n
    rw [abs_div, abs_mul, abs_pow, abs_neg, abs_one, one_pow, one_mul, abs_of_nonneg (pow_nonneg h0 _),
      Nat.abs_cast]
    have hd : (1 : ℝ) ≤ ((2 * (n + N) + 1 : ℕ) : ℝ) := by exact_mod_cast Nat.succ_le_succ (Nat.zero_le _)
    calc x ^ (2 * (n + N) + 1) / ((2 * (n + N) + 1 : ℕ) : ℝ) ≤ x ^ (2 * (n + N) + 1) :=
          div_le_self (pow_nonneg h0 _) hd
      _ = x ^ (2 * N + 1) * (x ^ 2) ^ n := by rw [← pow_mul, ← pow_add]; ring_nf
  rw [abs_le]
  constructor
  · have := hasSum_le (fun n => neg_le_of_abs_le (hb n)) hg.neg ht
    linarith
  · have := hasSum_le (fun n => (le_abs_self _).trans (hb n)) ht hg
    linarith

def e5 : ℚ := (1 / 5) ^ 301 * (1 - (1 / 5) ^ 2)⁻¹
def e239 : ℚ := (1 / 239) ^ 301 * (1 - (1 / 239) ^ 2)⁻¹

theorem pi_check : ((piC.u : ℚ) / (Q : ℚ)) ≤ 16 * (atS (1 / 5) 150 - e5) - 4 * (atS (1 / 239) 150 + e239) ∧
    16 * (atS (1 / 5) 150 + e5) - 4 * (atS (1 / 239) 150 - e239) ≤ (piC.v : ℚ) / (Q : ℚ) := by decide +kernel

/-- (comp:pi): `π ∈ pi`. -/
theorem pi_mem : piC.Contains Real.pi := by
  have hM := Real.four_mul_arctan_inv_5_sub_arctan_inv_239
  have h5 := arctan_tail (x := ((1 / 5 : ℚ) : ℝ)) (by norm_num) (by norm_num) 150
  have h239 := arctan_tail (x := ((1 / 239 : ℚ) : ℝ)) (by norm_num) (by norm_num) 150
  rw [← atS_cast] at h5 h239
  have c5 : ((1 / 5 : ℚ) : ℝ) = (5 : ℝ)⁻¹ := by norm_num
  have c239 : ((1 / 239 : ℚ) : ℝ) = (239 : ℝ)⁻¹ := by norm_num
  have ce5 : ((1 / 5 : ℚ) : ℝ) ^ (2 * 150 + 1) * (1 - ((1 / 5 : ℚ) : ℝ) ^ 2)⁻¹ = ((e5 : ℚ) : ℝ) := by
    simp only [e5]; push_cast; ring
  have ce239 : ((1 / 239 : ℚ) : ℝ) ^ (2 * 150 + 1) * (1 - ((1 / 239 : ℚ) : ℝ) ^ 2)⁻¹ = ((e239 : ℚ) : ℝ) := by
    simp only [e239]; push_cast; ring
  rw [ce5] at h5
  rw [ce239] at h239
  rw [c5] at h5
  rw [c239] at h239
  obtain ⟨a1, a2⟩ := abs_le.mp h5
  obtain ⟨b1, b2⟩ := abs_le.mp h239
  have hpi : Real.pi = 16 * Real.arctan 5⁻¹ - 4 * Real.arctan 239⁻¹ := by linarith
  refine contains_of_rat pi_check.1 pi_check.2 ?_ ?_ <;> push_cast <;> rw [hpi] <;> linarith

/-! ### `p`, `R₀`, `a` via fourth powers -/

lemma mem_of_pow4 {x lo hi : ℝ} (hx : 0 ≤ x) (hlo : 0 ≤ lo) (hhi : 0 ≤ hi)
    (h1 : lo ^ 4 ≤ x ^ 4) (h2 : x ^ 4 ≤ hi ^ 4) : lo ≤ x ∧ x ≤ hi :=
  ⟨(pow_le_pow_iff_left₀ hlo hx (by norm_num)).mp h1, (pow_le_pow_iff_left₀ hx hhi (by norm_num)).mp h2⟩

lemma contains_of_pow4 {a : IV} {x : ℝ} {c : ℚ} (hx : 0 ≤ x) (hx4 : x ^ 4 = (c : ℝ))
    (hchk : 0 ≤ (a.u : ℚ) / (Q : ℚ) ∧ ((a.u : ℚ) / (Q : ℚ)) ^ 4 ≤ c ∧ c ≤ ((a.v : ℚ) / (Q : ℚ)) ^ 4 ∧
      0 ≤ (a.v : ℚ) / (Q : ℚ)) :
    a.Contains x := by
  obtain ⟨h0, h1, h2, h3⟩ := hchk
  have h0' : (0 : ℝ) ≤ (a.u : ℝ) / (Q : ℝ) := by exact_mod_cast h0
  have h1' : ((a.u : ℝ) / (Q : ℝ)) ^ 4 ≤ (c : ℝ) := by exact_mod_cast h1
  have h2' : (c : ℝ) ≤ ((a.v : ℝ) / (Q : ℝ)) ^ 4 := by exact_mod_cast h2
  have h3' : (0 : ℝ) ≤ (a.v : ℝ) / (Q : ℝ) := by exact_mod_cast h3
  exact mem_of_pow4 hx h0' h3' (by rw [hx4]; exact h1') (by rw [hx4]; exact h2')

/-- `√(2/√3)`, the scale of the covolume-one triangular lattice (`ProgSandierSerfaty.triScale`). -/
noncomputable def tri : ℝ := Real.sqrt (2 / Real.sqrt 3)

lemma s3_sq : Real.sqrt 3 ^ 2 = 3 := Real.sq_sqrt (by norm_num)
lemma s3_pos : 0 < Real.sqrt 3 := Real.sqrt_pos.2 (by norm_num)
lemma tri_sq : tri ^ 2 = 2 / Real.sqrt 3 := Real.sq_sqrt (div_nonneg (by norm_num) s3_pos.le)
lemma tri_nonneg : 0 ≤ tri := Real.sqrt_nonneg _
lemma tri_pow4 : tri ^ 4 = 4 / 3 := by
  rw [show tri ^ 4 = (tri ^ 2) ^ 2 by ring, tri_sq, div_pow, s3_sq]; norm_num

theorem p_check : 0 ≤ (pC.u : ℚ) / (Q : ℚ) ∧ ((pC.u : ℚ) / (Q : ℚ)) ^ 4 ≤ 1 / 12 ∧
    1 / 12 ≤ ((pC.v : ℚ) / (Q : ℚ)) ^ 4 ∧ 0 ≤ (pC.v : ℚ) / (Q : ℚ) := by decide +kernel
theorem R_check : 0 ≤ (RC.u : ℚ) / (Q : ℚ) ∧ ((RC.u : ℚ) / (Q : ℚ)) ^ 4 ≤ 4 / 27 ∧
    4 / 27 ≤ ((RC.v : ℚ) / (Q : ℚ)) ^ 4 ∧ 0 ≤ (RC.v : ℚ) / (Q : ℚ) := by decide +kernel
theorem a_check : 0 ≤ (aC.u : ℚ) / (Q : ℚ) ∧ ((aC.u : ℚ) / (Q : ℚ)) ^ 4 ≤ 4 / 3 ∧
    4 / 3 ≤ ((aC.v : ℚ) / (Q : ℚ)) ^ 4 ∧ 0 ≤ (aC.v : ℚ) / (Q : ℚ) := by decide +kernel

/-- `p = √(2/√3)/2` (apothem of the hexagonal Voronoi cell) lies in the C++ interval `p`. -/
theorem p_mem : pC.Contains (tri / 2) :=
  contains_of_pow4 (by have := tri_nonneg; positivity)
    (by rw [div_pow, tri_pow4]; push_cast; norm_num) p_check

/-- `R₀ = 2p/√3` (circumradius of the hexagonal cell) lies in the C++ interval `R`. -/
theorem R_mem : RC.Contains (2 * (tri / 2) / Real.sqrt 3) :=
  contains_of_pow4 (by have := tri_nonneg; have := s3_pos; positivity)
    (by
      rw [show 2 * (tri / 2) / Real.sqrt 3 = tri / Real.sqrt 3 by ring, div_pow, tri_pow4,
        show Real.sqrt 3 ^ 4 = (Real.sqrt 3 ^ 2) ^ 2 by ring, s3_sq]; push_cast; norm_num) R_check

/-- `a = 2p = √(2/√3)` (nearest-neighbour distance) lies in the C++ interval `a`. -/
theorem a_mem : aC.Contains tri :=
  contains_of_pow4 tri_nonneg (by rw [tri_pow4]; push_cast; norm_num) a_check

end ProgSandierSerfaty.Cert
