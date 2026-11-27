# H3 stage 2: Keldysh-jellium Madelung energies of 2D Wigner crystals (Tier X)

Everything here is Tier X, floating-point numerics. None of it supports a theorem. The Lean results (FORMAL.md) cover
the raw, non-neutralised Keldysh lattice sum, where the triangular-optimality statement is expected to read ⊤ ≤ ⊤.
The neutralised (jellium) energy computed here is the physically relevant one for TMD Wigner crystals, and it is
**outside** the theorem. These numbers compare two lattices only, triangular and square, as static classical
lattices: no zero-point motion, no exchange, no general configurations.

Producer only. Nobody independent has rerun this yet.

## Code and provenance
- rusty-SUNDIALS worktree `/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h3`, branch `physics/ar-keldysh-2026-10-25`,
  commit **`2e41505cc9df8c46d2b2d667c89ea53e977218ca`** (from `git rev-parse HEAD`). Not pushed.
- New module `crates/qf-yukawa-crystal/src/keldysh.rs` and binary `src/bin/keldysh_jellium.rs`.
  Scripts are in `crates/qf-yukawa-crystal/scripts/keldysh/` and outputs in `crates/qf-yukawa-crystal/results/keldysh/`.
  Final figures and JSON are copied to `papers/ar_keldysh_tmd/data/`.
- Units: e²/(4πε₀ε̄) = 1. Energies are per particle at density one, so that E(n, r₀) = √n · E(1, r₀√n).
  A run checks this scaling (below).

## Method
- **Real-space V.** Two routes:
  - DLMF 11.5.2: V(r) = ∫₀^∞ e^{−rv}(1+r₀²v²)^{−1/2} dv, by adaptive Gauss–Kronrod 7-15.
  - The Gaussian mixture V(r) = ∫ w(a) e^{−r²/4a}/(2a) da, with w(a) = (1/r₀) erfcx(√a/r₀). This is the same definition as
    `keldysh` in `formal_cert/Autoresearch/KeldyshCM.lean`.
  - erfcx is computed as e^{x²}·erfc(x) below 26 and by its asymptotic series above.
- **Reciprocal kernel.** V̂(k) = 2π/(k(1+r₀k)) = 2π∫ w(a) e^{−ak²} da.
- **Ewald split.** The split is made in the mixture variable at a* = 1/(4α²): Gaussians with a < a* go to real space, the
  rest to reciprocal space. At r₀ = 0 this is exactly the erfc(αr)/r and 2π erfc(k/2α)/k split of `jellium.rs`.
  Per particle, at ρ = 1/A:
  e = ½Σ'V_sr(|v|) + (ρ/2)Σ_{G≠0}V̂_lr(G) − ½V_lr(0) − (ρ/2)V̂_sr(0),
  with V̂_sr(0) = 2π[r₀(erfcx(X)−1) + 2√(a*/π)] and X = √a*/r₀. This closed form follows from
  erfcx′ = 2x·erfcx − 2/√π. For X < 0.1 a series is used instead, to avoid cancellation.
- **Lattice sums.** These are sums over a Bravais lattice (one particle per cell). The tails are cut at e^{−46}.

## Commands (all on cores 4-7)
```
CARGO_TARGET_DIR=/home/callensxavier_gmail_com/rusty-target-ar cargo test --release -j 2 --offline \
  --manifest-path /home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h3/Cargo.toml -p qf-yukawa-crystal -- --test-threads=2
python -I scripts/keldysh/mpmath_refs.py results/keldysh/mpmath_refs.json
keldysh_jellium scan   results/keldysh/scan.json
keldysh_jellium points results/keldysh/large_r0_in.txt results/keldysh/large_r0.json
python -I scripts/keldysh/analyze.py prep  results/keldysh /home/callensxavier_gmail_com/hf-data/keldysh_tmd/tmd_rows.json
keldysh_jellium points results/keldysh/materials_in.txt results/keldysh/materials_out.json
python -I scripts/keldysh/analyze.py final results/keldysh /home/callensxavier_gmail_com/hf-data/keldysh_tmd/tmd_rows.json
```
- **Tests.** The crate test run gave `28 passed; 0 failed; 1 ignored`. The ignored test is pre-existing. The 9 new keldysh
  tests are included. `cargo clippy --all-targets` printed no warnings, and `cargo fmt` was applied.
- **Timing.** The scan binary runs in 0.33 s wall time.

