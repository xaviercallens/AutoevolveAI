# Flat-ΛCDM BAO Consistency Fit — Literature Review (assembled 2026-09-27)

Sources: alphaXiv search 2026-09-27 (IDs cited inline), the actual data release
README, and the primary DESI DR1 paper (fetched and grepped directly for the
quoted numbers — not recalled from memory). This is the RAG source for the
`literature` Chroma collection and the ground truth this run's independent
fit is checked against.

## The measurement

Baryon Acoustic Oscillations (BAO) are a ~150 Mpc comoving-scale imprint left
by pre-recombination photon-baryon acoustic waves, visible today as a
preferred separation in the galaxy/quasar clustering correlation function.
Because the *sound horizon at the drag epoch*, r_d, is fixed by early-universe
physics (photon-baryon fluid dynamics, calibrated independently e.g. by the
CMB), BAO measurements of the transverse comoving distance D_M(z)/r_d and the
Hubble distance D_H(z)/r_d ≡ c/(H(z) r_d) at a set of redshifts z act as a
"standard ruler" constraining the expansion history H(z) and hence the matter
density Ω_m in flat ΛCDM, where H(z) = H_0 √(Ω_m(1+z)³ + 1−Ω_m).

## Primary data source (used in this run)

**DESI DR1 (2024 VI)** [arXiv:2404.03002] — the source of
`desi_2024_gaussian_bao_ALL_GCcomb_{mean,cov}.txt` in this run's data
directory. Combined BAO measurements, 7 redshift bins (BGS, LRG×2, LRG+ELG,
ELG, QSO, Lyα), galaxy/quasar tracers from >6 million objects, 0.1<z<4.2, a
**blind analysis** (BAO scales measured before unblinding, to avoid
confirmation bias). Quoted directly from the fetched paper (not recalled):

> "DESI BAO data alone are consistent with the standard flat ΛCDM
> cosmological model with a matter density Ω_m = 0.295 ± 0.015 ... In the
> standard flat ΛCDM cosmology, we determine the matter density parameter
> Ω_m = 0.295 ± 0.015, and the product of the drag-epoch sound horizon and
> the scaled Hubble constant of r_d h = (101.8 ± 1.3) Mpc."

**This is the run's external validation target**: an independent re-fit of
the same public mean/covariance table should recover Ω_m near 0.295 and
r_d·h near 101.8 Mpc, without having used those numbers as inputs to the fit.

## Newer data (context, not used as the primary fit here)

- **DESI DR2 (2025)** [arXiv:2503.14738]: >14 million tracers, three years of
  data, supersedes DR1. Not used as the primary fit in this run (DR1's
  published Ω_m/r_d h are the numbers this run's methodology is checked
  against), but the DR2 mean/cov files are present in the same data
  directory for a follow-up run.
- **DESI DR1 Bispectrum + DR2 BAO joint fit** [ID=2606.23936, 2026-06]: joint
  full-shape + BAO combination — a natural "next rung" beyond this run's
  BAO-only scope.
- **Unified tracer analysis of DESI DR2** [ID=2608.27830, 2026-08]: improved
  cross-tracer weighting — methodology note relevant if this pipeline is
  extended to DR2.
- **2D BAO compilation vs DESI DR2** [ID=2510.16141, 2025-10]: independent
  compilation for cross-checking DESI against non-DESI BAO measurements.

## Prior data included in the same local dataset (not fit in this run)

SDSS DR7 MGS, SDSS DR12 consensus, eBOSS DR16 (LRG, ELG, QSO, Lyα), as
originally distributed with CosmoMC — present in
`dualscale-data-r3/desi_sdss_bao/` alongside the DESI files, per that
directory's own README. A natural extension (not attempted here, to keep this
run's scope to a single, cleanly-sourced dataset) is a joint DESI+eBOSS+SDSS
fit using the block-covariance combination technique from the DESI paper
itself.

## Theoretical background (for the Lean 4 formalization)

- Flat FLRW dimensionless expansion rate: E(z) = H(z)/H_0 =
  √(Ω_m(1+z)³ + Ω_Λ), Ω_Λ = 1 − Ω_m (flatness). Standard textbook result
  (e.g. Weinberg, *Cosmology*, 2008; Hogg, "Distance measures in cosmology,"
  arXiv:astro-ph/9905116, for the exact distance-measure algebra used below).
- Comoving distance: D_C(z) = c ∫₀^z dz'/H(z'). Luminosity distance
  D_L(z) = (1+z) D_C(z) (flat case). Angular-diameter distance
  D_A(z) = D_C(z)/(1+z). These two combine into the **distance-duality
  relation** D_L = (1+z)² D_A — a purely algebraic consequence of the two
  definitions in flat space, independent of the cosmological model (holds for
  any D_C > 0), which is what this run formalizes and kernel-verifies in
  Lean 4, alongside positivity and monotonicity of E(z).

## What this run does and does not claim

- **Does**: an independent scipy-based χ² minimization against the real
  published DESI DR1 mean vector and covariance matrix, cross-checked by an
  independent grid search, compared against the paper's own quoted numbers.
  A Lean 4 kernel-verified formalization of the model's algebraic skeleton
  (E(z) positivity/monotonicity, distance-duality). A from-scratch adversarial
  review of both (Elenchus-based for the Lean side).
- **Does not**: claim a new cosmological result. Reproducing a published
  fit from public data is a verification exercise (this run's entire point,
  per the task's own framing: a near-certain, checkable exercise, not a
  research gamble). Any deviation from Ω_m ≈ 0.295 in this run's own fit is
  reported as a discrepancy to investigate, not suppressed.
