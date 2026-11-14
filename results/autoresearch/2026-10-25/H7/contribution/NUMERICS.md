# H7 stage 2 (NUMERICS): the σ = 3 shell flow under CVODE, with controls and data-driven initial conditions

Tier X throughout. These are floating-point runs: they illustrate and stress-test the Lean statements in
`FORMAL.md` (`ham_conserved`, `energy_conserved`, `enstrophy_bound_along_flow`), and they do not support them.
No breakthrough claim.

## Code and provenance

- Rusty worktree `/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7`, branch `physics/ar-sigma3-shell-2026-10-25`, based on `47ef504` (origin/main). Not pushed.
  - Code commit `99f5df89e8d8380ea1a9f065ae87308e779224fc` (from `git rev-parse HEAD`). It adds `crates/qf-shell-cascade/src/sigma.rs` and `src/bin/sigma3_study.rs`, adds cvode/nvector as dependencies, and extends the README.
  - Results commit `e869e5fc4e38df24bc93ee2c22e19f2e68920041`, which adds `crates/qf-shell-cascade/results/sigma3/`. The study JSON records `git_sha = 99f5df89…24fc`: the binary was rebuilt at that commit and the tree was clean apart from untracked logs.
  - Supplementary σ = 2 probes commit `dfa9a0880450a7601e1ecdcb735b5897c6319ffd` (`sigma2_probes.jsonl`, `run_probes.py`, regenerated figures). These were run with the same binary.
- Model (`sigma::SigmaModel`), shells n = 0..n_max, k_n = 2ⁿ, truncation v_{n_max+1} = 0:
  `dv_n/dt = k_{n−1} v_{n−1}² − k_n conj(v_n) v_{n+1} − i D k_n^σ v_n`.
  This is the Lean `F kk (fun m => D * kk m ^ σ)` with Lean's N + 2 shells, so Lean N = n_max − 1 (recorded as `lean_N` per run).
  Monitored quantities:
  - S = Σ|v_n|²
  - Ω = ½ Σ k_n²|v_n|²
  - H_σ = Σ 2⁻ⁿ D k_n^σ |v_n|² + Σ_{n<n_max} 2⁻ⁿ k_n Im(conj(v_n)² v_{n+1}), the Lean `hamG` and `ham3` weights taken literally
  - bound ratio = 2DΩ(t) / (H_σ(0) + S(0)^{3/2})
  For σ = 3, the Lean bound says this ratio is ≤ 1.
  The H drift is measured relative to |Q| + Σ|cubic terms| at t = 0, because Q and C can nearly cancel.
- Integrator: this workspace's CVODE, `Method::Bdf`, with the analytical Jacobian (unit-tested against central differences), `rtol` as stated and `atol = 1e-3·rtol`. It runs in `Task::OneStep` mode, and every invariant is evaluated at **every internal step**, with no interpolation. Every supremum is over internal step points. `t_reached` is the last internal time, which is at least the requested T and is recorded per run.
- D = 0.05 for every run, fixed across N. Initial data are normalised to S(0) = 1. By the scaling v → λv, t → t/λ this is equivalent to D_eff = D/λ in data units.

## Commands (run as given; every Lean/Rust/Python job on cores 4-7, at most 2 threads)

