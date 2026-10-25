import Mathlib.Tactic.Ring

/-!
# ALIX / KAL specification: the identities Kernel-Gated Evolution rests on

The engine's codename is ALIX -- Apoptotic checkpoint, Lean-gated, Inheritance
by mutation, eXact arithmetic. The theorem names below are a tribute to the
people whose support carried this long effort; they are also the exact algebraic
facts the Rust crate `kernel_gated_evolution` relies on, stated over `Rat` and
proved so that the dosage machinery and the one-sided checkpoint rest on the
kernel and not on a comment.

Verification contract: compile, then `#print axioms` for every theorem; `sorryAx`
is rejected and the whitelist is {propext, Classical.choice, Quot.sound}.
-/

namespace ANSE.Alix

/-- Dosage through `+`: the locus value `v` enters with coefficient `1`. -/
theorem aurelia_dosage_add (a v : Rat) : a + v = a + 1 * v := by ring

/-- Dosage through `-` (right operand): the coefficient is `-1`. This is the fact
that makes a transplant into the right of a minus invert its contribution. -/
theorem alexis_dosage_sub (a v : Rat) : a - v = a + (-1) * v := by ring

/-- Dosage through `*`: the coefficient is the sibling's value `s`. -/
theorem ilene_dosage_mul (s v : Rat) : s * v = 0 + s * v := by ring

/-- The backward pass composes multiplicatively: an upstream coefficient `B` on a
product with sibling `s` becomes `B * s` on the locus. -/
theorem kal_dosage_chain (A B s v : Rat) : A + B * (s * v) = A + (B * s) * v := by ring

/-- Required value. If the expression is `A + B * v` and `B ≠ 0`, replacing the
locus value by `v + (want - (A + B * v)) * B⁻¹` makes the expression equal
`want`. This is the identity `v* = v + (want - out)/B` the crate verifies on
tens of thousands of (locus, point) pairs; here it is proved for all of them. -/
theorem xav_required_value (A B v want : Rat) (hB : B ≠ 0) :
    A + B * (v + (want - (A + B * v)) * B⁻¹) = want := by
  have h1 : B * B⁻¹ = 1 := mul_inv_cancel₀ hB
  calc A + B * (v + (want - (A + B * v)) * B⁻¹)
      = A + B * v + (want - (A + B * v)) * (B * B⁻¹) := by ring
    _ = want := by rw [h1]; ring

/-- The checkpoint is one-sided. A single disagreement refutes universal
equality, so refusing a candidate on one sample point can never refuse a
provable one. (Agreement at a point proves nothing, which is why survivors still
face the kernel.) -/
theorem alix_checkpoint_refutes {α β : Type} (f g : α → β) (x : α) (h : f x ≠ g x) :
    ¬ (∀ y, f y = g y) :=
  fun hall => h (hall x)

end ANSE.Alix

#print axioms ANSE.Alix.aurelia_dosage_add
#print axioms ANSE.Alix.alexis_dosage_sub
#print axioms ANSE.Alix.ilene_dosage_mul
#print axioms ANSE.Alix.kal_dosage_chain
#print axioms ANSE.Alix.xav_required_value
#print axioms ANSE.Alix.alix_checkpoint_refutes
