# Referee report, round 3 of 3: novelty, positioning and claims

Manuscript: `papers/cosmo_synthesis/cosmo_synthesis.tex` (draft of 2026-09-27, revised after
round 2). Rebuilt by this referee on 2026-09-27: `pdflatex -interaction=nonstopmode` twice,
rc 0 / rc 0, 23 pages, 753,892 bytes, no undefined references or citations, no overfull
boxes, 16 cosmetic LaTeX warnings.

Referee: a Claude model agent (Claude Code), NOT a person. Lens: novelty, positioning and
claims. Numerical correctness is out of scope; every number quoted from the manuscript is
quoted, not re-derived.

Sources: every statement below about a cited or candidate paper comes from text returned by
the alphaXiv MCP tools (`discover_papers`, `answer_pdf_queries`) on 2026-09-27 in this
session. Six `discover_papers` sweeps were run (exact inputs in Sec. 5); 14 papers were read
by targeted PDF query. Nothing is from memory. Local files read: the `.tex`, the generated
macro file, the two prior novelty reports, the two response letters, the two search logs,
`docs/literature/BAO_BBN_H0_LITERATURE_REVIEW_2026.md`, and the listing of
`results/*/fit*.json`. Nothing outside `papers/cosmo_synthesis/reviews/` was written.

Recommendation: **minor revision**. No claim in the manuscript is false or unsupported; the
honesty that the cosmology values are reproductions is complete, and every citation added in
rounds 1-2 that I re-fetched says what the manuscript says it says. What remains is that the
literature the "what is new" section is measured against still has two holes that a sweep
without the word "BAO" fills on its first page: (i) three agent-executed *reproduction*
pipelines that are closer in purpose to this paper than cmbagent or JFC, and (ii) two
DESI-side papers that bear directly on the H0 tolerance discussion and on the derivation of
the DR1->DR2 "nested sigma". Neither makes a claim false; both change how the nearest
neighbours read.

---

## 1. Were the round-2 novelty issues fixed?

Checked against the revised `.tex`, `round2_response.md`, `literature_search_log_round2.json`
and the re-fetched sources.

| round-2 item | claimed status | verified? |
|---|---|---|
| F1 (major) TOPO uncited | FIXED | **mostly**. Cited at l. 425 (blinding paragraph), l. 435 (novelty item 1), l. 483 (Limitations). The description (signed Analysis-Hash of code commits + input files, timestamped medium with a blockchain example, Merkle roots over the time-ordered chain, verifier re-runs a prefix, Cobaya/CLASS demo on BAO likelihoods incl. SDSS DR16) holds against 2411.00072v2 Secs. 3.1-3.3, 5.1. **Not** cited in Sec. 3.2 (protocol amendment, ll. 104-132), which round 2 also asked for; the response letter does not claim it. See F5. |
| F2 (major) AI Cosmologist, JFC, Gandhi et al. | FIXED | yes. 2504.03424: "autonomous", "without manual intervention", GZ2 + Quijote ML tasks, no reproduction of a published constraint: holds (abstract, Sec. 1, Sec. 4.1). 2603.20179v3: "multi-agent review replaces the human feedback loop ... single formal unblinding gate" (Sec. 2.1, verbatim), append-only experiment log (Secs. 3.1, 3.7), Asimov -> 10% -> full with human APPROVE/REQUEST CHANGES/HALT (Sec. 3.8), CMS H->tau tau "consistent with the published CMS mu tau_h measurement" (Sec. 4): all hold. 2511.14631: plots as checkpoints, VLM judge against dynamically generated rubrics, "auditable reasoning traces" (abstract, Sec. 3.1): holds. The manuscript's added sentence that JFC is *stronger* (staged blinding + human gate) is accurate and is a fair concession. |
| F3 (minor) Denario review module | FIXED | yes (l. 402). |
| F4 (minor) DR2's 1.9/2.6 sigma LRG2 figure | FIXED | yes (ll. 362-367), with the 2.3/1.5 sigma reanalysis figures added so the quote is not selective. Not re-fetched this round; round 2 verified the page. |
| F5 (minor) search log | PARTLY FIXED, as disclosed | `literature_search_log_round2.json` says honestly that no new keyword sweep was run and that the round-2 papers were supplied by arXiv id. The consequence is that the authors' own search has still never covered agentic reproduction outside cosmology/HEP. See F1 and F4 below. |
| F6, F7 (optional) | mostly NOT DONE, as disclosed | PhysProver/AxQM not read, Ferri caveat not re-verified, ReplicationBench Sec. 5.3 not verified; subtitle fixed. Acceptable. |

