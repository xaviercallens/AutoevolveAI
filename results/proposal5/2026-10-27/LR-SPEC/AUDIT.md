# LR-SPEC independent audit (auditor != producer), 2026-11-01

**Verdict: ACCEPT_WITH_CORRECTIONS.** Every headline count, k distribution and tuple set (including p, q, k) was reproduced exactly by an independent Rust screen that uses a strictly larger, complete candidate set. The four P-controls also match Cordella's own survey.c tuple for tuple. No tuple with k > n or k > n/2 occurs in any box. The corrections below are about wording and scope. No number changes. This is a null-box recomputation: Tier C, PARTIAL, not a proof of anything beyond the boxes.

Scratch: /tmp/lrspecaudit/ (not in the repo). Cores: taskset -c 6,7.

## 1. Definitions and completeness (read from the sources)
- ML(v) = max_t min_i ||t v_i|| (Fan-Sun arXiv 2306.10417 v2 p.1; Cordella arXiv 2609.03444 v2 §2.1).
- Near-tight: n distinct positive integers with ML < 1/n (Cordella §2.1, "k := q - np >= 1" with ML = p/q lowest terms).
- Conj 1.3 (Fan-Sun): ML = s/(ns+k), s,k in N, k <= n, or ML >= 1/n. With s = g p, ns+k = g q one gets k = g k', so Conj 1.3 <=> 1 <= k' <= n. Producer's equivalence is correct.
- Conj 6.1: same with k <= n/2.
- Completeness of the candidate set: Cordella Lemma 2.2 uses t = m/(v_i - e v_j), e = +-1 (sums AND differences). The producer (and Fan-Sun p.2) use sums only plus peaks. Sums suffice for positive speeds: at a maximiser t0 of f = min_i ||t v_i|| (f(t0) > 0) the right derivative of f is <= 0, so some active runner r has slope -v_r to the right (value b - t0 v_r, b in Z); the left derivative is >= 0, so some active runner s has slope +v_s to the left (value t0 v_s - a). If r != s then t0 = (a+b)/(v_r+v_s); if r = s then t0 v_r = 1/2 mod 1, f(t0) = 1/2, and then every active runner sits at 1/2 so t0 (v_i+v_j) in Z for any two of them, i.e. t0 is a sum time with m = D/2. Hence "scan m = 1..D/2 over D = v_i+v_j" (C) and "m/(v_i+v_j) plus peaks" (verify.py) are both exact. Symmetry t -> 1-t justifies m <= D/2.
- Note (correlated check): the producer's verify.py uses the same sums-only reduction as the C exact stage, so its "0 mismatches" cannot detect an error in that reduction. The auditor's own screen below uses the strictly larger set of all reduced a/b with b <= 2N (contains sums, differences and peaks).
- Scope: Conj 1.3 is stated for all positive integers. Restricting to distinct speeds is legitimate because a tuple with a repeated speed has at most n-1 distinct speeds and then ML >= 1/n by the Lonely Runner Conjecture for at most n-1 <= 7 speeds, i.e. at most 8 runners. That case is proved: classical results for up to 7 runners, Rosenfeld arXiv 2509.14111 for 8 runners. Restricting to primitive tuples is legitimate because ML is invariant under dividing by a common factor. RESULT.md does not state either reason (correction 4).

