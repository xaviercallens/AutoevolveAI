# P3 independent verification (producer != verifier)

Verifier: separate Claude agent, 2026-10-10, worktree commit 60e8020. Scratch:
`/home/callensxavier_gmail_com/.claude/jobs/6ecda88c/tmp/verify_p3/` (build.py, fullbuild.py, mkctl.py, numerics*.py, logs).

## VERDICT: CONFIRMED_WITH_CORRECTIONS

The theorem `BAOCert.P3.H0_ge_73_excluded` is kernel-checked. I rebuilt it from source, with all 173 BAOCert
modules in its closure compiled into an empty olean directory. Its axioms are `[propext, Classical.choice, Quot.sound]`.
The statement is the BAO+BBN chi² it claims to be, and it is not vacuous. Every branch of the proof avoids
Mathlib junk values. The claim is conservative: in this model the profile Δχ² at H0 = 73 is 54.6 and the
Δχ² = 25 crossing is at H0 ≈ 71.57. The corrections below concern wording and controls. None of them
affects soundness.

## 1. Statement adequacy

`#check` output from my own audit file:
```
H0_ge_73_excluded : ∀ (Om h wb : ℝ), 0 ≤ Om → Om ≤ 1 → 73 / 100 ≤ h → ↑(352897 / 10000) < chi2tot Om h wb
H0_ge_73_delta_chi2 : ... chi2tot (↑29743/↑100000) ↑(1371802127/2000000000) ↑(1109/50000) + 25 < chi2tot Om h wb
```
- **Data.** `P2/Data.lean` `dR` and `Cfull` are exactly equal to the official DESI DR2 files
  `desi_gaussian_bao_ALL_GCcomb_{mean,cov}.txt` (disk 2, `desi_bao_dr2/`). The maximum absolute difference is
  0.0 for both. The order (DV, DM/DH pairs, Lyα DH then DM) and the z values (590/2000 = 0.295, ...,
  4660/2000 = 2.33) match `xsOf`.
- **Observables.** `chi = ∫₀^z 1/E` and `invE = 1/E`, with `E = sqrt(Om(1+z)³ + 1 − Om)` (radiation off).
  `wV = cbrt(z chi² invE)`. `chi2Of` is `Σ P_jk (d_j − K x_j)(d_k − K x_k)`, so D_M/r_d = K·chi, D_H/r_d = K/E
  and D_V/r_d = K·(z chi²/E)^{1/3}, with `K = 299792.458/(100 h r_d)`.
- **Units.** c [km/s] / (100 h [km/s/Mpc]) = c/H0 [Mpc]. Divided by r_d [Mpc], K is dimensionless.
  c equals `common.C_KM_S` (scipy c/1000).
- **Independent reproduction.** My own code reads only the official files. It gives χ² = 10.271061 at the
  certified point (float and mpmath agree to 1e-10). That is below the certified upper bound 10.2897.
- **r_d.** `BBNBase.lean` and the AutoevolveAI original have the same sha256,
  `2b6530838efa0df9bfb475a5d8b25ee29aa121989cc83d04e07f595f5f616e38`, for both
  `formal_cert/BAOCert/H0/BBNBase.lean` and `formal/ANSE/BAO_BBN_H0.lean`. `rdAubourg`, `omegaCb = Om h² − ω_ν`
  and `omegaNu = 0.0107·0.06` match `common.rd_aubourg16` and `omega_cb_of` (common.py:114-132), with the
  same constants and exponents. `Kof h Om wb` calls `omegaCb h Om` with the arguments in the right order.
