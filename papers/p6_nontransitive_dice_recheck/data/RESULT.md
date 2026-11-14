# DICE-6 result: recheck of Easlick arXiv 2610.40321

Outcome: CONFIRMED for everything the paper computes that was rechecked (n=3..9 graph statistics; n=6 theorem). n=10 and the full-n>=7 conjecture were not rechecked. Recheck of a claim by others; no novelty claim. Preregistration: PREREG_ITEM.md (sha256 b3425a39bfecd0b1a3059068efc59aeed984140586873c5923ce4b3a70051765), written before any computation.

## Definition pinned (paper, Defs. 1-2, eqs 1,3,4)
n-sided die = multiset of n faces in [n]; D_x beats D_y iff P(X>Y) with strict inequality (ties lose); the minimal probability above 1/2 is W = floor(n^2/2)+1 over n^2 pairs (1/2+1/n^2 even n, 1/2+1/(2n^2) odd n). Edge iff W equals that value; a "uniform minimal" cycle is a cycle in this graph. "Maximum length n" is not formally defined; read here as: an n-cycle exists and no longer cycle exists (consistent with n=6 SCCs of 7 vertices). Note: this is not Trybula's maximin problem (best minimal winning probability); it is a different question.

## Results (Tier C: exact integer/Fraction arithmetic, two independent implementations for n<=6)
| n | dice | edges | SCCs | nontrivial SCC | paper |
|---|---|---|---|---|---|
| 3 | 10 | 3 | 10 | none | match |
| 4 | 35 | 67 | 35 | none | match |
| 5 | 126 | 620 | 126 | none | match |
| 6 | 462 | 5491 | 450 | two, 7 vertices / 10 edges each | match |
| 7 | 1716 | 89153 | 636 | one: 1081 / 53389 | match |
| 8 | 6435 | 956307 | 2115 | one: 4321 / 674108 | edges, SCC size match (SCC count not stated) |
| 9 | 24310 | 12528131 | 3860 | one: 20451 / 10933011 | match |

- n=3,4,5: no directed cycle at all (all SCCs trivial), hence no n-cycle. Reproduced.
- n=6: exhaustive simple-cycle enumeration inside the two 7-vertex SCCs gives exactly 2 six-cycles (plus 6 three-cycles), and no 7-cycle. Both six-cycles equal the paper's (SCC 1 cycle and the f-image); every edge exactly 19/36 by Fraction check. The map f(x)=(7-x_6..7-x_1) reverses edges (checked on all edges in the pure-Python graph, and on a 200x200 block for the converse) and swaps the cycles. So Theorem 1's n=6 part (a 6-cycle exists; longest cycle is 6; exactly two 6-cycles) is reproduced; with n=3,4,5 having no cycles, n=6 is the smallest n>=3 with an n-cycle.
- n=7,8,9: the paper's printed cycles (lengths 14, 29, 10) were parsed from the text; the printed order is a valid cycle for all three (exact check, all edges at minimal probability). So cycles longer than n exist, as stated. My own randomized search found valid exact cycles of lengths 7, 8, 14 in G_7 (Tier X search, Tier C check): so at n=7 an n-cycle exists but longer cycles also exist, which is why the paper's "maximum length n" reading fails for n>=7. The conjecture (n=6 is the largest) rests on this reading and is supported only by the existence of a longer cycle for n=7..10 (n=10 not rechecked).
- Not done: n=10 graph (157M edges), any n>=11, any proof of the conjecture.

## Controls
Positive: Efron set exact 2/3 on all four edges; Moon-Moser (2,4,9),(1,6,8),(3,5,7) exact 5/9 (reverse 4/9). Context maximin for 3-cycles of m-sided dice in [m] (X): m=5 3/5, m=6 7/12, m=7 29/49, all below (sqrt5-1)/2 = 0.618; m=4 has no 3-cycle. Negative: transitive triple has probs 5/18, 1/4, 2/3 (no cycle); all 62 single-face +-1 perturbations of the paper's n=6 cycle break the uniform minimal cycle; predicate rejects a W=36 pair.

## Caveats
Graph statistics for n=7..9 come from a single numpy implementation (independent of the Julia code but not duplicated by a second implementation of mine beyond the n<=6 brute force). The paper's cycles for n>=7 are checked, not the paper's claim that SCC contents are as listed in the appendices (only sizes). The n>=7 longest-cycle question is NP-hard in general and undecided here.

## Auditor should redo
Run code/dice_graph.py and code/verify.py from code/ (Python with numpy/scipy); independently re-implement the edge predicate W = floor(n^2/2)+1 and re-count n=6 cycles with a different language; check the Julia appendix output for n=10.
