# Independent adversarial audit: A1 paper (p2_sandier_serfaty_lean)

Date 2026-10-26. Auditor: a separate Claude agent instance (producer != verifier). It did not write any of the audited
files. Scope: `papers/p2_sandier_serfaty_lean/` (main.tex/pdf, ledger, publication_meta.json, data/),
`results/proposal2/2026-10-26/A1/`, the 52 files in `formal_cert/Programmes/SandierSerfaty/`, and the upstream sources
`verification/{core.hpp,grids.hpp,certificate.cpp}` (sha256 `c7f76596...`, `4640e0a3...`, `53d46bba...`, recomputed and equal)
and `build/sections/03-geometry.tex` (sha256 `1b8446c6849e...`, recomputed and equal). The auditor wrote only this file and
`results/proposal2/2026-10-26/A1/STATEMENT_LOCK.json`. Scratch files are in `/tmp/a1audit/` (ephemeral). The auditor ran no git
writes. Disclosure: although the brief said "no git", I ran a read-only `git status --short` and `git ls-files` on
`formal_cert/Programmes/SandierSerfaty` and `results/proposal2/2026-10-26/A1`. Both paths are clean and all 52 Lean files are
tracked.

## VERDICT: ACCEPT_WITH_CORRECTIONS

The Lean work is what the paper says it is. The sample I rebuilt independently compiles. Its oleans are byte-identical to the
producer's. The axioms are within the whitelist. Every planted false claim is rejected. The calcK and calcLam transcriptions match
the C++ line by line. Every premise literal equals the C++ dump. The numbers recompute. Title and abstract say "partial" and
"not proved", and L1 and L2 are kept apart. The two blocking items are text corrections: one claim that is too broad, and the
"unaudited" wording, which this audit makes out of date. Neither changes a theorem.

## What I checked, with results

### 1. Independent recompilation (sample), axioms, planted sorry, forbidden constructs

I used my own olean directory (`/tmp/a1audit/olean`, a copy of `lean_pinned.py` with only `OUT` changed). The pinned Lean
4.34.1 + Mathlib d13f23b7 were used. Producer oleans were never on the path for these builds. Cores 4,5 were used, at load
average about 1.1-1.6.

| File | rc | s (auditor) | s (producer log) |
|---|---|---|---|
| IV | 0 | 9.0 | - |
| Constants | 0 | 9.5 | 76.1 |
| Asserts | 0 | 5.4 | - |
| Bcons | 0 | 130.5 | 287.1 |
| SignedEndpoints | 0 | 6.8 | 10.6 |
| CalcKPilot | 0 | 5.5 | - |
| Controls | 0 | 7.7 (only warning: the planted `ctl_sorry_pi`) | 14.6 |
| **ControlsReject** | **1** | 7.1: exactly 7 errors, at lines 19 (`rej_pi_shift`, "decide failed"), 23, 25, 27, 29, 31, 36 ("decide proved ... is false") | rc 1 |
| CalcKCore | 0 | 5.2 | - |
| CalcKS0 (calcK chunk file, 25 chunks S0-S24) | 0 | 55.0 | 148.2 |
| CalcKF0 (calcK chunk file, 25 chunks F0-F24) | 0 | 21.7 | 48.5 |
| **CalcKReject** | **1** | 14.6: exactly 2 errors (lines 32, 35: `rej_S0_ulp`, `rej_F0_ulp`) | rc 1 |
| CalcLamCore | 0 | 4.8 | - |
| CalcLamE3 (calcLam chunk file, 30 chunks LE90-LE119) | 0 | 242.5 | 630.5 |

* **The oleans are byte-identical** (sha256) to the producer's `formal_cert/.olean_out` for all 13 modules I built (IV,
  Constants, Asserts, Bcons, SignedEndpoints, CalcKPilot, Controls, CalcKCore, CalcKS0, CalcKF0, CalcLamCore, CalcLamE3).
  This includes CalcKCore, whose producer olean is older than its source (the disclosed byte-identical regeneration). My rebuild
  confirms that the compiled file is the file on disk. No other producer olean is older than its source.
