# Independent adversarial audit of the A2 paper (`papers/p2_navier_stokes_audit/`)

**VERDICT: ACCEPT_WITH_CORRECTIONS** (2 BLOCKING wording/precision corrections, 6 NONBLOCKING).

Every technical claim I re-checked **reproduced**, using my own scripts. I found:
- no soundness escape;
- no statement mismatch;
- no wrong number.

The two blocking items are one sentence each. They concern what the paper *says*, not what was checked. If both are fixed exactly as stated below, the paper may be published under the binding wording "independently rebuilt and audited".

## Audit metadata

- **Auditor.** An independent AI agent instance (producer ≠ verifier), 2026-10-26.
  - It belongs to the same AI pipeline as the producer, so "independent" means a different instance with its own scripts, not a different organisation or a human.
  - No human has reviewed this audit.
- **Scope.** The paper (`main.tex` and `main.pdf` as of 07:46 UTC), `publication_meta.json`, `ledger/`, `results/proposal2/2026-10-26/A2/` (committed at `d677df8b1a243118ab2df7318a737400421cc8f2`; `git rev-parse` confirms; 79 files in the tree), and H9 `AUDIT.md`.
- **Scratch.** `/home/callensxavier_gmail_com/proposal2/A2-audit/`. All scripts there are mine. The producer's scripts were not run.
- **Read-only access.** The producer's build copy `/home/callensxavier_gmail_com/proposal2/A2/ns-copy/` was used read-only:
  - its oleans were on `LEAN_PATH`;
  - its `setup.json` files were read for the rebuild sample;
  - `find ns-copy -newer <marker>` after my runs printed **0** files.
- **Toolchain.** `leanprover/lean4:v4.34.0-rc2`.
  - `lean` sha256 `e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550`
  - `leanchecker` sha256 `ccef1bfe9bfeecea65137d94a69033c1a89f360711f50fa3178e7ba3e696fcbe`
  - Both hashes match the paper.
- **Resources.**
  - Cores: another session's Lean pipeline occupied cores 0–3, so my jobs ran on 0, 3, 4 and 5 under `taskset`.
  - Memory: MemAvailable stayed ≥ 12.9 GB throughout.

---

## BLOCKING

**B1. §Implications (main.tex l. 324): the consequent of the conditional is followed by a non-conditional nudge.**

The current sentence:

> "... then the kernel-checked theorem `navier_stokes_breakdown_R3` is a formal proof of Fefferman's alternative (C), **and Fefferman asks for a proof of one of four statements**."

The appended clause is true as a quotation. Placed inside the consequent, though, it invites exactly the inference the paper disclaims ("so Clay is answered"), and it is the sentence most likely to be excerpted.

**Exact fix.** Delete `, and Fefferman asks for a proof of one of four statements` so that the sentence ends at "...alternative~(C)". The quotation already appears in §1 with its tag L-0001, so no information is lost.

Ledger claim P2NS-C-0005 contains the same move, stated more strongly:

> "...is a formal proof of Fefferman's alternative (C). Fefferman asks for a proof of one of four statements. Whether this settles the Clay problem is not for us to say: the Clay Institute's own process decides any prize."

**Exact fix for the ledger.** Replace those two sentences with "This is not a Clay determination: the Clay Institute's own process decides whether anything is a solution and whether any prize is due." Then rebuild the ledger evidence blob and re-run the gate.

The same remark applies to `publication_meta.json`. It does not contain the clause (checked), so no change is needed there.

**B2. "every one of its 88,400 declarations re-passes the Lean kernel" (§Implications l. 321). Abstract and §Replay make the same claim in weaker form. It is not literally true.**

`Lean.Kernel.Environment.replay` (toolchain `src/lean/Lean/Replay.lean`, the `replay` definition) skips every constant with `isUnsafe || isPartial` ("We skip unsafe constants, and also partial constants").