- **Junk-value coverage.** The quantifier really is over all real ω_b, with no ω_cb > 0 hypothesis, so it is
  stronger than the preregistered claim shape. No branch uses junk values:
  - ω_b < 0.01833, which includes ω_b ≤ 0: only `gt_of_prior` is used. The BBN term is > 49, and
    `chi2DESI_nonneg` holds for every K (PSD).
  - Om ∈ [0, 0.255] or [0.35, 1]: the P2 `chi2_slab` theorems are stated `∀ K : ℝ`, so r_d never enters.
    This covers small Om with large h, and also the region ω_cb ≤ 0 (Om ≤ 0.0012 at h ≥ 0.73), where rpow
    would be junk.
  - Boxes, Om ∈ [0.255, 0.35] and ω_b ∈ [0.01833, 0.02603]: `K_le` assumes a > 0 and c > 0, and `hdom` forces
    ω_cb > 0. Every rpow base is positive. The boxes use only an upper bound on K plus the vertex check, so
    every K ≤ K0 is covered.
- **Non-vacuity.** For example (Om, h, ω_b) = (0.3, 0.73, 0.02218) satisfies the hypotheses.
  `chi2tot_point` is a non-trivial upper bound, and I reproduce it at 10.27106.
- **Scope edges.** Om > 1, Om < 0 and h < 0.73 are excluded by the hypotheses, not proved.

## 2. Recompilation and audit