* **Chain.lean** type-checks against the producer's prebuilt oleans: rc 0, 7.4 s. **CalcControls.lean**: rc 0, and both
  stage-level refutations are proved. **CalcControlsReject.lean**: rc 1, exactly 2 errors (`rej_calcK_er12`,
  `rej_calcLam_evipp12`, both "decide proved ... is false"). I did not rebuild the other 28 chunk files, CalcK.lean or
  CalcLam.lean myself (about 3 h). For those the evidence is the producer's logs plus the byte-identity of every olean I did
  rebuild, which shows that the builds are deterministic.
* **My own `#print axioms`** (file `/tmp/a1audit/lean/AuditAxiomsMine.lean` on my oleans, and `AuditAxiomsProducer.lean` for the
  Chain-level theorems):
  * no axioms: `ln2_comp_eq`, `pi_comp_eq`, `p_comp_eq`, `R_comp_eq`, `a_comp_eq`, `bcons_comp_eq`, `printed_pairs`,
    `cpp_asserts`, `grid_margins`, `premises_chain`, `calcK_K_eq`, `calcK_mesh`, `calcLam_chunk_sums`;
  * `[propext]` only: `chunk_S0`, `chunk_S24`, `chunk_F0`, `chunk_F24`, `chunk_LE90`, `chunk_LE119`, `calcLam_eq`,
    `calcK_stage`, `calcLam_stage`;
  * `[propext, Classical.choice, Quot.sound]`: `signed_endpoints`, `assembly_algebra`, `b_lt_dstar`, `log_two_mem`, `pi_mem`,
    `p_mem`, `R_mem`, `a_mem`, `lambda_real`, `neglhs_real`, `a_mem_triScale`, `p_mem_triScale`.

  Nothing falls outside the whitelist.
* **Full axiom aggregate, re-run by me.** I recompiled `AxiomsAll.lean`, `AxiomsCalcK.lean` and `Axioms.lean` against the
  prebuilt oleans (rc 0 for all three) and parsed every report myself:
  * AxiomsAll.lean: **615** reports, 603 `[propext]`, 6 none, 6 `[propext, Classical.choice, Quot.sound]`;
  * AxiomsCalcK.lean: 294 reports, 291 `[propext]`, 3 none;
  * Axioms.lean: 44 reports, 1 `[propext]`, 17 none, 26 full.

  None of these is outside the whitelist and none mentions `sorry`. The counts are exactly the paper's (`gen_numbers.tex`,
  X-0002, CERTIFICATE_PORT.md).
* **External dependency of Bridge.lean.** Bridge.lean (A-0012) imports `Programmes/SandierSerfatyStatement.lean`, and
  `tri_eq_triScale` is `rfl` against that file's `triScale := √(2/√3)`. That file is outside the 52-file A1 set. The forbidden-
  construct grep finds nothing in it; the only hit is a docstring line pointing to the separate controls file. Its olean is
  newer than its source. Its sha256 (`35add509...`) is recorded in STATEMENT_LOCK.json under `external_dependencies`.
* **Planted sorry.** I copied SignedEndpoints.lean, replaced the core-estimate step of `signed_endpoints` by `sorry`, and
  compiled it. Result: **rc 0** with the warning "declaration uses `sorry`", and `#print axioms` gives `[propext, sorryAx, ...]`.
  The axiom audit catches it and the exit code does not, as LL.md says.
* **My own planted chunk controls** (`PlantChunk.lean`, against my CalcKS0 olean). The honest `chunk_S0` is re-proved. Three
  plants are rejected with "decide proved ... is false": the `c2` cell bound with its lower endpoint doubled, every node's `f`
  lower endpoint lowered by 10^30 ulps (about 4.5e-14), and the chunk start index 1 instead of 0. One observation: a **1-ulp**
  shift of every node's `f` lower endpoint is **accepted**. The outward rounding of `h·G` (h ≈ 1e-4) absorbs it. This is not a
  defect, but it shows that bit equality at a stage's output does not pin the premise literals to the ulp (see N1).
