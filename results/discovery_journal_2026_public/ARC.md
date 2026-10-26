# The year as a story: from agents that claim to a kernel that judges

Dates are Zenodo publication dates from `zenodo_inventory.json` (records 2026-05-25 to 2026-10-26) and creation dates
from `github_inventory.json`. Every DOI below is `10.5281/zenodo.<record>`. The spine of the book is the loop the year
slowly learned: **AI proposes → numerics explore → Lean judges → humans decide meaning.** The path was not a straight
line. Over-claiming returned in mid-October, after the method that should have prevented it had been published, and it
was withdrawn two days later.

## Phase 1: May-August 2026, agents and over-claims

- **The instruments arrive first.** rusty-SUNDIALS, an AI-assisted Rust translation of the CVODE stiff solver, was
  created on 2026-05-11. It later became the numerical backbone of the programme (top-20 pick G-RUSTY).
- **Claims ran ahead of evidence.** On 2026-05-25/26 the same one-sentence claim was deposited 13 times (WARS-CI-DFA,
  20380024 and 12 copies): a backprop-free learning loop on a TPU, a 40% power saving, "formally verified in Lean 4".
  The record contains no Lean file.
- The same days brought RunuX v1 (20383038, 20383105, 20383112): a Lean-specified memory-safe runtime with TPU, 70B
  and Lean-certificate results. Version 2 later stated that those results were never run.
- SymBrain (20397720, 05-26) and the CPUGym freezes (20538871, 20539058, 06-04) reported benchmark numbers that a
  reader cannot check.
- **A cosmology built on numerology.** K3 string vacua were said to explain JWST galaxy tensions (Part I 20863378 and
  Part II 20863381, 06-25; Topological Phase Cosmology 21350629, 07-14).
- The repositories record the first retractions of that line. Agora-K3-DarkMatter's F6 disclosure of 2026-07-24
  retracts its C1/C2 lattice numbers. The Lean proposal repo found two vacuous "integrality" theorems and retracted
  early headline claims in July.
- The AlienMathematics retrospective (repo, June) described six AI-driven methods that all failed.
- **First contact with formal mathematics:**
  - Navier-Stokes frustration index (22108301, 08-26);
  - Ramanujan eta-quotients (22160184, 08-29), with Lean proofs through `native_decide`, which trusts the compiler;
  - an MHD neural operator (22161523, 08-29) whose Lean check was "zero sorry, exit 0". A `sorry` also exits 0.

**Lesson of the phase:** an agent's report of success is not evidence. Chapter candidates: RunuX (lesson line L-RUNUX)
and the dual-scale line (L-DUALSCALE).

## Phase 2: September 1-28, the formal turn and the first public corrections

- **Axioms, not exit codes.** The Fricke-involution formalization (22682139, 09-09) pins 16 theorems with
  `#print axioms` guards and a negative control. It also withdrew its own "first formalization" claim after an audit
  found prior work. The eta-quotient papers that followed (22682148, 22692600) are "axiom-audited".
- **The first withdrawal of a framing.** "Topological censorship of blow-up" (22723078, 09-12) analysed OpenAI's
  Navier-Stokes blow-up proof. Three days later, "Where the continuum ends" (22773907, 09-15) accepted the
  constructions as valid mathematics, withdrew the framing and printed a table of corrections. The physical reading
  followed (22838708, 09-19).
- **The method is written down.** "A laboratory method for AI-assisted science" (22829767, 09-18) extends
  verifier-in-the-loop practice to the whole laboratory: questions, instruments, numbers, writing. It became the
  Elenchus claim ledger.
- **The dual-scale lock is retracted.** On the same day, revision 5 of "The Dual-Scale String Theory" (22837842,
  09-18) reports two failures. The 27720 "lock" fails the twining test at all 25 non-identity M24 classes, which makes
  it numerology. The testable conjecture does not survive data. The pre-registered confrontation (22837837) gives four
  negative verdicts.
- The Lean mathematics of that programme stays Tier A and is kept apart from the retracted physics: 22837843 (the
  LeanMaster lattice library) and 22837835 (moonshine).
- **Corrections in cascade:**
  - QuantumFluids (22853896, 09-20) withdrew two "findings" after a literature check. Its theorems are re-checked by
    two independent kernels.
  - The T-duality paper (22872083, 09-21) withdrew its version 1 claims.
  - RunuX v2 (22879667, 09-21) withdrew the never-run TPU, 70B and Lean results: "withdrawn, not relabeled".
