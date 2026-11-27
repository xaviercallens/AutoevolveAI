# Proposal 5: new, true, checkable mathematics on one machine (2026-10-27)

**Author:** Xavier Callens (SocrateAI Lab). Drafted by an AI agent (Claude) as a scouting study. No person has reviewed it.
**Status:** proposal only. Nothing in it has been attempted, no code was written, nothing was committed. This is **not**
a preregistration: before any item starts it needs its own preregistration (statement, controls, kill criterion and
priors hashed before the first run), as in Proposal 4.
**User request (verbatim):** "continue finding more real mathematics breakthroughs".
**How we read it.** We never claim breakthroughs. The aim is **new, true, checkable** mathematical statements, found by
a disciplined, preregistered search with positive and negative controls, audited independently, with negative results
published. Every item below is small. Most of them close a finite case that someone else has explicitly left open.

Reading log, with one quoted sentence for each source opened: `docs/studies/MATH_SCOUT_2026-10-27.md`.

---

## 0. Rules this proposal keeps

- **Read vs not read.** A source is **read** only if it was opened in this session. Here that means the alphaXiv PDF
  page text, or a local file. A source seen only as a search snippet or as a reference inside another paper is marked
  **not read**, and nothing load-bearing rests on it.
- **Tiers (Elenchus, as in Proposal 4).**
  - A = kernel-checked Lean through `anse/formal/lean_runner.py`, with axioms limited to {propext, Classical.choice,
    Quot.sound}, no `sorry`, the statement locked, and a `leanchecker` replay.
  - L = literature, pinned to a page.
  - C = a human or AI argument, an exhaustive enumeration with a certified decision rule, or ball arithmetic not
    replayed in Lean.
  - X = floating point.
- **Toolchain (checked on this machine today, nothing installed).**
  - System `python3` has python-flint 0.9.0 (Arb), cypari2 2.1.2, mpmath 1.3.0 and networkx 3.4.2.
  - The venv has scipy 1.17.1 (LP and MILP through HiGHS), sympy 1.14.0 and z3-solver 5.1.0.
  - Also present: `gp`, Sage 9.5, GAP, and nauty (`nauty-geng`, `nauty-genbg`, `nauty-shortg`, `dreadnaut`).
  - **There is no SAT solver binary** (no cadical, kissat or minisat), **no SDP solver** (no cvxopt in Sage or
    Python), and no plantri.
  - Lean 4.34.1 is pinned, with a partial Mathlib. Never `import Mathlib` (LL §3).
- **Machine, as observed at 21:23 UTC.**
  - Load average is 13.2 on 8 cores, and every core is busy:
    - C1b census on core 2;
    - Lean or `leanchecker` jobs on cores 0, 1 and 4;
    - the Ollama prover on core 5;
    - Proposal 4 lanes on cores 3, 6 and 7.
  - Nothing below starts until Proposal 4 lanes release cores. Costs assume **1–2 cores per item**.
  - No item needs the GPU.
- **Scoring.**
  - Prior p = the probability that a **new** statement survives its gate within the time box. It ranges from 0.05 to
    0.4, and is deliberately sceptical.
  - Value v (1–5) = how much a correct result would matter to the people who posed the question.
  - Feasibility f (0–1) = the chance that we can run the method on this machine at the stated cost.
  - **Score = p × v × f.** All three numbers are our estimates, not measurements.

---

## 1. Ranked candidates

| Rank | Id | One-line statement | p | v | f | Score = p·v·f |
|---|---|---|---|---|---|---|
| 1 | **SLR-18** | The shifted lonely runner conjecture fails for every n with 18 ≤ n ≤ 94, so it fails for every n ≥ 5 | 0.35 | 4 | 0.9 | 0.35·4·0.9 = **1.26** |
| 2 | **LR-IND** | An independent reimplementation of the computer-assisted proof of the lonely runner conjecture for 11 runners (k = 10) | 0.35 | 2 | 0.7 | 0.35·2·0.7 = **0.49** |
| 3 | **EG-CB68** | Every cubic bipartite graph on ≤ 68 vertices has a cycle of length 4, 8 or 16 (Erdős–Gyárfás) | 0.3 | 2.5 | 0.6 | 0.3·2.5·0.6 = **0.45** |
| 4 | **DH-Ψ2** | Our own conjecture H + 3\|T\| ≤ 3∏‖F_v‖₃: exhaustive check over all sign inputs at resolution 2 | 0.4 | 1.2 | 0.9 | 0.4·1.2·0.9 = **0.43** |
| 5 | **LR-Q84** | Zhang's Question 8.4, LR([n−1]∖{r}) > 1/(n−1): an elementary argument found during scouting answers it, except for a finite check at n ≤ 21 (section 2.2). This is a remark to send the author, not a paper | 0.8 | 0.5 | 1.0 | 0.8·0.5·1.0 = **0.40** |
| 6 | **N1-ext** | A certified sign of the Gaussian zero-point curvature c(a) on [0.1, 0.425], including the third sign change near a ≈ 0.123 | 0.3 | 2 | 0.6 | 0.3·2·0.6 = **0.36** |
| 7 | **LR-SPEC** | A counterexample search for the amended Lonely Runner Spectrum conjecture (Fan–Sun, 1 ≤ k ≤ n) at 7 and 8 speeds, beyond Cordella's bounds | 0.1 | 3.5 | 0.9 | 0.1·3.5·0.9 = **0.32** |
| 8 | **LR-2E** | Extend Zhang's census of tight two-entry modifications (n ≤ 140, w ≤ 8n) to look for a tight set not produced by Goddyn–Wong (Question 8.3) | 0.08 | 3 | 0.8 | 0.08·3·0.8 = **0.19** |
| 9 | **GR-11** | An exhaustive n = 11 test of the open spectral Graffiti conjectures that need no NP-hard invariant | 0.08 | 2.5 | 0.7 | 0.08·2.5·0.7 = **0.14** |
| 10 | **S8-ALL** | A Lean replay of the computer-assisted "all s ≥ 0" part of the eight-point sphere theorem (Kryvonos–Liehr–Taylor) | 0.15 | 2 | 0.3 | 0.15·2·0.3 = **0.09** |

