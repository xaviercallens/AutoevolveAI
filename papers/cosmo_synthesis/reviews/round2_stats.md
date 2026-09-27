# Referee report, round 2 of 3 — statistics and cosmology lens

Manuscript: `papers/cosmo_synthesis/cosmo_synthesis.tex` / `.pdf` (revision after round 1; 21 pages, built 2026-09-27 21:45).
Referee: automated model referee (Claude, Claude Code), not a person. Everything below comes from tool output produced in this session (2026-09-27, 21:45–22:00 UTC); nothing is from memory. Scratch work lives only under `/tmp/ref_r2/` and `/tmp/r2_*`; nothing under `results/<run>/` was written. The only files touched under `papers/cosmo_synthesis/` are the regenerated `gen_*.tex`, `number_manifest.json`, `fig_*.{pdf,png}` (byte-identical, see Sec. 1) and this report.

Recommendation: **minor revision**. No claim in the paper is false or unsupported. All round-1 statistics issues (S-M1, S-M2, S-m1…S-m11) are fixed as the response letter says; I re-derived each of the new numbers and re-ran the two new synthesis scripts. What remains is one interpretive overstatement in Sec. 3.2 (the T2 PARTIAL is *attributed* to the gate mechanism, which the numbers only make *consistent with* it), one missing term in the T2 boundary discussion, and a handful of one-sentence items.

## 1. What was re-run

| Script (copied unchanged into `/tmp/ref_r2/`, sha256 checked against the committed file) | Output compared with | Result |
|---|---|---|
| `results/cosmo_synthesis/round1_response_checks.py` (new since round 1; only `WT`/`OUT` paths patched so it reads the worktree and writes to /tmp) | `results/cosmo_synthesis/round1_response_checks.json` | 0 differing leaves except `rust_pr61.queried_utc` (timestamp of the `gh pr view 61` call, state still MERGED, merge commit 7c9c3c3) |
| `results/cosmo_synthesis/dr1_chi2_offset_check.py` (new since round 1) | `results/cosmo_synthesis/dr1_chi2_offset_check.json` | 0 differing leaves (χ² 12.7405 / 12.7373 / 12.7374 / 12.7378; offsets +0.0805 … +0.0778) |
| `scripts/desi_dr2_bao/controls.py` | `results/desi_dr2_bao/controls.json` | 0 differing leaves ignoring `generated_at`; `pipeline_validated: True` |
| `scripts/bao_bbn_h0/control_n4.py run` | `results/bao_bbn_h0/controls/N4.json` | 0 differing leaves (ΔH0 = 0.163672, Δχ² = −5.19e−5) |
| `scripts/eboss_vs_desi/fit_eboss_vs_desi.py` (three emcee chains) | `results/eboss_vs_desi/fit.json` | 0 differing leaves ignoring `generated_at` and chain paths (N_σ 0.876725, PTE 0.380636, pulls identical) |
| `papers/cosmo_synthesis/gen_numbers.py` (in place) | all 13 `gen_*.tex` + `number_manifest.json` | sha256-identical after regeneration (439 macros, 459 manifest rows) |
| `papers/cosmo_synthesis/make_figures.py` (in place) | `fig_pulls.png`, `fig_h0.png` | sha256-identical |

The first two attempts of `controls.py` and `dr1_chi2_offset_check.py` failed in my scratch tree only because `dr2_model.py` imports `scripts/bao_flcdm/fit_desi_bao.py`, which I had not copied; after copying it (sha256 identical) both ran clean. As in round 1: identity to the last digit is expected from fixed seeds and the same code path; it establishes that the committed scripts produce the committed JSONs, not independent correctness.

## 2. Targets re-fetched from the source papers (alphaXiv `answer_pdf_queries`, 2026-09-27)