- The corpus has 12 such constants in the NS closure and 39 in the Euler closure: the `._unsafe_rec` compiler auxiliaries that SOUNDNESS_SCAN itself lists.
- These are counted in "53,752 / 34,648 declarations kernel-checked", but the kernel never saw them.
- Four `congr_simp` duplicates are also skipped as identical. The paper does disclose those.
- I confirmed this against the producer's script, which I read but did not run. `A2Replay.lean` l. 50 calls `env.toKernelEnv.replay newConstants`, and l. 52 prints `REPLAY OK: {newConstants.size} declarations kernel-checked`, so the count includes the skipped constants. My driver reports the skip count explicitly: `skipped by Replay: 12` (NS) and `39` (Euler).
- There is no soundness consequence. An unsafe or partial `_unsafe_rec` cannot be referenced by a safe declaration, and my closure scan finds none of them in any proof closure (see R3).
- But the sentence states something that did not happen.

**Exact fix.**
- §Implications: replace "every one of its 88,400 declarations re-passes the Lean kernel" with "all of its 88,400 stored declarations were sent to the kernel by `Lean.Replay`, which checks every safe declaration and skips, by design, the 51 compiler-generated `_unsafe_rec` auxiliaries (12 NS, 39 Euler; none in any proof closure) and the 4 identical `congr_simp` duplicates".
- §Replay: add one sentence with the same content after the table.
- Abstract: change "re-ran the Lean kernel over all 88,400 corpus declarations" to "re-ran the Lean kernel over all 88,400 corpus declarations (51 compiler-generated unsafe auxiliaries are skipped by design)".

## NONBLOCKING

**N1. leanchecker is per-module (non-transitive); say so where it is cited as evidence** (abstract, §Replay, ledger X-0006).

I demonstrated this:
- `leanchecker AuditForgeUser` returns **rc 0**. That module is honest but imports a forged module.
- `leanchecker AuditForge` returns rc 1.
- `leanchecker --fresh AuditForgeUser` returns rc 1.

The "leanchecker accepts the 8 root modules" result therefore says nothing about the other ~2,430 modules. Coverage of the closure rests on the replay. That replay now has two independent drivers that agree: the producer's and mine (R2).

**Suggested sentence:** "leanchecker without `--fresh` checks only the named module's own declarations against its imports; a forged lemma in an imported module would pass it (auditor control), so closure coverage rests on the full replay."

**N2. The second Clay erratum is not mentioned.**

The PDF's Errata contains a second item: "Eqn (10) should read: [a weak formulation]". By its content it corrects the weak form (12), not the periodicity condition (10).

The paper quotes only the first erratum and uses (10) as velocity periodicity. That is correct, but a reader who checks the PDF will see "Eqn (10) should read". Add one sentence in §1: the second erratum, nominally about (10), is by its content a correction to (12) and does not affect (C) or (D).

**N3. Non-vacuity has now been mechanised.**

Both fidelity audits left it informal (FIDELITY2 point 4, H9 caveat 3). I proved it against the *verbatim reference* definitions; see R6. Optional for the paper: cite it in §Fidelity as an auditor check ("the reference solution classes are non-empty: v = p = 0 for zero data and zero force, kernel-checked").

**N4. Replay counts versus kernel-attributed counts.**

- My replay attributes 53,750 / 34,646 constants to corpus modules.
- The producer's replay counts 53,752 / 34,648.
- The difference of 2 per closure is the `congr_simp` lemmas, which Lean attributes to the Mathlib module that first declares them.

This is consistent with SOUNDNESS_SCAN's `corpus_constants_in_env=53750/34646`. Optionally add one clause to the replay paragraph.

**N5. The paper does not say that reproducibility was sampled.** Optional: cite my rebuild sample (R5). Seven modules were rebuilt from source with the same deps and the same lake invocation, and the oleans are bit-identical, so the build is deterministic on this machine. This strengthens §Rebuild modestly.
- It is not an independent Mathlib or dependency build. The same imported oleans were used.

**N6. The "independent" wording in the title and abstract.** The disclosure paragraph already explains that every check is by agents of one pipeline, which is adequate. Consider "independently (of the corpus authors) rebuilt and audited" at the first use in the abstract.

## Wording review (item 7), other findings

- No "Clay solved", no prize or credit claim. Credit is attributed to the corpus authors (abstract, §Implications), and "not a Clay determination" is stated.
- The abstract's implication is conditional: "Conditionally on fidelity and on the soundness of Lean and Mathlib, the formal object proves Fefferman's alternative (C); that is not a Clay determination". This is acceptable.
- B1 is the only sentence that crosses the line.
- The limitations list in §5 is complete against the checklist:
  - Comparator, lean4export and nanoda not run;
  - Mathlib trusted, not replayed;
  - the formal-conjectures@8bf45ed diff is open, and so is 8937a8f versus f9e8bc5b;
  - no human referee of the proof, natural-language papers not read;
  - kernel and toolchain trusted (one kernel, two drivers);
  - fidelity judged by AI only;
  - controls do not exhaust the escape space.
