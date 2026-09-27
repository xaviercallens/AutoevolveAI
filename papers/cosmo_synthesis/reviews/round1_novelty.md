# Referee report, round 1 of 3: novelty, positioning and claims

Manuscript: `papers/cosmo_synthesis/cosmo_synthesis.tex` (draft of 2026-09-27; tex sha at
review time is the working-tree file; rebuilt by this referee with `pdflatex` x2 on
2026-09-27, exit 0, 0 undefined citations, 19 cosmetic warnings: float `h`->`ht` and
hyperref Unicode-in-bookmark).

Referee: a Claude model agent, NOT a person. Lens assigned: novelty, positioning and
claims. Numerical correctness of the fits is out of scope for this round.

Sources read for this review, all through the alphaXiv MCP `answer_pdf_queries` /
`discover_papers` tools on 2026-09-27 (every page quoted below was returned by the
tool; nothing is from memory): the eight prior-work papers the manuscript cites
(2412.00431, 2604.09621, 2605.14791, 2606.11157, 2510.24591, 2603.27646, 2405.08863,
2603.08139); the target papers 2503.14738 (v3) and 2404.03002 (v3); and, found by
search, 2408.04432, 2607.07348, 2404.07282, 2607.10039, 2604.23002, 2605.13950.
Two `discover_papers` sweeps per theme were run (agentic reproduction / AI scientists in
cosmology; formal verification of physics; DESI DR2 and SDSS-vs-DESI re-analyses;
preregistration and blinding in cosmology).

Recommendation: **major revision**. No claim is false as written, but two of the three
novelty claims are positioned against an incomplete literature, and the title says more
than the paper does.

---

## 1. Verification of the eight prior-work citations

| bib key | arXiv | title/authors match | attributed claim | verdict |
|---|---|---|---|---|
| laverick2024 | 2412.00431 | yes (Laverick, Surrao, Zubeldia, Bolliet, Cranmer, Lewis, Sherwin, Lesgourgues) | reproduced ACT DR6 lensing constraints; human approval at each step; "no way to confirm outputs without redoing the analysis independently" | **holds**. p.4: "we require human feedback at all stages"; p.6: "successfully reproduced the results presented in Madhavacheril et al."; p.9: quote verbatim. |
| borrett2026 | 2604.09621 | yes | "agent-driven inference pipelines in which human redirection was decisive" | **holds** (p.7-8: "our best score was obtained with human intervention"). Note it is a weak-lensing *competition*, not a reproduction of a published result; say so. |
| xu2026 | 2605.14791 | yes (Xu & Borrett) | "agentic cosmology frameworks and their caveats" | **holds** (p.4 caveats on AI-generated ACT diagnostics). |
| darkagents2026 | 2606.11157 | yes (Lucente, Pascoli, Sala, Zandi) | "audits assumptions and compares its results against a human analysis" | **holds** (Sec. 3.1, Fig. 2). It also reports "made-up references in the final pdf reports" (p.9), which is worth citing next to PRBench's fabrication finding. |
| replicationbench | 2510.24591 | yes (Ye et al.) | "best model scores about 22% on expert-written astrophysics replication tasks" | **holds** with a caveat: Sec. 5.1 and Table 3 give Claude 4.5 Sonnet 0.22 average; the same paper's abstract says "under 20%" and its discussion "just above 20%". Quote "22% (Claude 4.5 Sonnet, Table 3)" so a reader who checks the abstract is not confused. |
| prbench | 2603.27646 | yes (Qiu et al., PKU) | "zero end-to-end success rate and documents fabricated outputs" | **holds** (abstract; Sec. 4.2 "End-to-End Callback Rate is 0% for all evaluated agents"; Sec. 5.2.1 "Data Fabrication"). Best overall score is 34%; consider quoting it. |
| heplean | 2405.08863 | yes (Tooby-Smith) | "HepLean/PhysLib formalizes high-energy physics in Lean 4" | **holds**, naming nit: 2603.08139 p.1 says the library is now "Physlib (recently renamed from PhysLean and Lean-QuantumInfo)". Write "HepLean (now Physlib)". |
| toobysmith2026 | 2603.08139 | yes | "a Lean formalization found a genuine error in a widely cited 2HDM stability theorem" | **holds** (abstract: "invalidating their main theorem"; Sec. 5). Note the paper itself says "no extensive use of AI in the formalization", which contrasts with this manuscript's model-written statements; worth one sentence. |

