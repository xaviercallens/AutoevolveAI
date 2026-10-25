import Mathlib.Tactic

/-!
# Dyadic triangular Hilbert form: product rule and `C* ≥ 3` (H6, autoresearch 2026-10-25)

Finite, integer-valued model of the dyadic triangular Hilbert form of
`results/openai_math/hypotheses/night_2026-10-07/H5/NOTE.md` (conventions checked there against the
upstream openai/math preprint, eq. local-form: `h_I = 1_left - 1_right`, prefactor `2^l` at level `l`,
coupling `F0(x0,x1) F1(x1,x2) F2(x2,x0)`, XOR admissibility, all coarse scales contributing `|T|`).

A cell at resolution `N` is `X N` = `N` bits, most significant first (`X 0 = Unit`,
`X (N+1) = Bool × X N`); an input is `F : X N → X N → ℤ` (an `2^N × 2^N` matrix).
Everything is unnormalised by the cell volume `(2^N)^3 = 8^N`:

* `T N F` = `∑_{x0,x1,x2} F0 x0 x1 * F1 x1 x2 * F2 x2 x0`, written recursively over the top bit;
* `L0 F` = the level-0 Haar term (signs of the top bits);
* `H N F` = `∑_l 2^l ∑_{admissible triples at level l} |∫ ...|`, written recursively: level 0, then
  the four admissible top-bit triples `(b0, b1, b0 xor b1)` with weight 2;
* `S = |T| + H`, and for `±1` inputs (all `L^3` norms equal 1) the ratio is `R = S / 8^N`.

These recursive definitions were checked numerically against the recorded direct implementation and the
recorded exact values (g2: 2, 3/2, 1/2; w4: 5/2; w4 ⊗ w4 at N = 8: 23/8) in
`results/autoresearch/2026-10-25/H6/defs_check.py`.
-/

namespace AutoresearchDyadic

/-- Cells at resolution `n`: `n` bits, most significant first. -/
def X : ℕ → Type
  | 0 => Unit
  | n + 1 => Bool × X n

/-- An input function (a `2^n × 2^n` integer matrix). -/
abbrev Fn (n : ℕ) : Type := X n → X n → ℤ

/-- The `(b, c)` block of a matrix at resolution `n + 1`. -/
def restrict {n : ℕ} (F : Fn (n + 1)) (b c : Bool) : Fn n :=
  fun x y => F ((b, x) : Bool × X n) ((c, y) : Bool × X n)

/-- Sum over `Bool`. -/
def bsum (φ : Bool → ℤ) : ℤ := φ false + φ true

/-- Haar sign: `+1` on the left half (top bit `false`), `-1` on the right half. -/
def sgn (b : Bool) : ℤ := if b then -1 else 1

/-- Unnormalised trilinear integral `∑ F0 x0 x1 * F1 x1 x2 * F2 x2 x0`. -/
def T : (n : ℕ) → Fn n → Fn n → Fn n → ℤ
  | 0, F0, F1, F2 => F0 () () * F1 () () * F2 () ()
  | n + 1, F0, F1, F2 => bsum fun b0 => bsum fun b1 => bsum fun b2 =>
      T n (restrict F0 b0 b1) (restrict F1 b1 b2) (restrict F2 b2 b0)

/-- Unnormalised level-0 Haar integral. -/
def L0 {n : ℕ} (F0 F1 F2 : Fn (n + 1)) : ℤ :=
  bsum fun b0 => bsum fun b1 => bsum fun b2 =>
    sgn b0 * sgn b1 * sgn b2 * T n (restrict F0 b0 b1) (restrict F1 b1 b2) (restrict F2 b2 b0)

/-- Unnormalised Haar part `∑_l 2^l ∑_{admissible I} |∫_I ...|`. -/
def H : (n : ℕ) → Fn n → Fn n → Fn n → ℤ
  | 0, _, _, _ => 0
  | n + 1, F0, F1, F2 => |L0 F0 F1 F2| + 2 * (bsum fun b0 => bsum fun b1 =>
      H n (restrict F0 b0 b1) (restrict F1 b1 (xor b0 b1)) (restrict F2 (xor b0 b1) b0))