The response letter's three "referee specifics we could not verify and did not use" are
handled correctly: not asserting them is the right call.

## 2. Verification of citations added or changed in round 2

| bib key | arXiv | attributed | verdict from fetched text |
|---|---|---|---|
| topo2024 | 2411.00072 | see F1 row above | holds in every clause. One addition the authors may use: TOPO describes itself as "a trustless alternative to data analysis blinding" (abstract), which supports the manuscript's placement of it inside the blinding paragraph. |
| moreno2026 | 2603.20179 | Claude Code orchestrator delegating to executor/reviewer subagents; append-only log; CMS consistency; staged blinding; human gate | all hold (Secs. 2.1, 3.1, 3.2, 3.7, 3.8, 4). Also relevant to F3 below: JFC records its model ("Opus 4.8", Sec. 3.1) and notes the DELPHI runs used "Claude Opus 4.6" (Table 2 footnote). |
| moss2025 | 2504.03424 | autonomous; ML tasks, not reproductions | holds. |
| gandhi2025 | 2511.14631 | VLM-judged plot checkpoints, generated rubrics, auditable traces | holds. |
| denario2025 | 2510.26887 | Review module writes `referee.md` | verified in round 2; not re-fetched. |

Bibliographic details (author lists, titles, arXiv ids) of the four new entries match the
fetched first pages.

Verdict on honesty about reproductions: unchanged, complete (abstract, Sec. 1, Sec. 5 "Not
new", Sec. 4 "a pull is a measure of reproduction accuracy, not an independent-sample
significance").

## 3. Findings

### F1 (major) Three agent-executed reproduction pipelines are closer in purpose than the cited precedents and are not cited

The manuscript's title is "An agent-executed, preregistered reproduction pipeline"; its
prior-work paragraph opens "The most direct precedent is cmbagent" and names JFC "the closest
architectural precedent". One `discover_papers` sweep on autonomous agents reproducing
published results (no "BAO" keyword; Sec. 5, sweep 1) returned, on its first page, three
papers whose subject is exactly agent-executed reproduction of a published result. I read all
three.

- **SHARP, "A Scientific Human-Agent Reproduction Pipeline", Birk, Kasieczka, Mishra-Sharma,
  Nachman, Noll, Wamorkar, arXiv:2604.18752v2** (PAI 2026). Built on Claude Code v2.1.92 with
  claude-opus-4.6 (Sec. 2). The reproduction target and its numeric metrics are fixed in the
  initiating prompt ("Reproduce accuracy, AUC, and 1/eps_b results", Prompt 1); the agent
  delegates to Paper Analyst, Code, Test, Statistician and **Critic** subagents; the human
  reviews at checkpoints. It reports **three independent runs** against the published
  ParticleNet-Lite numbers (Table 1) and validates checkpoints with "an external evaluation
  script written by a human expert". Its limitations paragraph names "subtle implementation
  differences from the paper" and a truth-label-leakage failure "undetected by automated
  tests", the same class as this manuscript's N4 control. It positions itself explicitly
  between "fixed, task-specific pipelines" and "free-form agent workflows such as the Just
  Furnish Context [JFC]".
- **Huang, "Grounded autonomous scrutiny at scale: emergent critique from reproduction of
  published computational physics papers", arXiv:2604.12198v2** (ICML 2026 AI4Science
  workshop). Claude Code + Opus 4.6, no tool layer, reproduces **111 open-access Quantum
  ESPRESSO papers** end to end: "75.8% [of 571 claims] within 5% and 83.2% within 10% of the
  published value, with a median deviation of 0.9%"; a four-tier verdict scale (T1-T4); a
  12-paper two-machine cross-check "with no shared state"; and the finding that 85 of 88
  substantive critiques "emerged only after the agent had actually run a calculation". Its
  camera-ready "Note added" records that a human reviewer's *reading* caught an interpretation
  error and citation-fidelity lapses that the model-only pipeline missed, and says plainly
  "execution grounds numbers; it does not by itself protect setup choices, interpretation, or
  citation fidelity". That sentence is the published counterpart of this manuscript's "No
  person has reviewed any component."