**Why the lonely runner family dominates.**
- It moved very fast in 2025–2026: LRC was proved up to 15 runners, the shifted version was disproved, and several
  papers from August to October 2026 state explicit, finite open questions.
- Its objects are rational. A witness or a covering is checkable in exact integer arithmetic, and often in Lean by
  `decide` on scaled integers.
- Items SLR-18, LR-Q84 and LR-SPEC share one exact kernel, ML(v) / γ(v; s), so they are cheap to run together. They
  are not independent bets: a bug in the kernel would hit all three. Their controls (section 2) are therefore
  separate, and each certificate is checked by a second implementation.

**Elementary-attack pass (done before ranking).**
- Several targets were posed in the last three months, in papers that used AI assistance. So before scoring, each
  "explicitly open" item got about 10–15 minutes of trying for an elementary resolution.
- **One fell: LR-Q84** (section 2.2). The witness t = 1/r settles every case with r > (n−1)/2, and only a finite
  check at n ≤ 21 remains. It was demoted from rank 2 to rank 5 and rescored as a remark.
- Nothing elementary was found for SLR-18, LR-SPEC, LR-2E, EG-CB68 or DH-Ψ2:
  - SLR-18: the "add a runner" lemma moves only one size at a time, and no closed-form family of shifts came to mind.
  - LR-SPEC, LR-2E: no structural argument found.
  - EG-CB68: the C6-forcing argument reduces it to a finite search but does not finish it.
  - DH-Ψ2: the resolution-1 proof does not tensorise, because of the even/odd coupling the paper describes.
- That pass is not a proof that no short argument exists. Each preregistration must repeat it.

---

## 2. The candidates in detail

### 2.1 SLR-18: the shifted lonely runner conjecture fails for every n in [18, 94]

- **Exact statement.**
  - For every n with 18 ≤ n ≤ 94 there are distinct positive integers v_1, …, v_n and shifts s ∈ (ℚ/ℤ)^n such that
    max_t min_i ‖s_i + v_i t‖ < 1/(n+1).
  - Equivalently, Γ(n) < 1/(n+1) in Zhang's notation.
- **Sources (read).**
  - Blanco, Criado, Santos, *Coloopless zonotopes and counterexamples to the Shifted Lonely Runner Conjecture*,
    arXiv 2603.24784, v4 of 2026-10-24.
    - γ_sh(1,…,5) = 15/94 < 1/6.
    - "the shifted LRC … is false for n ∈ {5, …, 17}".
    - Table 2 gives the exact γ_sh(1,…,n) for n ≤ 15, e.g. γ_sh(1,…,15) = 1/18.
    - "whenever a vector of size n exists with γ_sh(v) ≤ 1/(n+2), it produces infinitely many sLRC counterexamples for
      n + 1".
  - Poliakova, *More (shifted) runners, less loneliness*, arXiv 2609.23952, 2026-09-20.
    - E_n ≥ ⌊n/287⌋ and E_n ≥ 1 for n ≥ 95, through a "local uniform rule" with L = 192.
    - Proposition 4: a rule of gain g whose largest velocity is L gives E_n ≥ g for n ≥ L/2 − g.
    - "finding counterexamples for the remaining 18 ≤ n ≤ 94 would establish that SLR is false for all n ≥ 5".
  - Zhang, *Tight instances of the Lonely Runner Conjecture…*, arXiv 2608.13599, v3 of 2026-10-18: "Question 8.5 …
    is therefore open only for 18 ≤ n ≤ 94".
- **Why it is open, and why a new result is plausible.**
  - Blanco et al. stopped at n = 17 because they computed γ_sh *exactly*. An *upper* bound needs only one good shift
    vector s, and checking it is a one-dimensional covering problem with rational endpoints.
  - Their exact values show E_n ≈ 2 for [n] at n = 11…15, with γ_sh(1..15) = 1/18. So the vector [n] itself is very
    likely a counterexample for n ≥ 18 once a good s is found.
  - Three further routes are available:
    - chaining through the "add a runner" lemma;
    - a uniform rule with L ≤ 38;
    - Goddyn–Wong-style modifications.
  - No item needs a lower bound on γ_sh. That is the hard direction, and it is not attempted.
- **Verifiable core and tier.** For each n, a certificate (v, s, δ = 1/(n+1)).
  - Check: the open bad arcs {t : ‖s_i + v_i t‖ < δ} cover ℝ/ℤ, so the continuous min_i ‖·‖ is < δ everywhere and its
    maximum is < δ.
  - All endpoints are (k ± δ − s_i)/v_i, which are rational. Scale by a common denominator and check the covering
    with integers.
  - **Tier A** is feasible per n: Lean `decide` over at most Σ v_i ≈ n²/2 ≤ 4,500 integer intervals at n = 94, on the
    pinned stack. Two independent checkers are written: Python `fractions` and a C integer checker.
