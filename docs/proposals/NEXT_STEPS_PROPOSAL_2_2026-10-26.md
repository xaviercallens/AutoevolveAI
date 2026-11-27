# Proposal 2: from contributions to landmark results (2026-10-26)

This builds on proposal 1 (`NEXT_STEPS_PROPOSAL_2026-10-25.md`) and on the ten papers it produced. It is a proposal:
nothing in it has been attempted. Priors are calibrated judgments for the stated time box, not promises.

## What the last round changed

- **Our method works on claimed landmark results (P1).** We reproduced the Sandier–Serfaty interval certificate,
  rejected a loosened negative control, and audited the reduction step by step without finding a gap at the stated
  depth. A preprint's claim to settle a famous conjecture was brought one tier closer to trust.
- **Natural conjectures can fail, and we can catch it (P2).** The zero-point version of Cohn–Kumar fails. For some
  Gaussians the triangular lattice is a local *maximum* of zero-point energy, which is a genuine surprise.
- **The infrastructure now exists.**
  - Completely monotone and Bernstein functions in Lean (P3).
  - Fail-closed Lean data certificates in LeanFlow (P1).
  - Certified interval enclosures, from the earlier DESI work.
  - Kernel-checked fixation and Price results (P7).

The natural escalation has two fronts:
1. **Verification:** become the independent trust layer for AI-claimed landmark mathematics.
2. **Discovery:** turn the P2 surprise into a physics prediction that a laboratory can test.

## Front A: verifying AI-claimed landmark results

### A1. A complete machine-checked proof of the Sandier–Serfaty conjecture (P1, steps 4–5)
- **Why it is the logical next step.** Steps 1–3 are done: the certificate reproduced, no gap was found in the
  reduction, and the statement is in Lean. What remains is moving trust from "AI audit" to "Lean kernel".
- **A1a. Port the finite certificate into Lean.**
  - Use LeanFlow `lean.*` plus the certified-numerics interval stack, stage by stage. The record holds 22 printed
    pairs and the mesh stages.
  - Every stage becomes a kernel-checked inequality, and the planted negative-control stages must be rejected.
  - Prior **0.35** in 4–6 weeks. The full mesh may be too large for `decide`, so subdivision certificates will be
    needed.
- **A1b. Formalize the analytic reduction.** This covers Voronoi-cell comparison, calibration and tails, on top of
  the P3 library and Mathlib's measure theory. Prior **0.10** in 2–3 months: it is a large formalization.
- **A1c. Corollaries, once A1a and A1b are done.**
  - Brauchart–Hardin–Saff: the linear term of the optimal logarithmic energy on S², via Bétermin–Sandier.
  - The Sandier–Serfaty link to Ginzburg–Landau: minimizers have triangular (Abrikosov) vortex lattices in the
    stated regime.
- **If it fully succeeds:** a machine-checked resolution of a conjecture open since 2012. It would be, to our
  knowledge, the first for a claimed AI-found proof in mathematical physics. That is landmark-level even though the
  proof is not ours.
- **For humanity:** superconductor vortex physics (MRI and fusion magnets), rotating condensates, and well-spread
  points on the sphere (numerical integration, geoscience grids).
- **Scope note:** this informs Smale's 7th problem but does not solve it.

### A2. Independent rebuild and axiom audit of the claimed Navier–Stokes breakdown proof (the H9 follow-up)
- **Background.** The openai/NavierStokesAndEuler corpus claims a sorry-free Lean proof of `navier_stokes_breakdown_R3`.
  H9 found its statement faithful to Fefferman's Clay alternative (C), with caveats. If the proof is sound, it settles
  the Clay Navier–Stokes problem on the blow-up side.
- **What we do:**
  - Rebuild the corpus ourselves on its rc2 toolchain.
  - Run `#print axioms` on both breakdown theorems.
  - Scan every file the theorem depends on for soundness escapes: `native_decide`, `implemented_by`, `extern`,
    unsafe declarations, `@[csimp]`, macros that could forge output (the lesson from the LeanFlow `#exit` finding),
    and environment hacks.
  - Re-check with an independent kernel checker if one is available (the corpus itself mentions nanoda).
  - Run a second fidelity audit by a different agent, and invite a human red team.
- **Priors:** rebuild plus axiom audit **0.6** in 2–3 weeks (it is heavy on disk 2); the second fidelity audit **0.8**.
- **If it holds:** the first independent machine check of a claimed Millennium Prize resolution. Outcome wording must
  stay strictly "independently rebuilt and audited". The Clay Institute's own process decides the prize.
