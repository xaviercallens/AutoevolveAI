# H8 stage 2: numerics (Tier X) and data (Tier L)

Lane H8 (`bogoliubov_sk`). All numbers below were copied from tool output. Nothing here is Tier A.

- **rusty-SUNDIALS worktree:** `/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h8`, branch `physics/ar-bogoliubov-2026-10-25`
- **Commits** (read with `git rev-parse HEAD`; not pushed):
  - `e1449988a91d8a38a7deee7f1106cfa3962c5759`: code and results.
  - `fdd6d2d64fbab0dcaad60fa7b7877d96095c2776` (**HEAD**): README wording, strict ⁴He variant, exact x = 1 ratio, test log re-run on the final text.
- **Crate:** `crates/qf-gpe2d`. Results are in `crates/qf-gpe2d/results/bogoliubov_sk/`.
- **Copies for the paper:** `papers/ar_bogoliubov_sk/data/`.

## 1. What was built (the rusty-SUNDIALS improvement)

- **`qf_gpe2d::linear_response`** (new module) does the following:
  - relaxes the uniform GP ground state in imaginary time, starting from a perturbed state (max residual of |ψ|²−n₀ is 4.3e-14);
  - imprints a weak phase kick `ψ→ψ·exp(iε cos k·r)` or density kick `ψ→ψ·√(1+ε cos k·r)` on one grid wavevector, with box `L = 2π|m|/k`;
  - records the density cos-component A(t) at k;
  - reads ω in two ways: from a least-squares line through the zero-crossing times, and from a golden-section least-squares sinusoid fit.
- **Phase kicks give a second estimator.** Continuity gives A(t) = (n k² ε/ω) sin ωt, so the amplitude provides S_amp = A/(2nε) = ε₀/ω (the f-sum route).
- **`evolve_observe`**: one shared FFT plan plus a per-step observer. This avoids the per-step FFT replanning that the crate README warns about.
- **`Splitting {PythonReference, Strang}`**: see the finding below. `step`/`evolve` are unchanged, so `tests/python_cross_check.rs` still passes.
- **Example:** `examples/bogoliubov_dispersion.rs` runs the full sweep with its controls and writes JSON. `examples/lr_series.rs` dumps one time series.
- **Tests:** `tests/linear_response.rs`, 5 tests covering the controls below.

### Finding: the upstream split step is not Strang

**Symptom.** The first sweep failed its positive gates. Max |ω−ε_B|/ε_B was 1.2e-2, and S_amp was up to 25% above S_freq. The amplitude error halved with dt, so it was first order.

**Diagnosis.**
- `which_strang.py` replays the pinned 4x4 Python reference data from `tests/python_cross_check.rs`.
- The reference reuses the start-of-step nonlinear phase on both sides of the kinetic step: max deviation 2.48e-16.
- A textbook Strang step, which recomputes |ψ|² after the kinetic step, deviates by 0.155.
- So the upstream `quantumfluids.gpe.solver2d.step`, as pinned, is not the symmetric Strang composition.

**Effect on the measurement** (`dt_convergence_reference`, k/k_s = 1, eps = 1e-4):
- The frequency still converges at second order: errors 7.31e-6 → 3.00e-8, observed orders 2.00, 2.00, 1.99, 1.95.
- The amplitude converges at first order: S_amp relative errors 2.65e-2, 1.31e-2, 6.54e-3, 3.26e-3, 1.63e-3, observed order max 1.013.
- A long-wavelength run (k = 0.1, 32x32 grid) grows exponentially from round-off late in the record. The cos-amplitude went from about 1e-7 to 3.8e-4 in the last 25 of 1201 steps.

**Fix.** `Splitting::Strang` cures both problems. The `max_dt` cap that was added first is **not** what fixed it: with Strang, the uncapped sweep reproduced the capped one (max relative ω error 4.09e-5 in both). The cap is kept as a conservative guard.

**Why it behaves this way** (expected, not a mystery). Reusing the old density on both sides makes the step a non-symmetric (symplectic-Euler-like) composition of the linearised flow. Its eigen-frequency error is O(dt²), but the invariant ellipse is distorted at O(dt). So the frequency estimator converges at second order while the amplitude estimator converges at first order. The k = 0.1 late-time growth is an observation from one run only, and its mechanism was not analysed.

**Scope.** This affects time-resolved dynamics computed with the upstream step. Energy and norm tests do not see it, because both compositions are pure phase rotations.

## 2. Commands

All runs were pinned to cores 4-7.