- **Method.**
  - (i) Port the exact γ(v; s) evaluator. Write our own; Criado's repository is public, and its
    `verify_solution.py` (not read) serves only as a cross-check.
  - (ii) For v = [n], search over s.
    - Seed it with structured s, e.g. periodic patterns extrapolated from the exact optima at n ≤ 15 (the s for
      n = 5 is printed in the paper).
    - Use local search or LP over fixed combinatorics: for a fixed assignment of runners to arcs, min δ is a linear
      program in (s, δ). scipy HiGHS solves it; the answer is rounded to rationals and re-checked exactly.
  - (iii) If [n] fails, search for a uniform rule in Poliakova's sense with L ≤ 38, or for modified velocity sets.
  - (iv) Chain: one vector with γ_sh ≤ 1/(m+1+k) covers sizes m+1, …, m+k after adding runners. The strictness at
    the last step is checked on the explicit vector, not assumed.
- **Positive controls.**
  - Reproduce γ(1..5; s) = 15/94 at s = (0,46,38,47,72)/94.
  - Reproduce γ_sh(2,3,4,5,6,8) ≤ 2/15 with s = (0,29,17,0,16,22)/30.
  - Certify < 1/(n+1) for [n], n = 5…17, using our own s (Blanco et al. report all of these as counterexamples).
- **Negative controls.**
  - s = 0 for [n] gives exactly 1/(n+1). It must **not** certify strict <, because the arcs are open and the
    tangencies matter.
  - Perturbing one shift by 1/(10·Σv) in a certified case must break the covering.
  - The unshifted LRC holds up to 14 speeds (Allikvere, arXiv 2609.02604, LRC(14), i.e. fifteen runners; literature,
    Tier L), so no s = 0 instance with ≤ 14 distinct speeds may ever certify.
- **Kill criterion.**
  - After 30 core-hours of search, stop and report the certified sub-range, e.g. "n ∈ [18, N] closed".
  - Any certificate that fails either independent checker kills that n until the bug is found.
- **Cost.** About 10–30 core-hours of search, under 1 core-hour of checking, and about 20–80 core-hours of Lean replay
  on the Lean lane, which is optional and done later.
- **Prior 0.35** for the full range. The prior is about 0.6 for a non-empty sub-range [18, N].
- **Novelty check.**
  - An alphaXiv sweep (recency) for "shifted lonely runner conjecture" returned nothing after 2609.23952 except
    Zhang v3. Zhang v3 (2026-10-18) calls the range open.
  - A WebSearch for the range returned only the same papers.
  - **Scoop risk is real.** The groups are active and Criado's code is public. Before publishing we must re-search
    arXiv the same day.
- **Over-claim risks.**
  - This finishes the disproof of a conjecture that is already disproved; it is not a breakthrough.
  - It says nothing about the unshifted LRC.
  - It gives no exact Γ(n), only upper bounds.
  - Velocities must be distinct positive integers. The trivial counterexample with repeated velocities must not be
    used.

### 2.2 LR-Q84: Zhang's Question 8.4, deletion values of [n−1]

- **Exact statement.** Is LR([n−1]∖{r}) > 1/(n−1) for all n ≥ 5 and all r ≤ n−2, where LR(V) = max_t min_{v∈V} ‖vt‖?
- **Source (read).** Zhang, arXiv 2608.13599 v3, Question 8.4.
  - "it can fail only for r > n − 2 − 2√n".
  - The question is settled when some D ∈ [n+r, 2n−3] is coprime to r: Theorem 2.9 gives a rational witness t = a/D.
- **What the scouting pass found.** This is an elementary argument, checked by hand once. It is Tier C until audited.
  - **Claim.** If (n−1)/2 < r ≤ n−2, then LR([n−1]∖{r}) ≥ 1/r ≥ 1/(n−2) > 1/(n−1).
  - **Proof.** Take t = 1/r.
    - For 1 ≤ v < r: ‖v/r‖ = min(v, r−v)/r ≥ 1/r.
    - For r < v ≤ n−1: since 2r ≥ n, we have 1 < v/r < 2. So ‖v/r‖ = min(v−r, 2r−v)/r ≥ 1/r, because v−r ≥ 1
      and 2r−v ≥ 2r−(n−1) ≥ 1.
    - This is the time used in Zhang's own Lemma 5.3.
  - **The remaining finite set.** Zhang's Corollary 2.10 already covers r ≤ n−2−2√n. The two ranges leave a gap only
    when n−2−2√n < (n−1)/2, i.e. n−3 < 4√n, i.e. **n ≤ 21** (at n = 21 only r = 10 is left; at n = 22, 19 > 4√22 ≈ 18.76).
  - In that gap r ≤ (n−1)/2, so Liu's exact formula LR = 2/D_r applies, with D_r the least integer ≥ n+r coprime to r
    (as quoted by Zhang). The question then reduces to D_r ≤ 2n−3 for finitely many (n, r).
  - That is a check of a few dozen pairs in exact arithmetic. It can be done by hand, or by a one-minute script plus an
    exact ML scan as a second, independent check.
  - **Caveat.** Liu's theorem (Taiwanese J. Math. 2008) is **not read**. The finite check must therefore also be done
    with a direct exact ML computation, not only through Liu's formula.
- **Why it is still listed.**
  - If the finite check passes, this answers a question posed eight days before this study.
  - It is a short remark to send to the author, not a result to publish on its own.
- **Verifiable core.**
  - The one-line witness argument, which is Lean-formalisable in a few lines (‖·‖ on rationals).
  - The finite table for n ≤ 21, Tier A by `decide`.
