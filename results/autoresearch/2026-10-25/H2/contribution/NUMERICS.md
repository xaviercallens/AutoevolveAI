# H2 Stage 2: numerics (exact-Yukawa fix for the published truncation erratum)

Tier: every number in this file is floating point (Tier X, exploration). None of it supports a mathematical claim on
its own. The only Tier A content of H2 is in FORMAL.md.

## 0. What is fixed

- **The erratum.** It is the textbook editor's note (doi:10.5281/zenodo.23295142, `editors_note.tex`) on the
  Yukawa CVODE paper (doi:10.5281/zenodo.23293429). The published N-body study used a shifted-force cut of
  `V(r) = e^{-kappa r}/r` at `r_c = 8`. That cut lowers the energy per particle by about 1.8e-2 at kappa = 1, which
  is more than the square-triangular gap (about 9.5e-3). The truncated potential is also not completely monotone,
  so the published P1 observation concerned an approximation of the interaction that the theorem covers.
- **The fix.** The potential is now evaluated exactly, with a controlled tail. The work is in the rusty-SUNDIALS
  worktree `/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h2`, crate `crates/qf-yukawa-crystal`, new module
  `src/exact.rs`, with new subcommands `exact-refs`, `exact-relax` and `exact-saddle` in `src/main.rs`. The
  published shifted-force code path (`System::pair`, `lattice_energy`, `refs`, `main`, `snapshot`) is unchanged.
  - `lattice_energy_exact`: the plain sum `(1/2) sum_{0<|v|<R} V(|v|)` over a Bravais lattice (sorted, Neumaier
    compensated), with a rigorous tail bound. For decreasing V, compare each lattice point with its Voronoi cell
    (circumradius delta, cell area A). The tail beyond R is then at most
    `(pi/A)(1 + delta/(R-2delta)) e^{-kappa(R-2delta)}/kappa` per particle.
  - `lattice_energy_ewald`: an independent Ewald-type splitting of the same sum. It uses the Gaussian integral
    representation `e^{-kappa r}/r = (2/sqrt pi) int_0^inf exp(-r^2 s^2 - kappa^2/(4 s^2)) ds`, split at `s = eta`,
    with closed-form real- and reciprocal-space terms in `erfc`.
  - `ExactBox`: a periodic rectangle in which every pair interacts with all of its periodic images within R (not
    only the minimum image). It includes each particle's own images (`self_image`). Energy, force and Hessian are
    analytic. `relax_exact` runs this repository's CVODE (BDF, analytic Jacobian = -Hessian) with the published
    protocol (rtol 1e-10, atol 1e-12, ftol 1e-9).
  - Cutoffs: R = 40 at kappa = 1 and R = 20 at kappa = 2. The rigorous tail is <= 5.6e-17 and <= 1.2e-16 per
    particle respectively.
- **Prior work in the crate.** `global_opt::periodic_energy_exact` / `floor_check` (exploratory, energy only) already
  existed. What is new is exact forces and Hessian, exact CVODE relaxation, the square lattice, the Ewald
  cross-check, the sharper Voronoi tail bound and the side-by-side erratum tables. The old function is used as a
  cross-check in section 2.

Rusty commits: see section 5.

## 1. Lattice energies, old vs new (`yukawa_crystal exact-refs`, `results/exact/exact_refs.jsonl`)

Commands:
1. Build at code commit cc5a8aed81b3228bd9e9eb69f2c326f926903a34:
   `CARGO_TARGET_DIR=/home/callensxavier_gmail_com/rusty-target-ar cargo build --release -j 2 --offline --manifest-path /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h2/Cargo.toml -p qf-yukawa-crystal`
2. Copy `/home/callensxavier_gmail_com/rusty-target-ar/release/yukawa_crystal` to
   `/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h2/target/h2bin/yukawa_crystal`. Do this right after the build,
   because the shared target dir is rebuilt by other lanes.
3. Run:
   `taskset -c 4-7 /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h2/target/h2bin/yukawa_crystal exact-refs /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h2/crates/qf-yukawa-crystal`

The first `exact-refs` run used the shared-dir binary immediately after building it.

Energy per particle at density one:

| kappa | lattice | published shifted force r_c=8 | exact (this work) | exact - published |
|---|---|---|---|---|
| 1 | triangular | 1.6076092171852698 | 1.6253213396062749 | 1.771212e-2 |
| 1 | square | 1.6171455730029276 | 1.6348554953171981 | 1.770992e-2 |
| 2 | triangular | 0.39353336682550988 | 0.39354284893239105 | 9.482107e-6 |
| 2 | square | 0.40096476989313634 | 0.40097424876505744 | 9.478872e-6 |

