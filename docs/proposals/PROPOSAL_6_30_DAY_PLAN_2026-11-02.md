# Proposal 6: a 30-day plan for the Elenchus programme, 2 November to 1 December 2026

Drafted by an AI agent (Claude, Sonnet 5.5) on 2026-11-02 (the session clock read 2026-11-01 while searching).
Nothing here is a result. No preregistration is written or hashed by this document; every item below still needs its
own hashed preregistration before any attempt. Probabilities, costs and ratings are **guesses** unless a source is
named. Claims by others are to be checked, never repeated as facts.

Target set by the owner: one new audited publication per day. Honest expectation: the calendar has 24 working items
and 6 reserve days; with the observed throughput (13 audited papers in about 2 days, 2 to 4 lanes) and a one-in-four
slip rate (guess), I expect 18 to 24 published items, not 30. Reserve days exist so that a slip does not break the
promise "one publication a day on average"; they can also publish a catch-up item.

## 0. Rules that every item respects

- Elenchus tiers: A = kernel-checked Lean (axioms in {propext, Classical.choice, Quot.sound}, `#print axioms`, leanchecker
  replay, statement locked); L = literature; C = exact or certified computation, or a human-style argument; X = floating point.
- Preregistration hashed and committed **before** any attempt, **in its own commit, separate from results**.
- Positive control and negative control before any number is reported.
- Producer != verifier. The auditor is a different instance and writes its **own** third checker (see section 5).
- Negative, partial and "not new" results are published. No human audit is disclosed (none exists). Never "breakthrough" or "solved".
- **Prior-art search before compute.** Of the last 13 items, 5 were recomputations of known results (EG-CB68, GR-11,
  MS-CENSUS, E2, K3). Every item gets a "searched on <date>, found X" line in its preregistration, and an OEIS / arXiv /
  Google Scholar lookup of any count or constant before it is computed.
- Cancer and medicine: no claim of cure, treatment, diagnosis, dose, device performance or climate effect; only strictly
  mathematical models of cell populations or exact rechecks of public datasets or published model claims; no patient or
  human-subject data. C2 and C3 are ON HOLD (section 1).
- Public data only, licence recorded in the preregistration; third-party full texts and datasets stay out of tracked paths
  (work in `.scratchpad/` or a staging tree outside git, then delete).
- Agentic items verify or audit public claims and systems about AI agents. Nothing is built or deployed live.

## 1. Calendar (30 days)

Legend. Direction: ENE energy, MAT materials, BIO biology, CAN cancer (math-only), MED medicine (math or public-dataset
recheck only), AGT agentic, AIC = recheck of a claim made by an AI system in mathematics (a bridge direction: it audits
claims about AI capability; I count it separately and it can absorb any slot). Type: N new, RC recheck of a claim by
others, RE recomputation of known results, LF Lean formalisation. Cost in core-hours (guess; producers plus auditor
checker). p = prior probability of a useful outcome, where "useful" means "completes with an audited verdict, any
verdict" (guess; not the probability of novelty). Risk = prior-art risk. Cores: A1 keeps core 0.
Items for days 1 to 10 are pinned (prior-art search done on 2026-11-02, section 2). Everything else is a class, to be
scouted the day before; the candidates named there were seen by title or snippet only.