All match the preregistrations, the JSONs and the PDF:
- arXiv:2503.14738v3 — eq. (17) Ω_m = 0.2975 ± 0.0086, hr_d = (101.54 ± 0.73) Mpc, r = −0.92; Table V wCDM "DESI" 0.2969 ± 0.0089, w = −0.916 ± 0.078; DESI+BBN 0.2977 ± 0.0086, H0 = 68.51 ± 0.58; eq. (18) is the (Ω_m, r_d h) parameter-difference χ² with Cov_A + Cov_B, converted to a PTE; eq. (19) 68.51 ± 0.58; Sec. III.C.1 best-fit χ²/dof = 10.2/(13−2); Sec. V priors "match those given in Table 2 of [38]"; **footnote 12: C = √(N_DR1/N_DR2) for galaxy and quasar clustering measurements, C = 0.61 for Lyα** (see m1); Sec. III.C.2: C ≈ 0.57 for LRG2 vs eBOSS LRG, and the sentence "the assumption of no correlation … sets a lower limit of the discrepancy", which supports the paper's lower-bound framing.
- arXiv:2404.03002v3 — eq. (4.1) 0.295 ± 0.015 and 101.8 ± 1.3; Fig. 1 caption best fit Ω_m = 0.294, H0 r_d = 1.0194 × 10⁴ km/s; Sec. 3.2 χ² = 12.66 for 10 dof (12 points, 2 parameters); eq. (4.4) and Table 3 68.53 ± 0.80 with Ω_m 0.295 ± 0.015; Sec. 6 r_d h = 101.9 ± 1.3 (ΛCDM) vs Sec. 8 101.8 ± 1.3; Sec. 3.3 "no significant difference in Ω_m and a shift of just ∼1σ in r_d h"; Sec. 4.1 SDSS 0.299 ± 0.016 and 100.4 ± 1.3 citing [139]; Table 2 priors U[0.01,0.99], U[10,1000], U[20,100], U[0.005,0.1]; Sec. 2.5 convergence rule R−1 < 0.01 and ESS ≳ 10³ (relevant to m2).
- arXiv:2007.08991v2 — Table IV BAO ΛCDM Ω_DE = 0.701 +0.017/−0.015 (footnote b: BAO constrain r_d H0/c only; no h r_d tabulated, so the "secondary-sourced" flag on SDSS hr_d is correct); Sec. III.A: no covariance between eBOSS samples.
- arXiv:1411.1074v3 — eq. (16) with exponents 0.25351 / 0.12807, "accurate to 0.021% for a standard radiation background with N_eff = 3.046, Σm_ν < 0.6 eV, and values of ω_b and ω_cb within 3σ of Planck"; ω_ν = 0.0107 Σm_ν/eV; eq. (17) carries the factor [1 + (N_eff − 3.046)/30.60] (relevant to m4).

## 3. Numbers in the PDF vs the JSONs (independent recomputation, `/tmp/r2_independent_checks.py`, no project code imported)

Recomputed from the raw JSON entries and compared with the macros: all 8 DR2 pulls and width ratios; the DR2 MC error (0.0068σ → "0.007"); n/(50τ) = 13.3; the three DR1→DR2 conventions 0.237 / 0.167 / 0.462; the nested identity (s1² + s2² − 2·(s2/s1)·s1·s2 = s1² − s2², exact); the CAMB- and radiation-shifted pulls 0.0048 / −0.0095; all 8 H0 |ΔH0|, pulls, σ ratios and the four verdicts (PASS/PARTIAL/PASS/PARTIAL re-derived from the preregistered rule text); strict window 0.259σ / 0.1875σ; T1/T2 MC errors 0.01065 / 0.01398; T2 margin 0.01697; G1/G2 pulls; gate propagation 0.2509 / 0.4451 and implied shifts 0.1829 (101.8) / 0.0459 (101.9); the slope 0.491 (I first got 0.394 by wrongly subtracting ω_b from ω_cb — Aubourg's ω_cb includes baryons, so the paper's 0.49 = 1 − 2·0.2535·(Ω_m h²/ω_cb) is right); N4 margin 0.01367 = 1.28 T1 MC errors = 0.024σ_pub; the re-budget 0.0502; 0.0292% and 2 of 5 points; N3 ratio 20.99; primary-minus-secondary −0.0340; eBOSS χ² 1.9318 = −2 ln PTE, PTE 0.3806, N_σ 0.8767, 1D 0.0405 / 0.668; the four eBOSS pulls; the literature band 0.323–1.559 recomputed from published means over corr ∈ [−0.95, 0.95]; N_σ = 1.344 at ρ = 0.57 with the paper's √C_S√C_D model; DR1 pulls −0.074 / 0.105 and χ² offset 0.0805; Rust CVODE − Python Ω_m = −3.18e−5 = 0.37% of σ. Tables 1–10 and Figs. 1–2 agree with the JSONs to the printed rounding. Git provenance of the preregistrations and the amendment (first committed in d58b63c, after every fit) was established in round 1 and is stated in the paper.