## Results (real output: `analysis.json`, `scan.json`)
| Check | Kind | Result |
|---|---|---|
| Rust DLMF V vs mpmath (π/2r₀)[H₀−Y₀] (40 digits), 28 points, r₀ ∈ {0.05, 0.3, 1, 4}, r ∈ [0.1, 12] | cross-language | max rel. err **1.8e-16** |
| Rust mixture V vs mpmath, same 28 points | cross-language | max rel. err **2.4e-15** |
| V̂_sr + V̂_lr = 2π/(k(1+r₀k)), r₀ ∈ {0, 0.05, 1, 10}, k ∈ {0.1 … 20} | identity | max rel. err 1.8e-15 |
| r₀ = 0: lattice Ewald vs `jellium.rs` N = 288 periodic box (triangular) | positive control | difference **7.0e-14** |
| r₀ = 0 vs Bonsall–Maradudin / Alves et al. ten-digit η (constants in `jellium.rs`) | positive control | tri +5.0e-10, sq −8.3e-10, within the 10-digit rounding of η |
| r₀ = 1e-9 through the erfcx code path, E_K − E_C | positive control | 3.14e-9, i.e. **< 1e-8** as required |
| (E_K − E_C)/(π r₀) as r₀ → 0 | positive control | 0.98585 (1e-2), 0.99858 (1e-3), 0.999858 (1e-4), 0.9999986 (1e-6), 0.99999998 (1e-8) |
| Ewald-parameter independence, α ∈ {0.8, 1.6, 3.2}, r₀ ∈ {0, 0.01, 0.1, 1, 10, 100, 1e4}, tri and sq | positive control | max rel. spread **3.5e-15** |
| r₀ → ∞: r₀(E_sq − E_tri) vs the 2D log-gas value ½[q(e^{iπ/3}) − q(i)], q(τ) = log(√Imτ·\|η(τ)\|²) = 0.005292251258 | positive control (Tier L formula) | rel. deviation −3.4e-3 (r₀=1e2), −3.4e-4 (1e3), −3.4e-5 (1e4), −3.4e-6 (1e5), −3.4e-7 (1e6): converges as 1/r₀ |
| Scaling E(n=4, r₀=0.7) = 2·E(1, 1.4), computed with different α | consistency | rel. diff 9.7e-16 |
| **NEG (a)**: reciprocal half with the wrong sign, −V̂_lr | negative control | the α-spread becomes ≥ **5.3e-2** relative at every r₀ (vs 3.5e-15). Caught. |
| **NEG (b)**: neutralising background dropped | negative control | α-spread ≥ 0.216 relative. Caught. |
| Sign sanity check (not a pipeline control, since E is linear in the kernel): wrong-sign kernel −2π/(k(1+r₀k)) at r₀ = 1e-9 | sanity | E = +1.9605, i.e. 3.92 away from Coulomb jellium |
| E_sq − E_tri over 51 values of r₀√n ∈ [1e-3, 1e2] | result | positive at every point. Min 5.27e-5 (at r₀ = 100), Coulomb value 1.0383e-2 |

The r₀ → 0 limit carries a lattice-independent linear term. By the derivation, Ŵ(0) = lim[2π/k − V̂] = 2πr₀, so
E_K − E_C = +πρr₀ + O(r₀²) for both lattices. The numbers confirm this: dE_tri = dE_sq to all printed digits up to
r₀ = 1e-8. So the triangular–square gap moves only at O(r₀²); it is 1.03833e-2 at r₀ = 1e-3, against 1.03833e-2 for Coulomb.

**The log-gas formula** is Sandier & Serfaty, arXiv:1011.4617, Lemma 3.3: W(Λ) = −½ log(√(2πb)|η(τ)|²). I read it
myself through alphaXiv. Their Remark 1.5 gives numbers W_tri ≈ −0.2011 and W_sq ≈ −0.1958, a difference of about
0.0053, which is consistent with the 0.0052923 here.

The large-r₀ agreement is a real independent check, because the Keldysh kernel tends to 2π/(r₀k²), the 2D Coulomb (log)
kernel. Agreeing with a Dedekind-η closed form to 3e-7 is hard to get by accident.

## Material-specific energies (`fig_keldysh_materials.pdf/png`)
**HuggingFace.** No dataset on the Hub carries a 2D polarizability α₂D or χ₂D.
- Queries run: c2db, C2DB, 2d materials, 2D-materials, jarvis, monolayer, polarizability, tmd, 2dmatpedia,
  "materials project 2d", "computational 2d", dielectric, exciton, "2d material", two-dimensional, "van der waals",
  monolayers, "materials property", matbench, colabfit, alpha_2d, "screening length". The full id lists are in
  `/home/callensxavier_gmail_com/hf-data/keldysh_tmd/search.json` and in `/home/callensxavier_gmail_com/hf-data/keldysh_tmd/search2.txt` (the stdout of `hf_search2.py`).
- The only C2DB-derived dataset found is **`colabfit/JARVIS_C2DB`**:
  - revision `432aeba9e505b59d0b3605c6346ac3816c754c02`, license **CC-BY-4.0**.
  - Files: `README.md`, `ds.parquet` (sha256 8cd04683…), `co/co_0.parquet` (sha256 b3daf888…, 1.98 MB).
  - Its properties are energy and electronic band gap only (DFT-PBE, GPAW). It has 3520 configurations.
  - Citation: Haastrup et al., doi:10.1088/2053-1583/aacfc1 (as given in the dataset README); ColabFit doi:10.60732/37c26dae.
  - `HZPM/C2DBench` is an unrelated single-cell biology dataset.
