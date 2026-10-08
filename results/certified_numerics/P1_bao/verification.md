# P1 certified BAO distances: independent verification

VERDICT: CONFIRMED_WITH_CORRECTIONS

The mathematics holds. All corrections are about how the write-up scopes its claims.
Verifier: independent adversarial agent (producer != verifier), commit 04ad62f. Scratch: `~/.claude/jobs/6ecda88c/tmp/verify_p1/`.

## 1. Statement adequacy (Core.lean, Fit.lean)
- `E Om z = √(Om(1+z)^3 + (1-Om))`, `invE = 1/E`, `chi Om z = ∫ x in 0..z, invE Om x`. This is the flat-ΛCDM, radiation-off formula. The verifier checked it by `rfl` against a hand-written `∫ 1/√(Om(1+x)^3+(1-Om))` (VerifyAxioms.lean).
- Casts: `((29743:ℕ):ℝ)/((100000:ℕ):ℝ) = 0.29743`, `1868/2000 = 0.934` and `4660/2000 = 2.33`, each proved by `norm_num` in the verifier's file. All seven DESI DR2 z (0.295, 0.51, 0.706, 0.934, 1.321, 1.484, 2.33, read from `desi_gaussian_bao_ALL_GCcomb_mean.txt`) are exact multiples of 1/2000 (n = 590, 1020, 1412, 1868, 2642, 2968, 4660), so the preregistration's rounding clause never applies. FitOm101 uses Om = 3004043/10^7, which is exactly 0.29743 × 1.01.
- `lowerSum` sums `y.1` (lo at the right endpoint of each cell) and `upperSum` sums `x.2` (hi at the left endpoint). Both directions are correct for an antitone integrand. `seg_bounds` is proved by induction over cells with `integral_add_adjacent_intervals`, and `cell_bounds` comes from `integral_mono_on`.
- `node_bounds`: `lo² a ≤ D² b` together with `A = a/b` (`A_eq`, with `Nat.cast_sub` guarded by `p ≤ q`) gives `lo/D ≤ 1/√A`, and the upper side is symmetric. Proved in Lean, not assumed.
- Not vacuous. The hypotheses `p ≤ q, 0 < q, S, D` are discharged by `norm_num`. The table has 4661 entries, and each theorem uses `tbl.take (n+1)` with the length checked. The bounds are tight (§4), not trivial.
- The verifier's file also derives the decimal statement `0.7341801200236125 ≤ chi 0.29743 0.934 ≤ 0.734384160133889` from `Fit.chi_z0934` (it elaborated, rc 0).

## 2. Independent recompile and axioms
```
lean_pinned.py compile formal_cert/BAOCert/Core.lean --olean BAOCert.Core  -> rc 0, 6.7 s (linter warnings only)
lean_pinned.py compile formal_cert/BAOCert/Fit.lean  --olean BAOCert.Fit   -> rc 0, 123.9 s, no output
lean_pinned.py compile <scratch>/VerifyAxioms.lean (import BAOCert.Fit)     -> rc 0, 5.3 s
  seg_bounds, chi_bounds, node_bounds, Fit.chi_z{0295,0510,0706,0934,1321,1484,2330},
  Fit.invE_z0934, Fit.invE_z2330: [propext, Classical.choice, Quot.sound]
  Fit.tbl_check: [propext]
<scratch>/CopyEdS.lean (EdS.lean + #print axioms, all 14 theorems)          -> rc 0, 133.4 s; 14/14 theorems [propext, Classical.choice, Quot.sound]
<scratch>/CopyFitOm101.lean (FitOm101.lean + #print axioms, all 14)         -> rc 0, 132.9 s; 14/14 theorems [propext, Classical.choice, Quot.sound]
grep -c native_decide / sorry / ^axiom in Core, Fit, EdS, FitOm101          -> 0 / 0 / 0 in every file
```
The kernel replays every check through `decide +kernel`. No `native_decide` is used, so there is no `Lean.ofReduceBool`.

