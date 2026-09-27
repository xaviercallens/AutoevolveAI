# DESI DR2 BAO: flat ΛCDM, flat wCDM and DR1→DR2 consistency. Literature review (2026-09-27)

Stage: literature review and preregistration. **No fit of this problem had been run
when this document and `results/desi_dr2_bao/preregistration.json` were written.**

Every number below comes from paper text fetched on 2026-09-27 with the alphaXiv MCP
tool `answer_pdf_queries`. Each is cited by arXiv id (with version) plus equation, table
or page. None is taken from memory. Where a value could not be found, this document
says so.

## 1. Sources read

| arXiv id | Role | What was extracted |
|---|---|---|
| 2503.14738v3 (DESI DR2 Results II, 9 Oct 2025) | primary target paper | eq.(17), Table IV, Table V, Sec. III.C.1, Sec. V |
| 2503.14738v1 (18 Mar 2025) | version check | Table IV, eq.(17), Sec. III.C.1 |
| 2404.03002v3 (DESI 2024 VI, DR1 cosmology) | DR1 targets, priors | eq.(4.1), eq.(5.1), Table 2, Table 3, p.36 |
| 2503.14743v2 (Lodha et al., DR2 extended dark energy) | looked for the wCDM h·r_d value | not found; see §4 |

The local data README (`dualscale-data-r3/desi_sdss_bao/README.md`, sha256 in the
preregistration) attributes the DR2 files to arXiv:2503.14738 and 2503.14739, and the
DR1 files to arXiv:2404.03000, 03001 and 03002.

## 2. Method used by DESI (what we must match)

- **Observables.** D_M/r_d, D_H/r_d and D_V/r_d at the effective redshifts. D_M = (c/H0)∫dz/E(z) in the flat case (2503.14738 eq.(4)), D_H = c/H(z) (eq.(5)). BGS gives D_V/r_d only. The six other bins give D_M/r_d and D_H/r_d (Table IV). The fits use 13 data points in total ("best-fit χ²/dof = 10.2/(13 − 2)", Sec. III.C.1, p.15).
- **Parameters.** With BAO alone, DESI samples "over Ω_m and the parameter hr_d" (Sec. V, p.19). wCDM adds a constant w.
- **Priors.** Sec. V says the priors "match those given in Table 2 of [38]". From context ([38] is where DESI "reported a ~3σ difference ... DR1 ... LRG2"), [38] is the DR1 cosmology paper 2404.03002. That identification is inferred; the bibliography entry itself was not read. 2404.03002 Table 2 gives flat priors Ω_m ∈ U[0.01, 0.99], r_d h ∈ U[10, 1000] Mpc and w ∈ U[−3, 1].
- **Estimator.** DESI runs Cobaya Metropolis–Hastings with CAMB theory, requiring R−1 < 0.01 or ESS ≳ 10³. "For 1D marginalized posterior results we quote the mean and standard deviation when the distributions are symmetric" (Sec. V, p.19). Table V caption: "marginalized posterior means and 68% credible intervals". Best fits come from iminuit started at the MAP.
- **Consequence for us.** The targets are posterior means, not χ² minima. The parent DR1 run (`results/bao_flcdm`) compared a χ² minimum with DESI's posterior mean. That was acceptable at DR1 precision, but it is the wrong estimator. This run uses emcee posterior means under exactly the priors above as the primary estimator. The χ² minimum is compared only with the published best-fit χ² of 10.2.

## 3. Data

- DR2 likelihood: `desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_{mean,cov}.txt`, 13 points, z = 0.295 (DV), 0.510, 0.706, 0.934, 1.321, 1.484 and 2.33 (DM and DH each). Lyα is listed DH first, then DM. The parser keys on the `kind` column, so order does not matter.
- DR1 likelihood: `desi_2024_gaussian_bao_ALL_GCcomb_{mean,cov}.txt`, 12 points (QSO is DV only in DR1).
- **Checks done before preregistration. These read the files only; no fitting.**
  - The DR2 file means match 2503.14738v3 Table IV to its rounding. Examples: LRG1 D_M/r_d is 13.58758 in the file and 13.588 in the table; BGS D_V/r_d is 7.94168 and 7.942. They match v3 better than v1 (v1 has BGS 7.944 and LRG2 D_M 17.347).
  - √diag(C) matches the Table IV σ to within about 1.5%.
  - The covariance is positive definite (minimum eigenvalue 5.8e−3).
  - **Caveat.** The file's DM–DH correlation coefficients differ from Table IV for some bins. File vs v3: LRG3+ELG1 −0.347 vs −0.416; ELG2 −0.398 vs −0.434; LRG1 −0.452 vs −0.459; Lyα −0.431 vs −0.431. They also differ from v1 (LRG3+ELG1 −0.425 there). Table IV quotes marginal posterior moments, while the file is a Gaussian likelihood product, so a difference is possible. The file is recorded as used. If the fit misses the targets, this caveat is the first thing to investigate.

## 4. Targets (exact, with sources)