- **If it fails:** finding the flaw is itself landmark-level and urgent to report.

### A3 (lower priority). Independent audit of the Anthropic FLT corpus
- **What we do:** a rebuild of 60k modules, `#print axioms fermat_last_theorem`, and the same soundness-escape scan.
- **Value:** FLT's statement is easy to check, and that corpus already ran Comparator and nanoda. Our added value is
  lower, but this is a cheap use of the same pipeline once A2 has shaken it out.

## Front B: discovery from the P2 surprise

### B1. A quantum structural phase transition in soft-core crystals
- **Physics.** For a quantum crystal, the energy E(τ) = E_static(τ) + ħ_eff · E_zp(τ) is a sum of two terms.
  - The static term is minimized by the triangular lattice (Cohn–Kumar, upstream).
  - P2 shows that for Gaussians with a ∈ (0.377, 1.581), the zero-point term has a strict local maximum there.
  - So beyond a critical quantum parameter ħ*, the triangular lattice stops being a local minimum: a continuous
    **triangular → rhombic** transition.
- **Prediction.** A structural transition in quantum crystals of soft-core particles before melting, with a
  computable ħ*(a), assuming harmonic theory holds there.
- **Tests, in order:**
  1. Compute ħ*(a) and compare with the Lindemann melting threshold from the textbook's quantum section. Does the
     transition happen before melting?
  2. Go beyond the harmonic approximation: self-consistent phonons, then path-integral Monte Carlo at a few points
     (Tier X, with controls).
  3. Find the experimental platform: **Rydberg-dressed atoms**, whose soft-core interactions are close to the
     Gaussian-core model and are a current quantum-simulation platform. Check against the literature via alphaXiv.
- **Priors:** ħ* below melting **0.4**; survives anharmonic checks **0.25**.
- **If it holds:** a new physics prediction derived from a formal-mathematics result, testable in today's quantum
  simulators.
- **For humanity:** quantum materials and simulators.

### B2. A kernel-checked refutation: the triangular lattice is not a local minimum of E_zp (Gaussian, a = 1)
- **What we do.**
  - The isotropic curvature at the triangular point is a convergent lattice sum. Its sign (negative) can be
    certified with interval arithmetic and the Lean data-certificate generator.
  - The Lean side already has the symmetry lemmas: `ProgZeroPoint`, 19 theorems.
- **Prior 0.4.**
- **Value.** Turns P2's numerical refutation into a Tier A theorem. It shows Cohn–Kumar does not extend to quantum
  zero-point energy, even locally, and it is exactly the input B1 needs.

### B3 (high risk, high reward). Can the Sandier–Serfaty method reach three dimensions?
- **Background.** In 3D, the crystallization question for Coulomb jellium (bcc) among *all* configurations is open
  and notoriously hard. Only lattice-restricted results exist (bcc among Bravais lattices: arXiv 2610.29732, Oct 2026).
- **The question.** The 2D proof's Voronoi-comparison-plus-certificate architecture is new. A feasibility study asks:
  - which steps are dimension-specific;
  - whether a 3D Voronoi comparison bound exists;
  - how large a 3D certificate would be.
- **Prior:** a credible 3D attack plan **0.15**; an actual proof **< 0.02**.
- **Why do it anyway:** a feasibility study is cheap. Even a negative assessment explains why 3D is harder, which is
  useful knowledge.

## Front C: closing the human-trust gap (the condition for any of the above to count)

- Every Tier A row in the ten papers is flagged LEDGER_UNAUDITED_TIER_A. Landmark claims (A1, A2) need human experts.
- **Actions:**
  1. Post the Reddit and Lean Zulip red-team calls (drafts in `docs/outreach/`), adding P1 and P2.
  2. The P3 Mathlib PR, under the author's own name, following Mathlib's disclosure policy.
  3. Contact the Sandier–Serfaty community (Serfaty, Bétermin, Petrache) with the P1 record. This is the author's
     decision.

## Recommended order

| When | Work |
|---|---|
| Weeks 1–3 | A2 rebuild + axiom/soundness audit (highest stakes, mostly mechanical); B2 certified curvature (small, high value); A1a pilot on the first certificate stages |
| Weeks 3–6 | B1 transition threshold + anharmonic checks + Rydberg literature; A1a full; second H9 fidelity audit |
| Months 2–3 | A1b reduction formalization; B3 feasibility study; A3 if A2's pipeline is solid |
| Ongoing | Front C |

Each item is preregistered with a kill criterion, uses the same workflow pattern (Opus for proofs and audits, Sonnet
for numerics and papers, producer ≠ verifier) and is published per paper after audit.
