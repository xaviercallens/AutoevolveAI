# Numerica: product positioning and roadmap (proposal, 2026-11-14)

Status: a proposal by the AI assistant for the owner. Nothing here is started. Evidence labels follow the Elenchus
tiers: **[A]** kernel-checked, **[C]** computed and audited, **[L]** literature or search snippet, **[X]** not verified
or an assumption. Every number about our own work is traceable to a Zenodo record or a file named below.

## 0. In five lines

1. **Product:** Numerica is the evolution of rusty-SUNDIALS from "a Rust port of SUNDIALS" into **numerical solvers
   that ship with a checkable argument for their answer**: fast solve, rigorous enclosure, and an audit trail, each
   labelled with how strongly it is established.
2. **Wedge:** not speed. Our own results show the gap is *trust in the number*: a standard solver passed its tolerance
   test while its true error was 169 times the relative tolerance (Robertson, component y2).
3. **Honest starting point:** today's rusty-SUNDIALS README claims more than the repository supports (section 2). The
   first phase of the roadmap is truth-in-labelling, before any new feature.
4. **Order of work:** labels and provenance, then diagnostics, then a native enclosure engine, then Lean (Tier A) for one
   theorem. Roughly 24 weeks to a first credible Tier-A release, with a kill criterion at each step.
5. **Cut from v1:** the E8 quantiser, topology bridge, PDE blow-up monitors and wavelet preconditioners in the
   brainstorm. They are different products, and several rest on artifacts I could not find (section 3).

## 1. What our own results say (the evidence base)

| Result | Where | Tier | Why it matters for Numerica |
|---|---|---|---|
| Validated enclosure of Robertson's problem to t = 4000, in Python/Sage with Arb balls, 8.31 core-hours; independent re-derivation only at t = 1, 10, 40 | Zenodo 10.5281/zenodo.24216837 | C | Proves the method works and is slow; the lemma is proved in prose, not Lean |
| True error of the Rust `cvode` crate against that enclosure: y2 error up to 169 times rtol·\|y2\|; y1, y3 up to 486 times at rtol 1e-10 (a non-preregistered run); the tolerance test passes only because atol dominates | same record | C | The headline user-facing problem Numerica can solve |
| That run needed a Rust port, not C CVODE (none installed); its source revision was not pinned (Cargo uses a path) | same record | C | Provenance is a product feature, not paperwork |
| Interval enclosures of D-T ignition quantities (Arb) | Zenodo 10.5281/zenodo.23733098 | C | Certified numerics already used in physics work |
| Kernel-checked BAO enclosures; certified exclusions; Lean through a pinned runner | 10.5281/zenodo.23247730, 23284020 | A/C | The certificate-then-Lean pattern exists and works at small scale |
| Exact rational witnesses, re-verified by an independent checker (754 bistability witnesses) | 10.5281/zenodo.24131124 | C | Cheap-to-verify, expensive-to-find: the right shape for certificates |
| Shifted lonely runner n = 63: Lean replay of a 639 KB generated proof took 2,028 to 3,328 s; `decide` hit the recursion limit until `maxRecDepth` was raised | 10.5281/zenodo.24051700 | C (Lean part A, run by the main session only) | **Scale warning for Lean integration:** unrolled certificate terms do not scale; design compact certificates |
| Process failures we caught: an audited certificate overwritten by a later run; background jobs dying with the session; an auditor's check "still running" at handback | session journals | X | Why the audit CI (section 5, Phase 0) is worth building |

## 2. rusty-SUNDIALS today (read directly at commit af4886f; the repository is `xaviercallens/rusty-SUNDIALS`)

- Workspace version 6.4.0, BSD-3-Clause, about 15,100 lines of Rust under `crates/`. Crates: `sundials-core`, `cvode`,
  `ida`, `nvector`, `sundials-mcp`, `benchmarks`, `qf-pgpe`, `qf-cmb-cascade`, `rusty-sundials-py`. [C: my own listing]
- **Claims versus what I found.** The README advertises "formally verified", 34 Lean 4 specs, "zero unsafe" and 134
  tests. In `proofs/lean4` there are 58 top-level Lean files and 27 occurrences of the word `sorry` in 13 of the 71
  Lean files (17 in code, 10 in comments; the first draft of this document said "10 of them", which was wrong). Under
  our own binding rule a file containing `sorry` is not a proof, so "formally verified" is not supportable until a
  sorry-free, axiom-audited run says otherwise. The README checklist mentions an `arkode` crate and `kinsol-rs`; only a
  small `arkode` module (about 350 lines) exists, inside `sundials-core`, and no `kinsol` code was found (the first
  draft said both were missing, which was too strong for `arkode`). `unsafe` matches 4 times in `crates` (two of them
  `forbid(unsafe_code)` directives, two comments). The first draft said "I did not run the 134 tests"; since then the
  measurements below were made.
