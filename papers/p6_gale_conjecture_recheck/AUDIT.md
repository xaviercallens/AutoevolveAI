# GALE-101 independent audit

Auditor: Claude (Opus 5.5), not the producer. Date: 2026-11-01. I wrote all code myself and used none of the producer's code. Heavy work ran under `taskset -c 1` (at most 2 cores). Scratch work, scripts and proofs are in `/tmp/galeaudit/` and were not committed. No coordinates were copied into the repo.

## Verdict: ACCEPT_WITH_CORRECTIONS

The headline holds. For the rounded Appendix A coordinates, the 2030-edge distance graph at 0.88928 D is not 4-colourable, and it is 5-colourable. I reproduced this independently in every respect I checked.

The corrections are about wording. The biggest one is the margin: the producer stated the ratio margin 10x too small (9.65e-8 instead of 9.65e-7). That error turned a robust result into one described as "rounding-sized".

## 1. Extraction and exact geometry (own code, exact rationals)

- **Extraction.** I used PyMuPDF word boxes, clustered into rows and taken in row-major order, and separately pdfminer.six. Neither is the producer's pdftotext tool. Both give 303 tokens and agree as multisets.
- **Order and rounding.** The 101 points in row-major order are exactly the author's repo `points.csv` (17-digit) rounded half-even to 7 decimals, in the same order. Column-major order does not match. The maximum rounding error is 4.963e-8. My parsed points equal the producer's `points_scaled1e7.json`.
- **Exact arithmetic.** I computed with `fractions.Fraction` on the decimal strings and found:
  - 101 distinct points.
  - D^2 = 10000002102003/10^13, which is 100000021020030 in units of 1e-14, so D = 1.0000001051. The diameter is attained only by the pair (19, 56).
  - The test dist^2 > (88928/100000)^2 D^2, compared exactly, gives 2030 edges. No pair sits exactly at the threshold.
  - The edge set equals the producer's `edges_088928.json` and the author's `witness_edges.csv`.
- **Extreme ratios.**
  - Weakest included edge: ratio^2 = 39541040058709/50000010510015, ratio 0.8892809651305.
  - Strongest excluded pair: ratio 0.8892597950.
  - Degrees range from 28 to 52.
- **Margin.**
  - In ratio^2 the margin is 1.7165e-6, which matches the producer.
  - In ratio the margin is **9.651e-7**. The producer wrote 9.65e-8, which is wrong.
- **Rounding robustness.**
  - If every coordinate moves by at most delta = 4.96e-8, each distance (and D) moves by at most 2*sqrt(3)*delta ≈ 1.72e-7. Each ratio then moves by at most about (1 + 0.889)*1.72e-7 ≈ 3.3e-7.
  - That is below the 9.65e-7 included margin, and far below the 2.02e-5 gap on the excluded side (0.88928 - 0.8892597950). The same holds for the full half-ulp delta = 5e-8: about 3.27e-7 against 9.65e-7, so the argument covers any set that rounds to Appendix A.
  - So every point set within the rounding box has the same 2030-edge graph at t = 0.88928. The rounding is not a risk to the claim.
  - Direct confirmation: the 17-digit repo set gives D = 1.0 (argmax pair (12, 37), a different pair) and **the identical 2030-edge set** (symmetric difference 0). Its weakest ratio is 0.8892811623939, matching the author's stored 0.889281162393.
- **beta_4(V) is determined exactly.** Sorting pairs by length, the weakest edge is the 2030th pair, and the 2029 longest pairs form a 4-colourable graph. PicoSAT found a colouring, which I decoded and validated edge by edge (class sizes 21/20/37/23); its longest monochromatic pair is exactly pair #2030. Therefore beta_4(V) = sqrt(39541040058709/50000010510015) = 0.88928096513, an equality, where the producer wrote ">=".
- **Gale inequality.** 0.88928 > sigma_3 holds exactly: (6t^2 - 3)^2 > 3 with 6t^2 - 3 > 0. sigma_3 = 0.8880738340.

## 2. Non-4-colourability with a different encoder, solver and checker

