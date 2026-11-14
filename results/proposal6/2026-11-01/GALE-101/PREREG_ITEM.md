# PREREG GALE-101 (independent recheck of a claim by others; not new)

Date: 2026-11-01. Producer: Claude (Sonnet 5.5). Compute: core 1 only (taskset -c 1), time box about 3 core-hours.
Status: written and hashed BEFORE any computation on the 101 points. Only the paper text and the repository
file listing/certificate.json were read before this file.

## Source (third-party; not copied into the repo)
- Paper: V. Voronov, "A counterexample to Gale's conjecture in R^3", arXiv:2610.28828v1 (20 Oct 2026), Appendix A, Table 2
  (101 points, 7-decimal coordinates, listed in two columns of 3 numbers). Paper licence: not stated in the text I read;
  it is therefore NOT copied into the repo. Raw appendix text is stored in
  /home/callensxavier_gmail_com/gale101_thirdparty/paper/appendixA_raw.txt (sha256 a1661e91fcdcccf93dbe1cb2dea37c614277e99ec8fdc0e848983a453776a903,
  303 numbers = 101 points). The repo will hold only its hash, a parse recipe, and derived summaries.
- Author repository https://github.com/vsvor/Gale-conjecture (no LICENSE file found at the root path). Its best_known/3d_101p_088928
  certificate uses 17-digit coordinates (a different, polished point set: lower bound 0.889281162393, 2030 witness edges).
  It is NOT the object rechecked here; the object is the paper's Appendix A rounded coordinates, as the paper states
  ("Theorem 2 holds for these rounded coordinates themselves").
- The repo README says "no independent DRAT/LRAT proof checking is provided" and the witness.cnf is not an UNSAT proof.

## Claims being rechecked
C1. Gale's conjecture (1953), as stated in the paper: for every n >= 2, beta_{n,n+1} = beta_{n+1}(B^n), with
    beta_k(A) = inf over partitions of A into k parts of max_i diam(A_i)/diam(A).
    The claimed refutation (n = 3): a finite V in R^3, |V| = 101, with beta_4(V) > 0.88928 > beta_4(S^2) (S^2 = sphere of unit diameter,
    beta_4(S^2) <= sigma_3 = sqrt((3+sqrt3)/6) = 0.88807...).
C2. If D = diam V (max pairwise distance), the pairs with distance > 0.88928 D number 2030, and the graph G on 101 vertices with
    these edges has no proper 4-colouring.
Logical bridge (checked by reasoning, not by computation): if G is not 4-colourable then in every partition of V into 4 parts some part
contains both ends of an edge, so its diameter is > 0.88928 D. Hence beta_4(V) >= 0.88928 (strict part diameter), and
beta_{3,4} >= beta_4(V) because V is a bounded set. The inequality 0.88928 > sigma_3 is an exact algebraic fact
(0.88928^2 = 0.7908... > (3+sqrt3)/6 = 0.7886...), decided exactly in the code. The upper bound beta_4(B^3) <= sigma_3 (tetrahedral cone partition)
is taken from the paper/Kalai as literature (Tier L), with a floating-point sanity computation (Tier X).

## Method
1. Parse: all 303 numbers in order, group in triples. Coordinates are decimals with 7 digits, so exactly rational: p = integer / 10^7.
   All computations use Python integers (squared distances scaled by 10^14). Expected: 101 distinct points.
2. Geometry, exact: all 5050 squared distances; D^2 = max; threshold T = 88928/100000 exactly; edge iff 10^10 * d^2 > 88928^2 * D^2
   (integers). Report: edge count, the smallest included and the largest excluded ratio^2 as exact fractions, gaps to the threshold
   squared, number of pairs achieving D, whether threshold sits in a gap. Also report the degree sequence, 4-core size.
3. Non-4-colourability, three independent routes:
   (a) SAT, one-hot encoding x[v][c], at-least-one, at-most-one (pairwise), edge conflicts, vertex 0 fixed colour 0 (symmetry breaking on
       the colour class of one vertex only), solver Glucose4 (pysat 1.9) with DRUP proof output, proof checked by drat-trim
       (built from github.com/marijnheule/drat-trim commit 2e3b2dc0) in backward mode;
   (b) SAT, a different encoding (no symmetry breaking, at-least-one + "at-most-one by sequential counter / binary-free ladder" encoding
       or equivalently colour-classes formulation with an extra, redundant clause set) with CaDiCaL 1.9.5 (pysat cadical195); verdict must agree;
   (c) an own exhaustive backtracking (DSATUR order, colour symmetry breaking by first-unused-colour rule, on the 4-core graph) returning
       UNSAT with a node count; independent code path from (a),(b).
   Accept UNSAT only if (a)'s drat-trim says VERIFIED, (b) and (c) say UNSAT.
