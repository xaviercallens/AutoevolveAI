# LT_D2 adversarial verification

Verifier: independent agent, 2026-10-08. Scratch files: /home/callensxavier_gmail_com/.claude/jobs/6ecda88c/tmp/verify_d2/
Toolchain used: /mnt/disks/disk-socrateai-local-1/callensxavier_home_data/elan/toolchains/leanprover--lean4---v4.34.0-rc2/bin/lean (Lean 4.34.0-rc2, commit 6a10ac8c), LEAN_PATH from `lake env printenv LEAN_PATH` in LeanMaster plus LT_D2/scratch_olean. No `lake build`, no writes outside the verify dir and this file.

## VERDICT: CONFIRMED (core claim holds), with three documentation corrections (items 1b, 4b, 7) that do not change the verdict.

## 1. Patch fidelity: PASS

Command: `python3 .../verify_d2/diff.py` (byte comparison + difflib of all 38 files against upstream .../openai-math/lean/).

```
38
DIFF OAI/Analysis/LiebThirring/FiniteParity.lean
--- upstream
+++ scratch
@@ -505 +505 @@
-    (Nat.card_congr (Set.equivOfEq hsingle)).trans Nat.card_unique
+    (Nat.card_congr (Equiv.setCongr hsingle)).trans Nat.card_unique
[]            <- no non-.lean files in src/
```
Exactly 1 of 38 files differs, by one line, by exactly the declared rename. No other byte differences (the comparison also ran on raw bytes).

The 14 carried-over files (Model, MatrixOrder, ResolventCalculus, MatrixTangent, FieldLimit, RankOne, FieldRegularity, FieldPrimitive, ActionPenalty, BoundaryValues, ActionBounds, BoundState, CubeFlags, FlagGeometry):
- Their LT_D2 scratch_olean copies are byte-identical (sha256) and mtime-identical to LT_D/scratch_olean (all 14 `True True`).
- olean mtimes 11:26:34 to 11:34:32 UTC; the LT_D2 src tree and patches.json did not exist until 11:56:20. So they were built before any rename existed. LT_D's preregistration states "no upstream file is patched" and LT_D's closure record has the matching compile times (ActionBounds 20.7 s, ActionPenalty 25.2 s, BoundState 18.3 s, ...). The 14 scratch sources equal upstream bytes (diff above).
- Import structure is a linear chain (`grep '^import'`: each file has exactly one import; Model imports Mathlib, FiniteParity imports FlagGeometry, GenericPosition imports FiniteParity, ...). `grep -l FiniteParity *.lean` returns only FiniteParity.lean and GenericPosition.lean. None of the 14 imports the patched module.
- 1b (limit, not a defect): I did not recompile the 14 from source, so "compiled from unmodified upstream" rests on mtimes + hash-identity + LT_D's record, not on my own rebuild.

## 2. Forgery / smuggling scan: PASS (zero hits)

Own scanner (`scan.py`; strips nested `/- -/`, `--`, and string literals first) over the 38 scratch files:

| category | hits |
|---|---|
| sorry, admit, axiom, opaque, unsafe, implemented_by, extern, native_decide, ofReduceBool | 0 each |
| #exit, #print, #eval, #check, any other `#cmd` | 0 |
| set_option (any) | 0 (no option is set anywhere) |
| macro, syntax, elab, notation/infix/prefix/postfix, macro_rules, initialize, run_cmd, open Lean, Lean.Elab/Meta | 0 |
| imports not Mathlib/OAI.* | 0 (38 import lines: Model has `import Mathlib`, the other 37 `import OAI.Analysis.LiebThirring.*`) |
| `attribute [local instance] Classical.propDecidable` | 9 (BoundaryParity:134, EquivariantFlags:158, FiniteParity:90,342,515,663, GenericPosition:436, InitialOrbit:22,221) |
| `local instance` on SeminormedAddCommGroup / NormedSpace ℝ of `selfAdjoint (Matrix ..)` | 8 (BoundaryValues:177,179; FieldPrimitive:29,31,123,125,222,224) |
| other `instance` declarations | 20 lines counted by the broad pattern, which includes the 17 above; none inspected as suspicious |