/-- Unnormalised form `S = |T| + H`. -/
def S (n : ℕ) (F0 F1 F2 : Fn n) : ℤ := |T n F0 F1 F2| + H n F0 F1 F2

/-- The ratio `S / ∏ ‖F_v‖_3`, valid as such for `±1` inputs (all norms are 1). -/
def R (n : ℕ) (F0 F1 F2 : Fn n) : ℚ := (S n F0 F1 F2 : ℚ) / 8 ^ n

/-- `±1`-valued input. -/
def PM1 {n : ℕ} (F : Fn n) : Prop := ∀ x y, F x y = 1 ∨ F x y = -1

theorem PM1.restrict {n : ℕ} {F : Fn (n + 1)} (h : PM1 F) (b c : Bool) :
    PM1 (AutoresearchDyadic.restrict F b c) := fun x y => h _ _

/-! ## Tensor (Kronecker) product: coarse `f` on the top `n1` bits, fine `g` on the low `n2` bits. -/

/-- Split a cell at resolution `n2 + n1` into its top `n1` bits and low `n2` bits. -/
def split (n2 : ℕ) : (n1 : ℕ) → X (n2 + n1) → X n1 × X n2
  | 0, z => ((), z)
  | n1 + 1, z =>
      let z' : Bool × X (n2 + n1) := z
      (((z'.1, (split n2 n1 z'.2).1) : Bool × X n1), (split n2 n1 z'.2).2)

/-- Kronecker product `f ⊗ g` (as `numpy.kron(f, g)`). -/
def tensor {n1 n2 : ℕ} (f : Fn n1) (g : Fn n2) : Fn (n2 + n1) :=
  fun z w => f (split n2 n1 z).1 (split n2 n1 w).1 * g (split n2 n1 z).2 (split n2 n1 w).2

/-- Pointwise scaling by a constant. -/
def cmul {n : ℕ} (a : ℤ) (G : Fn n) : Fn n := fun x y => a * G x y

theorem restrict_tensor {n1 n2 : ℕ} (f : Fn (n1 + 1)) (g : Fn n2) (b c : Bool) :
    restrict (n := n2 + n1) (tensor (n1 := n1 + 1) f g) b c = tensor (restrict f b c) g := rfl

theorem tensor_zero {n2 : ℕ} (f : Fn 0) (g : Fn n2) : tensor f g = cmul (f () ()) g := rfl

theorem restrict_cmul {n : ℕ} (a : ℤ) (G : Fn (n + 1)) (b c : Bool) :
    restrict (cmul a G) b c = cmul a (restrict G b c) := rfl

theorem PM1.tensor {n1 n2 : ℕ} {f : Fn n1} {g : Fn n2} (hf : PM1 f) (hg : PM1 g) :
    PM1 (AutoresearchDyadic.tensor f g) := by
  intro z w
  unfold AutoresearchDyadic.tensor
  rcases hf (split n2 n1 z).1 (split n2 n1 w).1 with h1 | h1 <;>
    rcases hg (split n2 n1 z).2 (split n2 n1 w).2 with h2 | h2 <;> simp [h1, h2]

/-! ## Homogeneity -/

theorem T_cmul (n : ℕ) : ∀ (a b c : ℤ) (G0 G1 G2 : Fn n),
    T n (cmul a G0) (cmul b G1) (cmul c G2) = a * b * c * T n G0 G1 G2 := by
  induction n with
  | zero => intro a b c G0 G1 G2; simp only [T, cmul]; ring
  | succ n ih =>
    intro a b c G0 G1 G2
    simp only [T, bsum, restrict_cmul, ih]
    ring

theorem L0_cmul {n : ℕ} (a b c : ℤ) (G0 G1 G2 : Fn (n + 1)) :
    L0 (cmul a G0) (cmul b G1) (cmul c G2) = a * b * c * L0 G0 G1 G2 := by
  simp only [L0, bsum, restrict_cmul, T_cmul]
  ring

theorem H_cmul (n : ℕ) : ∀ (a b c : ℤ) (G0 G1 G2 : Fn n),
    H n (cmul a G0) (cmul b G1) (cmul c G2) = |a * b * c| * H n G0 G1 G2 := by
  induction n with
  | zero => intro a b c G0 G1 G2; simp [H]
  | succ n ih =>
    intro a b c G0 G1 G2
    simp only [H, bsum, restrict_cmul, ih, L0_cmul, abs_mul]
    ring

/-! ## The tensor identities -/

theorem T_tensor {n2 : ℕ} (g0 g1 g2 : Fn n2) (n1 : ℕ) : ∀ (f0 f1 f2 : Fn n1),
    T (n2 + n1) (tensor f0 g0) (tensor f1 g1) (tensor f2 g2) = T n1 f0 f1 f2 * T n2 g0 g1 g2 := by
  induction n1 with
  | zero =>
    intro f0 f1 f2
    simp only [tensor_zero]
    show T n2 _ _ _ = _
    rw [T_cmul]
    simp only [T]
  | succ n1 ih =>
    intro f0 f1 f2
    show T (n2 + n1 + 1) (tensor (n1 := n1 + 1) f0 g0) (tensor (n1 := n1 + 1) f1 g1) (tensor (n1 := n1 + 1) f2 g2) = _
    simp only [T, bsum, restrict_tensor, ih]
    ring

theorem L0_tensor {n1 n2 : ℕ} (f0 f1 f2 : Fn (n1 + 1)) (g0 g1 g2 : Fn n2) :
    L0 (n := n2 + n1) (tensor (n1 := n1 + 1) f0 g0) (tensor (n1 := n1 + 1) f1 g1) (tensor (n1 := n1 + 1) f2 g2) = L0 f0 f1 f2 * T n2 g0 g1 g2 := by
  simp only [L0, bsum, restrict_tensor, T_tensor]
  ring

theorem H_tensor {n2 : ℕ} (g0 g1 g2 : Fn n2) (n1 : ℕ) : ∀ (f0 f1 f2 : Fn n1),
    PM1 f0 → PM1 f1 → PM1 f2 →
    H (n2 + n1) (tensor f0 g0) (tensor f1 g1) (tensor f2 g2)
      = 8 ^ n1 * H n2 g0 g1 g2 + |T n2 g0 g1 g2| * H n1 f0 f1 f2 := by
  induction n1 with
  | zero =>
    intro f0 f1 f2 h0 h1 h2
    simp only [tensor_zero]
    show H n2 _ _ _ = _
    rw [H_cmul]
    have habs : |f0 () () * f1 () () * f2 () ()| = 1 := by
      rcases h0 () () with a | a <;> rcases h1 () () with b | b <;> rcases h2 () () with c | c <;>
        simp [a, b, c]
    rw [habs]
    simp [H]
  | succ n1 ih =>
    intro f0 f1 f2 h0 h1 h2
    show H (n2 + n1 + 1) (tensor (n1 := n1 + 1) f0 g0) (tensor (n1 := n1 + 1) f1 g1) (tensor (n1 := n1 + 1) f2 g2) = _
    simp only [H, bsum, restrict_tensor, L0_tensor,
      ih _ _ _ (h0.restrict _ _) (h1.restrict _ _) (h2.restrict _ _), abs_mul]
    ring

/-- Product rule, integer form: `S(f ⊗ g) = 8^{n1} H(g) + |T(g)| S(f)` for `±1` coarse `f`. -/
theorem S_tensor {n1 n2 : ℕ} (f0 f1 f2 : Fn n1) (g0 g1 g2 : Fn n2)
    (h0 : PM1 f0) (h1 : PM1 f1) (h2 : PM1 f2) :
    S (n2 + n1) (tensor f0 g0) (tensor f1 g1) (tensor f2 g2)
      = 8 ^ n1 * H n2 g0 g1 g2 + |T n2 g0 g1 g2| * S n1 f0 f1 f2 := by
  simp only [S, T_tensor, H_tensor g0 g1 g2 n1 f0 f1 f2 h0 h1 h2, abs_mul]
  ring

/-- **Product rule** (NOTE.md §2): for `±1` inputs `f` (resolution `n1`) and `g` (resolution `n2`),
`R(f ⊗ g) = H(g) + |T(g)| · R(f)`, with `H(g) = H n2 g / 8^n2` and `T(g) = T n2 g / 8^n2`
(only `f` needs to be `±1` for the identity itself). -/
theorem product_rule {n1 n2 : ℕ} (f0 f1 f2 : Fn n1) (g0 g1 g2 : Fn n2)
    (h0 : PM1 f0) (h1 : PM1 f1) (h2 : PM1 f2) :
    R (n2 + n1) (tensor f0 g0) (tensor f1 g1) (tensor f2 g2)
      = (H n2 g0 g1 g2 : ℚ) / 8 ^ n2 + (|T n2 g0 g1 g2| : ℚ) / 8 ^ n2 * R n1 f0 f1 f2 := by
  unfold R
  rw [S_tensor f0 f1 f2 g0 g1 g2 h0 h1 h2]
  push_cast
  rw [pow_add]
  field_simp

/-! ## Explicit witness: the exhaustive N = 2 maximiser `g2` (chunk E2_00) -/

/-- Integer index of a cell, most significant bit first. -/
def idx : (n : ℕ) → X n → ℕ
  | 0, _ => 0
  | n + 1, z =>
      let z' : Bool × X n := z
      (if z'.1 then 2 ^ n else 0) + idx n z'.2

/-- Boolean check over all cells. -/
def allX : (n : ℕ) → (X n → Bool) → Bool
  | 0, p => p ()
  | n + 1, p => allX n (fun x => p ((false, x) : Bool × X n)) && allX n (fun x => p ((true, x) : Bool × X n))

theorem allX_spec (n : ℕ) : ∀ (p : X n → Bool), allX n p = true → ∀ x, p x = true := by
  induction n with
  | zero => intro p h x; cases x; exact h
  | succ n ih =>
    intro p h x
    simp only [allX, Bool.and_eq_true] at h
    obtain ⟨b, x'⟩ := (x : Bool × X n)
    cases b
    · exact ih _ h.1 x'
    · exact ih _ h.2 x'

/-- `F` given by a table (rows of the matrix), entries outside the table read as `0`. -/
def ofTable {n : ℕ} (t : List (List ℤ)) : Fn n :=
  fun x y => (t.getD (idx n x) []).getD (idx n y) 0

def g2t0 : List (List ℤ) := [[1, -1, -1, 1], [-1, 1, -1, 1], [-1, -1, 1, 1], [1, 1, 1, 1]]
def g2t1 : List (List ℤ) := [[1, -1, 1, -1], [1, -1, -1, 1], [-1, -1, 1, 1], [1, 1, 1, 1]]
def g2t2 : List (List ℤ) := [[1, 1, -1, 1], [1, 1, 1, -1], [1, -1, 1, 1], [-1, 1, 1, 1]]

def g2 : Fin 3 → Fn 2
  | 0 => ofTable g2t0
  | 1 => ofTable g2t1
  | 2 => ofTable g2t2

def isPM1 (z : ℤ) : Bool := z == 1 || z == -1

theorem PM1_of_check {n : ℕ} (F : Fn n)
    (h : allX n (fun x => allX n (fun y => isPM1 (F x y))) = true) : PM1 F := by
  intro x y
  have h1 := allX_spec n _ h x
  have h2 := allX_spec n _ h1 y
  simp only [isPM1, Bool.or_eq_true, beq_iff_eq] at h2
  exact h2

theorem g2_pm1 (v : Fin 3) : PM1 (g2 v) := by
  fin_cases v
  · exact PM1_of_check _ (by decide)
  · exact PM1_of_check _ (by decide)
  · exact PM1_of_check _ (by decide)

theorem g2_T : T 2 (g2 0) (g2 1) (g2 2) = 32 := by decide

theorem g2_H : H 2 (g2 0) (g2 1) (g2 2) = 96 := by decide

/-- `R(g2) = 2` (recorded: R = 2, H = 3/2, T = 1/2). -/
theorem g2_R : R 2 (g2 0) (g2 1) (g2 2) = 2 := by
  unfold R S
  rw [g2_T, g2_H]
  norm_num

/-! ## Tensor powers and `C* ≥ 3` -/

/-- Resolution of the `r`-fold tensor power of `g2`. -/
def d : ℕ → ℕ
  | 0 => 0
  | r + 1 => 2 + d r

/-- `r`-fold tensor power of `g2` (component `v`), with `g2^{⊗0}` the constant `1` at resolution 0. -/
def gpow (v : Fin 3) : (r : ℕ) → Fn (d r)
  | 0 => fun _ _ => 1
  | r + 1 => tensor (gpow v r) (g2 v)

theorem gpow_pm1 (v : Fin 3) (r : ℕ) : PM1 (gpow v r) := by
  induction r with
  | zero => intro x y; left; rfl
  | succ r ih => exact PM1.tensor ih (g2_pm1 v)

/-- **Tensor-power value** (NOTE.md, Corollary): `R(g2^{⊗r}) = 3 - 2^{1-r}`. -/
theorem gpow_R (r : ℕ) : R (d r) (gpow 0 r) (gpow 1 r) (gpow 2 r) = 3 - 2 / 2 ^ r := by
  induction r with
  | zero =>
    show R 0 (fun _ _ => 1) (fun _ _ => 1) (fun _ _ => 1) = _
    simp [R, S, T, H]
    norm_num
  | succ r ih =>
    show R (2 + d r) (tensor (gpow 0 r) (g2 0)) (tensor (gpow 1 r) (g2 1)) (tensor (gpow 2 r) (g2 2)) = _
    rw [product_rule _ _ _ _ _ _ (gpow_pm1 0 r) (gpow_pm1 1 r) (gpow_pm1 2 r), ih, g2_T, g2_H]
    rw [pow_succ]
    field_simp
    ring

theorem d_four : d 4 = 8 := rfl

/-- The `N = 8` value recorded for `w4 ⊗ w4`: the explicit `±1` input `g2^{⊗4}` at resolution 8 has
ratio `23/8`. -/
theorem gpow4_R : R (d 4) (gpow 0 4) (gpow 1 4) (gpow 2 4) = 23 / 8 := by
  rw [gpow_R]
  norm_num

/-- **`C* ≥ 3`**: for every `c < 3` some `±1` input at some finite resolution has ratio `> c`. -/
theorem sup_ge_three (c : ℚ) (hc : c < 3) :
    ∃ (n : ℕ) (F0 F1 F2 : Fn n), PM1 F0 ∧ PM1 F1 ∧ PM1 F2 ∧ c < R n F0 F1 F2 := by
  obtain ⟨r, hr⟩ := pow_unbounded_of_one_lt (2 / (3 - c)) (by norm_num : (1 : ℚ) < 2)
  refine ⟨d r, gpow 0 r, gpow 1 r, gpow 2 r, gpow_pm1 0 r, gpow_pm1 1 r, gpow_pm1 2 r, ?_⟩
  rw [gpow_R]
  have h3 : 0 < 3 - c := by linarith
  have hp : (0 : ℚ) < 2 ^ r := by positivity
  have : 2 / 2 ^ r < 3 - c := by
    rw [div_lt_iff₀ hp]
    rw [div_lt_iff₀ h3] at hr
    linarith
  linarith

/-! ## Negative control: the product rule without the `|T(g)|` factor is false. -/

theorem wrong_rule_refuted :
    ¬ (∀ (n1 n2 : ℕ) (f0 f1 f2 : Fn n1) (g0 g1 g2 : Fn n2), PM1 f0 → PM1 f1 → PM1 f2 →
        S (n2 + n1) (tensor f0 g0) (tensor f1 g1) (tensor f2 g2)
          = 8 ^ n1 * H n2 g0 g1 g2 + 8 ^ n2 * S n1 f0 f1 f2) := by
  intro h
  have hw := h 2 2 (g2 0) (g2 1) (g2 2) (g2 0) (g2 1) (g2 2) (g2_pm1 0) (g2_pm1 1) (g2_pm1 2)
  rw [S_tensor _ _ _ _ _ _ (g2_pm1 0) (g2_pm1 1) (g2_pm1 2)] at hw
  simp only [S, g2_T, g2_H] at hw
  norm_num at hw

end AutoresearchDyadic

#print axioms AutoresearchDyadic.product_rule
#print axioms AutoresearchDyadic.S_tensor
#print axioms AutoresearchDyadic.g2_R
#print axioms AutoresearchDyadic.gpow_R
#print axioms AutoresearchDyadic.gpow4_R
#print axioms AutoresearchDyadic.sup_ge_three
#print axioms AutoresearchDyadic.wrong_rule_refuted
