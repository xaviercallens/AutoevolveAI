# H13 verification (independent verifier, producer != verifier), 2026-10-25

**VERDICT: ACCEPT_WITH_CORRECTIONS** (Lean statements are kernel-checked; the physics reading of U2 needs narrowing)

## Recompile evidence
- Verbatim copy (`sha256 2bcc4cd2...fa62`, identical to `H13/Autoresearch_Tadpole.lean`) compiled with the LeanMaster
  toolchain binary `leanprover--lean4---v4.34.0-rc2/bin/lean`, `LEAN_PATH=<disk2>/leanmaster/lake-v434/build/lib/lean:<rc2>/lib/lean`
  (same as NOTE.md; `.lake` of LeanMaster symlinks to `lake-v434`), `taskset -c 4,5`, page cache warmed first: **rc 0**, no errors.
- Own `#print axioms` (appended to a scratch copy, outside the repo):
  `d7_count_unique`, `tadpole_pair_unique`: [propext, Classical.choice, Quot.sound]; `local_distribution_unique`: [propext, Quot.sound].
  All within the whitelist. The other 6 declarations match the producer's `compile_clean.log`.
- Planted `theorem planted_sorry ... := by sorry` in the same scratch file: shows `[sorryAx]` and a `declaration uses sorry`
  warning, **while the file still exits rc 0**. The audit catches what the exit code alone does not.
- Grep of the clean file for sorry/admit/native_decide/axiom: no match.
- Imported `TadpoleCancellation.olean` (2026-09-19 17:55) is newer than the source (2026-09-18 22:42); the source has no imports.

## Statement adequacy
- Constants checked in the kernel (verifier `example ... := by decide`): `chargeO7Minus = -4`, `chargeD7Brane = 1`,
  `d3ChargePerO7 = 2`, `d3ChargePerD7 = 1`, `d3TadpoleTarget = 24`, `numO7Planes = 4`, `numD7Branes = 16`, `k3EulerChar = 24`.
  They match NOTE.md, the imported file's docstrings and pinned text (Sen l. 242; TT ll. 160-171, read; DRS l. 640, read:
  "The anomaly chi/24 = 24").
- Verifier lemma: `D3Budget a b <-> 2a + b = 24` (unfolded, omega), and U2 also holds over `Int`
  (`-4a + b = 0 /\ 2a + b = 24 <-> (a,b) = (4,16)`). So U2 is a 2x2 linear system with determinant -6. It does not use ℕ.
  The result is honest about being integer arithmetic (NOTE.md, docstring, result.json all say Tier A for the Lean statement only).
- **Is `2a + b = 24` a physical constraint?** TT ll. 164-168 give 2 units per O7 and 1 per D7 as *induced* charges, and they
  report "a total of 24" as a *consequence* of 4 O7 + 16 D7. The constraint in TT is `N_flux/2 + N_D3 = 24`, which does not involve a or b.
  Read as "induced charge = chi(K3xK3)/24", the equation matches a quantity computed one way against the same quantity computed through the
  dual fourfold (DRS). It is a duality consistency condition, not an independent tadpole. A defensible independent reading exists:
  in F-theory language an O7^- counts as 2 seven-branes, and compactness of T^2/Z2 = P^1 needs 24 seven-branes (deficit angle 4π).
  This reading is not pinned in the imported file or in NOTE.md, so it is Tier L-unpinned at best. NOTE.md's own correction
  ("not the D3 tadpole", "consistency check, not a derivation") is right and should be kept.
- U1 is trivial once a = 4 is fixed (a one-line linear equation). U3 is honest: local cancellation per plane. The negative controls
  (1,4)/(4,16), (0,24)/(4,16), (16,0,0,0)/(4,4,4,4) are correct and kernel-checked. The ansatz restriction (O7^- and D7 only) is stated.

## Corrections required
1. In `result.json`/`results.tsv`, describe U2's second equation as "induced 7-brane D3 charge matches chi(K3xK3)/24 (a
   duality-consistency sum rule; 2 per O7 is a Tier L input)". Do not call it a tadpole constraint. The "(not the D3 tadpole ...)" wording in
   result.json is fine. The commit message "(O7-, D7) = (4,16)" should not be read as a derivation of the plane count.
2. If the F-theory 24-seven-brane reading is used to justify 2a+b = 24 as an independent constraint, pin a source first (e.g. Sen hep-th/9605150 on deficit angles).
3. Protocol: attempt 2 used 3 compiles inside one 5-minute attempt. That is within the 2-attempt rule (attempt 1 was infra-only). No issue.
4. Impact "low" is correct. Novelty: none beyond finite arithmetic over library constants.

Tier A applies to the Lean statements `d7_count_unique`, `tadpole_pair_unique`, `local_distribution_unique` (+ controls). The physical reading is Tier L.