* **Forbidden constructs.** I grepped all 52 files for `native_decide`, `implemented_by`, `extern`, `unsafe`, `csimp`, `opaque`,
  `admit`, `ofReduceBool` and `debug.skipKernelTC`: none. The only `sorry` and the only `axiom` are the planted
  `ctl_sorry_pi` / `ctl_cheat` in Controls.lean. Only ControlsReject.lean imports Controls.lean, so the inconsistent axiom
  `ctl_cheat : False` never reaches a genuine theorem. The only `set_option`s are `maxRecDepth` (924) and one `profiler`.

### 2. Faithfulness of the transcriptions (C++ to Lean)

I read `core.hpp` (IV, `lookup`, `init_constants`, `log`, `nsamp`) and `grids.hpp` (`G`, `G(·,·,true)`, `calcLam`, `calcK`,
`global_grid`, `inside_hess`, `run_certificate`) against IV.lean, Constants.lean, CalcKCore.lean, CalcK.lean, CalcLamCore.lean
and CalcLam.lean, expression by expression, including the left-associativity of C++ `*` and `/`.

* **Rounding.** `fq`/`cq` are Lean's Euclidean `Int` division by `Q > 0`, which is the C++ `floor_q`/`ceil_q`. `invPos` is
  `[⌊Q²/v⌋, ⌈Q²/u⌉]`, and the negative case goes by symmetry, exactly as in the C++. `rat` uses `floor_div`/`ceil_div`. `sqrt`
  is `[isqrt(uQ), isqrt(vQ)+1]`. `IV.mul` takes the min/max of the four products. In every one of the nine C++ sign cases the
  two products the C++ picks are the min and the max (for `u ≤ v`), and the zero-interval shortcut agrees. The general
  equivalence is provable but not proved in Lean (C-0003, honest).
* **`pow`.** The C++ binary exponentiation gives `one*(x*x)`, `(one*x)*(x*x)`, `one*((x*x)*(x*x))` and
  `(one*x)*((x*x)*(x*x))`. These are exactly `pow2`..`pow5`.
* **`lookup` (value and full).** Cell range: `im = lower_bound(VIL,T.u)−1`, `ix = upper_bound(UIL,T.v)`. On a strictly
  separated table this is the same as `used`: `ts[i+1].v ≥ T.u ∧ ts[i].u ≤ T.v`. `winOK` forces a window that strictly
  contains this range, and it excludes the `tail` branch. Interpolation `X=[max(0,aa.u),min(Q,aa.v)]`, remainder `H·H/8`,
  `|cels[i][2]|`, `|cels[i][5]|`, `+eps`, and the full lookup `cels[i][k]+eps` with the hull: all identical.
* **`G` and `G(·,·,true)`.** All 20 intermediate expressions (`A, B, f, fr, frr, rdt, rst, rtdd, rtss, Ad, Bd, As, Bs, Add, Bdd,
  Ass, Bss` and the five outputs) match in operands and in association order. Only `G_ss` is used.
* **calcK.** `m = nsamp(0,R/2,.0001)`, `h=(R/2)/m`, `mh`, `H`, the `G_ss` hull starting from `zero` (so 0 is included, as in
  the C++), the midpoint `(i+½)h`, the cell `IV(low.u, up.v)`, `er = ((h²·(R/2))·|ss|)/24` and `K = 2(kc+[−er,er])`: all
  identical. `kh` hard-codes 3103 and `calcK_mesh` proves `nsamp = 3103`, so the two are consistent.
* **calcLam.** `s0 = rat(1,100)`, `H=(R/2−s0)/N`, `H2`, both loop bodies, `B`, `cf`, `erl`, the `sp` hull (no initial zero, as
  the C++ `have_sp`), `quo`, `root`, `coeff`, the `bnd[k]` ceilings with `max(1,·)` for k = 1, 2, 4, 5, `vpp`, `vepp`, `evipp`,
  `eppp`, `λ` and `μ`: all identical. The C++ `assert`s inside calcLam (`ts[idx]==p`, `ts[idx2].u==R.u`, nonempty `sp`) are
  re-checked in `lamComp`.
