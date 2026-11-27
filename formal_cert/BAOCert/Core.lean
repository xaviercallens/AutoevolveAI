import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.MeasureTheory.Integral.IntervalIntegral.Basic
import Mathlib.MeasureTheory.Integral.IntervalIntegral.IntegrationByParts
import Mathlib.Tactic

/-!
# Certified enclosures of the flat ΛCDM comoving distance

`E Om z = √(Om (1+z)³ + 1 - Om)` (flat ΛCDM, radiation off) and `χ(z) = ∫₀ᶻ dz'/E(z')`.

Method. `1/E` is antitone on `[0, ∞)` for `0 ≤ Om ≤ 1`, so on the grid `xᵢ = i/S` each cell satisfies
`f(x_{i+1})/S ≤ ∫_{xᵢ}^{x_{i+1}} f ≤ f(xᵢ)/S`. An untrusted program supplies integers `loᵢ, hiᵢ`
with `loᵢ² aᵢ ≤ D² b ≤ hiᵢ² aᵢ`, where `A(xᵢ) = aᵢ / b` exactly; the kernel checks them with
`decide +kernel`, and `seg_bounds` lifts the check to bounds on the integral.

Nothing here is trusted except Lean's kernel and Mathlib.
-/

namespace BAOCert

open MeasureTheory Set

/-- Hubble rate in units of `H₀` for flat ΛCDM without radiation. -/
noncomputable def E (Om z : ℝ) : ℝ := Real.sqrt (Om * (1 + z) ^ 3 + (1 - Om))

/-- The integrand of the comoving distance. -/
noncomputable def invE (Om z : ℝ) : ℝ := 1 / E Om z

lemma arg_pos {Om z : ℝ} (h0 : 0 ≤ Om) (h1 : Om ≤ 1) (hz : 0 ≤ z) :
    0 < Om * (1 + z) ^ 3 + (1 - Om) := by
  have h3 : 1 ≤ (1 + z) ^ 3 := one_le_pow₀ (by linarith)
  nlinarith [mul_nonneg h0 (sub_nonneg.2 h3)]

lemma invE_antitoneOn {Om : ℝ} (h0 : 0 ≤ Om) (h1 : Om ≤ 1) : AntitoneOn (invE Om) (Ici 0) := by
  intro x hx y hy hxy
  simp only [mem_Ici] at hx hy
  have hAx := arg_pos h0 h1 hx
  have h3 : (1 + x) ^ 3 ≤ (1 + y) ^ 3 := pow_le_pow_left₀ (by linarith) (by linarith) 3
  have hmono : Om * (1 + x) ^ 3 + (1 - Om) ≤ Om * (1 + y) ^ 3 + (1 - Om) := by nlinarith
  exact one_div_le_one_div_of_le (Real.sqrt_pos.2 hAx) (Real.sqrt_le_sqrt hmono)

lemma le_invE_of {Om x r : ℝ} (hA : 0 < Om * (1 + x) ^ 3 + (1 - Om)) (hr : 0 ≤ r)
    (h : r ^ 2 * (Om * (1 + x) ^ 3 + (1 - Om)) ≤ 1) : r ≤ invE Om x := by
  unfold invE E
  have hs : 0 < Real.sqrt (Om * (1 + x) ^ 3 + (1 - Om)) := Real.sqrt_pos.2 hA
  rw [le_div_iff₀ hs]
  have hsq : (r * Real.sqrt (Om * (1 + x) ^ 3 + (1 - Om))) ^ 2 ≤ 1 := by
    rw [mul_pow, Real.sq_sqrt hA.le]; exact h
  nlinarith [mul_nonneg hr hs.le]

lemma invE_le_of {Om x r : ℝ} (hA : 0 < Om * (1 + x) ^ 3 + (1 - Om)) (hr : 0 ≤ r)
    (h : 1 ≤ r ^ 2 * (Om * (1 + x) ^ 3 + (1 - Om))) : invE Om x ≤ r := by
  unfold invE E
  have hs : 0 < Real.sqrt (Om * (1 + x) ^ 3 + (1 - Om)) := Real.sqrt_pos.2 hA
  rw [div_le_iff₀ hs]
  have hsq : 1 ≤ (r * Real.sqrt (Om * (1 + x) ^ 3 + (1 - Om))) ^ 2 := by
    rw [mul_pow, Real.sq_sqrt hA.le]; exact h
  nlinarith [mul_nonneg hr hs.le]

