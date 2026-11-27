# Independent audit of `papers/p4_amplifier_census_n11` (C1b, Proposal 4)

Auditor: an AI agent (Claude), not the producer. It is not a human audit. Date 2026-10-28.
Scope: main.tex (253 lines), ledger/, data/, ERRATUM_C1.md, publication_meta.json, the producer's files in results/proposal4/2026-10-27/C1b/, and formal_cert/Programmes/AmplifierCensus/.
Write scope: this file only. All scratch work is in `/tmp/c1baudit/` (sources in `/tmp/c1baudit/src/`). Heavy work was pinned with `taskset -c 4,5`. Nothing was committed, pushed or published. No producer file was edited or regenerated, and the producer's `formal_cert/.olean_out` was not touched: Lean was rebuilt into `/tmp/c1baudit/olean`.

**Verdict: ACCEPT_WITH_CORRECTIONS.** Every number I re-derived matches. The census decision rule is sound: I re-derived it, tested it adversarially, and an independent implementation (different solver, different error bound) gives the same verdicts. The Lean theorems recompile, pass the axiom audit and pass the kernel replay. The corrections below are wording and sourcing. One of them is a factual slip about the preregistered priors (C2). None of them changes a count, a value or a tier.

---

## 1. Criterion and my own exact solver

**Source.** I read the formula from Allen et al., arXiv:1906.01036v1, through alphaXiv full text, not from the producer's code. The equations are:
- eq. (5): tau_ij = 1 + 1/2 sum_k (p_ik tau_jk + p_jk tau_ik) for i != j, with tau_ii = 0 and p_ij = w_ij/w_i;
- eq. (6): tau_i = 1 + sum_j p_ij tau_ij;
- eq. (7): sum_i pi_i^2 tau_i = 1;
- eq. (8): rho = 1/N + delta (N_eff - 2)/(2N) + O(delta^2);
- eq. (9): N_eff = sum_i pi_i tau_i, with pi_i = w_i / sum_j w_j.

The definition on p. 8 calls a graph an amplifier of weak selection iff N_eff > N.

Note on the citation. The brief said "Nature 2017", but the N_eff criterion comes from Allen et al. 2020 (PLoS Comput. Biol. 16(1):e1007529, arXiv:1906.01036). The paper cites that work correctly.

**Implementation.** `src/neffaudit.py::neff_exact` is a Fraction Gauss–Jordan on eq. (5), followed by eqs. (6) and (9) directly. It does not use the edge identity. It asserts eq. (7) exactly on every graph it solves.