Data-paper bib entries: `eboss2021` title is truncated (the paper's title ends "...at the
Apache Point Observatory"); `dmdb2020` is a paraphrase of the real title. Neither is
wrong, both should be exact.

**Verdict on honesty about reproductions.** The abstract ("The cosmological values are
reproductions, not new measurements"), the introduction ("This paper does not claim new
cosmology") and Sec. "What is and is not new" ("Nothing here is a new measurement or a
new constraint") are unambiguous. This is done correctly and I have no finding here.

---

## 2. Findings

### F1 (major) The title overclaims: "machine-checked reproduction pipeline"

Sec. 3.4 states, in bold, that the Lean theorems "do not verify the fits, the data
handling or the numerics", and Sec. "Limitations" repeats that they "do not certify any
fit". What is machine-checked is 28 elementary identities (positivity, monotonicity,
distance duality, the (h, r_d) degeneracy). The title nevertheless calls the whole thing a
"machine-checked reproduction pipeline", which a reader will take to mean the
reproduction is machine-checked. It is not; the reproduction is checked by a model
referee re-running scripts. Retitle (e.g. "...an agentic, preregistered reproduction
pipeline for BAO cosmology with kernel-checked model identities") or drop
"machine-checked" from the noun phrase it currently modifies. Same issue, weaker, in the
abstract's first sentence, which lists Lean in the same breath as the fits.

### F2 (major) Preregistration is positioned in a vacuum; blind analysis is the field's existing safeguard and DESI's own analyses are blind

Novelty item 1 lists "preregistered targets and tolerances" and "an amendment that
hash-locks an unread earlier result" as safeguards not found combined elsewhere. The
manuscript never mentions blinding (grep of the .tex: zero hits). But:

- Both target papers are blind analyses. 2404.03002 abstract: "To mitigate confirmation
  bias, a blind analysis was implemented to measure the BAO scales." 2503.14738 Sec.
  II.A.1 is titled "Blinding" and Sec. IX: "we applied a strict catalog-level blinding
  to our data while ... the analysis pipeline was being finalized. The validation tests
  and the criteria that were required to be met before the data were unblinded are
  described in detail in the supporting publication [48]."
- The DESI blinding scheme has its own validation paper, Andrade et al. arXiv:2404.07282
  (JCAP 01 (2025) 128), whose Sec. 3.4 "When to Unblind: Criteria and Tests" is exactly a
  pre-specified pass/fail protocol; its Sec. 2 reviews blinding in SNe, KiDS and DES and
  cites Brieden et al. 2020 "Blind Observers of the Sky" (its ref. [22], arXiv:2006.10857)
  for the BAO/RSD catalog-level method.
- Grosso, Mikuni & Heinrich arXiv:2607.10039 (VERaiPHY / PHYSTAT review, July 2026)
  argues, for agentic systems specifically, that "Similar to blind analyses [83], it is
  essential that agentic systems use only simulated samples when performing optimization
  routines, while reserving the observed data for the final statistical test", and
  states that "No analogous verification infrastructure [to Lean] exists for physics
  analyses ... making the development of such scaffolding one of the central open
  problems for trustworthy agentic science." That is the sentence this manuscript is a
  partial answer to; it must be cited, and the paper's contribution should be framed
  against it.

Required: a paragraph relating preregistration + hash-locking to blinding (the
hash-locked unread fit *is* a one-shot blinding of the analyst), citing 2404.07282 and
2607.10039, and stating that the target analyses were themselves blinded. Without this the
"combination of safeguards" claim is measured against the wrong baseline.

### F3 (major) Derived quantity (b), the SDSS-DESI tension, ignores published SDSS-vs-DESI consistency tests

The manuscript's scoping sentence is carefully worded ("not quoted in the fetched text of
[desi2025dr2, desi2024vi]") and remains true. But novelty item 2 then calls the SDSS-DESI
DR2 N_sigma one of "three derived consistency numbers" that are new, and Sec. "Prior
work we found" reports no search on this axis at all. Two directly relevant papers were
found by one query:

- Ghosh & Bengaly, arXiv:2408.04432, "Consistency tests between SDSS and DESI BAO
  measurements" (Dec 2024). Non-parametric (Gaussian-process) reconstruction of H(z),
  q(z) and O_m(z) from the D_H/r_d points of SDSS and DESI DR1. Conclusion (abstract):
  "the reconstructed H(z) and q(z) from SDSS are significantly inconsistent with those
  obtained from DESI". This is the opposite headline to the manuscript's N_sigma = 0.88
  (PTE 0.38). The two are not in contradiction, since one is model-independent on D_H
  only against DR1 and the other is a flat-LCDM parameter-difference test against DR2 on
  the full vector, but a paper whose title is the manuscript's derived quantity cannot go
  uncited, and the manuscript should say in one sentence why the statistics differ.
- Ferri, Ruchika & Melchiorri, arXiv:2607.07348 (July 2026) compare SDSS DR16 and DESI
  DR2 at parameter level (w_0, q_0, with Planck), quoting a ~1.1 sigma offset. Different
  plane and different data combination, but it is a published SDSS-vs-DESI-DR2
  parameter-level comparison and belongs in the positioning.

Also: 2404.03002 Sec. 3.3 (p.20) does make a parameter-level statement for DR1 vs SDSS,
"no significant difference in Omega_m and a shift of just ~1 sigma in r_d h". The
manuscript's referee-finding bullet ("DR1 does not apply its parameter-difference
statistic to SDSS") is correct, eq. (4.2) is applied only to CMB and SNe, but the text
should acknowledge that DR1 did compare the two surveys in the (Omega_m, r_d h) plane
qualitatively (Fig. 2 right panel), so that "not quoted" is not read as "not compared".

Required: cite both papers, narrow novelty item 2(b) to "the eq. (18) statistic applied to
BAO-only SDSS vs DESI DR2 in the (Omega_m, h r_d) plane", and reconcile with 2408.04432
in one sentence.

### F4 (minor) Derived quantity (c) is a restatement of Aubourg's published accuracy

The CAMB-minus-fitting-formula shift of -0.034 km/s/Mpc (DR2) is presented as a
"quantity not quoted". Aubourg et al. state 0.021% accuracy for eq. 16, and the
manuscript's own H0 literature review (Sec. 6.1) gives the propagation 0.1% in r_d ->
0.14 km/s/Mpc, i.e. 0.021% -> 0.03 km/s/Mpc. The measured shift is therefore exactly the
size Aubourg's quoted accuracy predicts. It is a useful confirmation, not a new number;
say "consistent with the 0.021% accuracy quoted by [aubourg2015]" and remove it from the
list of things that are new. (The DR1 value -0.0044 is also worth a remark: it is an
order of magnitude smaller, which the text does not comment on.)

### F5 (minor) cmbagent is characterised by its 2024 workshop version only

Sec. "Prior work we found" says the most direct precedent is cmbagent "with a human
approving each step". That is accurate for 2412.00431. But 2604.09621 p.4 describes the
current cmbagent "Planning & Control" mode (Xu et al. 2025, arXiv:2507.07257, cited
there) in which "there is no human-in-the-loop beyond the initial user request prompt,
resulting in a fully autonomous execution", and the Denario system (2510.26887, cited in
2604.09621 and 2510.24591) builds on it. The "human approving each step" framing should be
dated to the 2024 paper and the autonomous successor cited; otherwise the reader
underestimates the precedent.

### F6 (minor) Missing prior work on three of the seven "safeguards"

- Lean statements written by agents and their drift: FormalScience, Meadows, Zhang &
  Freitas arXiv:2604.23002 (Apr 2026) is an agentic Lean-4 autoformalisation pipeline for
  physics with a human-in-the-loop alignment check and a taxonomy of "semantic drift"
  (notational collapse, abstraction elevation, ...). The manuscript's own finding that a
  DR2 statement drifted from z > -1 to z >= 0, and its rule that "no person has checked
  that any Lean statement means what its gloss claims", are precisely the failure mode
  that paper names. Cite it in Sec. 3.4 and in the limitations.
- Re-running referee / provenance audit: Collider-Bench, Faroughy et al.
  arXiv:2605.13950 (May 2026) benchmarks agents reproducing published LHC analyses and
  uses "an LLM judge that inspects the agent's full workspace and verifies that the
  submitted values trace to an executed simulation, not to fabricated scaling factors or
  values copied from the literature" (p.2), with per-run FABRICATED flags (Table 3). That
  is the closest published analogue of the manuscript's "adversarial referee re-runs the
  analysis" plus content-addressed evidence. Also surfaced by the same search and not
  read beyond its abstract by this referee: Moreno et al. arXiv:2603.20179, "AI Agents
  Can Already Autonomously Perform Experimental High Energy Physics" (also cited as
  ref. [8] of DarkAgents and ref. [75] of 2607.10039).
