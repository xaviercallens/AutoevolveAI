# LR-SPEC (Proposal 5, wave 2): counterexample search for the amended Lonely Runner Spectrum conjecture. Producer report, unaudited

**Outcome: PARTIAL (null box, Tier C). No counterexample.** The recomputation part of the box (8 speeds <= 60, 7 speeds <= 70) repeats Fan-Sun's own
published search; the part beyond the literature (7 speeds in (70,200], 8 speeds in (60,130]) is a null box. A null box proves nothing outside the box.
No "breakthrough", nothing is solved.

## Statement and sources (pinned)
Fan-Sun, Amending the Lonely Runner Spectrum Conjecture, Electron. J. Combin. 33(1) (2026) P1.38 (arXiv 2306.10417 v2). Conjecture 1.3: ML = s/(ns+k) with
1 <= k <= n, or ML >= 1/n. With ML = p/q in lowest terms and k' = q - np this is exactly "1 <= k' <= n" (PREREG_ITEM.md). Both the arXiv v2 and the EJC PDF
(sha256 de08d65c...06d9) were read; Table 1 is the same in both (n=7 up to speed 70, k in {1,2}; n=8 up to 60, k = 1). Cordella arXiv 2609.03444 v2 read.
Third-party copies are under /home/callensxavier_gmail_com/lrspec_thirdparty/, not in the repo.

## Novelty (same-day search 2026-10-31/11-01: alphaXiv, WebSearch)
No later search at 7/8 speeds, no refutation, no proof for n >= 5 found. The parent's "beyond Cordella's bounds" holds only against Cordella (7<=50, 8<=40). Against Fan-Sun's
Table 1: the 8-speed box <= 60 and 7 speeds <= 70 are recomputations. Beyond the literature: 7 speeds (70,200] and 8 speeds (60,130]. Fan-Sun's search has no published counts and
is uncertified, so ours are the first exact published counts at those bounds, and that is all they are.

