# FACTS: binding fact sheet for the textbook "De la conjecture au noyau Lean" (2026)

Every chapter writer MUST take numbers, theorem names, DOIs and tiers from here, or from the primary record files
listed, and nowhere else. If a number is not here or in a listed file, do not use it.

## Audience, language and conventions
- **Audience.** French CPGE (Math Sup / Math Spé, MPSI/MP2I, MP/MPI) and engineering-school students.
- **Language.** French. Lean names and code stay in English. Mathematical level: real analysis, linear algebra, finite
  Markov chains, basic Fourier series; Fourier/Laplace transforms are introduced when needed.
- **Tiers (Elenchus):**
  - **A**: kernel-checked Lean. The gate is the axiom list within {propext, Classical.choice, Quot.sound}, plus a
    kernel replay (`leanchecker`), plus a grep for `skipKernelTC`/`addDecl`/`native_decide`/`implemented_by`.
    `#print axioms` alone can be fooled by `debug.skipKernelTC`, as the A2 audit found.
  - **L**: cited literature, read and pinned.
  - **C**: a human argument not machine-checked.
  - **X**: floating-point exploration; it never supports a claim.
- **Honesty rules.**
  - Everything built on openai/math is conditional on upstream theorems, which are AI-generated and not peer reviewed.
  - Every result here was produced by AI agents (Claude) under the author's direction and audited by a separate AI agent.
  - No human has audited the results.
  - Never write "breakthrough", and never claim a conjecture proved beyond its tier.
- **Author.** Xavier Callens (SocrateAI Lab), with the AI disclosure. Dedication: "À Ilene, Alexis et Aurelia".

## The story (natural flow of the formalizations)
1. **Upstream (Tier L/A-conditional).** openai/math proves in Lean 4 that the triangular lattice A minimizes the lower
   energy among locally finite density-one configurations, for every smooth completely monotone (CM) potential
   g(r²) (`universal_energy_minimum`; Cohn–Kumar–Miller–Radchenko–Viazovska, Annals 2022, proved dimensions 8 and 24).
2. **Our corollaries (Tier A, conditional on 1).**
   - D1: Riesz r^{-s}.
   - D2: every density.
   - D3: CKMRV sense, and non-uniqueness via a vacancy.
   - D4: open vs closed disks.
   - Published: textbook v1, doi:10.5281/zenodo.23295142.
3. **Five physical potentials (autoresearch 2026-10-25), each Tier A unless noted:**
   - Dipolar excitons 2(1/r − 1/√(r²+d²)): doi:10.5281/zenodo.23646103.
   - Planar Yukawa e^{−κr}/r: doi:10.5281/zenodo.23646105.
   - Rytova–Keldysh (TMD): a Laplace mixture is admissible (Tier A); the link to the Struve form is Tier C.
     doi:10.5281/zenodo.23646107.
   - σ = 3 shell-model enstrophy bound: doi:10.5281/zenodo.23646111.
   - Bogoliubov S(k) ≤ √(k/2k*): doi:10.5281/zenodo.23646117.
4. **The CM/Bernstein library (P3, Tier A).** CM ∘ Bernstein is CM (subordination), and the CM definition is
   equivalent to upstream's AdmissiblePotential. doi:10.5281/zenodo.23653842.
5. **The quantum surprise (P2, then B2, B1).**
   - The zero-point conjecture QU-1 fails numerically for 8 of 12 CM potentials (Tier X). For Gaussians
     exp(−π a r²) with a ∈ (0.37668, 1.58148), the triangular lattice is a local MAXIMUM of the harmonic zero-point
     energy. doi:10.5281/zenodo.23653833.
   - B2 certified it at a = 1: not a local minimum along a symmetric shear. Lean holds the logic and rational
     certificate; the ball-arithmetic integrals are Tier C-ball; U''(0) ∈ [−1.948, −1.900]. doi:10.5281/zenodo.23655392.
   - B1: there is no physical triangular → oblique transition within SCHA, because quantum melting comes first;
     negative result. doi:10.5281/zenodo.23655625.