- I would add one item: **`leanchecker --fresh` (re-checking the reused Mathlib subset from an empty environment) was not run.** For the forged control it took about 10 minutes for the Lean package alone; the Mathlib-sized run was estimated at hours and not attempted, by the producer or by me.

---

## Independent re-checks performed (verbatim outputs)

All logs are under `/home/callensxavier_gmail_com/proposal2/A2-audit/out/`.

### R1. `#print axioms` on my own files (item 1)

`src/AxNS.lean` = `import NavierStokes.ComparatorSolution`, `import AuditScan`, then `#print axioms` and my scan. Log `axns.log`, rc 0:
```
'NavierStokes.Comparator.navier_stokes_breakdown_R3' depends on axioms: [propext, Classical.choice, Quot.sound]
'NavierStokes.Comparator.navier_stokes_breakdown_periodic' depends on axioms: [propext, Classical.choice, Quot.sound]
```

`src/AxEuler.lean`. Log `scan_axioms.log`, rc 0:
```
'Euler.euler_breakdown_R3' depends on axioms: [propext, Classical.choice, Quot.sound]
'Euler.exists_compact_smooth_euler_singularity' depends on axioms: [propext, Classical.choice, Quot.sound]
```

The theorems proved from the **verbatim challenge statements**, in R4 (`Xfer_*.out`), give rc 0:
```
'AuditRef.navier_stokes_breakdown_R3' depends on axioms: [propext, Classical.choice, Quot.sound]
'AuditRef.navier_stokes_breakdown_periodic' depends on axioms: [propext, Classical.choice, Quot.sound]
'AuditRefE.euler_breakdown_R3' depends on axioms: [propext, Classical.choice, Quot.sound]
'AuditRefE.exists_compact_smooth_euler_singularity' depends on axioms: [propext, Classical.choice, Quot.sound]
```

### R2. leanchecker and forged controls (item 2), plus my own full-closure replay

**My forged control** is `src/AuditForge.lean`. It stores `AuditForge.two_eq_three : 2 = 3` with value `Eq.refl 2` via `addDecl` under `set_option debug.skipKernelTC true`. It also derives `False` from it.

`AuditForgeUser` is an honest module that only uses the forged constant. `AuditHonest` is a positive control. Log `forge_controls.log`:
```
'AuditForge.false_of_forge' does not depend on any axioms
'AuditForgeUser.anything' does not depend on any axioms
AuditForgeUser.anything (1 = 0) : 1 = 0            <- fresh importer, rc 0
leanchecker AuditHonest rc=0
leanchecker found a problem in AuditForge
uncaught exception: while replaying declaration 'AuditForge.two_eq_three':
(kernel) declaration type mismatch, 'AuditForge.two_eq_three' has type
  Eq 2 2
but it is expected to have type
  Eq 2 3
leanchecker AuditForge rc=1
leanchecker AuditForgeUser rc=0                    <- N1: leanchecker is per-module
leanchecker --fresh AuditForgeUser rc=1            (same kernel mismatch message)
leanchecker --fresh AuditHonest rc=0
```

**leanchecker on the roots.** The toolchain source (`src/lean/LeanChecker.lean`) shows why a root-only run is weak. Without `--fresh`, it replays only the constants stored in the named module(s) into that module's imported environment.

I ran it myself on the two solution roots (`lc_roots.sh`, log `lc_roots.log`):
```
leanchecker NavierStokes.ComparatorSolution rc=0 secs=711   (machine load average ~46 at the time; producer's run took 15 s)
leanchecker Euler.Solution rc=0 secs=34
```
Read with N1: a root-only pass covers only the root module's own declarations. The transitive check is the replay below.

**My own full-closure replay** is `src/AuditReplay.lean`, written independently of `A2Replay.lean`. It works in four steps:
1. Import the root.
2. Take every constant whose defining module has root `NavierStokes`, `Euler` or `ComparatorChallenges`.
3. Build a base environment from only the non-corpus modules of the root's module list.
4. Call `Kernel.Environment.replay`.

