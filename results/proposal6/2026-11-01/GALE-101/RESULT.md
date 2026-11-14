# GALE-101: independent recheck of Voronov's 101-point set (arXiv 2610.28828)

Independent recheck of a claim by others. No novelty claim. Producer: Claude (Sonnet 5.5), core 1 only, total compute a few core-minutes.
Preregistration: PREREG_ITEM.md (sha256 f3ad4621...c82e278, written before any computation on the points).

## Outcome: CONFIRMED (for the rounded Appendix A coordinates, as the paper states Theorem 2)

| Claim in the paper | Recheck | Tier |
|---|---|---|
| 101 distinct points | 101 distinct (303 numbers parsed, PDF and alphaXiv text agree as ordered lists) | C |
| D = diameter | D^2 = 100000021020030 (units 1e-14), D = 1.0000001051; attained by one pair (19, 56) | C |
| 2030 pairs with distance > 0.88928 D | exactly 2030, threshold 88928/100000 exact, integer comparison; independent Decimal code gives the same edge set; the author's repo witness_edges.csv (2030 edges) is the same set | C |
| distance graph not 4-colourable | UNSAT, three independent routes agree (below) | C |
| beta_4(V) > 0.88928 > beta_4(S^2) | 0.88928 > sigma_3 = sqrt((3+sqrt3)/6) = 0.8880738 decided exactly (6*0.88928^2 - 3 > sqrt3 by squaring); beta_4(S^2) <= sigma_3 taken from the paper / Kalai | C (exact inequality), L (upper bound) |

### Margins (exact, from geometry_summary.json)
- Smallest included pair: ratio^2 = 39541040058709/50000010510015, ratio 0.88928096513; ratio^2 exceeds 0.88928^2 by 1.7165e-6 (ratio margin about 9.65e-8).
- Largest excluded pair: ratio 0.88925979500 (gap in ratio^2 of 3.59e-5 below the threshold).
- So the threshold 0.88928 sits in a real gap; the strict inequality for the weakest included edge holds only by about 1e-7, the same size as the 7-digit rounding (max coordinate rounding error 4.96e-8). That is why the statement is about the rounded coordinates, as the paper says; the exact computation settles it.
- Degrees 28..52, no isolated vertex, 4-core is all 101 vertices, maximum clique 4 (so non-4-colourability is not from a K5).
- Lower bound for this rounded set implied by the certificate: beta_4(V) >= 0.88928096513 (weakest edge); the author's repo reports 0.889281162393 for its 17-digit set, consistent (the paper's 7-digit coordinates are the repo coordinates rounded, in the same order, checked by Decimal).