- **The brainstorm's anchors are not in this checkout:** `crates/sundials-core/src/genetics.rs` (101 tests, Dual-RRK,
  ARS(2,2,2), Haar wavelet, Sherman-Morrison-Woodbury preconditioner), `sundials-enclose`, `sundials-krylov` and
  `sundials-elenchus` do not exist at this commit, and I did not find "Paper E" or "Paper C Edition 2" in our Zenodo
  record. They may live on a branch or another repository. **Treat them as inputs to verify, not as facts.**
  *Update of 16 November 2026:* `genetics.rs` was found in the separate genetics repository (branch
  `contrib/programme-n4-isothermal-2026-10-26`, `rust_solver/genetics.rs`, 1,497 lines, 5 test attributes in the file, so
  the "101 tests" is unverified); Paper E is in the same repository (Zenodo 10.5281/zenodo.23525664); Paper C Edition 2
  was not found; the three proposed crates do not exist.
- **Measurements made after this document was drafted (15 November 2026; AI agents, no human audit):**
  `cargo test --workspace` gives 344 passed, 0 failed, 6 ignored at the then-current `main` (137 passed at the earlier
  commit); the strict Lean gate passes 4 of the 58 top-level files (3 are candidates for kernel-checked status). The
  README was corrected in rusty-SUNDIALS pull request 83 (release v11.7.1).

## 3. The brainstorm, item by item

| Brainstorm item | Evidence in our record | Verdict |
|---|---|---|
| Atol-dominance diagnostic; Jacobian-scaled vector atol | Direct: the y2 finding (169x), our audit's correction 3 | **v1.** Highest value, cheapest |
| Local-to-global error estimator (forward/adjoint shadow) | Our true-error table is the benchmark (486x at rtol 1e-10) | **v1**, as a diagnostic; validate against the enclosure |
| Native Rust validated enclosure engine (log-norm + Lohner) | Producer method, auditor's Lohner/MPFI cross-check at t <= 40 (boxes 1e3 to 1e8 times narrower) | **v1 core.** The auditor's method is the better *tight* method, the producer's is the one that reached 4000; the hybrid is a research question, not a given |
| Persistent Newton contraction-rate tracker | Not in our record | Later; verify first |
| Precision escalation on `ErrTestFailure` (f64 to f128) | Direct: rtol 1e-10 aborted at the first output | **v1** |
| Generic scalar trait (f64, f128, rationals, balls) | Direct motivation: `fl(0.04) != 1/25` | **v1**, as the enabling refactor |
| Dual-RRK relaxation; invariant projections; positivity-preserving IMEX | Robertson's linear invariant was used by hand; the rest unverified | Later (v2), after the genetics code is located and re-tested |
| Radii-polynomial Banach contraction checker | Unverified here | Later |
| Lean theorem for the one-step log-norm bound; certificate emitter | Prose-only lemma today (the limitation our audit recorded) | **v1 flagship**, with a kill criterion (Phase 3) |
| Build-time provenance pinning (git SHA, toolchain, prereg hash) | Direct: unpinned Cargo path, post-launch preregistration commit | **v1, first** |
| Negative-control CI (`audit-controls`), claim ledgers per PR, Lean gate | Our controls caught real bugs; the ledger gate exists in the paper template | **v1** |
| Krylov/PDE crate, wavelets, Bi-Helmholtz, Leray projections | Unverified; a different problem class | **Cut from v1** |
| E8 lattice quantiser; GUDHI/TDA bridge; blow-up and "frustration index" monitors | Unverified; research topics | **Cut.** Keep on research branches |

Scope rule: a solver library that tries to carry spectral PDE kernels, topology and lattice compression will not
reach Tier A on anything. One wedge, done to the standard in section 5.

## 4. Positioning

**Category.** Audited numerical computing: solvers whose results carry their own evidence level.
**Promise (one sentence).** "Numerica returns the answer and how much to trust it: a fast solve, a rigorous enclosure
where you ask for one, and a machine-checkable certificate where we have one."
**Message rules (binding).** Never "formally verified" unless the claim is Tier A. Never "faster than SUNDIALS"
without a measurement we ran. Every output header names its tier. We say "to our knowledge" for novelty, as in our
papers.

**Three layers (names are working titles):**
1. **Numerica Solve:** SUNDIALS-compatible stiff and non-stiff solvers in Rust. Table stakes; not the pitch.
2. **Numerica Certify:** validated enclosures and exact-rational certificates, with a Lean checker for selected
   statements. The pitch.