| Day | Date | Id | Dir | One-line verifiable statement | Type | Source | Cost | p | Risk | Tier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2 Nov Mon | AIC-LUO | AIC | A 2-tetrahedron triangulation of L(3,1) (face pairings in the paper) has pi1 = Z/3, a null-homotopic loop edge, no solution of Thurston's gluing equations (z*w=1 forces z=1), and its Q-matching matrix has kernel vectors with at most 2 nonzero entries only along (1,0,0,1,0,0) | RC | arXiv 2610.13979 | 1 | 0.85 | low-med | C (A for the algebra only); L for Luo's theorems used in clause (iv) |
| 1 | same day | HOUSE-LOCK | all | Statement-lock procedure for Lean (section 5.3); not a paper | housekeeping | LeanMaster `tools/statement_lock.py` (to be checked) | 0.5 | 0.8 | n/a | n/a |
| 2 | 3 Nov Tue | BIO-BISTAB | BIO | Of 681 two-species mass-action networks (<= 3 internal reactions on {X,Y,2X,X+Y,2Y}, with inflow and linear removal) exactly 27 have two positive hyperbolic sinks; the 27 rational witnesses of Table 2 are valid | RC | arXiv 2610.32739 | 6 | 0.6 | med | C |
| 3 | 4 Nov Wed | AIC-MUC9 | AIC | The 182-vertex point-line graph of PG(2,9) minus 175 listed edges supports a causal linear code over F9 with 157 independent unicast sessions at rate 1, and every source-sink distance is >= 5, so any fractional multicommodity flow has common rate <= 735/785 = 147/157 | RC | arXiv 2610.10108 | 3 | 0.65 | med | C |
| 4 | 5 Nov Thu | AGT-RESTART | AGT | The alarm-to-action identity (Prop. 4.1) and the "90% accuracy swings from -5 to +35 points" example hold exactly; identity machine-checked in Lean on a finite probability space | RC + LF | arXiv 2610.36544 | 2 | 0.7 | low | C; A pending lock |
| 5 | 6 Nov Fri | ENE-TOKWATT | ENE (+AGT) | Every derived value of the TokWatt v0.1.0 tables (19 reference values, Table 5 sensitivities, Eq. 3: E Wh/day for 10^9 people = E/24 GW = 0.365 E TWh/yr, Table 6 profiles) follows from its 134-row CSV by the stated rules | RC | arXiv 2610.39846, repo AraoufBh/tokwatt | 0.5 | 0.8 | low-med | C |
| 6 | 7 Nov Sat | AIC-JC3 | AIC | The map F=(u^3 z + y^2 p(u), x u^2 z + y q(u), x+x^2 y+x^3 z), u=1-(2/3)xy, p=-(2/3)u^2-(2/9)u, q=u^2-(2/3)u-2/9, has constant Jacobian determinant -1/9 and F3 = x(1+xy+x^2 z) is reducible; Lean `ring` identity | RC + LF | arXiv 2609.17795 (van den Essen), 2610.24889 | 2 | 0.9 | **high** | A pending lock |
| 7 | 8 Nov Sun | RESERVE-1 | any | Weekly review, showcase and NewDiscoveries PR update, scheduler renewal (section 3); slip absorber | n/a | n/a | 0 | n/a | n/a | n/a |
| 8 | 9 Nov Mon | MAT-MPBORN | MAT | Born-Huang stability of Materials Project elastic tensors: exact fraction not positive definite, split by the project's own warning flags | RE (+ N for the flag split) | Materials Project API (licence to check) | 2 | 0.6 | med-high | C |
| 9 | 10 Nov Tue | AGT-AEGEAN | AGT | Safety and liveness of the Aegean leader-based multi-agent refinement protocol hold in an exhaustive state-space check for n <= 4 agents with <= 1 Byzantine | RC | arXiv 2512.20184 (not yet read) | 3 | 0.5 | med | C |
| 10 | 11 Nov Wed | BIO-R0 | BIO | For named public compartment models in arXiv 2610.29399, the learned threshold equations agree (or not) with the exact next-generation-matrix R0 | RC | arXiv 2610.29399 (abstract only) | 2 | 0.5 | med | C |
| 11 | 12 Nov Thu | ENE-2 | ENE | class: published closed-form or table claim in electrochemistry or thermal-cycle models (battery diffusion, efficiency bounds); certified enclosure or Lean monotonicity | RC | scout: alphaXiv physics.chem-ph, eess.SY, cond-mat.mtrl-sci, last 10 days | 3 | 0.5 | med | C / A |
| 12 | 13 Nov Fri | CAN-HOLD-C2 | CAN | **waiting for the human reader**: C2 (LQ fractionation theorems in Lean); not scheduled; slot is a reserve | n/a | Proposal 4 | n/a | n/a | n/a | n/a |
| 13 | 14 Nov Sat | AIC-2 | AIC | class: explicit AI-found counterexample with a finite certificate (candidates by title or snippet only: Dinitz-Garg-Goemans disproof with enumeration data; Comon 27x27x27 rank upper bounds, arXiv 2609.28292; Moreto, arXiv 2609.26471; survey arXiv 2608.29595) | RC | scout | 3 | 0.55 | med | C |
| 14 | 15 Nov Sun | RESERVE-2 | any | Weekly review (week 2), spend check, retrofit one "pending lock" Lean statement | n/a | n/a | 1 | n/a | n/a | n/a |
| 15 | 16 Nov Mon | MAT-2 | MAT | class: exact consistency or symmetry checks on a second public crystal-property dataset with a permissive licence (AFLOW, OQMD or similar; licences unchecked) | RE / N | scout | 3 | 0.45 | med | C |
| 16 | 17 Nov Tue | AGT-3 | AGT | class: arithmetic and statistical recheck of numbers in a published agent-benchmark paper (candidates: arXiv 2610.24206 SWE-Bench Pro V2, 2610.16067 oracle failures, 2610.05830 leaderboard audit, 2610.38691 misattributed numbers; none read) | RC | scout | 2 | 0.5 | med | C |
| 17 | 18 Nov Wed | BIO-2 | BIO | class: reaction-network or population-genetics theorem with a finite or algebraic certificate (candidate: arXiv 2610.30808 detailed-balance global convergence; abstract only) | RC / LF | scout | 4 | 0.4 | med | C / A |
| 18 | 19 Nov Thu | ENE-3 | ENE | class: plasma or fusion model statement with an exact inequality (follow-up of E1, ideal ignition windows); prior-art search on reactivity fits mandatory | RC / N | scout: physics.plasm-ph | 3 | 0.45 | med-high | C |
| 19 | 20 Nov Fri | CAN-A | CAN | class: a generic theorem on a birth-death or Moran process (exact fixation or extinction identity), no clinical vocabulary. **Optional**: stays a reserve until the owner accepts the wording | N / RC | scout: q-bio.PE, math.PR | 3 | 0.4 | med | C / A |
| 20 | 21 Nov Sat | AIC-3 | AIC | class: finite-census-type conjecture claimed settled by AI (the late-October scout pattern) | RC | scout: math.CO | 3 | 0.5 | med-high | C |
| 21 | 22 Nov Sun | RESERVE-3 | any | Weekly review (week 3) | n/a | n/a | 1 | n/a | n/a | n/a |
| 22 | 23 Nov Mon | MAT-3 | MAT | class: battery or solid-state structure data, a published stability or ionic-conductivity inequality; exact check | RC | scout | 3 | 0.4 | med | C |
| 23 | 24 Nov Tue | AGT-4 | AGT | class: HiveMind router follow-up (our own findings re-run read-only after the Gen 6 change) or recheck of a published scheduling-fairness claim (Jain index) | RC | `docs/studies/HIVEMIND_ROUTER_VERIFICATION_2026-11-01.md` (untracked) + scout | 2 | 0.6 | low | C |
| 24 | 25 Nov Wed | MED-A | MED | class: exact recheck of a closed-form identity in a published compartment model (algebra only, no doses, no patient numbers). Optional, same condition as CAN-A | RC | scout: q-bio.QM | 2 | 0.45 | med | C |
| 25 | 26 Nov Thu | BIO-3 | BIO | class: epidemic or ecology threshold statement with exact algebra (candidate: arXiv 2610.25971 vector abundance; unread) | RC | scout | 2 | 0.45 | med | C |
| 26 | 27 Nov Fri | ENE-4 | ENE | class: carbon-cycle or energy-system accounting identity (K-series follow-up), certified enclosure | RC / N | scout: physics.ao-ph, econ.GN | 3 | 0.45 | med | C |
| 27 | 28 Nov Sat | MAT-4 | MAT | class: lattice, polytype or elastic-tensor symmetry claim with exact algebra | RC | scout | 3 | 0.4 | med | C |
| 28 | 29 Nov Sun | RESERVE-4 | any | Weekly review (week 4), month synthesis draft | n/a | n/a | 1 | n/a | n/a | n/a |
| 29 | 30 Nov Mon | AGT-5 | AGT | class: formal check (Lean or exhaustive model) of a published agent-protocol, consensus or scheduling claim (candidates: arXiv 2606.15024, 2603.00121; abstracts only) | RC / LF | scout | 4 | 0.4 | med | C / A |
| 30 | 1 Dec Tue | CAN-HOLD-C3 | CAN | **waiting for the human reader**: C3 (containment vs MTD comparison principle in Lean); not scheduled; slot is a reserve and the month-closing review | n/a | Proposal 4 | n/a | n/a | n/a | n/a |