- **Huang, "Grounded autonomous research: a fault-tolerant LLM pipeline from corpus to
  manuscript in frontier computational physics", arXiv:2607.02329v1** (ICML 2026 AI4Science
  workshop). Its "pilot" stage reproduces k = 5 published anchors before any new computation
  and its review sessions are "adversarial review in fresh context ... prompted to find rather
  than confirm"; it quantifies human intervention (Table 2: nine operational events, zero
  scientific). Two points bear on this manuscript: (a) a no-pilot ablation shows that an agent
  with the published anchor value in its files still never wrote the comparison "0.066 vs.
  0.176", which is the failure mode preregistered targets and tolerances are meant to prevent;
  (b) its "Note added" reports that the published anchor value itself "is not a converged
  observable", i.e. reproduction against a published number certifies "consistency with
  published literature, not truth". The manuscript's DR1 chi-squared offset and its use of
  DESI posterior means as targets sit in the same epistemic position and would be well framed
  by that sentence.

Why this matters for the claims:

1. "The most direct precedent is cmbagent" is defensible for *cosmology*, but for
   *agent-executed reproduction of a published result against numeric targets* SHARP is the
   most direct precedent, and Huang 2604.12198 is the only prior at-scale measurement of how
   often such reproductions agree with the published value. A reader of Sec. 5 currently
   cannot see either.
2. The manuscript's benchmark sentence "faithful reproduction is hard for agents" (22%, 34%,
   zero end-to-end) is one-sided next to 75.8%-within-5% (Huang) and 0.1-percentage-point
   agreement (SHARP). The honest reading, which also fits this manuscript's own 4-for-4, is
   that success depends on whether the inputs are public summary files with a stated
   estimator; one sentence should say so.
3. Novelty item 1 ("the combination") survives: none of the three preregisters tolerances,
   hash-locks an unread result, kernel-checks model identities, or keeps a tier-capped ledger.
   But "we did not find these items combined in the literature we searched" is measured
   against a search that, per `literature_search_log_round2.json`, never ran on this axis.

Required: cite all three in Sec. 5 with one clause each (SHARP: Claude Code reproduction
pipeline with prompt-fixed numeric targets, three runs, human checkpoints; Huang 2604.12198:
111-paper autonomous reproduction with a graded verdict and cross-machine check; Huang
2607.02329: pilot reproduction of published anchors plus fresh-context adversarial review, and
the anchor-itself-unconverged caveat). Reword "most direct precedent" to distinguish the
cosmology precedent (cmbagent) from the reproduction-pipeline precedent (SHARP). Qualify the
"hard for agents" sentence.

### F2 (major) Two DESI-side papers bear on the H0 tolerance discussion and on the nested-sigma derivation and are not cited

