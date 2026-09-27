# SDSS/eBOSS DR16 BAO vs DESI DR2 BAO under flat ΛCDM: literature review (2026-09-27)

Problem slug: `eboss_vs_desi`. This stage covers only the literature review and the preregistration. No fit has been run.

## How the sources were read

The primary papers were read through the alphaXiv MCP (`answer_pdf_queries`, which returns PDF page text) on 2026-09-27. Every number in the target tables below was copied from the page text that call returned. The page cited is the PDF page. None of the numbers comes from model recall. The data-file conventions (redshifts, grid formats, the MGS α rescaling) were read from the Cobaya source on GitHub (`CobayaSampler/cobaya`, `cobaya/likelihoods/bao/*.yaml` and `cobaya/likelihoods/base_classes/bao.py`). The local data directory's README says these files come from Cobaya's `bao_data` repository.

| arXiv | Paper | Role |
|---|---|---|
| 2007.08991 (v2) | Alam et al., *Completed SDSS-IV eBOSS: cosmological implications from two decades of spectroscopic surveys* (PRD 103, 083533) | SDSS BAO compilation and SDSS BAO-only flat-ΛCDM target |
| 2503.14738 (v3) | DESI Collaboration, *DESI DR2 Results II: BAO measurements and cosmological constraints* | DESI DR2 target and DESI's statement about consistency with SDSS |
| 2404.03002 (v3) | DESI Collaboration, *DESI 2024 VI* (DR1 cosmology) | Secondary source for the SDSS h r_d value, and the precedent for the tension statistic |
| 2007.08995 (v2) | du Mas des Bourboux et al., *eBOSS DR16 Lyα BAO* | Gaussian summary for Lyα, used only in the sensitivity variant |

## The measurement

BAO measure D_M(z)/r_d, D_H(z)/r_d = c/(H(z) r_d) and D_V(z)/r_d = [z D_M² D_H]^{1/3}/r_d. In flat ΛCDM with E(z) = √(Ω_m(1+z)³ + 1 − Ω_m), BAO-only data constrain exactly two parameters: Ω_m and h r_d. DESI DR2 states this in §V ("When fitting to BAO data only, we sample over Ω_m and the parameter hr_d"). Radiation is negligible at z ≤ 2.33: using the Planck-2016 Ω_r = 7.975e-5 quoted in 2007.08995 Table 2, it changes E(z) by about 0.1%. The planned fit omits it and records that choice.

## Data: the SDSS side (as distributed, from 2007.08991 §III.A and Table III)

The paper states (p.14): "The full likelihood is reported for BAO-only studies in the MGS, ELG, and Lyα forest samples. The BAO-only results for the BOSS galaxy, eBOSS LRG, and eBOSS quasar samples are recorded as a covariance matrix. We refer to the combination of these measurements as the 'BAO' measurements." The eBOSS samples are treated as mutually uncorrelated (p.14): the "expected statistical correlation between clustering measurements derived from the eBOSS samples is negligibly small and we thus include no covariance between them". The same treatment applies to QSO vs Lyα auto vs Lyα×QSO, which was justified with mocks.