Non-benign hits: none. The 9 `Classical.propDecidable` locals are standard and add only Classical.choice (whitelisted). The 8 local instances are a seminorm-diamond workaround (source comment: "avoiding the duplicate subgroup class instance"); they are `local` and in proof files, not in Model.lean (where the statements live), and the instance bodies are `inferInstance`-derived. Note that `local` scope plus the axiom report below bound what they can do.

## 3. Independent axiom report: PASS, and the report path can fail

ax_real.lean = `import OAI.Analysis.LiebThirring.Main` + `#print axioms` on four declarations + `#check` + `#print MainClaim`. Run time 10.4 s, rc 0, empty stderr:

```
'OAI.SharpLiebThirring.sharp_lieb_thirring' depends on axioms: [propext, Classical.choice, Quot.sound]
'OAI.SharpLiebThirring.optimalConstant_le_sharp' depends on axioms: [propext, Classical.choice, Quot.sound]
'OAI.SharpLiebThirring.sharp_le_oneStateConstant' depends on axioms: [propext, Classical.choice, Quot.sound]
'OAI.SharpLiebThirring.sharp_times_extremizer_mass' depends on axioms: [propext, Classical.choice, Quot.sound]
OAI.SharpLiebThirring.sharp_lieb_thirring : OAI.SharpLiebThirring.MainClaim
```
(Main.lean has no "equality-attainment theorem" by name; its three lemmas are the three above, and the equality case is the last conjunct inside sharp_lieb_thirring.) My runner verdicts: all four `OK`.

Negative control (ax_neg.lean, same LEAN_PATH, rc 0):
```
ax_neg.lean:3:8: warning: declaration uses `sorry`
'neg_sorry' depends on axioms: [sorryAx]
'neg_axiom' depends on axioms: [cheat]
'pos_ok' does not depend on any axioms
neg_sorry FAIL:sorryAx
neg_axiom FAIL:cheat
pos_ok OK
```
So the runner rejects a sorry and a locally declared `axiom cheat : False`, and accepts a clean theorem. Both controls and the real report ran in the same environment.

## 4. Recompile the patched file from source

4a. Patched (scratch src), `lean --root=<src> -o out_patched/.../FiniteParity.olean <file>`:
`patched rc 0 secs 47.5`, STDOUT empty, STDERR empty (no error, no `sorry` warning). The resulting olean has sha256 ac1dbe6b88d06a895cf747055a3ad97918b9f48f288f77dcdd3e9eb5dba3dc8b, identical to LT_D2/scratch_olean's FiniteParity.olean (so that stored olean really is the compile of this source).

4b. Original upstream text (copied to a fresh root), same command: `original rc 1 secs 52.3`
```
.../orig_root/OAI/Analysis/LiebThirring/FiniteParity.lean:505:21: error(lean.unknownIdentifier): Unknown constant `Set.equivOfEq`
.../FiniteParity.lean:492:77: error: unsolved goals ... ⊢ False
olean exists False
```
Blocker reproduced exactly as claimed.

4c. UNDISCLOSED DEVIATION found. Upstream's lakefile.lean sets `leanOptions := #[⟨`autoImplicit, false⟩]`, and the pilot compiled with plain `lean` (no `-DautoImplicit=false`; confirmed: no `-D` flag anywhere in scripts/openai_math/lt_d_lean.py or lt_d2_shim.py). Plain `lean` has autoImplicit on, which is more permissive and could in principle mask a typo as an auto-bound variable. deviations.md and result.json do not mention this. Check I ran: recompiled with `-DautoImplicit=false` the files Model (the statement file), FiniteParity (patched) and Main: all `rc 0` (11.6 s, 47.6 s, 11.4 s). The other 35 files were not re-run under that flag (not done: roughly 12 more minutes of serial compile). Effect on the claim: none found; the disclosure gap is real.

## 5. Statement adequacy (reading only; no human audit possible)

Read ComparatorChallenges/LiebThirring.lean. The challenge file's `sharp_lieb_thirring` is `sorry` as expected for a challenge; the `MainClaim` type printed from the compiled solution (item 3) is the same proposition. The repo's text-level 16/16 match was not re-run; I relied on the printed MainClaim and the reading below.

