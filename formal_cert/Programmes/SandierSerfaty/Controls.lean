import Programmes.SandierSerfaty.Asserts
import Programmes.SandierSerfaty.Constants
import Programmes.SandierSerfaty.CalcKPilot
import Programmes.SandierSerfaty.SignedEndpoints

/-!
# Planted controls for the A1 port (never import this file)

Negative controls, each an HONEST kernel-checked theorem that a planted (perturbed) stage is false, so the
positive theorems are not vacuous:

* `ctl_ln2_199_ne`, `ctl_pi_noslack_ne` (stage `init_constants`, L1): 199 instead of 200 `atanh` terms, resp. Machin
  without the `[-2,2]/Q` remainder slack, do NOT reproduce the C++ endpoints.
* `ctl_pi_shift_false` (L2): moving the lower endpoint of `π` up by `2^100` ulps (`≈ 5.7e-14`) makes the rational
  enclosure check false.
* `ctl_pair_false`: the printed pair `(120, 162)` of `gmin-factor` changed to `(121, 162)`.
* `ctl_gmf_121_false`: `gmin - factor ≥ 1.21e-5` (record value `1.20e-5`).
* `ctl_erdrop_x2_false`: the negative-part assertion with the Lipschitz allowance doubled
  (`drneg + 2 er_drop + K < 0`), the arithmetic analogue of P1's S1-neg variant B.
* `ctl_det_false`: Hessian determinant `≥ 0.0087` (record `0.0086252`).
* `ctl_G_eight_to_four`: in the calcK pilot, the linear-interpolation remainder `H²/8` of `lookup` replaced by `H²/4`
  gives a G value different from the C++ one (the Lean transcription is sensitive to that constant).
* `ctl_signed_without_sum_false` (A1b): without `α + β > 0` the conclusion of `signed_endpoints` is false (G ≡ 1,
  K = -1, α = β = -π/4), while `ctl_signed_hyps` shows that this `G` satisfies every other hypothesis.

Planted cheats that only the axiom audit catches: `ctl_sorry_pi`, `ctl_axiom_pi` "prove" the shifted-`π` claim.
-/

namespace ProgSandierSerfaty.Cert.Controls

open ProgSandierSerfaty.Cert ProgSandierSerfaty.Cert.IV ProgSandierSerfaty.Reduction

set_option maxRecDepth 100000 in
theorem ctl_ln2_199_ne : add (mul (ofInt 2) (ln2Loop 199 0 (div oneI (ofInt 3)) zeroI)) ⟨-1, 1⟩ ≠ ln2C := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem ctl_pi_noslack_ne :
    add (add zeroI (mul (ofInt 16) (atanLoop 5 150 0 (div oneI (ofInt 5)) zeroI)))
      (mul (ofInt (-4)) (atanLoop 239 150 0 (div oneI (ofInt 239)) zeroI)) ≠ piC := by
  decide +kernel

theorem ctl_pi_shift_false :
    ¬ ((((piC.u + 2 ^ 100 : Int) : ℚ) / (Q : ℚ)) ≤ 16 * (atS (1 / 5) 150 - e5) - 4 * (atS (1 / 239) 150 + e239)) := by
  decide +kernel

theorem ctl_pair_false : coarse gmfC ≠ (121, 162) := by decide +kernel

theorem ctl_gmf_121_false : ¬ (121 * Q ≤ 10000000 * gmfC.u) := by decide +kernel

theorem ctl_erdrop_x2_false : ¬ ((add (add drnegC (mul (ofInt 2) erdropC)) KC).v < 0) := by decide +kernel

theorem ctl_det_false : ¬ (87 * Q ≤ 10000 * detC.u) := by decide +kernel

/-- `cellVal` with the interpolation remainder `H²/4` instead of `H²/8` (planted perturbed constant). -/
def cellVal4 (eps T : IV) (c : Cell) : Option (IV × IV) :=
  let H := sub c.t1 c.t0
  let aa := div (sub T c.t0) H
  let xu := max 0 aa.u
  let xv := min Q aa.v
  if xv < xu then none else
    let X : IV := ⟨xu, xv⟩
    let fv := add c.f0 (mul X (sub c.f1 c.f0))
    let ev := add c.e0 (mul X (sub c.e1 c.e0))
    let er := div (mul H H) (ofInt 4)
    let err := mul (absI c.c2) er
    let fv := add fv ⟨-err.v, err.v⟩
    let err2 := mul (absI c.c5) er
    let ev := add ev ⟨-err2.v, err2.v⟩
    some (add fv eps, add ev eps)