- I used the HF data **only to identify the 2H monolayers**. 2H means 3 sites, a hexagonal cell, and both chalcogens at the
  same in-plane point in `positions`; 1T rows fail this test. The selected rows are:

  | material | c2db row | a (PBE) Å | a (1305.4972 Table II, expt.) Å | PBE gap eV |
  |---|---|---|---|---|
  | MoS2 | c2db_atoms_3238 | 3.184 | 3.16 | 1.580 |
  | MoSe2 | c2db_atoms_3150 | 3.320 | 3.30 | 1.321 |
  | WS2 | c2db_atoms_3223 | 3.186 | 3.16 | 1.534 |
  | WSe2 | c2db_atoms_3118 | 3.319 | 3.29 | 1.238 |

  In all four, the rows that pass the 2H test are the gapped ones and the 1T rows have gap 0. This is consistent but was
  not used as the criterion.
- **Closest real source for r₀ (Tier L).** Berkelbach, Hybertsen & Reichman, arXiv:1305.4972, Table I, DFT+RPA χ₂D:
  - Values: MoS2 6.60 Å, MoSe2 8.23 Å, WS2 6.03 Å, WSe2 7.18 Å.
  - Also MoS2 GW χ₂D = 5.0 Å, from their text.
  - Their text gives r₀ = 2πχ₂D for a freestanding sheet (after Cudazzo et al.). That gives r₀ = 41.47, 51.71, 37.89 and
    45.11 Å, and 31.42 Å for the GW value. The paper's own estimate is "ρ₀ ≈ 30–40 Å" for MoS2.
  - I read this through alphaXiv myself. C2DB itself publishes α₂D, but it is not on the Hub and was not downloaded.
- **Scope.** The sheet is in vacuum (ε₁ = ε₂ = 1). No substrate or hBN environment is modelled. The density grid
  10¹⁰–10¹³ cm⁻² is illustrative only; I make no claim about where a Wigner crystal forms. Physical energies use
  E = 14.399645 eV·Å · √n · ẽ(r₀√n), where e²/(4πε₀) = 14.3996454687 eV·Å from `scipy.constants`.

  | material | r₀ Å | n cm⁻² | r₀√n | E_tri meV | E_tri (Coulomb) meV | ratio | E_sq − E_tri meV |
  |---|---|---|---|---|---|---|---|
  | MoS2 | 41.47 | 1e11 | 0.131 | −73.77 | −89.27 | 0.826 | 0.431 |
  | MoS2 | 41.47 | 1e12 | 0.415 | −172.97 | −282.31 | 0.613 | 0.961 |
  | MoSe2 | 51.71 | 1e12 | 0.517 | −159.17 | −282.31 | 0.564 | 0.857 |
  | WS2 | 37.89 | 1e12 | 0.379 | −178.52 | −282.31 | 0.632 | 1.002 |
  | WSe2 | 45.11 | 1e12 | 0.451 | −167.74 | −282.31 | 0.594 | 0.922 |
  | MoS2 (GW χ) | 31.42 | 1e12 | 0.314 | −189.72 | −282.31 | 0.672 | 1.084 |

  The ratio E_K/E_C (Fig. 2, left) is dominated by the lattice-independent +πρr₀ term. This term comes from the
  neutralising-background convention for a non-Coulomb kernel, not from lattice structure. At r₀√n ≈ 0.4 it alone is
  about 1.3, against |E_C| ≈ 1.96. The structure-sensitive quantity is the gap E_sq − E_tri (right panel).

  The full grid (31 densities × 5 r₀ values) is in `analysis.json` → `materials`. Screening lowers the magnitude of the
  Madelung energy and the square–triangular gap compared with Coulomb at the same density. The triangular lattice stays
  lower at every point computed.

## Caveats
- **Ewald route.** The summed real-space Ewald term uses the mixture window, not the DLMF integral. DLMF 11.5.2 quadrature
  is used only to verify V: it agrees with the mixture to 2.4e-15 and with mpmath to 1.8e-16.
- **Tier X only.** Triangular < square is shown for the two lattices only, at 51 + 155 sampled r₀√n values. This is
  not a proof, and no other lattice or configuration is compared.
- **Theorem scope.** The jellium energy is not the object of the Lean theorem, nor of upstream `universal_energy_minimum`.
- **Static classical crystal.** The energies are Madelung energies only. Real TMD Wigner crystals also need kinetic,
  exchange and correlation terms, and the dielectric environment.
- **Large-r₀ precision.** At r₀ ≳ 1e5 the absolute energy has rounding error of order 1e-10. That error sits in the
  lattice-independent background term, so the gap is unaffected.
- **Independent rerun owed.** Producer ≠ verifier: an independent rerun of `cargo test` and `scan` is still owed.