Log `replay_runs.log`:
```
--- control NEG: AuditForgeUser (honest root importing forged module)
AUDITREPLAY corpus_constants=3 (unsafe_or_partial, skipped by Replay: 0)
AUDITREPLAY RESULT REJECTED after 343 ms: while replaying declaration 'AuditForge.two_eq_three':
(kernel) declaration type mismatch, 'AuditForge.two_eq_three' has type
  Eq 2 2
but it is expected to have type
  Eq 2 3
rc=1
--- control POS: AuditHonest
AUDITREPLAY RESULT OK: 1 corpus constants kernel-replayed in 34 ms
rc=0
--- control POS: NavierStokes.ComparatorDefinitions
AUDITREPLAY base_constants=774999 import_ms=73076
AUDITREPLAY RESULT OK: 95 corpus constants kernel-replayed in 2208 ms
rc=0
--- NS closure 2026-10-26T08:16:37Z
AUDITREPLAY root=NavierStokes.ComparatorSolution modules_total=11191 corpus_modules=609 base_modules=10582
AUDITREPLAY corpus_constants=53750 (unsafe_or_partial, skipped by Replay: 12)
AUDITREPLAY base_constants=774999 import_ms=77804
AUDITREPLAY clashes=0
AUDITREPLAY RESULT OK: 53750 corpus constants kernel-replayed in 546996 ms
wall=680.00 maxrss_kb=16163952
rc=0
--- Euler closure 2026-10-26T08:27:57Z
AUDITREPLAY root=Euler.Solution modules_total=12411 corpus_modules=1829 base_modules=10582
AUDITREPLAY corpus_constants=34646 (unsafe_or_partial, skipped by Replay: 39)
AUDITREPLAY base_constants=774999 import_ms=97506
AUDITREPLAY clashes=0
AUDITREPLAY RESULT OK: 34646 corpus constants kernel-replayed in 1785122 ms
wall=1897.98 maxrss_kb=14935560
rc=0
```
- **Both closures replay OK** under my own driver, so the producer's replay result is independently reproduced. (It is still the same Lean kernel.)
- My max RSS was 16.2 GB for NS and 14.9 GB for Euler, against the paper's 8.1 / 9.8 GB, because my driver keeps two environments loaded. Euler wall time was 31.6 min under contention, against 15:42.
- The base env (774,999 constants) and the 95-declaration positive control equal the producer's numbers.
- The 2 `congr_simp` clashes the producer reports are attributed by Lean to their Mathlib modules (N4).
- The 12 skipped unsafe/partial constants are the basis of B2.

### R3. Environment scan of the proof closure (item 3)

`src/AuditScan.lean` is my own metaprogram. It walks the constants used by types **and values**, theorem proofs included, plus inductive↔constructor links. It flags `isUnsafe`, `isPartial`, axiom, opaque, `implemented_by` and `extern`, and attributes each constant to a corpus or non-corpus module.

NS (`axns.log`):
```
AUDITSCAN closure_total=93597 corpus_consts=31516 corpus_modules=597 noncorpus_consts=62081
AUDITSCAN closure_axioms=#[Classical.choice, Quot.sound, propext]
AUDITSCAN reaches sorryAx: false
AUDITSCAN reaches Lean.ofReduceBool: false
AUDITSCAN reaches Lean.ofReduceNat: false
AUDITSCAN reaches Lean.trustCompiler: false
AUDITSCAN flag_counts=[(noncorpus:axiom, 3), (noncorpus:extern, 58), (noncorpus:implemented_by, 6), (noncorpus:opaque, 50), (noncorpus:quot, 4)]
AUDITSCAN corpus_flagged_count=0
AUDITSCAN env_corpus_consts=53750 env_corpus_flagged=12      (all 12: ..._unsafe_rec [partial])
```

