# LR-SPEC item-level preregistration (written 2026-10-31 ~23:20 UTC, before any search binary was built or run)

Parent preregistration: `results/proposal5/2026-10-27/preregistration.json`
(sha256 140a28adfc1932e5330d650ffe43a43d9c8e417d9b38cbbdd7f03174a55ae9be, not edited), item LR-SPEC, wave 2.
This file only makes the parent's LR-SPEC entry operational; where they differ the parent wins.

## Statement under test and pinned source (the parent's "must be pinned" condition is now met)
Fan and Sun, "Amending the Lonely Runner Spectrum Conjecture", arXiv 2306.10417 v2 (30 Jan 2026), full text read
(copy under /home/callensxavier_gmail_com/lrspec_thirdparty/, not in the repo).
- Conjecture 1.3 (Amended Loneliness Spectrum): for positive integers v_1..v_n, either ML = s/(ns+k) for some s,k in N with k <= n,
  or ML >= 1/n.
- Equivalence with the parent's convention: write ML = p/q in lowest terms, k' = q - np. s/(ns+k) = p/q with s = gp, ns+k = gq gives
  k = g*k' >= k', so the existence of a representation with k <= n is equivalent to 1 <= k' <= n. (k' >= 1 is automatic when ML < 1/n.)
  So the parent's statement (k = q - np > n is a counterexample) is exactly Conjecture 1.3.
- Fan-Sun Conjecture 6.1 (stronger): k <= n/2. Not the target, but a tuple with n/2 < k' <= n would refute 6.1, not 1.3. Reported as a by-product.
- Fan-Sun Table 1 (their own computer search, "max value of speeds"): n=7 up to 70 (k in {1,2}), n=8 up to 60 (k in {1}); they call
  n=7,8 "unconvincing due to the low search bounds".
- Cordella arXiv 2609.03444 v2 read (searches: 7 speeds <= 50, 8 <= 40, 6 <= 110).

## Same-day literature / novelty re-search (2026-10-31, before the first run)
- alphaXiv discover_papers (3 queries, recency-weighted): newest relevant items are Cordella 2609.03444 (2026-09-03) and Hu-Jing 2610.23790
  (2026-10-16, a uniform ML > (1+c)/2n bound, not about the spectrum). No later search at 7 or 8 speeds, no refutation, no proof of Conj 1.3 for n >= 5 found.
- NOVELTY FINDING (stated now): the parent's 8-speed box (<= 60) and its 7-speed box up to 70 are NOT beyond Fan-Sun's published Table 1.
  The parent's claim "beyond Cordella's bounds" is true only relative to Cordella (7<=50, 8<=40). What is new relative to the literature:
  7 speeds in (70, 80] and every extension box below; the 8<=60 box is a recomputation (independent re-run) of Fan-Sun's.
  Their search is not certified and has no published counts, so our counts are the first exact published counts at those bounds, but that is
  all they are: Tier C, not a new theorem.

## Method (fixed before running)
Exact integer arithmetic throughout. Near-tight = ML < 1/n.
1. Candidate times: ML is attained at t = m/(v_i+v_j) (crossing of a rising and a falling branch); the single-peak case gives ML = 1/2. Verifier
   (Python, Fractions) uses the full candidate set m/(v_i+v_j), m = 0..v_i+v_j-1, i<j, plus peaks (2m+1)/(2 v_i).
2. Fast C screen (`lrspec_scan.c`): depth-first enumeration of all increasing n-tuples in [1..N]; each speed v has a bitmask over a fixed witness
   list W of reduced fractions a/b in (0,1/2], b <= B_W: bit set iff n*dist(a*v mod b, 0) >= b (i.e. ||t v|| >= 1/n, exact integers). A tuple is
   REJECTED (not near-tight) if the AND of its masks is nonzero (a valid exact witness). Soundness of rejection needs only the integer test.
   Survivors go to an exact stage: scan all pairs and m for a non-near-tight witness; if none, the tuple is near-tight; if gcd = 1 its ML is computed
   exactly (64-bit cross multiplication of integer fractions) and k' = q - np recorded.
