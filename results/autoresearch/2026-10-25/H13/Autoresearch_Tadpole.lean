/-
Autoresearch H13 (2026-10-25): tadpole uniqueness, LeanMaster `docs/NEXT_DIRECTIONS.md` D2.

New file; it imports `TadpoleCancellation.lean` unchanged and uses its constants (`chargeO7Minus = −4`,
`chargeD7Brane = 1`, `d3ChargePerO7 = 2`, `d3ChargePerD7 = 1`, `d3TadpoleTarget = 24`, `numO7Planes = 4`,
`numD7Branes = 16`). Every statement is integer arithmetic (Tier A for the Lean statement). That these numbers
are the physical charges of `K3 × T²/ℤ₂` is Tier L (pins in the imported file: Sen hep-th/9605150, Tripathy–Trivedi
hep-th/0301139, Dasgupta–Rajesh–Sethi hep-th/9908088, Polchinski hep-th/9611050).
-/
import StringTheoryFoundation.StringTheory.TadpoleCancellation

namespace StringTheory.Foundation.StringTheory.TadpoleCancellation.Autoresearch

open StringTheory.Foundation.StringTheory.TadpoleCancellation

/-- Seven-brane (`C₈`) tadpole for `a` O7⁻-planes and `b` D7-branes. -/
def SevenBraneTadpole (a b : Nat) : Prop :=
  (a : Int) * chargeO7Minus + (b : Int) * chargeD7Brane = 0

/-- Induced D3 charge of `a` O7-planes and `b` D7-branes wrapped on K3 equals the budget `χ(K3×K3)/24`. -/
def D3Budget (a b : Nat) : Prop :=
  (a : Int) * d3ChargePerO7 + (b : Int) * d3ChargePerD7 = d3TadpoleTarget

/-- **U1.** With the 4 O7⁻-planes fixed, `n` D7-branes cancel the seven-brane tadpole iff `n = 16`. -/
theorem d7_count_unique (n : Nat) :
    (n : Int) * chargeD7Brane + totalO7Charge = 0 ↔ n = numD7Branes := by
  simp only [chargeD7Brane, totalO7Charge, numO7Planes, chargeO7Minus, numD7Branes]
  omega

/-- **U2 (main).** The seven-brane tadpole and the matching of the 7-branes' induced D3 charge to
`χ(K3×K3)/24 = 24` together force `(a, b) = (4, 16)`. This is not the D3 tadpole `N_D3 + ½N_flux = 24` (which
does not involve `a, b`). The plane count `4 = 2²` is fixed by geometry (fixed points of the reflection of `T²`);
agreement with the value forced here is an arithmetic consistency check, not a derivation of the geometry. -/
theorem tadpole_pair_unique (a b : Nat) :
    SevenBraneTadpole a b ∧ D3Budget a b ↔ a = numO7Planes ∧ b = numD7Branes := by
  simp only [SevenBraneTadpole, D3Budget, chargeO7Minus, chargeD7Brane, d3ChargePerO7, d3ChargePerD7,
    d3TadpoleTarget, k3EulerChar, d3ChargePerD7, numO7Planes, numD7Branes]
  omega

/-- U2 with the geometric constraint `a = 2²` as a hypothesis: the seven-brane tadpole alone then fixes `b`. -/
theorem tadpole_unique_given_geometry (a b : Nat) (hgeom : a = 2 ^ 2) :
    SevenBraneTadpole a b ↔ b = numD7Branes := by
  subst hgeom
  simp only [SevenBraneTadpole, chargeO7Minus, chargeD7Brane, numD7Branes]
  omega

/-- The library's configuration satisfies both conditions (non-vacuity of U2). -/
theorem tadpole_pair_exists : SevenBraneTadpole numO7Planes numD7Branes ∧ D3Budget numO7Planes numD7Branes :=
  (tadpole_pair_unique _ _).2 ⟨rfl, rfl⟩

/-- Local cancellation of a distribution `f` of D7-branes over the four O7-planes. -/
def LocallyCancelled (f : Fin 4 → Nat) : Prop :=
  ∀ i, chargeO7Minus + (f i : Int) * chargeD7Brane = 0

/-- Global count for a distribution over the four planes. -/
def GloballyCancelled (f : Fin 4 → Nat) : Prop :=
  f 0 + f 1 + f 2 + f 3 = numD7Branes

/-- **U3.** Local cancellation at every O7-plane holds iff four D7-branes sit on each plane (`SO(8)⁴`). -/
theorem local_distribution_unique (f : Fin 4 → Nat) :
    LocallyCancelled f ↔ f = fun _ => 4 := by
  constructor
  · intro h
    funext i
    have hi := h i
    simp only [chargeO7Minus, chargeD7Brane] at hi
    omega
  · rintro rfl i
    show chargeO7Minus + ((4 : Nat) : Int) * chargeD7Brane = 0
    decide

/-- Local cancellation implies the global count. -/
theorem local_implies_global (f : Fin 4 → Nat) (h : LocallyCancelled f) : GloballyCancelled f := by
  rw [(local_distribution_unique f).1 h]
  unfold GloballyCancelled
  decide

/-! ### Negative controls: drop one hypothesis and uniqueness fails (two distinct solutions). -/

theorem ctl_neg_no_d3 :
    SevenBraneTadpole 1 4 ∧ SevenBraneTadpole 4 16 ∧ (1, 4) ≠ (4, 16) := by
  unfold SevenBraneTadpole
  decide

theorem ctl_neg_no_sevenbrane :
    D3Budget 0 24 ∧ D3Budget 4 16 ∧ (0, 24) ≠ (4, 16) := by
  unfold D3Budget
  decide

theorem ctl_neg_global_only :
    GloballyCancelled (fun i => if i = 0 then 16 else 0) ∧ GloballyCancelled (fun _ => 4) ∧
      ((fun i => if i = 0 then 16 else 0) : Fin 4 → Nat) ≠ (fun _ => 4) := by
  refine ⟨by unfold GloballyCancelled; decide, by unfold GloballyCancelled; decide, ?_⟩
  intro h
  exact absurd (congrFun h 0) (by decide)

end StringTheory.Foundation.StringTheory.TadpoleCancellation.Autoresearch

#print axioms StringTheory.Foundation.StringTheory.TadpoleCancellation.Autoresearch.d7_count_unique
#print axioms StringTheory.Foundation.StringTheory.TadpoleCancellation.Autoresearch.tadpole_pair_unique
#print axioms StringTheory.Foundation.StringTheory.TadpoleCancellation.Autoresearch.tadpole_unique_given_geometry
#print axioms StringTheory.Foundation.StringTheory.TadpoleCancellation.Autoresearch.tadpole_pair_exists
#print axioms StringTheory.Foundation.StringTheory.TadpoleCancellation.Autoresearch.local_distribution_unique
#print axioms StringTheory.Foundation.StringTheory.TadpoleCancellation.Autoresearch.local_implies_global
#print axioms StringTheory.Foundation.StringTheory.TadpoleCancellation.Autoresearch.ctl_neg_no_d3
#print axioms StringTheory.Foundation.StringTheory.TadpoleCancellation.Autoresearch.ctl_neg_no_sevenbrane
#print axioms StringTheory.Foundation.StringTheory.TadpoleCancellation.Autoresearch.ctl_neg_global_only
