# A1a: porting the triangular-minimality finite certificate into Lean

> **Superseded figures (revision after the independent AI audit, 2026-10-26).** This note is the producer's original; several figures
> below are stale. The recomputed ones are in the paper (`papers/p2_sandier_serfaty_lean/main.tex`, `data/cost_numbers.json`):
> 854-2,240 core-hours (not 760-2,130), and that range is **not conservative** (the auditor measured 2.2-2.7x faster compiles on a
> quiet machine); calcK chunk files 1251.3 s over 12 files (not 13); throughput lower bound 148 ops/s (not 155), valid only at the
> measured load. "Producer = verifier" below is out of date: a separate AI agent audited the work (`papers/p2_sandier_serfaty_lean/AUDIT.md`,
> `results/proposal2/2026-10-26/A1/STATEMENT_LOCK.json`); no human audit. The scope of the E-level assertions is as stated in row 8/10/11/12
> below (not "every executable assertion"): `core_test` at `core.hpp:274` is not covered.

Date 2026-10-26. Proposal 2, item A1a (preregistration `results/proposal2/2026-10-26/preregistration.json`, priors: pilot stages 0.6,
all stages 0.2, A1 complete 0.02). Subject: the finite certificate of the openai/math manuscript "Triangular minimality for planar
Coulomb renormalized energy" (2026-09-23; AI-generated, not peer reviewed), `verification/{certificate.cpp, core.hpp, grids.hpp}`,
SHA-256 `53d46bba...`, `c7f76596...`, `4640e0a3...` (equal to `data/certificate-record.txt`; the corpus was never edited).

**Bottom line.** The Sandier-Serfaty conjecture is **not** formally proved by this work, and nothing here says it is. What is
kernel-checked is listed below, stage by stage, with the level at which it is checked.

## Levels

* **L1 (kernel re-execution).** A Lean transcription of the stage's C++ interval computation, run by the Lean kernel
  (`decide +kernel`, no `native_decide`), gives bit for bit the integer endpoints that the C++ binary printed (the dump driver
  `cpp/dump_driver.cpp`, compiled against the unmodified corpus headers). Inputs from earlier stages enter as explicit premises
  (C++ endpoints). L1 removes the compiler, Boost, OpenMP and hardware from the trust base of that stage (P1 REDUCTION_AUDIT §6.2).
  It leaves the fidelity of the transcription (C++ to Lean) and does not by itself relate the numbers to the manuscript's real
  quantities (§6.1).
* **L2 (real statement).** A Lean theorem that a real number (`log 2`, `π`, `√(2/√3)/2`, ...) lies in the interval, from Mathlib
  plus kernel-decided rational comparisons, or the real meaning of an assertion conditional on its operands lying in their intervals.
* **A (arithmetic).** A kernel-checked statement about given integers only (the LeanFlow tier A of P1).

Fixed-point semantics: `IV.lean` transcribes `IV` (`[u/Q, v/Q]`, `Q = 2^144`), with soundness lemmas over ℝ for `+`, `−`, `×`, `inv`,
`/`, `rat`, `ofInt`, `hull` (`add_sound`, `mul_sound`, `inv_sound`, ...). `IV.mul` uses min/max of the four endpoint products,
which yields the same endpoints as the C++ nine-case split; the transcription was checked against the C++ on every ported stage.

## Stage map (what each stage checks, with which constants, on which mesh) and status

Op counts: per-stage counts of IV `*`, `inv`, `+` from an instrumented copy of the sources (`cpp/patch_counters.py`: counters and
exact-endpoint prints only; its log reproduces all 22 record pairs), single thread, `logs/counted_run.err`.

