# GR-11 RESULT: PARTIAL (null on the pinned subset; most of the list not run)

Item preregistration: PREREG_ITEM.md (sha256 5a02b566...c3d85), written before any run; addendum 2 for n=11 (PREREG_ITEM_addendum2.md, sha256 3fd041d3...b10b) written before the n=11 run. Parent preregistration untouched.

## UPDATE 2026-11-01: n=11 completed (supersedes the "n=11 NOT run" statements below)
- All 40 parts of `nauty-geng -c 11 r/40` finished; counts sum to exactly 1,006,700,565 (data/n11_aggregate.json). Cost 12.48 core-hours (limit 20), cores 4,5 only.
- Graffiti 20 and 21: 0 violations among all 1,006,700,565 connected graphs on 11 vertices (threshold 1e-6). Together with n<=10: 1,018,690,325 connected graphs on <=11 vertices, 0 violations (Tier X scan).
- Graphs with margin below 1e-6: exactly one, K_11 (g6 J~~~~~~~~~_), conjecture 21 equality S+ = 10 = n_neg. Decided exactly (data/n11_exact_check.jsonl): characteristic polynomial over Z, Descartes' rule (real-rooted) gives n_pos=1, n_neg=10, S+ enclosed as exactly 10: both HOLD, 21 with equality. Equals the hand-proved K_n tie. No near-ties other than K_11. Smallest margin otherwise: conj 20 min gap 0.828, (conj 21 non-K_n margins at n=11 are >= the 1e-6 flag threshold, none flagged).
- Controls at n=11: Graffiti 29 positive control fires on 1862 graphs (total over n<=11 consistent: first at n=7); negative controls lambda1 >= avg degree and sum|lambda| >= n_pos+n_neg fire 0 times.
- Caveat: floats (Tier X) for the screening of 1.0e9 graphs; only graphs with margin <1e-6 were exact-checked, so a float misclassification with margin >1e-6 is excluded only by the eigenvalue accuracy (~1e-13). Eigenvalue zero threshold 1e-9. Scope still only conjectures 20, 21 (and control 29); the other open conjectures remain BLOCKED (definitions not pinned) or claimed solved elsewhere.
- Auditor: rerun a few parts independently (e.g. `scan.py 11 7 40 flagged.txt`), re-derive the part-count sum, and re-run exact_check.py on data/flagged_n11_*.txt.
- Outcome label unchanged: PARTIAL (null for 20/21 on all connected graphs with <=11 vertices; ~20 other conjectures not run).


## Novelty / literature (same day, 2026-10-31)
- AutoGraphForge (arXiv 2609.03478) read: census only to 9 vertices, no Written-on-the-Wall spectral conjectures. No pre-emption of the n=11 niche.
- Roucairol-Cazenave 2409.18626 read in full; it does not state the open conjectures, and it documents definition errors (range, harmonic, gravity).
- Unverified third-party 2026-10 claims (GitHub issues/repos, AI-generated, not peer reviewed) that 198, 219, 252, 254, 262, 322, 712, 714 and 290, 292, 295 are already resolved (proofs / Lean / a 1024-vertex counterexample for 322). Not checked by me. For those the item is at best a recomputation, so they were not run. Nothing found for 20, 21, 39, 40, 129, 143, 154, 195, 284, 698.
- Primary source Written on the Wall (July 2004) obtained (sha256 d2c779d2...f7733, kept outside the repo in gr11_thirdparty/wow). It is a scanned bitmap without text layer and no OCR is available; each statement had to be read by eye. Within the time available only conjectures 20, 21 (p.19) and the control 29 (p.23) were pinned; 39/40 need the glossary definition of "deviation", the others need gravity/temperature/derivative definitions: BLOCKED (kill criterion: definitions not pinned).

## What was run (Tier X, floats)
- Graffiti 20: number of positive adjacency eigenvalues <= sum of positive eigenvalues. Graffiti 21: number of negative eigenvalues <= sum of positive eigenvalues.
- All connected graphs, nauty-geng -c, n = 4..10: 6, 21, 112, 853, 11117, 261080, 11716571 graphs (all match the known counts), total 11,989,760. n=11 (1,006,700,565 graphs) NOT run: measured throughput 23k graphs/s/core implies ~12 core-hours (6 h wall on cores 4,5), inside the 20 core-hour kill limit but beyond what this session waited for. Command: `geng -c 11 r/m` through code/scan.py in parts.
- Result: 0 violations for 20 and 21 at every n <= 10 (threshold 1e-6). Min margins: conj 20 min gap 0.236 (n=4); conj 21 attains equality exactly on K_n (S+ = n-1 = n_neg, integer, one tie per n, exact by hand), otherwise a clear gap (next smallest 0.22 at n=10, part 0).
- Known easy reasons they are plausible: |sum| of eigenvalues >= rank (WoW comment on conj 20), so 20/21 hold for rank-like graphs; no proof is claimed.

## Controls
- Positive: Graffiti 29 (Randic index <= number of negative DISTANCE eigenvalues, WoW p.23): no counterexample for n<=6, exactly 1 at n=7 (graph6 FEhf?), matching Roucairol-Cazenave "7+". Further counts 1,23,18 at n=8,9,10. The first version of the code decoded graph6 in the wrong bit order and mis-read 29 as using adjacency eigenvalues; both bugs were caught by this control and fixed before any reported number.
- Negative: lambda_1 >= average degree and sum|lambda| >= n_pos+n_neg: 0 firings over all 11,989,760 graphs.
- Graffiti 711/166 controls from the parent plan not run (statements not pinned).

## Outcome
PARTIAL / null: no refutation of Graffiti 20 or 21 among connected graphs with <= 10 vertices (Tier X; exhaustive over n<=10, floats only). It is a small recomputation-type negative: it does not answer the GR-11 question for n=11, nor for the other ~20 conjectures. Not a result about all graphs.

## Auditor must redo
1. Pin the statements and glossary definitions of 39, 40, 129, 143, 154, 195, 284, 698 (and any of the claimed-solved ones) from the scanned WoW PDF (or Larson's text).
2. Run n=11 (1,006,700,565 graphs) in parts, ideally with exact/interval check of near-ties.
3. Re-verify graph counts and the 29 control; check third-party solved-claims independently.
4. Exact (not float) check of 20/21 near-equality graphs; only K_n appears as tie here.

Files: code/scan.py, code/finalize.py, logs/scan_n*.json, result.json (sha256 of every file).
