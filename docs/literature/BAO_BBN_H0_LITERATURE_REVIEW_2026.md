# Inverse Distance Ladder: H0 from DESI BAO + a BBN omega_b Prior — Literature Review (2026-09-27)

Stage: literature review + preregistration. **No fit of this problem has been run.**
All numbers below were read from the source PDFs through the alphaXiv
`answer_pdf_queries` tool on 2026-09-27. They are not from model recall. Each
number cites the arXiv id and the equation or table. Anything not fetched is
marked UNVERIFIED.

## 1. Method

BAO measure D_M(z)/r_d, D_H(z)/r_d and D_V(z)/r_d. In flat LCDM these fix
Omega_m and the product h*r_d, but not h and r_d separately. Assume standard
pre-recombination physics (N_eff = 3.044, sum m_nu = 0.06 eV, one massive
eigenstate). Then r_d = r_d(omega_b, omega_cb), and a prior on omega_b = Omega_b h^2
from BBN breaks the degeneracy: at fixed Omega_m, r_d ∝ h^(-2*0.2535) (from
Aubourg eq. 16), so h r_d ∝ h^0.493 and h is determined (arXiv:2503.14738
§IV.A; arXiv:2209.14330 §2.1.1 eq. 2.4).

Planned pipeline (the preregistration fixes it):
- **Parameters:** sample (H0, omega_b, Omega_m) with emcee.
- **Priors:** H0 ~ U[20,100], omega_b ~ U[0.005,0.1], Omega_m ~ U[0.01,0.99]. These are the flat priors in DESI DR1 Table 2 (arXiv:2404.03002), which DR2 §V says it adopts. On top of these, the BBN Gaussian omega_b = 0.02218 ± 0.00055.
- **Background H(z):** flat LCDM with photons (T_CMB = 2.7255 K), N_eff = 3.044, and one 0.06 eV neutrino.
  - Primary implementation: astropy `FlatLambdaCDM(m_nu=[0.06,0,0], Neff=3.044)`.
  - Cross-check: an independent manual integrator.
- **Omega_m convention:** DESI's Omega_m includes the massive neutrino (DR1 Table 2 caption; Planck 2018 Table 1 note). So Omega_cb = Omega_m − omega_nu/h^2 with omega_nu = 0.0107 × 0.06 eV (Aubourg text under eq. 16). Astropy's Om0 excludes the massive nu, so Om0_astropy = Omega_m − Onu0.
- **r_d:** Aubourg et al. 2015 eq. 16, which is CAMB-calibrated (§3).
- **Reported statistic:** posterior mean ± standard deviation. This matches DR2 Table V ("marginalized posterior means and 68% credible intervals"). It is not a chi^2 best fit.

## 2. Data (sha256 in `results/bao_bbn_h0/preregistration.json`)

| Role | File (under `/mnt/disks/disk-socrateai-local-1/dualscale-data-r3/desi_sdss_bao/`) | Source |
|---|---|---|
| Primary | `desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_{mean,cov}.txt` (13 points, z = 0.295…2.33, BGS D_V + 6 × (D_M, D_H) incl. Lyα) | DESI DR2, arXiv:2503.14738 / 2503.14739 (per local README.md) |
| Second check | `desi_2024_gaussian_bao_ALL_GCcomb_{mean,cov}.txt` (12 points, DR1, DESI only, no SDSS) | DESI DR1, arXiv:2404.03002 |

## 3. Sound-horizon formula and its accuracy

**Primary: Aubourg et al. 2015, arXiv:1411.1074, eq. 16** (fetched):

    r_d ≈ 55.154 exp[−72.3 (omega_nu + 0.0006)^2] / (omega_cb^0.25351 omega_b^0.12807)  Mpc

- Stated accuracy (verbatim): "accurate to 0.021% for a standard radiation background with N_eff = 3.046, sum m_nu < 0.6 eV, and values of omega_b and omega_cb within 3σ of values derived by Planck."
- Convention: CAMB's r_d ("we adopt the CAMB convention for r_d"). Other conventions differ by 1–2%, which is why a CAMB-calibrated formula is required: DESI computes theory with CAMB (DR2 §V).
- omega_nu = 0.0107 (sum m_nu / 1 eV).

