# Proposal 4: energy, cancer models, new materials, carbon countermeasures (2026-10-27)

**Author:** Xavier Callens (SocrateAI Lab). Drafted with AI agents (Claude).
**Status:** proposal. Nothing in it has been attempted. The preregistration is
`results/proposal4/2026-10-27/preregistration.json`; it holds the SHA-256 of this file.
**User request (verbatim):** "Continue and look to new discoveries that could help humanity on energy, cancer
treatment, new materials and technical to counter balanced carbon emission based on existing works and go to the
next level with less certainty on what could be discovered but with the same rigor."

## 0. How to read this proposal

- **Priors.** Each prior is the probability, for the stated time box, that the hypothesis's *verifiable core*
  passes its gate with a non-trivial statement. It is not the probability that the physics is "right". Every headline
  prior is in [0.25, 0.45], and every sub-prior is at most 0.5. Expected passes of positive controls are recorded
  separately, not as priors. The 2026-10-25 round showed our priors were underconfident on corollaries
  (`results/autoresearch/2026-10-25/`, mean prior 0.45; every attempted item was a corollary and fell in minutes). So known results are used here only as
  **positive controls**, and every headline points at the uncertain extension.
- **Tiers (Elenchus).**
  - **A:** kernel-checked Lean statement. Axioms limited to {propext, Classical.choice, Quot.sound}, no `sorry`,
    statement locked, planted controls caught. Checked through `anse/formal/lean_runner.py`.
  - **L:** cited literature, pinned to page and line.
  - **C:** human or AI argument.
  - **X:** floating point. Tier X never supports a claim on its own.
- **Interval rule.** Ball arithmetic (python-flint/Arb) that is not replayed in Lean is Tier C. This is the
  N1/N2/B2 precedent: "Lean holds the logic and rationals; the integrals are ball arithmetic, outside the kernel".
- **Literature.** A paper is marked **read** only if we opened it in this session (alphaXiv full text or report,
  or the arXiv abstract when marked "abstract"). Anything else is marked **not read**. The reading log, with one
  quoted claim per paper, is in the preregistration.
- **Models are not reality.** Every number below is a property of a stated mathematical model with stated
  parameters. See section 6.

## 1. What this round builds on (verified in the registry, `NewDiscoveries-pr/elenchus_discoveries_2026-10/REGISTRY.md`)

