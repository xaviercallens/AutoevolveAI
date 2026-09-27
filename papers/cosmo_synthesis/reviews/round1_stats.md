# Referee report, round 1 of 3 — statistics and cosmology lens

Manuscript: `papers/cosmo_synthesis/cosmo_synthesis.tex` (PDF built 2026-09-27, 17 pages, 2 pdflatex passes, rc 0, no undefined references; the 19 warnings are hyperref Unicode-in-bookmark and `h`→`ht` float notices).
Referee: automated model referee (Claude, Claude Code), not a person. Everything below is from tool output produced in this session; nothing is from memory.

Recommendation: **minor revision**. No claim in the paper was found false or unsupported. Every number I checked traces to a result JSON, every re-fetched target matches its source, and every fit or control I re-ran reproduced bit-for-bit. Two issues are labelled *major* because they change how the headline PASS/PARTIAL labels and the DR1 row should be read; both are fixable with a paragraph and one added comparison, not new analysis.

## 1. What was re-run (all in an isolated `/tmp/ref_r1` tree; nothing under `results/` or on disk 2 was written)

| Script (committed copy) | Output compared with | Result |
|---|---|---|
| `scripts/desi_dr2_bao/controls.py` | `results/desi_dr2_bao/controls.json` | identical ignoring `generated_at` (6 positive-control entries, NC1–NC5, GL validation) |
| `scripts/desi_dr2_bao/mcmc_fit.run()` for DR2_LCDM, DR2_wCDM, DR1_LCDM | `results/desi_dr2_bao/fit.json` | means, stds, corr and DR1 Ω_m identical to the last digit (diff 0.0); CONVERGED, n=20000, ESS 21170/14859/19987; 60/57/41 s wall |
| `scripts/bao_bbn_h0/fit_real.py` (full, chains redirected to /tmp) | `results/bao_bbn_h0/fit.json` | 0 differing leaves (ignoring timestamps/paths/hashes/runtime); verdicts PASS/PARTIAL/PASS/PARTIAL reproduced with identical H0 |
| `scripts/bao_bbn_h0/control_n4.py run` | `results/bao_bbn_h0/controls/N4.json` | identical (ΔH0 = 0.16367, Δχ² = −5.19e−5) |
| `scripts/eboss_vs_desi/fit_eboss_vs_desi.py` | `results/eboss_vs_desi/fit.json` | 0 differing leaves; pulls, N_σ = 0.8767, KDE 0.9394 identical |
| `papers/cosmo_synthesis/gen_numbers.py` | all `gen_*.tex`, `number_manifest.json` | sha256-identical after regeneration (389 macros, 406 manifest rows) |

Note: identity to the last digit is expected from fixed seeds and the same code path; it establishes reproducibility of the artifacts from the committed scripts, not independent correctness (the paper says the same about the H0 secondary).

## 2. Targets re-fetched from the source papers (alphaXiv `answer_pdf_queries`, 2026-09-27)

All match the preregistrations and the PDF:
- arXiv:2503.14738v3: eq. (17) Ω_m = 0.2975 ± 0.0086, hr_d = 101.54 ± 0.73 Mpc, r = −0.92; Table V wCDM "DESI" 0.2969 ± 0.0089, w = −0.916 ± 0.078; DESI+BBN 0.2977 ± 0.0086, H0 = 68.51 ± 0.58; eq. (19) 68.51 ± 0.58; Sec. III.C.1 χ²/dof = 10.2/(13−2); Sec. V priors "match those given in Table 2 of [38]"; Sec. III.C.1 assumes *perfect correlation* between DR1 and DR2 for its distance-level comparison.
- arXiv:2404.03002v3: eq. (4.1) 0.295 ± 0.015, 101.8 ± 1.3; Sec. 6 r_d h = 101.9 ± 1.3 (ΛCDM); Sec. 8 101.8 ± 1.3; eq. (4.4) and Table 3 68.53 ± 0.80, Ω_m 0.295 ± 0.015; Sec. 4.1 SDSS 0.299 ± 0.016 and r_d h = 100.4 ± 1.3 citing [139]; **Fig. 1 caption: best-fit Ω_m = 0.294 and H0 r_d = 1.0194 × 10⁴ km/s; Sec. 3.2: χ² = 12.66 for 10 dof** (see issue M2).
- arXiv:2007.08991v2: Table IV BAO ΛCDM Ω_DE = 0.701 +0.017/−0.015 (footnote b: BAO constrain r_d H0/c only; no h r_d tabulated, so the "secondary-sourced" flag is right); Table III MGS 4.47 ± 0.17, ELG 18.33 +0.57/−0.62; Sec. III.A: no covariance between eBOSS samples.
- Prior-work claims: ReplicationBench (2510.24591v2) best average score 22% (Sonnet 4.5) on expert/author-written tasks — matches; PRBench (2603.27646v1) 0% end-to-end callback rate and documented data fabrication — matches; cmbagent (2412.00431v2) reproduces ACT DR6 lensing constraints with human feedback at every step and states there is "no way to confirm outputs without redoing the analysis independently" — matches; 2603.08139v2 identifies an error invalidating Theorem 1 of the 2006 2HDM stability paper — matches.