Euler (`scan_axioms.log`):
```
AUDITSCAN closure_total=94411 corpus_consts=26213 corpus_modules=1756 noncorpus_consts=68198
AUDITSCAN closure_axioms=#[Classical.choice, Quot.sound, propext]
AUDITSCAN reaches sorryAx: false   (ofReduceBool / ofReduceNat / trustCompiler: false)
AUDITSCAN flag_counts=[(noncorpus:axiom, 3), (noncorpus:extern, 58), (noncorpus:implemented_by, 6), (noncorpus:opaque, 53), (noncorpus:quot, 4)]
AUDITSCAN corpus_flagged_count=0
AUDITSCAN env_corpus_consts=34646 env_corpus_flagged=39      (all 39: ..._unsafe_rec [partial])
```

The paper's figures agree exactly:
- closure totals 93,597 / 94,411;
- corpus constants and modules 31,516 / 597 and 26,213 / 1,756;
- 58 extern and 6 `implemented_by`;
- opaques 2 core + 48 / 51 Mathlib = 50 / 53;
- 12 / 39 `_unsafe_rec`.

**Control** (`scan_ctl_run1.log`). The plants were compiled under the corpus-looking module name `NavierStokes.AuditPlant`:
```
AUDITSCAN closure_axioms=#[AuditPlant.native_lie._native.native_decide.ax_1_1, AuditPlant.planted_ax, sorryAx]
AUDITSCAN reaches sorryAx: true
AUDITSCAN corpus_flagged AuditPlant.logicallyFalse [NavierStokes.AuditPlant] [implemented_by]
AUDITSCAN corpus_flagged AuditPlant.ext [NavierStokes.AuditPlant] [extern, opaque]
AUDITSCAN corpus_flagged AuditPlant.loop [NavierStokes.AuditPlant] [opaque]
AUDITSCAN corpus_flagged AuditPlant.planted_ax [NavierStokes.AuditPlant] [axiom]
AUDITSCAN corpus_flagged AuditPlant.plainOpaque [NavierStokes.AuditPlant] [opaque]
AUDITSCAN corpus_flagged AuditPlant.native_lie._native.native_decide.ax_1_1 [NavierStokes.AuditPlant] [axiom]
AUDITSCAN corpus_flagged AuditPlant.unsafeVal [NavierStokes.AuditPlant] [unsafe]
AUDITSCAN env_corpus_flagged AuditPlant.loop._unsafe_rec [NavierStokes.AuditPlant] [partial]
positive control (AuditPlant.honest): AUDITSCAN closure_axioms=#[]  corpus_flagged_count=0
```
- A `partial def` appears to the kernel as an opaque, with its `_unsafe_rec` auxiliary marked partial. That is the same pattern as the corpus's 12 / 39, which are never in a proof closure.

### R4. Statement identity, checked in the kernel (item 4)

**Method** (`gen_identity.py`).
- The verbatim `ComparatorChallenges/NavierStokes.lean` (sha256 `0cd193b8d5cbd0266e6e2f72e68dd5abcdcf2430ebd435dd9289737e9aa7da61`) is copied with one change: `namespace NavierStokes.Comparator` becomes `namespace AuditRef`. Likewise `Euler.lean` (sha256 `b11e9baf…f1d4f7`) goes into `AuditRefE`.
- This keeps the reference's own definitions alongside the solution's in **one** environment (`import Mathlib` + `import NavierStokes.ComparatorSolution` / `Euler.Solution`).
- Only the challenge `sorry` bodies are replaced. The replacement proofs use **only** the solution theorem, with field-by-field structure conversion.
- The elaborator, and then the kernel, therefore check that every field type of every reference class is **definitionally equal** to the solution-side one.
- This is a stronger notion than comparing text, and it is what Comparator certifies.

**Result.** rc 0, with the 4 axiom lines in R1. The verbatim reference statements of (C), (D) and both Euler theorems are kernel-proved from the corpus theorems.

**Elaboration was not perturbed by importing the corpus.**
- `RefOnly_*.lean` is the same verbatim reference with `import Mathlib` only and `sorry` kept.
- I dumped every constant under `AuditRef` / `AuditRefE`: kind, level params, full type, and the value for non-theorems.
- I diffed the dumps against `Xfer_*` (`diff_dumps.py`). The normalisation rewrites only the main-module component of hygienic binder names, `_@.src.RefOnly_X.` ↔ `_@.src.Xfer_X.`. Before normalisation, the differences are exactly those binder-name tokens (`show_diff.py`).
```
NS:    ref=88 xfer=88 only_ref=[] only_xfer=[]; common=88 raw_differing=27 differing_after_hyg_normalisation=0
Euler: ref=71 xfer=75 (ignored auditor helpers 6) only_ref=[] only_xfer=[4 match_1_* auxiliaries generated by my proofs]
       common=71 raw_differing=34 differing_after_hyg_normalisation=0
```