## 4. Round-1 statistics issues: verified fixed

S-M1 (gate/strict incoherence): paragraph in Sec. 3.2, abstract sentence, Limitations bullet, numbers reproduced by the new script — fixed, but see M1 below on one sentence of it. S-M2 (matched DR1 target and χ² offset): Fig. 1-caption best fit and Sec. 3.2 χ² = 12.66 re-read correctly; four-model offset check re-run identically; offset honestly left open — fixed. S-m1 (N_σ lower / PTE upper bound, model-dependent, positive cross-covariance): fixed. S-m2 (DESI's own convention): fixed, and the response's reading of footnote 12 is correct for galaxies/quasars (m1). S-m3 (CAMB sign and numeric consequence): the paper's 0.005 / −0.009 are right; my round-1 range "−0.01 to −0.04" was wrong. S-m4…S-m9, S-m11: fixed as stated. S-m10 (PR #61): `gh pr view 61` result recorded; re-queried, still MERGED at 2026-09-27T17:29:02Z, merge commit 7c9c3c3.

## 5. Issues

### M1 (major, not blocking) — Sec. 3.2 attributes the T2 PARTIAL to the gate mechanism; the numbers only make it consistent with it
Location: Sec. 3.2 ("The T2 PARTIAL is this mechanism: the G2 offset is 0.134 Mpc (pull 0.10), which implies 0.183 km/s/Mpc against the observed 0.167."), echoed in Limitations.
The implied shift depends on which DESI DR1 hr_d one takes as the reference: 0.183 for the Sec. 8 value 101.8, 0.046 for the Sec. 6 value 101.9 (the paper's own Sec. 4.3 lists both), and 0.11–0.25 across the ±0.05 Mpc rounding interval of 101.8 alone (recomputed: 0.252 at 101.75, 0.114 at 101.85). In addition the G2 chain has 2000 steps (n/(50τ) = 1.42, ESS 2114), so the MC error on the G2 hr_d mean is 0.028 Mpc, i.e. ±0.038 km/s/Mpc on the implied value. So the mechanism explains anywhere between ~0.05 and ~0.25 of the observed 0.167, and the closeness of 0.183 to 0.167 is not evidence for it. The design conclusion of the paragraph (the gate admits up to 0.25 / 0.45, larger than the strict window, so PASS vs PARTIAL does not isolate the BBN/r_d step) is correct and unaffected. Please change "The T2 PARTIAL is this mechanism" to "The T2 PARTIAL is consistent with this mechanism" and add the 101.9 alternative (0.046) and the G2 MC error in the same sentence, so Sec. 3.2 and Sec. 4.3 say the same thing.

### m1 (minor) — footnote 12 of DR2 applies C = √(N_DR1/N_DR2) to galaxy and quasar tracers only
Sec. 4.5(a) says DR2 "computes σ² = … with C = √(N_DR1/N_DR2) per distance". The footnote says this for galaxy and quasar clustering measurements and uses C = 0.61 for Lyα (estimated as in Appendix F of [22]). Say "per galaxy/quasar tracer (C = 0.61 for Lyα)". The nested-form identity then holds for the galaxy/quasar bins only, which is all the parameter-level argument needs.

### m2 (minor) — T2 boundary: DESI's own sampling error is missing from the comparison
Sec. 4.3 compares the 0.017 margin over the strict window with "our posterior-mean Monte Carlo error of 0.014" only. DESI's DR1 convergence rule is R − 1 < 0.01 and ESS ≳ 10³ (Sec. 2.5, re-fetched), so the MC error on their quoted 68.53 is of order 0.80/√10³ ≈ 0.025, plus ±0.005 from rounding; the preregistration's own `sigma_mc_justification` says exactly this ("~0.02 for DESI and ours"), and `fit.json` `T2_boundary_resolution.note` says "DESI's own MC error is not published, so the strict/soft boundary is not statistically resolved". The paper should carry that sentence: the margin (0.017) is smaller than the combined resolution (≈ 0.03). The verdict stays PARTIAL as preregistered.

### m3 (minor) — DR1 grid cross-check: state that the 0.0018 difference is the grid step
Sec. 4.1: "Two independently coded predictors agree exactly, and a brute-force grid gives Ω_m = 0.2957 and hr_d = 101.79." `fit_desi_bao.py` uses a 141 × 141 grid on [0.20, 0.40] × [90, 115], i.e. steps of 0.00143 in Ω_m and 0.179 Mpc in hr_d; the grid minimum (χ² 12.7562) sits one node from the optimizer minimum (12.7405) along the degeneracy. Without the step size the reader sees a 0.12σ disagreement next to "agree exactly". One clause.

### m4 (minor) — the 0.029% vs 0.021% question is resolvable in one line
Sec. 4.3 says "Our CAMB table uses N_eff = 3.044, which may contribute; we did not resolve this." Aubourg's eq. (17) factor [1 + (N_eff − 3.046)/30.60] gives r_d(3.044)/r_d(3.046) = 1 + 6.5 × 10⁻⁵ (the `fit.json` deviations list already records "+0.0065%, logged not applied"). Applying it, the two offending points move from −0.0292% / −0.0272% to about −0.0227% / −0.0207%: one is at the stated 0.021%, the other inside it. Please either state this arithmetic or keep "unresolved" but not both; the current wording undersells what the run already measured.

### m5 (minor) — P2 (H0 noisy mocks): report the Ω_m pull too
`controls/P2_primary.json` has `pull_Om_mean = −0.131` and `pull_Om_std = 0.944` for 100 mocks (SE of the mean 0.10). The preregistered pass rule covers H0 only, so nothing changes, but Sec. 3.3 quotes only the H0 pull moments; list the Ω_m ones as report-only for completeness.

### m6 (minor) — cite DR2's own lower-bound sentence for the overlap argument
Sec. 4.5(b) argues that the independent-survey N_σ is a lower bound when the cross-covariance is positive. DR2 Sec. III.C.2 says the same for its own distance-level comparison ("the assumption of no correlation is less plausible, it sets a lower limit of the discrepancy"). Citing it strengthens the sentence, and it also makes clear that ρ = 0.57 is the value for the bin pair with the largest overlap, i.e. the illustration is an upper-end one.

## 6. Things I checked that are fine
- Preregistration logic: DR2 14/14 criteria and eBOSS tolerance rule (secondary-sourced SDSS hr_d excluded) recomputed; H0 verdicts re-derived from the rule text; the amendment left targets/tolerances/controls/data unchanged; the locked first attempt's hash still matches (b7fe5608…, Table 10 "yes").
- Preregistration mtimes (UTC): eBOSS 15:54:06, H0 15:54:35, DR2 15:55:09; the eBOSS amendment field says 15:58:00, later than the file's mtime — disclosed in the paper as stated.
- eBOSS positive control: coverage 0.655–0.695, bias < 0.09σ, tension calibration median N_σ = 0.67, KS p = 0.55, 3% of 200 null realizations above 2σ (expected 4.6%) — all within the preregistered thresholds.
- N4 sign and size: ω_ν = 6.4 × 10⁻⁴ left in ω_cdm lowers r_d by ~0.13%, which through 1/0.49 gives ~0.18 km/s/Mpc; measured 0.164. The wrong model has the lower χ² by 5 × 10⁻⁵; the data cannot see it, as the paper says.
- DR2 eq. (18) is what the eBOSS run implements (posterior mean vectors, sum of 2 × 2 posterior covariances, PTE with 2 dof).
- Slope 0.49 is right (ω_cb includes baryons); the propagation formula and the 0.25 / 0.45 admitted shifts reproduce.
- Fig. 1 bands: 0.5σ (DR2, eBOSS), 0.25σ (H0 Ω_m and gates), 0.26σ / 0.19σ (H0 strict window) — as read from the preregistration by `make_figures.py`.
- DR1 χ² offset: the four background models bracket 12.737–12.741 against DESI's 12.66; the paper correctly reports it as unexplained. Nothing in the fetched DR1 text (12 points, 2 parameters, iminuit from the MAP) points to a different data vector, so I have no better candidate than the ones the paper names.

## 7. Files written by this review
- `papers/cosmo_synthesis/reviews/round2_stats.md` (this file).
- Regenerated in place, byte-identical: `papers/cosmo_synthesis/gen_*.tex`, `number_manifest.json`, `fig_pulls.{pdf,png}`, `fig_h0.{pdf,png}`.
- Scratch, outside the repo: `/tmp/ref_r2/` (script copies, their outputs and stdout logs), `/tmp/r2_setup.py`, `/tmp/r2_independent_checks.py`, `/tmp/r2_gen_before.sha`, `/tmp/r2_fig_before.sha`, `/tmp/r2_cosmo_synthesis.txt`.