| Asset | Where it came from | Used by |
|---|---|---|
| Lean 4.34.1 pinned stack and integer-certificate method (`decide +kernel` tables lifted by induction) | Certified DESI BAO, ED-03/04 | E1, E2, K1, K2, M3 |
| LeanFlow fail-closed `lean.*` data certificates (with the `#exit` sentinel) | ED-14 | all A-tier items |
| Zero-point curvature certificates (Gaussian, Yukawa) and the open Ewald-split item for r^-3 tails | ED-20, N1, N2 | M1 |
| CM/Bernstein Lean library (subordination, Laplace mixtures) | ED-16 | K3, M3 |
| `PopGen` (absorption limits, Moran fixation, Price) and `EvoGraph/BirthDeath.lean` (isothermal theorem, birth-death) | ED-18, ED-23 | C1 |
| rusty-SUNDIALS CVODE/IDA crates (`qf-yukawa-crystal`, `qf-popgen` PR #80, phonons PR #79) | ED-09/10, ED-15 | M1, C1, C3, E2 |
| Audited 0D current-quench example (rusty-SUNDIALS PR #60) | fusion audit | E1 (numerics only) |

**Not used as a base.** The pre-audit fusion paper, the `discoveries/*fusion*.json` files, and the
19-October stellarator batch, which was withdrawn as an over-claim (L-STELLARATOR). E1 starts from published
formulas and is cross-checked only against the audited PR #60 code.

**Machine as observed on 2026-10-27 at about 11:45 UTC.**
- 8 vCPU; T4 shared with HiveMind (t4_governor running, 4.8 GB used); disk 2 has 1.4 TB free.
- The A1 Lean scheduler is **not running**. Its last status line is 2026-10-26 18:48 UTC, from before a reboot. It
  is meant to resume on cores 0-5 for weeks.
- Every cost below therefore assumes the **worst case**: cores 6-7 only, with A1 on 0-5. If A1 stays paused,
  lanes may spread over all 8 cores, pinned to disjoint sets with `taskset`.
- Nothing here needs the GPU beyond optional local-prover attempts (DeepSeek-Prover-V2-7B). Those must not be
  interleaved with embedding jobs on the T4.

## 2. The twelve hypotheses

Each hypothesis lists:
- the question and what it builds on;
- the literature, read and not read;
- the data source and its licence;
- the verifiable core, with its tier;
- the exploratory part (Tier X);
- positive and negative controls;
- the kill criterion and the prior, including what a negative result still teaches;
- the cost;
- the model tier for each stage;
- the failure modes (over-claim risks).

### Area 1: energy

#### E1. Certified ideal-ignition windows for proton-boron fuel under explicit power-balance models

- **Question.** Within the 0D power balance that Wurzel–Hsu use, P_c ≥ P_B (charged-particle heating at least
  bremsstrahlung), is there any (T_i, T_e/T_i, boron fraction) box where p-¹¹B can ideally ignite?
  - Use the Ochs–Fisch bremsstrahlung fit (with the x² term).
  - Test two published reactivity parametrisations: the older one, and the higher "updated" one.
  - Answer with certified inequalities, not plots.
- **Builds on.** Our BAO integer-certificate method, which proves inequalities of explicit functions over boxes.
  Audited PR #60 is used only to cross-check numerics.
- **Literature read.**
  - Wurzel & Hsu 2021, arXiv 2105.10954 (full text).
    - D-T ideal ignition temperature 4.3 keV.
    - Minimum D-T n_iTτ_E of 2.9×10²¹ m⁻³ keV s at 14 keV.
    - For the older p-¹¹B reactivity, "P_B always exceeds P_c when T_e ≳ T_i/3" (Fig. 28).
    - Updated cross sections "suggest that ignition may be possible".
  - Ochs & Fisch 2023, arXiv 2310.18508 (full text).
    - Bremsstrahlung fit, eq. (14).
    - About 450 s confinement needed for thermonuclear ignition at 10¹⁴ cm⁻³ with the Putvinski reactivity.
  - Context only: Kolmes, Ochs, Fisch 2022, arXiv 2211.17143 (abstract only, seen through the arXiv API).
- **Not read.** Putvinski, Ryutov, Yushmanov 2019 (Nucl. Fusion 59, 076018); Nevins & Swain 2000; Sikora & Weller
  2016; Bosch & Hale 1992. These must be obtained and pinned before the item starts.
- **Data and licence.**
  - Reactivity fit coefficients come from the primary papers above, licence to verify.
  - Fallback: the public Wurzel–Hsu plotting code, which their paper says is available; licence to verify.
  - Fallback: EXFOR cross-section tables (IAEA, public), licence to verify.
- **Verifiable core (Tier A for the inequalities, given the fitted formulas).**
  - **(a) Positive-control reproduction.** Certified enclosures of the D-T ideal ignition temperature, and of the
    minimiser and minimum of n_iTτ_E (Wurzel–Hsu eq. 22, Q_fuel = ∞).
  - **(b) Older reactivity.** A certified θ* such that P_c < P_B for every T_i ∈ [50, 500] keV and boron fraction in
    [0.05, 0.5] whenever T_e/T_i ≥ θ*.
  - **(c) Updated reactivity.** Either a certified non-empty box with P_c > P_B at T_e = T_i, or a certified
    exclusion over the same box.
- **Exploratory (Tier X).** Sensitivity to the kinetic enhancement factor, and to synchrotron losses (absent from
  both models). Cross-check against an independent float implementation.
- **Controls.**
  - Positive: the D-T numbers above, and their reproduction by an independent implementation.
  - Negative: a planted reactivity scaled ×0.5 must break the D-T reproduction (must fail). A tampered bremsstrahlung
    coefficient table must be rejected by the kernel.
- **Kill criterion.** The item stops at (a) in any of these cases:
  - the reactivity parametrisations cannot be pinned from primary sources;
  - (a) does not reproduce the published D-T numbers to the printed digits.
  - If (c) cannot separate P_c from P_B anywhere, the certified sub-boxes are reported.
- **Prior 0.35.** A negative or "no window" result still gives certified, model-scoped statements. That clarifies
  the p-¹¹B debate, which currently rests on figures.
- **Cost.** About 20 core-h numerics and 40–60 core-h Lean on cores 6-7; no GPU.
- **Model tiers.** Sonnet for the parametrisation pinning, the interval code and the paper; Opus for the Lean
  certificate assembly and the audit.
- **Failure modes.**
  - Turning "the model's ideal-ignition inequality holds or fails" into "p-¹¹B fusion is (im)possible".
  - Ignoring that T_e < T_i must be maintained by some mechanism.
  - Treating ideal ignition as reactor breakeven. Ochs–Fisch show breakeven is a different, weaker condition.

#### E2. A certified surface-saturation time for fast charging in the single-particle battery model

- **Question.** In the SPM, the representative graphite particle carries spherical diffusion with constant D and a
  constant-current surface flux. When does surface stoichiometry first reach a threshold c* (a model proxy for the
  onset of lithium plating), as a function of C-rate?
  - Enclose t*(C) rigorously, from the exact eigen-series with certified roots of tan α = α and a rigorous tail.
  - Then ask the uncertain question: does the certified t* survive replacing the SPM by the SPMe?
- **Builds on.** Certified integration and the CVODE method-of-lines.
- **Literature read.** Marquis, Sulzer, Timms, Please, Chapman 2019, arXiv 1905.12553 (full text).
  - SPM eq. (20).
  - The SPM's error grows with C-rate: 19.86 mV at 1C and 62.78 mV at 3C RMS vs DFN.
- **Not read.** Chen et al. 2020 (J. Electrochem. Soc., the "Chen2020" parameter set); the PyBaMM JORS paper;
  Crank, *Mathematics of Diffusion*.
- **Data and licence.** The Chen2020 parameter set as shipped in PyBaMM. Both the software licence (believed
  BSD-3) and the paper licence are to verify.
- **Verifiable core.** For stated parameters, t*(C) lies in a certified interval at C ∈ {1, 2, 3, 4}.
  - The series algebra and monotonicity lemmas are Tier A.
  - The root enclosures are Tier A if replayed with rational certificates, else Tier C.
- **Exploratory (Tier X).**
  - SPMe and DFN values from PyBaMM (SUNDIALS IDA) compared with the certified SPM t*.
  - Map where SPM and SPMe disagree by more than the certified width.
- **Controls.**
  - Positive: the short-time √t asymptotics; PyBaMM's SPM surface concentration falls inside the enclosure.
  - Negative: D perturbed by ×1.1 must move t* outside the enclosure; a planted wrong root must be rejected.
- **Kill criterion.** The tail bound cannot be made rigorous at the needed width, or PyBaMM SPM disagrees with the
  certified SPM. A disagreement is a finding: report it.
- **Prior 0.4.** A negative result shows how far a certified simple model is from the standard model it reduces.
- **Cost.** About 10 core-h numerics and 20 core-h Lean.
- **Model tiers.** Sonnet for numerics and paper; Opus for the Lean statement and audit.
- **Failure modes.** Presenting t* as a charging limit for real cells, or a plating prediction. It is a property of
  the SPM with one parameter set, and the SPM is known to be inaccurate at high C-rate.

#### E3. Kernel-checking the "numerically verified" monotonicity behind the universal efficiency–power bound of low-dissipation heat engines

- **Question.** Ma, Xu, Dong, Sun (2018) derive the detailed upper bound η̃₊(P̃, ζ, η_C) on efficiency at given
  power (their eq. 13). The universal bound (their eq. 1) needs η̃₊ to increase in ζ, which they only checked
  numerically: "the analytical proof of its monotonicity is tedious and difficult. Instead [we] numerically
  calculate the derivative" (Appendix B).
  - Can ∂η̃₊/∂ζ ≥ 0 on [0,1] × [−1,1] × (0,1) be proved, symbolically or by certified subdivision, and checked in
    Lean?
  - That would also give a machine-checked proof of the Holubec–Ryabov bounds (34).
- **Literature read.**
  - Holubec & Ryabov 2016, arXiv 1603.02551 (full text). Bounds (34) were proved only near δ_P = 0 and δ_P = −1,
    "strong numerical evidence" otherwise.
  - Ma et al. 2018, arXiv 1802.09806 (full text).
  - Ye & Holubec 2021, arXiv 2112.08923 (full text), the heat-pump analogue.
- **Not read.** Esposito, Kawai, Lindenberg, Van den Broeck 2010 (PRL 105, 150603).
- **Data.** None; closed-form model.
- **Verifiable core (Tier A).**
  - Lean: the universal bound (eq. 1) for all P̃ ∈ [0,1].
  - Then the monotonicity in ζ: symbolic, or by a rational subdivision certificate of a derivative lower bound away
    from the degenerate face η_C → 0, plus a separate argument on that face.
- **Exploratory (Tier X).** Locate where ∂η̃₊/∂ζ is smallest; test whether the bound is attained.
- **Controls.**
  - Positive: the Esposito EMP bounds η_C/2 ≤ η* ≤ η_C/(2−η_C), the δ_P = 0 case (should fall quickly).
  - Negative: a perturbed formula (one factor changed) must fail at a certified point; a planted `sorry` must be
    flagged.
- **Kill criterion.** Two budgets without the full box. Then report the certified sub-box. A certified point where
  ∂η̃₊/∂ζ < 0 is a counterexample, to be reported first, after a second independent check.
- **Prior 0.35.** The derivative vanishes as η_C → 0 (their Fig. 6), so certification degenerates on that face.
  A negative result locates exactly where the published "numerically verified" claim needs care.
- **Cost.** 10–40 core-h.
- **Model tiers.** Opus for the proof; Sonnet for subdivision tooling and paper.
- **Failure modes.** Claiming relevance to real power plants: the low-dissipation model is an idealisation
  (Ponmurugan, arXiv 1901.09908, not read).

### Area 2: cancer, strictly mathematical models

> **Nothing in this area is medical evidence.** These are statements about mathematical models of populations
> of cells, with made-up or literature parameters. They are not validated against patient data. No treatment
> schedule, dose or strategy is recommended, and no clinical claim is made. Bortfeld et al. themselves say their
> fractionation results "should not be taken as immediate recommendations for a change in clinical practice".

#### C1. The smallest unweighted amplifier of weak selection under death-Birth updating: an exact census of all connected graphs with N ≤ 10, and exact certificates

- **Question.** Under death-Birth (dB) updating (a cell dies, its neighbours compete for the slot), amplification is
  at most bounded and transient (Tkadlec et al. 2019).
  - Richter (2020) tested all cubic graphs with N ≤ 22 and all quartic graphs with N ≤ 16, each with one edge removed
    at the vertex of largest remeeting time.
  - He used the weak-selection test N_eff > N (his eqs. 1–4, attributed to Allen et al.).
  - His smallest amplifier is a quartic graph on N = 11 minus one edge, amplifying only for 1 < r < r_max ≈ 1.00075.
    The fixation-ratio excess is about 10⁻⁷, computed in floating point with round-off about 10⁻¹⁴.
  - Our questions:
    1. Over **all** connected unweighted graphs, is there a dB amplifier of weak selection with N ≤ 10?
    2. What is the exact smallest size?
    3. Can his N = 11 example be made rigorous by exact rational arithmetic?
  - Because amplification lives near r = 1, the census uses the **exact first-order (weak-selection) criterion**.
    For each graph this is a rational linear solve of C(N,2) coalescence times. Sampled r values could miss a graph
    that amplifies only on (1, 1.001), so they are not used.
  - Tissue-like graphs (cycles, 2D tori with boundary, crypt-like hierarchies) are included because the fixation of a
    fitter clone on tissue structures is the cancer-modelling motivation (Kaveh et al.).
- **Builds on.** `EvoGraph/BirthDeath.lean` (the Bd isothermal theorem, ED-23) and `PopGen` (absorption limits,
  ED-18); `qf-popgen` (rusty PR #80) for numerics.
  - ED-23's lesson applies: "the count is a birth-death chain" is **not** preregistered again; it was false (not
    lumpable).
- **Literature read.**
  - Tkadlec, Pavlogiannis, Chatterjee, Nowak 2019, arXiv 1906.02785 (full text). Theorem 2, ρ_dB ≤ 1 − 1/(r+1).
    Open question 1 asks about unweighted transient amplifiers.
  - Hindersin & Traulsen 2015, arXiv 1504.03832 (full text). "Up to size 14, we have not found a single
    amplifier" among random graphs; exact (I−Q)⁻¹R method; cycle formula with a positive-coefficient proof.
  - Kaveh, Komarova, Kohandel 2014, arXiv 1411.4556 (full text). The DB isothermal theorem holds only for r = 1;
    exact 1D formulas with separate birth and death rates.
  - Richter 2020, arXiv 2008.01446 (full text). Table 1, the N = 11 example (Fig. 1), the N_eff criterion (eqs. 1–4)
    and the cycle formula (eq. 12).
  - Richter 2022, arXiv 2204.12861 (abstract).
- **Not read.**
  - The Allen et al. paper Richter cites as [7] for the weak-selection criterion.
  - Allen et al. 2017 (arXiv 1605.06530, abstract only).
  - Nowak, Michor, Iwasa 2003; Werner et al. 2011.
  - Derényi & Szöllősi 2017 (arXiv 1701.00934, abstract seen in search only).
  - **Before the census starts:** read Allen et al. [7] and pin the exact statement and hypotheses of the N_eff > N
    criterion.
- **Data.** Graph enumeration with nauty `geng` (Apache-2.0, to verify). The connected-graph counts per N must match
  OEIS A001349 (11,117 at N = 8; the N = 9, 10 counts to be read from OEIS, not quoted from memory).
- **Verifiable core.**
  - **(a) Tier A, positive controls.**
    - The dB fixation formula on K_N: (N−1)/N · (1−1/r)/(1−r^{1−N}).
    - The dB cycle formula: 2(r−1)/(3r−1+(r−3)r^{2−N}).
    - The cycle-below-well-mixed inequality via Hindersin's positive-coefficient form.
  - **(b) Exact rational N_eff for every connected graph with N ≤ 10.** These are rational coalescence-time solves.
    - Census statement: either "no connected unweighted graph on N ≤ 10 vertices has N_eff > N", or the exact list of
      those that do.
    - Tier A for each listed graph: a kernel-checked rational certificate of the solve and of N_eff > N.
    - Tier C for completeness of the enumeration, which depends on `geng` and the OEIS count check.
  - **(c) Transient amplification at an explicit rational r slightly above 1,** for the smallest graph found and for
    Richter's N = 11 example: an exact rational solve of (I−Q)x = R over 2^N − 2 states, and ρ_G(r) > ρ_{K_N}(r).
    - Tier A if the kernel can replay the solve (N ≤ 8 expected).
    - Otherwise Tier C: exact arithmetic in python-flint, outside the kernel.
- **Exploratory (Tier X).**
  - The amplification window (1, r_max) for each graph found.
  - The birth-rate vs death-rate (r, d) plane on tissue-like graphs. This is a "drug raises death rate" model
    parameter, never a drug.
- **Controls.**
  - Positive:
    - the formulas in (a);
    - N_eff = N exactly on every regular (isothermal) graph;
    - the star must be a Bd amplifier and a dB suppressor;
    - Hindersin's N = 4 classification reproduced;
    - Richter's N = 11 graph must give N_eff = 11.0008 to the printed digits.
  - Negative: a planted wrong transition matrix must fail the kernel check; a well-mixed graph must never be
    classified as an amplifier of itself.
- **Kill criterion.**
  - The N = 10 census exceeds two budgets: report N ≤ 9 exact.
  - The criterion's hypotheses cannot be pinned from the primary source: the census stays Tier X.
- **Prior 0.45.**
  - "None with N ≤ 10" is a sharp exact negative result. Richter's N = 11 construction, made rigorous, would then be
    the smallest possible.
  - A smaller example would be a new smallest amplifier.
- **Cost.** About 5–15 core-h for the N ≤ 10 census (exact rational solves after a float pre-screen), 5–20 core-h
  for the exact 2^N solves at N = 11, and 5–20 core-h for Lean certificates.
- **Model tiers.** Sonnet for enumeration and solvers; Opus for criterion pinning, Lean certificates and the audit.
- **Failure modes.**
  - Saying "tissue architecture X promotes or suppresses resistance in patients".
  - Conflating uniform initialisation with mutation-at-birth placement (Hindersin–Traulsen discuss this).
  - Calling enumeration completeness "kernel-checked". It depends on `geng`.
  - Confusing "amplifier of weak selection" with amplification at a given finite r.

#### C2. Radiotherapy fractionation in the linear-quadratic model: kernel-checked structure theorems, and does dose monotonicity survive incomplete repair?

- **Question.** Bortfeld, Ramakrishnan, Tsitsiklis, Unkelbach prove three results in the LQ/BED model:
  - Theorem 1, the dichotomy: one fraction if [α/β]_O ≥ γ[α/β]_T, otherwise uniform doses;
  - Theorem 4, a closed-form optimal fraction number N_c under exponential repopulation (strictly concave
    objective);
  - Theorem 7, non-decreasing optimal doses when the growth rate decreases with tumour size.
  - Formalise Theorems 1 and 4 in Lean as positive controls. The uncertain question: does the
    non-decreasing-dose structure of Theorem 7 persist under incomplete inter-fraction repair, or with two
    organ-at-risk constraints?
- **Literature read.** Bortfeld et al., arXiv 1312.1332 (full text, theorems and appendix proofs).
- **Not read.** arXiv 1312.7337 (search snippet only); Saberian, Ghate, Kim (multiple normal tissues); the
  incomplete-repair literature (Thames).
- **Data.** None; model parameters from the paper's numerical section.
- **Verifiable core (Tier A).** Theorems 1 and 4 as stated. Theorem 7's interchange argument for the exponential and
  Gompertz cases, if time allows.
- **Exploratory (Tier X/C).**
  - Exact-rational dynamic programming on a dose grid with an incomplete-repair term. Look for a counterexample
    where the optimal doses decrease.
  - If one is found, kernel-check that instance (Tier A).
- **Controls.**
  - Positive: the paper's numeric example. Fast-proliferating case: N = 17 optimal, and their objective 15.42 vs
    17.78 for 2 Gy × 30.
  - Negative: a planted reversed condition must fail.
- **Kill criterion.** Two budgets per theorem; the extension stays Tier X if no clean statement emerges.
- **Prior 0.3.** "Monotonicity survives in all tested instances" is weak. A certified counterexample would be the
  real finding.
- **Cost.** About 10–20 core-h.
- **Model tiers.** Opus for proofs; Sonnet for the DP numerics and paper.
- **Failure modes.** Any wording that reads as a schedule recommendation; treating BED/LQ as valid at large
  fraction sizes.

#### C3. Containment versus maximum-tolerated dose: a machine-checked comparison principle, and a search for counterexamples to its conjectured extension

- **Question.** Alvarez & Viossat (2022) prove orderings of resistant-population size and time to treatment failure
  across treatments by comparing trajectories in the R–N plane:
  - Proposition 1: L₁ ≤ L̄ ≤ L₂ implies R₁ ≤ R₂;
  - ideal containment maximises time to failure.
  - They conjecture the results hold without assuming the resistant population keeps increasing.
  - Formalise Proposition 1 in Lean on top of Mathlib's ODE comparison lemmas.
  - Then search for a counterexample to the conjectured extension (Tier X; Tier A if an exact instance is found).
- **Literature read.**
  - Alvarez & Viossat, arXiv 2211.17041 (full text).
  - West et al. 2022, arXiv 2210.12062 (abstract).
- **Not read.** Viossat & Noble 2021 (Nat. Ecol. Evol.; no preprint found); Monro & Gaffney 2009; Zhang et al. 2017.
- **Data.** None; Monro–Gaffney Model 2 parameters as quoted by Alvarez–Viossat (N₀ = 10¹⁰, K = 2×10¹²).
- **Verifiable core (Tier A).** Proposition 1 for C¹ vector fields satisfying their stated monotonicity hypotheses.
- **Exploratory (Tier X).** CVODE runs of Model 2 for containment vs MTD vs intermittent treatment; an adversarial
  search over models violating "R increasing".
- **Controls.**
  - Positive: Proposition 7's ordering on Model 2 in CVODE.
  - Negative: a model violating the hypotheses (g_S increasing in R under high dose, their own example) must be
    shown to break the naive time-domain argument.
- **Kill criterion.** The Lean ODE comparison infrastructure is insufficient after two budgets. Then report the
  statement plus the Tier X study.
- **Prior 0.25.** A negative result shows which hypotheses of the containment theory are load-bearing.
- **Cost.** About 10–20 core-h, plus Lean.
- **Model tiers.** Opus for Lean; Sonnet for CVODE and paper.
- **Failure modes.** Above all, "containment is better for patients". The authors themselves stress that death
  modelled as a hard size threshold favours containment.

### Area 3: new materials

#### M1. Is the triangular dipolar-exciton crystal a local minimum of harmonic zero-point energy? A certificate with Ewald-split tails, at experimentally realised d/λ

- **Question.**
  - N2 certified that the triangular lattice is not a local minimum of E_zp for Yukawa κ = 1, 2. It left Riesz s = 3
    and the dipolar potential open because "r⁻³ tail needs an Ewald split".
  - Close that gap for the bilayer point-dipole exciton potential 2(1/r − 1/√(r²+d²)) (our ED-09 potential). Use
    d/a ∈ {0.06, 0.09, 0.1, 0.5}; the 0.06–0.09 range is d ≈ 0.6 nm with λ ≈ 7–10 nm, per Zhou–Tang–Yu.
  - Certify the sign of the zero-point second variation at the triangular point.
  - The uncertain part: whether this destabilisation can matter before Lindemann melting. ED-21 found it does not
    for the Gaussian core within SCHA.
- **Literature read.**
  - Zhou, Tang, Yu 2023, arXiv 2306.01456 (full text). Point-dipole limit; "only the triangular-type excitonic crystal
    is dynamically stable" at γ = 0; η_c^(m) ≈ 0.31.
  - Qi et al. 2026, arXiv 2601.19603 (abstract), an observed exciton crystal.
  - Our own ED-09 and ED-20.
- **Not read.** Bruun & Nelson 2014; Lagoin et al. 2022.
- **Data.** None; analytic potential.
- **Verifiable core.** The finite certificate with rigorous Ewald-split tails and the sign logic is Tier A. The ball
  integrals are Tier C, as in N2.
- **Exploratory (Tier X).** Harmonic Lindemann ratio at the same d/λ; compare with the curvature scale.
- **Controls.**
  - Positive: Gaussian a = 1 (ED-20, negative curvature) and Yukawa κ = 1 (N2) recovered.
  - Negative: Gaussian a = 2 (positive curvature) must not certify negative; a truncated tail must be rejected by the
    tail lemma.
- **Kill criterion.** The Ewald tail bound cannot reach the needed width after two budgets. Report the obstacle, as
  N2 did for Riesz s = 3.
- **Prior 0.4.** Either sign is a result. "Local minimum" would be, to our knowledge, the first certified *positive*
  zero-point statement for a slowly decaying (r⁻³) physical potential.
- **Cost.** 10–40 core-h certificate, about 20 core-h Lean.
- **Model tiers.** Opus for certificate design and Lean; Sonnet for numerics and paper.
- **Failure modes.**
  - Equating harmonic zero-point instability with a real structural transition (ED-21's lesson).
  - Ignoring the moiré potential γ, which Zhou et al. show dominates.

#### M2. An exact Born elastic-stability audit of the JARVIS-DFT elastic tensors

- **Question.** Mouhat & Coudert show that published "stability criteria" for low-symmetry crystals are often
  necessary but not sufficient. They report at least one MOF called stable when it is not.
  - Across all JARVIS-DFT entries with a full 6×6 elastic tensor: how many are **certifiably not positive
    definite** from the published decimals?
  - How many are ambiguous within rounding?
  - How many would pass the incorrect linear orthorhombic criterion but fail the correct one?
- **Builds on.** Exact rational arithmetic and LeanFlow certificates. Positive definiteness has small exact
  witnesses both ways: an LDLᵀ factorisation with positive diagonal, or a rational vector x with xᵀCx ≤ 0.
- **Literature read.**
  - Mouhat & Coudert 2014, arXiv 1410.0065 (full text).
  - Choudhary et al. 2020 JARVIS, arXiv 2007.01831 (full text). Elastic constants by finite differences; Γ-modes by
    DFPT.
- **Not read.** Wu et al. 2007 (PRB 76, 054115); Grimvall et al. 2012 (RMP).
- **Data and licence.** JARVIS-DFT `dft_3d`, through jarvis-tools / Figshare. data.gov lists it as "Public"; the
  licence is still to verify. Materials Project is not used: it needs an API key, and its licence is also to verify.
- **Verifiable core.**
  - Exact classification of every tensor from the printed decimals.
  - A robust classification that is interval-valid for every value within ±½ unit in the last printed place.
  - Tier A Lean certificates for all "unstable" entries and a random sample of "stable" ones.
- **Exploratory (Tier X).** Correlation with negative Γ-mode frequencies where JARVIS has them; ML-screening impact
  (how many entries in common ML benchmarks are unstable).
- **Controls.**
  - Positive: cubic Si/diamond-type entries pass; Mouhat–Coudert's footnote-26 counterexample is unstable.
  - Negative: a tampered tensor is rejected by the kernel.
- **Kill criterion.** The data licence forbids redistribution of derived tables: publish code and counts only. If
  the tensors are unavailable, stop.
- **Prior 0.4** that a non-trivial certified count (≥ 1% unstable, or an exact "none") survives. An exact "none" is
  itself a certified data-quality statement for ML screening.
- **Cost.** About 5–20 core-h.
- **Model tiers.** Sonnet for the pipeline and paper; Opus for the audit and the Lean certificate template.
- **Failure modes.**
  - Calling a DFT tensor "the material's" tensor: it is a calculation, and finite-difference noise can produce
    spurious instabilities.
  - Implying JARVIS is wrong rather than that some entries need care.

#### M3. An independent kernel check of the 3D Yukawa bcc→fcc transition parameter κ* ≈ 1.7179218684699

- **Question.** Luo & Wei (October 2026) determine the global minimisers of the 3D Yukawa lattice energy at every
  density: bcc below κ*, fcc above. The proof is computer-assisted, and "the authors used AI to assist the long but
  finite computations in the Appendix".
  - Can our stack independently kernel-check Lemma A.6, the enclosure 1.717921868469903 < κ* < 1.717921868469904?
  - Can it also kernel-check Lemma A.5 and Lemma 6.1, the theta ordering D(t) > 0 for t > 1 on 1000 + 2000 rational
    cells?
  - Can the 5,828-rectangle global comparison (Lemma A.4) be re-run independently?
- **Builds on.** The BAO integer-certificate method; the CM library (the Yukawa Gaussian representation); our
  Yukawa work (ED-10); the B3 (3D) feasibility study and the October 2026 bcc Coulomb paper (Muratov–Novaga,
  arXiv 2610.29732, which Luo–Wei recover as a corollary).
- **Literature read.** Luo & Wei, arXiv 2610.31456 (full text, including the appendix lemmas).
- **Not read.** Muratov & Novaga (abstract only); Hamaguchi–Farouki–Dubin 1996/1997; Kozhberov 2018.
- **Data.** None; integer shell multiplicities are printed in Lemma A.5 and re-enumerated by us.
- **Verifiable core (Tier A).**
  - Lemma A.6 and Lemma A.5 as Lean inequalities with rational exp/π enclosures.
  - The shell multiplicities, kernel-enumerated.
- **Exploratory and Tier C.** An independent Arb re-run of Lemma A.4 (5,828 rectangles at 512-bit) and of the local
  Lemma A.2.
- **Controls.**
  - Positive: κ* reproduced to 13 digits in an independent float and Arb implementation.
  - Negative:
    - κ = 1.717921868469902 and 1.717921868469905 must give the expected signs;
    - planting a wrong multiplicity (N₇ = 46 instead of 48) must be rejected;
    - a tampered rectangle must fail.
- **Kill criterion.** Rational exponential enclosures at the 10⁻²⁰ margin are too slow in the kernel after two
  budgets. Then kernel-check Lemma 6.1 only and report A.6 as Tier C (Arb).
- **Prior 0.45.**
  - A discrepancy would be urgent to report to the authors, after a second independent check.
  - Agreement would be, to our knowledge, the first independent check of an AI-assisted computer proof in 3D
    crystallisation.
- **Cost.** About 10 core-h Arb, 50–150 core-h Lean, 20–100 core-h for the Lemma A.4 re-run.
- **Model tiers.** Opus for Lean and audit; Sonnet for the Arb pipeline and paper.
- **Failure modes.**
  - Saying "the theorem is verified" when only the finite lemmas are.
  - The analytic reductions (Sections 3–5) stay Tier C unless separately audited. This is the Sandier–Serfaty lesson.

### Area 4: carbon-emission countermeasures

> **No climate effect is claimed by any K item.** These are bounds and identities inside stated models (ideal-gas
> thermodynamics, equilibrium carbonate chemistry, linear impulse-response models). They say nothing about how
> much CO₂ any real deployment would remove, and recommend no deployment.

#### K1. Does "start cold" survive exergy accounting? A second-law audit of the NIST intrinsic-DAC metric on a public 11,660-sorbent dataset

- **What the metric counts.** McDannald et al. (NIST, 2025) define ξ = Δn_CO₂/E_total, with E_total a plain sum of
  heats and works.
  - Eq. (1) counts the heat of adsorption removed at T₁ at face value, "energy will be spent cooling the system".
  - Eq. (4) counts the heating along the desorption path at face value.
  - Eq. (5) sets E₃ = 0 for the return from T_end to T₁, "we assume no energy recovery".
  - No ambient temperature T₀ appears.
  - Their headline insight is "start cold": the Pareto-optimal paths in Table 2 start at T₁ ≈ 200–237 K, and most
    materials are "optimized by lowering the start temperature below ambient".
- **Why this matters.** Under the second law, heat at temperature T is worth |1 − T₀/T| of work.
  - Removing heat at T₁ < T₀ costs refrigeration work.
  - Cooling the sorbent from ambient down to T₁ (inside Step 3, counted as zero) costs work.
  - Rejecting heat above ambient is free.
  - So the face-value sum neither bounds nor follows the minimum work, and it can reward sub-ambient starts for free.
- **Hypotheses.**
  - **H1 (headline).** Under an exergy-consistent energy count (every heat weighted by its Carnot factor relative to
    T₀ ∈ [273, 313] K, including the sub-ambient sensible cooling in Step 3), the Pareto-optimal start temperature
    moves to T₁ ≥ T₀ for most materials. That is, "start cold" is an artefact of the accounting convention.
  - **H2.** No dataset entry has exergy-weighted efficiency above 1/W_min, the ideal-mixture minimum work. A
    violation would flag an inconsistency in the model inputs (for example Henry-constant extrapolation to 200 K).
- **Literature read.** McDannald, Siderius, DeCost, Choudhary, Ortiz-Montalvo 2025, arXiv 2501.04825 (main text in
  full, including eqs. 1–10; the supplement was **not read**).
  - The text says "a few sorbents with intrinsic capture efficiencies above 1.0 × 10⁵ mol/J", while Table 2 lists ξ
    in µmol/J (maximum 11.259).
  - This looks like a unit slip, to be confirmed against the supplement before it is mentioned.
- **Not read.** House et al. 2011 (PNAS); Lackner; the supplement of 2501.04825.
- **Data and licence.**
  - doi:10.5281/zenodo.14452152 (GCMC and cycle results) and github.com/usnistgov/IntrinsicDACCycle (Julia).
  - The licences of both are to verify. NIST work is usually public domain in the US, but this must be checked.
- **Verifiable core.**
  - **(a) Tier A.** W_min(x, f, purity) for ideal mixtures: non-negative, increasing in purity and capture
    fraction, with the f → 0 limit. A certified enclosure at x = 400 ppm.
    - Scratch value (Tier X): 19.4 kJ/mol at 298.15 K for f → 0 and pure product, i.e. 1/W_min ≈ 51.6 µmol/J.
  - **(b) Tier A/C.** For each dataset path, the exergy-weighted energy per mole and the re-optimised Pareto start
    temperature, from the published code and data. Report a certified count of materials whose optimal T₁ moves
    above T₀ (H1), and of any H2 violation.
- **Exploratory (Tier X).** Sensitivity to T₀ ∈ [273, 313] K and to heat-recovery assumptions.
- **Controls.**
  - Positive:
    - reproduce Table 2 ξ values from the dataset and code to the printed digits before any re-weighting;
    - a path lying entirely at T ≥ T₀ with free heat rejection must give exergy weights in (0, 1) and no
      refrigeration term.
  - Negative: a planted path that violates W_min must be flagged; a planted unit error must be detected.
- **Kill criterion.**
  - The dataset and code do not expose per-path temperature-resolved energy terms: H1 stays a Tier C argument.
  - The supplement shows sub-ambient cooling is already priced: H1 is withdrawn and reported as checked.
- **Prior 0.35.** If "start cold" survives exergy accounting, that is a robustness confirmation of the paper's
  insight, plus the certified W_min lemma.
- **Cost.** About 5–10 core-h, plus 5 core-h Lean.
- **Model tiers.** Opus for the second-law argument and audit (Tier C reasoning must be adversarially checked);
  Sonnet for the data pipeline and paper.
- **Failure modes.**
  - Overstating a modelling-convention difference as "an error".
  - Any claim about real DAC plant performance.
  - The authors must be contacted (owner's decision) before any public wording that implies their bound is wrong.

#### K2. Certified CO₂-uptake efficiency per unit of added alkalinity, for seawater (OAE) and acidic soil water (enhanced weathering)

- **Question.** In equilibrium carbonate chemistry at fixed pCO₂, how much dissolved inorganic carbon does one mole
  of added alkalinity bring in: η = (∂DIC/∂TA)|pCO₂?
  - Seawater: T ∈ [0, 30] °C, S ∈ [30, 38], pCO₂ ∈ [280, 560] µatm. Enclose η with propagated uncertainty of the
    dissociation constants.
  - Soil water with acidity: the pH below which η ≈ 0.
  - Jessen et al.'s retardation model of the alkalinity front, v_front = v_H₂O/(1 + dq/dc): certified delay bounds as
    functions of CEC, depth and flux.
- **Literature read.**
  - Jessen, Jakobsen, Looms, Ambus, Postma 2026, arXiv 2607.01835 (full text). Subsoil delay of 12–34 yr per metre;
    55–157 yr at their site; PHREEQC model on Harvard Dataverse.
  - Beerling et al. 2023, arXiv 2307.05343 (abstract).
- **Not read.** Lueker et al. 2000 and Weiss 1974 (constants); Humphreys et al. 2022 (PyCO2SYS); Renforth & Henderson
  2017; Kanzaki et al. 2025.
- **Data and licence.**
  - Constant formulas from the primary papers (to pin).
  - PyCO2SYS as an independent check (GPL-3 believed; to verify; used, not redistributed).
  - The Jessen Dataverse files: licence to verify.
- **Verifiable core.** Certified enclosures of η over the boxes, given the pinned constant formulas. Tier A for the
  algebraic root bracketing; Tier C for any transcendental constants not replayed. Lean monotonicity lemmas for the
  retardation delay.
- **Exploratory (Tier X).** Re-run the Jessen PHREEQC model from their files; compare the delay with our closed form.
- **Controls.**
  - Positive: PyCO2SYS values inside the enclosure; freshwater analytic limit.
  - Negative: a swapped K₁/K₂ set must move η outside the enclosure; a planted unit error in pCO₂ must be detected.
- **Kill criterion.** The constants cannot be pinned to primary sources, so the item stays Tier X.
- **Prior 0.45.** Low novelty, high reliability. The value is certified, uncertainty-bounded numbers for
  measurement-and-verification debates.
- **Cost.** About 5–10 core-h, plus 10 core-h Lean.
- **Model tiers.** Sonnet for numerics and paper; Opus for the audit.
- **Failure modes.** Any statement about tonnes removed or about ecological safety of OAE/EW. Neither is studied.

#### K3. Completely monotone carbon-cycle impulse responses: what is provable about concentration peaks?

- **Question.** In linear impulse-response models, u(t) = u_P + ∫₀ᵗ m(z)h(t−z)dz, with the Joos et al. 2013 mean IRF
  h = a₀ + Σ aᵢe^{−t/τᵢ}, aᵢ ≥ 0.
  - Such an h is completely monotone, so our CM library applies.
  - **(a)** Kernel-check that after emissions stop (m = 0 for t > T), the excess concentration is completely
    monotone on (T, ∞): non-increasing, convex, with limit a₀∫m.
  - **(b)** Certify Seshadri's time delay between peak emissions and peak concentration for his emission family and
    the Joos coefficients.
  - **(c)** The uncertain question: can a single-peaked emission path produce a concentration path with **two**
    local maxima under a CM IRF with a₀ > 0? This means prove "at most one peak" under stated conditions, or find an
    exact counterexample.
- **Literature read.**
  - Seshadri 2015/2016, arXiv 1502.00805 (full text). The Joos mean IRF as quoted in his eq. (1) sums to 0.999 as
    printed, and his text uses τ₁ = 4.30 and 4.4 inconsistently; we will pin the coefficients from the primary source.
  - Joos et al. 2013, ACP 13, 2793 (landing page only; CC BY 3.0; coefficients **not read** in the original).
- **Not read.** The Joos supplement; Allen et al. 2009; FaIR.
- **Data.** Joos IRF coefficients (CC BY 3.0 article; supplement to read).
- **Verifiable core (Tier A).** (a) in full; (b) as certified interval enclosures for stated scenarios.
- **Exploratory (Tier X/C).** (c) by exact-rational piecewise-linear emission families and adversarial search.
- **Controls.**
  - Positive: the single-exponential IRF closed form; Seshadri's approximation eq. (13) within his stated accuracy.
  - Negative: an IRF with a negative coefficient (not CM) must violate (a) on an explicit instance.
- **Kill criterion.** (c) gets two budgets; then it is reported as open with the search space covered.
- **Prior 0.4** for (a) + (b) plus a definite answer to (c) on a stated class. A negative result still says which
  emission-path properties control the number of concentration peaks in linear models.
- **Cost.** About 5–20 core-h.
- **Model tiers.** Opus for (a) and (c); Sonnet for (b) and paper.
- **Failure modes.**
  - Turning model monotonicity into "concentrations will fall when emissions stop" in the real Earth system. The
    Joos fit is a multi-model mean for one pulse experiment (its design is not read here), and real responses are
    state-dependent and nonlinear.

## 3. Ranking

**Scales.**
- Prior p ∈ [0.25, 0.45], as in section 0.
- Value V ∈ 1–5:
  - 1 = re-check of a known result;
  - 2 = a useful certified number, or closes a small numerically-supported gap;
  - 3 = answers a stated open question, or independently checks a recent claimed result, or audits a widely used
    public dataset;
  - 4 = a new theorem likely to be cited broadly;
  - 5 = landmark.
- Feasibility F ∈ (0, 1]: our estimate of the fraction of the plan executable in its time box, given data access,
  licences, and cores 6–7 only if A1 resumes.
- Score = p × V × F.

| Rank | Id | One-line question | p | V | F | p × V × F |
|---|---|---|---|---|---|---|
| 1 | C1 | Smallest unweighted dB amplifier of weak selection: exact census of all graphs N ≤ 10; exact certificate of Richter's N = 11 | 0.45 | 3 | 0.80 | 0.45 × 3 × 0.80 = **1.080** |
| 2 | M3 | Independent kernel check of Luo–Wei κ* ≈ 1.7179218684699 (bcc→fcc Yukawa) | 0.45 | 3 | 0.70 | 0.45 × 3 × 0.70 = **0.945** |
| 3 | M1 | Certified zero-point (in)stability of the triangular dipolar-exciton crystal (Ewald tails) | 0.40 | 3 | 0.70 | 0.40 × 3 × 0.70 = **0.840** |
| 4 | K1 | Does NIST's "start cold" DAC insight survive exergy accounting? | 0.35 | 3 | 0.75 | 0.35 × 3 × 0.75 = **0.7875** |
| 5 | K2 | Certified CO₂ uptake per unit alkalinity (OAE, acidic-soil EW) and front-delay bounds | 0.45 | 2 | 0.85 | 0.45 × 2 × 0.85 = **0.765** |
| 6 | M2 | Exact Born-stability audit of JARVIS-DFT elastic tensors | 0.40 | 2.5 | 0.75 | 0.40 × 2.5 × 0.75 = **0.750** |
| 7 | E1 | Certified ideal-ignition windows for p-¹¹B under two reactivity fits | 0.35 | 3 | 0.70 | 0.35 × 3 × 0.70 = **0.735** |
| 8 | K3 | CM impulse responses: monotone decay after cessation; can one emission peak give two concentration peaks? | 0.40 | 2 | 0.90 | 0.40 × 2 × 0.90 = **0.720** |
| 9 | E2 | Certified surface-saturation time in the SPM battery model under fast charge | 0.40 | 2 | 0.80 | 0.40 × 2 × 0.80 = **0.640** |
| 10 | E3 | Kernel-check the numerically-verified ζ-monotonicity behind the low-dissipation efficiency–power bound | 0.35 | 2 | 0.85 | 0.35 × 2 × 0.85 = **0.595** |
| 11 | C2 | LQ fractionation theorems in Lean; does dose monotonicity survive incomplete repair? | 0.30 | 2.5 | 0.75 | 0.30 × 2.5 × 0.75 = **0.5625** |
| 12 | C3 | Containment vs MTD comparison principle in Lean; counterexamples to its conjectured extension | 0.25 | 2.5 | 0.60 | 0.25 × 2.5 × 0.60 = **0.375** |

The sort order matches the products. The gaps between neighbouring scores (0.7875 / 0.765 / 0.750 / 0.735) are
smaller than the calibration error of the inputs: treat ranks 4–7 as a tie.

## 4. Recommended waves

- **Wave 1 (top 5 by score):** C1, M3, M1, K1, K2. This covers cancer models, materials and carbon.
  - **Area note.** Energy has no item in the strict top 5. Ranks 4–7 are a statistical tie, so if the owner wants
    every area in wave 1, swap K2 (0.765) for E1 (0.735). We recommend the strict ranking and let the owner decide.
- **Wave 2:** M2, E1, K3, E2, E3. Also K2 if it was swapped out.
- **Deferred (wave 3):** C2, C3. Both start only after a human reader with radiotherapy or mathematical-oncology
  background has read the wording rules in section 6. This needs the owner's decision.
- **Scheduling.**
  - Wave 1 lanes are pinned to disjoint cores. If A1 resumes on 0–5, wave 1 runs serially on 6–7, in this order:
    1. K1 and K2 (light);
    2. C1 (exact solves);
    3. M1;
    4. M3 (heaviest Lean).
  - If A1 stays paused, C1 and M3 may take two cores each.
  - Heavy Lean builds must not overlap the A1 scheduler's disk-2 I/O. Warm the Mathlib oleans first (the cold-cache
    lesson).

## 5. The loop (Karpathy-style, time-boxed, keep or discard by a verifiable gate)

1. **Preregister** (this file plus the JSON, hashed) before any attempt. Changes after the first attempt go into a
   dated amendment, never into this file.
2. **Budgets.** Each statement gets a budget of about 4 agent-hours or 24 wall-clock hours, at most two budgets.
   Agents use `results.tsv` rows: id, attempt, gate, verdict.
3. **The gate.** It decides keep or discard; no human or AI judgement is involved.
   - **Lean items.** `lean_runner.py` compile plus `#print axioms` within the whitelist, no `sorry`, statement lock
     unchanged, and planted controls (in separate `*Controls.lean` files) caught.
   - **Certified-numeric items.** The enclosure excludes the threshold, the negative control is rejected, and an
     independent implementation agrees.
   - **Audit items (K1, M2).** The positive control reproduces the published numbers to the printed digits before any
     finding is counted.
4. **Keep / discard.** Keep only gate passes. Record discards with the reason; they feed the negative-results
   sections.
5. **Producer ≠ verifier.** Every kept Tier A row is recompiled by an independent Opus agent from a clean checkout
   (leanchecker replay), never by a cheaper tier than the producer. Every Tier C argument (K1(b), M3 reductions,
   C3) gets an adversarial Opus audit.
6. **Workflow hygiene.** Every agent prompt carries a TASK SCOPE preface; this is the prompt-leak lesson of
   2026-10-25. Agents never commit or push; the owner does.

**Model tiers by stage.**
- Opus: proofs, certificate design, statement fidelity, audits.
- Sonnet: numerics, data pipelines, papers, revisions.
- Haiku or local DeepSeek-Prover: short concrete Lean goals, judged only by the kernel.

## 6. What this programme will NOT claim

- **No cure, no treatment advice, no medical evidence.** C1–C3 are about mathematical models of cell populations.
  No schedule, dose or strategy is recommended. No patient data is used. No model here is validated against clinical
  outcomes.
- **No climate effect.** K1–K3 bound quantities inside thermodynamic, equilibrium-chemistry or linear-response
  models. They do not estimate tonnes removed, warming avoided, or the safety of any deployment.
- **No device performance.** E1–E3 and M1–M3 are about model plasmas, model cells, model engines and model crystals.
  - No claim that a fusion device ignites.
  - No claim that a battery charges faster.
  - No claim that a material is synthesisable or stable in the laboratory.
- **Models are not reality.** A Tier A theorem certifies a Lean statement about a model with stated parameters, not
  its physical meaning. Tier X numerics never support a claim alone.
- **Not "proved" when only the finite part is checked.** This applies to M3 especially: the analytic reductions stay
  Tier C unless audited.
- **No credit taken for others' theorems.** Reproductions and independent checks are labelled as such. Discrepancies
  go to the original authors first (owner's decision), after a second independent check.

## 7. Ethics and safety

- **Public data only.** JARVIS-DFT, NIST DAC dataset, Joos IRF, PyBaMM parameters, Jessen et al. Dataverse,
  published fit coefficients. Each licence is checked and recorded before download; anything unclear is marked
  "licence to verify" and not redistributed.
- **No patient data and no human-subject data**, of any kind.
- **No dual-use detail.**
  - E1 stays at textbook 0D magnetic-confinement power balance. It contains no inertial-confinement target design,
    no burn-propagation or yield modelling, and nothing beyond what Wurzel–Hsu and Ochs–Fisch publish.
  - No toxicity, synthesis or weaponisation content in materials or chemistry.
- **No deployment advocacy** for OAE, EW or DAC; ecological risks are out of scope and said so.
- **AI disclosure.** Every paper states that AI agents drafted and checked it, and that no human expert reviewed it
  unless one did. LEDGER_UNAUDITED_TIER_A flags are printed, not hidden.

## 8. Publication plan (as in previous rounds)

- **Gate before any paper.** Ledger gate with 0 blocking findings, an independent Opus audit that is not REJECT, the
  revision applied, Lean controls caught, and a result remaining. Negative results are published:
  - "no dB amplifier of weak selection for N ≤ 10";
  - "'start cold' survives exergy accounting";
  - "certificate width insufficient".
- **Zenodo.** One CC-BY-4.0 preprint per kept item, with a "Publication decision" paragraph when Tier A rows are
  not human-audited. Use `scripts/zenodo_new_version.py` for versions, plus the anonymous read-back check. Publishing
  is the owner's decision per item.
- **Code.**
  - rusty-SUNDIALS crates (squash PRs, branch per lane):
    - `qf-popgen` extension for C1/C3;
    - a new `qf-carbonate` for K2;
    - a new `qf-spm-battery` for E2;
    - `qf-yukawa-crystal` extension for M1/M3.
  - LeanFlow certificate templates (PD/LDLᵀ for M2; exp enclosures for M3).
  - Genetic repository for the C1 Lean (Programmes/EvoGraph).
  - The Elenchus registry in NewDiscoveries.
- **Outreach.**
  - Human red-team calls for M3 (crystallisation community) and C1 (evolutionary graph theory).
  - Author contact for M3 and K1 before publication, if a discrepancy appears. The owner decides.

## 9. References actually opened in this session

Opened via alphaXiv; "abstract" means the arXiv abstract only:

**Energy**
- Wurzel & Hsu 2021, 2105.10954
- Ochs & Fisch 2023, 2310.18508
- Kolmes, Ochs, Fisch 2022, 2211.17143 (abstract)
- Marquis et al. 2019, 1905.12553
- Holubec & Ryabov 2016, 1603.02551
- Ma, Xu, Dong, Sun 2018, 1802.09806
- Ye & Holubec 2021, 2112.08923

**Cancer models**
- Kaveh, Komarova, Kohandel 2014, 1411.4556
- Hindersin & Traulsen 2015, 1504.03832
- Tkadlec et al. 2019, 1906.02785
- Richter 2020, 2008.01446
- Richter 2022, 2204.12861 (abstract)
- Bortfeld et al., 1312.1332
- Alvarez & Viossat 2022, 2211.17041
- West et al. 2022, 2210.12062 (abstract)

**Materials**
- Luo & Wei 2026, 2610.31456
- Mouhat & Coudert 2014, 1410.0065
- Choudhary et al. 2020, 2007.01831
- Zhou, Tang, Yu 2023, 2306.01456
- Qi et al. 2026, 2601.19603 (abstract)

**Carbon**
- McDannald et al. 2025, 2501.04825 (main text; supplement not read)
- Jessen et al. 2026, 2607.01835
- Beerling et al. 2023, 2307.05343 (abstract)
- Seshadri 2015/16, 1502.00805
- Joos et al. 2013, ACP 13, 2793 (landing page only)

Everything else cited above is marked **not read** where it appears.
