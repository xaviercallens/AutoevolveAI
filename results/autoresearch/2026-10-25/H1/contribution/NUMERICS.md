# H1 contribution, stage 2 (NUMERICS): bilayer dipolar excitons, rusty-SUNDIALS CVODE + exact Ewald energies

Tier of everything in this file: **X**, floating-point exploration. None of it supports a claim on its own. It
illustrates, and checks for consistency, the Tier A statement `triangular_dipolar_optimal_any_density`
(formal_cert/Autoresearch/DipolarExcitonMultipolar.lean). That statement is producer-checked only, and it is
conditional on the upstream openai/math `universal_energy_minimum` (AI-generated, not peer reviewed) and on definition
fidelity. The Hugging Face interlayer spacings are Tier L (a DFT data citation, not experiment). Using them as the
exciton dipole length is a Tier C assumption (see the caveats).

## Code and commits (rusty-SUNDIALS worktree `/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h1`)

Branch `physics/ar-dipolar-exciton-2026-10-25`, created from origin/main `47ef504`. Not pushed. Every SHA below was
read with `git rev-parse`.

| commit | content |
|---|---|
| `4feb027eb502ff0936a28f8168499b6fef25e276` | preregistration `crates/qf-yukawa-crystal/results/dipolar/preregistration.json`, committed before the solver code |
| `17ea6beccd044a02f46a8d8f7f04c76f31ee33f0` | `src/dipolar.rs`, `src/dipolar_ewald.rs`, `src/bin/dipolar_crystal.rs`, the scripts |
| `916fc88c8cebab15426427a5601a38278a1467c2` | driver prints every finished job as a `RESULT` line; the incommensurate-run count becomes an argument |
| `272a09e62c1b9b36eabc167cdafaa2845fbe9198` | results, figures, summary, run table (HEAD of the branch) |

Not covered by these commits: the main d=0.066 run and the controls ran on the binary built from the `17ea6be` sources
(before `cargo fmt`, which changes formatting only). The d=0.0209 and d=1 runs ran on `916fc88`.

### What was added to `crates/qf-yukawa-crystal`
- **`dipolar.rs`** holds the pair potential.
  - `V(r) = g_d(r^2) = 2(1/r - 1/sqrt(r^2+d^2))` is the Lean `g d`, including the factor 2.
  - It is used in the rescaled form `U = V/d^2 = 2/(r s (r+s))`, where `s = sqrt(r^2+d^2)`. This form has no
    cancellation at small d, and `U -> 1/r^3` as `d -> 0`.
  - Lengths are in units of `n^-1/2` (density 1), so `d` means `d_tilde = d sqrt(n)`.
  - The dynamics potential is `U` with a shifted-force cutoff at `r_c = 8` (minimum image), plus an analytic force and
    Hessian (FD-tested). It is not completely monotone; its only job is to generate competitor configurations.
  - There is also a direct "full" sum: images within R, plus the exact uniform tail
    `(n/2) int_R^inf 2 pi r U dr = 2 pi n / (sqrt(R^2+d^2) + R)` per particle.
- **`dipolar_ewald.rs`** gives the exact energy of a periodic configuration under the untruncated potential.
  - It splits the integral representation `V = (4/sqrt(pi)) int_0^inf exp(-r^2 t^2)(1 - exp(-d^2 t^2)) dt` at
    `t = eta`.
  - Real-space part: `2(erfc(eta r)/r - erfc(eta s)/s)`.
  - Reciprocal part: `(1/A) sum_G K(G)|S(G)|^2`, including `G = 0`. The potential is integrable, so no background is
    needed.
  - Self term: `V_l(0)`.
  - The kernels use 8 x 40-point Gauss-Legendre quadrature with `-expm1(-d^2 t^2)`.
  - The same code handles any cell: the primitive triangular, square and honeycomb cells, and the 288/289-particle
    boxes.
- **`bin/dipolar_crystal.rs`** provides the commands `refs | gaps | controls | main <d> <n_quench> <n_anneal> [<n_incomm>]`.
- **Yukawa code is untouched.** `yukawa_crystal refs` was re-run after the change, and
  `git diff -- crates/qf-yukawa-crystal/results/references.jsonl` is empty, so the published references are
  byte-identical.