- **Controls.**
  - Positive: Liu's case LR([n−1]∖{2}) = 2/(2⌊n/2⌋+3) (Zhang, Theorem 2.11).
  - Negative: r = n−1, i.e. the set [n−2], must give exactly 1/(n−1) and must fail the strict test.
- **Kill criterion.** A single (n, r) with n ≤ 21 that fails the strict inequality. That would be a counterexample, and
  it would be reported, after a second check, as the real finding.
- **Cost.** Minutes.
- **Prior 0.8** that the question is answered "yes" in full.
- **Novelty check.**
  - The question appears in v3 of arXiv 2608.13599 (2026-10-18).
  - The alphaXiv lonely-runner sweep found no answer.
  - The author may simply have overlooked t = 1/r, or the question may intend something we misread. Ask before
    claiming.
- **Over-claim risks.**
  - Do not present it as a paper or a discovery.
  - Do not publish before the author has been contacted and the n ≤ 21 table is checked independently.

### 2.3 LR-IND: an independent check of LRC(10), i.e. eleven runners

- **Exact statement.** Re-derive, with independently written code, J(10, p) = ∅ for every prime p in
  Sungkawichai–Trakulthongchai's set P_10 (127 ≤ p ≤ 467, 61 primes, Σ ln p > 342 > ln B_10).
- **Sources (read).**
  - Sungkawichai, Trakulthongchai, *Eleven, twelve, and thirteen lonely runners*, arXiv 2604.23906 v2.
    - k = 10 "in 45 minutes on a 10-core Apple M4 processor"; k = 11 is about 40 hours.
    - Proposition 1.4 (polynomial method) handles (1, 2, …, k).
  - Allikvere, *Fourteen and fifteen lonely runners*, arXiv 2609.02604 v2: "The full computation has not been
    independently reimplemented or formally verified."
    - Their check of the LRC(12) input re-used the snapshot from [11], not new code.
- **Why it matters.**
  - This is a class (d) item: verification by computation of a recently claimed computer-checkable reduction.
  - It is **not a new statement**. Its value is an independent second implementation, the M3 pattern from
    Proposal 4.
  - LRC(10) is a link in the chain under LRC(11)…LRC(14). Only S–T and code derived from it have run it.
- **Verifiable core.**
  - Tier C: an exhaustive modular enumeration with exact integer witnesses.
  - Tier A for the scalar inputs: B_k, the log-prime sum, and the lemma bounds checked in Lean.
  - A formal replay of the enumeration is out of scope.
- **Method.**
  - Our own C implementation of I(k, p, 1), binary lifting and backward projection, written from the paper's
    definitions only.
  - A separate agent writes it **without reading their repository**. The repository is used afterwards for
    count-level comparison only.
  - Proposition 1.4 is re-proved, or audited as Tier C.
- **Controls.**
  - Positive: reproduce LRC(7) and LRC(8) (seconds) and their per-prime retained-tuple counts where printed.
  - Negative:
    - planting a deliberately wrong witness rule (strict < replaced by ≤) must change the counts;
    - k = 10 at a prime where (1, …, 10) is known to survive without the Proposition 1.4 step must report a survivor.
- **Kill criterion.**
  - Throughput is measured at p = 127 first. If the projected total exceeds 40 core-hours, stop and report the
    verified primes.
  - **A disagreement on any prime is reported to the authors before anything else**, after a second check.
- **Cost.** About 8–40 core-hours for k = 10. k = 11 (about 400 core-hours) is declined for now.
- **Prior 0.35** that the independent run completes. A discrepancy is very unlikely (< 0.05) and is not a goal.
- **Novelty check.**
  - The S–T paper says they tested against [16] on smaller cases only.
  - Allikvere confirms orbit counts at three primes for k = 13 only, and says the full computation was not
    independently reimplemented.
- **Over-claim risks.**
  - Do not call it "a new proof", and do not claim novelty for LRC(10).
  - Say exactly which primes and which lemmas were re-checked.

### 2.4 EG-CB68: Erdős–Gyárfás for cubic bipartite graphs up to 68 vertices

- **Exact statement.** Every simple cubic bipartite graph on at most 68 vertices contains a cycle of length 4, 8 or 16.
  Hence a cubic bipartite counterexample to the Erdős–Gyárfás conjecture has at least 70 vertices.
- **Sources (read).**
  - Tranquilli, arXiv 2608.02675 (≤ 58).
    - The method: a Moore-bound reduction forces a C6 below 62 vertices; then a triangle-rooted restricted-growth
      search over linear v₃-configurations with C8/C16 pruning.
    - The full cap-29 tree has 21,493 states and 1,762,368 attempted proposals, which is tiny.
    - "The computation does not examine side size 30".
  - Ducoffe, Dumitru, arXiv 2609.28594 (2026-09-23): "every bipartite graph of order at most 66" by SAT modulo
    symmetries, about 30 core-days in total, and "The solver was not asked to produce a resolution proof."
- **Why open, and why plausible.**
  - Order 68 is the first cubic-bipartite order covered by neither paper.
  - The C6-forcing step extends beyond Tranquilli's Moore bound. A C4- and C8-free bipartite cubic graph has girth 6 or
    at least 10, and a cubic graph of girth ≥ 10 has at least 70 vertices.
    - That last fact is the (3,10)-cage order, O'Keefe–Wong 1980, **not read**, to be pinned before the item starts.
  - So for side size v ≤ 34 the triangle-rooted search is still complete.
  - At 70 vertices, the girth-10 graphs are exactly the (3,10)-cages. Checking them for C16 is a stretch goal.
  - The search tree at cap 29 is tiny. Growth per cap step is unknown: this is the main risk.
