# News study, 2026-10-27: routes beyond brute-force Lean for the humanity goals

**Author:** Xavier Callens (SocrateAI Lab). Drafted by an AI agent (Claude). No person has reviewed it.
**Status:** read-only study. No code was changed, nothing was attempted, nothing was committed.
**User request (verbatim):** "Study the last news if there are opportunities for us to progress further with our
humanity goal and not only lean 4 brute force formalization, respecting Elenchus and our code of conduct".

**Rules this study keeps.**
- A source is **read** only if it was opened in this session. The reading log (section 8) gives one quoted sentence
  per source and says how it was opened.
- Anything seen only as a search-result snippet is marked **not read**.
- Two kinds of quote are not verbatim:
  - quotes that came through the WebFetch summariser;
  - quotes taken from alphaXiv's AI-written report rather than the paper text.
  Both are labelled where they appear.
- Every prior, value and feasibility number below is our estimate. None is a measurement.

---

## 1. The Reddit thread (share link `ck5D6BdQTD`): not read

The thread itself was **not read**. Reddit blocks automated access, and the share link carries no information about
its content. What follows is an inference from the news of the last ten days. The search used is in section 8.

| Candidate subject | Date | Evidence we hold |
|---|---|---|
| **OpenAI's three research claims.** (1) A disproof of the Exponential Time Hypothesis (ETH) with a Lean formalisation. (2) Local smoothing for the wave equation in every dimension, which would give the Kakeya maximal and dimension conjectures and Stein restriction "throughout the interior of the conjectured range". (3) A quantum chromodynamics / Yang–Mills claim. | Repo commit 2026-10-26 (`openai/math` `7ef5c0c`, PR #3); press 26–27 Oct | (1) and (2) **read** in the repo (`history.md`, PR #3, the Comparator config). (3) is **not released and not read**: Al Jazeera reports that the physics group delayed its release. |
| OpenAI will stop training frontier models on the live internet | 2026-10-23 (TechCrunch) | Search snippet only, **not read** |
| Simons Foundation $15M Math+AI initiative, with OpenAI contributing $5M and Anthropic a partner | 2026-10-15 | Simons page read through the summariser |
| Reports that OpenAI agents weakened their own monitors; METR's estimate of unmonitored Codex traffic | early October 2026 (roundup dated 2026-10-25) | Search snippets only, **not read** |
| OpenAI's release of 722 manuscripts in 372 families, later revisions and withdrawals | 2026-10-06/07 | **Read** in `history.md`. We already work on this corpus (LL §16–18). |

**Most likely subject:** the 26 October announcement. **Confidence: about 0.55.** It was a day old when the link was
shared and dominated the coverage we found. It also matches the user's wording: "not only lean 4 brute force
formalization" reads like a reaction to "formalized in Lean the next day". The other rows are real alternatives.

What the primary source says, at `history.md`, commit `7ef5c0c`:
- The ETH manuscript "gives a deterministic algorithm that exactly counts satisfying assignments of fixed-width CNF
  formulas in subexponential time and polynomial space".
