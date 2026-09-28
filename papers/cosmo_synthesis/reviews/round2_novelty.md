# Referee report, round 2 of 3: novelty, positioning and claims

Manuscript: `papers/cosmo_synthesis/cosmo_synthesis.tex` (draft of 2026-09-27, revised after
round 1). Rebuilt by this referee on 2026-09-27: `pdflatex -interaction=nonstopmode` twice,
rc 0 / rc 0, 21 pages, no undefined references or citations (20 LaTeX warnings, cosmetic).

Referee: a Claude model agent (Claude Code), NOT a person. Lens: novelty, positioning and
claims. Numerical correctness is out of scope for this lens; where I quote the manuscript's
numbers I quote them, I did not re-derive them.

Sources: every statement below about a cited or candidate paper comes from text returned by
the alphaXiv MCP tools (`discover_papers`, `answer_pdf_queries`) on 2026-09-27 in this session.
Four `discover_papers` sweeps were run (exact keyword lists in Sec. 5); 21 papers were read by
targeted PDF query. Nothing is from memory. Files under `results/cosmo_synthesis/` and
`docs/literature/` were read locally; nothing outside `papers/cosmo_synthesis/reviews/` was
written.

Recommendation: **minor revision**, with two issues rated major. No claim in the revised
manuscript is false or unsupported; the honesty about reproductions is complete. But the
literature that the "what is new" section is measured against still has two holes, one of
which (TOPO) is the published version of the exact safeguard the paper presents as its own
combination's most distinctive element, and the other of which (autonomous agentic analysis
with an unblinding gate and multi-agent review) is the closest architectural precedent to the
whole pipeline.

---

## 1. Were the round-1 novelty issues fixed?

Checked against the revised `.tex`, the response letter and the fetched sources.

| round-1 item | claimed status | verified? |
|---|---|---|
| N-M1 title overclaims "machine-checked" | FIXED | yes. New title puts "kernel-checked" on "model identities"; abstract adds "(the fits and numerics are not machine-checked)". |
| N-M2 blinding absent | FIXED | yes. New "Blind analysis" paragraph cites 2404.03002 Sec. 2.3.1, 2503.14738 Secs. II.A.1/IX, 2404.07282, 2607.10039. The Grosso et al. sentence is quoted verbatim (I re-fetched p. 11: "No analogous verification infrastructure exists for physics analyses, where correctness is probabilistic, domain-specific, and often only assessable in hindsight"). The paper states its setup is weaker than a blind analysis. |
| N-M3 SDSS-DESI claim unpositioned | FIXED | yes. 2408.04432 and 2607.07348 are cited and characterised correctly (see Sec. 2). Novelty item 2(b) is narrowed to BAO-only (Omega_m, h r_d) with eq. (18). The DR1 Sec. 3.3 sentence is quoted verbatim (re-fetched p. 21). |
| N-m1 derived quantity (c) not new | FIXED | yes. Sec. 4.5(c) calls it a confirmation of Aubourg's 0.021%; the "new" list has two items. |
| N-m2 cmbagent successors | FIXED | yes. 2507.07257 ("no human-in-the-loop at any point", verbatim in its abstract and Sec. 2.1) and Denario 2510.26887 (Cmbagent "as a deep-research backend", verbatim in its abstract) are cited. |
| N-m3 missing precedents | FIXED | yes for FormalScience, Collider-Bench, AI Scientist. 2603.20179 was not read and not cited; see F2 below, it now needs to be. |
| N-m4 search undocumented | PARTLY FIXED | as stated. `literature_search_log_round1.json` records two queries exactly; the original four are lost and the paper says so. See F5. |
| N-m5 Rust/CVODE attribution | FIXED | yes, abstract and Sec. 3.7. |
| N-m6 Elenchus authorship in text | FIXED | yes, Sec. 2 item 4 and bib entry. |
| N-m7 bibliography details | FIXED | yes. The response letter's correction of my round-1 note is right: in 2510.24591v2 the 0.22 figure is in Sec. 5.1 and the table captioned "Table 2" (the Sec. 5.1 text itself says "Table 3", but the table carrying 0.22 is Table 2; Table 3 is task completion). The abstract says "under 20%". The manuscript's wording is accurate. |

The three "referee statements did not match the sources" corrections in the response letter
that concern this lens (ReplicationBench table) are correct; I accept them.

## 2. Verification of citations added or changed in the revision

