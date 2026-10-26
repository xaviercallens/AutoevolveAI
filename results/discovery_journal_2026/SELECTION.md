# Discovery journal 2026: selection of the 20 contributions

Applied 2026-10-26 to the rubric frozen in `RUBRIC.md` (not changed). Built by `scripts/score_build.py` (scores, coverage
checks, ranking, hard rules) and `scripts/top20_build.py` (this file and `TOP20.json`). Every score has a one-line
justification in `scores.json` citing the inventory field, audit file, replay record or memory note it rests on.

## 1. Candidates

- **Zenodo:** all 144 records in `zenodo_inventory.json` (112 distinct titles) plus the N2 paper doi:10.5281/zenodo.23663551,
  which was published after the inventory was fetched (added from `papers/p3_zero_point_physical/`).
  The builder asserts that every record belongs to exactly one candidate.
- **GitHub:** all 57 science-relevant repositories. Test for 'represented': a Zenodo work *describes the repository's
  content* (its library, tool, programme or paper line). 24 repos pass and are attached to that work (listed in each
  candidate's `repos` and `merge_note`); the other 33 form 31 repository candidates.
- **Two judgement calls, stated because they decide picks:** AutoevolveAI (the ANSE harness) and rusty-SUNDIALS (the
  CVODE translation) host the code of many Zenodo works (the `autoevolve_*` bundles, the programme papers, qf-pgpe
  23269715) but no Zenodo work describes either repository itself, so both are candidates. They then fill the
  AI-methodology and numerics minimum slots. Counterfactual (computed in `score_build.py`, stored in `scores.json`
  as `counterfactual_harness_repos`): if both were treated as represented, Z-CLAIMS-AUDIT, Z-LEANFLOW would enter in place of G-RUSTY, G-AUTOEVOLVE; nothing else changes.
- **Result:** 113 candidates.
- **Mandatory merges:** duplicate deposits (e.g. WARS-CI-DFA x13, stellarator x7, PQC x7) and versions under one concept.
- **Declared research-line merges** (criterion: same research question, or an explicit 'supersedes/corrects'; decided
  before ranking): the dual-scale/K3 dark-sector hypothesis line (7 records + 6 repos) scored on its retraction
  22837842; Mathieu moonshine (22823720 + 22837835); Agora corpus papers 4-6; the gated-exciton-fluids series I-V plus
  23289027; vortex friction correction + transport v2.2; reticulate evolution 23604793 + its correction 23610116;
  QuantumFluids library under two concepts; GWAYA v3 + v3.1; Elenchus Trilogy I-III.
- **Aggregation of a merged line:** lesson lines are scored on the withdrawal/correction record (rubric exclusion rule);
  other research-line merges take the best member per criterion, and the justification names that member.

## 2. Scoring key (thresholds applied identically to every candidate)

- **C1 rigour** = the highest Elenchus tier reached by a claim the record itself states. 3 = Lean with axiom check *and* a
  recorded kernel replay (leanchecker / Comparator / a second kernel such as nanoda, or the 2026-10-26 replay record
  `results/kernel_replay_2026-10-26/replay.jsonl`), or an untrusted program's certificate re-checked by *different* code
  (the Lean kernel checking a solver's integer tables: P1, P2/P3). An auditor's recompilation is a compile, not a replay,
  so it does not lift 2 to 3. Re-running the *same* certificate code (Sandier-Serfaty reproduction, ball-arithmetic
  reruns) is not an independent checker. 2 = the record states a Lean axiom footprint within {propext, Classical.choice,
  Quot.sound} or 'zero sorryAx, zero custom axioms' (taken as recorded). 'Zero sorry' or 'exit 0' alone, and
  `native_decide`, do not reach 2 (a `sorry` compiles with exit 0). 1 = human argument, literature, or exact computation
  without a kernel. 0 = floating point only.
  Snapshot of the replay record used: `replay.jsonl` as read on 2026-10-26, 71 rows, all rc 0. That directory is
  untracked in git and the replay was still running (TIER_STATUS.md), so it must be committed before any score
  that cites it is published. ED-20 and N2 cite the N2 paper's own `data/leanchecker_replay.json` instead.
- **C2 independent check:** 3 = a verdict file by a separate agent (AUDIT.md, verification.md, manuscript_audit, referee
  rounds) *and* a record that its corrections were applied (REVISION.md, response files, or a memory note). 2 = such a
  verdict without a record of corrections. A review mentioned only in run notes, with no verdict file (ED-01, ED-02), is
  scored at the lower value. 1 = the author's own checks (preregistered gates, internal audits). The '5-Round
  Peer-Reviewed' label of the 19 October batch scores 1: AI-agent review with no audit artifact, and the same batch's
  review files were withdrawn as script-generated (23525655, 23468458). 0 = nothing.
- **C3 reproducibility:** 3 = re-run by an agent other than the producer with matching output, documented (audit
  recompile/rerun, verifier recompile, replay). 2 = the record ships code + data + commands (a reproduction bundle,
  MANIFEST, REPRODUCE.md, code.zip + dataset.zip). 1 = code available (record files or a public repository).
  0 = none, or the code sits only in a PRIVATE repository.
- **C4 synthesis** (mechanical, from inventory fields as found): physics/biology pillar = domain physics, cosmology,
  fusion/plasma or genetics/biology; formal pillar = `lean_component` yes (a mention, accepted for synthesis but not
  for rigour); mathematics pillar = domain mathematics or `lean_component` yes; numerics pillar =
  `numeric_or_simulation_component` yes. 1 pillar = 0 … 4 pillars = 3. For repos: Lean files, Rust/SUNDIALS/numerics
  and domain from `github_inventory.json`.
- **C5 honesty:** 3 = the record publishes a negative result, a self-correction of earlier work, or a refutation;
  2 = caveats stated; 1 = none; 0 = later retracted with no correction published.
- **C6 novelty:** 3 only when later work demonstrably reused it (reuse cited); 2 = new result or tool; 1 = incremental;
  0 = duplicate.
- **C7 value to people:** 3 = a non-specialist sees a concrete stake (health, energy, education, trust in AI); 2 =
  understandable; 1 = abstract; 0 = none.
- **Lesson** (for the '>= 3 lessons' rule) = the scored record's inventory kind is 'negative or null result', or the
  candidate is a withdrawal/correction line scored on its correction record. A positive paper that contains a
  refutation (ED-17) or an erratum fix (ED-10) is not counted as a lesson.
- **Domains** are the inventory's `classification.domain` as found (N2 given physics, like B2 and QU-1); cosmology,
  fusion/plasma, education/textbook and other count toward no minimum but are capped at 7. Repo labels were mapped
  by name only ('AI agents/methodology/verification' -> 'AI methodology/verification').
- **Ties:** total, then C1, then C2, then the earlier `created` timestamp (repo: creation date).

## 3. Hard rules, applied in this order (code: `select()` in `score_build.py`)

1. Exclusions: works whose central claim was withdrawn or refuted are folded into lesson lines scored on the
   withdrawal paper (RunuX v1 -> 22879667; 22723078 -> 22773907; dual-scale physics -> 22837842; stellarator x7 ->
   23532458; PQC -> 23532601; scale-dual subgrid -> 23532595; POLE mechanism -> 23526783). Edition 1 of stochastic
   thermodynamics (23510019), enstrophy v2.0 (23458238) and vortex transport (23262143) withdrew a label or a reading,
   not their central claim, and are merged with their correction. Exclusion test on 23646117 (Bogoliubov): its
   envelope is refuted for real He-4 by 23653846, but its own central claims are Lean shape theorems and a test that
   stayed silent, so it stays eligible.
2. Domain minimums: the top 2 of mathematics, physics, genetics/biology, numerics/software and AI
   methodology/verification are reserved.
3. Lessons: if fewer than 3 reserved picks are lessons, the top-ranked lessons are added.
4. The remaining slots are filled in rank order, skipping any candidate whose domain already has 7.

Selection log:

- reserve (domain minimum, mathematics): ED-14 total 18, pure rank 13
- reserve (domain minimum, mathematics): ED-22 total 17, pure rank 14
- reserve (domain minimum, physics): Z-UO-TIERED total 19, pure rank 3
- reserve (domain minimum, physics): ED-10 total 19, pure rank 4
- reserve (domain minimum, genetics/biology): ED-18 total 19, pure rank 6
- reserve (domain minimum, genetics/biology): ED-23 total 19, pure rank 7
- reserve (domain minimum, numerics/software): G-RUSTY total 16, pure rank 21
- reserve (domain minimum, numerics/software): L-STELLARATOR total 13, pure rank 42
- reserve (domain minimum, AI methodology/verification): Z-GWAYA total 15, pure rank 26
- reserve (domain minimum, AI methodology/verification): G-AUTOEVOLVE total 14, pure rank 34
- reserve (lessons >= 3): ED-20 total 18, pure rank 11
- reserve (lessons >= 3): N2 total 18, pure rank 12
- skip (cap 7 for physics): Z-QFLIB total 17, pure rank 16
- skip (cap 7 for physics): ED-15 total 17, pure rank 17

## 4. The 20 chosen

| # | id | title | domain | date | C1 | C2 | C3 | C4 | C5 | C6 | C7 | total | lesson |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Z-BAO-P1 | Kernel-checked enclosures of DESI DR2 BAO distances | cosmology | 2026-10-08 | 3 | 3 | 3 | 3 | 2 | 3 | 2 | 19 |  |
| 2 | Z-BAO-P23 | Kernel-checked constraints from DESI DR2 BAO: Omega_m bands and H0 >=… | cosmology | 2026-10-10 | 3 | 3 | 3 | 3 | 2 | 2 | 3 | 19 |  |
| 3 | Z-UO-TIERED | Planar universal optimality, tiered: Lean consequences and a CVODE N-… | physics | 2026-10-11 | 3 | 3 | 3 | 3 | 2 | 3 | 2 | 19 |  |
| 4 | ED-10 | The triangular lattice minimises the planar Yukawa energy | physics | 2026-10-25 | 3 | 3 | 3 | 3 | 3 | 2 | 2 | 19 |  |
| 5 | ED-17 | Feynman-Bijl single-mode bound in Lean and a diffraction test on He-4… | physics | 2026-10-26 | 3 | 3 | 3 | 3 | 3 | 2 | 2 | 19 |  |
| 6 | ED-18 | Fixation probabilities as absorption limits, kernel-checked (Wright-F… | genetics/biology | 2026-10-26 | 3 | 3 | 3 | 3 | 2 | 3 | 2 | 19 |  |
| 7 | ED-23 | The isothermal theorem of evolutionary graph theory, kernel-checked | genetics/biology | 2026-10-26 | 3 | 3 | 3 | 3 | 3 | 2 | 2 | 19 |  |
| 8 | Z-UO-BOOK | The Triangular Lattice and Universal Optimality (student textbook) | education/textbook | 2026-10-11 | 3 | 3 | 3 | 2 | 2 | 2 | 3 | 18 |  |
| 9 | ED-09 | The bilayer dipolar-exciton interaction is completely monotone | physics | 2026-10-25 | 3 | 3 | 3 | 3 | 2 | 2 | 2 | 18 |  |
| 10 | ED-11 | The Rytova-Keldysh interaction is a positive Gaussian mixture | physics | 2026-10-25 | 3 | 3 | 3 | 3 | 2 | 2 | 2 | 18 |  |
| 11 | ED-20 | The triangular lattice is not a local minimum of zero-point energy fo… | physics | 2026-10-26 | 3 | 3 | 3 | 3 | 3 | 2 | 1 | 18 | yes |
| 12 | N2 | The triangular lattice is not a local minimum of zero-point energy fo… | physics | 2026-10-26 | 3 | 3 | 3 | 3 | 3 | 2 | 1 | 18 | yes |
| 13 | ED-14 | Sandier-Serfaty triangular-lattice claim: reproduction and audit (no … | mathematics | 2026-10-26 | 2 | 3 | 3 | 2 | 2 | 3 | 3 | 18 |  |
| 14 | ED-22 | Toward a machine-checked Sandier-Serfaty certificate: 4 of 12 stages … | mathematics | 2026-10-26 | 3 | 3 | 3 | 2 | 2 | 2 | 2 | 17 |  |
| 15 | ED-24 | Independent rebuild, kernel replay and audit of openai/NavierStokesAn… | mathematics | 2026-10-26 | 3 | 3 | 3 | 1 | 2 | 2 | 3 | 17 |  |
| 16 | Z-RIESZ | Riesz-energy, finiteness and every-density corollaries of openai/math… | mathematics | 2026-10-10 | 3 | 3 | 3 | 1 | 2 | 3 | 1 | 16 |  |
| 17 | G-RUSTY | rusty-SUNDIALS: AI-assisted pure-Rust translation of SUNDIALS CVODE | numerics/software | 2026-05-11 | 0 | 3 | 3 | 2 | 3 | 3 | 2 | 16 |  |
| 18 | Z-GWAYA | GWAYA fail-closed verification gate for LLM-generated code (v3, v3.1) | AI methodology/verification | 2026-10-03 | 2 | 1 | 2 | 2 | 3 | 2 | 3 | 15 |  |
| 19 | G-AUTOEVOLVE | AutoevolveAI / ANSE: verification-first harness for LLM-agent science | AI methodology/verification | 2026-09-19 | 1 | 1 | 1 | 2 | 3 | 3 | 3 | 14 |  |
| 20 | L-STELLARATOR | RK4 cools at resolved step sizes, it does not heat (edition 2, refuti… | numerics/software | 2026-10-21 | 1 | 1 | 2 | 2 | 3 | 2 | 2 | 13 | yes |

Domain count: AI methodology/verification 2, cosmology 2, education/textbook 1, genetics/biology 2, mathematics 4, numerics/software 2, physics 7; lessons 3.

## 5. What the rules changed, said openly

Compared with the pure top 20 by total score:

- **Out:** Z-QFLIB (QuantumFluids: Lean 4 library of quantum-fluid structure (8…; physics; total 17; pure rank 16): removed by the cap of 7 per domain (physics already had 7 higher-ranked picks).
- **Out:** ED-15 (Does the triangular lattice minimise the harmonic zero-poin…; physics; total 17; pure rank 17): removed by the cap of 7 per domain (physics already had 7 higher-ranked picks).
- **Out:** Z-BAO-REPRO (Agent-executed preregistered BAO reproduction pipeline (cos…; cosmology; total 16; pure rank 19): displaced: the four slots reserved for the numerics/software and AI-methodology minimums pushed the lowest-ranked remaining picks out.
- **Out:** L-PROOFREADING (Hopfield-Ninio proofreading (edition 3): refuting the paper…; genetics/biology; total 16; pure rank 20): displaced: the four slots reserved for the numerics/software and AI-methodology minimums pushed the lowest-ranked remaining picks out.
- **In:** G-RUSTY (rusty-SUNDIALS: AI-assisted pure-Rust translation of SUNDIA…; numerics/software; total 16; pure rank 21): reserved by the
  minimum of 2 for numerics/software.
- **In:** Z-GWAYA (GWAYA fail-closed verification gate for LLM-generated code …; AI methodology/verification; total 15; pure rank 26): reserved by the
  minimum of 2 for AI methodology/verification.
- **In:** G-AUTOEVOLVE (AutoevolveAI / ANSE: verification-first harness for LLM-age…; AI methodology/verification; total 14; pure rank 34): reserved by the
  minimum of 2 for AI methodology/verification.
- **In:** L-STELLARATOR (RK4 cools at resolved step sizes, it does not heat (edition…; numerics/software; total 13; pure rank 42): reserved by the
  minimum of 2 for numerics/software.

- The lessons rule did not change the list: ED-20 and N2 were already in the pure top 20, and the numerics minimum
  brought in the stellarator lesson, which makes 3.
- The AI-methodology second place was a tie at 14 between G-AUTOEVOLVE and Z-CLAIMS-AUDIT: equal C1 (1) and C2 (1),
  broken by the earlier date (repo created 2026-09-19 vs record 2026-09-27).
- Numerics/software is thin: its second pick (L-STELLARATOR, 13) is a lesson, ranked 42nd overall. It counts as
  numerics/software because the rubric scores a lesson line on its withdrawal paper, and 23532458 is classified
  numerics/software; the seven merged stellarator deposits are classified fusion/plasma.
- The harness counterfactual (section 1): treating AutoevolveAI and rusty-SUNDIALS as represented would swap in Z-CLAIMS-AUDIT, Z-LEANFLOW.
- Private repositories among the 20: none. Z-LABMETHOD (below rank 20) rests on the
  private Elenchus repo; the book must ask before summarising any private repository.
- Concentration: 17 of the 20 are dated 8-26 October 2026, because the rubric rewards replay, independent audits with
  recorded revisions and published negative results, which the project only produced systematically from October.
  The earlier phases are told in `ARC.md` and enter the list mainly through the lessons and infrastructure picks.

## 6. Full ranked table (all candidates)

| rank | id | title | domain | date | C1 | C2 | C3 | C4 | C5 | C6 | C7 | total | lesson | selected |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Z-BAO-P1 | Kernel-checked enclosures of DESI DR2 BAO distances | cosmology | 2026-10-08 | 3 | 3 | 3 | 3 | 2 | 3 | 2 | 19 |  | **yes** |
| 2 | Z-BAO-P23 | Kernel-checked constraints from DESI DR2 BAO: Omega_m bands and… | cosmology | 2026-10-10 | 3 | 3 | 3 | 3 | 2 | 2 | 3 | 19 |  | **yes** |
| 3 | Z-UO-TIERED | Planar universal optimality, tiered: Lean consequences and a CV… | physics | 2026-10-11 | 3 | 3 | 3 | 3 | 2 | 3 | 2 | 19 |  | **yes** |
| 4 | ED-10 | The triangular lattice minimises the planar Yukawa energy | physics | 2026-10-25 | 3 | 3 | 3 | 3 | 3 | 2 | 2 | 19 |  | **yes** |
| 5 | ED-17 | Feynman-Bijl single-mode bound in Lean and a diffraction test o… | physics | 2026-10-26 | 3 | 3 | 3 | 3 | 3 | 2 | 2 | 19 |  | **yes** |
| 6 | ED-18 | Fixation probabilities as absorption limits, kernel-checked (Wr… | genetics/biology | 2026-10-26 | 3 | 3 | 3 | 3 | 2 | 3 | 2 | 19 |  | **yes** |
| 7 | ED-23 | The isothermal theorem of evolutionary graph theory, kernel-che… | genetics/biology | 2026-10-26 | 3 | 3 | 3 | 3 | 3 | 2 | 2 | 19 |  | **yes** |
| 8 | Z-UO-BOOK | The Triangular Lattice and Universal Optimality (student textbo… | education/textbook | 2026-10-11 | 3 | 3 | 3 | 2 | 2 | 2 | 3 | 18 |  | **yes** |
| 9 | ED-09 | The bilayer dipolar-exciton interaction is completely monotone | physics | 2026-10-25 | 3 | 3 | 3 | 3 | 2 | 2 | 2 | 18 |  | **yes** |
| 10 | ED-11 | The Rytova-Keldysh interaction is a positive Gaussian mixture | physics | 2026-10-25 | 3 | 3 | 3 | 3 | 2 | 2 | 2 | 18 |  | **yes** |
| 11 | ED-20 | The triangular lattice is not a local minimum of zero-point ene… | physics | 2026-10-26 | 3 | 3 | 3 | 3 | 3 | 2 | 1 | 18 | yes | **yes** |
| 12 | N2 | The triangular lattice is not a local minimum of zero-point ene… | physics | 2026-10-26 | 3 | 3 | 3 | 3 | 3 | 2 | 1 | 18 | yes | **yes** |
| 13 | ED-14 | Sandier-Serfaty triangular-lattice claim: reproduction and audi… | mathematics | 2026-10-26 | 2 | 3 | 3 | 2 | 2 | 3 | 3 | 18 |  | **yes** |
| 14 | ED-22 | Toward a machine-checked Sandier-Serfaty certificate: 4 of 12 s… | mathematics | 2026-10-26 | 3 | 3 | 3 | 2 | 2 | 2 | 2 | 17 |  | **yes** |
| 15 | ED-24 | Independent rebuild, kernel replay and audit of openai/NavierSt… | mathematics | 2026-10-26 | 3 | 3 | 3 | 1 | 2 | 2 | 3 | 17 |  | **yes** |
| 16 | Z-QFLIB | QuantumFluids: Lean 4 library of quantum-fluid structure (89 to… | physics | 2026-10-12 | 3 | 1 | 2 | 3 | 3 | 3 | 2 | 17 |  |  |
| 17 | ED-15 | Does the triangular lattice minimise the harmonic zero-point en… | physics | 2026-10-26 | 2 | 3 | 3 | 3 | 3 | 2 | 1 | 17 | yes |  |
| 18 | Z-RIESZ | Riesz-energy, finiteness and every-density corollaries of opena… | mathematics | 2026-10-10 | 3 | 3 | 3 | 1 | 2 | 3 | 1 | 16 |  | **yes** |
| 19 | Z-BAO-REPRO | Agent-executed preregistered BAO reproduction pipeline (cosmo3) | cosmology | 2026-09-27 | 2 | 3 | 2 | 3 | 2 | 2 | 2 | 16 |  |  |
| 20 | L-PROOFREADING | Hopfield-Ninio proofreading (edition 3): refuting the paper's o… | genetics/biology | 2026-10-21 | 2 | 1 | 2 | 3 | 3 | 2 | 3 | 16 | yes |  |
| 21 | G-RUSTY | rusty-SUNDIALS: AI-assisted pure-Rust translation of SUNDIALS C… | numerics/software | 2026-05-11 | 0 | 3 | 3 | 2 | 3 | 3 | 2 | 16 |  | **yes** |
| 22 | ED-16 | Completely monotone and Bernstein functions in Lean 4 | mathematics | 2026-10-26 | 3 | 3 | 3 | 1 | 2 | 2 | 1 | 15 |  |  |
| 23 | Z-SELFDUAL | When does self-duality cause physics? A machine-checked criteri… | physics | 2026-09-27 | 3 | 1 | 1 | 3 | 3 | 2 | 2 | 15 |  |  |
| 24 | ED-13 | Bogoliubov structure factor under the dual-scale envelope | physics | 2026-10-25 | 2 | 3 | 3 | 3 | 2 | 1 | 1 | 15 |  |  |
| 25 | L-NS-FRAMING | Where the continuum ends: version 2 withdrawing the 'topologica… | physics | 2026-09-15 | 2 | 1 | 1 | 3 | 3 | 3 | 2 | 15 | yes |  |
| 26 | Z-GWAYA | GWAYA fail-closed verification gate for LLM-generated code (v3,… | AI methodology/verification | 2026-10-03 | 2 | 1 | 2 | 2 | 3 | 2 | 3 | 15 |  | **yes** |
| 27 | Z-GODFRIN | Quantum Fluids in Lean 4: a tribute to Henri Godfrin (textbook) | education/textbook | 2026-10-10 | 2 | 1 | 2 | 2 | 3 | 2 | 3 | 15 |  |  |
| 28 | L-EXCITON | Gated exciton fluids, papers I-V and the lattice-optimality dep… | physics | 2026-10-11 | 2 | 1 | 2 | 3 | 3 | 2 | 2 | 15 | yes |  |
| 29 | Z-RETICULATE | Proof-carrying detection of reticulate evolution (split certifi… | genetics/biology | 2026-10-24 | 2 | 1 | 2 | 3 | 3 | 2 | 2 | 15 | yes |  |
| 30 | ED-19 | Can the planar Sandier-Serfaty architecture reach 3D bcc jelliu… | physics | 2026-10-26 | 1 | 3 | 3 | 3 | 3 | 1 | 1 | 15 | yes |  |
| 31 | Z-GEN-BOOK | Formal Genetics: Proof, Computation and Evidence in Molecular B… | genetics/biology | 2026-10-24 | 1 | 1 | 2 | 3 | 3 | 2 | 3 | 15 |  |  |
| 32 | Z-LT-NULL | Null result for the matrix-valued sharp 1D Lieb-Thirring inequa… | mathematics | 2026-10-08 | 3 | 1 | 2 | 2 | 3 | 2 | 1 | 14 | yes |  |
| 33 | ED-12 | Cutoff-independent enstrophy bound for the sigma = 3 dispersive… | mathematics | 2026-10-25 | 2 | 3 | 3 | 2 | 2 | 1 | 1 | 14 |  |  |
| 34 | G-AUTOEVOLVE | AutoevolveAI / ANSE: verification-first harness for LLM-agent s… | AI methodology/verification | 2026-09-19 | 1 | 1 | 1 | 2 | 3 | 3 | 3 | 14 |  | **yes** |
| 35 | Z-CLAIMS-AUDIT | Claims vs. evidence: audit of an AI-assisted Rust kernel | AI methodology/verification | 2026-09-27 | 1 | 1 | 2 | 2 | 3 | 2 | 3 | 14 | yes |  |
| 36 | L-DUALSCALE | The dual-scale hypothesis tested against data and retracted (re… | physics | 2026-09-18 | 2 | 1 | 1 | 2 | 3 | 2 | 2 | 13 | yes |  |
| 37 | L-STOCHTHERMO | Stochastic thermodynamics and chromatin remodelling (edition 2 … | genetics/biology | 2026-10-21 | 2 | 1 | 2 | 2 | 3 | 1 | 2 | 13 | yes |  |
| 38 | Z-CROSSOVER | Recombination does not help: kernel-gated crossover measurement | AI methodology/verification | 2026-10-24 | 2 | 1 | 2 | 2 | 3 | 1 | 2 | 13 | yes |  |
| 39 | Z-KGE | Kernel-Gated Evolution (KGE): foundation paper and Rust impleme… | AI methodology/verification | 2026-10-25 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 13 |  |  |
| 40 | Z-NS-PHYSREAD | The OpenAI Navier-Stokes and Euler blow-up proofs: a physical r… | physics | 2026-09-18 | 1 | 1 | 2 | 3 | 2 | 2 | 2 | 13 |  |  |
| 41 | G-EXOPLANET | TIC 4206066 b: independent adversarial re-analysis of an exopla… | cosmology | 2026-10-11 | 1 | 1 | 2 | 3 | 2 | 2 | 2 | 13 |  |  |
| 42 | L-STELLARATOR | RK4 cools at resolved step sizes, it does not heat (edition 2, … | numerics/software | 2026-10-21 | 1 | 1 | 2 | 2 | 3 | 2 | 2 | 13 | yes | **yes** |
| 43 | L-PQC | Maximal order of SQIsign's starting curve (edition 2): withdraw… | other | 2026-10-21 | 1 | 1 | 2 | 2 | 3 | 1 | 3 | 13 | yes |  |
| 44 | Z-HIVEMIND | Project HiveMind: decentralized sparse MoE training on 8 GB GPUs | AI methodology/verification | 2026-10-25 | 1 | 1 | 2 | 2 | 3 | 2 | 2 | 13 |  |  |
| 45 | L-VORTEX | Vortex friction follows temperature, not normal density (correc… | physics | 2026-10-09 | 0 | 3 | 1 | 3 | 3 | 2 | 1 | 13 | yes |  |
| 46 | Z-FRICKE | Lean 4 formalization of the Fricke involution | mathematics | 2026-09-09 | 2 | 1 | 2 | 1 | 3 | 2 | 1 | 12 |  |  |
| 47 | Z-MECHANICA | MechanicaFluidorum: verifier-in-the-loop programme on 3D Navier… | mathematics | 2026-09-18 | 2 | 1 | 2 | 2 | 2 | 2 | 1 | 12 |  |  |
| 48 | Z-LATTICES | Lattices, T-duality and double field theory on K3 x T2 in Lean … | mathematics | 2026-09-18 | 2 | 1 | 2 | 1 | 2 | 3 | 1 | 12 |  |  |
| 49 | Z-COOPER | Symmetric-square structure theorem for Cooper's Apery-like oper… | mathematics | 2026-10-08 | 2 | 1 | 2 | 1 | 3 | 2 | 1 | 12 |  |  |
| 50 | Z-ENSTROPHY10 | Cutoff-uniform enstrophy bounds in dyadic hierarchies: ten hypo… | mathematics | 2026-10-19 | 2 | 1 | 2 | 2 | 3 | 1 | 1 | 12 |  |  |
| 51 | G-AUTOEVOLVE-K3 | AutoEvolve-K3xT2: evolutionary cosmology search, with a NANOGra… | cosmology | 2026-07-29 | 1 | 1 | 1 | 3 | 3 | 1 | 2 | 12 | yes |  |
| 52 | Z-LABMETHOD | A laboratory method for AI-assisted science (the claim ledger t… | AI methodology/verification | 2026-09-18 | 1 | 1 | 0 | 2 | 2 | 3 | 3 | 12 |  |  |
| 53 | Z-TDUAL-CORR | Tiered formal and numerical methods for T-duality (corrected ve… | physics | 2026-09-21 | 1 | 1 | 2 | 3 | 3 | 1 | 1 | 12 | yes |  |
| 54 | Z-CALDERON | Exact exponential rates for the discrete Calderon problem on st… | mathematics | 2026-10-08 | 1 | 1 | 2 | 2 | 3 | 2 | 1 | 12 |  |  |
| 55 | Z-COLRES | Ill-conditioning as dependence on earlier span: a column-residu… | mathematics | 2026-10-08 | 1 | 1 | 2 | 2 | 3 | 2 | 1 | 12 |  |  |
| 56 | Z-GP-TRANSFER | Behavioural profiles are not heritable sequences: refuted trans… | genetics/biology | 2026-10-24 | 1 | 1 | 2 | 3 | 3 | 1 | 1 | 12 | yes |  |
| 57 | ED-21 | Triangular-to-oblique instability of the quantum Gaussian-core … | physics | 2026-10-26 | 0 | 3 | 3 | 1 | 3 | 1 | 1 | 12 | yes |  |
| 58 | Z-LIGOZAT | Eta-quotients in Lean 4: cusp orders and Ligozat's criterion | mathematics | 2026-09-09 | 2 | 1 | 2 | 1 | 2 | 2 | 1 | 11 |  |  |
| 59 | Z-MOONSHINE | Mathieu moonshine computed in Lean (with M24 rigidity and BPS d… | mathematics | 2026-09-18 | 2 | 1 | 1 | 2 | 2 | 2 | 1 | 11 |  |  |
| 60 | Z-TRIAD | The Frontier Triad on K3 x T2 | physics | 2026-09-19 | 2 | 1 | 1 | 2 | 3 | 1 | 1 | 11 |  |  |
| 61 | Z-WEIERSTRASS | Kernel-checked Weierstrass elliptic-curve arithmetic and Dream-… | mathematics | 2026-10-17 | 2 | 1 | 2 | 2 | 2 | 1 | 1 | 11 |  |  |
| 62 | Z-CAP-NS | Computer-assisted proofs in 3D Navier-Stokes and hurricane eyew… | mathematics | 2026-10-19 | 2 | 1 | 1 | 2 | 2 | 1 | 2 | 11 |  |  |
| 63 | Z-LEANFLOW | LeanFlow MCP: architecture for computer-assisted proofs and res… | numerics/software | 2026-10-19 | 2 | 1 | 1 | 2 | 1 | 2 | 2 | 11 |  |  |
| 64 | Z-BIOPHYS | Non-equilibrium biophysics, conformational genetics, bio-inspir… | genetics/biology | 2026-10-19 | 2 | 1 | 1 | 3 | 1 | 1 | 2 | 11 |  |  |
| 65 | G-CINETIQUE | Physique-Cinetique: exact-rational kinetic response engine, wit… | physics | 2026-06-22 | 1 | 1 | 1 | 3 | 3 | 1 | 1 | 11 | yes |  |
| 66 | L-RUNUX | RunuX: fixed-point attention on a T4, version 2 withdrawing ver… | numerics/software | 2026-09-21 | 1 | 1 | 2 | 0 | 3 | 1 | 3 | 11 | yes |  |
| 67 | Z-TOPO-PROG | Topology constrains, under a gap, what geometry determines (pro… | physics | 2026-10-10 | 1 | 1 | 2 | 3 | 2 | 1 | 1 | 11 |  |  |
| 68 | Z-BIHELM | Bi-Helmholtz thresholds, dyadic paraproducts, Heegner-Lienard o… | mathematics | 2026-10-18 | 1 | 1 | 2 | 2 | 3 | 1 | 1 | 11 |  |  |
| 69 | L-SUBGRID | Scale-dual subgrid model of 3D Navier-Stokes: the true quadrati… | mathematics | 2026-10-21 | 1 | 1 | 2 | 2 | 3 | 1 | 1 | 11 | yes |  |
| 70 | Z-MHD-NO | Structure-preserving neural operators for MHD | physics | 2026-08-29 | 1 | 0 | 2 | 3 | 1 | 2 | 2 | 11 |  |  |
| 71 | Z-FRICKE-SD | Fricke-self-dual eta-quotients are eigenforms | mathematics | 2026-09-10 | 2 | 1 | 2 | 1 | 2 | 1 | 1 | 10 |  |  |
| 72 | Z-DS-GEOM | Dual-scale generalized geometry on K3 x T2 (Lean) | physics | 2026-09-18 | 2 | 1 | 1 | 2 | 2 | 1 | 1 | 10 |  |  |
| 73 | Z-AGORA-RES | Formal resolutions of conjectures in the Lean 5 Agora corpus (p… | physics | 2026-09-18 | 2 | 1 | 1 | 2 | 2 | 1 | 1 | 10 |  |  |
| 74 | G-ALIEN | AlienMathematics-Foundation: retrospective of a failed AI-drive… | mathematics | 2026-06-08 | 1 | 1 | 1 | 1 | 3 | 1 | 2 | 10 | yes |  |
| 75 | G-WOLFRAM | Wolfram-Hypergraph: computation-augmented generation for hyperg… | cosmology | 2026-07-28 | 1 | 1 | 1 | 3 | 2 | 1 | 1 | 10 |  |  |
| 76 | G-TNN | TNN-UniversModel: tensor-NN universe model with a real-data reg… | AI methodology/verification | 2026-08-12 | 1 | 1 | 1 | 2 | 3 | 1 | 1 | 10 | yes |  |
| 77 | G-MATHESIS | Mathesis: shared notation, verification kernel and epistemic le… | AI methodology/verification | 2026-08-13 | 1 | 1 | 1 | 2 | 2 | 2 | 1 | 10 |  |  |
| 78 | Z-DYADIC | The absolute dyadic triangular Hilbert sum: sharp constant at l… | mathematics | 2026-10-08 | 1 | 1 | 2 | 1 | 2 | 2 | 1 | 10 |  |  |
| 79 | Z-AR-SCREEN | Karpathy-autoresearch screening and Elenchus deep-dive | AI methodology/verification | 2026-10-19 | 1 | 1 | 2 | 2 | 1 | 2 | 1 | 10 |  |  |
| 80 | Z-COND-DEPTH | Logarithmic boundary depth and conditioning of the discrete inv… | mathematics | 2026-10-08 | 0 | 1 | 2 | 1 | 3 | 2 | 1 | 10 |  |  |
| 81 | Z-TRILOGY | Elenchus Trilogy I-III | mathematics | 2026-10-19 | 2 | 1 | 1 | 2 | 1 | 1 | 1 | 9 |  |  |
| 82 | G-AGORA-WS | SocrateAI Agora / NewDiscoveries multi-agent workspace (private) | AI methodology/verification | 2026-05-31 | 1 | 1 | 0 | 2 | 2 | 2 | 1 | 9 |  |  |
| 83 | Z-ETA-RAMANUJAN | Ramanujan eta-quotients: classification, Lean, numerics | mathematics | 2026-08-29 | 1 | 0 | 2 | 2 | 2 | 1 | 1 | 9 |  |  |
| 84 | G-CMT | CondensedMatterTheory: AdS/CMT literature review with Lean offs… | physics | 2026-09-27 | 1 | 0 | 1 | 3 | 2 | 1 | 1 | 9 |  |  |
| 85 | Z-K3-BOOK | K3 Surfaces from the Lattice Up (textbook, ed. 0.1) | education/textbook | 2026-09-29 | 1 | 0 | 1 | 2 | 1 | 2 | 2 | 9 |  |  |
| 86 | Z-TOPO-PROXY | A topological proxy for ill-conditioning (persistent homology) | mathematics | 2026-10-08 | 0 | 1 | 2 | 1 | 3 | 1 | 1 | 9 |  |  |
| 87 | G-MIRROR | Mirror-Map-Sieve: an Apery-like sum and a possible Calabi-Yau r… | mathematics | 2026-06-18 | 1 | 0 | 1 | 2 | 2 | 1 | 1 | 8 |  |  |
| 88 | Z-TRIADIC | Triadic frustration index in 3D Navier-Stokes | mathematics | 2026-08-26 | 1 | 0 | 1 | 2 | 2 | 1 | 1 | 8 |  |  |
| 89 | G-LEANLIB | SocrateAI-Lean-Lib: 14-domain Lean library with an axiom-audit … | mathematics | 2026-09-05 | 2 | 1 | 1 | 1 | 1 | 1 | 0 | 7 |  |  |
| 90 | Z-BH-K3 | Smallest black hole picks a K3 surface, the vacuum does not | mathematics | 2026-09-20 | 1 | 1 | 0 | 1 | 2 | 1 | 1 | 7 |  |  |
| 91 | G-OPTENERGY | OptimalEnergyAI: triangular-lattice optimality as latent geomet… | mathematics | 2026-10-12 | 1 | 0 | 0 | 2 | 2 | 1 | 1 | 7 |  |  |
| 92 | G-COMM | Scientific-Communication: papers with the reviews that examined… | AI methodology/verification | 2026-09-06 | 0 | 1 | 0 | 0 | 3 | 1 | 2 | 7 | yes |  |
| 93 | Z-QFPGPE | qf-pgpe: Rust projected Gross-Pitaevskii engine | numerics/software | 2026-10-09 | 0 | 1 | 1 | 0 | 2 | 2 | 1 | 7 |  |  |
| 94 | G-THESIS | thesisautoresearch: DBA thesis copilot (private) | AI methodology/verification | 2026-05-21 | 1 | 0 | 0 | 2 | 1 | 1 | 1 | 6 |  |  |
| 95 | G-SUPERGRAVITY | SuperGravity: zero-trust gateway for agentic coding | AI methodology/verification | 2026-09-20 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 6 |  |  |
| 96 | G-XAURA | xAuraOS: local-first governed agent runtime | AI methodology/verification | 2026-08-06 | 0 | 1 | 1 | 0 | 2 | 1 | 1 | 6 |  |  |
| 97 | G-RAMANUJAN | RamanujanNeuroSymbolic: automated pipeline on mock modular forms | mathematics | 2026-08-09 | 1 | 0 | 1 | 1 | 1 | 1 | 0 | 5 |  |  |
| 98 | G-UNIVERSCRAFT | Universcraft: Rust procedural rendering engine | numerics/software | 2026-08-25 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 5 |  |  |
| 99 | Z-WARS | WARS-CI-DFA biomimetic learning on a TPU v5e | AI methodology/verification | 2026-05-25 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 5 |  |  |
| 100 | G-LEANVERIF | SocrateAI-Lean-Verification (private, tensor rank) | mathematics | 2026-06-13 | 1 | 0 | 0 | 1 | 1 | 1 | 0 | 4 |  |  |
| 101 | G-AMCP | AMCP: agent mesh communication protocol (Java) | AI methodology/verification | 2025-09-24 | 0 | 0 | 1 | 0 | 1 | 1 | 1 | 4 |  |  |
| 102 | G-CYCLO | OpenCycloInitiative: open algae photobioreactor design documents | genetics/biology | 2026-02-20 | 0 | 0 | 0 | 0 | 1 | 1 | 2 | 4 |  |  |
| 103 | Z-LAYA | Laya-LoRA Coding Companion (camera-ready v3) | AI methodology/verification | 2026-10-01 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 4 |  |  |
| 104 | Z-SYMBRAIN | SymBrain neuro-symbolic small-model architecture | AI methodology/verification | 2026-05-26 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 3 |  |  |
| 105 | Z-CPUGYM | CPUGym V9 final freeze artefacts | numerics/software | 2026-06-04 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 3 |  |  |
| 106 | G-ATTENTION | attentionmatter: prompt-token reduction proof of concept (priva… | AI methodology/verification | 2026-06-25 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 3 |  |  |
| 107 | G-LEVELDB | rusty-leveldb: Rust LevelDB port (fork-derived) | numerics/software | 2026-05-11 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 2 |  |  |
| 108 | G-QC | QuantumComputing stream ('prepared, not implemented') | physics | 2026-10-11 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 2 |  |  |
| 109 | G-NSYMBO | nSymboCoder: sub-1B neuro-symbolic code-model concept (private) | AI methodology/verification | 2026-05-10 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |  |  |
| 110 | G-POLY | Poly-Algebraic-Calculus (placeholder) | mathematics | 2026-08-11 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |  |  |
| 111 | G-FLUIDMEC | FluidMecanism (empty placeholder) | physics | 2026-08-12 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |  |  |
| 112 | G-CK8D | SocrateAI-CohnKumar-8D-Numeric (empty) | mathematics | 2026-10-11 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |  |  |
| 113 | G-FUSION-EMPTY | SocrateAI-Scientific-FusionEnergy (empty) | fusion/plasma | 2026-10-19 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |  |  |

Per-criterion justifications, member DOIs, repos (with visibility), merge and exclusion notes: `scores.json`.