## 3. Numbers in the PDF vs the JSONs

Checked by hand for the abstract and every table (Tables 1–8): all agree with the JSON values to the printed rounding (pulls recomputed independently: DR2 +0.0366/−0.0134/+0.0255/−0.0050; H0 |ΔH0| 0.0351/0.1670/0.0691/0.1714; eBOSS χ² 1.9318, PTE 0.3806, N_σ 0.8767 from the emcee moments; DR1→DR2 nested 0.237σ; strict window 0.259σ/0.188σ; N4 margin 0.0137 = 0.024σ_T1). Figure 1 and Figure 2 are consistent with the JSONs and with the text. Git confirms the provenance statement: all three preregistrations and the amendment first entered git in d58b63c at 19:43:54 UTC, after every fit.

## 4. Issues

### M1 (major, not blocking) — the H0 preregistration tolerances are not coherent, and the PASS/PARTIAL labels inherit that
Location: Sec. 3.2, Sec. 4.3, abstract (iii), Fig. 1 bands.
The gates G1/G2 accept a BAO-only posterior-mean offset of up to 0.25σ in h r_d (0.18 Mpc for DR2, 0.33 Mpc for DR1). Through the same slope the paper itself uses (d ln hr_d / d ln h = 0.49, `fixround_diagnostics.json`), an offset the gate permits propagates to |ΔH0| up to **0.25 km/s/Mpc (DR2) and 0.45 km/s/Mpc (DR1)**, i.e. beyond the strict window (0.15) in both cases and beyond the soft window (0.33) for DR1. So a run can pass every preregistered gate and still be PARTIAL or FAIL on H0 for reasons that have nothing to do with the BBN/r_d step. That is exactly what happened: the G2 h r_d offset of +0.134 Mpc (pull 0.10σ, well inside the gate) implies +0.183 km/s/Mpc, versus the observed T2 offset of +0.167; conversely T1 passes strictly in part because G1 happened to land at −0.020 Mpc (implied −0.027). The paper presents the T2 propagation as a "post-hoc diagnostic" but does not draw the design conclusion: the preregistered strict window was tighter than what the preregistered gates allow, so PASS vs PARTIAL does not isolate the inverse-distance-ladder step. Please say this explicitly next to the verdicts (and in the abstract's "(verdict PARTIAL)"), and note that the amendment kept this hierarchy unchanged. The verdicts themselves must stay as preregistered; only their interpretation needs the sentence.

### M2 (major, not blocking) — the DR1 row compares mismatched estimators although a matched target is in the fetched source
Location: Sec. 4.1, Table 1, Limitations "Estimators".
The paper says the DR1 χ²-minimum is compared with DESI's posterior mean and calls this an "estimator mismatch". The DR1 paper gives the matched quantity: best fit Ω_m = 0.294 and H0 r_d = 1.0194 × 10⁴ km/s (= 101.94 Mpc; Fig. 1 caption) with χ² = 12.66 for 10 dof (Sec. 3.2). Our χ²-min 0.29389 / 101.937 reproduces DESI's best fit to the printed precision (|ΔΩ_m| = 0.0001, |Δhr_d| = 0.003 Mpc), which is a cleaner statement than the 0.07σ/0.11σ pulls against the mean. But our χ²_min = 12.74 differs from DESI's 12.66 by +0.08 on the same data vector and covariance; this is not discussed anywhere. Candidate cause: DESI's CAMB background includes radiation and the 0.06 eV neutrino (the DR2 run measured Ω_m shifts of −0.046σ and +0.032σ from these). Please add the matched comparison and either explain or explicitly flag the 0.08 χ² offset. (For DR2 the χ² target 10.2 is only quoted to one decimal, so the same check cannot be made there.)

### m1 (minor) — abstract wording on the tension bound
"(PTE 0.381, a lower bound because the survey overlap is ignored)": the *N_σ* is the lower bound; the PTE would be an upper bound. Also the bound is model-dependent. With a structured cross-covariance X = ρ·C_S^{1/2}C_D^{1/2} (symmetrised), N_σ rises monotonically from 0.877 (ρ=0) to 0.995/1.155/1.344/1.761 at ρ = 0.2/0.4/0.57/0.8, so the claim holds for that model; state the assumption in one clause.

### m2 (minor) — DR1→DR2 shift: add DESI's own convention
Sec. 4.5 states as fact that "the uncertainty on their difference is the nested one". The preregistration called it an "ideal-nesting approximation", and DESI DR2 (Sec. III.C.1) conservatively assumes perfect correlation for its DR1-vs-DR2 comparison, under which σ_diff = |σ_DR1 − σ_DR2| = 0.0061 and the shift is 0.46σ. All three conventions (0.17σ / 0.24σ / 0.46σ) agree the shift is insignificant; Table 6 should carry the third.

### m3 (minor) — sign and meaning of the CAMB cross-check shift
Sec. 3.1 "a CAMB model with Σm_ν = 0.06 eV shifts it by 0.032σ": in `camb_crosscheck.json` this is (primary-model fit − CAMB truth) = +0.032σ, i.e. the radiation-free, neutrino-free model recovers a *higher* Ω_m than a CAMB-generated vector; a CAMB-based analysis of the real data would therefore sit ~0.03–0.05σ *lower* in Ω_m, in the same direction as the radiation variant (−0.046σ). Stating the direction matters because it would move the DR2 Ω_m pull from +0.037 to roughly −0.01 to −0.04.

### m4 (minor) — "6 positive controls" is a JSON key count
The preregistration defines PC0–PC4 (5); PC0 has two entries (quad and GL). Say "5 preregistered positive controls (6 entries)".

### m5 (minor) — N4 is caught "only barely" and by a different estimator than the verdict
The margin, 0.0137 km/s/Mpc, is 1.3 posterior-mean MC errors of the T1 chain (0.0107), and N4 measures a MAP shift while the verdict uses the posterior mean; the "wrong" model also has *lower* χ² by 5e−5. The abstract's "but the external target does" should read "marginally does".

### m6 (minor) — T2 verdict conditions use gate G1, not G2
`fit_real.py` line 262 passes `res["G1"]["passed"]` into `verdict_T2`; the preregistration defines `gate_G2` "same rule vs DR1 BAO-only" for the second check. G2 passed, so nothing changes, but the deviation should be logged.

### m7 (minor) — fitting-formula accuracy exceeds its stated bound at one point
`aub16_minus_camb_fracs` max |Δ| = 0.029% versus Aubourg's stated 0.021% (valid within 3σ of Planck). The paper quotes 0.029% without noting it exceeds the stated accuracy; one sentence (the point is presumably outside the validity window, as the preregistration anticipated).

### m8 (minor) — referee/fix-round counts
"eBOSS: 7 issues in round 1 (8 of 9 fixed)": the round-1 report has 7 issues, the fix record 9 items because item 7 was split (7a/7b/7c). Say so.

### m9 (minor) — eBOSS ledger rc 0 was obtained against the round-2 referee's stated preference
`referee_report_round2.json` records that the referee "confirm[ed] the current ledger reverted the earlier fix-round attempt that had filled Tier A audits from a model referee to force rc 0" and called rc 1 "the honest outcome"; `fixround2_outcomes.json` r2_8b then re-filled the audits "per the orchestrator's fix-round instruction". The synthesis correctly labels rc 0 as model-audited (Table 8) but should mention that this was done over the referee's objection, since Sec. 3.5 otherwise reads as if the referee endorsed it.

### m10 (minor) — "merged as PR #61" is not evidenced by any artifact
`rust_crosscheck.json` records only commit c46a680 and the README/validation.rs hashes (which I verified match the files on disk). The local rusty-SUNDIALS history shows a merge of origin/main *into* the feature branch, not the PR merge; I could not run git outside the worktree to check origin/main. Either record the merge commit in `rust_crosscheck.json` or drop the PR number from the paper.

### m11 (minor) — "pulls" are not independent-sample significances
Sec. 4 defines pulls as (ours − published)/σ_published without repeating the preregistrations' point that the same data vector, priors and estimator are used on both sides, so σ_published is not the scatter of the difference (the DR2 MC error on the Ω_m mean is 0.007σ). One clause in the first paragraph of Sec. 4 suffices; Fig. 1's grey bands are tolerances, not error bars, and the caption should say so.

## 5. Things I checked that are fine
- Preregistration logic: DR2 and eBOSS tolerance rules applied exactly as preregistered (14/14 criteria recomputed; eBOSS `counts_toward_within_tolerance` excludes the secondary-sourced SDSS h r_d). The H0 amendment leaves targets, tolerances, controls and data unchanged; the locked first attempt's sha256 matches the amendment (b7fe5608…) and the re-run secondary is identical to it.
- Literature band 0.32–1.56σ recomputed from published means over SDSS corr ∈ [−0.95, 0.95]: 0.323–1.559; at the measured SDSS corr −0.88 it is 1.10σ, above the measured 0.877 because the fitted means sit closer than the published ones (1D 0.041σ vs 0.083σ in Ω_m).
- H0 chains: n/(50τ) = 2.0–2.2 and ESS 3109–3353, so the preregistered rule (n > 50τ, ESS ≥ 2000) is met but not by much; the T2 boundary analysis in the paper accounts for the resulting 0.014 MC error.
- Dual-environment Lean table and `lnCleanTwo = 22`, `lnPairs = 7/8`, sorry negative control: consistent with `lean_dual_check.json`. Ledger counts and rc values: consistent with the four `gate_check.json` files (DR1 rc 1 from the DR2 parent-ledger control; H0 rc 1 with exactly two unaudited rows BBNH0-A-0009/0010).
- Guard/pytest strings in Limitations match the log tails (DR2 and eBOSS logs are two separate runs, 1171.89 s and 634.30 s, with the same summary).

## 6. Files written by this review
- `papers/cosmo_synthesis/reviews/round1_stats.md` (this file).
- Scratch only, outside the repo: `/tmp/ref_r1/` (isolated script copies and regenerated outputs), `/tmp/ref_r1_*.py` (setup, drivers, checks, compare).