**N_eff mismatch (3.044 here vs 3.046 in the calibration):**
- Aubourg eq. 17 gives the slope r_d ∝ 1/[1 + (N_eff − 3.046)/30.60].
- A shift of −0.002 changes r_d by +0.0065%. This is negligible, and it is logged, not corrected.

**Where the stated accuracy applies.** Checked numerically in `scripts/bao_bbn_h0/prereg_helpers.py`, with output in `results/bao_bbn_h0/prereg_helper_output.json`:
- The Planck-2013 uncertainties Aubourg refers to were **not fetched** (UNVERIFIED). As a proxy we use Planck 2018 (arXiv:1807.06209 Table 2, TT,TE,EE+lowE): omega_b = 0.02236 ± 0.00015 and Omega_m h^2 = 0.1432 ± 0.0013.
- **omega_b falls outside the window.** The BBN prior's ±2σ span, [0.02108, 0.02328], is wider than the proxy 3σ window [0.02191, 0.02281]. For part of the prior volume the 0.021% figure therefore **does not apply**, and the systematic declared below is a *proxy*, not a quoted accuracy.
- **omega_cb falls inside, barely.** At DESI's published DESI+BBN centre (Omega_m = 0.2977, H0 = 68.51), omega_cb = 0.13909. That is −2.67σ from the Planck proxy, inside the 3σ window.

**CAMB anchor check** (sourced reference value, not a fit):
- Planck 2018 Table 1 Plik best fit is a single CAMB model: omega_b = 0.022383, omega_c = 0.12011, r_drag = 147.049 Mpc.
- Eq. 16 gives 147.020 Mpc there, which is **−0.020%**. This agrees with the stated 0.021%.
- DESI eq. 2 gives 147.025 Mpc there, which is **−0.016%**. This uses eq. 2's own pivot convention, explained below.

**Addendum (fix round, 2026-09-27, after referee review): Planck 2018 posterior-mean r_drag.** Re-fetched with alphaXiv answer_pdf_queries on arXiv:1807.06209 and arXiv:2404.03002:
- Planck 2018 Table 1 r_drag row: Plik best fit 147.049 | Plik [1] 147.09 ± 0.26 | CamSpec [2] 147.26 ± 0.28 | +0.6 | Combined 147.18 ± 0.29.
- Planck 2018 Table 2, TT,TE,EE+lowE+lensing column (68% limits): Omega_b h^2 = 0.02237 ± 0.00015, Omega_c h^2 = 0.1200 ± 0.0012, H0 = 67.36 ± 0.54, r_drag = 147.09 ± 0.26 Mpc.
- arXiv:2404.03002, text before eq. (4.3): "Directly calibrating the BAO standard ruler using the value r_d = 147.09 ± 0.26 Mpc obtained from using all CMB and CMB lensing information [15] gives H0 = (69.29 ± 0.87)".
- So the amendment's "published Planck 2018: 147.09 +- 0.26" is the Table 1/Table 2 posterior mean. An earlier version of this project's paper said this value was not in the fetched sources; that was wrong (the Table 1 row quoted above for 147.049 is the same row).

**Secondary formula (sensitivity variant only): DESI DR2 eq. 2** (arXiv:2503.14738):

    r_d = 147.05 Mpc (omega_b/0.02236)^-0.13 (omega_bc/0.1432)^-0.23 (N_eff/3.04)^-0.1

- DR2 states no accuracy for it.
- Brieden, Gil-Marín & Verde 2023 (arXiv:2212.04522) eq. 3.4 is **the same power law**, citing Schöneberg et al. 2022 (arXiv:2209.14330) eq. 2.4. It is therefore not an independent second formula. Schöneberg+2022 says the scaling comes from numerical calculations (their ref. [21], a PhD thesis) and gives no percentage accuracy. Eq. 2's accuracy is **UNVERIFIED**.
- **Neutrino convention of eq. 2 (verified).** Eq. 2's pivots (0.02236, 0.1432, 147.05) are exactly the Planck 2018 Table 2 TT,TE,EE+lowE column. In that column 0.1432 is Omega_m h^2 *including* the 0.06 eV neutrino.
  - Test at the Planck Table 1 best fit: feeding eq. 2 the neutrino-inclusive Omega_m h^2 = 0.14314 gives −0.016% against CAMB. Feeding it the neutrino-exclusive omega_cb gives +0.088%.
  - So eq. 2 is always fed omega_cb + omega_nu, and eq. 16 is fed omega_cb.
  - (A first draft of this review used the wrong convention. It was corrected before any fit.)