```
CARGO_TARGET_DIR=/home/callensxavier_gmail_com/rusty-target-ar cargo build --release -j 2 --offline \
  --manifest-path /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h8/Cargo.toml -p qf-gpe2d --examples
taskset -c 4-7 /home/callensxavier_gmail_com/rusty-target-ar/release/examples/bogoliubov_dispersion \
  .../results/bogoliubov_sk/linear_response.json                          # wall 409.11 s
python -I .../results/bogoliubov_sk/summarize.py linear_response.json linear_response_summary.json
python -I .../results/bogoliubov_sk/crosscheck_compare.py .../release/examples/lr_series crosscheck_rust_numpy.json
python -I .../results/bogoliubov_sk/which_strang.py .../tests/python_cross_check.rs
python -I .../results/bogoliubov_sk/helium_tier_l.py helium_tier_l.json
python -I .../results/bogoliubov_sk/make_figures.py .../results/bogoliubov_sk .../figures
python -I .../results/bogoliubov_sk/run_cargo.py cargo_test.log test     # also: fmt, clippy
```

**Cargo test.** Exit 0, all 15 tests pass. The run was repeated on the final committed text, after fmt; `cargo fmt --check` exits 0.
- 9 library unit tests, including the 2 new ones in `linear_response`;
- the 5 new linear-response tests;
- the 1 Python cross-check.

`cargo fmt` exited 0. `cargo clippy --all-targets` exited 0 with no warnings. The logs are in `results/bogoliubov_sk/cargo_*.log`.

## 3. Linear-response results

The script `summarize.py` evaluates 14 gates, and all pass (`all_pass: true` in `linear_response_summary.json`).

**Units and setup:**
- ħ = m = 1, n₀ = 1, g = 1, so c = 1, k_s = 2mc/ħ = 2 and ξ = 1/√2.
- Grid 32x32, mode (2,0), 6 reference periods.
- 200 steps per period, with dt also capped at max_dt(grid, 0.25).
- ε = 1e-3.
- 25 wavevectors, k/k_s from 0.05 to 5 (log spaced).

| Gate | Value | Threshold |
|---|---|---|
| **Positive controls** | | |
| g=1 phase kick: max \|ω−ε_B\|/ε_B | 4.093e-05 | < 1e-4 |
| g=1 density kick (independent readout): max rel. err | 4.064e-05 | < 1e-4 |
| f-sum amplitude vs period estimator: max \|S_amp−S_freq\|/S_freq | 1.638e-04 | < 5e-3 |
| Strang dt refinement: min observed order (first 3 halvings) | 2.000 | > 1.8 |
| Isotropy, same \|k\| on modes (2,0), (1,1), (2,2): max rel. err | 1.777e-07 | < 1e-4 |
| Relaxed ground state: max \|\|ψ\|²−n₀\| | 4.308e-14 | < 1e-10 |
| **Negative controls** | | |
| g = 0 control: max \|ω−k²/2\|/(k²/2) | 7.787e-13 | < 1e-9 |
| g = 0 vs the g=1 ε_B for k/k_s < 1: min relative distance | 0.3355 | > 0.1 |
| Reference splitting: max \|S_amp−S_freq\|/S_freq (recorded failure) | 0.2497 | > 5e-3 |
| Reference splitting: amplitude convergence order (max) | 1.013 | < 1.5 |
| **Bound level (mirrors the Lean controls)** | | |
| g=1: max S_freq/√(k/2k_s) − 1 | −1.381e-03 | < 1e-4 |
| g=1: \|S/bound − 1\| at the sweep point nearest k = k_s (x = 1.0772); this is the exact-theory value S_B/bound − 1 = −1.381e-3 at that x, not numerical error | 1.381e-03 | < 2e-3 |
| g=0 (S = 1): fires at every sweep k < 2k_s | true | — |
| g=0 (S = 1): silent at every sweep k > 2k_s (the test is one-sided) | true | — |

**Strang convergence** (relative ω error at dt = max_dt(grid, s) for s = 1, ½, ¼, ⅛, 1/16; eps = 1e-4):

| k/k_s | Relative ω errors | Observed orders |
|---|---|---|
| 0.25 | 3.83e-5, 9.58e-6, 2.39e-6, 5.96e-7, 1.47e-7 | 2.00, 2.00, 2.00, 2.02 |
| 1 | 1.27e-6, 3.16e-7, 7.81e-8, 1.85e-8, 3.56e-9 | 2.00, 2.02, 2.08, 2.37 |
| 4 | 9.17e-9, 2.16e-9, 3.93e-10, 4.36e-11, 1.55e-10 | 2.08, 2.46, 3.17, −1.83 |

At k/k_s = 4 the error reaches a floor of about 1e-10. This is the least-squares/zero-crossing resolution, not the scheme. At k/k_s = 1 the Strang S_amp error falls from 8.90e-6 to 1.22e-8.