### Non-4-colourability (headline)
- (a) Direct encoding (ALO + pairwise AMO + 2030x4 conflict clauses, vertex 0 fixed to colour 0), Glucose4 (pysat 1.9.dev17) writing a DRUP proof; drat-trim (commit 2e3b2dc0, backward) says s VERIFIED. 404 variables, 8828 clauses, proof 24312 bytes.
- (a') Same without the symmetry unit (8827 clauses): UNSAT, DRUP proof 26643 bytes, drat-trim backward and forward both VERIFIED.
- (b) CaDiCaL 1.9.5 (pysat cadical195), different encoding (order/ladder encoding, no symmetry breaking): UNSAT; also UNSAT on encoding (a).
- (c) Own exhaustive DSATUR backtracking with forward checking and colour-symmetry breaking (independent code): not 4-colourable, 745 nodes.
- CNF audit: an independent parser rebuilt the expected clause set from the edge list and found both CNF files equal to it (so the encoder is not an unchecked link).
- Graph is 5-colourable (colouring validated edge by edge), hence chromatic number 5.
- Minimal critical subgraph (deletion-based): 425 edges on all 101 vertices; every single edge deletion gives a 4-colourable graph (N2, validated colourings); certified again by Glucose4+drat-trim and by DSATUR (85246 nodes).

### Controls (all pass; run before the headline except where noted)
- P1 (code/controls_small.py, controls_small.json): K4 k=4 SAT and k=3 UNSAT, K5 k=4 UNSAT, K6 k=5 UNSAT, Grotzsch k=3 UNSAT and k=4 SAT, Moser spindle k=3 UNSAT and k=4 SAT, Petersen k=3 SAT and k=2 UNSAT; each of the 3 routes agrees with the expected verdict, UNSAT proofs drat-trim VERIFIED, SAT colourings validated: ALL_PASS.
- Corrupted-proof control: a bogus or empty proof is rejected by drat-trim, the true proof accepted.
- N5: three planted 4-colourable random graphs with 101 vertices and 2030 edges: all three routes say colourable, colourings validated.
- P2/P3 (run after the headline, see Deviations): tetrahedron and square geometry; independent Decimal edge extraction equals the integer one; Decimal vs float on a random set equal.
- N1 threshold sweep (exact rational thresholds): non-4-colourable at t = 0.888, 0.888073 (2054 edges), 0.889 (2039), 0.88928 (2030); 4-colourable at t = 0.889281 (2025 edges) and above (0.8893, 0.8895, 0.890, 0.892, 0.895, 0.90). Sorting all 5050 pairs by length: the prefix of the 2029 longest pairs is 4-colourable, adding the 2030th (ratio 0.88928096513) makes it non-4-colourable. So the set is exactly tight at its weakest edge, as the paper's q* statement implies.
- N3: moving one coordinate of a random point by 1e-3 (20 trials): all 20 become 4-colourable (edge counts change to 1885-2028); deleting any one of the 101 points: all 101 graphs 4-colourable. The configuration is fragile; it is a finely tuned object, not robust.
- N4: 50 random 60-vertex induced subgraphs: 50/50 4-colourable.
- Tier X: tetrahedral partition of the unit-diameter sphere: analytic part diameter 0.88807383398 = sigma_3 (matches), sampled lower bound 0.8865 (sanity only).

## Not checked / limits
- Gale's conjecture wording (beta_{n,n+1} = beta_{n+1}(B^n)) is as quoted by the paper; I did not read Gale 1953. beta_4(B^3) <= sigma_3 (cone partition by a regular tetrahedron; optimal by Kalai's survey) is Tier L, only sanity-checked at sphere level in floating point.
- The combinatorial step (non-4-colourable distance graph implies every 4-partition has a part of diameter > 0.88928 D, hence beta_4(V) > 0.88928) is argued, not formalised. No Lean formalisation; the paper itself says no independent review and no Lean version exist. Tier A not reached.
- Trusted components: drat-trim, pysat/Glucose4/CaDiCaL, my CNF encoder (audited by an independent clause-set rebuild), Python integer arithmetic.
- Only the 3D, 101-point set. Dimensions 4, 5, 6 and the search algorithms were not examined. The author's 17-digit set was used only for the rounding cross-check and edge-set comparison, not re-certified.
- Whether the weakest-edge ratio margin (9.65e-8) is "real" depends on the rounded coordinates being the object; for the author's 17-digit set the stored bound is 0.889281162393.

## Deviations from the preregistration
1. Prereg P1 said Moser spindle k=3 SAT; wrong (Moser spindle has chromatic number 4). Executed: k=3 UNSAT and k=4 SAT.
2. Control P2b expectation (square, t=0.7 gives 2 edges) was my arithmetic slip (sides have ratio 0.707 > 0.7); changed to t=0.8 and rerun. P2/P3 ran after the headline rather than before it (the headline is unchanged by them).
3. The first analysis run crashed in the Tier X sphere step (memory); stage outputs were saved incrementally and the step replaced by an analytic value plus a small sample; MUS/sweeps were recomputed.
4. N1 thresholds executed differ from the list in the prereg (more values, rational); N3/N4 are as stated. The prereg's "drat-trim in backward mode" was run; forward mode only for the no-symmetry proof.
5. Added beyond prereg: no-symmetry proof, CNF audit, PDF re-parse, repo cross-check.
6. Points are not stored in the repo (arXiv non-exclusive licence; author repo has no LICENSE). Hashes and fetch instructions in data/third_party_hashes.json; geom.py regenerates all derived files from the raw appendix text.

## Discrepancies with the paper
None found for Theorem 2 and Appendix A. Minor: the paper's Section 4 refers to "short independent verivication scripts" (typo) and the repo README states that no independent DRAT/LRAT checking existed (this recheck supplies one). The owner decides whether to contact the author.

## What an independent auditor must redo
1. Re-fetch the arXiv PDF, re-extract the 303 numbers with a different tool, rerun geom.py; check 2030 edges and the margin.
2. Rebuild the CNF without my encoder (e.g. another colouring encoder), solve with a different solver (kissat), and check the proof with a different checker (cake_lpr or a verified LRAT checker).
3. Review the claim chain from the graph to beta_4(V) and the Gale statement (Tier L parts) against Gale 1953; formalise in Lean if a Tier A statement is wanted.
4. Review whether the upper bound sigma_3 for the ball is correct (literature).