Square minus triangular gap:

| kappa | published (sf, r_c=8) | exact | change |
|---|---|---|---|
| 1 | 9.5363558177e-3 | 9.5341557109e-3 | -2.200e-6 |
| 2 | 7.4314030676e-3 | 7.4313998327e-3 | -3.235e-9 |

So the absolute energies move by the published erratum amount, while the gap moves by only 2.2e-6 at kappa = 1
(relative 2.3e-4) and 3.2e-9 at kappa = 2. The ordering triangular < square holds under the exact potential at both
kappa.

Cutoff sweep, triangular lattice, error against the converged value (`kind: sweep` rows):

| kappa | r_c | shifted force | plain cut | plain + continuum tail `pi rho e^{-kappa r_c}/kappa` |
|---|---|---|---|---|
| 1 | 6 | -8.409e-2 | -6.196e-3 | 1.591e-3 |
| 1 | 8 | -1.771e-2 | -1.081e-3 | -2.710e-5 |
| 1 | 10 | -3.444e-3 | -1.429e-4 | -2.978e-7 |

The full sweep (r_c = 6 to 40, both lattices, both kappa) is in the jsonl and in `fig_cutoff_sweep.{pdf,png}`. Points
drawn at 1e-17 in that figure are exact zeros, clipped for the log axis. Where both are cut at the same r_c, the
shifted-force error is about 16 times the plain-cut error at kappa = 1, r_c = 8.

## 2. Positive controls

- **(P-a) Independent mpmath sum, 40 digits.** Script `scripts/mpmath_lattice_control.py`, output
  `results/exact/mpmath_control.json`. It shares no code with the Rust and computes the sums two ways:
  - a direct disk sum to R = 64/kappa + 2 delta + 1 (rigorous tail < 1.9e-28);
  - an mpmath Ewald splitting at eta = 0.7.

  Command:
  `taskset -c 4-7 /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h2/crates/qf-yukawa-crystal/scripts/mpmath_lattice_control.py /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h2/crates/qf-yukawa-crystal /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h2/crates/qf-yukawa-crystal/results/exact/mpmath_control.json`
  (total runtime about 7 s)

  | kappa | lattice | mpmath direct (30 digits) | mpmath direct - Ewald | Rust f64 - mpmath |
  |---|---|---|---|---|
  | 1 | tri | 1.62532133960627506131510966435 | -5.2e-29 | 1.7e-16 |
  | 1 | square | 1.63485549531719802497454729791 | -4.4e-29 | 6.8e-17 |
  | 2 | tri | 0.393542848932391123590016151462 | -2.9e-30 | 7.0e-17 |
  | 2 | square | 0.400974248765057473004594249749 | -2.0e-30 | 3.4e-17 |

  The threshold was 1e-9. The result is `positive_control_pass: true`, with every difference at most 1.7e-16. The
  mpmath values also agree with the textbook's R = 60 scratch sums (ch3, footnote fn:unshifted) to at most 1.5e-14.
- **(P-b) Rust direct sum vs Rust Ewald splitting** at eta = 0.5, 1, 2. They agree to at most 2e-15 (unit test
  `direct_sum_matches_ewald_splitting`, threshold 1e-12; values in the jsonl).
- **(P-c) Image-summed periodic box holding the perfect lattice vs the infinite-lattice sum.**
  - Triangular 16x18 box: differences -2.2e-16 (kappa = 1) and 0 (kappa = 2).
  - Square 17x17 box: -2.2e-16 and 5.6e-17.
  - The self-image term is 5.16e-9 at kappa = 1. It is included, and the box would be off by that much without it.
  - The old `global_opt::periodic_energy_exact` (naive summation) agrees to 2.0e-12 (kappa = 1) and 1.4e-13
    (kappa = 2).
- **(P-d) Finite-difference checks** of the `ExactBox` force (against energy) and Hessian (against force) at a
  perturbed lattice, kappa = 1, R = 30. Unit test `exact_force_and_hessian_match_finite_differences` passes.
- **(P-e)** `lattice_energy_shifted_force` reproduces the published `references.jsonl` values to < 1e-12 (unit test).

## 3. Negative controls

