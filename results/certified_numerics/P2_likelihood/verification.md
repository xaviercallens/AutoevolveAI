# P2 independent verification (producer != verifier)

Verifier: separate Claude Code agent, 2026-10-10. Target: commit 9b002ec. None of the verified P2 files
(Core, Likelihood, P2/Data, Fit, EdS, Ref_*, T_*, result.json, preregistration.json) changed in the later
commits f28c8d9 and 60e8020; those commits only add files.

## VERDICT: CONFIRMED_WITH_CORRECTIONS

H6, H7 and all 29 A2 slab theorems are correct as stated. They are about the intended object: the Gaussian
χ² of the DESI DR2 ALL_GCcomb data for flat ΛCDM with radiation off, profiled over every real K. I rebuilt the
whole dependency chain from source (§2), so the kernel re-checked it. My negative controls fail for the right
reason. Independent 40-digit numerics agree everywhere, with a margin of at least 3.05 in every slab. The
corrections (§6) are about wording only. Nothing is unsound.

## 1. Statement adequacy

Exact `Fraction` checks (`check_data.py`, my own parser of Data.lean against the raw files):
```
dR == file exactly: True            Cfull == file exactly: True (13x13, every off-block zero included)
xsOf length 13, kinds+redshifts match file rows: True
Pent entries: 25, indices<13: True, duplicates: 0
dense(Pent) == inv(C_file) exactly (my Gauss-Jordan over Q): True;  nonzeros of inv(C_file): 25
```
- **Rows.** The order is DV(0.295), then [DM, DH] at 0.51, 0.706, 0.934, 1.321 and 1.484, then
  **DH, DM** at 2.33. The file itself swaps the last pair, and `xsOf` has `invE`, `chi` there, which matches.
  The redshifts are written as n/2000 and are exact.
- **Model.** `E = √(Om(1+z)³ + 1 − Om)`, `chi = ∫₀ᶻ 1/E`, `invE = 1/E`, and
  `wV = cbrt(z·chi²·invE)`. So `K·wV = (z D_M² D_H)^{1/3}/r_d = D_V/r_d`, `K·chi = D_M/r_d` (flat) and
  `K·invE = D_H/r_d`, with `K = c/(100 h r_d)`.
- **K and h r_d.** `K_fit = 299792458/10154300 = 29.52369518`, which is exactly c/(100·101.543)
  with c = 299792.458 km/s. Each slab theorem quantifies over every real K. That is a superset of h r_d > 0,
  so it is conservative.
- **Quadratic form.** `chi2Of` sums P_jk(d_j − Kx_j)(d_k − Kx_k) over Pent; with no duplicates and indices
  < 13 this is rᵀ dense(Pent) r. `P_is_inverse` (a Bool on the same `Pent` constant) checks dense(Pent)·Cfull
  = I, so P = C⁻¹ on the exact file data; `#print` confirms `chi2DESI := chi2Of Pent dR (valOf (xsOf Om)) K`.
- **Vacuity: none.** All slabs have a < b (EdS a = b = 1); `envOf`/`valOf` defaults only hit indices ≥ 13,
  which Pent never uses; table Om literals must be defeq to slab ends; a false L = 40 is rejected (§3).
- **Monotonicity** (`chi/invE/wV_anti_Om`) is proved in Likelihood.lean, not assumed.
- **What "Δχ² > 25" means.** The certified exclusion test is L_slab > U_fit + 25 = 352897/10000 = 35.2897,
  with exact rational equality checked. U_fit bounds an attained value, χ²(0.29743, K_fit), from above, so
  U_fit ≥ min χ² over all (Om, K), and L > U_fit + 25 implies χ² − χ²_min > 25 on the whole slab. The argument
  is correct and conservative: the floating global minimum is 10.27104, 0.0187 below U_fit.
- **Coverage.** Sorted and parsed from the `.lean` theorem lines, not from result.json: 29 slabs, all with
  L > 35.2897 (minimum 36.02, `Ref_R101_400_R51_200`). Their union is exactly **[0, 51/200] ∪ [7/20, 1]**
  with no gaps.

## 2. Independent recompile (from source, into a separate olean dir)

**Setup.**
- Driver: `vcompile.py`, pinned Lean 4.34.1 + Mathlib, `-DautoImplicit=false`.
- LEAN_PATH is the pinned stack plus **my own** olean dir (`/home/callensxavier_gmail_com/.claude/jobs/6ecda88c/tmp/verify_p2/olean`).
  `formal_cert/.olean_out` was removed from the path, so no producer olean was loaded and every BAOCert
  module below was re-elaborated and kernel-checked.