3. Independent checks: (a) Python verifier recomputes ML with Fractions over the full candidate set for EVERY near-tight tuple found and compares p/q;
   (b) the whole scan is run twice with two different witness lists (B_W = 40 and B_W = 60, different mask width) and must give identical
   near-tight sets; (c) pure-Python brute force (no masks) on small boxes (n=4 <= 40, n=5 <= 30, n=6 <= 24, n=7 <= 22) equals the C counts;
   (d) a float grid scan (not a proof) of random tuples agrees with the exact ML to 1e-9; (e) Cordella's MIT code (Zenodo 10.5281/zenodo.22252166) is
   used for a cross-check only if downloadable; it would sit under lrspec_thirdparty, and its absence is reported, not hidden.
4. Cores: taskset -c 6,7 only.

## Controls (all run and reported BEFORE any headline number)
Positive
- P1: 4 speeds <= 200: Cordella reports 4125 primitive near-tight (3836 with k=1, 289 with k=2; 50 on U1, exactly one off both critical subtori:
  (1,3,4,14) with ML 4/17). We must reproduce 4125 / 3836 / 289 and the tuple (1,3,4,14).
- P2: 6 speeds <= 110: 348 primitive near-tight; 315 with k=1, 33 with k=3; all with ML=(P-1)/(6P), P = +-1 mod 6; largest v_max/q = 105/43.
- P3: 7 speeds <= 50: 29 primitive near-tight, 26 with k=1 and 3 with k=2: (1,2,3,4,5,7,18) and (1,3,4,5,7,13,18) with ML=3/23, (1,3,4,5,7,11,30) with ML=5/37.
- P4: 8 speeds <= 40: 29 primitive near-tight, all k=1.
- P5: Fan-Sun's examples ML(8,3,11,19)=7/30, ML(5,6,11,17,23,28)=8/51, ML(1,3,4,5,7,13,18)=3/23, and the family ML(8,4s+3,4s+11,4s+19)=(2s+7)/(8s+30) for s=0..20.
Negative
- N1: strictness corruption: replacing the exact test n*d >= b by n*d > b in the witness bits (and in the exact stage) must change the near-tight
  counts (tuples with ML exactly 1/n become wrongly "near-tight"); the changed counts are reported next to the true ones.
- N2: using only candidates m < D/2 (or deleting the smallest-denominator candidates) in the exact stage must be detected on P1/P3 by a changed count.
- N3: tuples with ML exactly 1/n ((1,2,...,n-1, n*s) family, s=1..5) must NOT be counted near-tight, and must be counted when strictness is corrupted.
If any P-control fails to reproduce exactly, it is reported as a deviation/convention difference with the numbers, and no headline claim is made until it is resolved.

## Boxes and kill criterion
- Primary box (parent): 7 speeds <= 80 and 8 speeds <= 60. Speeds distinct, subsets of {1..N}; primitive (gcd 1) tuples reported; dilations are not counted.
- Extension ladder (labelled EXTENSION, only after the primary box and all controls, in this order, each only while the cumulative projected
  core-hours stay <= 60 at the throughput measured on the primary box): 7 <= 100, 8 <= 80, 7 <= 120, 8 <= 100, 7 <= 150.
- Secondary (descriptive, by-products of the same kernel): 6 speeds <= 130 (and <= 150 if cheap): test whether every near-tight sextuple has
  ML=(P-1)/(6P), P = +-1 mod 6 (Cordella Conj 6.2 form) and record max v_max/q (Cordella Q6.6: < 3?). Also v_max/q for 7 and 8 speeds. Boxes above
  Cordella's are Tier C observations only.
- Kill / stop: the parent's: box (7 <= 80, 8 <= 60) or 60 core-hours, whichever first, plus the explicit extension ladder above within 60 core-hours total.
  Outcome rules: any primitive near-tight tuple with k' > n (verified by the Fraction verifier and by an independent second integer check) = candidate
  counterexample, Tier A only after a Lean `decide` certificate through scripts/certified_numerics/lean_pinned.py; otherwise a null box (Tier C, PARTIAL/null).
  A null box proves nothing beyond the box. No Lean is planned unless a counterexample appears.
- Prior 0.1 (parent). Expected outcome: null box.

## Not claimed
No proof of Conjecture 1.3; no statement about tuples outside the boxes; no breakthrough; a null box is not evidence beyond the box.