Balance: ENE 4 (TokWatt also touches AGT), MAT 4, BIO 4, AGT 5, AIC 5, CAN 1 optional plus 2 held slots, MED 1 optional,
reserve 4 Sundays. Medicine and cancer are thin on purpose: I found no allowed candidate that is not about doses or patients
(two pharmacokinetic papers, arXiv 2610.14719 and 2610.38325, are excluded because the topic is dosing). Absent a
candidate, those slots become reserves that BIO or AGT absorb. Days 12 and 30 are the days waiting for the human reader
(Dr Henry Maurin, a physician; the owner will ask him; this programme does not contact him). If he agrees, C2 and C3
start only after the wording rules are signed off, and only in reserve slots. They are not scheduled here.

Total planned cost of the 24 working items: about 66 core-hours (sum of the guesses above), well inside 6 cores x 30 days;
the binding constraint is model spend and audit attention, not CPU.

## 2. First 10 days: prior-art search and readiness

All searches on 2026-11-02 (planning session): alphaXiv `discover_papers` (four queries: AI-found counterexamples and
Jacobian/Dinitz; agent-benchmark audits; epidemiology, pharmacology and mass-action models; materials, plasma and energy
datasets), alphaXiv `get_paper_content`, and four WebSearch (standard) queries. "Read" means the full text or the alphaXiv
report came back; "snippet" means a search result only. Coverage is thin (a limit of two alphaXiv searches per message):
treat "not found" as "not found in these queries".