- **Verifiable core.**
  - Tier C: exhaustive search with a witness-stream certificate checked by a separate streaming checker, as in
    Tranquilli.
  - The reduction lemma (Moore or cage bound, incidence translation) is Tier C, with a Lean formalisation optional.
- **Method.**
  - Reimplement the restricted-growth search from the paper, with two different C16 oracles (DFS paths, and
    half-path joins).
  - Run caps 29 (control), 30, 31, …, 34.
- **Controls.**
  - Positive:
    - reproduce Tranquilli's cap-29 counters (21,493 states; 0 completions) and their v ≤ 13 configuration counts
      (1, 1, 3, 10, 31, 229, 2,036), which agree with genbg and Betten–Brinkmann–Pisanski;
    - with the C16 filter switched off, the search must find completions (e.g. the 19₃ configurations).
  - Negative: switching off the C8 filter must produce completions. The Heawood graph has C8, so it must be rejected
    by the C8 test.
- **Kill criterion.**
  - Measure the cap-30 and cap-31 growth factors. If the cap-34 projection exceeds 48 core-hours on 2 cores, report
    the largest completed cap as a partial result: "≥ 62", "≥ 64" and so on, where new.
  - Orders up to 66 are not new as bounds (Ducoffe–Dumitru), but they are an independent, certificate-producing
    re-check of an uncertified SAT run.
- **Cost.** Time-boxed at 48 core-hours.
- **Prior 0.3** that order 68 is closed.
- **Novelty check.**
  - A WebSearch for "Erdős–Gyárfás cubic bipartite … 62 vertices" finds only these two papers and Wikipedia's 60.
  - The alphaXiv graph-enumeration sweep found nothing newer.
- **Over-claim risks.**
  - This is a finite bound, not progress on the conjecture.
  - Say "cubic bipartite" every time.

### 2.5 DH-Ψ2: our own C* = 3 conjecture, all sign inputs at resolution 2

- **Exact statement.** For all sign inputs F ∈ {±1}^48 at resolution 2, Ψ(F) = H(F) + 3|T(F)| ≤ 3, where
  Ψ ≤ 3 ⇔ Φ ≤ 3 for sign inputs.
- **Source (read, local).** `papers/dyadic_triangular_hilbert/dyadic_triangular_hilbert.tex`, the Conjecture in
  section "A sharp conjecture" (Zenodo 10.5281/zenodo.23232389).
  - Resolution 1 is a theorem.
  - At resolution 2 only max R = 2 was computed exhaustively; Ψ was only hill-climbed.
  - TODO 31 in `docs/OPENAI_MATH_HYPOTHESES.md`.
- **Why.**
  - It is cheap, and it cannot be scooped because the conjecture is ours.
  - Either outcome is a result: a violation refutes our published conjecture and must be reported as an erratum.
- **Verifiable core.**
  - Tier C: exhaustive enumeration with the same F₂ reduction as the R run. For fixed coefficient vectors c_t and d,
    max over F₂ of Σ_t |⟨c_t, F₂⟩| + 3|⟨d, F₂⟩| = max over signs of an ℓ₁ norm.
  - A violation is a single exact input, Tier A by `decide`.
- **Controls.**
  - Positive: reproduce max R = 2, and Ψ = 3 at the seed g (H = 3/2, T = 1/2) and at the constant input.
  - Negative: the Haar-free form must give N + 1 = 3 for R and must exceed 3 for Ψ where expected. A planted factor 4
    in place of 3 must find violations.
- **Kill criterion.** More than 60 core-hours projected after a 1% sample.
- **Cost.** About 20–60 core-hours.
- **Prior 0.4.** Value is low: sign inputs only, real inputs untouched.
- **Over-claim risks.** Say "sign inputs, resolution 2". It says nothing about C* for real inputs.

### 2.6 N1-ext: completing the Gaussian zero-point sign classification below a = 0.425

- **Exact statement.**
  - Certify the sign of c(a) = F(a, 0)/8, the exact second variation of the harmonic zero-point energy at the
    triangular lattice for the Gaussian e^{−πa r²}, on [0.1, 0.425].
  - Enclose the sign change near 0.123 reported by P2.
  - Together with N1 this would give the sign on [0.1, 4] with three enclosed roots.
- **Source (read, local).** `results/proposal3/2026-10-26/N1/CLASSIFICATION.md`.
  - "The unrestricted iff for all a > 0 is false: P2 finds another sign change near a ~ 0.123".
  - Cost driver: "small a needs many lattice terms … and a nearly singular B near Gamma".
  - Published as doi:10.5281/zenodo.23667863 with the range [0.425, 4] only.
- **Verifiable core.** The same as N1: Tier A for the logic and the rationals; Tier C-ball for the integrals (the
  N1/N2 precedent). Per-point certificates are used at thin points where intervals fail.
- **Controls.**
  - Positive: reproduce N1's certified points at a = 0.425 and 0.45 with the extended engine.
  - Negative: a tampered tail bound must be rejected by the kernel, as `lean_reject_tampered.json` was.
- **Kill criterion.**
  - det B > 0 cannot be certified on cells at a ≤ 0.15 after two budgets. Report the certified part.
  - The third root may then remain Tier X.
- **Cost.** About 50–150 core-hours. QMAX grows like 20/a, so this is the slowest item.
- **Prior 0.3.**
- **Novelty check.** This is an internal open item. P2 is our own number, and the Gaussian zero-point problem has no
  external literature that we know of. N3's `LITERATURE.md` holds the literature scan; it was not re-read today.
- **Over-claim risks.** Harmonic, Bravais, 2D, local only, exactly as N1.