**Tangency at k = k_s exactly** (`informational` in the summary): S_freq/√(k/2k_s) − 1 is −3.56e-9 at x = 1 (finest dt, ε = 1e-4) and +6.07e-8 at x = 1 (ε = 1e-3, 200 steps per period). Both are at the level of the measured discretisation and ε² errors.

**Nonlinearity** (k = k_s, 200 steps per period):

| ε | Relative ω error |
|---|---|
| 1e-3 | −6.07e-8 |
| 3e-3 | −1.18e-6 |
| 1e-2 | −1.39e-5 |
| 3e-2 | −1.25e-4 |

The shift scales as about ε², as expected for the leading nonlinear correction. That is why the convergence runs use ε = 1e-4.

**Two-language cross-check** (Rust `lr_series` vs the independent 1D numpy `numpy_crosscheck.py`, Strang, safety 0.25):

| k/k_s | ω relative difference | Amplitude relative difference |
|---|---|---|
| 0.05 | 1.6e-12 | 2.4e-9 |
| 1 | 1.9e-14 | 1.3e-9 |
| 4 | 1.6e-13 | 1.5e-9 |

The amplitude difference comes from the two fits: Rust fits at the golden-section ω, numpy at the zero-crossing ω.

**What this numerics shows, and what it does not:**
- It shows that the GP linear response reproduces ε_B(k) = √(ε₀(ε₀+2gn)) within the measured discretisation error.
- It shows that the measured Bijl–Feynman S = ε₀/ω stays under √(k/2k_s) and touches it near k = k_s.
- It shows that the free control S = 1 violates the threshold for k < 2k_s. These are numerical counterparts of `sBog_le_sqrt`, `diffraction_silent_on_sBog` and `diffraction_fires_free_at_selfdual`.
- **It is not an independent measurement of a quantum static structure factor.** A classical GP field has no quantum density fluctuations. S = ε₀/ω is the Bijl–Feynman identification, which is exact for Bogoliubov theory and is the same by-construction point the verifier flagged for `feynman_sBog_exact`. S_amp is the same quantity reached through the f-sum rule; its agreement with S_freq checks the time stepper, not many-body physics.
- All of this is Tier X.

## 4. HuggingFace search: no S(k) dataset exists

**Search.** `hf_search.py` ran 30 queries through `HfApi.list_datasets` (public metadata, no token). The full record is `hf_search.json`. The queries included:
- structure factor, static/dynamic structure factor;
- liquid helium, helium-4, superfluid helium, helium;
- neutron scattering/diffraction, neutron, x-ray diffraction liquid;
- Bose-Einstein condensate, BEC, Bragg spectroscopy, cold atoms, ultracold, absorption imaging, quantum gas, superfluid, Bogoliubov, condensate;
- pair/radial distribution function, phonon, scattering, SANS.

None of the hits is a measured S(k), S(Q,ω), Bragg-spectroscopy or cold-atom-image dataset. The "helium" and "BEC" hits are name collisions: LLM checkpoints, EEG, robotics, Sanskrit and so on.

**The one plausible hit is out of scope.**
- Dataset: `popoff4rtem/2D-Neutron-Diffraction-Dataset-for-Discriminative-Models`, sha `648119c2030c5352c37a305deb74aa8ec84a4402`, MIT licence tag.
- Only its card and file list were fetched (`hf_card.py`, recorded in `hf_neutron_card.json`; card stored at `/home/callensxavier_gmail_com/hf-data/bogoliubov_sk/neutron_diffraction_card/`).
- The card holds only the licence header and no description.
- The data are Python pickles: `datasets/dataset.pkl` is 4.38 GB, plus three 3–6 MB files. They are named for discriminative ML on 2D diffraction maps.
- Nothing identifies them as a liquid or ⁴He S(Q).
- Not downloaded, not used, not substituted.

**Conclusion.** No HuggingFace dataset is used to illustrate this lane. The real-data illustration below uses a published table (Tier L), and it is not from HF.

**BEC literature was checked and rejected for the absolute test.**
- Steinhauer et al., arXiv:cond-mat/0111438: measured S(k) is shown only in a figure, after multiplying by 2.3 "giving rough agreement with S(k) from Bogoliubov theory".
- Shammass et al., arXiv:1207.3440: S(k) is shown only in a figure, multiplied by 1.5 to agree with a 2D GPE simulation.
- An absolute threshold test cannot be applied to data rescaled toward the model under test. Both are cited only for method: the short-Bragg-pulse standing-wave technique in 1207.3440 is the experimental analogue of the phase kick used here.

## 5. Real data (Tier L, not HF): superfluid ⁴He

`helium_tier_l.py` → `helium_tier_l.json`, `helium_tier_l.out`.