/-! ## Integer certificate -/

/-- Numerator of `A(i/S)` for `Om = p/q`: `A(i/S) = a p q S i / b q S`. -/
def a (p q S i : ℕ) : ℕ := p * (S + i) ^ 3 + (q - p) * S ^ 3

/-- Common denominator of `A(i/S)`. -/
def b (q S : ℕ) : ℕ := q * S ^ 3

/-- Node check: `lo² a ≤ D² b ≤ hi² a`, i.e. `lo/D ≤ 1/E(i/S) ≤ hi/D`. -/
def nodeOK (p q S D i lo hi : ℕ) : Bool :=
  Nat.ble (lo ^ 2 * a p q S i) (D ^ 2 * b q S) && Nat.ble (D ^ 2 * b q S) (hi ^ 2 * a p q S i)

/-- Checks a table of `(lo, hi)` pairs for consecutive nodes starting at node `i`. -/
def checkFrom (p q S D : ℕ) : ℕ → List (ℕ × ℕ) → Bool
  | _, [] => true
  | i, x :: t => nodeOK p q S D i x.1 x.2 && checkFrom p q S D (i + 1) t

/-- Sum of the lower bounds at the right endpoints of the cells. -/
def lowerSum : List (ℕ × ℕ) → ℕ
  | _ :: y :: rest => y.1 + lowerSum (y :: rest)
  | _ => 0

/-- Sum of the upper bounds at the left endpoints of the cells. -/
def upperSum : List (ℕ × ℕ) → ℕ
  | x :: y :: rest => x.2 + upperSum (y :: rest)
  | _ => 0

lemma A_eq {p q S : ℕ} (i : ℕ) (hpq : p ≤ q) (hq : 0 < q) (hS : 0 < S) :
    ((p : ℝ) / q) * (1 + (i : ℝ) / S) ^ 3 + (1 - (p : ℝ) / q) = (a p q S i : ℝ) / (b q S : ℝ) := by
  have hq' : (q : ℝ) ≠ 0 := by positivity
  have hS' : (S : ℝ) ≠ 0 := by positivity
  unfold a b
  push_cast [Nat.cast_sub hpq]
  field_simp <;> ring

lemma node_bounds {p q S D i lo hi : ℕ} (hpq : p ≤ q) (hq : 0 < q) (hS : 0 < S) (hD : 0 < D)
    (h : nodeOK p q S D i lo hi = true) :
    (lo : ℝ) / D ≤ invE ((p : ℝ) / q) ((i : ℝ) / S) ∧ invE ((p : ℝ) / q) ((i : ℝ) / S) ≤ (hi : ℝ) / D := by
  simp only [nodeOK, Bool.and_eq_true, Nat.ble_eq] at h
  obtain ⟨h1, h2⟩ := h
  have hOm0 : (0 : ℝ) ≤ p / q := by positivity
  have hOm1 : (p : ℝ) / q ≤ 1 := by
    rw [div_le_one (by exact_mod_cast hq)]; exact_mod_cast hpq
  have hx : (0 : ℝ) ≤ (i : ℝ) / S := by positivity
  have hA := arg_pos hOm0 hOm1 hx
  have hb : (0 : ℝ) < (b q S : ℝ) := by unfold b; positivity
  have hDr : (0 : ℝ) < D := by exact_mod_cast hD
  have hDb : (0 : ℝ) < (D : ℝ) ^ 2 * (b q S : ℝ) := mul_pos (pow_pos hDr 2) hb
  constructor
  · apply le_invE_of hA (by positivity)
    rw [A_eq i hpq hq hS, div_pow, div_mul_div_comm, div_le_one hDb]
    exact_mod_cast h1
  · apply invE_le_of hA (by positivity)
    rw [A_eq i hpq hq hS, div_pow, div_mul_div_comm, one_le_div hDb]
    exact_mod_cast h2