### 2.7 LR-SPEC: a counterexample search for the amended Lonely Runner Spectrum conjecture

- **Exact statement.**
  - Find a near-tight tuple of 7 or 8 distinct speeds whose loneliness ML = p/q (in lowest terms, below 1/n) has
    k = q − np > n, which would refute Fan–Sun.
  - Or show that there is none in an extended box.
  - Secondary targets:
    - Cordella's Conjecture 6.2 (odd denominator for six speeds) beyond speed 110;
    - Question 6.6 (max v_i < 3q for near-tight sextuples).
- **Source (read).** Cordella, arXiv 2609.03444 v2.
  - The searches covered 4 speeds ≤ 200, 5 ≤ 130, 6 ≤ 110, 7 ≤ 50 (three tuples with k = 2) and 8 ≤ 40.
  - "For seven speeds the method is blocked by the missing classification of the tight sextuples".
  - The Fan–Sun paper itself (Electron. J. Combin. 2026) is **not read**.
  - The statement "1 ≤ k ≤ n" and the convention for k (k = q − np, with p/q in lowest terms and n the number of
    speeds) are Cordella's paraphrase. **Fan–Sun must be obtained and the exact statement pinned before the item
    starts**, or the item is killed.
- **Why plausible.** Even values of k already occur for 4 and 7 speeds (Cordella, section 6.3). At 7 and 8 speeds only
  boxes up to 50 and 40 have been searched, and the structure is not classified ("blocked by the missing
  classification of the tight sextuples").
- **Novelty check.**
  - Cordella's v2 (2026-09-08) is the latest search found in the alphaXiv lonely-runner sweeps.
  - No later search at 7 or 8 speeds was found.
- **Verifiable core.** The exact ML of one tuple by a finite breakpoint scan. A counterexample is Tier A
  (`decide`). A null box is Tier C.
- **Method.**
  - A fast exact kernel in C, cross-checked against Cordella's MIT code on random tuples (their kernel agreed with a
    Python version on hundreds of tuples).
  - Fast rejection with small-denominator witness times.
- **Controls.**
  - Positive: reproduce Cordella's counts (348 near-tight primitive sextuples ≤ 110; the 3 septuples with k = 2 ≤ 50;
    the 29 octuples ≤ 40, all with k = 1).
  - Negative: corrupting the strictness of the band test must change the counts.
- **Kill criterion.** Box 7 speeds ≤ 80 and 8 ≤ 60, or 60 core-hours, whichever comes first.
- **Cost.** 30–60 core-hours.
- **Prior 0.1.** If found, the result is of real interest to people working on the spectrum.
- **Over-claim risks.** A null box is not a proof of anything.

### 2.8 LR-2E: tight multi-entry modifications beyond Goddyn–Wong

- **Exact statement.**
  - Find a tight set ([n−1]∖R) ∪ W, with |R| = |W| = 2 or 3, that does not arise from Goddyn–Wong's Theorem 5.1
    (Zhang Question 8.3).
  - Or extend the exact census (n ≤ 140, w ≤ 8n, Theorem 6.10) to n ≤ 300 or w ≤ 16n.
- **Source (read).** Zhang, arXiv 2608.13599 v3, sections 6–8 and Table 1: 821,305 cases, "0 unexpected tight sets".
- **Why plausible (weakly).**
  - Zhang states that the converse of Theorem 5.1 "already fails in general", and that no general bound on the
    inserted speeds is known (Question 8.2).
  - The census window w ≤ 8n is "a pragmatic window".
  - So tight sets with larger inserted speeds have not been searched.
- **Core.** Tightness is an exact finite test: a covering condition plus one witness. A new tight set is Tier A by
  `decide`.
- **Method.**
  - Reimplement the "remaining-region" test, the third of Zhang's three methods, which does not use the component
    structure.
  - Extend to n ≤ 300 with w ≤ 8n, and to n ≤ 140 with w ≤ 16n, using his edge-reach masks to prune.
  - Re-check every survivor exactly.
- **Controls.**
  - Positive: recover {1,4,5,6,7,11,13} (n = 8) and the n = 74 Goddyn–Wong set.
  - Negative: a perturbed inserted speed must fail.
- **Kill criterion.** 20 core-hours.
- **Cost.** At most 20 core-hours. It shares the exact-ML kernel with SLR-18 and LR-SPEC.
- **Prior 0.08.** A null extension has little value. Only a new set counts as a result.
- **Novelty check.** Zhang v3 (2026-10-18) is the latest census found. No other two-entry census appeared in the
  sweeps.
- **Over-claim risks.**
  - A null box does not answer Question 8.1, 8.2 or 8.3.
  - A new tight set must be checked against Theorem 5.1's criterion before calling it "not of Goddyn–Wong type".

### 2.9 GR-11: open spectral Graffiti conjectures on all 11-vertex graphs

- **Exact statement.**
  - For each open, NP-hard-free spectral Graffiti conjecture in Roucairol–Cazenave's Table 1 (e.g. 20, 21, 39, 40,
    129, 143, 154, 195, 198, 252, 254, 262, 698, 712, 714, and the class-restricted 219, 284, 290, 292, 295, 322),
    decide whether a connected graph on ≤ 11 vertices refutes it.
  - The graph class must be respected.
- **Source (read).** Roucairol, Cazenave, arXiv 2409.18626: "we were unable to refute conjectures that were open
  except one".
  - They also warn about erroneous definitions ("range", "harmonic", "gravity") in the Aouchiche–Hansen survey.
- **Not read.** *Written on the Wall* (the primary statement source), and the Aouchiche–Hansen 2010 survey. **Both
  must be obtained and pinned before the item starts**, or the item is killed. Definition errors are the dominant risk.