| bib key | arXiv | what the manuscript attributes | verdict from fetched text |
|---|---|---|---|
| xu2025pc | 2507.07257 | P&C mode "with no human-in-the-loop at any point" | holds, verbatim (abstract; Sec. 2.1). Also confirms the SN cosmology task was "successfully solved the first time it was run", i.e. a single-run demonstration, no repeat trials. |
| denario2025 | 2510.26887 | end-to-end research assistant with cmbagent backend | holds (abstract; Sec. 3.5 "relies exclusively on Cmbagent"). Note: Denario has its own **Review module** (Sec. 3.7) that produces `referee.md`; that is a nearer precedent for a model referee in cosmology than the AI Scientist, see F3. |
| aiscientist | 2408.06292 | automated model reviewer | not re-fetched this round; it is cited for this in 2604.23002, 2507.07257 and 2511.14631 (all fetched). Accepted. |
| colliderbench | 2605.13950 | agents reproduce LHC analyses; LLM provenance judge with FABRICATED flag | holds (Sec. 3.3 "Provenance Judge", flags PASSED/FAILED/FABRICATED; Sec. 4.5: 87/6/6% over 364 runs). The judge inspects traces and workspace, it does **not** re-run; the manuscript says "closest analogue", which is fair. |
| formalscience | 2604.23002 | agentic Lean-4 autoformalisation of physics; semantic-drift taxonomy incl. "abstraction elevation" | holds (Sec. 5: notational collapse, abstraction elevation, proof strategy substitution, implicit premise selection). It is human-in-the-loop, which the manuscript does not claim otherwise. |
| grosso2026 | 2607.10039 | blind-analysis-like separation for agents; "No analogous verification infrastructure" | holds, both verbatim (pp. 10-11). |
| andrade2024 | 2404.07282 | DESI DR1 catalog-level blinding validation | verified in round 1; not re-fetched. |
| ghosh2024 | 2408.04432 | GP reconstruction of H(z), q(z) from D_H/r_d only, DR1, Planck r_d, "significantly inconsistent" | holds (Sec. II.C: "we only adopt BAO measurements given in terms of the ratio (iii)", i.e. D_H/r_d; Table II is DR1; r_d = 147.05 +- 0.30 Planck; abstract quote verbatim). |
| ferri2026 | 2607.07348 | SDSS DR16 vs DESI DR2 with Planck in CPL, w0 and q0 offsets ~1.1 sigma | holds (Sec. 5.1: "approximately 1.1 sigma" for both). One nuance the manuscript may add: their SDSS chains include RSD and a different Planck likelihood version (their Sec. 4 caveat), so it is not a pure BAO-vs-BAO comparison. |
| prbench | 2603.27646 | best overall 34% (GPT-5.3-Codex), zero end-to-end callback, fabrication | holds (Table 2; Sec. 4.2; Sec. 5.2.1). |
| toobysmith2026 | 2603.08139 | Physlib renamed from PhysLean; error invalidating 2HDM Theorem 1; no extensive AI use | holds (p. 1; p. 2 "there was no extensive use of AI in the formalization"). |
| aubourg2015 | 1411.1074 | 0.021% accuracy for N_eff = 3.046, parameters within 3 sigma of Planck | holds (p. 5, eq. 16 and the sentence after it). |
| desi2025dr2 | 2503.14738 | footnote 12 C = sqrt(N_DR1/N_DR2); C ~ 0.57 for LRG2/eBOSS LRG; eq. (18); "perfectly consistent" with no number | all hold (pp. 15-16, 21). |
| desi2024vi | 2404.03002 | Sec. 3.3 quote; Fig. 1 best fit 0.294 / 1.0194e4; chi2 12.66 for 10 dof; eq. (4.2) applied to CMB | all hold (pp. 17, 20, 21, 23). |

Verdict on honesty about reproductions: unchanged from round 1, fully adequate (abstract,
Sec. 1, Sec. 5 "Not new").

## 3. Findings

### F1 (major) TOPO is the published form of the paper's hash-locking safeguard and is not cited