(a) **Akharman, DePorzio, Giovanetti, Liu, "The Role of Big Bang Nucleosynthesis in Joint
Cosmological Analyses", arXiv:2609.12065v1, 10 Sep 2026.** An independent BAO+BBN analysis of
DESI DR2 with a full BBN likelihood (CLASS r_d, one 0.06 eV neutrino, the same public
`desi_gaussian_bao_ALL_GCcomb` files as this manuscript). Fiducial h = 0.6833 (+0.0048/-0.0053)
with PRIMAT; "a modest spread in h across the three reaction networks considered here, up to
roughly 0.5 sigma"; and the explicit remark that "the DESI DR2 analysis uses a prior on the
baryon density from just one reaction network [PRyM/YOF]" (Secs. 1, 3.1, Fig. 1). This was on
arXiv 17 days before the H0 literature review (dated 2026-09-27) and is not in it. It matters
for positioning in two ways: the manuscript's strict window of 0.15 km/s/Mpc (0.26 sigma) and
its 10^-5-level N_eff discussion (Sec. 4.3) sit below a published reaction-network systematic
of ~0.5 sigma (~0.3 km/s/Mpc) in the very quantity being reproduced, so the T1 PASS / T2
PARTIAL boundary should be described as lying inside a known systematic, not only as
"incoherent" with the BAO-only gates; and 2609.12065 gives a third, non-DESI BAO+BBN number
(and Omega_m = 0.2991 +0.0095/-0.011, Table 2) that a reproduction paper should place next to
its own 68.545 and DESI's 68.51. No verdict changes; the manuscript already refuses to
re-budget post hoc. Required: cite in Sec. 3.3 or 4.3 and in the "Incoherent H0 tolerances"
limitation, one or two sentences.

(b) **Kim, Mota, Tamosiunas, "A Sequentially-Valid Reanalysis of DESI's Dynamical Dark Energy
Signal", arXiv:2607.28918v1, 31 Jul 2026.** Not about Omega_m, so novelty item 2(a) survives.
But it is the prior work that models the DR1-inside-DR2 nesting explicitly: DR2 = mu + (1/3)
eps_y1 + (2/3) eps_y23 (their eq. B.1), "the treatment of nested survey releases in Appendix
B.2 is new", and it checks the year-scaling assumption against the published covariances:
"the published covariances straddle that ratio bin by bin (0.22-0.49, median 0.32) without
satisfying it" (Appendix B.2). The manuscript's Sec. 4.5(a) argues "with sigma ~ N^{-1/2} this
is the nested form for the galaxy and quasar bins". 2607.28918's per-bin ratios are the direct
empirical test of that step and show it holds only approximately. Required: cite it in Sec.
4.5(a) as the prior explicit treatment of the nesting, and note that the per-bin C_DR2/C_DR1
ratios span 0.22-0.49 so sigma_nested is an approximation, which is consistent with the
manuscript's own bracketing by the C=1 and independent conventions.

Also seen and read: **Forero-Sanchez et al. (DESI), arXiv:2602.18761**, which estimates the
DR1xDR2 cross-covariance from EZmocks for the DR1 full-shape x DR2 BAO combination (Secs. 2.2,
3.4) and finds the cross terms "have little effect ... causing only minor shifts in h and
Omega_m" (Sec. 4.2). Optional one clause in 4.5(a) as DESI's own mock-based treatment of the
DR1/DR2 correlation.

### F3 (minor) Producer and verifier are the same model family; the manuscript should say so, and the peer systems record what this one cannot

The AI-use statement says Lean and "the refuting review run on Fable; fits and papers use the
default model", and that the default model's identity is unrecorded. All of these are Claude
models run in Claude Code. The manuscript never states that the adversarial referee and the
analysis author share a vendor and training lineage, so "producer != verifier" holds only at
the model-tier level. Two fetched papers make this a positioning point rather than a quibble:
2607.28631 (Ravideshik & Kejriwal, "Can AI Evaluate AI Scientists?") finds Gemini and Claude
reviewers agree at rho = 0.907 while GPT-5.4 agrees with either at rho ~ 0.32, i.e. automated
review verdicts are reviewer-family dependent; and JFC/SHARP/Huang all record their model
versions (Opus 4.8 / claude-opus-4.6 + Claude Code v2.1.92 / Opus 4.6) and JFC reports a
cross-model comparison. Required: one sentence in the "Tier A is model-audited" limitation
naming the same-family referee, with 2607.28631 as the reason it matters. Optional: state
explicitly that each of the four problems was executed once by the agent pipeline (the
artifacts show one `fit.json` per run; the DR2 fix-round "bit-for-bit identical" regeneration
is a fixed-seed re-execution of scripts, not an independent agent run), so no run-to-run
statistics exist, in contrast to SHARP's three runs and Huang's cross-machine check.