- **Core.**
  - Tier X screening with float eigenvalues, then exact re-check of any near-tie or violation (characteristic
    polynomial via flint, with Sturm sequences).
  - A refuting graph is Tier A-checkable for algebraic invariants. It is Tier C if the invariant needs a numeric
    eigenvalue bound.
- **Resources.**
  - Its own `nauty-geng -c 11` stream, 1,006,700,565 graphs, as in C1b. C1b's code is not modified, because C1b is
    preregistered.
  - geng alone takes core-hours, plus the eigenvalue cost.
- **Controls.**
  - Positive: re-refute already-refuted Graffiti 29 (7 vertices), 166 and 711 (5 vertices).
  - Negative: a known theorem, e.g. λ₁ ≥ average degree, must never fire.
- **Why plausible (weakly).**
  - Roucairol–Cazenave's searches build graphs edge by edge up to 50 or 100 vertices. They are heuristic and do not
    cover all small graphs.
  - An exhaustive n = 11 pass is complementary: it is the regime where heuristic searches have no guarantee.
  - Most Graffiti conjectures were checked by the authors on databases of small graphs, though, so the prior is low.
- **Method.**
  - Run `geng -c 11` in res/mod parts.
  - Compute numpy eigenvalues of A, L, Q and D, plus the needed invariants (harmonic, temperatures, gravity per the
    pinned definitions).
  - Flag anything within 10⁻⁶ of violating, and re-check it exactly.
- **Cost.** About 10–20 core-hours.
- **Kill criterion.** The definitions cannot be pinned from a primary source, or the run exceeds 20 core-hours.
- **Prior 0.08.**
- **Novelty check.**
  - Roucairol–Cazenave 2024 is the latest systematic attempt found. AutoGraphForge (arXiv 2609.03478) was seen only as
    a title, **not read**.
  - It must be read before starting, in case it already ran exhaustive small-n checks.
- **Over-claim risks.**
  - A refutation under a misread definition is worthless. Report the definition source next to every result.
  - "No counterexample on ≤ 11 vertices" is weak evidence and must be worded that way.

### 2.10 S8-ALL: Lean replay of the eight-point "all s ≥ 0" certificate

- **Statement.** The square antiprism X(a_s) uniquely minimises the Riesz s-energy of 8 points on S² for all s ≥ 0.
- **Source (read).** Kryvonos, Liehr, Taylor, arXiv 2609.22077.
  - s ∈ {0, 1} and large s are Lean-verified.
  - The all-s computer-assisted proof is in the repository but "not included in the main article, as Lean
    verification is one of our standards"; they "expect that it will now be entirely possible … to complete the Lean
    verification".
- **Why low.**
  - The authors plan to do it themselves, so scoop risk is high.
  - The certificate size is not stated.
  - We hold no SDP machinery to regenerate certificates, only to replay them.
  - It is an independent check, not a new statement.
- **Verifiable core and tier.**
  - A kernel replay (Tier A) of the published certificates, on our pinned Lean 4.34.1 stack, after porting their Lean
    development.
  - They used Lean 4 with Mathlib. The version was not checked; a version mismatch is likely, which is the LT_CMP
    lesson.
- **Method.**
  - Read their repository (`github.com/lukasliehr/Energy-Minimization-8-Points`, **not read**).
  - Run their Python checkers.
  - Port the s ∈ {0, 1} Lean development first, as a control, then attempt the all-s certificates.
- **Controls.**
  - Positive: their s = 0 and s = 1 theorems replay under our pin with axioms in the whitelist.
  - Negative: a tampered certificate entry must be rejected.
- **Kill criterion.** The s ∈ {0, 1} port is not achieved within 40 core-hours, or the all-s certificate size makes
  the replay exceed 200 core-hours.
- **Cost.** 40–200+ core-hours, unknown until the repository is read.
- **Prior 0.15.**
- **Novelty check.**
  - The paper (2026-09-18) states the authors' own plan to do this.
  - Before starting, check their repository for a newer Lean release.
- **Over-claim risks.** This is a replay of someone else's proof. Never call it ours, and never call it new.

---

## 3. First wave: four items with disjoint resources

Every first-wave lane is CPU-only and needs neither the GPU nor the A1 Lean scheduler. Lean is used only at the end,
for small `decide` certificates, on the Lean lane. Cores are assigned when Proposal 4 releases them; the numbers below
are placeholders to fix in the preregistration.

| Lane | Item | Cores | Budget | Code base | Independent checker |
|---|---|---|---|---|---|
| W1-a | SLR-18 | 1 | 30 core-h search + optional Lean | exact γ(v;s) kernel (Python + C) | second integer checker; Lean `decide` per n |
| W1-b | LR-IND (k = 10) | 1 | 40 core-h | new C modular sieve, written blind to S–T code | count comparison with S–T logs afterwards |
| W1-c | EG-CB68 | 2 | 48 core-h, time-boxed | new C restricted-growth search | streaming certificate checker (separate program) |
| W1-d | DH-Ψ2 | 1 | 60 core-h, gated on a 1% sample | the existing `scripts/openai_math/hypotheses/tensor/` evaluator, extended to Ψ | the second evaluator `h5_exact.py`, run on every argmax |

**Why these four.**
- They are the four highest scores.
- They use **four different code bases**, with no shared kernel:
  - W1-a: exact rational covering.
  - W1-b: modular sieve.
  - W1-c: configuration search.
  - W1-d: tensor sign enumeration.
  - So a common-mode bug cannot hit two lanes. DH-Ψ2 is also impossible to scoop.