/-- One cell: `f((i+1)/S)/S ≤ ∫_{i/S}^{(i+1)/S} f ≤ f(i/S)/S` for antitone `f = 1/E`. -/
lemma cell_bounds {Om : ℝ} (h0 : 0 ≤ Om) (h1 : Om ≤ 1) {S : ℕ} (hS : 0 < S) (i : ℕ) :
    invE Om (((i + 1 : ℕ) : ℝ) / S) / S ≤ ∫ x in ((i : ℝ) / S)..(((i + 1 : ℕ) : ℝ) / S), invE Om x ∧
    ∫ x in ((i : ℝ) / S)..(((i + 1 : ℕ) : ℝ) / S), invE Om x ≤ invE Om ((i : ℝ) / S) / S := by
  have hSr : (0 : ℝ) < S := by exact_mod_cast hS
  have hab : (i : ℝ) / S ≤ ((i + 1 : ℕ) : ℝ) / S := by
    apply div_le_div_of_nonneg_right _ hSr.le; push_cast; linarith
  have hsub : uIcc ((i : ℝ) / S) (((i + 1 : ℕ) : ℝ) / S) ⊆ Ici 0 := by
    intro x hx
    rw [uIcc_of_le hab] at hx
    exact le_trans (by positivity) hx.1
  have hint : IntervalIntegrable (invE Om) volume ((i : ℝ) / S) (((i + 1 : ℕ) : ℝ) / S) :=
    ((invE_antitoneOn h0 h1).mono hsub).intervalIntegrable
  have hlen : ((i + 1 : ℕ) : ℝ) / S - (i : ℝ) / S = 1 / S := by push_cast; ring
  have hmem : ∀ x ∈ Icc ((i : ℝ) / S) (((i + 1 : ℕ) : ℝ) / S),
      invE Om (((i + 1 : ℕ) : ℝ) / S) ≤ invE Om x ∧ invE Om x ≤ invE Om ((i : ℝ) / S) := by
    intro x hx
    have hx0 : x ∈ Ici (0 : ℝ) := le_trans (by positivity) hx.1
    exact ⟨invE_antitoneOn h0 h1 hx0 (le_trans (by positivity) hab) hx.2,
           invE_antitoneOn h0 h1 (by positivity : (0:ℝ) ≤ (i : ℝ) / S) hx0 hx.1⟩
  constructor
  · have := intervalIntegral.integral_mono_on hab intervalIntegrable_const hint (fun x hx => (hmem x hx).1)
    rw [intervalIntegral.integral_const, hlen, smul_eq_mul] at this
    calc invE Om (((i + 1 : ℕ) : ℝ) / S) / S = 1 / S * invE Om (((i + 1 : ℕ) : ℝ) / S) := by ring
      _ ≤ _ := this
  · have := intervalIntegral.integral_mono_on hab hint intervalIntegrable_const (fun x hx => (hmem x hx).2)
    rw [intervalIntegral.integral_const, hlen, smul_eq_mul] at this
    calc _ ≤ 1 / S * invE Om ((i : ℝ) / S) := this
      _ = invE Om ((i : ℝ) / S) / S := by ring

lemma intervalIntegrable_grid {Om : ℝ} (h0 : 0 ≤ Om) (h1 : Om ≤ 1) {S : ℕ} (hS : 0 < S) (i j : ℕ) :
    IntervalIntegrable (invE Om) volume ((i : ℝ) / S) ((j : ℝ) / S) := by
  have hsub : uIcc ((i : ℝ) / S) ((j : ℝ) / S) ⊆ Ici 0 := by
    intro x hx
    have := hx.1
    exact le_trans (le_min (by positivity) (by positivity)) this
  exact ((invE_antitoneOn h0 h1).mono hsub).intervalIntegrable