| Id | Searched, found | Read | Readiness verdict |
|---|---|---|---|
| AIC-LUO | arXiv 2610.13979 (Guo, 11 Oct 2026, math.GT). The paper says ChatGPT supplied the counterexample idea. No independent recheck found in the results; 1 vote on alphaXiv | full text | **READY.** Tiny finite computation. Caveats: reference [1] (Jaco-Rubinstein-Tillmann, Fig. 3(b)) was not opened, so "minimal" and "this is the L(3,1) triangulation" are Tier L; clause (iv) depends on Luo's Theorems 4.2(a) and 4.4 (Futer-Gueritaud), Tier L and not read. Read Luo's definitions of "cluster" and "2-quad-type" before preregistering. Compute pi1 and the gluing equations independently, not with the paper's presentation. |
| BIO-BISTAB | arXiv 2610.32739 (Peng, 23 Oct 2026, math.DS). Author says OpenAI Codex assisted and that a rational-arithmetic verifier (`verify_all.py`, `data/catalogue.json`) is shipped. Related: Lixiviant manuscript v1.1 (22 Sep 2026, cusps), Banaji-Feliu (J. Math. Biol. 2026), Banaji arXiv 2609.07265 (cited by the paper, not opened) | full text | **READY with a scope limit.** Independent code from the paper's text (do not copy the shipped verifier; its licence is unchecked). Full scope: the count 1351 -> 681, the 27 witnesses (Table 2 gives rationals), exclusion rules JAC and DIV (mechanical sign tests). ROOT (Sylvester resultant plus Descartes) and FLUX (14 networks, ray decompositions) are the heavy part; a valid partial outcome is "27 witnesses and 461 of 654 exclusions independently verified" (245 JAC + 216 DIV). Negative control: relax a sign in one witness and it must fail Sturm or Hurwitz. Prior-art risk medium because the author ships a verifier and the family is small. |
| AIC-MUC9 | arXiv 2610.10108 (Braverman, He, Princeton, 7 Oct 2026, cs.IT): refutes the undirected multiple-unicast conjecture; GPT-6 found the non-deterministic example; the paper says a "standalone symbolic verifier" and a simulator are in an accompanying repository. Concurrent: OpenAI "Finite tensor savings and exact Fourier circuits" (25 Sep 2026), cited by the paper, not opened | full text | **READY.** The appendix gives the deleted-edge set R (175), the order pi (182), the sets C and J. Checks: PG(2,9) construction, |E|=910, no 4-cycles, dimension of W >= 166 (rank over F9), degree conditions d-=d+=5, the causal interpolation giving a valid code for random inputs, the distance bound (>= 5, which also follows from girth >= 6 plus the deleted edge). The flow bound 735 < 785 is arithmetic. We do **not** verify the amplification theorem of Braverman-Garg-Schvartzman or the Omega((log n)^eps) corollary (Tier L). Pitfall: the neighbour ordering and the basis "first two triples of T in z-perp" must be reproduced exactly. |
| AGT-RESTART | arXiv 2610.36544 (Jain, Vedam, Intuit, 27 Oct 2026). Abstract: exact alarm-to-action identity; 194 executions on 19 SymPy issues from SWE-bench Verified; "zero of 103 live comparisons" certified | abstract, introduction; Proposition 4.1 body and the audit section **not read** | **READY for the identity and the 90% example after a full read of Prop. 4.1 the day before.** The trace-level numbers (2.29 and 42.29 points, 130 traces) are rechecked only if the traces are public with a recorded licence; otherwise the item says so and stops. The Blackwell-comparison background is classical: expect "the identity is elementary" and publish it that way. |
| ENE-TOKWATT | arXiv 2610.39846 (Bahi, 29 Oct 2026, cs.CY), data on GitHub AraoufBh/tokwatt; the paper states data CC BY 4.0 and code MIT (grid carbon from OWID, CC BY 4.0). My own back-of-envelope: 176/24 = 7.3 GW, 0.365 x 176 = 64 TWh, 1507/24 = 63 GW all match Table 6; that is not a check of the CSV | full text | **READY, low value.** Download the CSVs into `.scratchpad/`, confirm the LICENSE files on the day, keep them out of git. Scope: the arithmetic and the harmonisation rules, **not** the 134 transcriptions from the 13 sources (the author says every row is "human verified"; we can neither confirm nor deny that and say so). Also check from the CSV the "9 of 10 reasoning rows from Jegham" and "within a factor of 1.8" statements. Energy per AI task is not an energy-source claim. |
| AIC-JC3 | arXiv 2609.17795 (van den Essen, Radboud, 15 Sep 2026): elementary derivation of a map linearly equivalent to Alpoge's; arXiv 2610.24889 (Radboud, 17 Oct 2026): stabilisation of Alpoge's example; the first cites follow-up work by Gallagher, Gao, Speyer and Tao. Secondary web reports (letsdatascience, nocode.tech, aiweekly) attribute the original 3-dimensional example to Alpoge in July 2026 with an AI model and say it was questioned; I verified none of this | alphaXiv report (not full text) | **READY technically, prior-art risk HIGH.** The determinant -1/9 and the factorisation are one `ring` call; many people have surely done it and a Lean file may already exist (search GitHub and the Lean Zulip the day before; if one exists the item becomes "independent re-derivation" or moves to reserve). The implication "a Keller map with a reducible component is not invertible" is Tier L (invertibility preserves irreducibility); formalising it is out of scope for one day. The map must be re-read from the full text, not from the report. |
| MAT-MPBORN | Web: MechElastic (arXiv 2012.04758) applied Born-Huang checks to Materials Project elastic data (13,167 structures, 11,390 stable per the snippet, i.e. about 13.5% failing: **my arithmetic, not the paper's statement**); MP now flags failing entries with warnings and documents positive-definiteness (docs.materialsproject.org). M2 did the same on JARVIS (33.45%). Licence pages **not read**; OQMD licence seen as CC-BY 4.0 in a catalogue snippet, but with no elastic data; AFLOW licence unconfirmed | snippets only | **NOT READY.** Needs: the MP data licence recorded; a rule for counting flagged entries; the only stated novelty is the split by MP's own warning flags. If the licence is unclear, say so and swap in another dataset. Prior-art risk medium-high (a number near 13.5% already exists for an older snapshot). |
| AGT-AEGEAN | Web: Aegean, "Reaching Agreement Among Reasoning LLM Agents" (arXiv 2512.20184, Dec 2025): safety and liveness properties and a paper-level correctness proof, not mechanised per the snippet. Related: arXiv 2606.15024 (Byzantine consensus game with LLM policies), 2605.09076, 2603.00121; ePrint 2026/978 uses LLM-assisted TLA+ for Byzantine reliable broadcast (a different protocol) | snippets only | **NOT READY.** Read the protocol and lemmas first. LLM nondeterminism must be abstracted as a finite state machine, and the paper then says it checks the protocol skeleton only, not any LLM. If it cannot be finitised in a day, swap to 2603.00121. |
| BIO-R0 | arXiv 2610.29399 (REEBLRA, Univ. of the Philippines Los Banos, 21 Oct 2026): Bayesian classification to learn R0 threshold equations from simulation | abstract only | **NOT READY.** Read the full text; check whether the named public models (SIR variants, SEIR, vector-borne) have a known next-generation-matrix R0 so that the learned equation can be compared exactly (Van den Driessche-Watmough method). Model level only; no epidemiological data. |

Seen in the same searches and **not used yet** (titles or snippets only): arXiv 2610.34642 (erroneous values in
literature-mined materials datasets), 2610.38691 (misattributed numbers in agent-written papers: a fit for AGT-3),
2610.18911 (a 2026 measles model; uses outbreak data, excluded unless the data are public and non-individual).

## 3. Daily cycle and pipelines

Latency of one item is about 3 days; steady state is one publication a day because items overlap. Each day runs four
stages on four different items:

| Clock (UTC, guess) | Stage | Item | Model | Cores |
|---|---|---|---|---|
| 06:00-08:00 | Scout for day N+2: three candidates, prior-art search, full read of the chosen source, readiness verdict | N+2 | Sonnet | 1 (network) |
| 08:00-09:00 | Preregistration for day N+1: statement, controls, kill criterion, cost, tiers; hash; **commit alone** | N+1 | Sonnet writes, Opus reads | 0 |
| 09:00-17:00 | Produce day N: code, numbers, draft paper, Lean (Opus only for Lean proofs) | N | Sonnet | 2 per pipeline |
| 09:00-17:00 | Audit day N-1: independent reimplementation, third checker, review of text; verdict ACCEPT / ACCEPT_WITH_CORRECTIONS / REJECT | N-1 | Opus | 2 per pipeline |
| 17:00-19:00 | Revise day N-2 per audit, re-verify, publish on Zenodo (staging tree, links verified), update journal and roadmap | N-2 | Sonnet | 0 |
| 19:00-20:00 | GitHub: push branch, PR text (merges only on the owner's word), roadmap row | N-2 | Sonnet | 0 |

Cores (7 in total; the A1 Lean port occupies core 0 and must not be starved):

| Pipeline | Cores | Role |
|---|---|---|
| P1 (exact algebra and combinatorics: AIC, BIO, MAT) | 1, 2 | producer on 1, auditor checker on 2 |
| P2 (data and numerics: ENE, MAT, MED, CAN) | 3, 4 | same split |
| P3 (agentic and Lean) | 5, 6 | Lean builds use both cores when a proof compiles; warm the Mathlib oleans first (disk-2 cold-cache lesson) |

Use `taskset -a -cp` to recap; start long runs with `setsid nohup` (background shells die with the session). A day that
needs more than 6 core-hours moves to a reserve day; core 0 is never borrowed.

Weekly rhythm (Sundays 8, 15, 22 and 29 November; each is also a reserve day):
1. Showcase page and NewDiscoveries PR update (new records only; merge only if the owner says "merge").
2. Lessons review: read the week's audit verdicts, list recurring errors, update the checklist of section 4.
3. Spend check against the cap the owner sets (section 5); recount the yield; replan.
4. Scheduler renewal: re-create the session cron (it expires in 7 days; see 4.2).
5. Hygiene: clear third-party files from data folders; check the PREREG-first commit order with `git log`.

After each publication: add the DOI to `docs/roadmap/ROADMAP.md` and to the journal of the day, with a "Not claimed" line.
The month closes on 1 December with a synthesis: published, partial, negative, not new, and the share of rechecks of other
people's claims (guess: at least 40% of this plan; that is the honest character of the plan).

## 4. Risk register

### 4.1 API spend (the monthly limit was hit once, on 2026-10-28)

- Producers and writers on Sonnet. Opus only for audits and Lean proofs. No silent model swap.
- Ledger: every lane writes tokens or cost per item (the APIExtractor JSONL already logs calls).
- Throttle rule (percentages of the weekly cap the owner sets; thresholds are my proposal): below 70% normal; at 70% stop
  starting new items, finish audits and publications; at 90% audits and publication only; at 100% pause everything.
- On a limit hit: stop, write BLOCKED with the time in the journal and roadmap, do not retry in a loop, do not use a
  weaker model for audits, resume at the reset with the oldest unfinished item first. Reserve days absorb the loss.
- Keep scouting cheap: full text only for the chosen item.

### 4.2 Scheduler

The daily cron is session-only and expires after 7 days. Renew it every Sunday; keep each stage idempotent and
resumable from files (preregistration hash, results directory, audit file) so a dead session loses at most one stage; a
system cron or timer launching a headless run is an owner decision (section 5). An unattended job never publishes to
Zenodo or pushes to GitHub without the owner's standing approval; at most it scouts and audits.

### 4.3 Lean statement-lock gap (Tier A is "pending lock" everywhere) and a day-1 procedure

Proposal for day 1 (time box 2 hours; the owner approves before use):
1. Check whether LeanMaster's `tools/statement_lock.py --check` (and the `check_statement_lock` MCP tool) can be pointed
   at files in `formal_cert/`. If yes, adopt it. If not, write a script of about 40 lines.
2. For each theorem, before any proof attempt, write `statements/<ID>.lock.json`: theorem name; SHA-256 of its elaborated
   type printed with `pp.all true`; the same hash for every definition it depends on (transitive closure from `#print`);
   the toolchain string (4.34.1); the import list.
3. Commit the lock file together with the preregistration and **before** the proof file exists; record the commit hash.
4. After the proof: rerun on the final file and require identical hashes; run lean_runner (`#print axioms`, whitelist,
   `sorryAx` rejected) and a leanchecker replay; the auditor recomputes the hashes independently.
5. Retrofit one existing "pending lock" item per reserve day (SLR-18 covering statements, K3, E3, then the rest). Until a
   lock exists the paper keeps the words "A pending statement lock".
Limit: a hash fixes the statement as elaborated, not its meaning. A plain-language gloss in the preregistration and an
auditor reading the gloss against the Lean text remain necessary.

### 4.4 Other risks

| Risk | Why | Mitigation |
|---|---|---|
| Recomputation of known results (5 of 13 recently) | the scout finds papers that already did the computation | mandatory prior-art line; OEIS and author-repository check before compute; a recheck is labelled a recheck in the title |
| Unverifiable claims | an AI-lab announcement with only secondary reports | no preregistration without a primary source and a finite certificate; otherwise log "claim not checkable" |
| Third-party licences | shipped verifiers, CSVs, appendices | licence recorded in the preregistration; our own code from the paper's text; data in `.scratchpad/` only |
| Correlated checkers | producer-written checkers share the producer's misreadings | require an auditor-written third checker by a different algorithm; the paper lists what was independent |
| Outward rounding | E2 bug | interval or ball arithmetic with outward rounding; the auditor tests the direction of every rounding |
| Misattributed quotations; unverified URLs and DOIs | LR-IND; a guessed URL once redirected to a portal | quote only text actually read in the session; fetch every link and DOI before publishing |
| Third-party texts in data folders | recurring | scrub step before every commit and Zenodo bundle |
| PREREG committed together with results | recurring | separate commit; the auditor checks `git log` order and the hash |
| Over-claiming | a checker verifies a program, not the paper's proof | a "does not verify X" sentence per item (as in MS-CENSUS) |
| Same model family for producer and auditor | both are Claude models | state it; the independent algorithm and the third checker are the real safeguard |
| Wording in cancer and medicine items | harm if read as clinical | held for the human reader; no dose, patient or diagnosis vocabulary; only generic theorems |
| Lean build cost | partial Mathlib build; never `import Mathlib` | pin imports to built modules; at most one Lean item a week per pipeline |
| Core starvation of A1 | other jobs spill | never core 0 |

## 5. What the owner decides

1. **Weekly budget cap** (currency or tokens) and the throttle thresholds of 4.1. Without a cap the plan runs three
   pipelines for 30 days at a cost I cannot estimate (the 28 October limit shows it is not small).
2. **Statement-lock procedure** (4.3): approve or amend; whether Tier A may be written without it (I say no).
3. **Contacting original authors** of rechecked works (arXiv 2610.13979, 2610.32739, 2610.10108, 2610.36544, 2610.39846):
   none by default; a neutral note after publication needs the owner's wording.
4. **How much more to formalise in Lean**: this plan has two Lean items (AGT-RESTART, AIC-JC3) plus optional ones; more
   Lean competes with A1 for disk and cores.
5. **Human-reader wait**: C2 and C3 stay on hold (days 12 and 30 are the waiting slots); CAN-A (day 19) and MED-A
   (day 24) are scheduled only if the owner accepts their generic-theorem wording, otherwise they become reserves.
6. **Unattended running**: a system cron or timer on the machine for scout, preregistration, produce and audit (never
   publish), or session-bound running with weekly renewal.
7. Whether rechecks of AI-lab claims (5 of the 24 working slots) should be a standing lane or be capped.
8. Whether Zenodo records stay one per item or are bundled weekly.

## 6. Not claimed

No cure, treatment, diagnosis, dose, device performance, climate effect, new energy source or deployable material. No
human has audited this plan or any item. The plan lists candidates; none of the listed statements has been checked by us.