- The two formulas differ at most by 0.233%, over omega_b ∈ BBN ± 3σ and omega_cb ∈ [0.130, 0.155]. The corners of that box lie outside eq. 16's validity window, so this maximum is a deliberately conservative bound.
- **Anchor B.** At DESI's centre, with omega_b set to the BBN prior centre as a proxy (DR2 does not quote the DESI+BBN posterior omega_b):
  - h·r_d = 101.46 Mpc from eq. 16, versus the BAO-only value hr_d = 101.54 ± 0.73 (DR2 eq. 17). That is −0.077%, or 0.11σ.
  - Eq. 2 gives 101.41 Mpc (−0.131%).
  - Eq. 2 and eq. 16 differ by −0.053% at that point.
  - This is a loose consistency check. A function of posterior means is not a posterior mean.

A text inconsistency in DR2: page 22 says the DESI+BBN result assumes r_d "through eq. (2)", but §V says theory is computed with CAMB. We treat CAMB as authoritative, which is why the CAMB-calibrated eq. 16 is primary.

## 4. BBN prior (exact value DESI uses)

- DR2 eq. 14 (arXiv:2503.14738 §IV.A): **Omega_b h^2 = 0.02218 ± 0.00055** in LCDM. The same prior is used in DR1 eq. 2.8 (arXiv:2404.03002 §2.4.1).
- Origin: Schöneberg 2024, arXiv:2401.15054, eq. 5.1. It is the PRyMordial code in NACRE II mode, marginalised over nuclear-rate uncertainties, with PDG Aug-2023 light-element abundances (10^5 D/H = 2.547 ± 0.029, Y_P = 0.2450 ± 0.0030, Table 1).
- The N_eff-free variant (0.02196 ± 0.00063, eq. 15 / eq. 5.3) is **not** used, since N_eff is fixed.
- The prior is taken as an independent Gaussian on omega_b.

## 5. Targets (fetched)

| Target | Value | Source | Variant |
|---|---|---|---|
| **T1 (headline)** H0, DESI DR2 BAO + BBN, flat LCDM | **68.51 ± 0.58** km/s/Mpc | arXiv:2503.14738 eq. (19) and Table V row "DESI+BBN" | BAO+BBN only, **no CMB θ\*** |
| T1b Omega_m, same run | 0.2977 ± 0.0086 | 2503.14738 Table V | |
| **T2 (second check)** H0, DESI DR1 BAO + BBN | **68.53 ± 0.80** km/s/Mpc | arXiv:2404.03002 eq. (4.4), Table 3; also quoted in 2503.14738 §VI | BAO+BBN only, no θ\* |
| T2b Omega_m, DR1 DESI+BBN | 0.295 ± 0.015 | 2404.03002 Table 3 | |
| G1 (gate) DR2 BAO-only | Omega_m = 0.2975 ± 0.0086, hr_d = 101.54 ± 0.73 Mpc, r = −0.92 | 2503.14738 eq. (17) | uncalibrated |
| G2 (gate) DR1 BAO-only | Omega_m = 0.295 ± 0.015, r_d h = 101.8 ± 1.3 Mpc | 2404.03002 §8, p. 46 (§6 on p. 36 gives 101.9 ± 1.3, an internal 0.08σ inconsistency; 101.8 is used) | uncalibrated |

Values documented but **not** targets:
- DR2 DESI+BBN+θ\* 68.45 ± 0.47 (eq. 20).
- DR1 DESI+BBN+θ\* 68.52 ± 0.62 (eq. 4.5; this is the number in the DR1 abstract, so a careless comparison would pick it up).
- DR1 BAO + r_d(CMB) 69.29 ± 0.87 (eq. 4.3).
- DR1 (DESI+SDSS)+BBN 67.98 ± 0.75 (eq. A.2), which uses SDSS data we do not fit.
- DR1 free-N_eff variant 68.5 ± 1.5 (§6).