- An independent working group led by Impagliazzo, Paturi and Williams "will examine and explain the proof".
- The Comparator challenge `SubexponentialSAT.json` names one theorem, has no definition holes, and permits only
  {propext, Quot.sound, Classical.choice}. The challenge file defines its own machine model (`PrimitiveMachine`,
  over Mathlib's `Turing.TM0`).
- Al Jazeera quotes Ryan Williams as saying the proof is still being checked (summariser quote, not verified
  verbatim).
- None of this is verified by us.

**Relevance to our goals: low.**
- The two released results are pure mathematics and complexity theory, outside energy, cancer models, materials and
  carbon.
- They are already under expert examination.
- See section 4, row X1, for the one small contribution open to us: a statement-adequacy review of the machine
  model. It is scored there as off-mission.

---

## 2. Constraints every opportunity must meet

**Code of conduct.**
- Claims are written down before the test.
- Every experiment has a positive and a negative control.
- The maker is not the checker.
- Results carry one of four tiers, A, L, C or X, and Tier X never supports a claim on its own.
- Negative results are published.
- We say plainly that no human has audited the work.
- No medical, climate or device claims.
- Public data only.
- Upstream authors are credited.
- No hype wording.

**Elenchus specifics** (METHODOLOGY §1–5):
- **Effective tier.** A claim's tier is the minimum over its dependency closure.
- **Interval rule.** Ball arithmetic not replayed in Lean is Tier C.
- **The Tier-A gate.** Axioms limited to the whitelist, plus a kernel replay, plus an escape grep for `sorry`,
  `axiom`, `debug.skipKernelTC`, `addDecl`, `native_decide`, `implemented_by` and `#exit`.

**Machine.**
- 8 vCPU. Proposal 4 assigns cores 0–3 to the A1 scheduler and cores 4–7 to wave 1.
- One T4, shared with HiveMind.
- Lean 4.34.1 pinned with Mathlib `d13f23b7` (the openai/math build). The `formal/` tree uses v4.34.0-rc2 with a
  partial Mathlib, and the two must never be mixed.
- rusty-SUNDIALS, LeanFlow, and python-flint/Arb.
- Disk 2 had 1.4 TB free on 2026-10-27, per Proposal 4 §1.

**Proposal 4 is preregistered and wave 1 is running.**
- The preregistration is commit `7b412d0`, with the SHA-256 in `results/proposal4/2026-10-27/preregistration.json`.
- Anything below that touches it is a **dated amendment**. It is never an edit to the preregistered file, and it
  never swaps an in-flight wave-1 lane.

---

## 3. Opportunities found (September–October 2026), by category

Each entry gives:
- what it is, with URL, date and licence;
- a 1–2 week plan on this machine;
- the tier reachable;
- the prior (that a result survives our gate in the time box);
- the over-claim risk;
- how it serves people.

The scales are those of Proposal 4 §3, so the scores are comparable:
- **V** (value) runs from 1 to 5:
  - 1 = a re-check of a known result;
  - 2 = a useful certified number or a small gap closed;
  - 3 = an independent check of a recent claim, an answer to a stated open question, or an audit of a widely used
    public dataset;
  - 4 = a broadly cited new theorem.
- **F** (feasibility) is the fraction of the plan we expect to execute.

### (a) Open scientific datasets and models

**BATT-1. Public Battery Field Data: an audit of physical invariants across the open releases**
- **Source.** Masse (Astrolabe Analytics), arXiv 2610.05811, 2026-10-05.
  - The collection has 35 field-data releases from 27 groups: 256 GB, 149,188 cells, 6,465 labelled or reported
    faults.
  - Repository: github.com/Astrolabe-Analytics/public-battery-field-data, **MIT** (licence confirmed through the
    GitHub API), archived at doi:10.5281/zenodo.23150592.
  - **Per-release licences differ.** Six restrict commercial use (NC), one forbids derivatives (ND), and two state
    no licence.
  - The paper itself reports that "In four releases the number of units or cells differs from the paper."
- **Plan (1–2 weeks).**
  1. Use only releases licensed CC BY 4.0, CC0 or MIT that are under 1 GB each. Candidates include `rwth-home` (CC BY,
     21 GB, so a subset), `cloverleaf`, `tongji_rest`, `deng` (MIT) and `xie` (CC BY / MIT).
  2. **Positive control.** Their `scripts/rebuild.py` rebuilds the headline numbers "from input files stored in the
     repository", so it never touches the downloaded data and does not test our instrument. Instead, load each chosen
     release through their loaders, after checksum verification, and recount units, cells and service spans against
     Table 2 to the printed digits.
  3. **Reference-free invariant audit**, in the spirit of pescert (MLIP-1 below). Where the release exposes the
     fields, check exact or interval-valid necessary conditions:
     - SOC within [0, 100];
     - cell voltages inside the chemistry window;
     - the sum of series cell voltages consistent with pack voltage within the stated resolution;
     - charge throughput consistent with SOC change under the release's own sign convention;
     - no time reversals.
     Count violations per release, taking rounding as ±½ unit in the last place.
  4. **Negative control.** A planted sign flip and a planted unit error (mV vs V) must be detected.
- **Tier.**
  - The counts are exact arithmetic outside the kernel, so Tier C.
  - A Lean certificate is possible for a sample of violations (the LeanFlow `lean.*` data certificates, as in M2):
    Tier A per certificate.
  - Correlating violations with fault labels is Tier X.
- **Prior 0.40.** A clean "no violations under these invariants" is also a result.
- **Over-claim risk: high.**
  - Never "battery X is unsafe" or "dataset Y is wrong". The claim is that some records violate a stated necessary
    condition at the printed precision.
  - The fault labels are other people's.
  - Any discrepancy goes to the release authors first (owner's decision).
- **Serves people.** Field data, not lab cycling, is where battery safety and second-life decisions are made. A
  checked data-quality layer helps fault-detection research and second-life screening.

**MLIP-1. Reference-free certification of machine-learning interatomic potentials, plus an exact Born-stability probe**
- **Source.** Hänseroth & Dreßler (TU Ilmenau), arXiv 2610.00585, 2026-09-30.
  - Fourteen probes, each "certifying against a target that is exact and independent of chemistry and reference
    method". They were applied to 64 pretrained potentials.
  - Code github.com/jhaens/pescert, **MIT**. Data doi:10.5281/zenodo.22731106, licence **to verify**.
- **Plan.**
  1. Reproduce 2–3 of their probes, the cheapest ones (rotational invariance, force–energy integrability), on 2–3
     small open potentials on CPU. **Positive control:** their published leaderboard values.
  2. Add a probe they do not have: **exact Born elastic stability** of potential-predicted elastic tensors, using the
     LDLᵀ / witness-vector certificates planned for Proposal 4 M2.
  3. **Negative control.** A deliberately non-conservative force field must fail integrability, and a tampered
     tensor must be rejected.
- **Tier.** The probe scores are Tier X. The positive-definiteness certificates are Tier A per tensor.
- **Prior 0.35.**
- **Over-claim risk.** Saying "potential P is wrong". The probes test internal consistency, not accuracy, and the
  elastic tensors are model outputs.
- **Serves people.** These potentials are used to screen battery, catalyst and capture materials, so cheap checks of
  their consistency guard screening pipelines.

**Seen in search only (not read).** Each needs its licence and contents read before any use:
- SoLiD26 solid–liquid interface dataset (2609.28013);
- an EPFL hierarchical open structure dataset (2610.21771);
- a 58 Ah prismatic NMC ageing and teardown dataset (2610.23049);
- WBM-MatPES pressure benchmark (2610.14891);
- LLNL/Meta polymer benchmark (2609.27036).

### (b) Verification tooling that lowers the cost per verified claim

**GATE-1. Mechanical numeric and vacuity checks for statement adequacy, applied to our own Tier-A rows**
- **Source.** Mei & Douglas (Harvard CMSA / AletheAI), "Beyond LLM Judge", arXiv 2610.20573, 2026-10-14.
  - The method "combines LLM-based semantic review with mechanical numerical and vacuity checks".
  - Code github.com/annamei1/FLMF-Ch7ErrFunc-Release, **Apache-2.0**.
- **Why it matters to us.** METHODOLOGY says statement adequacy is the gap: "no human has audited [it] for any row".
  Mechanical checks do not close that gap, but they turn part of it from opinion into a test. Two checks apply:
  - **Numeric.** Mei–Douglas (§3.2, read) bind each Lean special function once to an mpmath counterpart, sample points
    from the stated domain, and compare both sides of the identity. They exclude "definitions, limits, infinite sums,
    etc.", and they warn that the check "should only be used as a partial check for correctness, not a complete
    faithfulness check".
    - Our Tier-A rows mostly define functions over ℝ that Lean cannot evaluate, so the binding is a hand translation
      of each definition. That is the same step the check is meant to test.
    - Mitigation: write each binding once, from the paper rather than from the Lean, by an agent that did not write
      the Lean; then count how often each binding is reused.
  - **Vacuity.** Exhibit concrete witnesses for every hypothesis, so a provable-because-vacuous statement is caught.
- **Plan.**
  1. Write a small harness.
  2. **Plant controls first:** a sign flip, a wrong domain, contradictory hypotheses, and `MainStatement := True` for
     a definition hole (LL §16). All four must be caught.
  3. Run it over the Lean statements behind the registry rows ED-01 to ED-24, and over the Proposal 4 wave-1
     statements before their Lean work starts.
     - The rows span two toolchains: v4.34.0-rc2 (QuantumFluids, LeanMaster) and 4.34.1 (openai/math pinned).
     - The harness runs once per toolchain and never mixes them.
     - Rows built on limits or infinite sums get the vacuity check only.
- **Tier.** This is a process audit. It upgrades no claim. Its output is a list: statements that pass, and
  statements flagged with the reason.
- **Prior 0.45.** We expect the harness to run and the controls to be caught. Whether it flags any real row is open.
- **Over-claim risk.** Saying "statements are adequate". Mechanical checks are necessary, not sufficient, and the
  human-audit caveat stays in every paper.
- **Serves people.** It raises the trustworthiness of every already-published row that readers might rely on.

**LEANCERT-1. LeanCert and the RadiiPolynomial framework: certified numerics inside Lean, if kernel-only**
- **Sources.**
  - Wang, Mischaikow & Gameiro (Rutgers), "A Lean 4 Framework for the Radii Polynomial Method", arXiv 2610.02335 (v2
    2026-10-26). Built with "Lean 4.34.1, Mathlib d13f23b7 (tag v4.34.1), and LeanCert ... 7f91b6eb". That is
    exactly our pinned openai/math toolchain.
  - Its code repository github.com/IlPreteRosso/RadiiPolynomial was **not reachable** (GitHub API 404 today).
  - LeanCert, github.com/alerad/leancert: **Apache-2.0**, DOI 10.5281/zenodo.21681348. Main is now on Lean 4.35.0.
    Revision `7f91b6eb` (2026-09-29) is on 4.34.1.
- **The trap, read in the source.**
  - LeanCert's interval tactics state in `LeanCert/Tactic/Interval.lean`: "`interval_le`, `interval_ge`,
    `interval_lt`, `interval_gt` - Prove bounds using `native_decide`".
  - Its design notes describe several certificate paths closed "with one `native_decide`".
  - On Lean 4.34, `native_decide` shows up in `#print axioms` as an auxiliary axiom (`…native_decide.ax_1_1`, per our
    verification-traps note). Our whitelist rejects that axiom, and our escape grep forbids `native_decide`. **As
    shipped, LeanCert proofs on those paths are not Tier A under Elenchus.**
  - The same file also says that the `Real.exp` paths, which use noncomputable evaluation, "cannot use
    `native_decide`". Those are exactly the paths E1 and M3 need, so they are the first test target.
  - Its CI soundness guard bans user axioms and `sorry`, but `native_decide` is part of its trusted base, by design.
- **Plan.**
  1. Build LeanCert `7f91b6eb` in its own Lake project against the pinned openai/math Mathlib. Never inside
     `formal/`.
  2. Run `#print axioms` on its README examples, as a control.
  3. Classify each tactic path as kernel-only or `native_decide`.
  4. Start with the `Real.exp` paths. If a kernel-only path exists for transcendental bounds, possibly by swapping in
     `decide +kernel` on the rational checker, try it on **one** existing Tier-C Arb enclosure: for example one Proposal 4 E1 reactivity bound, or one
     N2 sub-box. Record the width and time reached.
- **Tier.**
  - A kernel-only success is Tier A for that enclosure. It would upgrade a Tier C piece and lower the cost of the
    interval rule.
  - Otherwise LeanCert is an **independent Tier C cross-check** (producer ≠ verifier for Arb results), which is still
    useful.
- **Prior 0.30.**
- **Over-claim risk.** Calling a `native_decide` proof "kernel-checked".
- **Serves people.** Indirectly. It makes certified statements about energy and carbon models cheaper.

**Also read, lower priority for us.**
**KAPPA-1 (conditional). A step-by-step proof check of a published cancer-model paper**
- **Source.** She & Wang (Purdue), KAPPA, arXiv 2610.35596, 2026-10-26; github.com/ziwaa-se/kappa, **MIT**.
  - It runs on Claude Code and checks a paper's proofs result by result. Each result gets one of four verdicts:
    verified, verified conditionally (with named hypotheses), issue recorded, or unfinished.
  - Blind on three published statistics papers, "the kit found the published error at the step that the correction
    names".
- **Condition.** The natural target is Proposal 4 C3's Alvarez–Viossat Proposition 1, the comparison principle. C3 is
  **deferred** until a reader with a mathematical-oncology background has seen the wording rules (section 5).
  KAPPA-1 is therefore an opportunity **only if the owner un-defers C3**.
- **Plan (if un-deferred).**
  1. Install KAPPA in a separate project on the pinned 4.34.1 toolchain.
  2. **Controls.**
     - Positive: one of KAPPA's own example papers with an answer key, reproduced to its published verdicts.
     - Negative: a planted false step in a copy of Proposition 1's proof must receive "issue recorded".
  3. Run the kit on Alvarez–Viossat arXiv 2211.17041 Proposition 1. Every cited ODE comparison input becomes a named
     hypothesis.
- **Tier.** A for "verified conditionally", with the named hypotheses listed. An "issue recorded" verdict is Tier C
  until a second, independent check confirms it.
- **Prior 0.35.** Mathlib's ODE comparison coverage, and our partial local Mathlib, may stop it at "unfinished".
- **Over-claim risk.** Above all, "containment is better for patients". The statement is about ODE trajectories under
  stated monotonicity hypotheses.
- **Serves people.** It makes explicit which hypotheses a widely discussed adaptive-therapy argument rests on, with
  no clinical claim.
- **FloatLib** (Caltech/WUSTL, arXiv 2609.19352; we read alphaXiv's AI report, **not** the paper text). A verified
  floating-point library in Lean. Per the report, it is slower than MPFR on all 84 binary medians. It could one day
  give a verified semantics to Tier X float code. Not actionable in two weeks.
- **AnnalsChallenge** (Imperial, arXiv 2610.18301; github.com/ImperialCollegeLondon/AnnalsChallenge,
  **Apache-2.0**). 50 hand-formalised Annals main theorems on LeanEval. Its AI audit found mistakes in 11 of the 50
  formalisations, and 7 papers missing hypotheses. This is strong outside evidence for GATE-1's premise. The
  benchmark is pure mathematics: off-mission.
- **Seen in search only (not read).** Numina Fuse (2610.33860), SemantEq (2610.32919), MechAlign (2610.35269),
  NanoProof (2610.11605), LeanPRM (2610.17697), Reflections on Trusting Lean (2610.30433).

### (c) AI-for-science releases we could use or audit

**MHD-1. An independent check of AI-produced closed-form 3D MHD equilibria that break stellarator symmetry**
- **Source.** Issan, Citrin, Landreman & Tracey (Google DeepMind / UCSD / UMD), arXiv 2610.07304, 2026-10-05, read
  in full.
  - Two explicit multi-parameter families solve (∇×B)×B = ∇p and ∇·B = 0, with nested tori and non-constant pressure.
    They generalise Landreman's stellarator-symmetric solutions (arXiv 2609.26742, **not read**).
  - The paper says this "has therefore remained an open problem" until now.
  - The AI disclosure says the work "was carried out using Gemini 4 running as a small team of agents in Google
    Antigravity". The authors re-derived it and checked it symbolically.
  - Licence of the arXiv text: to verify. The formulas themselves are mathematics.
- **Why it fits.** It is an AI-made claim in energy, checked by a different maker. That is the Elenchus
  producer ≠ verifier rule applied outside our lab. The result is closed-form, so the check is exact rather than
  numerical.
- **Plan.**
  1. **Family 1** (the stretched asymmetric Solov'ev family, eqs. 4–7):
     - Compute the residual of force balance and of ∇·B exactly in Sage, with F treated algebraically (F² = G).
     - Check the constant Jacobian −ab/Ω³ (eq. 11) and the enclosed volume (eq. 13).
     - Check the nested-torus condition 0 < δ < (1 − Ω²ε)²/4.
     - **Positive control:** τ₀ = 0 must reproduce Landreman's family. **Negative control:** flipping the sign of the
       2τ₀z term in B_z must leave a non-zero residual.
  2. **Lean, family 1.** Prove the force-balance identity as an identity in a differential-algebra formulation:
     polynomials in x, y, z, F with ∂F = ∂G/(2F). The chain from that algebra to the real PDE statement is Tier C
     glue, stated as such.
  3. **Family 2** (the complex-phase elliptic family, eqs. 15–17): exact CAS check only. Its branch of √(1 + ε/ω̄²)
     and the elliptic-coordinate map need care.
  4. **Exploratory (Tier X, wave 2 at the earliest).** Run one open equilibrium solver on a τ₀ ≠ 0 case and compare.
     DESC is the candidate; its licence and CPU cost are to verify.
- **Tier.**
  - The algebraic identity for family 1 is Tier A.
  - The PDE statement and the family-2 checks are Tier C.
  - Solver comparisons are Tier X.
  - The headline is Tier C.
- **Prior 0.45.** The authors already checked symbolically, so agreement is the likely outcome. The uncertain parts
  are the Lean core and the family-2 branch conditions. Any discrepancy goes to the authors first, after a second
  independent check.
- **Over-claim risk.**
  - "Fusion equilibria verified". These are ideal-MHD model solutions, with no stability, transport or device
    statement.
  - "AI result confirmed". We check the stated formulas, not the paper's interpretation.
- **Serves people.** Closed-form benchmarks are how open stellarator codes are verified. A checked benchmark that
  breaks stellarator symmetry exercises the half of the Fourier space those codes usually skip.

**Seen in search only (not read).**
- Gómez-Serrano, Liehr & Taylor, "Counterexamples to Grad's conjecture" (2609.24739, cited by MHD-1);
- PPPL AI gyrokinetic surrogates (2609.28730);
- Tokamak-SI (2610.32264);
- IGNITE world model (2610.02515; trained on DIII-D data, so not public data);
- Oxford/Shanghai equilibrium reconstruction (2610.09674);
- the Columbia/IPP open vacuum-response code (2610.00536).

From web search only (not read): Anthropic's ART enzyme-system announcement (late September 2026; Bloomberg reports
expert caution); Meta/LLNL OPoly26; the OMat24 and OMol25 datasets. One extended web search, plus one about OpenAI
specifically, found no September–October 2026 open-weights science model from OpenAI, DeepMind, Meta, Microsoft or
NVIDIA. That is a search result, not proof of absence.

### (d) Recent results in our four areas that are reproducible from public data

**CARBON-1. Certified bookkeeping of the 2025 low-latency global carbon budget**
- **Source.** Ciais, Ke, Tian et al. (LSCE and 30+ institutions), arXiv 2609.34226, 2026-09-28, read in full.
  - The paper states: "The bottom-up budget imbalance ... is 0.81 ± 0.69 GtC yr⁻¹ using the growth rate of MBL
    stations and a conversion factor of 2.124 GtC per ppm."
  - Its inputs are public: Global Carbon Budget 2025, NOAA GML, OCO-2, GFED and ERA5. Each licence is to verify. GCB
    data are commonly CC BY 4.0, which we have not checked.
- **Scratch check (Tier X, by hand, not a result).**
  - 10.38 − 2.04 − 3.15 − 2.06 × 2.124 = 0.8146, consistent with 0.81, when the ocean term is the emulator value 3.15.
  - With the combined ocean value 3.11 it would be 0.85.
  - So the paper's imbalance uses the emulator ocean flux. That is consistent with "bottom-up", but it should be
    pinned from the text, not inferred.
- **Plan.**
  1. Write the paper's budget identities as exact interval statements over the printed decimals: the bottom-up and
     top-down budgets, the land-sink average 2.36 ± 0.16, and the strengthening 2.81 ± 0.31.
  2. Certify which printed combinations are arithmetically consistent at the printed precision.
  3. Test whether each stated ± matches quadrature, or worst-case propagation, of the component uncertainties. The
     convention is not stated, so report both.
  4. **Positive control:** the identities that must close exactly. **Negative control:** a planted ppm-to-GtC factor
     of 2.13 must break closure.
  5. Then link to K3: under the Joos impulse-response model the 2025 numbers sit in a stated set. This is Tier X/C
     context only.
- **Tier.** Tier A is possible for the interval arithmetic over printed rationals, since it is trivial in Lean. The
  meaning is Tier L, the paper's numbers.
- **Prior 0.45.** Low novelty, high reliability, the same profile as K2.
- **Over-claim risk.**
  - Any statement about the land sink or the climate. We certify arithmetic consistency of published numbers, nothing
    about the Earth system.
  - If an inconsistency appears, it goes to the authors first.
- **Serves people.** Carbon-budget numbers drive public and policy discussion. Transparent, checkable arithmetic is a
  small but real public good.

**TUMOR-1. When can sparse tumour-volume data identify a growth law? A certified non-identifiability statement on synthetic data**
- **Source.** Lu & Wang (University of Oklahoma), "AI-Assisted Tumor-Growth Law Discovery from Sparse Data", arXiv
  2610.16891, 2026-10-12. **Abstract and introduction read; the body was not read.**
  - "Plausible saturation, accurate trajectory fits, and convincing explanations can therefore coexist with incorrect
    growth laws."
  - They also report that archived LLM rankings show "no consistent improvement over selection by training error".
  - Their code repository has **no licence** (GitHub API), so we do not reuse it. The data are synthetic Gompertz
    data, which we regenerate ourselves.
- **Plan.**
  1. From scratch, with our own synthetic Gompertz, logistic and Richards trajectories, prove a **certified
     non-identifiability** statement: for a stated sampling design (n points on [0, T], noise level σ), there exist
     parameters for which a Gompertz and a logistic trajectory stay within σ of each other at every sample point. Use
     interval-certified bounds on the closed-form solutions.
     - **Non-triviality condition.** Two curves can stay within σ of each other merely by both sitting on their
       plateau. The witness must therefore have:
       - at least half the sample points in the growth phase (V(t) ≤ 0.8 of the carrying capacity);
       - a fold-change of at least 4 over the window;
       - a design no denser than the sparse designs the paper studies (to pin from its body, which is not read yet).
     - A witness that fails this condition is discarded. That is the GATE-1 vacuity rule applied here.
  2. Also certify admissibility lemmas (positivity, boundedness, saturation) for the families. These are short Lean
     statements, Tier A.
  3. **Positive control:** dense noiseless sampling separates the families (a certified separation). **Negative
     control:** logistic-generated data must not be certified as "Gompertz only".
- **Tier.**
  - The admissibility lemmas are Tier A.
  - The non-identifiability witness is Tier A if the closed forms are bounded in Lean, else Tier C (Arb).
  - Model-selection experiments are Tier X.
- **Prior 0.35.**
- **Over-claim risk: high.**
  - Anything about patients, prognosis or treatment.
  - This is about ODE families on synthetic data. No real tumour data is used, and no clinical inference is drawn.
- **Serves people.** Model-based oncology increasingly relies on fitted growth laws, including "virtual trials" (see
  section 6). A certified "these data cannot tell the laws apart" is a guard against over-confident model selection,
  by humans or LLMs.

**Novelty checks for wave 1 (search snippets only, so weak evidence).**
- No 2026 paper surfaced that pre-empts Proposal 4 **C1**, the census of death-Birth amplifiers on graphs with
  N ≤ 10. Nearest hits: 2610.04090 on multi-allele fixation, 2608.06552 on replacers in the Moran Birth-death process,
  2610.05857 on random regular networks. All are **not read**.
- No 2026 paper surfaced that pre-empts **E1**, certified p-¹¹B ideal-ignition windows in the 0D power balance.
  - 2610.16304, six-fluid spherical-torus equilibria, is **not read**.
  - The laser-driven papers 2609.04987 and 2609.33483 are inertial or beam schemes, outside E1's scope. They fall
    under the E1 dual-use line in any case.

### (e) Community initiatives where honest negative results are an asset

- **Simons Foundation Math+AI initiative.** $15M with OpenAI and Anthropic, announced 2026-10-15.
  - The open call is "Targeted Grants to Math+AI Institutes", with a proposal deadline of **2026-12-01**.
  - Eligibility was **not read**, and the summariser could not tell whether an independent lab qualifies.
  - The page says "The goal of the program is to support the mathematics community" (summariser quote).
  - **Owner's decision.** Our Elenchus registry, with its published negative results and controls, is the kind of
    "shared standards for AI use" material the call describes. But that is a mathematics programme, not our four
    areas.
- **ETH working group (Impagliazzo, Paturi, Williams).** Materials were made public "so others can examine them as
  well". See X1 in section 4.
- **LeanEval / AnnalsChallenge.** A public leaderboard, pure mathematics, off-mission. Section 6 covers why we would
  not chase it.
- **openai/math auxiliary checker.** The restored C++ sources and Python checker for "The maximum number of mutually
  unbiased bases in dimension six" can be re-run independently, as Tier C. Quantum information is off-mission, so it
  is not ranked.

---

## 4. Ranking

**Score = p × V × F**, with Proposal 4's exact scales (p in [0.25, 0.45], V from 1 to 5, F in (0, 1]).

**The "Serves people" column is reported beside the score. It does not enter it.** The tiers are those reachable
within the time box.

**How V is assigned to tooling items (GATE-1, LEANCERT-1).** Proposal 4's value rubric is written for claims. A
tooling item upgrades no claim by itself, so it gets the rubric's V = 2 ("a useful certified number, or closes a
small numerically-supported gap"). It does not get V = 3, which is reserved for audits of widely used public
datasets, independent checks of recent outside claims, and answers to stated open questions. The draft of this
study had given both tooling items V = 3. That broke comparability with Proposal 4 and has been corrected.

| Rank | Id | One line | p | V | F | p × V × F | Tier reachable | Serves people (not scored) |
|---|---|---|---|---|---|---|---|---|
| 1 | MHD-1 | Independent exact check of DeepMind/Gemini-produced non-stellarator-symmetric MHD equilibria | 0.45 | 3 | 0.75 | 0.45 × 3 × 0.75 = **1.013** | A (algebraic core), C headline | verified benchmarks for open fusion codes |
| 2 | CARBON-1 | Certified arithmetic consistency of the 2025 low-latency global carbon budget | 0.45 | 2 | 0.90 | 0.45 × 2 × 0.90 = **0.810** | A arithmetic, L meaning | checkable public carbon numbers |
| 3 | BATT-1 | Invariant audit of CC-BY/MIT battery field-data releases | 0.40 | 2.5 | 0.70 | 0.40 × 2.5 × 0.70 = **0.700** | C counts, A samples | battery safety and second-life data quality |
| 4 | GATE-1 | Mechanical numeric (mpmath-bound) and vacuity checks on our own Tier-A statements | 0.45 | 2 | 0.70 | 0.45 × 2 × 0.70 = **0.630** | process audit | trust in all published rows |
| 5 | TUMOR-1 | Certified, non-trivial non-identifiability of tumour-growth laws from sparse synthetic data | 0.35 | 2 | 0.80 | 0.35 × 2 × 0.80 = **0.560** | A lemmas, C/X rest | guards model-based oncology against over-fit laws (no clinical claim) |
| 6 | MLIP-1 | Reference-free MLIP probes plus an exact Born-stability probe | 0.35 | 2.5 | 0.60 | 0.35 × 2.5 × 0.60 = **0.525** | X probes, A per tensor | materials screening reliability |
| 7 | KAPPA-1 (conditional) | Step-by-step proof check of C3's Alvarez–Viossat Prop. 1, **only if the owner un-defers C3** | 0.35 | 2.5 | 0.60 | 0.35 × 2.5 × 0.60 = **0.525** | A conditional / issue recorded | the hypotheses of containment theory made explicit (no clinical claim) |
| 8 | LEANCERT-1 | Can LeanCert certify our enclosures kernel-only (no `native_decide`)? `Real.exp` paths first | 0.30 | 2 | 0.70 | 0.30 × 2 × 0.70 = **0.420** | A if kernel-only, else C cross-check | cheaper certified energy and carbon models |
| – | X1 | Statement-adequacy review of the ETH Comparator machine model (off-mission) | 0.45 | 1 | 0.80 | 0.45 × 1 × 0.80 = **0.360** | C | none for the four areas |

**How to read the table.**
- **Why GATE-1 has F = 0.70, not the draft's 0.85.**
  - Mei–Douglas bind special functions to mpmath once each. Our rows need hand bindings of noncomputable ℝ
    definitions, which is the very translation step under test.
  - Limits and infinite sums are excluded from the numeric check.
  - The harness has to run separately on two toolchains.
- **KAPPA-1 is conditional.** Without it, the **unconditional list has 7 items**. X1 is not promoted to fill the gap.
- **Ties.** Ranks 6 and 7 are tied. The gaps between ranks 2 to 8 are smaller than the calibration error of the
  inputs, as in Proposal 4.
- **X1 is out of the top 8 on purpose.**
  - It is complexity theory, not one of our four areas.
  - An expert group already owns it.
  - LL §16 and §18 say a Comparator re-run is an instrument check, not discovery.
  - Its V = 1 is the "re-check of a known result" score.
- **KAPPA-1 is the only Lean-heavy item in the top 8**, and it is not brute force. It follows the paper's own proof
  and records an "issue" verdict when the proof fails.
- **Six of the eight are mainly non-Lean routes**: data audits, exact CAS checks, interval bookkeeping, mpmath-based
  statement checks, and certified witnesses on synthetic data. They are MHD-1's CAS half, CARBON-1, BATT-1, GATE-1,
  TUMOR-1 and MLIP-1.

---

## 5. Is Proposal 4 already covering the best options?

**Mostly yes.**
- Its wave 1 (C1, M3, M1, K1, E1) still looks right.
- Nothing we found pre-empts C1 or E1, though that rests on search snippets only.
- M3, the independent check of Luo–Wei's AI-assisted proof, is the same producer ≠ verifier idea as MHD-1, and it is
  already in flight.

**Four dated amendments are worth considering.** Each augments a preregistered item and replaces none. No wave-1 lane
is swapped. Each would be written as `results/proposal4/2026-10-27/AMENDMENT_<date>.md`, never as an edit to the
preregistered file.

1. **§5, the gate, augmented by GATE-1.** Add the vacuity check, and the numeric check where a definition can be
   bound, to the Tier-A gate for every item, before its Lean work starts.
   - It ranks 4th as a scored item, but it is the change with the widest effect, because it applies to every item.
   - It touches no hypothesis, only the instrument, and its planted controls must be caught first.
2. **Energy, a wave-2 addition: MHD-1 as E4.** Energy is Proposal 4's thinnest area: E1 is in wave 1 only by the
   K2 ↔ E1 swap.
   - MHD-1 (0.45 × 3 × 0.75 = 1.013) scores above every energy item, including E1 (0.735), E2 (0.640) and E3 (0.595).
   - Recommendation: **add** it to wave 2 and do not drop E3. If the owner wants wave 2 kept at its size, E3 is the
     item it would displace.
3. **Tooling note for E1, K2, M1 and M3 (LEANCERT-1).**
   - Record that LeanCert at `7f91b6eb` matches the pinned toolchain.
   - Record that its interval tactics use `native_decide`, so they may be used only as an independent Tier C
     cross-check unless a kernel-only path passes the escape grep.
   - This changes no prior. It adds a possible second checker for the Arb enclosures.
4. **K3, an added positive control: CARBON-1.**
   - Add the carbon-budget arithmetic as a cheap positive control and context for K3, or file it as a small K4.
   - It does not change K3's question (c) about the number of concentration peaks.

**What would not change.**
- C2 and C3 stay deferred until a reader with a medical-physics or mathematical-oncology background has seen the
  wording rules.
- When C3 is un-deferred, KAPPA-1's verdict scheme (verified, conditionally verified, issue recorded, unfinished) is
  the instrument to use.
- BATT-1, TUMOR-1 and MLIP-1 are candidates for a later Proposal 5, not amendments. M2 could absorb MLIP-1's Born
  probe if M2 runs.

---

## 6. What to decline (it would breach the code of conduct)

| Decline | Why | Examples seen (not read unless stated) |
|---|---|---|
| **Anything using patient or human-subject data** | No patient data, of any kind | causal "medical world model" for treatment planning (2610.26923); biopsy-based parameter estimation with a cancer centre (2609.22363) |
| **Unreviewed clinical modelling framed as therapy guidance** | No medical claims. "Virtual trials" and RL-chosen chemotherapy schedules read as treatment advice. | CAR-T plus chemoradiotherapy "virtual trials" in glioma (2609.39191); RL adaptive chemotherapy (2609.12264) |
| **Claims of tonnes removed, or MRV for commercial carbon removal** | No climate or deployment claims | weather-foundation-model ERW quantification by a removal company (2610.28973); artificial ocean fertilisation (2610.10204) |
| **Closed or restricted data** | Public data only; respect NC/ND terms | DIII-D-trained IGNITE (2610.02515); the 6 NC, 1 ND and 2 unlicensed battery releases (read in 2610.05811 Table 1); the unlicensed tumour-growth code repository |
| **Inertial-fusion yield or target modelling** | The Proposal 4 §7 dual-use line | laser-driven p-¹¹B yield studies (2609.04987, 2609.33483) |
| **Benchmark or leaderboard chasing** | Benchmark gaming; a score is not a verified claim. LL §1 and the verification traps note the 200 cases that embed their solutions. | LeanEval/AnnalsChallenge submissions; tuning to the pescert leaderboard |
| **"Verifying" the headline OpenAI claims, or racing the expert groups** | LL §16/§18: a re-run is an instrument check. Saying "we verified ETH is false" would be an over-claim. | ETH, local smoothing / Kakeya, the unreleased QCD claim |
| **Wet-lab biology claims** | Outside a one-machine computational lab and outside our tiers | the ART enzyme system (Anthropic, late September 2026) |
| **Hype wording, or a "peer-reviewed" label without a reviewer** | Code of conduct; the discovery-journal lesson ("5-round peer-reviewed" meant no reviewer was called) | — |

---

## 7. Summary for the owner

- **The Reddit thread was not read.** It is probably about OpenAI's 26 October ETH and local-smoothing release
  (confidence about 0.55).
- That release is off-mission for energy, cancer models, materials and carbon.
- **Best new routes beyond brute-force Lean:**
  - an exact check of an AI-made fusion-equilibrium result (MHD-1);
  - certified bookkeeping of public carbon-budget numbers (CARBON-1);
  - an invariant audit of open battery field data (BATT-1);
  - mechanical statement-adequacy checks for our own gate (GATE-1).
- **LeanCert matches our toolchain but relies on `native_decide`.** It is a cross-check, not Tier A, unless a
  kernel-only path is shown.
- **Proposal 4 stands.** Four dated amendments are possible: the gate, E4 = MHD-1, the LeanCert tooling note, and the
  K3 control. None of them touches wave 1.

---

## 8. Reading log

The "how opened" column takes four values:
- **full**: alphaXiv full text or raw file;
- **partial**: the stated sections only;
- **report**: alphaXiv's AI-written report, not the paper;
- **summariser**: WebFetch's model summary, so the quote is not verified verbatim.

| # | Source | Date | How opened | One quoted sentence |
|---|---|---|---|---|
| 1 | `openai/math` `history.md`, commit `7ef5c0c` (Apache-2.0) | 2026-10-26 | full (raw via `gh api`) | "The case of 3-SAT refutes the Exponential Time Hypothesis." |
| 2 | `openai/math` PR #3 description | 2026-10-26 | full (`gh api`) | "Add the manuscripts *Local smoothing for the Euclidean wave equation* and *The Exponential Time Hypothesis is False*, with accompanying Lean formalizations." |
| 3 | `openai/math` `lean/ComparatorChallenges/SubexponentialSAT.json` and the first ~120 lines of `.lean` | 2026-10-26 | partial | `"theorem_names": ["OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat"]` |
| 4 | `openai/math` ETH preprint README (paper.pdf **not read**) | 2026-10-25 | full (README only) | No sentence to quote: the README holds only the title, author, date and a BibTeX block. |
| 5 | Al Jazeera, "AI makes discoveries in mathematics, computer science, physics, OpenAI says" | 2026-10-27 | summariser | Williams: "We are working to verify and examine their proof and determine if it holds up." (summariser quote) |
| 6 | Simons Foundation, "Simons Foundation launches $15M effort" | 2026-10-15 | summariser | "The goal of the program is to support the mathematics community." (summariser quote) |
| 7 | Issan, Citrin, Landreman, Tracey, arXiv 2610.07304 | 2026-10-05 | full | "As noted in Section 4 of Landreman [1], constructing explicit analytical solutions that break stellarator symmetry has therefore remained an open problem." |
| 8 | Wang, Mischaikow, Gameiro, arXiv 2610.02335 | 2026-10-01 (v2 2026-10-26) | partial (abstract, introduction, source footnote, references) | "Source code at https://github.com/IlPreteRosso/RadiiPolynomial, revision 445773960f43, built with Lean 4.34.1, Mathlib d13f23b7 (tag v4.34.1), and LeanCert [Rad26] 7f91b6eb." |
| 9 | LeanCert README, `lean-toolchain`, `soundness-guard.yml`, `Tactic/Interval.lean` (grep), `Tactic/design-notes.md` (grep) | main as of 2026-10-21; rev `7f91b6eb` 2026-09-29 | partial (`gh api`) | "`interval_le`, `interval_ge`, `interval_lt`, `interval_gt` - Prove bounds using `native_decide`" |
| 10 | George, Adkisson, Anandkumar, FloatLib, arXiv 2609.19352 | 2026-09-16 | report (paper text **not read**) | "Against MPFR, all 84 measured binary medians are slower for FloatLib." (from the AI report) |
| 11 | Browning et al., AnnalsChallenge, arXiv 2610.18301 | 2026-10-13 | full | "We release them without formalised proofs." |
| 12 | Hänseroth & Dreßler, arXiv 2610.00585 | 2026-09-30 | partial (abstract, introduction opening, data and code availability) | "Here we show that a potential can be graded without any reference calculation, against properties the exact Born-Oppenheimer surface satisfies by mathematical or physical necessity." |
| 13 | Masse, Public Battery Field Data, arXiv 2610.05811 | 2026-10-05 | full | "In four releases the number of units or cells differs from the paper." |
| 14 | Lu & Wang, arXiv 2610.16891 | 2026-10-12 | partial (abstract, introduction opening, code-availability line) | "Plausible saturation, accurate trajectory fits, and convincing explanations can therefore coexist with incorrect growth laws." |
| 15 | She & Wang, KAPPA, arXiv 2610.35596 | 2026-10-26 | partial (abstract, introduction opening, licence line) | "In all three, the kit found the published error at the step that the correction names, together with further problems that we confirmed by hand." |
| 16 | Mei & Douglas, arXiv 2610.20573 | 2026-10-14 | partial (abstract, introduction opening, §3.2 numerical check) | "Unlike most verification methods, which rely on LLMs or trained models, our method combines LLM-based semantic review with mechanical numerical and vacuity checks, providing checkable feedback and detecting errors missed by LLM judges." |
| 17 | Ciais, Ke, Tian et al., arXiv 2609.34226 | 2026-09-28 | full | "The contrasting changes in land and ocean uptake indicate that the rebound of the terrestrial sink is the dominant carbon budget change associated with the sharp decline in atmospheric CO2 growth in 2025." |
| 18 | GitHub API licence lookups | 2026-10-27 | API | pescert MIT; AnnalsChallenge Apache-2.0; FLMF Apache-2.0; public-battery-field-data MIT; the tumour-growth code repository has no licence; leanprover/comparator Apache-2.0; kappa MIT; openai/math Apache-2.0; LeanCert Apache-2.0; RadiiPolynomial 404 |

**Opened and failed (not read).**
- openai.com/index/sharing-ai-progress-in-mathematics/ (HTTP 403).
- openai.com/index/building-scientific-understanding-with-academic-communities (HTTP 403).

**Seen only as search snippets (not read).** These cover the news context in section 1 and the "seen in search"
lists in section 3:
- the WebSearch results: unite.ai, TechCrunch (2026-10-23), Euronews (2026-10-16), the enoumen roundup (2026-10-25),
  Washington Post (2026-10-07), Wikipedia, and the Anthropic ART coverage with Bloomberg (2026-09-24);
- every alphaXiv identifier listed in section 3 or section 6 without a row above.

**Local context read for this study.**
- The memory index `MEMORY.md`, and the notes `proposal4-and-showcase-2026-10-27.md`, `discovery-journal-2026.md`,
  `proposal3-run-2026-10-26.md` and `verification-traps.md`.
- `LL.md` (headings plus §16–18 in full).
- `docs/proposals/NEXT_STEPS_PROPOSAL_4_2026-10-27.md` (full).
- `NewDiscoveries-pr/elenchus_discoveries_2026-10/METHODOLOGY.md` (§0–5).
