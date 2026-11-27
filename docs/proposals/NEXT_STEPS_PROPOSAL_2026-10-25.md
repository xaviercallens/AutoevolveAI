# What comes next: natural steps from the seven 2026-10-25 results

**Author:** Xavier Callens (SocrateAI Lab). Drafted with AI agents (Claude).
**Status:** proposal, nothing attempted yet.
**Calibration:** each programme gets a probability of success for a ~1-month effort and an honest value rating.
Neither the probability nor the rating claims a breakthrough.

## 1. Where we stand

| # | Result | What it really is |
|---|---|---|
| H1 | Bilayer dipolar excitons: 2(1/r − 1/√(r²+d²)) is completely monotone (CM) in r², so the triangular lattice is optimal at every density | A new kernel-checked corollary; the CM step is elementary |
| H2 | Planar Yukawa e^{−κr}/r, and mixtures of screening lengths | A corollary plus a reusable product-closure lemma |
| H3 | Rytova–Keldysh (TMD screening) is a positive Gaussian mixture; Laplace-mixture ⇒ admissible is in Lean | A corollary; the Struve-function link is Tier C; the raw energy is ∞ (only the jellium version is physical) |
| H7 | σ = 3 dyadic shell model: an enstrophy bound independent of the cutoff | A specialization of the owner's lemma, plus a conservation identity |
| H8 | Bogoliubov S(k) ≤ √(k/2k*), equality iff k = k*, with shape theorems | Elementary algebra and a diffraction test; no data yet |
| H11 | Neutral Wright–Fisher: i/N is the unique harmonic function | A known result; the probability link is not formalized |
| H12 | One-locus, two-allele mean-fitness monotonicity | A known result |

**The common thread.** H1–H3 all use the same mechanism. A pair potential that is a positive mixture of Gaussians in
r² inherits the triangular lattice's universal optimality (Cohn–Kumar, proved upstream in openai/math). What we built
is the toolkit for showing that physical potentials belong to that class. The real limits of this method are:
1. long-range interactions (Coulomb, Keldysh), where only *renormalized* (jellium) energies make sense;
2. quantum effects (zero-point motion), which the classical theorem ignores;
3. other dimensions;
4. biology, where the "potentials" are fitness landscapes and there is no energy at all.

Each programme below pushes one of these limits.

## 2. The programmes, ranked

### P1 (flagship): verify, then formalize, the claimed proof of the Sandier–Serfaty conjecture
- **The claim.** openai/math contains a preprint, *Triangular minimality for planar Coulomb renormalized energy*
  (Sept 2026), which states: "We prove the Sandier–Serfaty conjecture: the triangular lattice of covolume one
  minimizes planar Coulomb renormalized energy over all admissible curl-free fields with a unit uniform background."
  Through Bétermin–Sandier it also gives the Brauchart–Hardin–Saff conjecture for log-energy points on the sphere.
- **How it is proved.** A Voronoi-cell comparison plus a finite interval-arithmetic certificate (316 lines of C++).
- **What is missing.** Upstream has no Lean formalization. Outside upstream, the literature still lists the
  conjecture as open (alphaXiv check, 2026-10-25). The proof is AI-generated and not peer reviewed.
- **Why it is the natural next step.** It is exactly the "renormalized energy" wall we hit in H3, in the jellium
  section of the textbook and in the jellium CVODE study. Sandier and Serfaty introduced this energy for
  **Abrikosov vortex lattices** in Ginzburg–Landau superconductors.
- **Steps, each a separate preregistered experiment:**
  1. **Reproduce.** Run the certificate independently on our hardware. The negative control is a deliberately
     loosened analytic bound, which must make the certificate fail. Prior **0.75**.
  2. **Adversarial audit of the reduction.** Read Sections 2–5 step by step: reduction to Voronoi cells, geometry,
     calibration, tails. Does each bound the certificate assumes actually hold? Producer ≠ verifier, and a human
     expert is invited (Reddit/Zulip red team). Prior of finding a fatal gap: **~0.25**; the prior of a clean audit
     is the rest.
  3. **Lean statement first.** State the conjecture in Lean against Mathlib's distributions and fields, the way
     Comparator challenges do, and lock it. Prior **0.40**. A faithful statement is valuable on its own.
  4. **Port the finite certificate to Lean.** Use our certified-numerics stack, which already kernel-checked DESI
     BAO interval enclosures. Prior **0.30** for the finite part.
  5. **Formalize the analytic reduction.** Prior **0.10** in a month; this is a multi-month effort.