| Sample | z_eff | Local file | Likelihood form | Table III BAO-only (Gaussian approx.) |
|---|---|---|---|---|
| MGS | 0.15 | `sdss_MGS_prob.txt` | χ²(α) table, 399 points on α ∈ [0.8005, 1.1985]; α = (D_V/r_d)/4.29720761315 (Cobaya `sdss_dr7_mgs.yaml`) | D_V/r_d = 4.47 ± 0.17 |
| BOSS DR12 galaxies | 0.38, 0.51 | `sdss_DR12_LRG_BAO_DMDH.dat` + `_covtot.txt` (4×4) | Gaussian | D_M/r_d 10.23±0.17, 13.36±0.21; D_H/r_d 25.00±0.76, 22.33±0.58 |
| eBOSS LRG (incl. BOSS z>0.6) | 0.698 | `sdss_DR16_LRG_BAO_DMDH.dat` + `_covtot.txt` (2×2) | Gaussian | D_M/r_d 17.86±0.33; D_H/r_d 19.33±0.53 |
| eBOSS ELG | 0.845 | `sdss_DR16_ELG_BAO_DVtable.txt` | 1D table of (D_V/r_d, likelihood) on [14.88, 22.28]; log-likelihood = ln L (Cobaya) | D_V/r_d = 18.33 +0.57/−0.62 |
| eBOSS QSO | 1.48 | `sdss_DR16_QSO_BAO_DMDH.txt` + `_covtot.txt` (2×2) | Gaussian | D_M/r_d 30.69±0.80; D_H/r_d 13.26±0.55 |
| Lyα auto | 2.334 | `sdss_DR16_LYAUTO_BAO_DMDHgrid.txt` | 2D grid (D_M/r_d, D_H/r_d, likelihood ratio) | D_M/r_d 37.6±1.9; D_H/r_d 8.93±0.28 |
| Lyα × QSO | 2.334 | `sdss_DR16_LYxQSO_BAO_DMDHgrid.txt` | 2D grid | D_M/r_d 37.3±1.7; D_H/r_d 9.08±0.34 |

Gaussian summaries of the non-Gaussian pieces are used only in the documented sensitivity variant and the positive control:
- **ELG**: D_V/r_d(0.845) = 18.33 +0.57/−0.62 (2007.08991 Table III). The variant symmetrises the error to σ = 0.595.
- **Lyα**: the joint auto+cross fit from 2007.08995 eq. (43): D_H/r_d = 8.99 +0.20/−0.19, D_M/r_d = 37.5 +1.2/−1.1, ρ = −0.45. Using this single joint summary instead of two separate Gaussians avoids double-counting auto and cross. The separate summaries are eq. (41), auto: 8.93, 37.6, ρ = −0.49, and eq. (42), cross: 9.08, 37.3, ρ = −0.43.

Recorded now so that a later small offset is not blamed on it after the fact: the DR12 covariance file gives σ(D_H, 0.38) = √0.5307 = 0.73 and σ(D_M, 0.51) = √0.04148 = 0.204. Table III rounds these as 0.76 and 0.21. The planned fit uses the file.

**Files deliberately excluded from the SDSS side:**
- `desi_2024_eboss_gaussian_bao_Lya_GCcomb_{mean,cov}.txt`. This is the DESI DR1 + eBOSS combined Lyα (Cobaya: "DESI BAO results for Lya, in combination with eBOSS"), with values matching 2404.03002 eqs. (3.3)–(3.4): D_M/r_d = 38.80 ± 0.75, D_H/r_d = 8.72 ± 0.14. It contains DESI data, so using it would combine the two surveys, which this problem forbids.
- `sdss_DR12Consensus_bao.dat` + `BAO_consensus_covtot_dM_Hz.txt`. Its z = 0.61 bin overlaps and double-counts the eBOSS LRG sample.
- `*BAOplus*`, `*FS*` and `*final*` files. They carry RSD / fσ8 or full-shape information and are not BAO-only.
- All `desi_2024_*` DR1 files. DR1 is superseded by DR2 and is a subset of it.

## Data: the DESI DR2 side

`desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_{mean,cov}.txt` has 13 data points: BGS D_V; D_M and D_H for LRG1, LRG2, LRG3+ELG1, ELG2, QSO and Lyα. The covariance is block-diagonal and 13×13. This matches 2503.14738 Table IV (p.14), where for example LRG2 at z = 0.706 has D_M/r_d = 17.351 ± 0.177, D_H/r_d = 19.455 ± 0.330 and r = −0.404. DESI's own joint fit: "χ²/dof = 10.2/(13 − 2)" (p.15).

## Target values (exact, sourced)