- **Full fresh build.** `python3 fullbuild.py` builds the transitive closure of `BAOCert.P3.Main`: 173 modules,
  including Core, Likelihood, P2 Data, all T_* tables, 29 Ref slabs, H0/*, Glue, Point, Box_000..088 and Main.
  It writes to an empty `out2/`. The producer's `.olean_out` is not on LEAN_PATH, which the script asserts.
  Result: `built 173 of 173 rc!=0: 0 cpu s 9928`. The only non-empty outputs are linter warnings
  (unused variables, deprecated `push_neg`) and `#print axioms` lines.
- **Earlier partial build.** H0 + P3 + Ref slabs rebuilt on top of the producer's other oleans gave 125/125
  rc 0 (Main 10 s).
- **Axiom audit.** My own file (`VerifyScratchAx.lean`, compiled against `out2`, then deleted) gives
  `[propext, Classical.choice, Quot.sound]` for each of `H0_ge_73_excluded`, `H0_ge_73_delta_chi2`,
  `Point.chi2tot_point`, `rdIv_mem`, `K_le`, `chi2DESI_nonneg`, `Box_044.box` and `Ref_O090_O100.chi2_slab`.
- **Grep.** I grepped for `sorry|native_decide|^axiom|implemented_by` across `formal_cert/BAOCert/`. The only
  hits are the audit files `Axioms.lean`, `P2/Axioms.lean` and `P3/Axioms.lean` (the planted
  `ctl_sorry` / `ctl_cheat`). H0/ and P3/ have no other hits.
- **No `native_decide`.** All numeric steps are `decide +kernel`.

## 3. Negative and tightness controls (verifier-written, compiled against `out2`, then deleted)

| file | change | rc | meaning |
|---|---|---|---|
| VerifyScratchMain65 | threshold 35.2897 → 65 | 1 | **False statement, rejected.** Witness: χ²(0.3076, 0.73, 0.025022) = 64.91088 (mpmath, 30 digits) < 65. Errors: the prior-tail goals reduce to `False`, and `decide` fails on `65 < 3187/50` and `65 < 4861/100`. |
| VerifyScratchBoxL | Box_000 L 30.43 → 40.43 | 1 | The kernel rejects a lower bound the certified interval evaluation does not support (`4043/100 ≤ (ieval ...).lo` fails). The raised bound may still be mathematically true. |
| VerifyScratchBoxK | Box_000 K0 30.4634 → 30.1634 | 1 | The kernel rejects a K bound below the certified r_d bracket (`c/(100·0.73·rdIv.lo) ≤ 30.1634` fails). |
| VerifyScratchMain36 | threshold → 36.2897 | 1 | **Not a negative control. The statement is true** (my profile minimum at h ≥ 0.73 is 64.91). It fails only at slab `Ref_R101_400_R51_200` (Om ∈ [0.2525, 0.255]), where L = 36.02. The structure's slack is 0.73 in the tightest slab and 1.53 in the tightest box (`Box_048`, L + prior = 36.8225). |

- **The suggested h ≥ 0.72 control is also not a negative control.** The claim is true there too: my
  profile minimum at h = 0.72 is 42.98 > 35.29. It also cannot reuse the boxes, which assume h ≥ 0.73.

## 4. Independent numerics (my own scipy + mpmath code, official files only)

```
global best fit: Om=0.297462 h=0.685895 wb=0.0221800  chi2 = 10.271041   (certified upper bound 10.2897: slack 0.0187)
h=0.72 profile min 42.9829 (Om 0.3053, wb 0.02441)
h=0.73 profile min 64.9109 (Om 0.3076, wb 0.02502)  margin over 35.2897 = 29.62, Δχ² vs global = 54.64
h=0.75 profile min 125.196 (Om 0.3120, wb 0.02619)  margin 89.91
h=0.80 profile min 367.164 (Om 0.3223, wb 0.02883 -> outside 7σ, covered by prior tail in Lean)  margin 331.87
h=1.00 profile min 2343.61 (Om 0.3503, wb 0.03615)  margin 2308.3
H0 at profile Δχ² = 25 vs global min: 71.571 ; H0 at profile chi2 = 35.2897: 71.572
C10 (BBN mean 0.0282): profile chi2 at h = 0.73 = 10.273 < 35.29 -> the claim is genuinely FALSE there
C9 (H0 = 68.59 point): chi2 = 10.271 < 35.29 -> genuinely false there
```
The preregistration's prediction ("73 at ~7σ") is consistent with these numbers: Δχ² = 54.6, √ ≈ 7.4.

## 5. Overclaim scan of result.json and the commit message

1. **C8.** The certified r_d bracket has relative width 2.29e-10. The float value sits 1.17e-10 and 1.12e-10
   from its two ends. The preregistered criterion, "agrees ... to 1e-10 relative", is therefore shown only to
   about 1.2e-10. Report it as "the bracket contains the float; width 2.3e-10" or as a marginal miss, not as a
   pass at 1e-10.
2. **C9 and C10 are planner-level controls, not Lean controls.** The Python planner ran out of its 300-box
   budget (291 tried, 0 passed). That shows the pipeline *did not* certify, not that Lean *rejected* a proof.
   My numerics show that both target statements are actually false, so the controls are meaningful.
   result.json should say "planner (Python) level" explicitly. The commit message's "not certifiable" is
   acceptable only with that qualifier.
3. **Scope wording to keep.** The model is flat ΛCDM with radiation off in E(z). The Aubourg eq. 16 fit is
   calibrated on CAMB, which includes radiation, so the model is internally mixed; the effect is ~1e-4 in
   E(2.33). ω_ν is fixed, Σm_ν = 0.06 eV, and neutrinos are treated as matter in E(z). The likelihoods are
   Gaussian. Om ∈ [0, 1]. This is a certified version of a known tension, not a new measurement: the claim is
   about this model as coded, not about CAMB r_d or about the sky. result.json `scope` covers most of this;
   add Om ∈ [0, 1] and the CAMB-calibration caveat.
4. **Conservative bound.** The certified statement (χ² > U + 25) is much weaker than the truth: Δχ² = 54.6 at
   H0 = 73, and the Δχ² = 25 crossing is at H0 ≈ 71.6. A write-up should not read "H0 ≥ 73 excluded at 5σ" as
   the measured boundary of the tension.
5. **Commit message phrase.** "for all omega_b" is correct: the theorem holds for all real ω_b, which is
   stronger than the preregistered ω_b > 0 with ω_cb > 0. Say that ω_b ≤ 0 is covered by the BBN prior tail.
6. **Trust base.** The P2 modules are kernel-checked now (fresh build above), but I did not separately audit
   P2's preregistration or results. This report verifies the P3 statement and its proof only.
7. **Missing caveat.** H11 (H0 ≤ 64) was not attempted, as result.json correctly states. Do not cite a
   two-sided certified interval.

## Cleanup
All `VerifyScratch*.lean` files were removed (`mkctl.py clean`). The controls were compiled without `-o`, so
they wrote no oleans. Nothing was written into the producer's `.olean_out`. `git status` matches the session
start, apart from this file.