### F4 (minor) The documented search still does not cover the axis that produced F1

Both search logs are cosmology/HEP-scoped, and the round-2 log says no new sweep was run. My
sweep 1 (Sec. 5) differs from the round-2 referee's sweep 1 only by dropping "BAO" and adding
"reproduce"/"published results"; SHARP and both Huang papers came back on its first page.
Required: add the sweep (or an equivalent) to the log, and keep the hedge "within the limits
of that search". Optional: the same sweep on benchmarks returned SA-Bench (arXiv:2608.24252,
read), which defines "semantic drift" for paper-to-code reproduction with a four-type taxonomy
(numerical, method/formula, protocol, step ordering); the manuscript borrows the term only
from FormalScience for the Lean side, whereas its code-side deviations (G1 passed where G2 was
named; `BAO_TensionStatistic.lean` shipped as `BAO_Consistency.lean`; the H0 monotonicity
theorem replaced by identities) are protocol and method drift in SA-Bench's terms.

### F5 (minor) TOPO is still absent from Sec. 3.2

Round 2 asked for the citation in Sec. 3.2 (the hash-lock is introduced at ll. 108-110), the
blinding paragraph, novelty item 1 and Limitations. The last three were done; Sec. 3.2 was not,
and the response letter does not claim it. A reader who reaches the hash-lock in Sec. 3.2
meets it as the paper's own device and learns of TOPO ten pages later. One `\cite`.

### F6 (minor) Checks that came back clean

- **BAO-only DR2 wCDM h r_d "no published value was found"**: 2510.09074 (Yadav et al.,
  "Investigating the wCDM Model with Latest DESI BAO Observations", read) uses DESI 2024 (DR1)
  and BAO+BBN(+OHD+SN) combinations, not BAO-only DR2, so it is not a counter-example. The
  claim stands as far as my search went.
- **Formal side**: the Lean sweep (Sec. 5, sweep 3) returned no formalization of FLRW
  distances, BAO or cosmological background quantities (hits: 2210.12150 chemical physics in
  Lean, 2608.21502 Hamilton's theorem, 2609.16801 Landau damping, 2609.05157 AxQM, 2607.05492
  Lean-Quantum, 2606.14867, 2608.28433). Consistent with rounds 1-2. If the authors want the
  earliest physics-in-Lean precedent, 2210.12150 (2023) is it; I read only its listing line.
- **Preregistration/blinding sweep** (sweep 2) returned nothing beyond what rounds 1-2 found
  (TOPO, Muir et al. 1911.05929, Smokescreen 2604.18111, DESI bispectrum blinding 2407.12931,
  Lya AP blinding 2607.07875). The manuscript uses "preregistration" without citing the
  practice's own literature; 2010.10513 ("Does preregistration improve the credibility of
  research findings?") surfaced but I did not read it, so I do not prescribe it.