**Source data:**
- Dispersion: Godfrin et al., arXiv:2012.09067v1, Table VI. This is ε(k) at SVP, T < 100 mK, k = 0–3.6 Å⁻¹ in steps of 0.05 (73 rows). Below 0.15 Å⁻¹ the entries are ultrasound data. The table was transcribed from the alphaXiv full text.
- Constants, same paper Sec. II A: c = 238.3 ± 0.1 m/s and m₄ = 4.0026032 g/mol. CODATA values come from scipy.
- Roton cross-check: Beauvois et al., arXiv:1802.08120v3, Table I, gives Δ_R = 0.7416(10) meV at Q_R = 1.9260(2) Å⁻¹.

**Transcription controls** (all pass):
- 73 rows, k uniform in steps of 0.05.
- Table minimum (1.90, 0.7427), against the reference (1.926, 0.7416).
- Table maximum (1.10, 1.1907), against Godfrin Table V (1.103, 1.191).
- ε(0.05) = 0.0787 against ħck = 0.07843, a difference of 0.35%.

**Scales:**
- k_s = 2m₄c/ħ = 3.0038 Å⁻¹, which passes the assert 2.9 < k_s < 3.1.
- ħ²/2m₄ = 0.52218 meV Å².
- ħc = 1.56852 meV Å.

**Threshold at the roton.** √(Q_R/2k_s) = **0.5662** at Q_R = 1.9260. The ±0.1 m/s uncertainty in c moves it to 0.56633 / 0.56609. This confirms round 1's "S ≤ 0.565" figure, to rounding.

**What a dispersion table can decide.** The hypothesis is Feynman's inequality, with the single-excitation branch taken as the lowest density-channel energy. This is exactly what `hfeyn` assumes in the Lean file. It gives S(k) ≤ S_up(k) = ε₀(k)/ε(k), an upper bound. The comparison was made conservatively, using ε − err.
- **Silent (proved, given Feynman's inequality) for every tabulated k from 0.05 to 0.90 Å⁻¹** (18 points): the bound S_up stays under √(k/2k_s) there. Over that range the diffraction test cannot fire on ⁴He.
- **Stricter variant, same answer.** Where the dispersion is anomalous (ε > ħck), multi-phonon states may lie near ħck, below the measured branch. Recomputing with ω_min = min(ε − err, ħck) leaves the silent set unchanged (`silent_set_unchanged_under_strict_variant: true`). The margin at k = 0.5 Å⁻¹ is 0.1665 against a threshold of 0.2885.
- **Undecided from k = 0.95 Å⁻¹ upward** (54 points). At the roton, S_up = 2.66 (k = 1.95), far above 0.566. Only a measured S(k) can decide there. No verified S(Q) table was found on HF or through alphaXiv (two targeted searches), so the round-1 remark "the measured ⁴He peak is far above 0.565" **remains conditional**.
- A dispersion table can never show the test fires, because S_up is an upper bound.

**Dispersion-level comparison** (same data, no S needed). Measured ε(k) against Bogoliubov ε_B = √((ħck)² + ε₀²) with the same c: ε/ε_B = 0.205 at k = 1.95 Å⁻¹, and the minimum is 0.176 at k = 3.6 Å⁻¹. So ⁴He lies far below the weak-coupling (Bogoliubov) dispersion at roton wavevectors. This is the standard statement that ⁴He is not a weakly interacting gas, now read directly from the pinned table.

**Controls on the same code path** (pass):
- Bogoliubov S_B built with ⁴He's c fires nowhere.
- The free value S = 1 fires for every tabulated k < 2k_s.

## 6. Figures

Each figure is generated as PDF and PNG by `make_figures.py`. Copies are in `papers/ar_bogoliubov_sk/data/`.

| Figure | Contents |
|---|---|
| `fig_dispersion` | ω(k) from GP linear response (g=1 phase and density kicks, g=0 control) against ε_B and ε₀ |
| `fig_s_over_bound` | S/√(k/2k_s): exact S_B, measured ε₀/ω, f-sum amplitude, and the g=0 control above 1 for k < 2k_s |
| `fig_convergence` | Strang second-order ω convergence at three k, and the reference splitting's first-order amplitude error |
| `fig_helium` | ⁴He Feynman upper bound against the threshold (silent region shaded), Bogoliubov S_B, and measured ε against ε_B and ε₀ |

## 7. Open items

- Tier A for the stage-1 Lean file is still pending an independent recompile (unchanged from FORMAL.md).
- A measured, absolutely normalised ⁴He S(Q) table is still needed to decide the diffraction test at k ≥ 0.95 Å⁻¹, including the roton. Candidates are the neutron and X-ray diffraction literature that the cited papers reference (e.g. Svensson et al. 1980). They were not verified here, so they are not cited.
- The upstream Python `solver2d.step` composition issue should be reported to the QuantumFluids project. It was not done here: no writes outside the lane.