- H1: pair (val, grad) in L²(ℝ;ℂ) with weak-derivative identity `∫ val·φ' = -∫ grad·φ` for all C^∞ compactly supported φ. I checked in Lean that `ContDiff ℝ (↑(⊤:ℕ∞) : WithTop ℕ∞)` is smooth (∞), not analytic (ω): `(↑⊤ : WithTop ℕ∞) ≠ ⊤` and `∞ ≠ ω` both proved. This matters: with ω the test-function class would be {0} and the derivative condition vacuous. It is not. Faithful H¹(ℝ;ℂ), though as a structure of representatives (not a quotient mod null sets); harmless since forms and pairing ignore null sets, and `grad` is determined a.e. by `val`.
- l2Pairing: ∫ conj(u)·v, complex. Standard.
- schrodingerForm W u v = ∫ conj(u')v' - ∫ W conj(u) v. Correct sesquilinear form of -d²/dx² - W. Bochner integrals return 0 on non-integrable integrands; for Admissible W (L^{γ+1/2}, exponent > 1) and u,v ∈ H¹ ⊂ L²∩L^∞ the W-term is integrable, so no junk-value effect inside MainClaim.
- IsNegativeEigenfunction: 0<k and form(v,u) = -k²⟨v,u⟩ for all v∈H¹. This is the weak eigen-equation -u''-Wu = -k²u tested against all of H¹ (not just compactly supported test functions; equivalent by density). Not too restrictive: any true negative eigenfunction qualifies, and the eigenvalue is -k² with k>0 any real. It does not force the moment to 0: the equality potential gives a nonzero moment (see numeric check below). Non-zero-ness of u comes from orthonormality.
- negativeMoment: sup over N and orthonormal families of eigenfunctions of Σ ofReal(k_i)^(2γ) in ℝ≥0∞. Equals Σ|E_j|^γ with multiplicity; N=0 gives 0 (so the sup is ≥ 0). ENNReal avoids a finiteness assumption; it could make a claim of "≤ finite" stronger than a real-valued one, not weaker. Orthonormal families with repeated k are allowed (multiplicity), which matches the standard moment (1D eigenvalues are simple anyway).
- oneStateMoment: sup over a single unit-norm eigenfunction of k^(2γ). Lower than or equal to negativeMoment as it should be.
- Admissible: W ≥ 0 a.e. and MemLp W (γ+1/2). Nonnegativity is a standard WLOG (use the positive part), exponent γ+1/2 is the correct 1D LT exponent. Not trivial: nonzero W exist (equalityPotential is shown admissible).
- potentialMass: ∫⁻ ofReal(W)^(γ+1/2). Correct; finite for admissible W.
- semiclassicalConstant = Γ(γ+1)/(2√π Γ(γ+3/2)) = L^cl_{γ,1} (the (4π)^(-1/2)Γ(γ+1)/Γ(γ+3/2) formula at d=1). Correct.
- sharpConstant = 2((γ-1/2)/(γ+1/2))^(γ-1/2)·L^cl: the one-bound-state (Keller / Lieb-Thirring) conjectured sharp constant. Positive for γ>1/2, so ENNReal.ofReal does not collapse it to 0.
- optimalConstant = sup_W negativeMoment/mass; oneStateConstant likewise with oneStateMoment; both over Admissible W with positive mass. Division in ℝ≥0∞ with mass>0 and mass<⊤ for admissible W has no 0/0 or ⊤/⊤ artefact.
- equalityPotential: (r+1)·sech²(r x), r = (γ-1/2)⁻¹, Pöschl-Teller form.
- MainClaim: ∀ γ∈(1/2,3/2): (i) negativeMoment ≤ sharpConstant·mass for all admissible W, (ii) optimalConstant = sharp, (iii) oneStateConstant = sharp, (iv) equalityPotential admissible, (v) positive mass, (vi) equality there.

Independent numeric spot-check (hand calculation, not Lean) at γ=1: r=2, W=3 sech²(2x); bound-state parameter s(s+1)=3/4, s=1/2, k=r·s=1, so moment 1 (one bound state, since s ≤ 1). Mass = 3^{3/2}·(1/2)·(π/2) ≈ 4.081. Ratio ≈ 0.2450. sharpConstant(1) = 2·(1/3)^{1/2}·1/(2√π·Γ(5/2)) ≈ 2·0.5774·0.2122 ≈ 0.2450. Equality case is consistent, and the moment there is nonzero (not vacuous).

Does MainClaim state the scalar 1D Lieb-Thirring conjecture for 1/2<γ<3/2? Yes, as written it states the sharp bound with the one-bound-state constant for all admissible W in that open range, plus that the optimal constant equals it. That is the content of the (to my knowledge, still open as of my knowledge) scalar-case conjecture for that range; I found nothing in the definitions that makes it weaker or easier. It is therefore a very strong claim and warrants the human statement audit that result.json says has not happened.

What I cannot judge: (a) whether `Admissible` plus the form domain match the conventions of the published conjecture in every corner (I found no discrepancy); (b) whether the literature status "open" is current as of today (I did not search); (c) whether the 16/16 text match really ensures the challenge MainClaim equals the Model.lean one at elaboration level (I saw the elaborated MainClaim from the closure only, not the challenge's elaborated form); (d) subtle Mathlib junk-value behaviours of `rpow` at `ofReal` ≥ 0 (benign here by inspection).

## 6. Process: PASS

- Preregistration commit e27c7a5, committer date 2026-10-08 11:56:12 UTC (`git log -- LT_D2/preregistration.json`). File mtime 11:56:06; working tree equals HEAD (`git diff --stat HEAD` empty).
- First result artefacts: patches.json and src FiniteParity 11:56:20, closure.json 11:56:20, deviations.md 11:56:48, part_statements.json 11:57:17, part1b_closure.json 12:06:16, scratch_axioms 12:06:28, part_axioms.json 12:06:40, result.json 12:07:32. All after the commit.
- Only the declared rename applied (item 1). The rename is the one in preregistration allowed_renames; no amendments needed.
- deviations.md D1 (relative path bug) is plausible: the stored record dates are consistent. Problem: it is timestamped "~12:10 UTC", later than part1b_closure.json (12:06) and result.json (12:07). That clock inconsistency is cosmetic but should be corrected.
- The preregistration states "the driver's classifiers were controlled by lane LT_D"; I added my own positive/negative axiom controls (item 3).

## 7. Overstatement review of result.json

Supported by evidence: verdict KERNEL_PILOT_OK; single-replacement patch with the stated sha256 values (not re-hashed by me; the diff confirms the single line); axiom list; 38/38 compiled with 14 carried / 24 in-lane; tier "Tier A is NOT claimed". `does_not_establish` is complete and honest (Comparator, original-files-under-v4.34.1, statement adequacy, matrix/equality classification).

Sentences claiming more than evidence, or missing disclosure:
1. `meaning`: "all 38 files compile under Lean v4.34.0-rc2" omits that 14 of the 38 were compiled in lane LT_D, not this lane (stated only in `files`), and omits that compilation used plain `lean` without upstream's `autoImplicit false` option (item 4c). Suggested amendment: add the autoImplicit deviation to deviations.md and note that Model, FiniteParity, Main were re-checked under `-DautoImplicit=false` by this verifier.
2. `deviations`/deviations.md D1 timestamp (12:10) postdates the artefacts it describes (12:06-12:07): fix the time.
3. Mathlib drift: result.json says "mathlib_rev 85e3a25e" and upstream toolchain v4.34.1; upstream's lakefile pins mathlib at d13f23b7 which differs from LeanMaster's. The claim "differs from upstream only by the rename" is true for the sources but not for the environment (Lean rc2 vs 4.34.1; different Mathlib revision; options). The text partly says this under `does_not_establish`, but the `meaning` sentence ("differs ... only by the rename") is about sources only and should say so.
4. `statement_comparison_text_level` 16/16 match: labelled text-level, not elaboration; I did not reproduce it. It is not used as an adequacy claim in `meaning`, so acceptable.

Nothing in result.json asserts Tier A, Comparator, or truth of the Lieb-Thirring conjecture. That restraint is correct; the kernel report alone supports only "the adapted proof term typechecks with whitelist axioms under this toolchain".

## Summary of commands run (all by me)
- diff.py (item 1), scan.py (items 1b, 2), run_ax.py real / neg (item 3), recompile.py (item 4), autoimp.py (item 4c), run_t.py (smooth-vs-analytic check, item 5), `git log`, `stat`, `git diff --stat` (item 6).
- Not done: full independent recompile of all 38 files; independent re-hash of patches.json sha256 values; literature check of the conjecture's current status.