- Each has a kill criterion that is measured early: search hours (a), p = 127 throughput (b), cap-30/31 growth (c),
  and the 1% sample (d).
- Together they need 5 cores in the worst case, so they can run alongside C1b (core 2) once Proposal 4 lanes finish.

**LR-Q84 needs no lane.** Do the n ≤ 21 table, then a second check with an exact ML scan, then the Lean witness lemma.
That takes minutes, in the preregistration session. If it passes, write to the author. Do not publish it.

Second wave: N1-ext and LR-SPEC. Third: LR-2E, GR-11 and S8-ALL, only if a first-wave item leaves a reason to continue.

**Model tiers, as in Proposal 4.**
- Sonnet for search code and drivers.
- Opus for proofs (the LR-Q84 witness lemma, EG reduction lemmas), Lean certificate assembly and the independent audit.
- The producer is never the verifier. LR-IND's implementer must not read the S–T repository.
- No simulated agents. A stage that cannot run reports BLOCKED.

---

## 4. What we decline

| Declined | Why |
|---|---|
| Brouwer's Laplacian conjecture, n = 11 | **Proved** for all graphs by Kothari–Tudose (arXiv 2606.12197, read). Lew's two refinements are also proved (Lu–Yang, arXiv 2607.08452, read). A census would restate a theorem. |
| LRC for 16 runners | It needs a new finite-checking bound and prime computations whose cost grows roughly as p⁶ (Allikvere, read). S–T estimate LRC(13) at "15 years on our original machine" with their method (read). |
| Erdős–Gyárfás balanced colourings, r = 6 | r = 5 needed 12,296 SAT cells and 5.5 TB of DRAT proofs on a 96-thread cluster (Xia–Szeider, arXiv 2610.24484, read). We have no SAT solver. |
| Erdős–Gyárfás for general graphs > 40, cubic > 48 | SAT modulo symmetries, about 30 core-days already spent (Ducoffe–Dumitru, read). No SAT solver here. |
| Ramsey numbers, Erdős–Szekeres, Keller-type, Schur numbers, Hadamard maximal determinants, Golomb rulers, graceful trees, graph reconstruction at 14 vertices | Massive SAT or enumeration compute. |
| Autocorrelation constant C₆.₂ and the Erdős minimum-overlap constant | Crowded: AlphaEvolve, Together AI, the Stanford dual-agent SDP (Kim–Pilanci, arXiv 2606.31182, read: lower bounds 1.2937 and 0.37912). Lower bounds need SDP certificates and we have no SDP solver. Constructions are an arms race of 10⁻⁶ improvements. |
| Thomson N = 7, Tammes N ≥ 15, new sphere energy cases | Three-point SDP bounds (as used for N = 8 by Kryvonos–Liehr–Taylor, read). No SDP solver. Heavy recent AI-assisted activity. |
| 3D Gaussian/Epstein lattice minimisation (fcc/bcc), 2D Lennard–Jones lattice thresholds | Luo–Wei have the 3D Yukawa result (arXiv 2610.31456, read) and cite their own "On Sarnak–Strömbergsson conjecture" (arXiv 2609.17356, **not read**) and JEMS 2025 Lennard–Jones exact solutions (**not read**). The Yukawa check is already Proposal 4 M3. |
| The OEIS Open set (492 conjectures) | About 30% were resolved by generic LMs at $50 each (Adamczewski, arXiv 2608.11941, read). The authors say the conjectures are "of uncertain mathematical significance". Heavily mined. |
| Erdős-problems database (FrontierMath Erdős, 68 open) | Famous, heavily attacked by frontier labs. The finite cases left there are rarely decidable by our compute. |
| "Verify up to a larger bound" number theory (Erdős–Mollin–Walsh, Erdős ternary digits, …) | Gives only a restatement with a larger number. Low value per core-hour. |
| Graffiti or Wagner-style RL refutations at large n | Search-based groups do this faster (Roucairol–Cazenave, read). We keep only the exhaustive n = 11 niche (GR-11). |
| Polyhedral Schurian graphs at 17 vertices | Needs plantri, which is not installed, and we install nothing for a scouting study. |
| Anything framed as solving a famous conjecture (Cohn–Kumar in 2D, Kakeya, Navier–Stokes, ETH, Sendov, Hadwiger–Nelson, the full LRC) | Out of scope by our code of conduct. Our corollary-level work on these is already published and scoped. |

---

## 5. What this programme will not claim

- No "breakthrough". Each result is a finite case, a bound, an independent check, or a null box. It will be said that
  way in the title.
- Upper bounds on γ_sh are not exact values. A computational range is not an answer to a "for all n" question. An
  independent re-run is not a new theorem.
- The elementary answer to Zhang's Question 8.4 (section 2.2) is a remark for the author, not a result of this
  programme. It will not be counted or titled as a discovery.
- Sections 2.1–2.10 are in discussion order, not rank order. The rank is the table in section 1.
- Tier C enumerations are not Lean proofs. Only single certificates (witnesses, coverings, counterexamples) are
  promoted to Tier A, and only through `lean_runner.py` with a kernel replay.
- Every positive and negative control runs and is reported **before** any headline number. A failing gate is
  reported, not hidden.

## 6. Publication plan (as before)

- Each item that passes gets a short paper: statement, certificate, controls, and the code with its sha256.
- The paper goes through an independent AI audit (producer ≠ verifier) before a Zenodo DOI is minted.
- Null results are published with the same care.
- Before any item is written up, re-search arXiv for the exact case the same day. The lonely runner area moves weekly.
