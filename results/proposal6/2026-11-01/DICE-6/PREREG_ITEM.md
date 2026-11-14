# DICE-6 preregistration (written before any computation)
Date 2026-11-01. Recheck of Easlick, arXiv 2610.40321 (read in full via alphaXiv text; copy in data/). Not a novelty claim.

## Pinned definitions (from the paper)
- A die: multiset of n face values in [n]={1..n}, each face prob 1/n. Number of dice C(2n-1,n).
- D_x beats D_y: P(X>Y) strict, ties do not count. W(x,y)=#{(i,j): x_i>y_j} out of n^2.
- Minimal winning probability >1/2: W = floor(n^2/2)+1 (even n: 1/2+1/n^2; odd n: 1/2+1/(2n^2)).
- Edge x->y iff W(x,y)=floor(n^2/2)+1. Non-transitive cycle of length k: distinct dice D1..Dk with D_i->D_{i+1} (cyclically), all edges at the minimal advantage (uniform+minimal).
- "Maximum length n": read as: an n-cycle exists and no longer cycle exists in G_n (n=6: SCCs of 7 vertices, no 7-cycle). Alternative reading (only existence of an n-cycle) is also reported.

## Claims under test
C1 n=3,4,5: G_n has no directed cycle (paper: 10/35/126 vertices, 3/67/620 edges).
C2 n=6: 462 vertices, 5491 edges, 450 SCCs, two nontrivial SCCs of 7 vertices / 10 edges, each with a 6-cycle and no 7-cycle; exactly two 6-cycles (swapped by f(x)=(7-x_6..7-x_1), an edge-reversing involution).
C3 n=7..10 (evidence): vertices 1716/6435/24310/92378, edges 89153/956307/12528131/157244770, single big SCC 1081/4321/20451/81791 vertices; cycles longer than n exist (paper's cycles of length 14, 29, 10, 110).

## Method
(a) Independent numpy implementation (count-vector form of the double sum) of vertices, edges, SCCs (scipy), exhaustive cycle enumeration in SCCs for n<=6; plus a pure-Python brute-force double-sum cross-check for n<=6 (and n=7 edge count). Exact integer arithmetic; probabilities as Fractions.
(b) Exact Fraction re-verification of the paper's printed cycles for n=6,7,8,9 (n=10 optional) and of my own cycles.
(c) n=7..9 counts vs paper; own cycle longer than n. Longest-cycle / n-cycle existence for n>=7 is NOT decided (NP-hard in general); report only what is found.
(d) "Minimal" is by definition W=floor(n^2/2)+1, so no optimisation is claimed. As orthogonal context control only: Trybula/Moon-Moser maximin over 3-cycles of 9-sided dice in [9] (expect 45/81=5/9, bound (sqrt5-1)/2).

## Controls
Positive: Efron 4-dice set exact 2/3 per edge; Moon-Moser 5/9 triple; paper's n=6 cycles have all 6 edges exactly 19/36. Negative: transitive set (a pair with P<=1/2); perturbing one face of a paper-cycle die by +-1 destroys the uniform minimal cycle; predicate rejects non-minimal pairs (W=20).

## Decision rules
CONFIRMED if C1, C2 reproduce exactly (counts, the two cycles, no 7-cycle) and paper cycles for n=7..9 verify. PARTIAL if any count differs or n>=7 parts unreproduced. Tier C for exact verification, X for searches. Cores 6,7 only.