- **(N-a)** The published shifted-force lattice energies, compared with the exact values, FAIL the 1e-9 test, as
  intended. The differences are exactly the published erratum amounts: 1.7712122e-2 (tri) and 1.7709922e-2 (square)
  at kappa = 1, and 9.4821069e-6 / 9.4788719e-6 at kappa = 2 (`negative_control_pass: true` in
  `mpmath_control.json`).
- **(N-b) Incommensurate 17x17 box** (cannot hold the triangular lattice). Under the exact potential every
  relaxation stays above the exact e_tri; see section 4.
- **(N-c) Square-lattice saddle under the exact potential** (`exact-saddle`); see section 4.

## 4. Relaxed configurations under the exact potential

**Protocol (`exact-relax`).** Each run does four things:
1. It re-runs a published seed with the published shifted-force protocol (CVODE quench, optionally the
   300k-step Langevin anneal plus quench).
2. It checks that the re-run reproduces the published energy. The comparison is against
   `results/main_kappa{1,2}.jsonl` with threshold 1e-13 (`sf_reproduces_published`), and it holds for all 24 stages.
3. It evaluates the exact image-summed energy at that minimiser.
4. It re-relaxes under the exact potential (CVODE, analytic Jacobian), then computes the Hessian spectrum (Jacobi)
   at the exact minimiser.

Annealing with the exact potential (300k force evaluations of the image-summed potential) was not attempted. The cost
was not measured, but it was expected to exceed the 30 min per-run cap: a single exact re-relaxation at kappa = 1
already takes minutes on the contended cores.

**Coverage.** 21 runs (13 at kappa = 2, 8 at kappa = 1) giving 24 stages. That is 11 of the 50 published kappa = 1
stages (quench and anneal_quench) and 13 of the 100 published kappa = 2 stages (quench only). It is a subset, not the
full published study.

Commands:
- `bash scripts/run_exact_relax.sh` runs `exact-relax 2 4 0 1`, `exact-relax 1 1 1 0`, `exact-saddle` and
  `exact-relax 1 2 0 1`.
- `exact-relax 2 1 0 0` was run separately.
- Arguments are kappa, nrun, anneal and first. The binary is a private copy at `target/h2bin/yukawa_crystal`, because
  other lanes rebuild the shared target dir.
- Wall times per job (`wall_s`) were 60.2-158.2 s at kappa = 2 and 207.7-1485.5 s at kappa = 1. The three anneal
  jobs took 1173.9-1485.5 s. All ran on 2 contended threads, so every job stayed under the 30 min cap.

Per-stage gap to the triangular lattice (`e - e_tri`). Shifted force is measured against the published sf e_tri,
exact against the exact e_tri:

| kappa | run | stage | sf gap (published) | exact gap after exact relax | change | defects sf/exact | Hessian neg. modes |
|---|---|---|---|---|---|---|---|
| 1 | oc20_00 | quench | 4.583519e-4 | 4.585606e-4 | +2.09e-7 | 0/0 | 0 |
| 1 | oc20_00 | anneal_quench | 4.794193e-4 | 4.79949e-4 | +5.30e-7 | 0/0 | 0 |
| 1 | oc20_01 | quench | 6.692996e-4 | 6.696038e-4 | +3.04e-7 | 4/4 | 0 |
| 1 | oc20_02 | quench | 8.441395e-4 | 8.443006e-4 | +1.61e-7 | 4/4 | 0 |
| 1 | uniform_00 | quench | 9.580413e-4 | 9.58281e-4 | +2.40e-7 | 4/4 | 0 |
| 1 | uniform_00 | anneal_quench | 3.108624e-14 | 0.0 | -3.1e-14 | 0/0 | 0 |
| 1 | uniform_01 | quench | 1.274349e-3 | 1.274168e-3 | -1.81e-7 | 8/8 | 0 |
| 1 | uniform_02 | quench | 6.692996e-4 | 6.696038e-4 | +3.04e-7 | 4/4 | 0 |
| 1 | incommensurate_00 (17x17) | quench | 7.535281e-4 | 7.536546e-4 | +1.27e-7 | 4/4 | 0 |
| 1 | incommensurate_00 (17x17) | anneal_quench | 4.963049e-4 | 4.965976e-4 | +2.93e-7 | 4/4 | 0 |
| 1 | incommensurate_01 (17x17) | quench | 7.917745e-4 | 7.921755e-4 | +4.01e-7 | 4/4 | 0 |
| 2 | oc20_00 | quench | 1.742040e-3 | 1.742040e-3 | 0 (at 7 digits) | 24/24 | 0 |
| 2 | oc20_01 | quench | 1.858344e-3 | 1.858344e-3 | 0 | 24/24 | 0 |
| 2 | oc20_02 | quench | 5.048796e-4 | 5.048798e-4 | +2e-10 | 4/4 | 0 |
| 2 | oc20_03 | quench | 6.575263e-4 | 6.575262e-4 | -1e-10 | 4/4 | 0 |
| 2 | oc20_04 | quench | 1.355027e-3 | 1.355027e-3 | 0 | 12/12 | 0 |
| 2 | uniform_00 | quench | 6.678927e-4 | 6.678928e-4 | +1e-10 | 4/4 | 0 |
| 2 | uniform_01 | quench | 6.027099e-4 | 6.027096e-4 | -3e-10 | 4/4 | 0 |
| 2 | uniform_02 | quench | 7.233317e-5 | 7.233329e-5 | +1.2e-10 | 0/0 | 0 |
| 2 | uniform_03 | quench | 2.376668e-3 | 2.376668e-3 | 0 | 34/34 | 0 |
| 2 | uniform_04 | quench | 7.233317e-5 | 7.233329e-5 | +1.2e-10 | 0/0 | 0 |
| 2 | incommensurate_00 (17x17) | quench | 3.777154e-4 | 3.777157e-4 | +3e-10 | 4/4 | 0 |
| 2 | incommensurate_01 (17x17) | quench | 3.788130e-4 | 3.788133e-4 | +3e-10 | 4/4 | 0 |
| 2 | incommensurate_02 (17x17) | quench | 9.130359e-4 | 9.130359e-4 | 0 | 8/8 | 0 |