```
# build and test (run_cargo.py pins cores 4-7 and sets CARGO_TARGET_DIR=/home/callensxavier_gmail_com/rusty-target-ar)
/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/scripts/run_cargo.py /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/cargo_test_full.log test --release -j 2 --offline -p qf-shell-cascade -- --test-threads=2
  -> 32 unit tests (5 new sigma tests among them) + 2 positive_control.rs tests, all ok, RC 0
/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/scripts/run_cargo.py /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/cargo_clippy.log clippy --release -j 2 --offline -p qf-shell-cascade --all-targets
  -> RC 0, 0 warnings
/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/scripts/run_cargo.py /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/cargo_fmt.log fmt -p qf-shell-cascade
  -> RC 0
# timing probe (chooses the N range)
taskset -c 4-7 /home/callensxavier_gmail_com/rusty-target-ar/release/sigma3_study probe 7 3 0.05 0.1 1e-10
# HF data -> shell spectrum (h5py exists only in the venv-pta interpreter; the AutoevolveAI .venv lacks it)
/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/scripts/hf_get.py /home/callensxavier_gmail_com/hf-data/sigma3_enstrophy/
taskset -c 4-7 /mnt/disks/disk-socrateai-local-1/venv-pta/bin/python -I /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/scripts/well_spectrum.py /home/callensxavier_gmail_com/hf-data/sigma3_enstrophy/data/test/turbulent_radiative_layer_tcool_0.32.hdf5 /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/well_spectrum.json
/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/scripts/make_amps.py /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/well_spectrum.json /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/well_amps.txt
# study, supplementary probes, summary, figures
taskset -c 4-7 /home/callensxavier_gmail_com/rusty-target-ar/release/sigma3_study full /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/sigma3_study.json /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/well_amps.txt 99f5df89e8d8380ea1a9f065ae87308e779224fc
/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/scripts/run_probes.py /home/callensxavier_gmail_com/rusty-target-ar/release/sigma3_study /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/sigma2_probes.jsonl
/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/scripts/summarise.py /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/sigma3_study.json /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/summary.json
taskset -c 4-7 /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/scripts/make_figures.py /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/sigma3_study.json /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/well_spectrum.json /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/figures /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade/results/sigma3/sigma2_probes.jsonl
```
The full study took 143.7 s wall (`total_wall_s` in the JSON) as a single-threaded process pinned to cores 4-7. The longest single run took 40.5 s (σ = 3, n_max = 7, T = 2, rtol = 1e-10, 6,325,180 BDF steps). The supplementary probes took under 20 s in total; the longest was 9.2 s at n_max = 10.

## Cost and choice of N range (timing probe, real output)

```
probe_decaying:  n_max=6 sigma=3 D=0.05 rtol=1e-10 steps=43970  t=0.100 0.3s
probe_decaying:  n_max=7 sigma=3 D=0.05 rtol=1e-10 steps=316335 t=0.100 2.7s
```
The step count grows about 7× per added shell. It is set by the top-shell frequency D·8^{n_max}, which lies on the imaginary axis, where BDF orders above 2 are not A-stable, so CVODE has to resolve the rotation. Extrapolating from the measured n_max = 6 and 7 step counts (not a measurement), n_max = 8 would cost about 45 M steps, about 5 min, for T = 2, and n_max = 10 would cost about 2 G steps, which is infeasible. The sweep therefore stops at n_max = 7 (Lean N = 6).

## Results (from `summary.json`; gates computed by `summarise.py`, all True)

### Positive control: conservation converges with tolerance (σ = 3, decaying data |v_n| ∝ 2^{−1.5n}, T = 2)

| n_max | rtol | max rel ΔS | max rel ΔH₃ | BDF steps |
|---|---|---|---|---|
| 4 | 1e-6 | 5.40e-7 | 2.64e-5 | 5,405 |
| 4 | 1e-8 | 1.75e-8 | 8.56e-7 | 7,302 |
| 4 | 1e-10 | 3.97e-10 | 1.94e-8 | 15,460 |
| 6 | 1e-6 | 1.17e-6 | 6.28e-4 | 188,969 |
| 6 | 1e-8 | 3.15e-8 | 1.70e-5 | 408,026 |
| 6 | 1e-10 | 6.92e-10 | 3.73e-7 | 878,138 |

From rtol 1e-6 to 1e-10, both drifts shrink by more than a factor of 100 (gate True).

### Negative control: perturbed coupling (outgoing k₁ in B₁ multiplied by 1.01, same data, same rtol sweep)

| n_max | rtol | max rel ΔS | max rel ΔH₃ |
|---|---|---|---|
| 4 | 1e-6 / 1e-8 / 1e-10 | 2.62e-3 / 2.62e-3 / 2.62e-3 | 2.31e-3 / 2.34e-3 / 2.34e-3 |
| 6 | 1e-6 / 1e-8 / 1e-10 | 4.57e-3 / 4.57e-3 / 4.57e-3 | 5.92e-3 / 5.46e-3 / 5.45e-3 |

The drift stays at O(ε) and does not change with rtol, so it is a structural break, not integrator error (gate True).
At rtol = 1e-10 the drift ratios (negative over positive) are:
- ΔS: 6.6e6 at both n_max = 4 and n_max = 6
- ΔH₃: 1.2e5 at n_max = 4 and 1.5e4 at n_max = 6
The perturbed runs still have bound ratio below 1 (0.270 and 0.350). The perturbation breaks conservation, not the measured bound, and no bound violation is claimed for it.

### σ = 3 truncation sweep (decaying data, 2 phase seeds, n_max = 2..7, T = 2, rtol = 1e-10)