**Results.** Every file returned rc = 0.

- Core 8.5 s, Likelihood 9.1, P2/Data 8.6; T_FitFine 1328.7; T_O100 125.9, T_R101_400 135.1, T_R51_200 130.8,
  T_O035 130.9, T_R141_400 122.2, T_O000 118.1, T_R1_40 121.6; Fit 12.6, EdS 18.0;
  Ref_R101_400_R51_200 18.0 (L = 36.02, weakest, 0.255 edge), Ref_O035_R141_400 8.1 (0.35 edge), Ref_O000_R1_40 8.1 (far).

**Axioms** (scratch file `VerifyScratchAx.lean`, rc 0, 7.4 s):
```
'BAOCert.P2.Fit.chi2_fit'                     depends on axioms: [propext, Classical.choice, Quot.sound]
'BAOCert.P2.EdS.chi2_slab'                    ... [propext, Classical.choice, Quot.sound]
'BAOCert.P2.Ref_O000_R1_40.chi2_slab'         ... [propext, Classical.choice, Quot.sound]
'BAOCert.P2.Ref_O035_R141_400.chi2_slab'      ... [propext, Classical.choice, Quot.sound]
'BAOCert.P2.Ref_R101_400_R51_200.chi2_slab'   ... [propext, Classical.choice, Quot.sound]
'BAOCert.P2.Data.P_is_inverse'                ... [propext, Classical.choice, Quot.sound]
'BAOCert.Ex.ieval_sound'  /  'BAOCert.chi2_lower_of_env'   ... [propext, Classical.choice, Quot.sound]
```
None of them uses `Lean.ofReduceBool` or `trustCompiler`.