Notes on the table:
- The change column is computed from the printed 7-digit gaps (`gap_change` in `exact_summary.json`). At kappa = 2
  it sits at the print resolution, about 1e-10.
- Every exact re-relaxation converged (max force < 1e-9).
- Rows with identical gaps (kappa = 1: oc20_01 and uniform_02; kappa = 2: uniform_02 and uniform_04) are distinct
  runs from different initial conditions that reach equivalent minima. Each reproduces its own published jsonl value,
  and their `max_displacement` values differ (kappa = 1: 2.135e-4 vs 2.134e-4; kappa = 2: 3.206e-10 vs 7.105e-15).
- The exact minimiser moves from the shifted-force one by at most 8.3e-4 (kappa = 1) and 1.1e-6 (kappa = 2) in any
  coordinate (`max_displacement`).

Observations (Tier X, 24 relaxed stages, not a statistical sample):
- No relaxed configuration is below the exact triangular lattice under the exact potential (`below_exact_floor`
  false for all 24). The published P1 observation therefore holds for these seeds with the potential that the
  theorem covers.
- The perfect lattice found by the published uniform_00 anneal at kappa = 1 is a minimum of the exact potential with
  gap exactly 0.
- The large absolute shift (1.77e-2 at kappa = 1) is common to every configuration. It cancels in the gaps, which
  change by at most 5.3e-7 at kappa = 1, at least 860 times smaller than the smallest nonzero gap (4.58e-4), and by
  about 1e-10 or less at kappa = 2. The defect counts are unchanged.
- The published P2 failure at kappa = 1 (annealing from OC20 does not reach the lattice) is a dynamics statement, not
  an energy one. It is not re-tested here, because annealing was not re-run under the exact potential.

**Negative control (N-c), square-lattice saddle under the exact potential** (`results/exact/exact_saddle.jsonl`):
| kappa | negative Hessian modes, published sf (`results/controls.jsonl`) | negative modes, exact | e_after - e_tri, published sf | e_after - e_tri, exact |
|---|---|---|---|---|
| 2 | 72 | 72 (lowest -0.4137) | 2.224733e-3 | 2.224729e-3 |
| 1 | 64 | 64 (lowest -0.5302) | 2.859127e-3 | 2.856510e-3 |

The perfect square lattice in the 17x17 box is the starting point. After a 1e-3 perturbation, CVODE lowers the
energy, and the result stays above e_tri (each potential measured against its own e_tri).
- So the exact-potential pipeline does detect an unstable non-optimal lattice. The 17x17 box cannot hold the
  triangular lattice, hence the positive final gap.

Figures (generated by `scripts/exact_figures.py`, PDF and PNG):
- `fig_cutoff_sweep`: error of shifted-force, plain-cut and plain+tail lattice energies vs r_c, with the
  square-triangular gap as reference.
- `fig_relaxed_gaps`: shifted-force gap vs exact gap per relaxed stage.