| Target | Value | Source | Status |
|---|---|---|---|
| SDSS BAO-only flat ΛCDM Ω_DE | 0.701 +0.017/−0.015 | 2007.08991 **Table IV**, row "BAO", ΛCDM block (p.17) | Verified, primary |
| → SDSS Ω_m = 1 − Ω_DE | 0.299 +0.015/−0.017 (asymmetry swaps under the subtraction); symmetric σ = 0.016 used for pulls | derived from Table IV | Verified (derived) |
| SDSS Ω_m (secondary quote) | 0.299 ± 0.016 | 2404.03002 §4.1 (p.23, PDF p.26), citing [139] = 2007.08991 | Verified, secondary; agrees with the primary |
| SDSS h r_d | (100.4 ± 1.3) Mpc | 2404.03002 §4.1 (p.23), citing [139] | **Secondary only.** Not found in the fetched pages of 2007.08991: Table IV footnote b says BAO constrain r_d H_0/c but no value is tabulated. Treat as unverified against the primary. |
| DESI DR2 Ω_m | 0.2975 ± 0.0086 | 2503.14738 **eq. (17)** (p.19) | Verified, primary |
| DESI DR2 h r_d | (101.54 ± 0.73) Mpc | 2503.14738 eq. (17) | Verified, primary |
| DESI DR2 corr(Ω_m, h r_d) | r = −0.92 | 2503.14738, text after eq. (17) | Verified, primary |
| SDSS corr(Ω_m, h r_d) | not published in the fetched sources | none | **Unavailable** |

**DESI DR2 statements on consistency with SDSS** (2503.14738), quoted:
- Abstract: "The DR2 BAO results are consistent with DESI DR1 and SDSS".
- §VI after eq. (17): the DR2 (Ω_m, h r_d) result is "perfectly consistent with them [DR1] as well as with the SDSS and DESI+SDSS results reported in [38]" ([38] = the DESI DR1 cosmology paper).
- §III.C.2 (p.16–17), LRG2 D_M/r_d vs eBOSS LRG: "the discrepancy between the DR2 and SDSS results has reduced from 3σ to ∼2.6σ" assuming a correlation C ≈ 0.57, with a lower limit of 1.9σ assuming no correlation. Against the DESI reanalysis of SDSS it is 2.3σ (C = 0.57) or 1.5σ (C = 0). The conclusions give "within the range 1.5σ to 2.6σ".
- Four-bin comparison (LRG1, LRG2, QSO, Lyα): "The biggest difference we find is 1.49σ for α_iso and 1.69σ for α_AP. The KS statistic is 0.30, p = 0.39. If we conservatively treat SDSS as a pure subsample of DESI DR2 … p = 0.15 … We conclude that there is no significant discrepancy between the DR2 measurements and those from SDSS."
- DR2 no longer mixes DESI and SDSS bins ("we therefore no longer consider any combination of bins picked from DESI and SDSS data").

DR1 precedent (2404.03002 §3.3): DESI DR1 and SDSS give "no significant difference in Ω_m and a shift of just ∼1σ in r_d h".

**No published number exists for the DESI DR2 vs SDSS tension in the (Ω_m, h r_d) plane.** The comparison target is therefore DESI's qualitative claim ("consistent", "no significant discrepancy"). `scripts/eboss_vs_desi/prereg_inputs.py` also computes, from the published means and errors alone, an expectation for this problem's statistic:
- In 1D: Ω_m differs by 0.083σ and h r_d by 0.765σ.
- In 2D: N_σ ranges from 0.32 to 1.56 as the unpublished SDSS correlation is scanned over [−0.95, 0.95]. It is 0.43 at r = −0.5, 0.74 at r = −0.8 and 1.10 at r = −0.9.
- BAO-only posteriors are strongly anticorrelated in this plane (DESI DR2 has r = −0.92), so the upper part of the band is more likely.

This band is an expectation, not a pass criterion.

## Method (planned, following DESI's eq. (18) statistic)