def lookupV4 (eps T : IV) : List Cell → Option (IV × IV)
  | [] => none
  | c :: cs => match cellVal4 eps T c, lookupV4 eps T cs with
    | none, r => r
    | some x, none => some x
    | some x, some y => some (hull2 x y)

def Gs4 (lam mu eps d s : IV) (cs : List Cell) : Option IV :=
  let t2 := add (mul d d) (mul s s)
  let t := IV.sqrt t2
  match lookupV4 eps t cs with
  | none => none
  | some (f, e) =>
    let f := sub (sub f (div (mul lam t2) (ofInt 2))) mu
    let A := div d t2
    let B := div (mul (neg s) s) (mul d t2)
    some (add (mul A f) (mul B e))

set_option maxRecDepth 100000 in
theorem ctl_G_eight_to_four :
    Gs4 pilot_lam pilot_mu pilot_eps pilot_p (calcK_s 0) calcK_G0_cells ≠ some calcK_G0_expected := by
  decide +kernel

/-- The constant kernel `G ≡ 1` (even, locally integrable, no negative part). -/
def one2 : ℝ → ℝ → ℝ := fun _ _ => 1

lemma gPrim_one (d x : ℝ) : gPrim one2 d x = x := by
  simp [gPrim, one2]

theorem ctl_signed_hyps :
    (∀ d : ℝ, 1 ≤ d → ∀ s : ℝ, one2 d (-s) = one2 d s) ∧
    (∀ d : ℝ, 1 ≤ d → ∀ a b : ℝ, IntervalIntegrable (one2 d) MeasureTheory.volume a b) ∧
    (∀ d : ℝ, 1 ≤ d → ∀ x : ℝ, 0 ≤ x → (-1 : ℝ) ≤ 2 * gPrim one2 d x) ∧
    (∀ d : ℝ, 1 ≤ d → ∫⁻ s in Set.Ioi (0 : ℝ), ENNReal.ofReal (-one2 d s) ≤ ENNReal.ofReal (-(-1 : ℝ))) := by
  refine ⟨fun _ _ _ => rfl, fun _ _ a b => intervalIntegrable_const, fun d _ x hx => ?_, fun _ _ => ?_⟩
  · rw [gPrim_one]; linarith
  · simp [one2, ENNReal.ofReal_of_nonpos (show (-1 : ℝ) ≤ 0 by norm_num)]

theorem ctl_signed_without_sum_false :
    ¬ (∀ α β : ℝ, |α| < Real.pi / 2 → |β| < Real.pi / 2 →
      (-1 : ℝ) ≤ gPrim one2 1 (1 * Real.tan α) + gPrim one2 1 (1 * Real.tan β)) := by
  intro h
  have hpi := Real.pi_pos
  have hα : |(-(Real.pi / 4))| < Real.pi / 2 := by
    rw [abs_neg, abs_of_pos (by positivity)]; linarith
  have := h _ _ hα hα
  simp only [gPrim_one, Real.tan_neg, Real.tan_pi_div_four] at this
  linarith

/-! Planted cheats (caught only by `#print axioms`). -/

theorem ctl_sorry_pi : (((piC.u + 2 ^ 100 : Int) : ℚ) / (Q : ℚ)) ≤ 16 * (atS (1 / 5) 150 - e5) - 4 * (atS (1 / 239) 150 + e239) :=
  sorry

axiom ctl_cheat : False

theorem ctl_axiom_pi : (((piC.u + 2 ^ 100 : Int) : ℚ) / (Q : ℚ)) ≤ 16 * (atS (1 / 5) 150 - e5) - 4 * (atS (1 / 239) 150 + e239) :=
  ctl_cheat.elim

end ProgSandierSerfaty.Cert.Controls

#print axioms ProgSandierSerfaty.Cert.Controls.ctl_ln2_199_ne
#print axioms ProgSandierSerfaty.Cert.Controls.ctl_pi_noslack_ne
#print axioms ProgSandierSerfaty.Cert.Controls.ctl_pi_shift_false
#print axioms ProgSandierSerfaty.Cert.Controls.ctl_pair_false
#print axioms ProgSandierSerfaty.Cert.Controls.ctl_gmf_121_false
#print axioms ProgSandierSerfaty.Cert.Controls.ctl_erdrop_x2_false
#print axioms ProgSandierSerfaty.Cert.Controls.ctl_det_false
#print axioms ProgSandierSerfaty.Cert.Controls.ctl_G_eight_to_four
#print axioms ProgSandierSerfaty.Cert.Controls.ctl_signed_hyps
#print axioms ProgSandierSerfaty.Cert.Controls.ctl_signed_without_sum_false
#print axioms ProgSandierSerfaty.Cert.Controls.ctl_sorry_pi
#print axioms ProgSandierSerfaty.Cert.Controls.ctl_axiom_pi