- **Value.** Even steps 1–3 would be the first independent check of a claimed resolution of a famous conjecture.
  Steps 4–5 would make it one of the few machine-checked results in Ginzburg–Landau theory.
- **For humanity:** superconductor vortex physics (Abrikosov lattices, flux pinning in MRI magnets and fusion coils),
  rotating Bose–Einstein condensates (our QuantumFluids work), and well-spread points on the sphere (numerical
  integration, sampling on climate grids).

### P2 (new conjecture, ours): quantum universal optimality, the zero-point version of Cohn–Kumar
- **Conjecture QU-1.** For every admissible (CM) pair potential g, among planar Bravais lattices of unit covolume, the
  triangular lattice minimizes the harmonic zero-point energy E_zp(L) = ½ Σ_k Σ_branches ħω_L(k), and hence also
  E_classical + E_zp.
- **QU-2 (hard).** The same among all periodic configurations.
- **Novelty.** An alphaXiv search found no such statement, only harmonic-stability analyses and Lennard-Jones
  lattice results. Novelty is unconfirmed until a deeper search.
- **Why it is natural.**
  - H8 (Bogoliubov), the textbook's quantum-melting section and H1/H3 (exciton and TMD Wigner crystals) all point
    to systems where quantum motion matters.
  - For Gaussian potentials, the phonon dynamical matrix is built from derivatives of lattice theta functions. That is
    exactly the object behind Montgomery's 1988 lattice theorem.
- **Steps:**
  1. **Falsification gate.** A rusty-SUNDIALS phonon code computes E_zp over the fundamental domain of lattice shapes
     for Gaussian, Yukawa, dipolar and Riesz potentials, with Ewald for long range. Find a counterexample or
     confirm. Prior that the conjecture survives: **0.6**.
  2. **Human proof among lattices for Gaussian g**, via theta-function convexity (Montgomery-type). Prior **0.15**.
  3. **Lean formalization** of whatever is proved.
- **Value:** a genuinely new theorem if proved, even restricted to lattices.
- **For humanity:** quantum materials. This covers Wigner crystals in 2D semiconductors, exciton crystals for
  optoelectronics, and the design of quantum simulators.

### P3 (infrastructure): a Lean library of completely monotone and Bernstein functions
- **What to build.** Turn the H1–H3 toolkit into a clean library:
  - closure under products, positive combinations and limits;
  - composition of a CM function with a Bernstein function (subordination);
  - Laplace and Stieltjes mixtures;
  - Bernstein–Widder in both directions (upstream proves one direction internally);
  - Fourier criteria (a CM 2D Fourier transform in k² implies CM in r², the Keldysh argument).
- **Payoff.** One theorem per physical potential becomes a one-line corollary: screened multipoles, Keldysh, mixtures,
  dipolar in any geometry.
- **Prior 0.6.** Target: a Mathlib PR, which gets human review from Mathlib maintainers. That partly answers our
  "no human audit" gap.
- **Value:** high reuse. It enables P2 and P4.

### P4: three dimensions, where real crystals live
- **Background.** In 3D there is no universal optimum: fcc and bcc trade places. October 2026 preprints prove bcc
  optimality for Coulomb among 3D lattices (arXiv 2610.29732) and exact Yukawa bcc→fcc transitions (2610.31456).
- **Steps:**
  1. Kernel-check one of these lattice-restricted 3D results with our certified-numerics stack.
  2. Turn our conditional textbook statement "neither fcc nor bcc is universally optimal" into a certified
     inequality: Project U2 at α = 2.
- **Prior:** **0.35** for step 2, **0.15** for step 1.
- **For humanity:** metals, dusty plasmas, ion traps and neutron-star crusts. The bcc/fcc question is the classic
  Yukawa phase diagram.

### P5: turbulence, from a uniform bound to global existence
- **Background.** H7 gives an enstrophy bound for the σ = 3 shell model that is uniform in the cutoff and conserved
  along the flow.
- **Next step.** A Galerkin compactness argument: global smooth solutions of the infinite-dimensional σ = 3 model.
- **Contrast.** Dyadic Euler models blow up (Katz–Pavlović), and the openai/NavierStokesAndEuler corpus claims blow-up
  for forced Navier–Stokes. H9 found its statement faithful to Clay alternative (C), but that was a statement-only
  audit. So the question becomes which mechanism, dispersion with σ = 3, prevents blow-up.