**Mutation controls.** Each must fail, with the expected error:
```
Mut1 (energy `< E` -> `≤ E`)         rc=1  error: Application type mismatch: hs.globally_bounded_energy has type
                                            ∃ E, ∀ t ≥ 0, ∫ ‖v x t‖^2 ≤ E but is expected to have type ∃ E, ∀ t ≥ 0, ∫ ‖v x t‖^2 < E
Mut2 (drop isOnePeriodic_pressure)  rc=1  error(lean.invalidField): ... does not contain
                                            AuditRef.NavierStokesExistenceAndSmoothnessPeriodic.isOnePeriodic_pressure
Mut3 (decay (1+‖x‖)^K -> (2+‖x‖)^K) rc=1  error: Application type mismatch (decay field)
Mut4 (Euler Tstar ≤ 1 -> Tstar < 1/2) rc=1  error: Application type mismatch
```
- Mut2 is a shape change (unknown field), not a definitional-equality failure. It is weaker as a control, but it does show the periodic-pressure field is load-bearing.
- Mut3 is mathematically equivalent but not definitionally equal. The check is at the definitional level, as intended.

### R5. Rebuild reproducibility (item 5)

`rebuild_sample.sh` and `rebuild_sample2.sh` use the same `lean` invocation lake logged, with the producer's `setup.json`, writing `-o` into my scratch dir:

| module | sha256 (mine = producer's) | result | wall |
|---|---|---|---|
| NavierStokes.ComparatorDefinitions | `c29084be2ae337952dbedc07539e967874fe480b41be27dd5a6accd28bd96bca` | IDENTICAL | 20 s |
| NavierStokes.ComparatorTheorem | `beb9f692ec5a17e351fa5cc332744fd9b22311984e386ee2948dd375db23ee10` | IDENTICAL | 11 s |
| NavierStokes.ComparatorSolution | `5025fa4e63160cea4fff8dd8f8350acabd3478cdc08563f383484fd01620de76` (= paper) | IDENTICAL | 10 s |
| NavierStokes.FiveProfileMoments (one of the heaviest NS modules) | `3a017f5d50e19ebe73b0303deb937325e286e5c2703677a5f19561f95ad0e0d8` | IDENTICAL | 162 s |
| Euler.SolutionDefinitions | `32959d40ba65ffe0621d3218631e1867ca599e90aafa1c0f1f91590c1f9a3a84` | IDENTICAL | 13 s |
| Euler.Solution | `4c1131d1d7451f13977111c4116f230ac1067aa0b24e946c398cc2e71dd0102e` (= paper) | IDENTICAL | 12 s |
| Euler.LpCylinderRectangular (one of the heaviest Euler modules) | `db5cbaddb1743e337ebe40336d5676575be64b1a10f2fad909f0e9b1d9e65e89` | IDENTICAL | 160 s |

- All 7 are rc 0. The build is deterministic.
- **Scope.** Each module was rebuilt against the producer's imported oleans, so this is per-module reproducibility, not a from-scratch chain.
- Also checked:
  - `diff -rq` of the corpus source tree against `ns-copy` (excluding `.git`, `.lake`, `*.orig`) differs only in `lakefile.toml` and `lake-manifest.json`, the documented Comparator-require removal.
  - The submodule HEAD file reads `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`.

### R6. Fidelity spot-check (item 6) and non-vacuity

**The Clay PDF.** I fetched it myself with `curl` into an empty dir (`clay_fetch/`). Its sha256 is `c1b5f27b1a64705cfaf1afceea513db5deedca8a18ca56ab32e7f86445a06d0c`, which equals the paper's. I extracted its text with `pdftotext -layout`.

The quotations of (C), (D), the errata sentence and the Euler sentence in §1 are verbatim against my extraction. The second erratum is omitted (N2).

**Four rows checked against the elaborated reference (RefOnly dump), not the source text:**

1. **(6) / smoothness order.** The type of `AuditRef.InitialVelocityCondition.smooth` ends in `ContDiff ... (WithTop.some (Top.top : ENat)) u₀`. That is C^∞, not the analytic `ω = ⊤`. **Match.**
2. **(7) energy.** `globally_bounded_energy` elaborates to `∃ E, ∀ t ≥ 0, LT.lt (MeasureTheory.integral ... (measureSpaceOfInnerProductSpace ...)) E`, a strict bound under Lebesgue (inner-product Haar) measure on `EuclideanSpace ℝ (Fin 3)`. Together with the `MemLp` field this is Clay's ∫|u|² < C for all t ≥ 0. **Match.**
3. **(8)/(10) periodicity.** `AuditRef.IsOnePeriodic` elaborates to `∀ x i, f (x + EuclideanSpace.single i 1) = f x`, with e_j = `single j 1`. **Match.**
4. **Errata: periodic pressure.** `isOnePeriodic_pressure : ∀ t ≥ 0, IsOnePeriodic (p · t)` is a field of the *solution* class. **Match with the errata**, with the paper's caveat. Mut2 shows the proved statement genuinely needs this field.

Also read against the PDF: (4) and (5) decay, with `iteratedFDeriv` operator norm versus multi-index partials (equivalent up to constants), and (1) with `fderiv (v·t) x (v x t) = (v·∇)v`. **Match.** I agree with the paper's table and the (D) caveat. I found no disagreement.

**Non-vacuity, mechanised** (`src/NonVac_NS.lean`: the verbatim reference plus my theorems; log `nonvac_try2.log`, rc 0). The only warnings are the two challenge placeholders, which are not used:
```
'audit_nonvac_Rn' depends on axioms: [propext, Classical.choice, Quot.sound]        -- ∀ nu, ∃ v p, ref NSRn nu 0 0 v p
'audit_nonvac_periodic' depends on axioms: [propext, Classical.choice, Quot.sound]  -- ∀ nu, ∃ v p, ref Periodic nu 0 0 v p
'audit_zero_data_ok' depends on axioms: [propext, Classical.choice, Quot.sound]     -- zero data/force satisfy the ref data classes
```
So the reference solution classes are not empty, and the breakdown theorems are not vacuous by an unsatisfiable class.

### R7. Numbers trace (item 8)

Checked against the logs and against my own runs:

| claim in the paper | source | status |
|---|---|---|
| 2,440 oleans | `find` | ✓ |
| 609 and 1,829 `Built` lines | build logs | ✓ |
| "Build completed successfully (9371 / 10591 jobs)" | build logs | ✓ |
| 0 `Built Mathlib` lines | build logs | ✓ |
| 0 `warning:` and 0 `error:` lines in the solution builds | build logs | ✓ (the only "warning" grep hits are `Mathlib.FieldTheory.ChevalleyWarning`) |
| 2+2 `sorry` warnings in the challenge builds | build logs | ✓ |
| 3,300 / 5,109 / 33 / 12 s | `build_progress.log` | ✓ |
| olean sha256s | my `sha256sum` | ✓ |
| 53,752 / 34,648; 621,964 / 933,056 ms; 11:33 / 15:42; 8.1 / 9.8 GB; base 774,999 | replay logs | ✓ |
| leanchecker 8× rc 0, 15–17 s | `leanchecker_roots.log` | ✓ |
| 2,585 / 2,659 files; 150 / 156; 10 / 11 | `scan_*.txt` | ✓ |
| 93,597 / 94,411 etc. | my R3 | ✓ |
| gate exit 1, 4 `LEDGER_UNAUDITED_TIER_A` flags | `gate_output.txt` | ✓ |
| 26 claims (4 A / 4 L / 8 C / 10 X) | `ledger.json` | ✓ |
| commit `d677df8b…` | `git rev-parse` | ✓ |

No number was found that does not trace. B2 concerns the *gloss* "every one … re-passes the kernel", not the logged count.

## What this audit did NOT do

- Comparator, lean4export and nanoda were not run by the auditor. Their availability is as stated in the producer's notes; I did not re-verify it.
- `leanchecker --fresh` was not run on the solution roots. That run would re-check the reused Mathlib subset, roughly 775k constants: hours of compute, not attempted.
- There was no Mathlib replay, no formal-conjectures diff and no reading of the authors' papers.
- No human has refereed the proof, and no human has reviewed this audit.