- **Unit tests:** `cargo test -p qf-yukawa-crystal` gives 28 passed, 1 ignored (pre-existing), 0 failed (after fmt,
  on HEAD). The 9 new dipolar tests are:
  - the U formula against the naive formula, and analytic derivatives against FD
  - force and Hessian against FD
  - box image sum against the lattice sum
  - R-convergence, and the tail is not negligible
  - square and honeycomb above triangular
  - Gauss-Legendre exactness
  - **eta-independence** to 1e-11
  - Ewald against the direct sum within its residual, and the box against the primitive cell to 1e-11
  - the pure dipolar limit

## Why the energies are Ewald-summed (the erratum is not repeated)

- In the Yukawa paper the truncation size was reported as `V(r_c)`, which is not the change in energy per particle.
  Here that number is never used.
- A spherically truncated `d^2/r^3` tail, even with the exact uniform tail added back, leaves a lattice-minus-continuum
  residual. It decays only algebraically and oscillates in R.
- That residual was measured: `references.jsonl` holds the `convergence` array, and the figure is
  `fig_truncation_residual`.
  - At d = 0.066, `|e_tri(R) - e_tri^Ewald|` is 1.7e-3 at R = 8, 7.9e-5 at R = 16, 6.6e-7 at R = 32, 4.0e-5 at R = 64,
    7.6e-7 at R = 128, and 2.5e-7 at R = 256 (units of d^2). This is not monotone.
  - Without the tail, the error is the tail itself: about 2 pi n/(2R), which is 0.098 at R = 32.
- Every reported energy (`e_exact`) is therefore the Ewald value. The truncated `e_sf` is reported separately, and only
  as the dynamics potential.
- The tail is configuration-independent at fixed density, so it cancels in gaps. The oscillating residual does not.

## Positive control: Rust Ewald against an independent Python evaluation

`scripts/dipolar_independent_check.py` is written from scratch: numpy direct sums, plus an Ewald sum with adaptive
`scipy.integrate.quad` at a different split (eta = 1.0, against 0.8 in Rust). Output is in `independent_check.json`.

| d_tilde | Rust e_tri (U units) | Python Ewald, rel. diff | Python direct R=400 + tail, abs diff | square: Python Ewald rel. diff |
|---|---|---|---|---|
| 0.0209 | 4.445599702965617 | -8.5e-14 | 1.7e-8 | -1.9e-13 |
| 0.066 | 4.438685393575219 | -2.1e-14 | 1.7e-8 | -1.9e-14 |
| 0.114 | 4.423567867903930 | -4.6e-15 | 1.7e-8 | -1.2e-15 |
| 0.3 | 4.295977545078494 | -1.4e-15 | 1.7e-8 | -2.0e-16 |
| 1.0 | 3.355596439147457 | -1.1e-15 | 1.7e-8 | -1.4e-15 |

- Over the R = 100, 200 and 400 direct sums, the largest deviation from the Ewald value is 1.85e-5 (triangular) and
  9.5e-6 (square). This is the oscillating residual described above.
- **Negative control:** dropping the tail at R = 100 gives an error of 3.14e-2 at every d. The check detects a missing
  tail.
- **eta-independence (Rust):**
  - At the five d values, e_tri at eta = 0.6, 0.8 and 1.2 agree to at most 1.3e-13 relative (`references.jsonl`; recomputed 1.3186e-13 at stage 5. Erratum: this line said
    1.5e-13 before the stage-4 audit).
  - Over the 41-point grid d in [0.01, 3], eta = 0.8 and eta = 1.2 agree to at most 4.8e-13 relative.
- The 288-particle box against the primitive cell agrees to at most 2.6e-14 relative (`e_tri_exact_box288`).
- Pure-dipolar limit: as d -> 0, e_tri approaches 4.4462 (d = 0.01), which should equal half the triangular Riesz
  s=3 lattice sum at density 1. That value was **not** compared to a literature value here.

## Hugging Face data: the physical interlayer separation

- **Search** (`scripts/dipolar_hf_search.py`, `HfApi().list_datasets(search=...)`) used 26 queries: C2DB, BiDB,
  bilayer, heterobilayer, JARVIS, 2D materials, van der Waals, TMD, MoS2, WSe2, MoSe2, interlayer, and others. The raw
  hits are in `hf_search.json`.
  - **No Hub dataset of TMD heterobilayers or of interlayer separations was found.**
  - The search for `bilayer` returned nothing materials-related.
  - The "C2DB" hits are unrelated (for example `HZPM/C2DBench` is a gated single-cell biology set), apart from
    `colabfit/JARVIS_C2DB`, which holds monolayers.
