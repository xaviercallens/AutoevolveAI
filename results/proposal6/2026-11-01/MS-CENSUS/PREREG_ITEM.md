# MS-CENSUS preregistration (written before any computation)

Date: 2026-11-01. Producer: Claude agent. Status of claim: RECHECK / CONSISTENCY CHECK of statements by others
(Das-Fox, arXiv 2610.39032, v1, 28 Oct 2026; the paper says GPT-5.6 Sol found the proof). No novelty claim.
This census does NOT verify the paper's proof. It can only find a finite counterexample to a lemma as stated.

## Prior art (searched 2026-11-01 before preregistration)
- Dailly, Foucaud, Hansberg, "Strengthening the Murty-Simon conjecture on diameter 2 critical graphs", Discrete Math 342 (2019)
  3142-3159 (arXiv 1812.08420): reports an exhaustive computer search of all graphs of order up to 11 for diameter-2-critical
  graphs (they found 13 non-bipartite D2C graphs outside family C5+ attaining the bound). So the n<=11 enumeration of D2C
  graphs is ALREADY DONE by others; this item is a RECOMPUTATION and, new relative to that, a per-graph test of the Das-Fox lemmas.
  I did not read that paper in full; the statement is from a search snippet. Not searched: Plesnik, Caccetta-Haggkvist, Fan,
  Hanson-Seyffarth small-n computations; other lemma-like checks.
- Furedi 1992 (large n), Haynes et al. survey 2015 (restricted classes), Das-Fox 2610.39032 (claimed proof for all n>=3).

## Definitions (pinned from the paper)
D2C: diameter exactly 2 (all pairs at distance <=2, not complete) and deleting any single edge makes the diameter >2
(disconnected counts as >2). n>=3. (Paper: "every pair at distance at most 2, loses this property if any edge is deleted";
complete graphs K_n, n>=3, are excluded by "diameter 2" and also fail criticality: deleting an edge of K_n for n>=4 leaves
diameter 2, not increased; K_3 deleting an edge gives path, diameter 2, also not increased.)
E, F = edges, non-edges (|F| = C(n,2)-|E|). Maximal matching M: matching not extendable by any edge.
Critical non-edge: non-edge with exactly one common neighbour.

Lemma 1.2 (verbatim): "Let G be a diameter-2-critical graph on n>=3 vertices, and let M be any maximal matching of G. Then |E(G)\M| <= |complement edges E(G)bar|."
Quantifier: for ALL D2C graphs and ALL maximal matchings. Not a minimal-counterexample statement; directly testable.
Lemma 1.3 (verbatim): "Let G be D2C on n>=3 vertices, and suppose that for every maximal matching M of G we have |E(G)\M| = |E(G)bar|. Then G is triangle-free." Directly testable (conditional on equality for every M).
Theorem 1.1: n>=3, D2C has <= floor(n^2/4) edges, equality only for K_{ceil(n/2),floor(n/2)}.
Secondary (stronger lemma used for 1.3): Lemma 3.1: equality case (equality for every maximal M) => G is the star K_{1,n-1} or has no critical non-edges.
Further secondary (intermediate lemmas, per graph and per maximal matching M, with I the bipartite incidence graph E vs F_c,
I' = I minus M): Lemma 2.4 (each component has a<=b+1), Lemma 2.13 (|C_l(M)| <= |F_nc|). Reported separately; failures there would
not by themselves refute Lemma 1.2 and must be examined for misreading.

## Method
1. nauty geng -c n (connected graphs, all edge counts, n=3..10; n=11 if time) split by res/mod over cores 2,3,4,5 (taskset, <=4 processes).
2. C filter (code/d2c_filter.c) on graph6 stream: bit-mask exact D2C test by explicit edge deletion and all-pairs distance<=2 check.
   Outputs the D2C graphs as graph6 per n, plus counts of connected graphs seen.
3. Python (code/lemmas.py), independent implementation: re-verify D2C with networkx (diameter, edge deletion), enumerate ALL maximal
   matchings, test Lemma 1.2 per M, equality-for-all-M detection, Lemma 1.3, Lemma 3.1, Lemma 2.4/2.13, Theorem 1.1 (max edges, extremal graphs = K_{a,b} count).
## Controls (run and logged before headline)
Positive: C5, Petersen, K_{a,b} (a,b>=2), K_{1,n-1} (star is D2C: diameter 2, every edge is a bridge; expected D2C), the 7-vertex
Figure 1 graph (edges: triangle v1v3v5 plus v2,v4,v6 each adjacent to two triangle vertices and v7? -- the exact edge set is NOT in the
extracted text; it is NOT used unless reconstructed; if reconstructed it is labelled reconstructed). Brute-force cross-check: networkx
graph_atlas (n<=7, independent of geng) gives D2C counts that must equal the geng+C counts; n=8 geng+Python D2C count must equal geng+C count.
geng connected counts must equal A001349: 2,6,21,112,853,11117,261080,11716571 for n=3..10 (n=11: 1006700565).
Negative: K_n (n>=4), C6/C7 (diameter >2), P4 (diameter 3), K_4 minus an edge (non-critical), must be rejected as D2C.
Perturbed lemmas that MUST fail on some D2C graph: (a) strict "<" in Lemma 1.2; (b) "<= |F|-1"; (c) any (non-maximal) matching M including empty; (d) "equality
case => bipartite complement"? not used. (e) Theorem 1.1 with bound floor(n^2/4)-1.
## Kill / outcome criteria
- VIOLATION FOUND: any D2C graph with a maximal matching M with |E\M| > |F|, or an equality case containing a triangle. Then: re-verify in an independent
  exact implementation, re-read the lemma for misreading, and only then report. Never conclude the paper is wrong from this alone.
- CONSISTENT: no violation for all D2C graphs with 3<=n<=N (N=10, or 11 if feasible), all controls pass.
- LEMMA UNTESTABLE: not expected.
## Tiers
Tier C: exact integer/combinatorial enumeration (finite, exhaustive). Tier X: none (no floating point used; timing numbers are measurements only).
Not claimed: the proof is correct; the conjecture holds for n>N; anything about n>N. Resources: cores 2,3,4,5, <=4 processes, ~10 core-hours.