| graph | edges | N_eff (mine, exact) | paper |
|---|---|---|---|
| A1 `J?`@`eoRAW?` | 16 | 328435957/29601736 = 11.095159 | equal |
| A2 `J?`CP_p[C[?` | 16 | 2890154941667179019/262436329991601232 = 11.012785 | equal |
| A3 `J?`@`eoRAW_` | 17 | 88175846355074579/8011935789939084 = 11.005561 | equal |
| R11 `JCQRRQodIU?` (and `J?ouPjI[@i?`) | 21 | 2668552698098/242579025123 = 11.000756 | equal |
| K11 | 55 | 11 | equal |
| C11 | 11 | 11 | equal |
| Richter's parent `J?ouPjI{@i?` (R11 plus the edge between its two non-adjacent degree-3 vertices) | 22 | 11 | equal |
| K11 minus an edge | 54 | 4514/411 | equal |
| stars S3, S5, S10 | | 3, 10/3, 40/11 | Allen's closed form 4n/(n+1) |
| the 5 nearest non-amplifiers of Table 2 | | all five fractions equal | |
| corrupted-pi control `I?`CP`ce_` | | 10.0193 corrupted, 9.6643 correct | equal |

**Regular graphs.** `nauty-geng -c -d k -D k 11` gives 1, 265, 266, 6 and 1 graphs for k = 2, 4, 6, 8, 10. Odd k is impossible because 11k must be even. The total is 539, which equals A005177(11) (read on oeis.org today). The `nauty-labelg` canonical set of my 539 regular graphs **equals** the canonical set of the 539 regular candidates in the producer's 256 part files. 48 sampled regular graphs (40 random, plus all k = 2, 8, 10) have exact N_eff = 11.

Other identities checked:
- A001349(9, 10, 11) = 261080, 11716571, 1006700565 (oeis.org).
- `nauty-labelg` gives JCQRRQodIU? and J?ouPjI[@i? the same canonical form, and networkx `is_isomorphic` agrees. The four amplifiers have four distinct canonical forms.
- A3 minus A1 is exactly one edge, (9,10), whose endpoints both have degree 4 in A3.

## 2. Census checks

(a) **Part sums.**
- The 256 `data/parts/*.json` files sum to 1,006,700,565 graphs, 1,006,700,022 excluded, 539 regular and 543 candidates. The non-regular candidates are exactly the four amplifiers.
- guard_fail = 0, chol_fail = 0, bad_lines = 0, and all 256 files have count_check_ok.
- max_eps = 7.4506e-8 and the minimum certified gap is 0.0020643, both as printed.
- Independently, the 256 `data/logs/parts/*.log` files each hold one `>Z k graphs generated` line equal to the `done N=11 graphs k` line, and each ends with `geng_rc 0 census_rc 0`. The `>Z` values sum to 1,006,700,565.

(b) **My own decision code on N = 11 slices.** `src/census.py` uses my own graph6 parser and my own unsymmetrised integer system. The decision uses a float64 LU solve (numpy) and a rigorous a-posteriori bound of my own, which differs from the producer's exact-integer residual:
- the float residual carries the Higham bound gamma_{n+2}(|b| + |A||x|);
- because (I−P)^{-1} ≥ 0 and (I−P)^{-1} 1 = tau, |e| ≤ ‖s‖ x_max/(1−‖s‖);
- the edge-identity sum has its own rounding term.

Graphs that are not excluded are solved exactly with Fractions.

| slice | graphs (= geng `>Z`) | result |
|---|---|---|
| `geng -c 11 10:13` (sparsest) | 44,725 | 0 amplifiers; 1 tie (C11) |
| `geng -c 11 44:55` (densest) | 15,969 | 0 amplifiers; 7 ties (six 8-regular, K11); min gap 0.010916 = 11 − 59396/5405 |
| `geng -c -d2 -D4 11 15:21` (positive control: contains all four by degrees and edges) | 351,703 | **exactly the 4 amplifiers, with the same exact values**; 0 ties; min gap 0.0020647 (the exact value for `J?`bJaWeJK?` is 0.0020647) |
| `geng -c 11 103/256` (random part) | 6,860,093 (producer: 6,860,093) | 6,860,089 excluded by my bound, 4 not excluded (all regular, exact 11); 0 amplifiers; min certified gap 0.0332950 (producer 0.0332948). Producer: 6,860,089 excluded, 4 regular candidates. Same verdicts |

Total N = 11 graphs decided by my own code: 7,272,490 (44,725 + 15,969 + 351,703 + 6,860,093).

(c) **Full independent re-census, N ≤ 10.**

| N | graphs | ties (all regular) | amplifiers |
|---|---|---|---|
| 3 | 2 | 1 | 0 |
| 4 | 6 | 2 | 0 |
| 5 | 21 | 2 | 0 |
| 6 | 112 | 5 | 0 |
| 7 | 853 | 4 | 0 |
| 8 | 11,117 | 17 | 0 |
| 9 | 261,080 | 22 | 0 |
| 10 | 11,716,571 | 167 | 0 (min certified gap 0.020734; C1 states at least 0.0207) |

All match C1 and A001349/A005177.

Extra check on C1's line 218. I applied every single-edge deletion to the 265 quartic graphs: 5,830 graphs, all connected. Exactly 4 labelled graphs are amplifiers, and they form one isomorphism class, R11 (canonical form `J@LCKMF]Bo?`). This is consistent with C1's "unique quartic graph … from which an edge removal works" when that phrase is read as a *single* removal. Richter 2022's 5 of 265 quartic inputs use multiple removals.

(d) **Producer's C port rerun.** I rebuilt `census_fast.c` in /tmp with gcc 11.4.0 and the recorded flags. The source sha256 is `bdfe481d…`. The binary sha256 is `6f658a7869b219c2…`, which equals the value in the paper and in data/result.json, so the build is reproducible. Two random parts were chosen with a secrets-seeded RNG: 158 and 207.
- **Part 158:** 9,101,908 graphs, equal to geng `>Z`. Every non-timing field of the output JSON is **identical** to `data/parts/part_0158of256.json`, including the candidate list, the near list, the top lists, max_eps and the minimum gap.
- **Part 207:** 3,159,768 graphs (= geng `>Z`), 3,159,765 excluded, 3 candidates; every non-timing field **identical** to `data/parts/part_0207of256.json`.

(e) **Soundness of the exclusion bound.**

*By hand.* The scaled matrix A_s = D(I−P), with D = diag(2k_ik_j) ≥ 2, so |D^{-1}r|/2^30 ≤ E/2^31 = eps. Since (I−P)^{-1} ≥ 0 and (I−P)^{-1}1 = tau, |tau − t/2^30| ≤ eps·tau_max ≤ eps·X/(2^30(1−eps)). N_eff = 1 + (1/m)·sum over edges of tau_e (derived: pi_i p_ij = 1/2m). This gives exactly the C inequality, (Den·2^30+W)(2^31−E) + Den·E·X < N·Den·2^30·(2^31−E), with Den = 2m and W = 2·sum t_e.

*Code review.*
- The guard E < 2^31 is enforced.
- The int128 ranges are safe: |t| < 2^50, entries ≤ 200 and at most 21 nonzeros per row (MAXNZ = 24).
- A_s is symmetric, and as a symmetric nonsingular M-matrix it is positive definite, so Cholesky is legitimate.
- Regular graphs are never excluded.
- The float proposal only enters through t, so a bad proposal can only fail to exclude.

*Adversarial test* (`src/adversarial.py`). I re-implemented the integer inequality from its written statement and ran it with a rational threshold T on A1, A2, A3, R11 and four nearest non-amplifiers. The inputs were the exactly rounded t, t with random noise of ±1 to ±10^8 units, scalings by 0.999999, 1.000001, 1/2 and 2, single zeroed entries, sign-flipped entries, and t with ten entries lowered (to push W down). The thresholds were T = 11, v, v ± 10^-9 and v + 10^-6.
- 11,800 tests gave **0 violations**: no t ever certified N_eff < T when exact v ≥ T.
- No amplifier was ever excluded at T = 11.
- The bound is also tight: for all 8 graphs the rounded t certifies N_eff < v + 10^-6.

## 3. Richter 2022, Fig. 1 (re-opened)

I read arXiv:2204.12861v1 through alphaXiv full text, and the J. Math. Biol. 87(1):3 (2023) version, doi:10.1007/s00285-023-01937-1, at PMC10247861.

**Caption of Fig. 1 (p. 8).** "4 non-isomorphic graphs on N = 11 vertices which are transient amplifiers of death-Birth updating and have maximum degree Δ(G) = 4. (a) N_eff = 11.0008, δ(G) = 3, k̄ = 3.8182, λ2 = 0.0567 (b) N_eff = 11.0128, δ(G) = 2, k̄ = 2.9091, λ2 = 0.0399 (c) N_eff = 11.0056, δ(G) = 2, k̄ = 3.0909, λ2 = 0.0451 (d) N_eff = 11.0952, δ(G) = 2, k̄ = 2.9091, λ2 = 0.0481. This graph can be obtained by removing the edge depicted in red of the graph in Fig. 1(c)."

The paper's transcription of N_eff and k̄ is correct.

**Identification is stronger than the paper says.** I computed the minimum degree δ(G) and the normalized-Laplacian λ2 (networkx) myself:

| graph | δ(G) | λ2 | Richter's panel |
|---|---|---|---|
| R11 | 3 | 0.0567 | (a) |
| A2 | 2 | 0.0399 | (b) |
| A3 | 2 | 0.0451 | (c) |
| A1 | 2 | 0.0481 | (d) |

All match the caption to every printed digit. The match therefore rests on N_eff, k̄, δ(G) and λ2 for each panel, plus the (c)→(d) one-edge relation. Drawings were still not compared.

**Inconsistencies.**
1. Δ(G) = 4 is stated in the caption **and** in the body text on p. 8 ("All 4 graphs have a maximum degree Δ(G) = 4"). A1, panel (d), has Δ = 3.
2. "the graph in Fig. 1(b) has the highest value N_eff = 11.0128" (p. 8). This is repeated on p. 10 ("only for the graph with highest N_eff = 11.0128, Fig. 1(b)") and in the caption of Fig. 2(b).
3. (Additional) p. 10 says that (b) and (d) "have the lowest mean degree k̄ = 2.0991". The caption has 2.9091, which equals 32/11.

The J. Math. Biol. version keeps all three wordings.

**What Richter claims about completeness.**
- His N = 11 results are outputs of Algorithm 1 ("approximative, greedy search", filter size 500, with cospectrality used as a proxy for isomorphism, p. 5). They start from all regular inputs with k = 4, 6, 8 (Table 1: 265/266/6 inputs, 4 non-isomorphic amplifiers overall).
- Only for the 265 quartic inputs is "a complete enumeration" of the edge-removal search reported (p. 9).
- He reports none found from regular inputs with N ≤ 10.
- He makes no claim about all connected graphs on 11 vertices.

**Prior art for an exhaustive N = 11 dB census.**
- alphaXiv `discover_papers` returned Allen 2019/2020, Richter 2020/2022, Tkadlec 2019, Hindersin–Traulsen 2015, Svoboda 2024, arXiv:2512.11164 and 2511.18252.
- Two web searches, standard and extended, found Richter's J. Math. Biol. papers, Allen 2020 and Svoboda 2024.
- **None reports an exhaustive enumeration of all connected 11-vertex graphs under dB.** This is a search result, not a proof of absence. The paper's "to our knowledge" wording is appropriate.

## 4. Lean

**Recompile.** Sources were copied to /tmp with sha256 identical to the paper's six hashes. I compiled them with the pinned toolchain (Lean 4.34.1, pinned Mathlib from `lean_pinned.py`'s PINNED path), with oleans written to /tmp/c1baudit/olean.

| module | rc | time |
|---|---|---|
| Core | 0 | 24.9 s (one `push_neg` deprecation warning) |
| DataA1 | 0 | 16.8 s |
| DataA2 | 0 | 22.6 s |
| DataA3 | 0 | 16.7 s |
| Amplifiers11 | 0 | 77.2 s |
| ControlsC1b | 0 | 23.3 s |

**Deviation, disclosed.** I used neither `scripts/certified_numerics/lean_pinned.py` itself nor `anse/formal/lean_runner.py`. CLAUDE.md makes the latter binding, but it does not use the pinned 4.34.1 stack these modules need. lean_pinned.py writes oleans into the shared `formal_cert/.olean_out`, which is outside my write scope and would have mixed my build with the producer's. Instead, `/tmp/c1baudit/src/lean_audit.py` is a clone of lean_pinned.py's compile path: the same toolchain binary, the same `lake env` LEAN_PATH from the same PINNED directory, and `-DautoImplicit=false`. Its only differences are `--root=/tmp/c1baudit/lean` and oleans written to `/tmp/c1baudit/olean`. The producer's `.olean_out` was never read or written; replay.py asserts that it is absent from LEAN_PATH.

**Axioms.** `#print axioms` on A1_amplifier, A2_amplifier and A3_amplifier gives exactly [propext, Classical.choice, Quot.sound].

**Controls.**
- ctlb_perturbed_vector_rejected, ctlb_wrong_graph_rejected and ctlb_wrong_value_rejected are proved negations (`¬ Eq5 …` and `≠`), each with the three allowed axioms.
- ctlb_sorry reports `sorryAx`, and ctlb_axiom reports `AmplifierCensusControlsC1b.ctlb_cheat`. Both planted controls are caught, as claimed.

**Escape grep.** I searched Core, DataA1–3 and Amplifiers11 for sorry, axiom, skipKernelTC, debug., addDecl, #exit, implemented_by, native_decide, set_option, extern, unsafe, opaque, macro, elab, run_cmd, attributes and instances. There were no hits other than the three `#print axioms` lines.

**leanchecker replay** of my own oleans, with LEAN_PATH set to the pinned Mathlib plus /tmp only:

| module | rc |
|---|---|
| Core | 0 |
| DataA1 | 0 |
| DataA2 | 0 |
| DataA3 | 0 |
| Amplifiers11 | 0 |
| ControlsC1b | 0 |

**What the theorems say.**
- `Eq5 A τ` is Allen eq. (5) verbatim: τ i i = 0, and for i ≠ j, τ i j = 1 + ½ Σ_k (p A i k τ j k + p A j k τ i k), with p A i k = [A i k]/deg A i.
- `neff` is eq. (9) with eq. (6) and π_i = deg i / Σ deg.
- `Ak_amplifier : ∀ τ, Eq5 GAk τ → neff GAk τ = q ∧ 11 < neff GAk τ`.

The statements are not vacuous. `tauAk_eq5 : Eq5 GAk tauAk` is a proved theorem, so a solution exists, and `eq5_unique` (maximum principle) makes it the only one.

**Link to the graph6 strings.** The `edgesAk` lists in DataA1–3 (and in DataR11) are labelled-equal to my own decode of the four graph6 strings, and re-encode to exactly those strings. Symmetry, looplessness and degrees are additionally kernel-checked (GAk_symm, GAk_loopless, GAk_deg).

**What Lean does not cover.** It does not certify the enumeration, the absence of other amplifiers, or eq. (8).

## 5. Ledger and erratum

**Elenchus gate.** I ran it read-only on the existing ledger.json and evidence/, with output in /tmp/c1baudit/gate_audit.txt. It exits **1** with exactly the four flags `LEDGER_UNAUDITED_TIER_A` (AMN-A-0001..0004), 0 blocking findings, identical to ledger/gate_output.txt.

**Tiers.**
- The tiers match the evidence: A = the Lean statements (verified above), L = Allen and Richter as stated, C = the census and the finite-r checks.
- AMN-L-0003's content is now confirmed against the PDF.
- AMN-C-0007 could cite δ(G) and λ2 as well (correction C3).

**ERRATUM_C1.md against `papers/p4_amplifier_census/main.tex` (393 lines).**
- Item 1. The old text is real, but it spans a line break: line 53 ends "Richter (2020)" and line 54 begins "exhibited an eleven-vertex example." It is not one string on one line. The cited lines 53–54 are correct.
- Item 2. The old string is on line 59 only, not 58–59.
- Item 3. Lines 93–96 are verified: the old text runs from the end of line 93 to "using his method." on line 96.
- Item 4. Line 218 is verified.
- Item 5. Line 343 is verified, and the old string is present verbatim.
- Item 6. Line 285 is verified.
- Item 7. C1's publication_meta.json description and notes contain no wording that presents R11 as the unique or only example. The description says "Richter's eleven-vertex graph", which stays correct. Item 7 is therefore an addition only.
- The C1 Zenodo DOI in zenodo_doi.txt is 10.5281/zenodo.23704563, as cited.
- The erratum's sourcing note ("did not re-open the PDF … should confirm the four printed values") is now discharged: confirmed here (§3).

## 6. Wording and build

**Wording.**
- There is no claim of new graphs. The abstract and §3 say explicitly that the four graphs are not new.
- There is no medical claim. The "What this is NOT" box and the Limitations section exclude it.
- No overreach found beyond C1–C7 below.

**Build.** I rebuilt in /tmp/c1baudit/build with pdflatex twice. Both runs returned rc 0, 8 pages, with **0 undefined references or citations** and one overfull hbox of 13.2 pt at lines 196–198 (the display listing q values).

---

## Corrections (old → new), main.tex unless stated

**C1 (lines 40–41, and Limitations line 215, and publication_meta description/notes "no independent audit").**
Old: `\textbf{This version is a producer's draft. No independent audit of any kind has been made}: the Lean modules have not been recompiled by a different agent, no statement lock exists, and no human has read the Lean statements or the hand argument of the decision rule. These three are owed`
New: `\textbf{This version was independently audited by a different AI agent (AUDIT.md, ACCEPT\_WITH\_CORRECTIONS), not by a human}: the auditor recompiled and replayed the Lean modules, re-derived the decision rule, re-censused $N\le10$ and parts of $N=11$ with its own code, and reran the C port on two parts. No statement lock exists and no human has read the Lean statements or the hand argument. These two are owed`
Line 215 needs the corresponding change: replace "No independent agent has recompiled … not been." with the audit facts above. Line 222 item (5) should become "no statement lock; the producer ≠ verifier recompile was done by the AI auditor". Line 210 should become "an AI audit exists (AUDIT.md); no `ai_audit` field was added to the ledger rows" (or add the field).

**C2 (line 73, factual slip about the priors).**
Old: `the first held, the other two did not (three further graphs were found).`
New: `the first two held (three graphs other than Richter's were found), the third did not.`
The preregistration (sha256 a5e5909d…) reads: "Prior that it finds a graph other than Richter's: 0.25. Prior that Richter's graph is the only amplifier at N = 11: 0.6". The event with prior 0.25 occurred. A grep over papers/p4_amplifier_census_n11/ (main.tex, ledger, data) and results/proposal4/2026-10-27/C1b/ finds "other two did not" only in main.tex l. 73. The run note RESULT.md (l. 244–247) has it right: "it found 3", "Richter unique … false".

**C3 (lines 50, 107/118, 158, 218; ledger AMN-C-0007 gloss). Stronger identification.**
Old (l. 50): `They are, by printed $\Neff$, edge count and degrees (we did not compare the drawings), the four $N=11$ graphs`
New: `They are, by printed $\Neff$, mean degree, minimum degree and normalized-Laplacian $\lambda_2$ (we did not compare the drawings), the four $N=11$ graphs`
In §3 (l. 118), after "the $\Neff$ values agree to every printed digit (table above)", add: `Their minimum degrees $3,2,2,2$ and normalized-Laplacian algebraic connectivities $\lambda_2=0.0567,0.0399,0.0451,0.0481$ for R11, A2, A3, A1 also equal Richter's printed $\delta(G)$ and $\lambda_2$ for (a)--(d) to every printed digit.` Change "the match is by $\Neff$, edge count and degrees" to "the match is by $\Neff$, edge count, minimum degree and $\lambda_2$". Make the same change at l. 158 and l. 218.

**C4 (lines 186–191, Richter observations).**
Old (item 1): `The caption states that all four graphs have maximum degree $\Delta(G)=4$.`
New: `The caption and the text of p.~8 (``All 4 graphs have a maximum degree $\Delta(G)=4$'') state that all four graphs have maximum degree $4$.`
Old (item 2): `The text says that (b), with $11.0128$, has the highest $\Neff$, whereas (d) has $11.0952$ in the same figure.`
New: `The text (p.~8, again p.~10 and in the caption of Fig.~2(b)) says that (b), with $11.0128$, has the highest $\Neff$, whereas (d) has $11.0952$ in Fig.~1.`
Optionally add item 3: `On p.~10 the mean degree of (b) and (d) is printed as $2.0991$; the caption of Fig.~1 has $2.9091=32/11$.`
Old line 186: `as transcribed in our run note` → New: `as read in arXiv:2204.12861v1 and in the J.\ Math.\ Biol.\ version (unchanged there)`.
Also change "Two inconsistencies" to "Three inconsistencies" if item 3 is added (line 186, and the description in publication_meta.json).

**C5 (line 210).**
Old: `\texttt{AMN-L-0003} (Richter's Fig.~1 values and caption) is transcribed from the run note of the C1b session and was not re-opened when this paper was written.`
New: `\texttt{AMN-L-0003} (Richter's Fig.~1 values and caption) was re-read in arXiv:2204.12861v1 and its journal version by the auditor and confirmed.`

**C6 (line 217, Richter's completeness claim — now answerable).**
Old: `We have not established what, if anything, Richter claims about completeness at $N=11$.`
New: `Richter's $N=11$ graphs are the output of his Algorithm~1 (an approximative greedy search with a filter, cospectrality used as a proxy for isomorphism) started from all regular graphs with $k=4,6,8$; only for the $265$ quartic inputs does he report a complete enumeration of the edge-removal search (pp.~5, 8--9). He makes no statement about all connected graphs on $11$ vertices. An additional literature search by the auditor (alphaXiv, web) found no exhaustive $N=11$ death-Birth enumeration.`

**C7 (line 247, bibliography).**
Old: `arXiv:2204.12861 (2022, v1 p.~8, Fig.~1); cited by Svoboda et al.\ as J.\ Math.\ Biol.\ 87(1):3 (2023).`
New: `arXiv:2204.12861 (2022, v1 p.~8, Fig.~1); J.\ Math.\ Biol.\ 87(1):3 (2023), doi:10.1007/s00285-023-01937-1 (Fig.~1 caption and text unchanged).`

**C8 (ERRATUM_C1.md).**
- Item 2: change "line 58-59" to "line 59".
- Item 1: note that the old text spans the line break between 53 and 54, "Richter (2020)⏎exhibited an eleven-vertex example."
- Sourcing note: replace "The agent that wrote this erratum did not re-open the PDF; whoever applies it should confirm the four printed values on p. 8 first." with "The four printed values, the caption and the text of p. 8 were confirmed by the independent auditor (papers/p4_amplifier_census_n11/AUDIT.md §3) in arXiv v1 and in the J. Math. Biol. version."
- Optional item 3: describe the N=11 figure as "(Fig. 1, same page) four non-isomorphic N = 11 transient amplifiers found by his greedy regular-input search".

- ERRATUM intro (l. 7). Old: `matching those four by N_eff, edge count and degrees (drawings not compared)`. New: `matching those four by N_eff, mean degree, minimum degree and normalized-Laplacian lambda_2 (drawings not compared)`.
- Optional, item 4: append "(by a single edge removal; Richter 2022 obtains amplifiers from 5 of the 265 quartic graphs by repeated removals)" after C1's "from which an amplifier constructor edge removal works". The auditor's single-deletion check (§2) supports the single-removal reading.

**C10 (C1b publication_meta.json, exact strings).**
- description. Old: `by printed N<sub>eff</sub>, edge count and degrees (drawings not compared)`. New: `by printed N<sub>eff</sub>, mean degree, minimum degree and normalized-Laplacian &lambda;<sub>2</sub> (drawings not compared)`.
- description, Limitations. Old: `the identification with Richter's Fig. 1 is by N<sub>eff</sub>, edges and degrees, not by drawings`. New: `the identification with Richter's Fig. 1 is by N<sub>eff</sub>, mean and minimum degree and &lambda;<sub>2</sub>, not by drawings`.
- description, Limitations. Old: `Producer's draft: no independent audit, no recompile of the Lean modules by a different agent, no human audit and no statement lock (all owed); the C implementation is validated against the Python code but not independently audited`. New: `Independently audited by a different AI agent (AUDIT.md, ACCEPT_WITH_CORRECTIONS): Lean recompiled and kernel-replayed, decision rule re-derived and tested adversarially, N &le; 10 and 7.27 million N = 11 graphs re-decided with independent code, C port rebuilt reproducibly and rerun on two parts with identical output; no human audit and no statement lock (owed); the C code was reviewed and rerun but not given a line-by-line independent audit`.
- description. If C4's third item is added, old: `<b>Two observations on Richter's Fig. 1</b>`; new: `<b>Three observations on Richter's Fig. 1</b>`, and add "; and p. 10 prints the mean degree of (b) and (d) as 2.0991, against 2.9091 in the caption".
- notes. Old: `Preprint v1 (2026-10-28), producer's draft, unaudited.` New: `Preprint v1 (2026-10-28), independently AI-audited (AUDIT.md), not human-audited.` Old: `Owed: erratum to the N <= 10 paper (ERRATUM_C1.md), independent recompile of the Lean modules, statement lock, audit of the C implementation.` New: `Owed: erratum to the N <= 10 paper (ERRATUM_C1.md), statement lock, human audit, a line-by-line audit of the C implementation (independent recompile and kernel replay of the Lean modules: done in AUDIT.md).`

**C11 (optional, arithmetic check done).** AMN-C-0008's first-order prediction for A1: 10^-4 × (328435957/29601736 − 11)/22 = 4.325×10^-7. This matches the printed 4.325×10^-7. No change.

**C9 (cosmetic).** Overfull hbox (13 pt) at main.tex lines 196–198: break the list of three q values onto separate lines.

None of C1–C11 changes a count, an exact value, a Lean statement or a tier.
