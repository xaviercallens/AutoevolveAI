# Research directions: mathematics discovery for public benefit (2026-11-11)

Status: proposal by the AI assistant, not started, not audited. Success chances are rough estimates by the
author, not measurements. Every item follows the Elenchus rules (section 1). Nothing here is a result.

## 0. Why these directions

The programme's strength is narrow and real: **exact, machine-checkable statements** (rational certificates, interval
enclosures, Lean theorems with the three standard axioms, exhaustive finite searches). Its weakness is also measured:
in the week of 8-11 November, one item of four produced something new (the n = 63 shifted lonely runner
counterexample, doi:10.5281/zenodo.24051700); one was a 1956 theorem, two were solver-limited negatives. So each
direction below is chosen for three properties:

1. the answer can be **checked by anyone cheaply**, even if finding it is expensive;
2. a public-benefit field (energy, materials, physics optimisation, genetics, oncology) **uses the statement as an
   input**, so an exact version or a found error has value;
3. prior art can be screened in a day, before any compute.

What mathematics can honestly offer these fields is not cures or devices. It is **trust in the numbers and bounds
that engineers and biologists already rely on**, plus occasional new optimal configurations and counterexamples.

## 1. Rules (unchanged)

Prior-art search before compute. Hashed preregistration before any run. Positive and negative controls. Producer and
verifier are different agents; the verifier writes its own checker. Tiers: A kernel-checked, L literature, C
computed-and-audited, X negative or inconclusive. Negative and not-new results are recorded. No human audit unless
stated. Never "breakthrough" or "solved". Lean through the pinned runner with the axiom whitelist; number theory
through PARI/Sage. Oncology and medicine: section 6 adds stricter rules.

## 2. Energy