| # | C++ stage | What it certifies (manuscript) | Constants / mesh | IV ops (mul / inv / add) | Lean status |
|---|---|---|---|---|---|
| 1 | `init_constants` | (comp:logarithm) `log 2`, (comp:pi) `π` enclosures; `p = √(2/√3)/2`, `R₀ = 2p/√3`, `a = 2p` | 200-term `atanh(1/3)` + `[−1,1]/Q`; Machin, 150 terms per arctan + `[−2,2]/Q` | 1311 / 1006 / 505 | **L1 + L2, complete.** `ln2_comp_eq`, `pi_comp_eq`, `p_comp_eq`, `R_comp_eq`, `a_comp_eq`; `log_two_mem`, `pi_mem`, `p_mem`, `R_mem`, `a_mem` |
| 2 | `cs()` + `init_after_co` | lattice coefficients `c_m`, `m ≤ 38` (comp:coefficient-summand), half-square doubling, tail (tail:coefficient-square); `\|c₁\| < 1`; edge/extension coefficients | squares `n ≤ 256` (`m = 1`), `n ≤ 48` (`m ≥ 2`): 131,841 + 4,753 lattice points, exact integer sums grouped by norm | 1217 / 152 / 62303 (+ big-integer lattice sums, not IV) | `\|c₁\| < 1` on the exact endpoints: **A** (`cpp_asserts`). Computation not ported |
| 3 | `table(24000)` | `f̃₀, ẽ` jets at 6826 nodes and cell enclosures (comp:initial-integrals), (comp:propagation), (comp:midpoint), (comp:cell-integrals), (comp:jet-ode) | 8000 nodes/unit on seg 0, 24000/unit elsewhere; serial propagation, 39 modes | 650,719,043 / 29,043,655 / 522,428,086; 42,014 IV logs | not ported (premise of stages 6-10) |
| 4 | `core_test` | finite-core premise (tail:finite-core-premise): `‖B̃₁‖_{2,t} < 6000`, `Σ(k+1)³‖D̃‖_{3,t} < 2·10⁶` | mesh `.00022` on `[b, l]` | 16,355,419 / 471,300 / 13,335,274; 2233 logs | not ported |
| 5 | `bcons`, `eps` | `B(l)` enclosure, `ε = 10⁻¹¹` truncation allowance | | 407 / 202 / 244 | value used as premise; printed pair checked (**A**) |
| 6 | `calcLam` | `λ, μ` (cal:constants) via (comp:lambda-origin), (comp:lambda-derivatives) | two 45,000-step midpoint sums, `s₀ = .01` | 1,170,066 / 270,024 / 1,272,010; 90,000 lookups | **L1** (see below) |
| 7 | `calcK` | `K = 2∫₀^{x₀} G(p,s) ds` (comp:K-quadrature) | midpoint `h = (R/2)/3103`; `G_ss` hull on `(R/2)/1552` | 203,308 / 38,805 / 122,155; 3103 `G` + 1552 `G(·,·,true)` | **L1, complete** (see below) |
| 8 | asserts after `calcK` | (comp:tail-signs): `−6.731 < λ < −6.729`, `K < 0`, `f(l) > 0`, `−πB(l) − λ/2 > 0` | | — | **A** on the exact endpoints (`cpp_asserts`, `rat_consts_eq`), conditional **L2** (`lambda_real`, `K_real`, `fl_real`, `slope_real`) |
| 9 | `bdsup` | (comp:global-derivative-bounds) `L₁..L₄` on `[b, .697] × [0, .65]` | 519 × 813 cells, `H = .0008` | 39,948,239 / 6,329,213 / 52,815,498; 421,947 `G(·,·,true)` | printed hulls checked (**A**, `printed_pairs`); computation not ported |
| 10 | `global_grid` (outer) | (comp:outer-assertion) `m_* − E₀ − E_I > 0` on `𝒟 ∖ int 𝒟₀` | 2186 × 3612 nodes, steps `.00019`, `.00018` | 178,370,424 / 50,606,017 / 133,662,969 (both parts); 7,895,832 `G` | final assertion on exact endpoints **A** (`cpp_asserts`: `(gmin − factor).u > 0`; `grid_margins`: `≥ 1.20e-5`), conditional **L2** (`gmf_real`); computation not ported |
| 11 | `global_grid` (negative part) | (comp:negative-assertion) `N_* + K + .65(S_h L₂/4 + D_h L₁/2) < 0` | same mesh | (in 10) | final assertion **A** (`(drneg + er_drop + K).v < 0`; `≤ −4.585e-4`), conditional **L2** (`neglhs_real`); computation not ported |
| 12 | `inside_hess` | (comp:hessian-assertions) on `𝒟₀` | 601 × 4079 cells, steps `.00004`, `.00008` | 228,480,114 / 36,776,868 / 124,482,693; 2,451,479 `G(·,·,true)` | hull minima `g_dd, g_xx, det > 0` on the exact endpoints **A**; computation not ported |
| P | `coarse_list` | the 22 printed pairs of `certificate-record.txt` | display scale `10⁻⁷` | — | **A**: `printed_pairs` shows each saved pair is `(⌊10⁷u/Q⌋, ⌈10⁷v/Q⌉)` of the exact interval |