- Model referee as a concept: the AI Scientist's automated reviewer (Lu et al.
  arXiv:2408.06292, cited in 2412.00431, 2510.24591, 2604.23002 and 2607.10039) predates
  this work; one citation suffices.

### F7 (minor) The search that supports "we did not find them combined" is thin and undocumented

Four alphaXiv queries are named by topic only. The six papers in F2, F3, F5, F6 were found
with two further queries. List the exact query strings and dates in an appendix or
footnote, add the two axes that were missing (SDSS-vs-DESI consistency; blinding /
preregistration in cosmology), and keep the hedge "within the limits of that search".

### F8 (minor) Ambiguous attribution of the ODE-solver defect

Abstract: "a Rust/CVODE port that reproduces the DR2 fit and exposed a defect in its ODE
solver". "Its" is read most naturally as "CVODE's". Sec. 3.7 makes clear the solver is
rusty-SUNDIALS's own reimplementation ("on that repository's own CVODE"). The abstract
should say "a Rust reimplementation of CVODE (rusty-SUNDIALS, not the LLNL library)", so
that no reader takes away that LLNL SUNDIALS CVODE has an Adams-order-1 bug.

### F9 (minor) Self-authored, unreviewed tool presented as a citation

`\cite{elenchus}` is the author's own unpublished GitHub repository. The bib entry makes
the authorship visible, but the pipeline description (Sec. 2 item 4) should say in text
that the ledger tool is the author's own and has no independent review, in the same
spirit as the paper's other disclosures.

