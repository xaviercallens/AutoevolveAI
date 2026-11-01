# MS-CENSUS result: census of diameter-2-critical graphs and per-graph test of Das-Fox Lemmas 1.2 / 1.3, n = 3..11

**Outcome: CONSISTENT.** No violation of Lemma 1.2, Lemma 1.3 (or of the intermediate Lemmas 2.4, 2.5, 2.13, 3.1, 3.2, or of
Theorem 1.1) on any of the 4,419 diameter-2-critical (D2C) graphs with 3 <= n <= 11. Preregistration: PREREG_ITEM.md
(sha256 b731521c12d72e6bb9a250d9aa4f5ea602e3788dbf52ae519abc2a886d7b5d56, written before any computation).

**What this is.** A recheck / consistency check of statements by others (Das-Fox, arXiv 2610.39032, which says GPT-5.6 Sol found
the proof). It tests the lemma STATEMENTS on a finite range. It does NOT verify the proof, says nothing for n >= 12, and makes no
novelty claim. The enumeration of D2C graphs up to n = 11 was already done by others (Dailly-Foucaud-Hansberg, Discrete Math 2019,
arXiv 1812.08420, per a search snippet; paper not read in full), so the enumeration part is a RECOMPUTATION; the per-graph test of
the Das-Fox lemmas is what this adds, and I did not search whether anyone else has run it.

## Statements tested (verbatim from the paper, pinned in the preregistration)
D2C = diameter 2 and deleting any edge raises the diameter. Lemma 1.2: for every D2C G (n >= 3) and EVERY maximal matching M,
|E(G) \ M| <= |non-edges of G|. Lemma 1.3: if equality holds for EVERY maximal matching, G is triangle-free. Both are
unconditional universally-quantified statements (no minimal-counterexample hypothesis), so they are directly testable.

## Numbers (Tier C: exact integer enumeration, no floating point)
| n | connected graphs (geng -c) | = A001349 | D2C graphs | max edges | floor(n^2/4) | extremal graphs (all = K_{ceil,floor}) | equality cases of L1.2 (all M) | maximal matchings tested |
|---|---|---|---|---|---|---|---|---|
| 3 | 2 | yes | 1 | 2 | 2 | 1 | 1 | 2 |
| 4 | 6 | yes | 2 | 4 | 4 | 1 | 1 | 5 |
| 5 | 21 | yes | 3 | 6 | 6 | 1 | 1 | 15 |
| 6 | 112 | yes | 5 | 9 | 9 | 1 | 1 | 39 |
| 7 | 853 | yes | 10 | 12 | 12 | 1 | 1 | 147 |
| 8 | 11,117 | yes | 30 | 16 | 16 | 1 | 1 | 788 |
| 9 | 261,080 | yes | 103 | 20 | 20 | 1 | 1 | 5,142 |
| 10 | 11,716,571 | yes | 519 | 25 | 25 | 1 | 1 | 50,991 |
| 11 | 1,006,700,565 | yes | 3,746 | 30 | 30 | 1 | 1 | 719,088 |

Total D2C graphs 3..11: 4,419 (1+2+3+5+10+30+103+519+3746). Violation counts for L1.2, L1.3, L2.4, L2.5, L2.13, L3.1, L3.2: all 0 for every n. Every equality case is the
balanced complete bipartite graph, which is triangle-free, so Lemma 1.3 and 3.1 hold; the K_{a,b} extremal graph is the unique graph with
|E| = floor(n^2/4) at each n (Theorem 1.1 consistent). I could not match the D2C counts 1,2,3,5,10,30,103,519,3746 against an
OEIS sequence (not searched; no claim).

Caveat on strength: Lemma 1.3's hypothesis is satisfied by exactly one graph per n (the extremal K_{a,b}), so its test is nearly
vacuous in this range. Lemma 1.2 is tested on 776,217 maximal matchings (sum of the last column) on every D2C graph, which is the informative test.

## Controls (all passed; data/controls.json)
- geng connected-graph counts equal A001349 for n = 3..11 (the n = 11 total, 1,006,700,565, is the sum over 4 res/mod parts).
- D2C predicate: positives C4, C5, Petersen, K_{2,3}, K_{3,3}, K_{4,5}, star K_{1,5}, and the Figure 1 graph (edge list reconstructed from the
  three quoted critical 2-paths and the stated triangle, labelled RECONSTRUCTED: every non-edge critical, contains a triangle, D2C).
  Negatives K3, K4, K5, K4-e, C6, C7, P4 all rejected.
- Independent counts: networkx graph_atlas (independent of geng) gives D2C counts equal to the geng+C counts for n = 3..7; geng + Python/networkx
  predicate gives 30 at n = 8, equal to the C filter. The C filter and the Python re-verification agree on all 4,419 graphs
  (0 graphs that the C filter accepted were rejected by networkx).
- Maximal-matching enumerator equals a brute force (all edge subsets) on 40 random graphs with n in 4..7.
- Perturbed lemmas that must fail do fail: strict "<" in Lemma 1.2, "<= |F|-1", the empty (non-maximal) matching, and the bound floor(n^2/4)-1
  (fail at the extremal graph at every n; K_{3,3}, K_{4,5} spot-checks in controls.json).

## Not checked / limits
The proof (Lemmas 2.x, 3.x beyond those tested per graph, and the logical deduction of Theorem 1.1) is not verified. Nothing is said about
n >= 12 (n = 12 has ~1.65e11 connected graphs, estimated ~16 wall-hours on 4 cores with this pipeline; not run). The reading of "maximal
matching" (no edge can be added) and "diameter-2-critical" (diameter exactly 2, so K_n excluded) follows the paper's text; the
Figure 1 graph is reconstructed, not copied. The lemma checker is my own implementation (code/lemmas.py) of the paper's definitions of
critical non-edge, I, I', C_l; a misreading of those intermediate definitions would not affect the checks of Lemmas 1.2, 1.3 and Theorem 1.1,
which use only edges, non-edges, maximal matchings and triangles.

## Resources
Cores 2-5 only, <= 4 processes. Wall: n <= 10 about 4 s, n = 11 358 s (4 cores, about 0.4 core-hours); lemma checks 1 min 43 s wall.
Total about 0.5 core-hours of the 10 allowed.

## What an independent auditor must redo
1. Re-run geng -c n (n = 3..11) and a separately written D2C test (not reusing code/d2c_filter.c or networkx is_d2c) and compare counts 1,2,3,5,10,30,103,519,3746.
2. Re-read Lemmas 1.2 and 1.3 in the paper and confirm they match the statements above; recompute all maximal matchings with a different enumerator.
3. Compare with the enumeration in Dailly-Foucaud-Hansberg (2019), including their 13 extra non-bipartite extremal graphs for their strengthened bound (not tested here).
4. Treat this as no evidence about the correctness of the proof beyond the finite range.