**Grep.** I grepped `sorry|admit|native_decide|^axiom|implemented_by|@[extern|unsafe|opaque|ofReduceBool|trustCompiler`
over Core, Likelihood and P2/*.lean. Every count is 0 except P2/Axioms.lean, which has 3 lines: the planted
C7 controls `ctl_sorry` and `axiom ctl_cheat` and their `#print`. Only Axioms.lean and Fit_Tamper.lean import
audit or tamper modules. No real case file imports them.

**Not recompiled.** I rebuilt 3 of the 29 Ref slabs. The other 26 rest on the producer's compile logs. They
share the same generator and proof skeleton, and my numerics in §4 confirm all 29 statements are true.

## 3. Own negative controls (each with a true-bound twin)

**Fit control.** `VerifyScratchPosFit`, a copy of Fit with the true bounds, gives rc 0. `VerifyScratchNegFit`
lowers the upper bound to 1025/100 = 10.25, below the true value of 10.27106, and gives **rc 1**:
`28:109: error: Tactic decide failed` on `hhi` (`(cEx …).ieval … .hi ≤ 1025/100`).

**Ref control.** `VerifyScratchPosRef`, a copy of Ref_R101_400_R51_200, gives rc 0.
- `VerifyScratchNegRef` (L = 50) gives **rc 1**.
- `VerifyScratchNegRef2` (L = 2000/50 = 40) also gives **rc 1**. It is false because the true slab minimum is
  39.07. The error is `70:123: Tactic decide failed` on the `hL` inequality, while `hA` passes.

**Why these fail for the right reason.** Each negative differs from its passing twin only in the bound literal.
The "stuck at Decidable" text is the elaborator's diagnostic after the kernel decision fails. It is not an
import or elaboration error.

## 4. Independent numerics (mpmath, 40 digits; my code `numerics.py` reads the raw files)

```
chi2(0.29743, K_fit) = 10.2710611243   in [10.2525, 10.2897]  (rusty-SUNDIALS 10.2710, MCP 10.271057868)
global min (profile over all real K): Om* = 0.29746182, chi2_min = 10.271041, h r_d* = 101.53977 Mpc
EdS profile chi2(Om=1) = 1420.18328  >= 1415.82 (claimed)
profile chi2: Om=0.25 47.03 | 0.2525 42.91 | 0.255 39.07 | 0.2575 35.51 | 0.26 32.22
              Om=0.34 31.19 | 0.345 35.96 | 0.35 41.13 | 0.3525 43.85 | 0.355 46.67 | 0.36 52.57
float Delta chi2 = 25 edges (chi2 = chi2_min+25 = 35.2710): Om = 0.25767 and 0.34430
float edges at the certified threshold 35.2897:             Om = 0.25766 and 0.34432
```

**Slab check** (`grid.py`). I evaluated the closed-form profile χ²_min(Om) = dᵀPd − (xᵀPd)²/(xᵀPx) on 25
points in each of the 29 slabs. No slab has a violation. The smallest margin, true minimum minus L, is
**3.05**, on [0.2525, 0.255] (39.07 vs 36.02). The other near-edge margins are 3.79 on [0.35, 0.3525] and
3.23 on [0.25, 0.2525].

**Certified vs true boundary.** The certified excluded set ends at 0.255 and starts at 0.35. The true Δχ² > 25
region begins below 0.2577 and above 0.3443. So the certificate is conservative by about 0.0027 on the low
side and about 0.0057 on the high side. That gap comes from the 1/400 width floor in A2 and the slack in the
box bound, not from an error. (The profile is skewed: 39.07 at 0.255, not the ≈36 a symmetric Gaussian gives.)

## 5. Overclaim scan (result.json, preregistration amendments)

- **Failed H8.** The preregistered H8 is reported as failed (8/19, prediction false), and the verdict is
  P2_PARTIAL. That is honest.
- **A2 disclosure.** A2 is openly disclosed as written after the untrusted Python preview. Its rule, bisection
  down to a width of 1/400, is mechanical; the leaves are consistent with it (all 6 unexcluded leaves have width 1/400).
- **Missing scope in result.json.** result.json says "excluded_certified" without stating the convention. The
  `not_claimed` scope (flat ΛCDM, radiation off, Gaussian likelihood as input, thresholds as conventions) is
  only in the preregistration.

## 5b. Controls C4–C7
- **C4: consistent.** The MCP profile covers only h r_d in [50, 200]; my all-real-K profile is ≥ L in all 29 slabs.
- **C5: consistent.** `Slab_O029_O030.chi2_slab` is the line `29/100 ≤ Om ≤ 30/100 → ∀ K, 33/100 ≤ chi2DESI`.
  The profile at 0.29743 is 10.27, so this slab cannot be excluded and is not. I did not recompile this file.
- **C6: verified numerically, Lean not recompiled.**
  - Diffing Data_Tamper.lean against Data.lean shows exactly one change, in `dR[2]` (DH at z = 0.51):
    21.86294686 becomes 26.15163010780462. My mpmath gives a shift of exactly +10.0σ.
  - Cfull and Pent are unchanged.
  - My tampered χ² at the fit point is 122.7241171, inside the certified [122.697, 122.7513].
- **C7: producer-only.** The planted `sorry` and `axiom` lines exist in P2/Axioms.lean. I did not rerun the
  producer's 59-theorem audit. My independent evidence is my own `#print axioms` on 8 declarations (§2).

## 6. Corrections for the write-up

1. Say "excluded at Δχ² > 25, profiled over h r_d (all real K), against a certified upper bound on the global
   minimum." Do not write "5σ" unless the 1-dof Wilks reading is stated explicitly. With two free parameters
   (Om, h r_d) jointly, Δχ² = 25 corresponds to about 4.6σ.
2. State the scope in the same sentence as the result: flat ΛCDM, radiation and neutrinos off, Om ∈ [0, 1],
   DESI DR2 ALL_GCcomb Gaussian likelihood taken as input. These Om numbers are not directly DESI's published
   analysis, although the floating best fit, 0.29746, is close to 0.2975.
3. Lead with the preregistered H8 failure (8/19). Present [0, 0.255] ∪ [0.35, 1] as the result of the post hoc,
   disclosed A2 refinement. Note that each slab theorem is true regardless of how the slab was chosen.
4. Quote the conservativeness: the certified edges are 0.255 and 0.35, the floating edges are 0.2577 and
   0.3443, and the unresolved pieces are [0.255, 0.26] and [0.34, 0.35].
5. Add the scope and convention fields to result.json, or to the paper table, so the artifact stands alone.
6. **Housekeeping.** The producer's commit 60e8020 (P3) swept in the verifier's temporary files
   `formal_cert/BAOCert/P2/VerifyScratch{Ax,PosFit,NegFit,PosRef,NegRef,NegRef2}.lean`. Three of them (NegFit, NegRef, NegRef2)
   are deliberately false controls that do not compile. I deleted them from the working tree, but did not commit.
   A follow-up commit should remove them from git so they do not break a `lake build` of the directory.

Scratch work: `/home/callensxavier_gmail_com/.claude/jobs/6ecda88c/tmp/verify_p2/` holds `check_data.py`,
`numerics.py`, `grid.py`, `vcompile.py` and the `logs/*.json` compile records.