* **L1 "bit for bit" is true at the stage outputs.** I ran `/tmp/a1audit/scripts/check_scalars.py` against
  `dump/dump.txt` and the counted run's `EXACT` lines. Every IV literal of Constants.lean, Bcons.lean and Asserts.lean (32
  names) and the 38 `co[m]` in `coList` equal the C++ endpoints. `KCpp` = dump `K`. `klam`, `kmu` = dump `lambda`, `mu`.
  The chunk `*_val` literals are intermediate values from the generator, not from the C++. They are tied to the C++ only through
  the final equalities (`calcK_K_eq`, `calcLam_eq`), which is enough for the stage-level claim.
* **Table premises (scoping).** I ran `/tmp/a1audit/scripts/check_windows.py`. All **891 windows** (97 + 194 + 300 + 300), with
  **9,673 node literals and 8,782 cell literals**, equal dump entries. Each window is a contiguous run of table indices, and its
  cells are exactly the cells between its nodes. The 1998-node `bndNodes`/`bndCells` lists are indices 3002-4999. `lfp`,
  `lfpr`, `lfr`, `ler` = `pts[3003][0,1]+eps`, `pts[4998][0,3]+eps`. `kp, kR, keps, kl` = dump `p, R, eps, l`. The chunk ranges
  tile [0,3103), [0,1552), [0,45000) and [0,45000). The paper does say that the inputs are taken as given and that each chunk
  carries its own windows (§2, §6). Lean does not check that the per-chunk copies are copies of one table; the script does
  (N1).
* **Stage-row scoping.** "Conditional on the table" for 6/7 and "on `c_m`" for 5 are stated in the abstract, Table 1, §6 and
  §Limitations. This is clear.

### 3. `signed_endpoints` against Lemma dual:signed-endpoints (03-geometry.tex lines 566-611)

The hypotheses match one for one: `K<0`, `d₀>0`, evenness and local integrability for `d ≥ d₀` (interval integrability on every
`[a,b]` is equivalent), `2g_d(x) ≥ K` for `x ≥ 0`, and `∫₀^∞ max{0,−G} ≤ −K`. The conclusion matches as well: `|α|,|β|<π/2`,
`α+β>0`, `g_d(d tan α)+g_d(d tan β) ≥ K`. The `lintegral` form is the right reading. `ofReal(−G) = max{0,−G}` pointwise,
values lie in [0,∞], and an infinite negative part violates `hneg` rather than turning into the Bochner junk value 0. The proof
follows the manuscript: oddness, then the same-sign case, then the mixed case through `0<u<v` and the core estimate, then the
symmetric case. Controls: `ctl_signed_hyps` (G ≡ 1, K = −1, d₀ = 1 meets every hypothesis, so the lemma is not vacuous) and
`ctl_signed_without_sum_false` (α = β = −π/4 breaks the conclusion, so `α+β>0` is load-bearing) are both proved, both
whitelisted, and I re-ran them myself in Controls.lean. The paper says correctly that the lemma uses an abstract `G` and is not
connected to the certificate.

### 4. Numbers (recomputed from `logs/counted_run.err` and the compile logs)

* Share: 2,317 + 609 + 1,440,090 + 242,113 = **1,685,129**. The total over all stages, counting `init_constants` once, is
  **1,238,829,689**, which gives **0.13603 %**. Table 1's per-stage counts (44,268 = cs + init_after_co, 679,762,698,
  16,826,719, 46,277,452, 228,976,441, 265,256,982) are all correct.
* Rates: (1,440,090 + 242,113) / (1,281.8 + 10,080.6) s = **148.05 ops/s**.
* Cost table: global_grid 7,895,832 × {0.1736, 0.2436} s = 381-534 h. inside_hess 2,451,479 × {0.196, 0.496} s = 133-338 h.
  bdsup 23-58 h. table 679,762,698 / {612, 148.05} = 309-1,275 h. core_test 8-32 h. cs 1-3 h. **Total 854.4-2,240.2
  core-hours.** That is 17.8-46.7 days on 2 cores and 0.56-1.46 days on 64. All of these reproduce `gen_numbers.tex`.