- The two surveys are fitted **separately and never combined**. Parameters are (Ω_m, h r_d), with flat priors Ω_m ∈ [0.05, 0.95] and h r_d ∈ [60, 150] Mpc. Sampling uses emcee. Reported values are posterior mean ± std, the same convention as DESI (§V: "mean and standard deviation when the distributions are symmetric"). The MAP (best fit) is reported alongside.
- Tension: χ² = Δpᵀ(C_SDSS + C_DESI)⁻¹Δp with p = (Ω_m, h r_d). This is 2503.14738 eq. (18) and 2404.03002 eq. (4.2). It is converted to a PTE with 2 dof and then to a two-sided Gaussian N_σ. The 1D parameter-difference significances are reported too.
- Cross-check: a posterior-level parameter-shift statistic, P(Δp) from the two chain sets. It avoids the Gaussian assumption because the SDSS posterior may be non-Gaussian through the grid likelihoods.
- Grid-likelihood rules, matching Cobaya (`base_classes/bao.py`): out-of-range parameters return −∞ for MGS and ELG. The Lyα 2D grids are interpolated in ln L by `RectBivariateSpline`, and bounds are checked explicitly, because the spline extrapolates silently.
- **Replacing the grid likelihoods with their Gaussian summaries** is a documented sensitivity variant. It is not the baseline.

## Known systematics and caveats

1. **Overlapping volumes and correlated samples.** DR2 estimates C ≈ 0.57 between DR2 LRG2 and eBOSS LRG (2503.14738 p.16). The DR1 footprint overlapped about 65% of BOSS (2404.03002 §3.3). The tension formula assumes the two surveys are independent. Positive cross-survey correlation means the true tension is **larger** than the independent-survey figure, so this problem's N_σ is a lower bound on the tension in that respect.
2. **Non-Gaussian SDSS likelihoods** (MGS, ELG, Lyα). eq. (18) needs a Gaussian 2×2 posterior covariance. The posterior-shift cross-check addresses this.
3. **Different samplers and priors.** eBOSS sampled (Ω_m, H0, Ω_b) in CosmoMC's "background" parameterization (2007.08991 App. B), not h r_d directly. This is one reason the reproduction tolerance is 0.5σ rather than tighter.
4. **Asymmetric published errors** on SDSS Ω_m. Pulls use the symmetric 0.016.
5. **BAO pipeline differences.** 2404.03002 §3.3 reports that reprocessing BOSS/eBOSS through the DESI pipeline gives shifts that are "at most a small fraction" of the uncertainties.
6. **Radiation and neutrinos** are neglected in E(z). Both are sub-0.1% at z ≤ 2.33 for BAO ratios. Massive neutrinos are absorbed into Ω_m.

## What would count as failure

Thresholds are fixed in `results/eboss_vs_desi/preregistration.json`:
- The reproduced SDSS Ω_m or DESI DR2 (Ω_m, h r_d) differs from the published value by more than 0.5σ. The SDSS h r_d check is recorded but marked secondary-sourced.
- The positive control fails: parameters injected into synthetic Gaussian-summary data are not recovered (coverage and bias thresholds), or the tension statistic run on two synthetic sets drawn from the same parameters is not calibrated.
- A negative control passes. Each of these must be rejected at its preset threshold:
  - the no-Λ (Einstein–de Sitter) model;
  - a deterministic DESI D_M↔D_H swap, or the DESI covariance divided by 25;
  - an injected distance-scale shift where every DESI ratio is multiplied by 0.93. From the published numbers alone this is expected at ≥ 5.4σ, and the threshold is 3σ.
- The grid-likelihood instrument check fails: the peak and 68% width of each interpolated MGS, ELG and Lyα table must match its published summary. As a paired negative, dropping the MGS α rescaling must fail that check.
- The two independent prediction implementations disagree by more than 1e-4 (relative).
- An N_σ ≥ 2 for DESI DR2 vs SDSS is **not** a pipeline failure. It would be a scientific disagreement with DESI's "no significant discrepancy" claim, reported as it is, and it counts as a failed replication of that claim.