## 2. Auditor's own screen (Rust, /tmp/lrspecaudit/rs/src/main.rs; not derived from lrspec_scan.c)
- Witness set = EVERY reduced fraction a/b in (0,1/2] with b <= 2N (3903 fractions for N=80, 24339 for N=200). It contains every Lemma 2.2 time (sums, differences, peaks 2v_i), so "near-tight <=> AND of per-speed bitsets = 0" is exact with no second stage ("full" mode). A faster "pre" mode filters with the first 6 words (b up to about 50) and decides each survivor against the full fraction set. ML of each primitive near-tight tuple is the max over the full fraction set (exact u64 arithmetic). Parallelised over (v1,v2) work items with 2 threads, taskset -c 6,7.
- full mode and pre mode give byte-identical tuple sets on n4<=200, n6<=110, n7<=80, n8<=60.
- The tuple sets were compared exactly as lines "v1..vn p q k", not only as counts (/tmp/lrspecaudit/cmp.py). The k distributions were recounted from the raw data/*.txt files, not from summary.json.

| box | auditor (Rust) | producer data | identical (incl. p q k) |
|---|---|---|---|
| 4 <= 200 | 4125 (k1 3836, k2 289) | controls/P1 4125 | yes |
| 6 <= 110 | 348 (k1 315, k3 33) | controls/P2 348 | yes |
| 7 <= 50 | 29 (k1 26, k2 3) | controls/P3 29 | yes |
| 8 <= 40 | 29 (k1 29) | controls/P4 29 | yes |
| 7 <= 80 (primary) | 37 (k1 33, k2 4); 3,176,716,400 tuples; 119 near-tight incl. non-primitive | primary/n7_N80_W4 and W9: 37 | yes |
| 8 <= 60 (primary) | 36 (k1 36); 2,558,620,845 tuples | primary/n8_N60_W4 and W9: 36 | yes |
| 6 <= 200 (pre mode, 212 s wall) | 1085 (k1 971, k3 114); 82,408,626,300 tuples | ext2/n6_N200_W4: 1085 | yes; restriction to max <= 150 equals ext2/n6_N150 (627) |
| 7 <= 56 | 32 (k1 28, k2 4) | (Cordella survey.c, sec. 3) | yes |
| 8 <= 130 (pre mode, 4133 s wall, 2 threads) | 65 (k1 65); 1,624,177,854,000 tuples; 207 near-tight incl. non-primitive (producer logs: 86+121 = 207) | ext2/n8_N130_W4: 65 | yes |
| 7 <= 200 (pre mode, 5339 s wall, 2 threads) | 55 (k1 51, k2 4); 2,283,896,214,600 tuples; 341 near-tight incl. non-primitive (producer logs: 168+173 = 341) | ext2/n7_N200_W4: 55 | yes |
| sub-boxes obtained by restricting the two runs above to max speed <= N | 7<=80: 37, 7<=100: 40, 7<=120: 44, 7<=150: 48, 7<=180: 52; 8<=60: 36, 8<=80: 47, 8<=100: 53 | primary/, ext/, ext2/ | all identical |

The auditor's complete screen therefore covers every box in the results table. It replaces the producer's missing W9 identity check on 8<=130 and 7<=200 (Deviation 2) with a stronger check, one that does not depend on any witness list. The producer's own W9 binary was NOT rerun on those two boxes: about 3.7 h wall each, and it is superseded.

## 3. Cordella's own code (survey.c, MIT, archive sha256 c29542a2...3598)
- The archive was copied to /tmp/lrspecaudit/cordella and survey.c + lrk.h were reviewed before building: printf and OpenMP only, with no file, network or exec calls. Built with gcc -O2 -fopenmp and run with OMP_NUM_THREADS=2 under taskset -c 6,7. Unlike the producer's run, the sandbox did not refuse this one.
- survey 200 4: 4125 (3836/289; U1 50, U2 4075, none 1). survey 110 6: 348 (315/33). survey 50 7: 29 (26/3). survey 40 8: 29 (all k=1). Each tuple set (with p, q, k) is IDENTICAL to the producer's controls/P1..P4. So the controls now match Cordella's code exactly, not only his published counts.
- survey 56 7: 32 primitive near-tight (k1 28, k2 4) and includes "2 7 9 11 13 20 54 ML=9/65 k=2". The set is identical to the auditor's Rust 7<=56.

## 4. Exact checks (Fractions over the complete Lemma 2.2 set: sums, differences, peaks; /tmp/lrspecaudit/fracverify.py)
- (1,2,3,4,5,7,18): ML 3/23, k 2, optimal t = 4/23. (1,3,4,5,7,13,18): 3/23, k 2, t = 4/23. (1,3,4,5,7,11,30): 5/37, k 2, t = 6/37. (2,7,9,11,13,20,54): gcd 1, ML 9/65 < 1/7, k = 65-63 = 2, optimal t = 11/65 = 11/(11+54). Also Fan-Sun's examples: (8,3,11,19) gives 7/30 and (5,6,11,17,23,28) gives 8/51.
- Rows re-verified with the complete set: all 37 rows of 7<=80, all 36 of 8<=60, 40 random rows of each of 7<=200 (of 55), 8<=130 (of 65) and 6<=200 (of 1085). 0 mismatches.
- About (2,7,9,11,13,20,54) being "not listed": it is true that neither paper prints it. That fact carries no weight. The tuple lies outside Cordella's 7-speed box (max 54 > 50), and his own code finds it as soon as the box reaches 54. It lies inside Fan-Sun's searched range (<= 70), where they report k in {1,2} without listing tuples, so they very likely saw it. This is not a novelty claim (correction 1).
- Grep evidence: "9/65" and "20, 54" give 0 hits in the Cordella text, the Fan-Sun arXiv v2 text and the EJC text (out.txt). "9/65", "20 54" and "20, 54" give 0 hits in the unpacked Cordella archive (it ships no survey output files; uc_theorem_output.txt concerns U_C only).

## 5. Rebuilt producer scan and controls
- lrspec_scan.c was rebuilt from source in /tmp (-O2, -DNW=4 and -DNW=9) and rerun on 7<=80 and 8<=60 with the producer's arguments. The outputs are identical to data/primary and to the auditor's Rust (37 and 36). The diff was taken against the rebuilt binaries, not the shipped ones.
- Code review of lrspec_scan.c: a rejection uses an exact integer witness. The exact stage scans m = 1..D/2 over D = v_i+v_j, which is complete by section 1. The ML stage omits peaks, which is harmless for near-tight tuples. The counter gives tuples = C(N,n): checked from the logs for 7<=200 (2,283,896,214,600) and 8<=130 (1,624,177,854,000).
- Strictness corruption, auditor's own implementation (n*d > b): n4<=200 gives 14197, n6<=60 gives 908, n7<=50 gives 382, n8<=40 gives 394. These equal the producer's N1 counts exactly. Every added row has ML = p/q = 1/n exactly: 10072, 353, 365 and 790 added rows for n = 4, 7, 8, 6, each with p = 1 and q = n (checked by awk; 0 exceptions). The control discriminates. N2 (truncated m) is specific to the producer's code and was not re-implemented.
- Cost arithmetic: the core-s column sums to 23,473 core-s = 6.52 core-h. That covers boxes only (2 x wall, an upper bound) and excludes controls and verification. The unrun preregistered box 8<=150 has C(150,8) = 5.26e12 tuples, about 26,300 core-s at the producer's rate. The cumulative total would then have been about 13.8 core-h, far below the 60 core-h cap, so stopping there was a choice, not the stop rule. The producer disclosed this correctly (Deviation 1).
- Timing evidence (weak): file mtimes give PREREG_ITEM.md 23:16:30, lrspec_scan.c 23:17:02, binaries 23:17:09, first control output 23:17:25, ext_n7_N150.json 23:44:44, PREREG_ADDENDUM_1.md 23:45:02. The order is consistent with the claims. The header "written ~23:20" is a few minutes off the mtime. The whole directory arrived in one commit (bfa690b, 03:28), so the hashes prove content, not time.
- Minor: code/ladder2.py docstring says "8<=150 and 7<=200 not run", but 7<=200 was run (logs/ext2_n7_N200.json). The docstring is stale (correction 6).

- Secondary claims, recomputed from the AUDITOR's outputs:
  - All 1085 sextuples <= 200 have ML = (P-1)/(6P) with P = +-1 mod 6. All 1085 have odd q. 0 failures.
  - Max v_max/q: 195/73 for 6 speeds, attained only at (6,61,67,128,189,195). The other two family members give 105/43 and 141/55, the maxima of the <= 110 and <= 150 boxes. So "attained on the family" should read "attained at (6,61,67,128,189,195), a member of the family ..."; this is minor.
  - Max v_max/q is 13/5 at (1,4,5,6,7,11,39) for 7 speeds and 21/17 at (1,5,6,7,8,11,13,21) for 8 speeds.
  - U_C check by hand: B = 6 and A = 31, 43, 61 give {B, A, A+B, 2A+B, 3A+B, 3A+2B} = the three listed sextuples.
- Version note: the archive on disk, and the version the auditor ran, is v1.0.2 (doi 10.5281/zenodo.22345079). Cordella's paper cites v1.0.1 under the concept doi 22252166.

## 6. Novelty
- alphaXiv discovery (recency-ranked, 2026-11-01; queries "amended loneliness spectrum", "near-tight", "lonely runner spectrum", "Cordella") found nothing after Cordella 2609.03444 and Hu-Jing 2610.23790 that extends the 7/8-speed spectrum searches. The new LRC results (e.g. 14 and 15 runners, 2609.02604) do not concern the spectrum. The producer's novelty statement is accurate: 7<=70 and 8<=60 recompute Fan-Sun's Table 1 range, and only 7 in (70,200] and 8 in (60,130] go beyond it. These are null boxes, not evidence beyond the box.

## 7. Corrections (exact old -> new; apply to RESULT.md and, where noted, result.json)
1. RESULT.md, Results paragraph: "The last is not listed in Cordella or Fan-Sun (maximum speed 54 is inside Fan-Sun's <= 70 range, so they may have seen it)." -> "The last is printed in neither paper. It lies outside Cordella's 7-speed box (maximum speed 54 > 50), and Cordella's own survey.c finds it (ML = 9/65, k = 2) as soon as the box reaches 54 (auditor's run of survey 56 7). It lies inside Fan-Sun's searched range (<= 70), where they report k in {1,2} without listing tuples. It is not a new finding." (result.json does not contain this phrase.)
2. RESULT.md, Deviation 3 and "What an independent auditor must redo": add "Auditor (AUDIT.md section 3) built and ran Cordella's survey.c from a reviewed scratch copy: the tuple sets for 4<=200, 6<=110, 7<=50 and 8<=40 are identical to controls/P1-P4, including p, q, k."
3. RESULT.md, Deviation 2: append "Superseded by the auditor's independent complete screen: 8<=130 and 7<=200 tuple sets are identical (AUDIT.md section 2). The W9 run itself was not done."
4. RESULT.md, Statement section, after the equivalence sentence: add "Distinct speeds suffice because a tuple with a repeated speed has at most n-1 distinct speeds, and then ML >= 1/n by the Lonely Runner Conjecture (proved for these n). Primitive tuples suffice because ML is invariant under dividing by a common factor."
5. RESULT.md, under the table: "(core-s = 2 x wall, an upper bound; total about 6.5 core-hours of boxes, far below the 60 core-hour cap.)" -> "(core-s = 2 x wall, an upper bound; the boxes sum to 23,473 core-s = 6.5 core-h, excluding controls and verification. The unrun preregistered box 8 <= 150 would have added about 26,000 core-s, still far below the 60 core-hour cap.)"
6. code/ladder2.py docstring: "(8<=150 and 7<=200 not run: wall-clock)" -> "(8<=150 not run; 7<=200 was run separately, logs/ext2_n7_N200.json)".
7. RESULT.md, Controls: add "Note: verify.py uses the same sums-only candidate reduction as the C exact stage, so '0 mismatches' was a correlated check. The auditor's screen uses all fractions with denominator <= 2N (sums, differences and peaks) and agrees on every box."
8. PREREG_ITEM.md is hashed and must not be edited. In RESULT.md, add: "The PREREG_ITEM header says 'written ~23:20 UTC'. Its mtime is 23:16:30, before the scan binaries (23:17:09). The preregistration timing is self-attested: the directory arrived in one commit."

## 8. What remains unverified
- The producer's N2 (truncated-candidate) and N3 sampling controls were not re-implemented. They are specific to the producer's code, and the auditor's strictness control and complete screen cover the substance.
- The W9 run on 8<=130 and 7<=200 was not done (superseded, see section 2). 8<=150 was run by nobody.
- The float-grid check (d) was not repeated.
- The Fan-Sun search itself is unpublished code, so "they likely saw (2,7,9,11,13,20,54)" is an inference.
- Both screens enumerate only the stated boxes. Nothing is claimed about larger speeds. Conjecture 1.3 is neither proved nor refuted. These are null boxes from a partial recomputation, and no breakthrough is claimed.

Auditor scratch: /tmp/lrspecaudit/{rs (Rust source + outputs), survey (Cordella runs), prod (rebuilt producer), cmp.py, fracverify.py, fracverify.json}.

Hashes rechecked at audit end: preregistration.json 140a28ad...ae9be, PREREG_ITEM.md 7e62a74e...7ac7a6, PREREG_ADDENDUM_1.md b6d9ebf0...7669, all unchanged.