| Quantity | Published | Source |
|---|---|---|
| DR2 ΛCDM Ω_m | 0.2975 ± 0.0086 | 2503.14738v3 eq.(17), p.19; Table V "DESI" ΛCDM row; identical in v1 eq.(17) |
| DR2 ΛCDM h·r_d | 101.54 ± 0.73 Mpc | 2503.14738v3 eq.(17); identical in v1 |
| DR2 ΛCDM corr(Ω_m, h r_d) | r = −0.92 | 2503.14738v3 text after eq.(17) |
| DR2 ΛCDM best-fit χ²/dof | 10.2 / 11 | 2503.14738v3 Sec. III.C.1, p.15; identical in v1 |
| DR2 wCDM Ω_m | 0.2969 ± 0.0089 | 2503.14738v3 Table V, wCDM "DESI" row |
| DR2 wCDM w | −0.916 ± 0.078 | 2503.14738v3 Table V, wCDM "DESI" row |
| DR2 wCDM h·r_d | **not found**. Report only, no target | Table V omits it; 2503.14743v2 (the pages returned) gives no BAO-only wCDM value |
| DR1 ΛCDM Ω_m, r_d h | 0.295 ± 0.015, 101.8 ± 1.3 Mpc | 2404.03002v3 eq.(4.1), p.21 |
| DR1 wCDM Ω_m, w | 0.293 ± 0.015, −0.99 (+0.15 / −0.13) | 2404.03002v3 eq.(5.1), Table 3 |
| DR1 wCDM r_d h | 101.7 (+2.9 / −3.5) Mpc | 2404.03002v3 Sec. 6, p.36 |

The Table V wCDM row was read from v3 only; it was not re-checked in v1.

**DR1→DR2 shift in Ω_m.** DESI does not quote a single number for the shift. It says DR2 is "fully consistent with DR1" (Fig. 8 caption) and reports a KS test on the distance differences: p = 0.40 in v3, p = 0.22 in v1. The version change here is a revised correlation model between DR1 and DR2, C = √(N_DR1/N_DR2), with 0.61 for Lyα. The derived shift from the two published values is ΔΩ_m = 0.2975 − 0.295 = +0.0025. DR1 is a subset of DR2, so the two results are correlated. Under ideal nesting, σ_nested = √(0.015² − 0.0086²) = 0.0123, which puts the shift at 0.20σ. Treating the releases as independent gives σ = 0.0173; that is a bound only.

## 5. Known systematics and modelling differences

1. **Physics in E(z).** DESI's theory comes from CAMB: radiation is included, and one 0.06 eV massive neutrino is counted inside Ω_m (2404.03002 Table 2 note). Our primary model is matter plus dark energy only. At z = 2.33, radiation changes E² by roughly 10⁻³. That is an order-of-magnitude estimate, not a computed value. The preregistered sensitivity variant takes Ω_γ and Ω_ν from astropy (Planck18 T_cmb, N_eff = 3.044, h fixed at 0.68) and will measure the effect rather than assume it.
2. **Covariance in the file vs Table IV correlations** (§3). DESI's Cobaya likelihood uses the Gaussian file, so matching the file is the right choice. The Table IV differences are still recorded.
3. **Lyα theory systematic.** A 0.3% systematic in α_∥ and α_⊥ is already added to the covariance (2503.14738v3 p.15). We do not add it again.
4. **DR2 vs SDSS LRG2 D_M/r_d.** The tension is 1.5–2.6σ depending on the assumed correlation (Sec. III.C.2). It is not relevant to a DESI-only fit, but it is noted.
5. **The parent code does `from datetime import UTC` at module top level.** That name does not exist in the venv-pta Python 3.10 interpreter, so the import fails. Workaround: a shim, `import datetime; datetime.UTC = datetime.timezone.utc`, placed before inserting `scripts/bao_flcdm` on `sys.path` and importing. Then reassign the module globals `MEAN_FILE` and `COV_FILE`, and never call the parent `main()`, which writes into `results/bao_flcdm`. Import and parse of the DR2 files were verified this way (13 points, 13×13 covariance). No fit was run.

## 6. What counts as failure (summary; binding version in the preregistration JSON)

- Any target mean more than **0.5σ** (published σ) from the published value.
- A σ ratio outside [0.8, 1.2].
- |r − (−0.92)| > 0.05.
- |χ²_min − 10.2| > 0.5.
- Any positive control failing:
  - regression reproduction of `results/bao_flcdm`;
  - noiseless ΛCDM and wCDM mock recovery;
  - 500 noisy mocks with Fisher-σ pull mean and std inside the preregistered bands;
  - astropy vs manual-integration agreement.
- Any negative control *not* failing:
  - z-label permutation in which every point's redshift changes;
  - DM↔DH label swap;
  - Einstein–de Sitter model;
  - ΛCDM fit to a w = −0.7 mock;
  - P C Pᵀ covariance scrambles.
- MCMC not converged by the preregistered τ rule.
- A data-file sha256 that differs from the preregistered value.

**Why 0.5σ.** The data vector, covariance, priors and estimator are all the same as DESI's. What remains is the E(z) physics (item 5.1) and Monte Carlo noise (about 0.01σ). The DR1 parent run landed at 0.07σ and 0.11σ. DR2 errors are about 40% smaller, so fixed modelling offsets roughly double in σ units. 0.5σ allows for that and still catches a wrong file, prior or model.

## 7. Lean plan (for the later stage)

`formal/ANSE/DESI_DR2_wCDM.lean`, with imports pinned as in `formal/ANSE/BAO_FlatLCDM.lean`. It will prove three things:
- for 0 < Ω_m < 1, z > −1 and any real w, E(z)² = Ω_m(1+z)³ + (1−Ω_m)(1+z)^{3(1+w)} > 0;
- at w = −1 this reduces to the ΛCDM E²;
- the integrand 1/E is positive, so the comoving distance is strictly monotone in z.

The gate is `anse/formal/lean_runner.py`, with `#print axioms` lines inside the file (LL.md §11b) and a statement review for vacuity (LL.md §2, §7).