4. Further structure: 5-colourability (SAT then verified colouring checked exactly against the edge list); chromatic number is then 5 if 4 fails and 5 holds.
   Minimal unsat core (greedy edge deletion on the 4-core, or MUS extraction by deletion) to give a small critical subgraph, re-verified by (a).
5. Gale link: exact check 88928^2 * 6 > 10^10 * (3 + sqrt 3)... decided exactly with integer arithmetic (compare 6*88928^2 - 3*10^10 > sqrt3*10^10 by squaring);
   floating-point check that the tetrahedral partition of the unit-diameter sphere has max part diameter sigma_3 (Tier X).

## Controls (all run and logged BEFORE the headline number is reported)
Positive (the pipeline must say what is known):
- P1. The encoding/solver/proof pipeline returns UNSAT, with a drat-trim VERIFIED proof, on K5 (4-colouring) and on the Grotzsch graph
  (chromatic number 4 - tested with k = 3) and returns SAT for the Moser spindle with k = 3 and for K4 with k = 4; colourings checked edge by edge.
- P2. Geometry code on a known set: regular tetrahedron vertices plus integer scaling: D^2 correct, all 6 pairs are edges for t < 1.
- P3. The edge-extraction, parse and count code, run on a synthetic 101-point set with a known graph (random integer points, graph recomputed by
  an independent float code), must agree.
Negative (the pipeline must be able to fail):
- N1. Raising the threshold: with threshold t' set to the largest exact ratio below which the graph still has 2030 edges is boundary; for thresholds t' in
  {0.8893, 0.8895, 0.890, 0.892, 0.895, 0.90} the graph must become 4-colourable at some t' (the smallest such t' is reported); this is
  consistent with the paper's tightness claim (q* = 0.889281...), and for t' = repo bound 0.889281162393 the pairs with ratio > t' are the same 2030
  or fewer. A report of 4-colourability at t' > ratio of the weakest edge is expected and is NOT a discrepancy.
- N2. Remove each edge of the 4-core (or of the extracted minimal critical subgraph): a critical subgraph must become 4-colourable after any single edge deletion
  (checks that UNSAT is not an artefact of a degenerate encoding).
- N3. Perturb one coordinate of the 101 points by 1e-3 (several seeds) or delete one point: the full 2030-edge claim is expected to fail or the graph to change; report whether UNSAT
  survives (informational, not a pass criterion).
- N4. 50 random 60-point subsets of V (induced subgraph of the claimed graph's vertex subsets, with the same threshold on the whole-set D) are 4-colourable
  except those containing a critical subgraph; report counts. Must contain 4-colourable ones.
- N5. Known-satisfiable instance: planted 4-colourable random graph with the same vertex/edge count must return SAT and the colouring must validate.

## Kill / outcome criteria
- NOT CONFIRMED if: (i) the parse does not give exactly 101 distinct points, OR (ii) the exact edge count differs from 2030 AND the resulting graph is 4-colourable,
  OR (iii) the graph (whatever its edge count) is 4-colourable (a 4-colouring exists and validates exactly), OR (iv) the exact threshold comparison
  0.88928 vs sigma_3 fails.
- PARTIAL if: the edge count differs from 2030 (or D / threshold behaves differently from the paper's statement) but non-4-colourability still holds with a verified proof, or if
  the drat-trim check cannot be completed while two independent solvers and the exhaustive search agree.
- CONFIRMED if: 101 distinct points, exactly 2030 edges at the exact threshold 88928/100000, UNSAT with drat-trim VERIFIED, agreement of cadical195 and the exhaustive search, all
  positive controls pass, N1/N2/N5 behave as expected.
- Any control failure invalidates the headline: it is reported as BLOCKED, not as a result.

## Tiers
C: exact integer geometry plus certified UNSAT (drat-trim verified DRUP proof, produced by Glucose4 with the encoding stated; the drat-trim binary and
the CNF encoder are trusted code; no Lean). X: floating-point sanity checks (tetrahedral partition diameters). L: the upper bound beta_4(B^3) <= sigma_3 and the equivalence of
Gale's statement as quoted by the paper (not independently checked against the 1953 original, which I do not have). No novelty claim. Tier A would require a Lean statement plus a verified checker: not done.

## Not claimed / out of scope
No review of the paper's other dimensions (4, 5, 6) or of the search algorithms; no claim about the author's 17-digit repository set beyond what is explicitly stated;
no claim that beta_{3,4} is strictly larger than the ball value in the sense of the original wording of Gale (1953) beyond the paper's definitions; no contact with the author (owner decides).