- **The bench audits itself.** The AutoevolveAI remediation audits of 2026-09-25/26 found 14 components reporting
  success without doing the work (repo honesty files, memory `remediation-audit-findings.md`). Examples:
  - a "peer review" script that never called a model;
  - a Lean scorer fooled by stdout;
  - a "SUCCESS" adapter whose loss rose.
- The claims-vs-evidence audit of RunuX (22985926, 09-27) found 141 of 316 crates were placeholders and 249 open
  `sorry` obligations behind a "zero sorry" claim.
- **First reproduction run by agents.** An agent-executed, preregistered BAO reproduction pipeline was published on
  09-28 (23003926). Its earlier DR1 run had recovered DESI's published fit to within 0.07σ and 0.11σ (memory
  `bao-flcdm-run.md`). Three rounds of AI referees were recorded, and the paper states that no person reviewed it.

**Lesson of the phase:** correction became a published act, not a private edit. Picks from this phase:
G-AUTOEVOLVE (the harness and its self-audit).

## Phase 3: October 1-11, Elenchus in practice

- **Gates that can fail.** The GWAYA fail-closed gate (23119953, 10-03) withdrew its v1 and v2 benchmark figures. It
  shows that a Lean "proof" of 1 = 2 via a hidden axiom compiles with exit 0 and is caught only by the axiom audit.
  (pick Z-GWAYA)
- **Numerics enter the kernel.** On 10-08 the Lean kernel checked a solver's own integer certificate for the first
  time: DESI DR2 BAO distances enclosed at seven redshifts (23247730, pick Z-BAO-P1).
- On 10-10 the certified likelihood excluded H0 ≥ 73 km/s/Mpc with BBN, inside flat ΛCDM and its stated
  simplifications (23284020, pick Z-BAO-P23).
- **Negative results published as such** (8-10 October):
  - matrix Lieb-Thirring null result (23245266);
  - refuted predictions kept in the conductance series (23228685, 23241463, 23244556, 23248393);
  - vortex friction follows temperature, not normal density (23262132), with the transport paper corrected
    (23262143 v2.2).
- **AI proposes, Lean checks the consequences.** OpenAI's AI-generated proof of planar universal optimality became the
  upstream theorem. Three kernel-checked corollaries came first (23285631, 10-10, pick Z-RIESZ).
- Then the tiered paper (23293112 v1 and 23293429 v2, 10-11, pick Z-UO-TIERED) added Lean consequences, a CVODE
  N-body check and an Elenchus ledger. Its ledger gate exits 1 because no human has audited the Tier A statements. The
  owner published anyway and said so in the paper.
- **Teaching.** The student textbook (23295142, 10-11, pick Z-UO-BOOK) shows every result three ways: a human proof,
  a Lean statement and tests. The Godfrin tribute (23272154, 10-10) teaches quantum fluids with neutron data, Lean and a
  solver.
- The exciton-fluid series opened (23289027, 23294615, 23297479, 23298292, 23302787). Most of its gates failed, and the
  papers report them as failed.

**Lesson of the phase:** the loop works when each stage is allowed to say no. Picks: Z-BAO-P1, Z-BAO-P23, Z-RIESZ,
Z-UO-TIERED, Z-UO-BOOK, Z-GWAYA.

## Phase 4: October 17-21, relapse and withdrawal

- **The relapse.** On 2026-10-19 a batch appeared under the label "5-Round Opus Peer-Reviewed". All of it claimed
  "zero sorryAx, zero custom axioms":
  - the Elenchus Trilogy (23469404/10/18, each deposited twice);
  - seven copies of a stellarator paper (23478809 …);
  - seven post-quantum cryptography deposits (23478813 …);
  - three LeanFlow MCP deposits, one carrying another paper's files (23481384);
  - two scale-dual subgrid papers (23483566, 23483647);
  - a hurricane-eyewall paper (23478811);
  - a biophysics paper (23484342).
- Genetics followed on 10-20 (23490729, 23510019). This happened a month after the claim-ledger method was published.
- **The withdrawals came two days later** (all on 2026-10-21):
  - 23525655: edition 1's "peer reviewed" is withdrawn, because the review file "was generated by a script that calls
    no reviewer".
  - 23526783: the paper's own POLE P286R mechanism is refuted, and a no-go theorem is added.
  - 23532458: RK4 cools and does not heat, which refutes the stellarator paper's premise. Its confidence figures and a
    theorem are withdrawn (pick L-STELLARATOR).
  - 23532595: the subgrid paper's Theorem 2.5 is refuted, and its blow-up claim withdrawn.
  - 23532601: the "verified SQIsign verifier" accepts the scalar 256, and three headline claims are withdrawn.