3. **Numerica Audit:** provenance, claim ledger, negative controls, and an AI-producer/AI-verifier gate for pull
   requests. The moat. It is also what makes AI-written numerical code trustworthy to anyone else.

**Who it is for (hypotheses to test with interviews, [X]):**
- verification-minded computational science teams (fusion, nuclear, aerospace, energy-system modelling) who must
  defend numbers to a regulator or a reviewer;
- AI-for-science groups whose pipelines need a machine-checkable verifier, not another model;
- Lean and formal-methods users who need numerics next to their proofs;
- journals and archives that want reproducible, hash-pinned computation.

**Landscape (search snippets, [L], not exhaustive):**
- SUNDIALS (LLNL) is active: v7.6 (January 2026) added official Python interfaces; v7.9 is the newest version I saw.
  It is the incumbent for speed and trust through maturity, not through certificates. I found nothing on global-error
  estimation in the releases I could read.
- Rust has interval-arithmetic crates (for example `inari`) and plain ODE solvers; my search found **no Rust crate
  that does validated ODE integration**. Established validated integrators are C++ or Julia (CAPD, VNODE-LP,
  TaylorModels.jl, DynIBEX; named in our earlier prior-art screen, SECONDARY).
- Lean: LeanCert (verified interval arithmetic, v1.0 announced January 2026) is the closest neighbour; it proves
  numerical facts and is not a dynamics solver. A Lean library of Lyapunov stability theorems exists (May 2026,
  theory only). I found no Lean-verified ODE integrator. **Numerica should depend on and cite these, not rebuild them.**
- Our differentiation is therefore the *combination*: a solver users can run, an enclosure engine, and a Lean-checked
  core, under an audit discipline.

**Non-goals for v1:** replacing SUNDIALS' C ABI; GPU performance claims; general PDE tooling; claiming correctness
for problems we did not enclose.

**Name.** `numerica` is already a crate on crates.io (MIT, from the Symbolica team: number types, error-tracking
floats, dual numbers), so a crate with that name is unavailable and the two would be confused. "Numerica" is also used
by Numerica Corporation (tracking and defence) and by a mathematics-education service mark; a 1991 Wolfram filing for
NUMERICA appears abandoned. I did **not** run a formal trademark search. Options: keep "Numerica" as the brand with
crate names such as `socrate-numerica-*`, or pick a different name before any public launch. A trademark lawyer
should confirm either way.

## 5. Roadmap (rough, from a standing start; ranges are my estimates [X])

Each phase ends in an audited release candidate and has a kill criterion. Producers are AI agents; an independent
verifier writes its own check; Opus-class audits only where they pay.

**Phase 0 (2 to 3 weeks): truth-in-labelling and provenance.**
- Run the strict Lean gate on all 58 files in `proofs/lean4`; relabel everything that fails; delete "formally
  verified" from the README until true. Reconcile the README with the workspace (arkode, kinsol, test counts).
- `build.rs` embeds git SHA, dirty-tree hash, toolchain and any preregistration hash in every binary and JSON header;
  replace path dependencies (as in our `rob_runner`) with pinned revisions.
- Claim ledger and negative-control CI (a broken solver must be rejected), gated per pull request.
- Locate the brainstorm's artifacts (`genetics.rs` and the papers it cites) and record what exists.
- *Exit:* every public claim maps to a ledger row. *Kill:* none; this is the price of entry.

**Phase 1 (4 to 8 weeks): Numerica Check, the diagnostics.**
- Atol-dominance monitor and a global-error estimator in the BDF controller; optional Jacobian-scaled vector atol.
- Generic scalar trait and automatic f128 rescue on `ErrTestFailure`.
- *Exit:* reproduces our published Robertson table (169x, 486x) from the diagnostics alone, and a measured
  false-alarm rate on a set of well-posed benchmarks. *Kill:* if the estimator cannot beat a simple tighter-tolerance
  rerun at similar cost, ship the monitor only.

**Phase 2 (8 to 16 weeks): Numerica Enclose, native.**
- Port the PH-2 method to Rust ball arithmetic. The backend (FFI to flint/Arb versus a pure-Rust ball type) is an
  open decision that needs a short spike.
- Keep the independent Lohner method as a cross-check inside CI.
- *Exit:* boxes equal or inside the published ones to t = 4000, with the 8.31 core-hour Sage figure as the baseline
  to beat (I set no speed-up promise before measuring). *Kill:* if the native engine cannot match the Python/Sage
  boxes, keep Sage as the reference and document it.

