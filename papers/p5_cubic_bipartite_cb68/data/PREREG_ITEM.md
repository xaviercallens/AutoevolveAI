# EG-CB68 item-level preregistration (written 2026-10-28 ~17:06 UTC, before any search binary was built or run)

Parent preregistration: `results/proposal5/2026-10-27/preregistration.json`
(sha256 140a28adfc1932e5330d650ffe43a43d9c8e417d9b38cbbdd7f03174a55ae9be, not edited), item EG-CB68, lane W1-c.
This file only makes the parent's EG-CB68 entry operational; where they differ the parent wins.

## Statement under test
Every simple cubic bipartite graph on at most 68 vertices contains a cycle of length 4, 8 or 16.
Equivalently (Tranquilli 2608.02675 Prop. 3, Lemmas 5, 6): no connected linear symmetric v_3-configuration with
v <= 34 avoids Berge 4- and 8-cycles (Levi C8, C16).

## Same-day literature re-search (2026-10-28, before the first run)
- alphaXiv discover_papers (recency) "Erdos-Gyarfas conjecture / cubic bipartite": newest relevant items are
  Tranquilli 2608.02675 v1 (<= 58) and Ducoffe-Dumitru 2609.28594 v1 (bipartite <= 66, SAT, no proof log). Nothing at 62+ for cubic bipartite.
- WebSearch "Erdos-Gyarfas cubic bipartite counterexample lower bound 62 OR 64 OR 68 OR 70 vertices Tranquilli": nothing beyond 60.

## Reduction premise (pinned before start)
- Moore: a cubic bipartite graph of girth >= 10 has >= 62 vertices (Tranquilli Lemma 8 argument). Covers caps v <= 30 (2v <= 60).
- (3,10)-cage order n(3,10) = 70 (O'Keefe-Wong, JCTB 29 (1980) 91-105; completeness Wong 1983, McKay et al. 2000).
  Read in session only through the Exoo-Jajcay Dynamic Cage Survey (EJC DS16 v3, 2013), p. 7 Table 1 and p. 10 §2.1.6,
  which states "The proof for girth 10 was computer assisted [91]". The original paper was NOT read.
  This is a Tier L premise (itself a computer result). Caps 31..34 (2v = 62..68) rest on it; girth >= 12 is excluded by the Moore bound 126.
- Hence for 2v <= 68 a C4- and C8-free cubic bipartite graph has girth exactly 6, i.e. a Berge triangle, and the triangle-rooted search is complete (Tranquilli Prop. 10) for every cap <= 34.

## Elementary-attack pass (repeated here, about 10 minutes)
Tried: counting C6 / C8 / C16 via eigenvalue (trace) bounds of the Levi graph; local density near a Berge triangle;
whether C8-freeness plus girth 6 forces a small dense substructure with a forced 16-cycle. Nothing closes the case;
the C6-forcing argument only reduces it to the finite search. Same conclusion as the parent.

## Method (fixed before running)
1. New C program `cb_search.c`: triangle-rooted restricted-growth search exactly as in Tranquilli §3.1, two roots
   {0,1,3},{1,2,4},{0,2,5} + {0,4,6} (orbit 1) or {0,6,7} (orbit 2), processing the least unfinished point, proposals in
   lexicographic order, reject order: structural, then C8 (Levi path of length 6 between two block points), then C16 (length 14).
   Two C16/C8 oracles selectable at run time: (A) DFS simple paths; (B) join of complete half-path lists.
   Both must give identical counters AND identical ordered decision-transcript hashes.
2. Separate streaming checker (`cb_check.py`, Python, written separately) that regenerates the proposal schedule,
   checks structural rejections directly, checks every C8/C16 witness path (simple, in the pre-insertion Levi graph,
   correct length, endpoints two distinct points of the proposal), recurses into accepted proposals, and fails on any completion.
   Tamper tests (truncated stream, flipped counter, corrupted witness) must be rejected.
3. Caps: 29 (control), 30, 31, ... as far as the time box allows, 2 orbits, on taskset -c 2,3 only.

## Controls (all run and reported before any headline number)
Positive
- P1: cap 29 reproduces Tranquilli Table 2 per orbit: states 1,405 / 20,088; attempted 106,964 / 1,655,404;
  structural 7,184 / 113,012; C8 63,526 / 1,208,473; C16 34,850 / 313,832; completions 0 / 0.
  If states/C8/C16 match but structural/attempted do not, that is reported as a proposal-enumeration convention
  difference, not hidden.
- P2: C8 and C16 filters off: connected linear v_3-configuration counts (nauty canonical, bipartition-preserving)
  for v = 7..13 must be 1, 1, 3, 10, 31, 229, 2,036.
- P3: C16 filter off, cap 19: completions must exist (19_3 configurations that are C4/C8-free). Their isomorphism-class
  count is reported beside the paper's "128" without preregistering equality.
Negative
- N1: C8 filter off (C16 on): completions must appear (e.g. Fano, v = 7).
- N2: the Fano plane / Heawood graph fed to the C8 test must be rejected (it has C8).
- N3: checker tamper tests must fail.

## Kill criterion (copied from parent)
Measure cap-30 and cap-31 growth factors. If the cap-34 projection exceeds 48 core-hours on 2 cores, report the largest
completed cap as a partial result. Orders <= 66 are not new as bounds (Ducoffe-Dumitru), only an independent
certificate-producing re-check of an uncertified SAT run. Only cap 34 (order 68) would be new.

## Tiers
- Tier C: exhaustive search + independent witness checker, for the configuration statement.
- Graph statement for 2v <= 60: Tier C + Moore lemma (proved in the text). For 62 <= 2v <= 68: additionally conditional on the Tier L premise n(3,10) = 70.

## Priors (copied)
prior 0.3 that order 68 is closed.