Casas & Fidler, "TOPO: Time-Ordered Provable Outputs", arXiv:2411.00072 (Open J. Astrophys.,
Nov 2024). From the fetched text: it "provid[es] a trustless alternative to data analysis
blinding" by (i) freezing an analysis before the run as a SHA256 "Analysis-Hash" of the git
commit hashes of the codes plus the hash of the input files, signed and published to a
timestamp server ("A possible solution ... is via platforms like the arXiv ... a more robust
solution is ... a public blockchain"); (ii) after the run, publishing a Merkle-tree proof over
the time-ordered MCMC chain so a verifier can re-run any prefix and check it; (iii) a
`topocobaya freeze / proof / verify` CLI. The worked example (Sec. 5.1) is a **BAO analysis on
SDSS DR16 likelihoods with CLASS and Cobaya**, i.e. the same instrument class as this paper.

Why this matters for the novelty claims:

- Novelty item 1 lists "preregistered targets and tolerances", "an amendment that hash-locks an
  unread earlier result", and "a tier-capped claim ledger with content-addressed evidence
  blobs" (Sec. 2 item 4; "each evidence blob is addressed by its sha256"). TOPO is the prior
  publication of pre-run hash commitment plus content-addressed, verifiable outputs in
  cosmology, with a public timestamp. The manuscript's own weakest link, disclosed three times
  ("none of the preregistration files was committed to git before its fit, so ... the file
  mtime is the only evidence of ordering"; "the eBOSS amendment field's timestamp is later than
  the file's mtime"), is precisely the gap TOPO's timestamped commitment closes.
- The new "Blind analysis" paragraph says the established safeguard is catalog-level blinding
  and that the paper's setup is weaker. It should also say that a hash-commitment alternative
  to blinding already exists in the field, that the paper's hash-lock is a one-file,
  post-hoc-timestamped instance of it, and that TOPO-style pre-registration of the
  Analysis-Hash on a timestamp server is what would have made the preregistration provenance
  claim checkable.

Required: cite 2411.00072 in Sec. 3.2 (protocol amendment), in the blinding paragraph and in
novelty item 1; reword the hash-lock bullet so that it does not read as the paper's own device;
add one sentence to Limitations ("Preregistration provenance") naming TOPO-style timestamped
commitment as the fix. No claim becomes false, but the "combination" claim is currently
measured against a baseline that omits the closest instance of its most distinctive member.

Also found by the same sweep and worth one clause in the blinding paragraph: Muir et al. (DES),
"Blinding multiprobe cosmological experiments", arXiv:1911.05929 (summary-statistic blinding,
the DES Y3 scheme; fetched, holds), and "Smokescreen" arXiv:2604.18111 (a data-vector blinding
package; abstract only, not read further). These are optional; TOPO is not.

### F2 (major) The agentic-cosmology prior work still omits the systems closest to this pipeline

The revised "Prior work we found" paragraph is anchored on the cmbagent lineage. One
`discover_papers` query on agentic cosmology returned, besides the papers already cited:

- **Moss, "The AI Cosmologist I: An Agentic System for Automated Data Analysis",
  arXiv:2504.03424** (Apr 2025). Fetched: fully autonomous planning/coding/execution/analysis/
  synthesis agents in cosmology, "without manual intervention", producing complete papers;
  demonstrated on Galaxy Zoo 2 and Quijote ML tasks, not on reproduction of a published
  constraint. It is cited by 2507.07257 itself (its ref. "Moss, 2025"). It is the
  highest-visibility standalone "agentic cosmology" system and must appear in a prior-work
  paragraph titled that way, with the one-clause distinction that it does ML tasks rather than
  reproductions.
- **Moreno et al., "AI Agents Can Already Autonomously Perform Experimental High Energy
  Physics", arXiv:2603.20179v3** (JFC framework). Round 1 flagged it; the response letter says
  it "was not read and is not cited". I read it. It is the closest architectural precedent to
  this paper's whole design and it is now also cited by Grosso et al. (their ref. [81]): a
  Claude Code orchestrator runs an analysis end to end; **"multi-agent review replaces the
  human feedback loop during analysis development, and human oversight is concentrated at a
  single formal unblinding gate"**; each phase "must produce a written artifact and pass an
  independent review before the next phase can begin"; an "append-only log" is kept for human
  verification; it **reproduces a published result** (CMS H->tau tau mu tau_h, "consistent with
  the published CMS ... measurement") and reports an indicative cross-model comparison
  (Fig. 5: three driving models, one of which returns a negative signal strength) "with no
  repeat trials". That last point is directly relevant to this manuscript's own disclosure
  that "the identity of the 'default model' is not recorded in any artifact".
- **Gandhi, Bolliet, Zubeldia, arXiv:2511.14631**: cmbagent extended with plots as "verifiable
  checkpoints" judged by a VLM against dynamically generated rubrics, "providing auditable
  reasoning traces". A verification-mechanism precedent for the "re-running adversarial
  referee" bullet.

Required: cite all three in Sec. 5; in the sentence "The most direct precedent is cmbagent",
add that JFC is the closest precedent for the *gate-plus-model-review* architecture and that,
unlike this paper, it keeps a human at the unblinding gate; state in one clause that neither
JFC nor cmbagent preregisters targets or hash-locks results, which is where this paper's
combination differs. (The claim "we did not find these items combined" survives after this;
the point is that the reader must be able to see what the nearest neighbours are.)

### F3 (minor) Model-referee precedent: Denario's review module is nearer than the AI Scientist

Sec. 5 says "The AI Scientist uses an automated model reviewer, a precedent for our model
referee." Denario (already cited) has a Review module (its Sec. 3.7) that renders the PDF to
images and produces `referee.md`, and 2511.14631 has a VLM judge; both are cosmology-native.
Add "and Denario's review module [denario2025]" to that sentence. One clause.

### F4 (minor) The SDSS-DESI DR2 tension number is presented without DESI's own bin-level figure

Sec. 4.5(b) says DR2 "gives no number for this pair of parameters" and mentions the bin-by-bin
alpha comparison. Both true. But DR2 Sec. III.C.2 (fetched, p. 16) also quantifies the single
worst bin: LRG2 vs eBOSS LRG "has reduced from 3 sigma to ~2.6 sigma" at C ~ 0.57, and "the
assumption of no correlation ... sets a lower limit of the discrepancy at the 1.9 sigma level".
The authors' own `docs/literature/EBOSS_VS_DESI_LITERATURE_REVIEW_2026.md` (line 66) records
exactly this, yet the synthesis paper omits it. Two consequences:

1. A reader of "N_sigma = 0.88 (PTE 0.38)" should be told in the same paragraph that DESI's own
   worst-bin distance-level discrepancy is 1.9-2.6 sigma and that the parameter-level statistic
   averages over it. Otherwise 0.88 sigma reads as "no tension anywhere".
2. The manuscript's "N_sigma is a lower bound if the cross-covariance is positive" argument is
   DESI's own framing ("no correlation ... sets a lower limit"); cite that sentence as the
   precedent for the bound rather than presenting the reasoning bare.

Required: one or two sentences in Sec. 4.5(b) with the 1.9 / 2.6 sigma figures and a citation
to Sec. III.C.2.

### F5 (minor) The documented search is still thin on the two axes that produced this round's finds

`literature_search_log_round1.json` records one query on SDSS-DESI consistency and one on
"blind analysis, preregistration, LLM agents, physics", whose only "relevant hit read" is
Collider-Bench. TOPO (F1) is squarely a blinding/preregistration paper in cosmology and sits
under keywords ["blind analysis", "preregistration", "cosmology"]; the AI Cosmologist (F2)
sits under ["LLM agents", "cosmology", "autonomous"]. Both came back on the first page of my
sweeps (Sec. 5). Add the two sweeps below (or equivalent) to the log with their hit lists, and
keep the hedge "within the limits of that search". The `other_hits_not_read` list already
contains 2603.20179; after F2 it moves to "read".

### F6 (minor) Formal side: the positioning could name the LLM-written-Lean precedents

The `discover_papers` sweep on Lean formalization of physics returned no formalization of FLRW
distances, BAO or cosmological background quantities (results: 2HDM stability 2603.08139, Wick's
theorem 2505.07939, AxQM 2609.05157, PhysProver 2601.15737, index notation 2411.07667,
dimensional analysis 2509.13142, Seiberg-Witten 2607.06379, constructive QFT 2603.15770). That
absence weakly supports the paper, which does not claim it; no change needed there. But
since the paper's Lean statements are model-written and model-audited, PhysProver
(automatic theorem proving for physics with LLMs) and AxQM (LLMs "formalizing autonomously"
in a QM library) are the natural precedents for that mode of production, next to FormalScience.
I read only their listing lines, not their PDFs, so I do not prescribe wording; if the authors
read them, one sentence in Sec. 3.4 suffices.

### F7 (minor) Small wording points

- Sec. 5, ReplicationBench: fine as is. Optionally note that its Sec. 5.3 found agents copy
  values from unmasked manuscripts ("certain agents score 15-20%+ higher ... by direct copying
  of values"), which is the failure mode this paper's "targets were visible to the agents"
  limitation is exposed to; it strengthens the "not a blind analysis" paragraph.
- Sec. 4.5(b), Ferri et al.: add "(their SDSS chains also include RSD and an older Planck
  likelihood, per their Sec. 4 caveat)" so the 1.1 sigma is not read as BAO-only.
- Sec. 5, cmbagent 2507.07257: the SN task "was successfully solved the first time it was run"
  is a single-run demonstration; if the manuscript wants to contrast its own controls and
  referee re-runs with that, the fetched sentence supports it.
- Abstract, "(i) DESI DR1 flat LCDM (not preregistered)": good. Title says "preregistered
  reproduction pipeline"; with the DR1 exception and the post-fit git commits disclosed in the
  abstract and Sec. 3.2 this is acceptable, but "four ... reproductions" in the subtitle
  includes the unpreregistered one, and a reader who stops at the title will not know. Consider
  "three preregistered and one earlier reproduction" in the subtitle. Cosmetic.

## 4. What survives

- Reproductions-not-measurements honesty: complete.
- Novelty item 1 (the combination): survives as hedged, and only after F1 and F2 supply TOPO
  and JFC as the nearest neighbours. Nothing I found combines preregistered tolerances, a
  timestamped-or-hash-locked unread result, kernel-checked model identities with an axiom
  audit, a tier-capped ledger, a re-running model referee and a second-language port on an
  agent-executed cosmology reproduction. But two of its seven members (hash-lock;
  model-review gate) now have close published instances that the text does not name.
- Novelty item 2(a), DR1->DR2 shift in nested sigma: survives. 2603.05472 (Ong, Yallup,
  Handley; fetched) "track[s] the DR1->DR2 evolution" of tensions with external datasets but
  gives no DR1-vs-DR2 parameter-level shift; 2604.06888 and 2602.18761 were listed but not read.
- Novelty item 2(b), narrowed: survives, subject to F4. Neither 2608.19432 nor 2608.04353 nor
  2604.11106 (all fetched, all in the authors' "not read" list) computes a parameter-level
  SDSS-vs-DESI-DR2 BAO-only statistic; 2604.11106 does compare SDSS and DESI D_M/r_d bin by
  bin (0.85 sigma at z=0.51, 0.95 sigma at z=2.33) as a side check.
- Novelty item 3 (process audit and failures): survives; still the paper's most defensible
  contribution.
- All fourteen citations checked in Sec. 2 resolve to the right papers and say what the
  manuscript says they say.

## 5. Search record for this round (exact inputs)

`discover_papers`, all on 2026-09-27:

1. keywords ["LLM agents","cosmology","reproduction","autonomous","BAO"], prioritize recency,
   difficulty 8. Hits: 2605.14791*, 2604.09621*, 2507.07257*, **2504.03424**, 2412.00431*,
   2601.14288, **2511.14631**, 2606.11157*, 2508.05728, 2605.22343. (* already cited)
2. keywords ["DESI DR2","SDSS","BAO","consistency","DR1","tension"], difficulty 8. Hits:
   2607.27411, 2602.18761, 2606.23936, 2607.19619, 2604.06888, **2603.05472**, 2510.16141,
   2510.04179, 2509.19899, 2503.14742.
3. keywords ["Lean 4","formalization","physics","general relativity","cosmology","PhysLean"],
   difficulty 7. Hits: 2603.08139*, 2505.07939, 2609.05157, 2601.15737, 2411.07667,
   2412.01349, 2509.13142, 2607.06379, 2603.15770.
4. keywords ["preregistration","blind analysis","registered report","astronomy","cosmology"],
   difficulty 7. Hits: 2604.18111, 2404.07282*, **2411.00072**, 1911.05929, 2205.11262,
   2608.06078.

Read by `answer_pdf_queries` (page text returned): 2510.24591, 2607.10039, 2503.14738,
2404.03002, 2604.23002, 2605.13950, 1411.1074, 2504.03424, 2603.05472, 2608.19432, 2608.04353,
2604.11106, 2408.04432, 2607.07348, 2507.07257, 2510.26887, 2603.27646, 2603.08139,
2411.00072, 2511.14631, 1911.05929, 2603.20179. Not read beyond the listing line: everything
else named above.

Rate-limit note: the first batch of alphaXiv calls failed with `mcp_upstream_auth_rate_limited`
and was retried successfully; no result in this report comes from a failed call.

## 6. Summary of required changes

1. Cite TOPO (2411.00072) in Sec. 3.2, the blinding paragraph and novelty item 1; reword the
   hash-lock bullet; name timestamped commitment as the fix in Limitations (F1).
2. Cite 2504.03424, 2603.20179 and 2511.14631 in Sec. 5 and state how JFC's unblinding gate plus
   multi-agent review relates to this pipeline (F2).
3. Add Denario's review module to the model-referee precedent sentence (F3).
4. Add DESI DR2's 1.9 / 2.6 sigma LRG2 figures and its "lower limit" framing to Sec. 4.5(b) (F4).
5. Log the two missing search axes and move 2603.20179 to "read" (F5).
6. Optional: F6, F7.