- **Steps:**
  1. A human proof of global existence for the shell model. Prior **0.3**.
  2. In parallel, run H9's second fidelity audit and rebuild the NS corpus with `#print axioms`. Prior 0.7 to finish
     the audit.
- **Value:** moderate, since shell models are toy models. H9 has high stakes and must stay strictly
  statement-honest.

### P6: confront the superfluid diffraction test with real data
- **Data.** H8 made a falsifiable prediction but had no data: no Hugging Face dataset holds S(k). Collect published
  tables:
  - neutron and X-ray S(k) of ⁴He (Svensson et al.; Robkoff–Hallock);
  - Bragg-spectroscopy S(k) of BECs (Steinhauer et al.).
  Pin each source with page and line, as Tier L.
- **The test.** Apply S(k) > √(k/2k*) ⇒ "not weakly interacting".
- **Lean.** Formalize the Feynman–Bijl variational bound ε(k) ≤ ħ²k²/(2m S(k)) from the f-sum rule, the
  single-mode bound, in a finite-dimensional Hilbert space with Cauchy–Schwarz. Prior **0.45**.
- **Value:** a clean, citable bridge between a Lean theorem and a laboratory measurement.

### P7: population genetics, from H11/H12 to quantities that matter for medicine
1. **Close the H11 gap.** Prove that the fixation probability equals i/N via Pⁿ(i,N) → i/N or a first-step lemma
   with `ProbabilityTheory.Kernel`. Prior **0.5**.
2. **Moran model with selection.** Fixation probability (1 − r^{−i})/(1 − r^{−N}), kernel-checked. Prior **0.6**.
   This is the standard model for the chance that a **drug-resistance mutation** (antibiotic, antiviral, or a cancer
   clone) takes over a population.
3. **The Price equation** in Lean: an identity, prior **0.8**. Then Fisher's *general* fundamental theorem (the
   additive-variance reading) from it: prior **0.35**.
4. **Stretch:** Kimura's diffusion limit, prior 0.1.

**Value.** The first machine-checked core of mathematical evolution theory, in the owner's Genetic repository. Its
medical relevance comes from (2).

### Cross-cutting: close the "no human audit" gap
- **The gap.** Every Tier A ledger row in the five papers is flagged LEDGER_UNAUDITED_TIER_A.
- **Remedy.** Use the Reddit/Zulip red-team drafts (`docs/outreach/`) and the Mathlib PR from P3 to obtain real human
  statement audits.
- **Why it matters.** This is the cheapest way to raise the credibility of everything above.

## 3. Recommended order (each step preregistered, Karpathy-style keep/discard, kernel as judge)

| Window | Work |
|---|---|
| Weeks 1–2 | P1 steps 1–2 (reproduce + audit Sandier–Serfaty); P3 core closure lemmas; P7 steps 1–2; P6 data collection |
| Weeks 3–4 | P2 falsification gate (phonon code); P1 step 3 (Lean statement); P7 step 3 (Price) |
| Month 2 | P2 step 2 (Gaussian lattice proof attempt); P1 step 4 (certificate in Lean); P4 step 2; P5 step 1 + H9 audit |
| Ongoing | Human audits via community and Mathlib review |

**What would count as a real breakthrough, honestly:**
- **A fully kernel-checked proof of Sandier–Serfaty (P1, all steps):** a landmark verification of a famous
  conjecture's claimed resolution, even though the proof is not ours.
- **A proof of QU-1 (P2), even only among lattices:** a new theorem connecting quantum crystals to universal
  optimality.

Everything else is a solid, publishable contribution, not a breakthrough.

## 4. Risks and kill criteria
- **P1:** if reproduction fails, or the audit finds an unrepaired gap, report that. A refutation of a claimed
  famous-conjecture proof is itself important. Never write "conjecture proved" on our authority.
- **P2:** a numerical counterexample kills QU-1 (and is publishable). If the Gaussian proof attempt stalls after two
  budgets, keep the conjecture at Tier C with its numerical evidence.
- **All:** conditionality on upstream AI-generated theorems must be stated everywhere. Disk 2 I/O limits Lean builds
  (see the memory note); schedule heavy builds at night on 2 cores.