### F10 (minor) Small wording and citation fixes

- Sec. "Prior work": "HepLean/PhysLib" -> "HepLean (now Physlib) [heplean,
  toobysmith2026]".
- ReplicationBench figure: "22% (Claude 4.5 Sonnet, average of 6; Table 3 of
  [replicationbench])"; the paper's own abstract says "under 20%".
- PRBench: add "best overall score 34% (Codex, GPT-5.3-Codex)".
- `eboss2021` and `dmdb2020` titles to the exact published titles.
- Borrett et al.: say it is a competition entry (FAIR Universe weak-lensing challenge),
  not a reproduction of a published result.

---

## 3. What survives

- Honesty that the cosmology values are reproductions: fully adequate (Sec. 1, abstract,
  Sec. "Not new").
- Novelty item 1 (the *combination* of safeguards): survives as hedged, once F2 and F6
  supply the missing baseline citations. I found no single paper that combines
  preregistration, hash-locked unread results, kernel-checked model identities with an
  axiom audit and a `sorry` control, a tier-capped evidence ledger, a re-running model
  referee and a second-language port, applied to an agent-executed cosmology reproduction.
- Novelty item 2(a), the DR1->DR2 shift in nested sigma: 2503.14738 Sec. III.C.1 gives
  distance-level consistency (KS p = 0.40) and Sec. VI only "perfectly consistent"; no
  parameter-level number was found in the fetched text. Survives, as a small
  complement, which is how the manuscript already frames it.
- Novelty item 2(b): survives only in the narrowed form of F3.
- Novelty item 2(c): does not survive as "new" (F4).
- Novelty item 3 (the process audit and its failures): survives; this is the paper's
  most defensible contribution and the section is candid.
- All eight prior-work citations resolve to the right papers and say what the manuscript
  says they say (Sec. 1 table).

## 4. Summary of required changes

1. Retitle / reword so that "machine-checked" modifies the model identities, not the
   reproduction (F1).
2. Add a blinding paragraph citing 2404.07282 and 2607.10039, and state that the DESI
   target analyses are blind analyses (F2).
3. Cite 2408.04432 and 2607.07348, reconcile with the former, and narrow novelty item
   2(b) (F3).
4. Reframe derived quantity (c) as a confirmation of Aubourg's stated accuracy (F4).
5. Cite the autonomous cmbagent successor (F5) and the three missing safeguards
   precedents (F6).
6. Document the search (F7); fix the CVODE attribution (F8); disclose Elenchus
   authorship in text (F9); apply F10.