- **Different encoding.** I used a log/binary encoding with 2 bits per vertex, 202 variables, no ALO/AMO and no symmetry breaking. Each edge gets 4 clauses of 4 literals, 8120 clauses in total.
- **Encoder controls.** K4 is 4-colourable, K5 is not, the Moser spindle is 4-colourable, and a planted 4-colourable graph with 101 vertices and 2030 edges is 4-colourable. All four pass, and every SAT colouring was validated.
- **Different solvers.**
  - PicoSAT (pycosat 0.6.6) reports UNSAT on the log encoding, and also on a direct encoding without AMO.
  - CaDiCaL 3.0.1 (git c607304, a different major version from the producer's pysat cadical195) reports UNSAT.
- **Proof checking.**
  - CaDiCaL wrote a DRAT proof; drat-trim (the third-party build) says `s VERIFIED`.
  - CaDiCaL wrote an LRAT proof. `lrat-check.c`, compiled by me, says `c VERIFIED`. **My own Python LRAT checker** (RUP hints only, RAT rejected) checked 6246 lemmas and verified the proof.
  - Negative control: I dropped one hint from one line. Both LRAT checkers rejected the result ("hint 7780 not unit" / "multiple literals unassigned").
  - Not done: kissat. Building kissat was refused by the session's permission classifier, and cake_lpr was not built.
- **Producer artefacts.**
  - drat-trim backward gives `s VERIFIED` on `gale101_k4.drup`, and backward and forward both give `s VERIFIED` on `gale101_k4_nosym.drup`.
  - drat-trim -L turned the no-symmetry proof into LRAT. lrat-check says VERIFIED, and my Python checker verified 294 lemmas.
  - I decoded the producer's no-symmetry CNF into a graph: 101 ALO clauses, 606 AMO clauses, 2030 edges each with 4 colour clauses, and no stray clauses. It equals my edge set. CNF hashes match `result.json`.

## 3. 5-colouring and critical subgraph

- **5-colouring.** PicoSAT on a direct 5-colour encoding found a colouring, which I validated edge by edge. The chromatic number is therefore 5.
- **Critical subgraph.** I checked the producer's 425-edge list:
  - It is a subset of my 2030 edges and touches all 101 vertices.
  - It is UNSAT under the log encoding with PicoSAT.
  - **All 425** single-edge deletions are 4-colourable, with validated colourings. This was exhaustive, not a sample.
  - So it is a minimal (edge-critical) non-4-colourable subgraph. I did not check whether it is minimum-size; the producer does not claim that either.
- **Vertex deletions.** Deleting any one of the 101 vertices from the full graph leaves a 4-colourable graph. This confirms the producer's N3.

## 4. Logical chain and constants (paper text read)

- **Definitions.** Definition 1: beta_k(A) = inf over partitions of max_i diam A_i / diam A. Definition 2: beta_{n,k} = max beta_k(A). Conjecture 1 (Gale 1953 [6], as quoted): beta_{n,n+1} = beta_{n+1}(B^n).
- **The chain.**
  - V is finite, so the infimum is a minimum.
  - A partition into 4 parts is a 4-colouring. Since G_t is not 4-colourable, some part contains an edge, and that part has diameter > tD.
  - So beta_4(V) > t, where the ratio is taken relative to D = 1.0000001051. That normalisation is applied correctly, because the threshold multiplies D, not 1.
  - The chain is valid. It is argued, not formalised.
- **The ball bound needed for the refutation reduces to diam T.**
  - The refutation only needs beta_4(B^3) <= sigma_3, not optimality. That bound comes from the explicit cone partition over a regular tetrahedron. Each cone lies in conv({0} ∪ T), whose diameter is max(diam T, 1/2) = diam T.
  - The vertex-to-opposite-midpoint chord is (1/2)*sqrt(2 + 2/sqrt3) = sqrt((3+sqrt3)/6) = sigma_3 (analytic). That gives diam T >= sigma_3. The equality diam T = sigma_3 is supported only by floating-point dense sampling of the whole spherical triangle (6000 boundary + 4000 interior points: max 0.888073833977, equal to sigma_3 to 2e-16). It is not proved here: Tier X. The paper asserts it.
  - Only the optimality beta_4(B^3) = sigma_3, cited to Kalai [11], is Tier L, and the refutation does not need it.
  - The wording of Gale's conjecture is taken from the paper's quotation of [6]. I did not read Gale 1953: Tier L.

## 5. Literature (2026-11-01)

- alphaXiv lists only the paper itself (5 votes) and the related 2610.39078 (Borsuk number in R^4 <= 7).
- The MathWorld "Gale's Conjecture" entry restates the claim. It is a report, not a verification.
- I found no independent verification, refutation or comment.
- The paper states (fn. 1) that there is no Lean formalisation and no independent review. The author's README says no DRAT/LRAT checking exists. This recheck supplies DRAT/LRAT checking.

## 6. Wording

- `RESULT.md` and `result.json` correctly say "independent recheck of a claim by others; no novelty claim", Tier C, Tier A not reached.
- They contain no "we disproved Gale" claim. Keep it that way: the refutation is Voronov's.
- PREREG hash verified: f3ad4621...c82e278.

## Corrections (exact old -> new, in RESULT.md)

1. **Line 17.** Old: "(ratio margin about 9.65e-8)." New: "(ratio margin about 9.65e-7)."
2. **Line 19.** Old: "the strict inequality for the weakest included edge holds only by about 1e-7, the same size as the 7-digit rounding (max coordinate rounding error 4.96e-8). That is why the statement is about the rounded coordinates, as the paper says; the exact computation settles it." New: "the strict inequality for the weakest included edge holds by 9.65e-7 in ratio, about 3x the worst-case ratio change (about 3.3e-7) that a coordinate rounding of up to 5e-8 (half-ulp) can cause, and the excluded side has a gap of 2.02e-5. So any point set within the 7-digit rounding box, including the author's 17-digit set (checked: identical 2030-edge set), has the same graph. The statement is made for the rounded coordinates, as the paper says, and the exact computation settles it."
3. **Line 21.** Old: "Lower bound for this rounded set implied by the certificate: beta_4(V) >= 0.88928096513 (weakest edge)". New: "Exact value for this rounded set: beta_4(V) = 0.88928096513... (weakest edge; the 2029 longest pairs are 4-colourable, validated colouring, so a partition achieving this ratio exists)".
4. **Line 47.** Old: "Whether the weakest-edge ratio margin (9.65e-8) is \"real\" depends on the rounded coordinates being the object; for the author's 17-digit set the stored bound is 0.889281162393." New: "The weakest-edge ratio margin is 9.65e-7, larger than any rounding effect; the author's 17-digit set gives the same edge set with weakest ratio 0.889281162393."
5. **Line 43 (clarification, tier unchanged).** Old: "beta_4(B^3) <= sigma_3 (cone partition by a regular tetrahedron; optimal by Kalai's survey) is Tier L, only sanity-checked at sphere level in floating point." New: "beta_4(B^3) <= sigma_3 follows from the explicit tetrahedral cone partition. The reduction to the spherical-triangle diameter diam T is rigorous (each cone lies in conv({0} u T)). diam T = sigma_3 is asserted by the paper and supported by dense floating-point sampling (Tier X), not proved here, so the upper bound stays Tier L. Its optimality (Kalai [11]) is also Tier L and is not needed for the refutation." Keep upper_bound_ball = "L" in result.json.
6. **Line 40 (optional).** Replace "sampled lower bound 0.8865" with the auditor's dense-sample value 0.888073833977 (whole triangle).

## What remains unverified

- Gale 1953's original wording. It is Tier L, taken from the paper.
- Optimality of sigma_3 for the ball. It is Tier L and not needed.
- diam T = sigma_3 for the tetrahedral spherical triangle. Only a lower bound (analytic chord) and floating-point dense sampling were done; no proof (Tier X/L). This is the one non-elementary link in beta_4(B^3) <= sigma_3.
- No Lean formalisation of the graph-to-beta_4 step or of UNSAT: Tier A is not reached.
- Trusted components: drat-trim, lrat-check.c (same author family as drat-trim), my roughly 40-line Python LRAT checker, PicoSAT, CaDiCaL 3.0.1, PyMuPDF/pdfminer and Python Fraction.
- Not done: kissat (build blocked by the permission classifier) and a formally verified checker such as cake_lpr.
- The dimension 4 to 6 sets and the search code were not examined.