## Controls (all run BEFORE the headline boxes; data/controls, logs/)
Positive (exact reproduction of Cordella's published numbers): P1 n=4 <= 200: 4125 primitive near-tight, 3836 k=1, 289 k=2, includes (1,3,4,14) ML 4/17. P2 n=6 <= 110: 348 (315 k=1, 33 k=3),
all of form (P-1)/(6P) with P = +-1 mod 6, max v/q = 105/43. P3 n=7 <= 50: 29 (26 k=1; k=2: (1,2,3,4,5,7,18) and (1,3,4,5,7,13,18) ML 3/23, (1,3,4,5,7,11,30) ML 5/37). P4 n=8 <= 40: 29, all k=1.
P5 Fan-Sun examples (7/30, 8/51, 3/23, 5/37 and the family (2s+7)/(8s+30), s=0..20): all exact.
Negative: N1 strictness corrupted (n*d > b): counts change (n4: 4125 -> 14197; n6<=60: 118 -> 908; n7<=50: 29 -> 382; n8<=40: 29 -> 394). N2 truncated candidates (m <= D/4): counts change (4143, 119, 39, 31).
N3 (see correction in ADDENDUM_1): 25 sampled tuples per box that only the corrupted scan adds all have ML exactly 1/n by the Fraction verifier; the true set is a subset of the corrupted set. V1: a tampered p/q is
flagged by verify.py (1 mismatch; also an assertion fires if k is inconsistent).
Other: C scan vs pure-Python brute force (no masks) identical on n=4<=30, 5<=24, 6<=20, 7<=18, 8<=16; two different witness lists (W4: B_W=40, W9: B_W=60) give byte-identical output on
n4<=200, n5<=100, n6<=110, n7<=60, n8<=45, and on the headline boxes 7<=80, 8<=60 and the ladder box 7<=120. Every box enumerates exactly C(N,n) tuples (checked). Every near-tight tuple found was
recomputed with Python Fractions (candidate set m/(vi+vj) plus single-speed peaks): 0 mismatches in every box.

## Results (primitive near-tight tuples = ML < 1/n, gcd 1; k' = q - np)
| n | speeds <= | tuples | near-tight | k counts | k > n | k > n/2 | core-s |
|---|---|---|---|---|---|---|---|
| 7 | 80 (primary) | 3.18e9 | 37 | 1:33, 2:4 | 0 | 0 | 14 |
| 8 | 60 (primary) | 2.56e9 | 36 | 1:36 | 0 | 0 | 13 |
| 7 | 100 | 1.60e10 | 40 | 1:36, 2:4 | 0 | 0 | 66 |
| 8 | 80 | 2.90e10 | 47 | 1:47 | 0 | 0 | 128 |
| 7 | 120 | 5.95e10 | 44 | 1:40, 2:4 | 0 | 0 | 243 |
| 8 | 100 | 1.86e11 | 53 | 1:53 | 0 | 0 | 831 |
| 7 | 150 | 2.94e11 | 48 | 1:44, 2:4 | 0 | 0 | 1225 |
| 7 | 180 | 1.08e12 | 52 | 1:48, 2:4 | 0 | 0 | 4054 |
| 8 | 130 | 1.62e12 | 65 | 1:65 | 0 | 0 | 8136 |
| 7 | 200 | 2.28e12 | 55 | 1:51, 2:4 | 0 | 0 | 8409 |
| 6 | 150 | 1.43e10 | 627 | 1:562, 3:65 | 0 | 0 | 53 |
| 6 | 200 | 8.24e10 | 1085 | 1:971, 3:114 | 0 | 0 | 301 |
(core-s = 2 x wall, an upper bound; total about 6.5 core-hours of boxes, far below the 60 core-hour cap.)

The four septuples with k = 2 are the same four in every box from <= 54 up to 200: (1,2,3,4,5,7,18) and (1,3,4,5,7,13,18) ML 3/23; (1,3,4,5,7,11,30) ML 5/37; (2,7,9,11,13,20,54) ML 9/65.
The last is not listed in Cordella or Fan-Sun (maximum speed 54 is inside Fan-Sun's <= 70 range, so they may have seen it). No tuple with k > n/2 (Fan-Sun Conjecture 6.1 / Remark 28 stays unrefuted in the boxes).
Secondary: for all 1085 sextuples <= 200, ML = (P-1)/(6P) with P = +-1 mod 6 and q odd (Cordella Conj 6.2 is the odd-denominator statement, k in {1,3}; our test is the stronger Theorem 6.1 form). Max v_max/q = 195/73 < 3
(Cordella Q6.6) attained on the family (6,31,37,68,99,105), (6,43,49,92,135,141), (6,61,67,128,189,195), which look like the extremal U_C family for which Cordella's Theorem 5.3 already proves v_max < 3q: this is consistent with a theorem and
is NOT new evidence about the sporadic tuples. For 7 and 8 speeds the max v_max/q is 13/5 at (1,4,5,6,7,11,39) and 21/17 at (1,5,6,7,8,11,13,21) (descriptive).

## Tiers
Tier C throughout (exhaustive enumeration with exact integer witnesses and a Fraction-recomputed ML for each reported tuple). No counterexample, so no Tier A / Lean artefact was due or produced.

## Deviations (all disclosed)
1. Hashed ADDENDUM_1 ladder 2 was only partly run: 8 <= 150 (about 3.7 h wall on 2 cores, ~25000 core-s, within the 60 core-h cap) was NOT run for session wall-clock reasons, which is not a stop rule in the addendum. Also 6-speed boxes ran before 8 <= 150 (order differs).
2. The W9 (second witness list) identity check promised for "the two largest boxes" was NOT done for 8 <= 130 and 7 <= 200; it was done on 7 <= 120 and the primary boxes only. Soundness does not depend on it (rejection = exact integer witness; survivors re-tested exactly), but the check is open.
3. Optional control (e): Cordella's survey.c was NOT run (the sandbox refused executing downloaded third-party code). Comparison with Cordella is through his published counts only.
4. PREREG_ITEM N3 wording error (tuples (1..n-1, ns) are near-tight), corrected in ADDENDUM_1 without editing PREREG_ITEM.
5. Cores: scans ran under taskset -c 6,7; short single-threaded verify.py / n3_p5.py / finalize.py runs were not all pinned (the first P1 verify was, others ran unpinned or on 6 or 7). Minor.
6. Parent's secondary "Conjecture 6.2 beyond speed 110" and "Q6.6" were done only to 200 and only as observations.

## What an independent auditor must redo
- Write an independent screen (different language/algorithm) and recompute the primary counts (37 septuples <= 80, 36 octuples <= 60) and their k distributions; ideally also 7 <= 200, 8 <= 130.
- Run Cordella's survey.c (Zenodo 10.5281/zenodo.22345079, MIT; archive sha256 c29542a2...3598 on disk) at 7 <= 50, 8 <= 40 and one larger box, and compare tuple sets.
- Re-verify exactly the four k=2 septuples (and e.g. (2,7,9,11,13,20,54) ML = 9/65).
- Run the W9 identity on 8 <= 130 and 7 <= 200, and 8 <= 150 if wanted.
- Check the completeness lemma (ML attained at t = m/(vi+vj), or peak 1/2) against Cordella Lemma 2.2.

## Files
PREREG_ITEM.md (+.sha256), PREREG_ADDENDUM_1.md (+.sha256), code/ (lrspec_scan.c and binaries, verify.py, brute.py, run_*.py, ladder2.py, finalize.py, n3_p5.py), data/ (controls, primary, ext, ext2, summary.json), logs/, result.json (sha256 of every file).