- **Title and subtitle**: the round-2 cosmetic fix ("three preregistered ... and one earlier
  reproduction") is in place and accurate.

### F7 (minor) Wording

- Sec. 5, "In the pages of JFC and cmbagent that we read we did not find preregistered numeric
  targets or hash-locked results; we do not claim that they lack them." After F1 this sentence
  should also cover SHARP, whose initiating prompt *does* fix the numeric targets (without
  tolerances or a lock); saying so sharpens what is different here (tolerances, controls,
  hash-lock) rather than what is shared (targets).
- Sec. 5, JFC sentence: the manuscript's phrase "checked against, and consistent with, a
  published CMS measurement" is JFC's own wording and is correct; JFC also says the result
  "rebuilds point-by-point in an independent Combine implementation" (Sec. 4), which is the
  analogue of this manuscript's Rust port and could be named in Sec. 3.7 in one clause.

## 4. What survives

- Reproductions-not-measurements honesty: complete.
- Novelty item 1 (the combination): survives as hedged. Nothing I read combines preregistered
  tolerances, a hash-locked unread result, kernel-checked model identities with an axiom
  audit, a tier-capped ledger, a re-running model referee and a second-language port on an
  agent-executed reproduction. After F1 the nearest neighbours on the *reproduction* axis are
  SHARP and Huang 2604.12198 rather than cmbagent, and the text must say so.
- Novelty item 2(a), DR1->DR2 shift in nested sigma: survives; 2607.28918 models the nesting
  but for (w0, wa) evidence, not Omega_m. The derivation's sigma ~ N^{-1/2} step should cite
  2607.28918's per-bin ratios (F2b).
- Novelty item 2(b), narrowed SDSS-DESI DR2 N_sigma: survives; nothing new found this round.
- Novelty item 3 (process audit and failures): survives and remains the most defensible
  contribution.
- All five citations re-verified in Sec. 2 resolve to the right papers and say what the
  manuscript says.

## 5. Search record for this round (exact inputs)

`discover_papers`, all on 2026-09-27:

1. keywords ["LLM agents","cosmology","reproduce","published results","autonomous","parameter
   constraints"], prioritize recency, difficulty 8. Hits: 2605.14791*, 2507.07257*,
   2606.11157*, 2604.03691, **2604.12198**, **2607.02329**, 2604.09621*, **2604.18752**,
   2606.19427, 2601.14288. (* already cited)
2. keywords ["preregistration","blinding","cosmology","hash","commitment","reproducibility",
   "provenance"], difficulty 8. Hits: 2604.18111, 2407.12931, 2411.00072*, 1911.05929,
   2607.07875, 2205.11262, 2511.05470, 2505.24675, 2501.14651, 2010.10513.
3. keywords ["Lean 4","formalization","cosmology","FLRW","general relativity","Friedmann",
   "physics","proof assistant"], difficulty 8. Hits: 2210.12150, 2608.21502, 2609.16801,
   2609.05157, 2607.05492, 2606.14867, 2608.28433.
4. keywords ["DESI DR2","BAO","reanalysis","independent","Omega_m","r_d h","flat LCDM","BBN",
   "H0"], prioritize recency, difficulty 8. Hits: **2609.12065**, 2607.13009, **2607.28918**,
   2510.09074, 2209.14330.
5. keywords ["DESI","DR1","DR2","parameter shift","consistency","nested","correlated",
   "Omega_m"], difficulty 8. Hits: 2606.23936, 2608.01844, **2602.18761**, 2512.06086,
   2503.14742, 2608.27830, 2608.19883.
6. keywords ["AI scientist","automated review","referee agent","reproducibility","paper
   reproduction","benchmark","physics","astronomy"], prioritize recency, difficulty 8. Hits:
   2603.27646*, 2605.13950*, 2604.15664, 2604.15411, 2606.24530, 2606.18648, 2607.02931,
   2609.11117, **2607.28631**, 2606.07591, 2608.13331, 2604.12198, **2608.24252**.

Read by `answer_pdf_queries` (page text returned): 2603.20179, 2411.00072, 2504.03424,
2511.14631, 2604.18752, 2604.12198, 2607.02329, 2609.12065, 2607.28918, 2510.09074,
2608.24252, 2607.28631, 2602.18761. Everything else named above was seen only as a listing
line and is not asserted beyond its title.

No alphaXiv call failed in this session.

## 6. Summary of required changes

1. Cite SHARP (2604.18752) and Huang (2604.12198, 2607.02329) in Sec. 5; distinguish the
   cosmology precedent from the reproduction-pipeline precedent; qualify "faithful
   reproduction is hard for agents" (F1).
2. Cite 2609.12065 next to the H0 strict window and in the tolerance limitation; cite
   2607.28918 in Sec. 4.5(a) for the nesting treatment and the 0.22-0.49 per-bin ratios (F2).
3. State that referee and author are the same model family, citing 2607.28631; optionally
   state that each problem was one agent execution (F3).
4. Log the missing sweep (F4). Add `\cite{topo2024}` in Sec. 3.2 (F5). Wording items (F7).