- **Closest real data:** the ColabFit mirror of JARVIS-DFT (VASP, DFT-OptB88vdW, a van der Waals functional), which
  contains multilayer TMD slabs.
  - `colabfit/JARVIS_DFT_3D_12_12_2022`, revision `f4de0085edcf92885870c67459363d2c7080c90b`, file `co/co_0.parquet`
    (54,027,813 bytes, sha256 `9f6c21a2a3eda4316eee1f2be7dddc276eeb5f905de87dcce70f20e36132510b`), plus `README.md`
    and `ds.parquet`. Card license: **"unknown"** (recorded verbatim). Cite: Choudhary et al., ColabFit 2023,
    doi:10.60732/e9e65ccd; publication doi:10.1038/s41524-020-00440-1.
  - `colabfit/JARVIS_DFT_2D_3_12_2021`, revision `a1b0a91056e1030388e8f619fc45bb69768888a4`, file `co/co_0.parquet`
    (4,995,064 bytes, sha256 `60149baa3d5a1b24de9148ac304f90a125a7398a0e8a601a818bc8157aac188d`). Card license:
    **"unknown"**. This set is used only for the monolayer a and t_XX, never for d.
  - Downloads are in `/home/callensxavier_gmail_com/hf-data/dipolar_exciton/` (`provenance.json` has sha256 values)
    and were read with `python -I`.
- **Extraction and selection** use `dipolar_tmd_extract.py` and `dipolar_physical_d.py`. The selection rule was fixed
  in the docstring before the output was seen:
  - semiconducting rows only
  - at least 2 MX2 layers, with metal-plane spacings between 4.5 and 8 Å
  - vacuum gaps excluded
  - deduplicated by name

  The resulting adjacent metal-plane spacings are:

| material | JARVIS rows (jid) | spacing (Å) |
|---|---|---|
| MoSe2 | `jdft_3d-12-12-2022_27269` (CO_3818104148691522390860544, 4-layer slab + vacuum), `jdft_3d-12-12-2022_15445` (CO_3423589954252039515764859, bilayer + vacuum), `jdft_3d-12-12-2022_24840` (CO_2346514921117518660845305, 3-layer slab + vacuum) | mean 6.5827, range 6.5818–6.5842 |
| WSe2 | `jdft_3d-12-12-2022_35821` (CO_1114500911969241970045731, 4-layer slab + vacuum) | mean 6.6151, range 6.6131–6.6162 |
| MoS2 | `jdft_3d-12-12-2022_33239` (CO_1670468883093595270935984; four 6.24 Å spacings and no vacuum gap, so a bulk-like cell, not a slab) | mean 6.2371 |

The identifiers are ColabFit `names` and configuration ids, exactly as printed by `dipolar_hf_method.py`. They are
not JVASP ids, and their numeric suffixes differ between JARVIS releases.

Tiers:
- the JARVIS spacings are Tier L, a data citation of doi:10.1038/s41524-020-00440-1 through ColabFit
  doi:10.60732/e9e65ccd
- the step from "homo-stack mean metal-plane spacing" to "heterobilayer dipole length" is a Tier C assumption
| WS2 | none passed the selection (only metallic or non-layered polytypes in this shard) | — |