6. **Sandier–Serfaty (Abrikosov lattices).**
   - The openai/math preprint claims a proof (AI-generated, not peer reviewed).
   - P1 reproduced its interval certificate in 478 s and audited the reduction with no gap found (Tier C). The Lean
     statement is locked. doi:10.5281/zenodo.23653827.
   - A1 ported 4/12 stages at L1 (kernel re-execution, bit for bit) and 1/12 at L2 (real-number statement), and proved
     the reduction lemma `signed_endpoints`. This is NOT a proof of the conjecture. doi:10.5281/zenodo.23656804.
   - B3: the method does not extend as stated to 3D bcc (negative result). doi:10.5281/zenodo.23655002.
7. **Navier–Stokes (A2).**
   - The openai/NavierStokesAndEuler corpus was independently rebuilt (2,440 modules) and kernel-replayed (53,752 +
     34,648 declarations). The axioms are on the whitelist, no soundness escape was found, and the statements are
     faithful to Clay alternative (C).
   - Published, independently audited (ACCEPT_WITH_CORRECTIONS): doi:10.5281/zenodo.23661381. Never claim "Clay
     solved". The credit belongs to the corpus authors.
8. **Population genetics.**
   - H11/H12: Wright–Fisher harmonic characterisation and diploid mean-fitness monotonicity.
   - P7: Pⁿ(i,N) → i/N; Moran with selection gives fixation (1 − r^{−i})/(1 − r^{−N}); the Price equation.
     doi:10.5281/zenodo.23653850.
   - N4: the isothermal theorem (birth–death), with forward bias P⁺ = r·P⁻ per configuration. The count is not
     strongly lumpable (4-cycle: 1/3 vs 2/3). Star n = 3: 5/12, 2/3, 7/12 against Moran's 4/7.
     doi:10.5281/zenodo.23660071.

## Primary records (read these for details and numbers)
- Our papers: `papers/` in the worktree /home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery:
  - autoresearch: `ar_dipolar_exciton`, `ar_yukawa_crystal`, `ar_keldysh_tmd`, `ar_sigma3_enstrophy`, `ar_bogoliubov_sk`;
  - programmes: `prog_sandier_serfaty_audit`, `prog_zero_point_optimality`, `prog_cm_bernstein_library`,
    `prog_superfluid_structure_factor`, `prog_population_genetics_fixation`;
  - proposal 2: `p2_certified_zero_point`, `p2_quantum_transition`, `p2_3d_feasibility`, `p2_sandier_serfaty_lean`;
  - proposal 3: `p3_isothermal_theorem`;
  - the textbook v1: `textbook_universal_optimality`.
- Records: `results/autoresearch/2026-10-25/`, `results/programmes/2026-10-25/`, `results/proposal2/2026-10-26/`,
  `results/proposal3/2026-10-26/`.
- Lean: `formal_cert/Triangular/`, `formal_cert/Autoresearch/`, `formal_cert/Programmes/`.
- Numerics:
  - rusty-SUNDIALS worktrees `~/rusty-SUNDIALS-wt-*` (merged crates: qf-yukawa-crystal with dipolar/exact/keldysh,
    qf-shell-cascade sigma, qf-gpe2d linear_response);
  - P2 phonons and SCHA in `~/rusty-SUNDIALS-wt-p2`;
  - P7 `qf-popgen` in `~/rusty-SUNDIALS-wt-p7`.
- LeanFlow: `~/LeanFlow-wt-p1`, the fail-closed `lean.*` data certificates (`decide_kernel`).
- Hugging Face datasets used so far (check each paper's data provenance section):
  - JARVIS-DFT interlayer spacing (H1);
  - OC20 (H2);
  - The Well, turbulence (H7);
  - none exists for S(k) (H8/P6, which used tabulated Donnelly–Barenghi data);
  - the Genetic repo's `katarinagresova/Genomic_Benchmarks_*`.
- Other GitHub repos: SocrateAI-Scientific-Genetic (`formal/ANSE/AlixPopulationGenetics.lean`, PRs #1–#3),
  SocrateAI-Scientific-Agora-LeanMaster (contrib v3.49.0), rusty-SUNDIALS, SocrateAI-Scientific-Agora-LeanFlow.

## The family Easter eggs (Lean file `formal_cert/Programmes/Famille/Acronymes.lean`)
Real Lean theorems re-exporting existing kernel-checked results under acronym names, each with a backronym docstring.
The final names and backronyms are set by the Lean agent and listed in `Acronymes.md`. Chapters reference them once,
lightly, where the underlying result appears, without explaining the family meaning; the dedication page carries it.