- Already on 10-19, 23468458 had withdrawn a scripted "peer review report" with invented referee personas.

**Lesson of the phase:** a method on paper does not stop over-claiming. Running it does. "Peer reviewed by AI agents" is
not human peer review, and a review file must show that a reviewer was actually called.

## Phase 5: October 23-26, the kernel-checked programme with independent audits

- **Negative results in biology and AI search:**
  - a proved certificate whose transfer to sequence data fails (23604793, 10-23);
  - understated null floors, corrected (23610116, 23610123, 10-24);
  - a refuted transfer to genetic programming (23611425);
  - "recombination does not help" (23626924, 10-24).
- **Five contributions** (10-25) applied the upstream theorem to physical systems, each with Lean admissibility, an
  independent AI audit (AUDIT.md) and a recorded revision (REVISION.md):
  - dipolar excitons (23646103, pick ED-09);
  - Yukawa crystals, fixing the earlier truncation erratum (23646105, pick ED-10);
  - Rytova-Keldysh (23646107, pick ED-11);
  - σ = 3 enstrophy (23646111);
  - Bogoliubov S(k) (23646117).
- **Programmes, 10-26:**
  - the Sandier-Serfaty certificate reproduced and audited, with no proof claimed (23653827, pick ED-14);
  - QU-1 refuted numerically (23653833, pick ED-15);
  - a Lean library of completely monotone functions (23653842);
  - the Feynman-Bijl bound in Lean, with He-4 data refuting the project's own envelope (23653846, pick ED-17);
  - fixation probabilities kernel-checked (23653850, pick ED-18).
- **Proposal 2 and 3, 10-26:**
  - a negative feasibility result in 3D (23655002);
  - a certified proof that the triangular lattice is not a local minimum of zero-point energy (23655392, pick ED-20);
  - a negative result for a quantum transition (23655625);
  - 4 of 12 Sandier-Serfaty stages in the Lean kernel (23656804, pick ED-22);
  - the isothermal theorem, with its own pre-registration error reported (23660071, pick ED-23);
  - the independent rebuild and kernel replay of 88,400 declarations of OpenAI's Navier-Stokes corpus, explicitly not a
    claim that a Clay problem is solved (23661381, pick ED-24);
  - the N2 certificate for Yukawa (23663551). It is not among the final 20: in the rescore with the final replay record
    it ties ED-15 and ED-20 at 18, loses the tie on the earlier `created` date, and the cap of 7 per domain then skips
    it (`RESCORE.md`).
- On the same day a full leanchecker replay (`results/kernel_replay_2026-10-26/`) gave rc 0 on every module it reached
  (final record: 93 modules OK, 778 skipped, no failure). The modules were the Triangular, Autoresearch,
  CompletelyMonotone, PopGen, EvoGraph, FeynmanBijl, SandierSerfaty and SandierSerfatyStatement modules, and the
  zero-point modules ZeroPoint, ZeroPointCert, ZeroPointClass and ZeroPointPhys.
- What is still missing is written in every ledger: each gate exits 1 with `LEDGER_UNAUDITED_TIER_A`, because no
  person has yet certified that the kernel-checked statements mean what their glosses say.

**Lesson of the phase:**
- AI proposes, through the upstream theorems and the hypotheses.
- Numerics explore, through CVODE, ball arithmetic and data.
- Lean judges, through axiom audits and kernel replay.
- An independent agent audits, and the human decides what it means and whether to publish.
- The last step, a human statement audit, is the one the year has not yet done.

## How the 20 picks sit on the arc

| phase | picks |
|---|---|
| 1 May-Aug | G-RUSTY (the instrument, created 2026-05-11) |
| 2 Sep | G-AUTOEVOLVE (the harness and its self-audit) |
| 3 Oct 1-11 | Z-GWAYA, Z-BAO-P1, Z-BAO-P23, Z-RIESZ, Z-UO-TIERED, Z-UO-BOOK |
| 4 Oct 17-21 | L-STELLARATOR (relapse withdrawn) |
| 5 Oct 23-26 | ED-09, ED-10, ED-11, ED-14, ED-15, ED-17, ED-18, ED-20, ED-22, ED-23, ED-24 |

The rubric does not select the Phase-1 and Phase-2 over-claims as successes; they enter the book as lessons. Lessons
that ranked below 20 but belong in the narrative: L-RUNUX (22879667), L-DUALSCALE (22837842), L-NS-FRAMING (22773907),
Z-CLAIMS-AUDIT (22985926), L-PQC (23532601), L-STOCHTHERMO (23525655) and L-PROOFREADING (23526783). Their scores are
in `scores.json`.