| ID | Direction | Checkable deliverable | First item | Kill criterion | Chance |
|---|---|---|---|---|---|
| EN-1 | **Certified fusion operating windows.** Ignition and burn conditions (Lawson-type inequalities, D-T reactivity fits, power balance with bremsstrahlung) as rigorous interval enclosures instead of plotted curves. Builds on E1 and the rusty-SUNDIALS work. | Enclosures of the ignition boundary n·τ·T over a temperature range, with the reactivity fit and its stated error carried through; Lean statement for the algebraic core. | Re-derive one published ignition curve with certified error bars; report where the published figure is inside or outside the enclosure. | The reactivity data's own uncertainty swamps the numerical error (then the result is "numerics are not the bottleneck", Tier X). | 0.5 |
| EN-2 | **Battery diffusion bounds.** Closed forms and bounds in single-particle and porous-electrode models (Sand's time, limiting current, diffusion-limited capacity). | Exact recheck of published closed forms; certified enclosures of the PDE solution for stated parameters; any discrepancy reported to the authors' public tracker. | One widely used closed form, rechecked symbolically and by validated numerics. | The form is textbook and correct to all digits (record as verified, do not publish as discovery). | 0.4 |
| EN-3 | **Exactness certificates for power-flow relaxations.** Convex relaxations of optimal power flow are used to plan grids; exactness is proved only under conditions. | For public small test networks: a rational certificate that the relaxation is exact, or an explicit gap instance. | The smallest public radial and meshed cases. | Known theory already decides every case tried. | 0.35 |
| EN-4 | **Energy cost of computation.** Follow-up of the TokWatt recheck: exact accounting identities for inference energy, including citizen-compute settings. | Recomputed tables with exact arithmetic and stated assumptions. | The plan's ENE-TOKWATT item. | Source tables not reproducible from the paper. | 0.6 |

## 3. New materials

| ID | Direction | Checkable deliverable | First item | Kill criterion | Chance |
|---|---|---|---|---|---|
| MA-1 | **Optimal lattices in three dimensions.** Our 2D results (triangular lattice optimal for Riesz, Yukawa and Gaussian families, kernel-checked) do not carry over: in 3D the minimiser changes between FCC and BCC with the interaction range. | Certified enclosures of lattice energies and of the **crossover parameter** where FCC and BCC exchange for Yukawa and Gaussian interactions, among lattices of fixed density; statement in Lean for the comparison at fixed parameters. | The Yukawa FCC/BCC crossover as a certified interval (the 3D feasibility study B3 is the starting point). | The crossover is already published to more digits with rigorous error control. | 0.5 |
| MA-2 | **Exact audits of public materials databases.** Elastic tensors must satisfy Born stability and crystal symmetry; band gaps and formation energies must be internally consistent. | Per-database counts of entries violating exact necessary conditions, split by the database's own warning flags; neutral issue reports upstream (as done for JARVIS). | The plan's MAT-MPBORN item, then a second database. | Licence forbids redistribution of the needed fields (then publish method and counts only). | 0.7 |
| MA-3 | **Certified packing and covering bounds relevant to porous and granular matter.** Linear-programming bounds with exact rational dual certificates. | Kernel-checked replays of known bounds; small improvements where the LP is not yet optimised. | One dimension/angle where the published bound has no public certificate. | Bound already has a formal proof. | 0.3 |

## 4. Physics optimisation

| ID | Direction | Checkable deliverable | First item | Kill criterion | Chance |
|---|---|---|---|---|---|
| PH-1 | **Quantum corrections to classical optimality.** QU-1 was refuted numerically (zero-point energy does not preserve triangular optimality everywhere); the triangular-to-rhombic transition (B1) is open in certified form. | Certified interval for the transition parameter; Lean statement at parameters on each side. | Certify the sign of the energy difference at two parameters bracketing the transition. | Enclosures too wide to separate the phases at feasible cost. | 0.4 |
| PH-2 | **Validated integration for stiff models.** CVODE solutions are used in plasma, combustion and N-body work without error certificates. | For benchmark stiff systems: a validated enclosure of the solution next to the CVODE output, with the first time the solver's reported tolerance is violated, if any. | Robertson and one plasma benchmark from rusty-SUNDIALS. | Enclosure methods blow up before the time of interest. | 0.5 |
| PH-3 | **Certified cosmology, continued.** P1-P3 certified BAO enclosures and an exclusion statement. | Extend to one more public dataset with the same certificates. | A dataset with a public covariance matrix. | No public covariance. | 0.5 |
| PH-4 | **Extremal problems with finite certificates.** The shifted lonely runner line: n = 63 found; other n in 39..94 undecided by solver search. | A structural argument (why N = 64 is special: it uses 128 = 2N and powers of 3) turned into either a second family or an impossibility lemma for the template. | Pen-and-paper analysis of the template, then a targeted search. | No structure after one audit-sized effort (more solver time is not the answer). | 0.15 |

## 5. Genetics

| ID | Direction | Checkable deliverable | First item | Kill criterion | Chance |
|---|---|---|---|---|---|
| GE-1 | **Exact fixation on population structures.** Whether a spatial structure amplifies or suppresses selection (Moran process on graphs) matters for tissue architecture and for somatic evolution. | Exact rational fixation probabilities for all small graphs under stated update rules; a census of amplifiers and suppressors with certificates; Lean proof of the general identity used. | Screen the existing censuses, then extend one update rule or one size. | The census at reachable sizes is already published. | 0.35 |
| GE-2 | **Multistationarity census of small reaction networks.** BIO-BISTAB rechecked Peng's classification (arXiv:2610.32739) of 681 two-species networks (27 bistable); the classification is Peng's, not ours. Bistability is the mathematical core of genetic switches. | Three-species or higher-molecularity census with algebraic certificates (exact steady states, sign conditions). | Fix the class and prove completeness of the enumeration. | Enumeration explodes beyond what exact algebra can handle. | 0.5 |
| GE-3 | **Structural identifiability certificates.** Many published gene-regulation and compartment models have parameters that no data can determine. | For named public models: exact algebraic verdict (identifiable or not) with the certificate, compared with what the paper assumes. | The plan's BIO-R0 class of models. | Verdicts already published by identifiability tools for the same models. | 0.5 |

## 6. Oncology (mathematical models only)

Stricter rules: statements are about **equations**, never about patients. No doses, schedules, or treatment advice.
Each item names its assumptions in the title. **Nothing is published before a human medical reader has read it**;
C2 and C3 are on hold for that reason and stay on hold.

| ID | Direction | Checkable deliverable | Status | Chance |
|---|---|---|---|---|
| ON-1 | **Fractionation theorems in the linear-quadratic model** (C2), in Lean. | Kernel-checked statements with the model's assumptions explicit. | ON HOLD for the human reader. | n/a |
| ON-2 | **Containment versus maximum-tolerated-dose comparison principle** (C3), in Lean. | Kernel-checked comparison theorem for the stated competition model. | ON HOLD for the human reader. | n/a |
| ON-3 | **Exact resistance probabilities in branching-process models.** Probability that a resistant clone exists at detection (Luria-Delbrück type). | Exact generating-function identities and certified bounds; recheck of published closed forms. | Can be prepared; publication waits for the reader. | 0.5 |
| ON-4 | **Identifiability of tumour-growth laws.** Whether exponential, logistic, Gompertz and von Bertalanffy laws can be told apart from the data designs used in the literature. | Exact identifiability and distinguishability verdicts per design. | Can be prepared; publication waits for the reader. | 0.5 |

## 7. Link with citizen compute

Searches of the kind used for n = 63 are expensive to run and cheap to verify: a certificate found on any volunteer
machine is checked exactly in seconds, and by the Lean kernel in under an hour. That matches the manifesto's
requirement of rejecting bad results without recomputing them. Proposed, **not implemented**: package exact searches
(CP-SAT pools, lattice-energy enclosures, graph censuses) as volunteer work units whose only accepted output is a
certificate that passes the public checker.

## 8. Order of work

**Update, 2026-11-11 (prior-art screen, `results/proposal7/2026-11-11/MA1/PRIOR_ART.md`): MA-1 is NOT NEW.**
Luo-Wei (arXiv:2610.31456, unrefereed) state a computer-assisted proof that among all 3D lattices at unit covolume
BCC minimises the Yukawa energy below a single crossover and FCC above it, with the crossover enclosed to 15 digits;
Luo-Wei (arXiv:2609.17356) settle the Gaussian case, where the crossover is exact by duality. The scout read the
theorem statements, not the proofs, and did not run their certificates. MA-1 ends with this record; no compute was run.
The chance estimate of 0.5 in section 3 was wrong.

**Update, 2026-11-11 (`results/proposal7/2026-11-11/EN1/PRIOR_ART.md`): EN-1 is NOT NEW, and the duplicate is our own.**
Our published E1 (papers/p4_pb_ignition, doi:10.5281/zenodo.23733098) already gives interval enclosures of the D-T
ideal ignition temperature and of the minima of n·T·τ and n·τ for the Wurzel-Hsu model. Propagating the reactivity
fit error would only widen those intervals by the fit error, which is the kill criterion written in section 2. The
author of this document proposed EN-1 without checking our own record; that was an error. Possible small add-ons
(a Lean unimodality lemma, a check against the Bosch-Hale primary source, which E1 never obtained) belong in an E1
version 2, not in a new item. No compute was run.

**Update, 2026-11-11: GE-2 was done and published** as a partial census, doi:10.5281/zenodo.24131124.

1. **MA-1** (3D lattice crossover): largest reuse of our kernel-checked 2D work; a certified crossover is a usable number.
2. **GE-2** (reaction-network census): extends an audited result; exact algebra; relevant to genetic switches.
3. **EN-1** (fusion windows): reuses E1 and the solver work; clear deliverable.
4. **MA-2**, **PH-2**, **GE-3** as low-risk rechecks between the larger items.
5. **PH-4** only as a pen-and-paper structural study; no more blind solver time.
6. Oncology items are prepared but not published until the human reader has read C2 and C3.

Each start needs the owner's spend check (weekly meter) and a one-day prior-art screen; a screen that returns
"known" ends the item with a record, as for the K3 follow-up.