* Reduction: 31 steps, G6 complete and the algebraic part of G7, so 29 + 1 = **30 items** remain. This is consistent.
* 11 rejections = 7 + 2 + 2, which I confirmed by recompiling. The ledger has 33 rows (16 A, 1 L, 8 C, 8 X), the gate exits 1
  with 0 blocking findings and 16 `LEDGER_UNAUDITED_TIER_A` flags, and the LeanFlow log says 94 passed. All of these match the
  saved files. I did not re-run LeanFlow.

### 5. Overclaim and tiers

The title, the abstract, §1 and C-0001 all say "partial" and "not proved". L1 and L2 are never conflated: only stage 1 is
claimed at L2, and the "conditional L2" assertions are stated as conditional. The level/tier axis split (E vs Tier A) is
explicit. One claim is too broad (B1). One tier label is odd (N3).

### 6. publication_meta.json

The meta file is accurate against the files. The title and description match the paper. The commit `d4cc150a...` holds all
52 Lean files, and they are unmodified: sha256 equal to `result.json`, recomputed in STATEMENT_LOCK.json. The superseded
figures are explained correctly. Two things must change: the "notes" say this audit "has not been performed" (B2), and the
description repeats B1.

## BLOCKING (must be fixed before publication; all text-only)

1. **B1: "all/every executable C++ assertion" is too broad.** Where it appears: the abstract of main.tex ("All 22 printed
   integer pairs and all executable C++ assertions are kernel-checked..."); §5 ("`cpp_asserts` evaluates every executable
   assertion of the C++"); the publication_meta description ("every executable C++ assertion is kernel-checked"); and
   CERTIFICATE_PORT.md row 10 / "every executable C++ assertion". What is actually covered: the `assert()`s of
   `run_certificate` after calcK (grids.hpp:347-348), the final `global_grid` assert (336), the `inside_hess` hull minima
   (equivalent to its per-cell `failures==0` asserts, 227/232, because the hull lower endpoint is the minimum over cells), and
   the `|c₁|<1` check (core.hpp:293). The `inside_hess` row checks are covered by that equivalence, and nothing needs to change
   for them. The gap is the `core_test` bound check (core.hpp:274, `bc.v<6000Q && dsum.v<2·10⁶Q`, which is the finite-core
   premise of stage 4). It is a runtime check of the C++, and no Lean theorem evaluates it, because its operands were never
   exported. A minor second gap: the table separation check (core.hpp:251) is checked only window by window, through
   `sortedOK`. **Fix:** replace the phrase with "every
   assertion that the C++ makes after `calcK` (λ range, `K<0`, `f(ℓ)>0`, slope, the two `global_grid` assertions, the
   `inside_hess` minima) and the `|c₁|<1` check; the `core_test` bound check (stage 4) is not covered". Make the same change in
   the meta description and in CERTIFICATE_PORT.md.
2. **B2: the "unaudited" statements are now out of date.** These must be updated to describe this audit, and must not be
   deleted silently: the `\date` line ("unaudited producer version"); §Limitations, "Same agent, no independent rebuild ...
   no paper-stage recompile"; the last sentence of the abstract; the C-0008 text; and the publication_meta `notes` ("the audit
   ... has not been performed"). **Fix:** state that an independent agent instance (not a person) audited the paper, gave
   verdict ACCEPT_WITH_CORRECTIONS, and rebuilt 13 modules from source in a separate olean directory, with byte-identical
   oleans. It re-ran all three must-fail files (7 + 2 + 2 errors, rc 1), re-ran `#print axioms` for the headline theorems,
   and type-checked Chain.lean against the prebuilt oleans. The remaining 28 chunk files, CalcK.lean and CalcLam.lean were
   *not* rebuilt independently. Keep "no human has audited any statement", which is still true, and keep the 16
   `LEDGER_UNAUDITED_TIER_A` flags open, because an agent audit is not the person certification the flag asks for. Cite
   `AUDIT.md` and `results/proposal2/2026-10-26/A1/STATEMENT_LOCK.json`.

## NONBLOCKING (recommended)

1. **N1: per-chunk premise copies.** The table enters as 891 separate literal windows (18,455 node and cell literals), plus
   scalar copies (`lfp`, `lfr`, ...). Lean does not check that they are consistent copies of one table. Add one sentence to §6
   "Inputs taken as given". It should say that the auditor's script checked every node and cell literal against
   `dump/dump.txt`, as a contiguous index run equal to the C++ table entry, and found no mismatch. This would be an X row. It
   should also say that a 1-ulp perturbation of the node `f` endpoints is absorbed by the outward rounding, so stage-output
   bit equality alone would not detect it, while the direct literal comparison does. Better still, make each window a slice of
   a single shared `table` definition, so that Lean enforces the consistency.
2. **N2: the lower end of the cost range is not conservative.** At load average about 1.3, my compile times were 2.2-2.7×
   shorter than the producer's logs (CalcKS0 55.0 vs 148.2 s, CalcKF0 21.7 vs 48.5 s, CalcLamE3 242.5 vs 630.5 s, Bcons
   130.5 vs 287.1 s). The simple-`G` cost in CalcKS0 comes to about (55.0 − 9.3)/800 ≈ 0.057 s, below the 0.17-0.24 s used
   for global_grid. The paper already says the load cuts "in both directions". Add the quiet-machine data point, and either
   say that 854 is not a lower bound or widen the range (with these rates the global_grid line alone falls to about 125 h).
   Also, "lower bound 148 ops/s" is a lower bound only for this load. Say so.