Copies of all figures and JSON are in
`/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/papers/ar_yukawa_crystal/data/`.

## 5. Code, tests, commits

- Worktree /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h2, branch physics/ar-yukawa-2026-10-25. The base is
  origin/main 47ef5044c10b04c64d8c86f483f1aa47c400ab28. Nothing was pushed.
  - Code commit: cc5a8aed81b3228bd9e9eb69f2c326f926903a34.
  - Results commit (HEAD): 7f2a45c32a9eb9722ca36c334329cb7a5a541951.
  - Both SHAs come from `git rev-parse`.
- `bash crates/qf-yukawa-crystal/scripts/check_crate.sh` runs `cargo fmt --check`, clippy (no warnings printed) and
  `cargo test --release -- --test-threads=2`. Result: 24 passed, 0 failed, 1 ignored (pre-existing).
- The 5 new tests in `exact::tests` are:
  - direct_sum_matches_ewald_splitting
  - voronoi_circumradius_known_values
  - shifted_force_reproduces_published_reference
  - perfect_lattices_in_image_box_equal_lattice_sum
  - exact_force_and_hessian_match_finite_differences
- The published shifted-force path is unchanged, and the re-runs reproduce the published energies (section 4).

## 6. Scope and honest limits

- Classical, periodic, density one, N = 288 (triangular box) or 289 (17x17 box); 24 relaxed stages from 21 runs. That is a subset of the published study: 11 of 50 stages at kappa = 1 and 13 of 100
  at kappa = 2.
  These are floating-point observations (Tier X). They are consistent with planar universal optimality for the
  exact Yukawa potential, but they are not evidence for it in any proof sense.
- The theorem-side statement (Tier A, FORMAL.md) is conditional on upstream openai/math universal_energy_minimum
  (AI-generated, not peer reviewed) and on definition fidelity.
- Annealing under the exact potential was not run, so the kappa = 1 P2 (dynamics) failure is untested here.
- The rigorous tail bound covers the infinite-lattice sums. For the periodic box only the continuum tail estimate is
  reported (1.3e-17 at kappa = 1, 6.7e-18 at kappa = 2). The existing `global_opt::tail_bound` gives a rigorous box
  bound if one is needed.
- The 2D Debye-Hueckel K0 potential is not studied; the potential is the 3D-screened e^{-kappa r}/r in the plane.

## 7. Hugging Face data

- **Search.** On 2026-10-25 the Hub (public, unauthenticated, `scripts/hf_search.py`, output
  `/home/callensxavier_gmail_com/hf-data/yukawa_crystal/hub_search.json`) was searched for "dusty plasma",
  "dusty-plasma", "complex plasma", "colloid", "colloidal", "yukawa" and "wigner crystal". It returned only two
  datasets, and neither contains particle data:
  - `YangyangTan/yukawa-2d-diffusion` (rev bf47f82f366dc5d2e192f23aeda6bd74fdef0db9, MIT) holds lattice-field-theory
    configurations of a Yukawa *coupling* (scalar field on a 16x16 grid). That is a name collision, not particle
    positions.
  - `VIJAYALAKSHMI10/Colloidal_model` (rev b29728fe06acc75efcd714eae0de4bcf2c222461) has no license, an empty
    README and two small text files.

  So no dusty-plasma or colloid particle dataset was found. Only README metadata was downloaded
  (`scripts/hf_inspect.py`, into `/home/callensxavier_gmail_com/hf-data/yukawa_crystal/`).
- **OC20, kept for the initial conditions.** Dataset `colabfit/OC20_IS2RES_val_id`, license CC-BY-4.0, dataset DOI
  10.60732/b4005525, shard `co/co_10.parquet` (142,986,687 bytes).
  - The prior-round provenance file did not record a revision. `scripts/hf_shard_check.py` (output
    `hf-data/yukawa_crystal/oc20_shard_check.json`) compared the shard against the Hub:
    - local shard sha256: 9e4249ba20cf4cdc46f69e7fe6deb19be286dd19c9f1cf85d350816d2b1e748b;
    - Hub LFS sha256 at the current revision 6a1dfef12aec878b4cda99edd54b16a6a254e135: the same, so they match.
  - The initial conditions `data/initial/oc20_tri_box_*.csv` and `oc20_square_box_*.csv` are therefore traceable to
    revision 6a1dfef12aec878b4cda99edd54b16a6a254e135. The check is that the file content is identical; the date of
    the original download was not recorded.
  - No new download was made in this stage.
