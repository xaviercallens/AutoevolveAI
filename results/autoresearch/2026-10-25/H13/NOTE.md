# H13 — Tadpole uniqueness (LeanMaster NEXT_DIRECTIONS D2)

## Statement chosen (written before the first attempt, 2026-10-25 08:03 UTC)

D2 says: "Uniqueness of `16 × (+1) + 4 × (−4) = 0` under the geometric constraints is finite arithmetic. Extend
`TadpoleCancellation.lean`." The workflow `.claude/workflows/tadpole-uniqueness.js` asks for "the only integer
solution" of the budget, quantifying over the numbers of planes/branes, with the geometric constraints.

This is ambiguous: with the O7 charge `−4` and the plane count 4 fixed, "uniqueness of `n = 16`" for
`n·1 + 4·(−4) = 0` is a one-line linear equation and says little. I therefore prove three precise statements,
all phrased with the existing definitions of `TadpoleCancellation.lean` (imported, not modified), so the
constants are exactly the library's:

**U1 (global seven-brane count).** For `n : ℕ`, `n · chargeD7Brane + totalO7Charge = 0 ↔ n = numD7Branes` (= 16).

**U2 (both tadpoles fix the geometry; the main statement).** For `a b : ℕ` (number of O7⁻ planes, number of
D7-branes), the two conditions
- seven-brane tadpole `a · chargeO7Minus + b · chargeD7Brane = 0` (i.e. `b = 4a`), and
- induced D3 charge equals the budget `a · d3ChargePerO7 + b · d3ChargePerD7 = d3TadpoleTarget` (i.e. `2a + b = 24`)

hold **iff** `a = numO7Planes ∧ b = numD7Branes` (`a = 4, b = 16`). So the plane count 4, which the file takes
from geometry (fixed points of the reflection of `T²`), is *recovered* from the two charge conditions; the
geometric value is then a consistency check, not an input. I also state the version with the geometric
constraint `a = 2²` as a hypothesis, which reduces to U1.

**U3 (local distribution).** For a distribution `f : Fin 4 → ℕ` of D7-branes over the 4 O7-planes, local
cancellation at every plane `chargeO7Minus + f i · chargeD7Brane = 0` holds iff `f = fun _ => 4` (the
`SO(8)⁴` point). Local cancellation implies the global one.

**Negative controls (hypothesis dropped → uniqueness fails, two distinct solutions exhibited):**
- U2 without the D3 condition: `(a,b) = (1,4)` and `(4,16)` both cancel the seven-brane tadpole.
- U2 without the seven-brane condition: `(0,24)` and `(4,16)` both meet the D3 budget.
- U3 with only global cancellation (`∑ f i = 16`): `(16,0,0,0)` and `(4,4,4,4)` both satisfy it.

Why this choice: U2 is the only reading that is both true and non-trivial with the library's own constants
(it uses two independent equations from two different sources, Sen / TT ll.160–171), and U3 is the precise form of
"under the geometric constraints" for the brane positions. All are integer arithmetic (Tier A for the Lean
statement); that these are the physical charges is Tier L (pins in the imported file).
