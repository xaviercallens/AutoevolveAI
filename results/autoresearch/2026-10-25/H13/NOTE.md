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

## Correction to the wording above (made after compiling; the Lean statements did not change)
U2's second equation is **not the D3 tadpole**. The D3 tadpole is `N_D3 + ½N_flux = 24` (TT (2.3)), and it does
not involve `a` or `b`. U2's equation says that the D3 charge induced by the wrapped 7-branes (`2` for each O7, `1` for each D7)
equals `χ(K3×K3)/24 = 24` of the dual fourfold (TT ll. 164–171, DRS l. 640). The file's `induced_d3_charge_matches_target` states the same equality.
Also, "recovered, not assumed" overstates it: geometry fixes `a = 4`. That the two charge equations force the same value is an
arithmetic consistency check, not a derivation of the geometry. The Lean docstring was corrected to match.

## Human proof
- U1: `n·1 + 4·(−4) = 0` ⇔ `n = 16`.
- U2: `−4a + b = 0` and `2a + b = 24`. Subtract to get `6a = 24`, so `a = 4` and `b = 16`. Conversely, `(4,16)` satisfies both
  (`−16+16 = 0`, `8+16 = 24`). The determinant is `−6 ≠ 0`, so the solution is unique in ℚ, and hence also in ℕ.
- U3: `−4 + f(i) = 0` for each `i` ⇔ `f(i) = 4` for each `i`. Summing gives 16, which is the global condition.
- Negative controls: with one equation dropped, the solution set is a whole line. `b = 4a` gives `(1,4)` and `(4,16)`; `2a + b = 24`
  gives `(0,24)` and `(4,16)`. The global count alone allows any composition of 16 into 4 parts, for example `(16,0,0,0)` and `(4,4,4,4)`.

## Physical meaning and limits
- All of this is integer arithmetic about the library's constants. The Lean statement is Tier A after the verifier; that these are the physical
  charges is Tier L, pinned in `TadpoleCancellation.lean` (Sen hep-th/9605150 l. 242; TT hep-th/0301139 ll. 160–171;
  DRS hep-th/9908088 l. 640; Polchinski hep-th/9611050 eq. (93)).
- The ansatz is narrow: only O7⁻ planes (charge −4) and D7-branes (charge +1). O7⁺ planes, anti-D7s, (p,q)
  7-branes, exotic O-planes, and F-theory away from weak coupling are all outside it. Uniqueness is relative to this ansatz.
- U3's `(16,0,0,0)` is physics, not only a control. D7 positions on `T²/ℤ₂` are moduli, so global cancellation allows
  every distribution. Only local cancellation (constant dilaton, Sen's `SO(8)⁴` point) singles out `(4,4,4,4)`.
- Nothing here concerns flux vacua, supersymmetry or moduli stabilisation. `N_D3` and `N_flux` do not appear.

## Toolchain and compile details
- `lean` v4.34.0-rc2 (LeanMaster's toolchain binary) was run directly with `LEAN_PATH=<LeanMaster>/.lake/build/lib/lean`,
  because `lake --dir <LeanMaster> env lean` hung at 0% CPU. `TadpoleCancellation.olean` (2026-09-19 17:55) is newer than its
  source (2026-09-18 22:42). That file has no imports, so the only dependency is `Init`.
- Attempt 1 (08:03–08:47 UTC) was DISCARDED for infrastructure reasons: the compile was IO-starved on disk 2. A `gcloud storage rsync -r
  /mnt/disks/.../leanmaster` and two sibling `lean` jobs from other sessions were running at the same time (load ≈ 110), and the compile used 0.4 s of CPU in 900 s.
  The proof was never elaborated.
- Attempt 2 (08:48–08:53 UTC) started after warming the page cache (580 MB of the mapped `.olean`s, read sequentially). It took 3 compiles.
  Compile 1 had expected errors: `decide` cannot see through the user `def` Props, and `decide` failed on a goal with a free variable. Both were fixed with
  `unfold`/`show`. Compile 2 returned rc 0. Compile 3 changed docstrings only and also returned rc 0.
- `Autoresearch_Tadpole.lean` contains no planted controls (grep for sorry/admit/native_decide/axiom finds nothing).
  `Autoresearch_Tadpole_controls.lean` is the same file plus `ctl_sorry` and `ctl_axiom`. Both are caught there.
- No LeanMaster file was created or changed.
- Producer ≠ verifier is still pending (an independent recompile and statement audit are needed for Tier A).