/-- Main soundness theorem: a checked table starting at node `i₀` encloses the integral over its span. -/
theorem seg_bounds {p q S D : ℕ} (hpq : p ≤ q) (hq : 0 < q) (hS : 0 < S) (hD : 0 < D) :
    ∀ (L : List (ℕ × ℕ)) (i₀ : ℕ), checkFrom p q S D i₀ L = true →
      (lowerSum L : ℝ) / (D * S) ≤
          ∫ x in ((i₀ : ℝ) / S)..(((i₀ + (L.length - 1) : ℕ) : ℝ) / S), invE ((p : ℝ) / q) x ∧
        ∫ x in ((i₀ : ℝ) / S)..(((i₀ + (L.length - 1) : ℕ) : ℝ) / S), invE ((p : ℝ) / q) x ≤
          (upperSum L : ℝ) / (D * S) := by
  have hOm0 : (0 : ℝ) ≤ p / q := by positivity
  have hOm1 : (p : ℝ) / q ≤ 1 := by
    rw [div_le_one (by exact_mod_cast hq)]; exact_mod_cast hpq
  have hSr : (0 : ℝ) < S := by exact_mod_cast hS
  have hDr : (0 : ℝ) < D := by exact_mod_cast hD
  intro L
  induction L with
  | nil => intro i₀ _; simp [lowerSum, upperSum]
  | cons x t ih =>
    intro i₀ hchk
    cases t with
    | nil => simp [lowerSum, upperSum]
    | cons y rest =>
      simp only [checkFrom, Bool.and_eq_true] at hchk
      obtain ⟨hx, hy, hrest2⟩ := hchk
      have hrest : checkFrom p q S D (i₀ + 1) (y :: rest) = true := by
        simp only [checkFrom, Bool.and_eq_true]; exact ⟨hy, hrest2⟩
      obtain ⟨ihl, ihu⟩ := ih (i₀ + 1) hrest
      obtain ⟨hxl, hxu⟩ := node_bounds hpq hq hS hD hx
      obtain ⟨hyl, hyu⟩ := node_bounds hpq hq hS hD hy
      obtain ⟨hcl, hcu⟩ := cell_bounds hOm0 hOm1 hS i₀
      have hend : (i₀ + ((x :: y :: rest).length - 1) : ℕ) = (i₀ + 1) + ((y :: rest).length - 1) := by
        simp only [List.length_cons]; omega
      rw [hend, ← intervalIntegral.integral_add_adjacent_intervals
        (intervalIntegrable_grid hOm0 hOm1 hS i₀ (i₀ + 1))
        (intervalIntegrable_grid hOm0 hOm1 hS (i₀ + 1) _)]
      have hL : ((lowerSum (x :: y :: rest) : ℕ) : ℝ) = (y.1 : ℝ) + (lowerSum (y :: rest) : ℝ) := by
        simp [lowerSum]
      have hU : ((upperSum (x :: y :: rest) : ℕ) : ℝ) = (x.2 : ℝ) + (upperSum (y :: rest) : ℝ) := by
        simp [upperSum]
      rw [hL, hU]
      constructor
      · have e1 : (y.1 : ℝ) / D / S ≤ invE ((p : ℝ) / q) (((i₀ + 1 : ℕ) : ℝ) / S) / S :=
          div_le_div_of_nonneg_right hyl hSr.le
        calc ((y.1 : ℝ) + lowerSum (y :: rest)) / (D * S)
            = (y.1 : ℝ) / D / S + (lowerSum (y :: rest) : ℝ) / (D * S) := by rw [add_div, div_div]
          _ ≤ _ := add_le_add (e1.trans hcl) ihl
      · have e2 : invE ((p : ℝ) / q) ((i₀ : ℝ) / S) / S ≤ (x.2 : ℝ) / D / S :=
          div_le_div_of_nonneg_right hxu hSr.le
        calc _ ≤ (x.2 : ℝ) / D / S + (upperSum (y :: rest) : ℝ) / (D * S) := add_le_add (hcu.trans e2) ihu
          _ = ((x.2 : ℝ) + upperSum (y :: rest)) / (D * S) := by rw [div_div, ← add_div]

/-- The comoving distance in units of `c/H₀`. -/
noncomputable def chi (Om z : ℝ) : ℝ := ∫ x in (0 : ℝ)..z, invE Om x

/-- Corollary for a table starting at node 0 with `n + 1` entries: `χ(n/S)` is enclosed. -/
theorem chi_bounds {p q S D n : ℕ} (hpq : p ≤ q) (hq : 0 < q) (hS : 0 < S) (hD : 0 < D)
    (L : List (ℕ × ℕ)) (hlen : L.length = n + 1) (hchk : checkFrom p q S D 0 L = true) :
    (lowerSum L : ℝ) / (D * S) ≤ chi ((p : ℝ) / q) ((n : ℝ) / S) ∧
      chi ((p : ℝ) / q) ((n : ℝ) / S) ≤ (upperSum L : ℝ) / (D * S) := by
  unfold chi
  have h := seg_bounds hpq hq hS hD L 0 hchk
  rw [hlen] at h
  simp only [Nat.add_sub_cancel, zero_add, Nat.cast_zero, zero_div] at h
  exact h

end BAOCert