- The bound holds on every run. The largest sup_t ratio is 0.360, and per n_max the ratio lies in 0.25–0.36 with no trend in N. See `fig_truncation_sweep`, left panel.
- In 12 of 12 runs the supremum is above the t = 0 value, so the dynamics move the ratio.
- Maximum drifts over the sweep are ΔS 2.1e-9 and ΔH₃ 4.0e-6. The worst H₃ drift is at n_max = 7, where the step count is 6.3 M.
- The signed final S drift is negative in 11 of 12 runs, with magnitude at most 2.1e-9. This is consistent with slight BDF numerical damping and is not physics.

### σ = 2 control (top-shell data: v_{n_max} = 1, other shells 1e-3, random phases, S = 1, T = 0.5)

| n_max | σ = 2: sup ratio with H₂ | σ = 3: sup ratio with H₃ |
|---|---|---|
| 2 | 0.667 | 0.444 |
| 3 | 2.286 | 0.762 |
| 4 | 7.111 | 0.928 |
| 5 | 19.69 | 0.981 |
| 6 | 48.76 | 0.995 |
| 7 (supp.) | 110.70 | not run |
| 8 (supp.) | 237.45 | not run |
| 9 (supp.) | 492.75 | not run |
| 10 (supp.) | 1004.38 | not run |

The rows marked "supp." come from `sigma2_probes.jsonl`: same binary, same seeds (7 + n_max), T = 0.5, rtol = 1e-10.

- **Growth law, measured.** From n_max = 6 to 10 the local log₂ steps of the σ = 2 ratio are 1.18, 1.10, 1.05 and 1.03, so the ratio approaches 2^{n_max} growth. Over n_max = 2..6 alone the fitted slope is 1.55. This matches the t = 0 closed form D·4ⁿ/(D·2ⁿ + 1), which tends to 2ⁿ once D·2ⁿ ≫ 1.
- **On top-shell data the supremum equals the t = 0 value.** The σ = 2 failure there is the static ratio, carried along the trajectory.
- **The C2 drifts do not test H₂ conservation.** On these runs ΔH equals ΔS to three digits for both σ. With the other shells at 1e-3 the nonlinearity is negligible, so both numbers measure BDF damping of the top-shell rotation, not conservation.
- **H₂ conservation on cascading data** (supplementary decaying σ = 2 runs, same seeds as P1, T = 2):
  - n_max = 4: max rel ΔH₂ 8.2e-10, ΔS 3.8e-10.
  - n_max = 6: ΔH₂ 9.9e-11, ΔS 1.1e-11.
  - n_max = 7..10 at T = 0.5: ΔH₂ at most 1.5e-9.
  This matches the Lean finding that the rate identity holds for every ω (σ = 2 included). It is a floating-point check, not evidence for the theorem.
- **A dynamical σ = 2 observation (Tier X).** On the same decaying data, σ = 2 enstrophy grows during the run: Ω goes from 0.85 to sup 19.4 at n_max = 4 and from 0.87 to 32.6 at n_max = 6. The σ = 2 analogue ratio therefore rises from 0.069 to 1.57 and from 0.065 to 2.43, crossing 1. The σ = 3 runs from the identical initial states (P1) stay at 0.27 and 0.35. This is one D and two seeds, an illustration only.
- For σ = 3 the same data approach the bound (0.995 < 1) and never cross it. This top-shell family is close to extremal, because H₃(0) ≈ 2DΩ(0).
- At n_max = 6 the σ = 3 top-shell runs have the largest S drift of the study, −2.8e-5 (signed, damping), because the rotation D·8⁶ ≈ 1.3e4 is fast.

### Data-driven initial conditions (HuggingFace, The Well)

- Dataset: `polymathic-ai/turbulent_radiative_layer_2D`, revision (commit sha) `2ee7756575ff6f90981d0308cbcb6a2ab5995bdc`, license **CC-BY-4.0** (dataset card). The card cites Fielding et al., ApJL, doi 10.3847/2041-8213/ab8d2c, and Athena++.
- Files downloaded to `/home/callensxavier_gmail_com/hf-data/sigma3_enstrophy/` (untrusted data, read with `python -I`):

  | file | size (bytes) | sha256 |
  |---|---|---|
  | `data/test/turbulent_radiative_layer_tcool_0.32.hdf5` | 109,051,904 | `06cbd36c…f747` |
  | `README.md` | 5,804 | `53aadbad…1501` |
  | `turbulent_radiative_layer_2D.yaml` | 488 | `60f768b6…1fce` |
  | `stats.yaml` | 576 | `f57e18d8…2b62` |

  Full hashes are in `download_record.json`. The total download is about 110 MB.