**Phase 3 (12 to 24 weeks, overlapping): Numerica Lean, Tier A for one theorem.**
- Formalise the one-step theorem: the midpoint identity for quadratic fields, the Dini-derivative comparison, the
  spectral-norm basis-change bound. Emit compact certificates checked by a verified checker.
- **Design constraint from our own data:** unrolled terms made a 639 KB file take about 34 to 55 minutes to compile.
  Use proof by reflection or a verified checker over rational traces, not generated term proofs.
- *Exit:* a sorry-free, axiom-audited theorem plus an end-to-end certificate for one Robertson step range, through the
  pinned runner. *Kill:* if no sorry-free statement of the one-step theorem exists after the allotted weeks, release
  Tier C with a prose proof and an independent checker, and say exactly that.

**Phase 4 (after the above, only for verified items): structure preservation.**
Relaxation Runge-Kutta, invariant and positivity projections, persistent Newton rate, radii-polynomial checker,
brought over from `genetics.rs` only after it is located and its tests re-run.

## 6. Evidence and release discipline

- Every release ships its ledger (A, C, L, X rows), the controls output, the pinned build header and the independent
  audit report. Releases are reproducible from a hash.
- Benchmarks: reproduce our Zenodo numbers first; add external reference problems (Robertson, Van der Pol, E5,
  Oregonator) with the references' own status marked (the "recalled" literature values for Robertson are solver
  output, not exact).
- Success metrics ([X] targets to be set by the owner): audited claims per release; enclosure horizon at a fixed
  width and cost; false-alarm rate of the diagnostics; independent reproductions.

## 7. Licensing and go-to-market (owner decisions)

rusty-SUNDIALS is BSD-3-Clause, matching upstream SUNDIALS; the NOTICE and attribution obligations to LLNL stay.
Three options:
- **A. Open everything (BSD-3 or MIT/Apache for the Lean library)**, earn from certified runs, audit CI and support.
- **B. Open core**, commercial audit and certificate services; risk: weakens the trust story.
- **C. Academic first:** papers, Zenodo, Lean library, no commercial offer until Phase 3 produces Tier A.
Recommendation: **C, then A.** The credibility is the asset, and our records show it comes from published, audited,
reproducible results. The private AI-reasoning direction is separate and must not be mixed into Numerica
repositories.

## 8. Risks

- **Over-claiming.** The largest risk and already present in the README. Mitigation: Phase 0.
- **Scope creep** from the brainstorm. Mitigation: section 3's cuts.
- **Lean cost.** Certificate checking can be slow and Mathlib builds here are partial. Mitigation: reflection, small
  imports, the pinned runner.
- **Incumbent catch-up.** SUNDIALS or Julia could add a global-error estimator. Mitigation: the Certify and Audit layers.
- **Name conflict** (section 4).
- **AI-produced everything.** No human audit has been part of any of our papers. A human reviewer for the first
  Tier-A release is advisable.
- **Capacity.** About 8.3 core-hours per validated enclosure today; the roadmap assumes the native engine fixes this and
  that spend stays inside the weekly cap.

## 9. Decisions needed

1. Brand: keep "Numerica" (with prefixed crate names) or rename, after a trademark search.
2. Enclosure backend: FFI to Arb/flint or pure Rust.
3. License model: A, B or C (recommendation C then A).
4. Phase 0 authorisation: relabel the README and run the Lean gate on all 58 files now.
5. Where the brainstorm's artifacts live (`genetics.rs`, "Paper E", "Paper C Edition 2"), so I can verify them.
6. Whether a human reviewer is available for the first Tier-A release.

## Sources

- Our records: Zenodo 10.5281/zenodo.24216837, 24131124, 24051700, 23733098, 23247730, 23284020.
- SUNDIALS releases: [v7.6.0](https://groups.google.com/g/sundials-users/c/DnPUT5P6iu4), [LLNL releases](https://github.com/LLNL/sundials/releases).
- Rust interval arithmetic: [inari](https://docs.rs/crate/inari/latest); crate-name conflict: [numerica on docs.rs](https://docs.rs/numerica), [Symbolica 1.0 post](https://symbolica.io/posts/stable_release/).
- Lean neighbours: [LeanCert discussion](https://leanprover-community.github.io/archive/stream/113488-general/topic/LeanCert.20-.20Verified.20Computation.20.26.20Interval.20Arithmetic.html), [Verifier closure for interval programs](https://zenodo.org/records/19808324).
- Name search: [NUMERICA trademark record](https://trademark.justia.com/741/61/numerica-74161030.html), [Numerica Corporation](https://markinton.com/company/numerica-corporation).