## 3. Verifier-planted negative controls (not the producer's Tampered.lean)
- NegA (`BAOCert.FitNegA`): node 3000 (chunk c23, offset 56) changed from hi 432341186175 to 431341186175, i.e. hi − 10^9. Result: rc 1, 124.8 s. The errors fall exactly where node 3000 is used: `50:81 (kernel) application type mismatch` (tbl_check), plus `159:44` and `161:62` (chi_z2330's checkFrom and its upperSum). `chi_z0295`..`chi_z1484` (take ≤ 2969) and all seven invE theorems still compiled, so the edit is local and the control is informative.
- NegB (`BAOCert.FitNegB`): the stated upper bound of chi_z0934 changed to 1468000000000000/(D·S) = 0.734, below the true 0.7342821 (mpmath), so the statement is false. Result: rc 1, 137.5 s, `112:2: error: Type mismatch` at `exact h`. This is an elaborator rejection: the original sum no longer matches the false statement. It is not a kernel rejection.

## 4. Independent recomputation (mpmath, 50 digits; bounds parsed from the Lean theorem statements)
| z | chi (mpmath) | Lean lo | Lean hi | rel width | Om×1.01 gap |
|---|---|---|---|---|---|
| 0.295 | 0.274742144914262 | 0.2747074286 | 0.2747768599 | 2.527e-4 | 3.8e-4 |
| 0.510 | 0.449010661391892 | 0.4489509195 | 0.4490704032 | 2.661e-4 | 7.8e-4 |
| 0.706 | 0.589831404769656 | 0.5897507515 | 0.5899120598 | 2.735e-4 | 1.10e-3 |
| 0.934 | 0.734282137994077 | 0.7341801200 | 0.7343841601 | 2.779e-4 | 1.41e-3 |
| 1.321 | 0.939747181341637 | 0.9396160789 | 0.9398782917 | 2.790e-4 | 1.82e-3 |
| 1.484 | 1.013970640030867 | 1.0138296368 | 1.0141116524 | 2.781e-4 | 1.95e-3 |
| 2.330 | 1.315964485769369 | 1.3157876260 | 1.3161413589 | 2.688e-4 | 2.44e-3 |
- All seven values lie inside. The maximum width is 2.790e-4 (≤ 2.8e-4; the preregistered threshold was 5e-4). The invE values lie inside 1e-12-wide boxes at all 7 z for Fit, FitOm101 and EdS.
- Om×1.01: each FitOm101 upper bound is below the matching Fit lower bound, so the enclosures are disjoint at all 7 z, including z = 0.295, which H3 did not require. mpmath values lie inside the FitOm101 bounds.
- EdS: the closed form 2(1 − (1+z)^(−1/2)) agrees with mpmath quad to < 1e-40 and lies inside EdS.lean at all 7 z. The EdS widths are 4.6e-4 to 6.6e-4, above 5e-4. That is fine for a control, but H1's width claim covers only the fit point, not EdS.
- `bounds_{Fit,FitOm101,EdS}.json`, which evaluate_p1.py consumes, match the Lean statement numbers exactly (Fraction equality, 7/7 each).
- The astropy values in result.json agree with mpmath to about 1e-15.

## 5. rusty-SUNDIALS audit fairness
- main.rs uses `FlatCosmology::lcdm(0.29743, 0.7)`. With `radiation: None`, E² = Om(1+z)³ + (1−Om)·1 (Lambda), and h = 0.7 is inert when radiation is off. It uses the same 7 z, Om×1.01 = 0.3004043 (f64), and EdS Om = 1.
- Re-checked against the Lean-parsed bounds (exact Fraction of each f64):
  - cvode_default, quadrature_default, cvode_rtol1e-3, Om101 quad and EdS quad are all inside at 7/7.
  - cvode_rtol1e-2 is outside at 3/7: z = 0.934 HIGH, 1.321 HIGH, 2.33 LOW. This matches result.json.
- Branch: the checkout is `~/rusty-SUNDIALS-wt-cvode-adams`, branch `fix/cvode-adams-order-and-stderr` (b25f152; clean tree; merge-base e793810 with origin/main).
  - The diff touches `crates/cvode/src/solver.rs`, but the BDF arm of `set_coefficients` still returns `BDF_L[q][..=q]` and the BDF `err_coeff` is unchanged.
  - The new `etamax`/`tq`/`tau` state is read only in Adams code (`set_adams`, `adams_complete_step`, lines ≥ 820).
  - The other edits are `println!` → `eprintln!` and a stats counter. qf-bao-distances changes only in its README.
  - Conclusion: BDF numerics are unchanged, judged by reading the code. The audit was not re-run on origin/main. This matters only for the exact 3/7 pattern in H4. H2 is insensitive at this width.

## 6. Overclaim scan of result.json
- D_M/r_d and D_H/r_d intervals: evaluate_p1.py multiplies the certified bounds by `C_OVER_100_HRD = Fraction(299792458, 10154300)` in Python. That step is exact rational arithmetic but outside Lean. The pulls are then computed in float with diagonal σ = √cov[j][j] only (marginal; they ignore the D_M–D_H correlation at equal z).
- D_V(z = 0.295) is not certified, and result.json says so. H5 (certified χ²) is NOT_ATTEMPTED, and it is reported that way.
- The fit point (Om = 0.29743, h r_d = 101.543 Mpc) is a rounded floating-point grid fit taken from the origin/main README. It is not certified as the χ² minimum. The certificate is "chi at this given Om", not "chi at the best fit".
- H2 discriminates only at about 1e-4. rtol = 1e-3 also lies inside at 7/7, so the enclosures say nothing about default-CVODE accuracy (about 1e-7). H2 audited only chi; the Rust 1/E (D_H) was never compared with the 1e-12 invE boxes.
- H4's loose run sets atol = 1e-2 as well as rtol = 1e-2. The preregistration names only rtol.
- Note: the comment in evaluate_p1.py says "exact rational arithmetic", but the pulls themselves are float.

## Corrections for any write-up
1. Say that D_M/r_d, D_H/r_d and the DESI pulls are derived in Python from the Lean bounds, not proved in Lean. The pulls are float, use diagonal errors only, and are marginal.
2. Say that the fit point is an uncertified, rounded floating-point fit. Lean certifies chi at Om = 29743/100000 exactly, not at a χ² minimum.
3. Say that H2 has discrimination of about 1e-4 (rtol 1e-3 passes too). Do not present it as validating CVODE to its tolerance. D_H from Rust was not audited.
4. Say that H4 used rtol = atol = 1e-2, on the PR branch fix/cvode-adams-order-and-stderr. The BDF path is unchanged by code reading but was not re-run on main.
5. Say that the EdS control widths (≤ 6.6e-4) exceed 5e-4. The ≤ 2.8e-4 width applies to the fit point and Om×1.01 only.
6. Say that H3 disjointness holds at all 7 z, which is more than preregistered (z ≥ 0.5).
7. Say that `Fit.tbl_check` uses only [propext]. Every other theorem uses exactly {propext, Classical.choice, Quot.sound}. Never write "no axioms".