- **Proxy for MoSe2/WSe2:** d = mean(6.5827, 6.6151) = **6.599 Å = 0.660 nm**.
- **Exciton densities.** arXiv:2001.03812 (J. Wang et al., "Diffusivity reveals three distinct phases of interlayer
  excitons in MoSe2/WSe2 heterobilayers", read via alphaXiv) reports:
  - a free interlayer-exciton gas "only exists in the narrow density range around 10^11 ~ 10^12 cm^-2"
  - a Mott density n_Mott ~ 1.6–3 x 10^12 cm^-2
- **Hence d_tilde = d sqrt(n):** 0.0209 (n = 1e11), 0.0660 (1e12), 0.1143 (3e12), where lengths are in units of
  n^-1/2. The triangular spacing is a = 1.0746 n^-1/2. The study used 0.0209, 0.066 and 0.114.
- **Caveats:**
  1. The proxy comes from homo-stacks, not a heterobilayer row. No heterobilayer row exists in the Hub data.
  2. The metal-plane spacing is used as the electron-hole separation. Real carrier centroids differ.
  3. The model is classical, rigid, point-like and unscreened. There is no hBN/Keldysh screening, no moiré potential
     and no quantum kinetic energy. In the physical density window the excitons are a quantum gas, not a classical
     T = 0 crystal.
  4. The license on both cards is "unknown", so redistributing the parquet files needs care. Only derived numbers are
     redistributed here.

## Lattice energy gaps against d (exact, `lattice_gaps.jsonl`, figure `fig_lattice_gaps`)

Exact per-particle energies and absolute gaps (U = V/d^2 units):

| d_tilde | e_tri | e_sq − e_tri | e_hc − e_tri |
|---|---|---|---|
| 0.0209 | 4.445599702966 | 7.0378e-2 | 4.2354e-1 |
| 0.066 | 4.438685393575 | 6.9837e-2 | 4.2033e-1 |
| 0.114 | 4.423567867904 | 6.8667e-2 | 4.1339e-1 |
| 0.3 | 4.295977545078 | 5.9459e-2 | 3.5897e-1 |
| 1.0 | 3.355596439147 | 1.9453e-2 | 1.2225e-1 |

- On the 41-point grid, e_sq/e_tri − 1 decreases from 1.584e-2 (d = 0.01) to 1.36e-3 (d = 3). Over the same range,
  honeycomb decreases from 9.53e-2 to 8.75e-3.
- In the physical window the gaps are essentially at the pure-dipolar value.
- **Physical scale** of the square-triangular gap per exciton, unscreened (eps_r = 1; divide by eps_r otherwise), with
  `E = (e^2/4 pi eps0) sqrt(n) d_tilde^2 U`:
  - 0.0014 meV at n = 1e11
  - 0.044 meV at n = 1e12
  - 0.22 meV at n = 3e12 cm^-2

  This is far below the moiré trap depths of tens to 100 meV quoted in arXiv:2001.03812, so the classical lattice
  ordering would not be the dominant energy in a real device.

## CVODE relaxation study (preregistration DIP-TRI-1)

**Setup.**
- N = 288 in the periodic box 16a x 9√3a, at density 1. This box holds the 16 x 18 triangular lattice exactly.
- Dynamics: overdamped gradient flow of the shifted-force potential (r_c = 8), integrated with rusty-SUNDIALS CVODE
  (BDF, analytic Jacobian = −Hessian, rtol 1e-10, atol 1e-12) until max|F| < 1e-9.
- Annealing: Euler–Maruyama, T from 0.05 to 1e-5 (U units) over 300000 steps, dt = 0.002, step cap 0.05a, followed by
  a CVODE quench.
- For each relaxed state the record holds:
  - e_exact (Ewald) and the gap to the exact triangular lattice energy
  - e_sf (truncated)
  - defects (coordination ≠ 6 within 1.35·d0) and psi6
  - the Hessian spectrum of the truncated potential by cyclic Jacobi, for the N = 288 runs
- Full table: `crates/qf-yukawa-crystal/results/dipolar/run_table.md`. Per-run JSON: `main_d*.jsonl`, `controls.jsonl`.

**Controls (`controls.jsonl`, all five d, 8:12.70 wall).**
- **Positive, perfect lattice:** stays put. |rel gap| ≤ 2.6e-14, 0 defects, 2 zero modes and then the first positive
  eigenvalue: 0.2232 (d=0.0209), 0.2214 (0.066), 0.2177 (0.114), 0.1883 (0.3), 0.0614 (1.0).
- **Positive, triangular + 0.1a Gaussian noise:** relaxes back to the lattice at every d. |rel gap| ≤ 2.2e-14,
  0 defects, 0 negative modes.
- **Negative, square lattice (17 x 17 box, N = 289):**
  - It is a saddle of the truncated potential, with 72 negative Hessian eigenvalues at d ≤ 0.3 and 64 at d = 1.
  - Its exact energy is above e_tri by 7.04e-2, 6.98e-2, 6.87e-2, 5.95e-2 and 1.95e-2 for the five d.
  - Square + 1e-3 noise relaxes to a lower state that is still above the triangular lattice: rel gap 4.77e-3,
    4.74e-3, 4.68e-3, 4.16e-3, 1.73e-3, with 0 defects and psi6 = 0.9548. This is a distorted lattice; the box cannot
    hold the triangular one.
- **Negative, incommensurate square box (N = 289, d = 0.066, 2 runs):** both stay defected (8 and 4 defects) and above
  e_tri (rel gap 2.00e-3 and 7.90e-4). The pipeline does report "not triangular".

**Main runs.**

| d_tilde | runs | wall (process) | outcome |
|---|---|---|---|
| 0.0209 | 2 T=0 quenches | 11:07.98 (1 thread) | 1 ends defected (rel gap 1.39e-3, 4 defects); 1 reaches the perfect lattice (rel gap 2.8e-14) |
| 0.066 | 8 T=0 quenches + 2 annealed + 2 incommensurate | 57:48.33 (2 threads) | quenches: 1 reaches the lattice (−2.0e-16); 7 end above, rel gap from 1.54e-4 to 3.50e-3. Of those 7, 5 are defected (4–24 defects); 2 have 0 defects but higher energy (1.54e-4, 7.94e-4), consistent with strained or rotated crystallites. Annealed: 1 reaches the lattice (−5.2e-15), 1 ends at rel gap 1.54e-4 (the same energy as quench 04) |
| 1.0 | 2 T=0 quenches | 14:24.29 (1 thread) | 1 defected (rel gap 7.35e-4, 8 defects); 1 reaches the lattice (−2.3e-14) |
| 0.114, 0.3 | controls only | — | — |

- Per-job wall times: quenches 275–880 s, anneal phases 1012 s and 1014 s, square-noise relaxations 92–113 s. Every
  single relaxation or anneal stayed under 30 min.
- Every relaxed state with a Hessian check (all N = 288 runs) has 0 negative eigenvalues, so they are local minima of
  the dynamics potential. All runs converged to max|F| < 1e-9.

**Prediction outcomes.**
- **P1 (full, exact potential): PASS at the three d with runs, and at all five d through the control relaxations.**
  - Over 21 relaxed competitors (main runs, incommensurate boxes, square + noise) plus 10 positive-control
    relaxations, there are 0 states with rel gap < −1e-9.
  - The most negative relative gap is −2.3e-14, which is rounding at the perfect lattice.
  - The smallest gap among states that did not reach the lattice is 1.54e-4.
- **P1b (truncated dynamics potential): PASS**, with 0 undercuts. Over all competitors, |gap_exact − gap_sf| ≤ 1.6e-5.
  The truncation shifts absolute energies by about 0.78 (U units), but gaps by at most 1.6e-5, below every observed
  nonzero gap.
- Gaps from plain R = 32 or R = 64 sums with the tail differ from the Ewald gaps by up to about 1.5e-4 for individual
  states (`gap_full_R32` vs `gap_exact` for uniform_07 at d = 0.066: 3.37e-3 vs 3.52e-3). The configuration-dependent
  residual is real, which is why only Ewald gaps are reported as gaps.
- **P3 (T=0 quenches mostly glassy): weakly supported.** 7 of 12 random-start quenches end defected. 3 of 12 (one at
  each d) end on the perfect lattice. The other 2 have 0 defects but a positive gap. **Seeds are reused across d.**
  `uniform_config` uses seed 500+k at every d, so the three lattice-reaching quenches all start from seed 501, and
  uniform_00 is the same start at all three d. These are not independent samples across d.

**Deviations from the preregistration.** They are stated, not hidden.
1. The preregistration planned 8 quenches + 2 anneals + 2 incommensurate runs at each of the five d. Only d = 0.066
   received the full set.
   - The first attempts at d = 0.0209 and d = 1 (4 quenches + 1 anneal + 2 incommensurate, 1 thread) were killed after
     about 34 min because they could not finish within the budget.
   - The driver then kept results only in memory, so their finished jobs (incommensurate runs and anneal) are lost.
     The logs `killed_main_d*_first_attempt_stdout.txt` show only "done job" lines.
   - Those two d were rerun with 2 quenches each, using the patched driver that prints each result.
2. d = 0.114 and d = 0.3 have controls and exact lattice sums but no random-start runs.
3. The d = 0.066 main process ran for 57:48 wall as one process with many jobs. No single relaxation exceeded 30 min.

## What this does and does not show
- **It shows (Tier X):**
  - With an exact (Ewald-summed) untruncated dipolar-exciton potential and CVODE gradient flow, no relaxed periodic
    configuration found here lies below the triangular lattice, at the physical d_tilde values 0.0209 and 0.066 and
    at d_tilde = 1.
  - The triangular lattice is reached from random starts in 3 of 12 T=0 quenches and in 1 of 2 annealed runs. The
    three quenches share one starting configuration (seed 501) across d.
  - Lattice gaps to square and honeycomb are 1.6% and 9.5% relative in the physical window.

  This is consistent with `triangular_dipolar_optimal_any_density`, but it is not evidence for it in any proof sense.
- **It does not show:**
  - a global optimum: only 21 competitors were sampled, from a single box shape and N
  - anything about the open 2D Cohn–Kumar conjecture or the upstream proof
  - anything about real excitons: they are quantum, screened, sit in a moiré potential, and turn into an e-h plasma
    above n_Mott
  - that the JARVIS homo-stack spacing equals the heterobilayer dipole length

## Reproduce
```
CARGO_TARGET_DIR=/home/callensxavier_gmail_com/rusty-target-ar cargo build --release -j 2 --offline --manifest-path /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h1/Cargo.toml -p qf-yukawa-crystal
CARGO_TARGET_DIR=/home/callensxavier_gmail_com/rusty-target-ar cargo test --release -j 2 --offline --manifest-path /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h1/Cargo.toml -p qf-yukawa-crystal -- --test-threads=2   # 28 passed, 1 ignored
taskset -c 4-7 /home/callensxavier_gmail_com/rusty-target-ar/release/dipolar_crystal refs  <crate_dir>
taskset -c 4-7 /home/callensxavier_gmail_com/rusty-target-ar/release/dipolar_crystal gaps  <crate_dir>
taskset -c 4-7 /home/callensxavier_gmail_com/rusty-target-ar/release/dipolar_crystal controls <crate_dir>
taskset -c 4-7 /home/callensxavier_gmail_com/rusty-target-ar/release/dipolar_crystal main <crate_dir> 0.066 8 2
DIPOLAR_THREADS=1 taskset -c 4-7 .../dipolar_crystal main <crate_dir> 0.0209 2 0 0
DIPOLAR_THREADS=1 taskset -c 4-7 .../dipolar_crystal main <crate_dir> 1 2 0 0
python -I scripts/dipolar_hf_search.py results/dipolar/hf_search.json
python -I scripts/dipolar_hf_download.py /home/callensxavier_gmail_com/hf-data/dipolar_exciton colabfit/JARVIS_DFT_3D_12_12_2022@f4de0085edcf92885870c67459363d2c7080c90b:README.md,ds.parquet,co/co_0.parquet colabfit/JARVIS_DFT_2D_3_12_2021@a1b0a91056e1030388e8f619fc45bb69768888a4:README.md,ds.parquet,co/co_0.parquet
python -I scripts/dipolar_tmd_extract.py results/dipolar/jarvis_tmd_structures.json <3D co_0.parquet> <2D co_0.parquet>
python -I scripts/dipolar_physical_d.py results/dipolar/jarvis_tmd_structures.json results/dipolar/physical_d.json
python -I scripts/dipolar_independent_check.py results/dipolar/references.jsonl results/dipolar/independent_check.json
python -I scripts/dipolar_figures.py results/dipolar results/dipolar/figures
python -I scripts/dipolar_table.py results/dipolar/figures/summary.json
```
Here `<crate_dir>` = `/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h1/crates/qf-yukawa-crystal`, and python =
`/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python`.
- Clippy on the crate is clean.
- `cargo fmt -p qf-yukawa-crystal` was applied.

## Files copied to the paper
`papers/ar_dipolar_exciton/data/` contains:
- `fig_lattice_gaps`, `fig_relaxed_gaps`, `fig_truncation_residual` (PDF and PNG)
- `summary.json`, `references.jsonl`, `lattice_gaps.jsonl`, `controls.jsonl`, `main_d{0.0209,0.066,1}.jsonl`
- `independent_check.json`, `physical_d.json`, `preregistration.json`, `run_table.md`, `hf_provenance.json`