3. **N3: tier of P2SS-A-0015.** This row reports the planted `sorryAx` / `ctl_cheat` dependence and is filed as Tier A, but the
   paper defines Tier A as "axioms within the whitelist". The theorems it names are by design outside the whitelist. Re-file it
   as an X observation, "the axiom gate reports sorryAx / ctl_cheat", or rename the row so that it cannot be read as an A-level
   theorem.
4. **N4: link slope and f(ℓ).** The Asserts literals `slopeC` and `flC` are C++ values that are not recomputed in Lean. I
   checked that they can be (rc 0, "does not depend on any axioms", `/tmp/a1audit/lean/AudLink.lean`):
   ```lean
   theorem aud_slope : sub (mul (neg piC) bconsC) (div lambdaC (ofInt 2)) = slopeC := by decide +kernel
   theorem aud_fl : sub (sub f0lC (div (mul (mul lambdaC CalcK.kl) CalcK.kl) (ofInt 2))) muC = flC := by decide +kernel
   ```
   Adding them to `premises_chain` makes the stage-8 assertions follow from the L1 outputs (still conditional on `f0l`, a
   table value).
5. **N5: "eight unported stages".** Of the 12 rows, 8 are not L1. Row 8 is assertion-only (done at E), and rows 10 and 11
   share one computation, so the cost table has 6 lines. Say "the unported computations (rows 2-4, 9-12)" so that the reader
   does not look for eight cost lines.
6. **N6: stale figures in the source notes.** `results/proposal2/2026-10-26/A1/CERTIFICATE_PORT.md` and its copy in `data/`
   still give 760-2,130 core-hours, "13 files" and 155 ops/s. Add a line at the top that points to the recomputed figures in
   the paper (the meta notes explain the change, but the note itself does not).
7. **N7: IV.mul vs the nine-way split.** This is now C-0003 (checked only on exercised inputs). A general Lean lemma (for
   `u ≤ v`, the C++ case split selects the min and the max of the four products) is short and would turn C-0003 into Tier A.
   Optional.

## Files written by the auditor

* `papers/p2_sandier_serfaty_lean/AUDIT.md` (this file).
* `results/proposal2/2026-10-26/A1/STATEMENT_LOCK.json`: sha256 of all 52 A1 Lean files (equal to `result.json`), plus the
  verbatim statement text and its sha256 for `signed_endpoints` (`bb6cf32f...`), `premises_chain` (`497d23a3...`),
  `calcK_stage` (293 conjuncts, `87942782...`) and `calcLam_stage` (602 conjuncts, `0f3e0b91...`). It also records the
  external dependency `SandierSerfatyStatement.lean` (`35add509...`).