Internal discrepancy: DR2 §IX (Conclusions) states 68.50 ± 0.58, while eq. 19 and Table V state 68.51 ± 0.58. We compare to **eq. 19 / Table V (68.51)**. The 0.01 difference is far below the tolerance.

Context, not targets:
- Schöneberg+2022 (arXiv:2209.14330, Table 1) found SDSS-era BAO+BBN H0 = 67.64 +0.94/−1.03 with a full BBN likelihood.
- Aubourg+2015 used an older BBN prior, omega_b = 0.02202 ± 0.00046.

## 6. Known systematics

1. **r_d fitting formula vs DESI's CAMB.**
   - Measured size: 0.020% at the Planck best-fit anchor. It is unquantified for omega_b outside the Planck 3σ window.
   - Propagation: δH0/H0 ≈ −δr_d/r_d / 0.493, so each 0.1% in r_d moves H0 by about 0.14 km/s/Mpc.
   - CAMB version and recombination-code drift since 2015 is **not measurable here**: CAMB/CLASS are not installed.
2. **omega_b posterior vs prior.** BAO carry little omega_b information, so the omega_b posterior ≈ prior. This is not a systematic, but it means anchor B used the prior centre.
3. **Background radiation and massive nu in H(z).** Radiation is about 0.1% of H^2 at z = 2.33. It is modelled. A no-radiation variant is run as a sensitivity check.
4. **Statistic.** DESI reports posterior means from Cobaya MCMC with R−1 < 0.01 or ESS ≳ 10^3 (DR2 §V). The Monte-Carlo error on the mean is ~σ/√ESS ≈ 0.02 km/s/Mpc.
5. **Gaussian BAO likelihood.** We use the published Gaussian compressed mean and covariance, the same ones Cobaya's DESI BAO likelihood reads. There is no extra non-Gaussianity treatment.
6. **Model dependence.** The result assumes flat LCDM and standard pre-recombination physics (DR2 p. 22). It is not a test of early-universe extensions.

## 7. What counts as failure

These criteria are fixed in the preregistration.
- The positive control fails to recover the injected parameters.
- Any negative control passes when it should fail.
- The DR2 BAO-only gate G1 is off by more than 0.25σ in Omega_m or hr_d.
- |H0_ours − 68.51| exceeds the soft tolerance (0.33 km/s/Mpc). A result between the strict tolerance (0.15) and the soft tolerance is reported as **PARTIAL**, not PASS.

How the tolerances are built:
- DESI used the same data vector, BBN prior and flat priors. σ_pub is therefore not independent noise on the difference, and the tolerances come from the systematic budget instead.
- **Strict tolerance (0.15 km/s/Mpc):** sqrt(σ_sys,strict^2 + 0.05^2).
  - σ_sys,strict = 0.10% of r_d, which is 0.139 km/s/Mpc in H0. It is a proxy, set by the −0.020% anchor rounded up.
  - 0.05 km/s/Mpc is the Monte-Carlo and numerics allowance.
  - In units of the published errors: 0.26σ for T1 and 0.19σ for T2.
- **Soft tolerance (0.33 km/s/Mpc):** the same construction with the conservative 0.233% box bound, giving 0.324 km/s/Mpc from the formula term.
- The recovered σ(H0) is outside ±15% of 0.58.

A failure is reported, not hidden.

## 8. Lean idea (for a later stage; not written yet)

Module: `formal/ANSE/BAO_BBN_H0.lean`, with pinned imports as in `formal/ANSE/BAO_FlatLCDM.lean` and in-file `#print axioms`, per LL.md §11b. Planned statements:
- For A, a, b > 0, the map omega_cb ↦ A · omega_cb^(−a) · omega_b^(−b) is positive and strictly antitone on (0, ∞). This is the monotonicity of r_d in omega_cb, and hence in Omega_m at fixed h.
- The algebraic identity H0 = 100 h.
- h·r_d(h) is strictly increasing in h when a·2 < 1. With a = 0.25351 the exponent is 1 − 2a > 0. This is the property that makes the BBN calibration identify h.

The statements will be reviewed for faithfulness before any proof (LL.md §7).