Infrastructure transcribed and exercised by the ported stages: `IV` (`+ − × inv / rat sqrt hull abs`), the value lookup
(linear interpolation `+ H²/8 |f̃₀''|`, `+ ε`) and the full lookup (cell hulls `+ ε`), `G(d,s)`, `G(d,s,true)` (all five
components), `pow`.

## Results

Denominator: the 12 rows above. Lean sources: `formal_cert/Programmes/SandierSerfaty/` (new files only); compile logs
`logs/compile_*.json` (pinned Lean 4.34.1 + Mathlib d13f23b7 via `scripts/certified_numerics/lean_pinned.py`, cores 4,5);
sha256 of every source in `result.json`.

* **L1 complete: 4/12** — init_constants, bcons, calcLam, calcK. calcLam and calcK are L1 **conditional on the table enclosures**
  (stage 3, not ported) and on `l`; bcons on the `co[m]` premises (stage 2, not ported).
* **L2 complete: 1/12** — init_constants (`log 2`, `π`, `p`, `R₀`, `a` as real numbers; `a`, `p` also stated over the
  statement file's `ProgSandierSerfaty.triScale` in `Bridge.lean`).
* **A on exact endpoints**: rows 8, 10, 11, 12 (every assertion that the C++ makes after `calcK`: λ range, `K<0`, `f(ℓ)>0`, slope, the two `global_grid` assertions, the `inside_hess` minima; the `core_test` bound check at `core.hpp:274` is NOT covered, and the table separation check at `core.hpp:251` is checked only window by window), `|c₁| < 1`, and the 22 printed pairs (row P), plus
  conditional L2 meaning of the row-8/10/11 assertions.
* **Not ported: table, core_test, cs, bdsup, and the computations of global_grid / inside_hess.**
* Share of the C++ work re-executed in the kernel: 1,685,129 of 1,238,829,689 IV mul+inv (**0.136 %**).

### Details of the ported stages

* `Constants.lean` (76 s): `ln2_comp_eq`..`a_comp_eq` (L1), `log_two_mem` (Mathlib `abs_log_sub_add_sum_range_le`, 160 terms),
  `pi_mem` (Machin `four_mul_arctan_inv_5_sub_arctan_inv_239` + `Real.hasSum_arctan` with a geometric tail bound, 150 terms each),
  `p_mem`, `R_mem`, `a_mem` (fourth powers `1/12`, `4/27`, `4/3`).
* `Bcons.lean` (287 s): `bcons_comp_eq` re-executes the C++ interval `log` (range reduction + 200-term atanh), `pow`, `comb`, Horner,
  the 38 edge values `VR_m` of `init_after_co`, and `bcons = −log R + (π/2)R² + ΣVR_m + eps`.
* **calcK** (`CalcKCore`, `CalcKS0..3`, `CalcKF0..7`, `CalcK`; 1251 s of process time over 13 files): 97 chunks of the midpoint sum
  (indices `32c..32c+31`, c < 97, last chunk 31 long) and 194 chunks of the `G_ss` hull (indices `8c..8c+7`, c < 194); `calcK_mesh`
  (`nsamp` gives 3103 and 1552) and `calcK_K_eq` (`K = 2(kc + [−er, er])`, `er = h²(R/2)|ss|/24`, equals the C++ `K`). Every lookup
  re-checks in Lean that its window is sorted and contains the full C++ cell range for the `T` computed in Lean.
* **calcLam** (`CalcLamCore`, `CalcLamF0..9`, `CalcLamE0..9`, `CalcLam`; 10,070 s over 21 files): 300 + 300 chunks of 150 midpoint
  steps (indices `150c..150c+149`); `calcLam_chunk_sums`; `calcLam_eq`: the scalar part (`B`, `cf`, `sp` hull over the cells meeting
  `[p, √(p²+s₀²)]`, `quo`, `root`, `coeff`, derivative bounds `C, C′, C_e0, C_e1` over the 1997 cells meeting `[p, R]`, both
  midpoint allowances) gives exactly the C++ `λ, μ`.
* `Chain.lean`: `premises_chain` (kernel): calcK's premises `kp, kR, klam, kmu` equal Constants' `pC, RC` and the values
  recomputed by calcLam; Asserts' `lambdaC, muC, KC, bconC` equal the calcLam/calcK/bcons outputs; `eps = [−rat(1e−11).v, rat(1e−11).v]`.
  `calcK_stage`, `calcLam_stage`: one statement per stage (conjunction of all chunk theorems and the final theorem). The chunk
  ranges tile the index sets by construction of the generator (`scripts/gen_calck.py`, `gen_calclam.py`); Lean does not check the
  tiling, the ranges above let a reader check it from the statement.
* LeanFlow (`leanflow/`, worktree commit `06084ef`, tactic `decide_kernel`): the 12 assertions (λ range, K<0, f(l)>0, slope>0,
  gmin−factor ≥ 1.2e−5, neg_lhs ≤ −4.585e−4, three Hessian minima, |c₁|<1) over the exact endpoints → `ok`, tier A, axioms `[]`;
  the planted copy (`≥ 1.21e−5`) → `rejected`, `false-statement`, failing exactly `cert_5`.

### Axioms (verbatim excerpts; full lists in `logs/compile_Axioms.json`, `compile_AxiomsCalcK.json`, `compile_AxiomsAll.json`)

```
'ProgSandierSerfaty.Cert.ln2_comp_eq' does not depend on any axioms
'ProgSandierSerfaty.Cert.pi_mem' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgSandierSerfaty.Cert.log_two_mem' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgSandierSerfaty.Cert.p_mem' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgSandierSerfaty.Cert.printed_pairs' does not depend on any axioms
'ProgSandierSerfaty.Cert.cpp_asserts' does not depend on any axioms
'ProgSandierSerfaty.Cert.bcons_comp_eq' does not depend on any axioms
'ProgSandierSerfaty.Cert.CalcK.calcK_K_eq' does not depend on any axioms
'ProgSandierSerfaty.Cert.CalcK.calcLam_eq' depends on axioms: [propext]
'ProgSandierSerfaty.Cert.Chain.premises_chain' does not depend on any axioms
'ProgSandierSerfaty.Cert.Chain.calcK_stage' depends on axioms: [propext]
'ProgSandierSerfaty.Cert.Chain.calcLam_stage' depends on axioms: [propext]
'ProgSandierSerfaty.Cert.a_mem_triScale' depends on axioms: [propext, Classical.choice, Quot.sound]
```

Audit totals: `Axioms.lean` 44 reports, `AxiomsCalcK.lean` 294, `AxiomsAll.lean` 615; non-whitelisted: none. No genuine log contains a
`sorry` warning (only `Controls.lean`, where `ctl_sorry_pi` is planted).

### Negative controls (planted false stages must be rejected by the kernel)

| Control | Kind | Result |
|---|---|---|
| ln2 with 199 terms; π without `[−2,2]/Q` slack | L1 perturbed constant | `ctl_*_ne` proved; `rej_ln2_199` rejected ("proved that the proposition ... is false") |
| π lower endpoint + 2^100 ulps | L2 | `ctl_pi_shift_false` proved; `rej_pi_shift` rejected (decide could not reduce to true; falsity proved by the honest control) |
| printed pair `(121,162)`; `gmin−factor ≥ 1.21e−5`; `drneg + 2·er_drop + K < 0`; `det ≥ 0.0087` | A | honest refutations proved; all four rejected |
| calcK pilot with `H²/8 → H²/4` in `lookup` | L1 | `ctl_G_eight_to_four` proved; rejected |
| calcK chunk values ±1 ulp (S0, F0) | L1 | `ctl_*_ulp_ne` proved; both rejected (`CalcKReject.lean`, recompiled against the final oleans) |
| **calcK stage with `/24 → /12` in `er`** | L1 stage | `ctl_calcK_er12_ne` proved; `rej_calcK_er12` rejected |
| **calcLam stage with `/24 → /12` in the Facc allowance** | L1 stage | `ctl_calcLam_evipp12_ne` proved; `rej_calcLam_evipp12` rejected |
| `sorry` / custom axiom proofs of the shifted-π claim | axiom gate | `#print axioms` shows `sorryAx`, resp. `ProgSandierSerfaty.Cert.Controls.ctl_cheat` |

Must-fail files: `ControlsReject.lean`, `CalcKReject.lean`, `CalcControlsReject.lean` (rc 1, every error is a rejected planted claim).

## Cost of the remaining stages (L1 only), with evidence

Measured kernel rates (process wall time on cores 4,5 with the machine at load average 12-16 from other sessions, so treat as ranges):

| Unit | Measured | Source |
|---|---|---|
| simple `G(d,s)` incl. lookup | 0.09-0.21 s | calcK trial chunk (32 G in 2.95 s) / calcK S files (3103 G in ~640 s) |
| value lookup (calcLam step) | 0.11 s | 90,000 steps in ~9,700 s |
| `G(d,s,true)` | 0.31-0.52 s | calcK F files (1552 in ~490 s) / trial (8 in 4.1 s) |
| IV mul+inv | 155-610 ops/s | calcK+calcLam (1.68e6 ops in ~10,900 s) / `bench/BenchIV*.lean` (3k-12k ops) |
| one theorem's memory | +0.3 GB at 3k ops, +4.9 GB at 48k ops (3.3 GB import baseline) | `logs/bench_results.json` |

Projection (counts from the counted run × measured rates):

| Stage | Work | Projected core-hours |
|---|---|---|
| global_grid | 7,895,832 `G` | 197-461 |
| inside_hess | 2,451,479 `G(·,·,true)` | 211-354 |
| bdsup | 421,947 `G(·,·,true)` | 36-61 |
| table | 6.80e8 mul+inv (+5.2e8 add, 42,014 logs), serial: needs per-node state witnesses (~41 IVs × 6826 nodes) | 310-1220 |
| core_test | 1.68e7 mul+inv | 8-30 |
| cs | 136,594 lattice points, exact grouping by norm | ~1-3 (estimate; mode-0 arithmetic measured at 6.8 ms/point, `bench/BenchCs.lean`) |
| **total** | | **~760-2130 core-hours** (≈ 16-44 days on 2 cores, ≈ 0.5-1.4 days on 64 cores), ≤ 1e4 ops per theorem to stay near 4 GB per process |

Even when finished, L1 is not a proof. The larger gap is **L2**: Lean definitions of `f₀` and `e` (Section 4 radial data, the
lattice coefficients `c_m` as lattice sums with the Section 5 tail bounds), and soundness proofs for the jet arithmetic, the ODE
propagation of `table`, the midpoint/interpolation remainders (Mathlib has a trapezoidal-rule error bound, no midpoint rule), the
lookup, and the grid arguments of Theorem `comp:scalar`; then the bridge from `global_grid`'s assertions to the hypotheses of
`signed_endpoints` (REDUCTION_LEMMA.md), and the whole of Sections 2-5. That is a multi-month formalization project.

## Caveats

* L1 fidelity was checked only by bit-equality with the C++ outputs of the same stage; the table data enter as premises.
* Producer = verifier in this run (same agent wrote the generators and the Lean files); no independent rebuild from scratch yet.
  `CalcKCore.lean` was rewritten byte-identically by the generator after its olean was built (sha256 equal to a fresh regeneration).
* The counted copy (`cpp/patch_counters.py`) added counters and endpoint prints only; the global_grid/inside_hess exact endpoints come
  from it (its log reproduces all 22 record pairs); all other endpoints come from the dump driver over the unmodified headers.