- File layout: `t1_fields/velocity` has shape (1, 101, 128, 384, 2), and t_cool = 0.32. x has 128 points and is **PERIODIC**; y has 384 points and is OPEN.
- Spectrum method (`well_spectrum.py`; velocity only, not √ρ·u):
  - FFT along x only. kx = 0, the x-mean that carries the mean shear, is removed.
  - The one-sided spectrum is averaged over y and summed over the two components.
  - Dyadic shells are kx ∈ [2ⁿ, 2^{n+1}) for n = 0..5. kx = 64 is Nyquist and is excluded.
  - |v_n| = √(2E_n).
  - The snapshots are developed-turbulence time indices 25, 50, 75 and 100 (dataset time 39.93, 79.85, 119.78, 159.70), not the seeded t = 0 noise.
- Pipeline controls (all pass):
  - Parseval: shell sum plus Nyquist equals ½⟨|u − ⟨u⟩_x|²⟩, with relative error at most 4.0e-16. The Nyquist energy is at most 4.2e-9 in data units, against fluctuation energies of 1.0e-4 to 3.0e-4.
  - A synthetic sin(2π·8x/Lx) field puts 100% of its energy in shell 3.
  - White noise gives E_n ∝ 2ⁿ (log₂ slope 1.01), while the data slopes are −2.13, −1.56, −1.79 and −1.81.
- Runs:
  - Each snapshot's moduli (normalised to S = 1) get 2 random phase seeds. The spectrum carries no phases, and the cubic part of H₃ depends on them.
  - Truncations n_max = 5, 6, 7; shells above n = 5 start at zero. This is a family with N-uniform Ω(0) and E(0), the class the cutoff-uniformity caveat requires.
  - σ = 3, T = 2, rtol = 1e-10, 24 runs in all.
- Results:
  - The bound holds on all 24 runs, with the largest sup ratio 0.631 (t index 75, seed 11, identical at every n_max).
  - In 24 of 24 runs the supremum is above the t = 0 ratio.
  - The sup ratio is the same at n_max = 5, 6 and 7 to the printed 4 digits, because over T = 2 almost no energy reaches the zero-initialised top shells. With this horizon the data therefore do not probe the cutoff dependence, only the bound on realistic spectra.
  - Drifts: ΔS ≤ 2.4e-8 and ΔH₃ ≤ 1.2e-6. The largest drifts are at n_max = 5, where shell 5 starts populated.

### Figures (generated from the JSON by `make_figures.py`, PDF + PNG)

- `fig_conservation_controls`: drift against rtol, positive and negative controls.
- `fig_truncation_sweep`: the σ = 3 sweep, and the σ = 2 against σ = 3 control.
- `fig_well_data`: The Well shell spectra with the white-noise control, and one data-driven 2DΩ(t) against its bound.

All three are copied to `papers/ar_sigma3_enstrophy/data/` together with `sigma3_study.json` (sha256 `9813b31b…f88a`), `summary.json`, `well_spectrum.json` (sha256 `ec8083a7…301e`), `well_amps.txt`, `sigma2_probes.jsonl` and `download_record.json`. The σ = 2 panel of `fig_truncation_sweep` includes the supplementary n_max = 7..10 points and a 2ⁿ reference line drawn through the n_max = 10 point.

## Scope and caveats

- Tier X. Every number here is a floating-point measurement at finite T, finite N ≤ 7 and fixed D = 0.05. The claimed content is in the Lean theorems; these runs only show that the integrator and the model agree with them, and that the controls separate.
- Suprema are over internal BDF step points, not over continuous t.
- The S drift has a consistent negative sign, which is BDF damping of fast rotations. It is largest for top-shell data: −2.8e-5 at n_max = 6 for σ = 3, and −1.3e-4 at n_max = 10 for σ = 2.
- **Damping cannot explain the passes.** Damping lowers Ω, so integrator error leans toward passing the bound. In S3 and W, however, the smallest margin to the bound is 1 − 0.631 = 0.37, while H₃ drifts by at most 4.0e-6. In C2 for σ = 3, the supremum (up to 0.995) is attained at t = 0, where no integration error enters.
- Phases for the data-driven runs are random (2 seeds), not taken from the data. The spectrum is 1D along the periodic x direction only. The mapping from a compressible, radiatively cooling 2D flow to a 1D dyadic shell model is an illustration, not a physical model of that flow.
- n_max > 7 is out of reach for this BDF path. CVODE's step count scales like T·D·8^{n_max}. An exponential or splitting integrator for the linear rotation would be needed, and none is attempted here.
