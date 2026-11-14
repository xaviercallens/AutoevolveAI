# LR-SPEC addendum 1 (written 2026-10-31 after the controls and the primary box and the ladder up to 8 <= 100 had run, BEFORE any box beyond them)

Why: measured throughput is about 2.2e8 tuples per core-second, so the preregistered ladder (7 <= 100, 8 <= 80, 7 <= 120, 8 <= 100, 7 <= 150) costs
well under 1 core-hour in total, far below the parent's 60 core-hour cap. The parent's stop rule is "box or 60 core-hours, whichever first"; this addendum
adds an explicit second ladder inside the same 60 core-hour cap. It changes no control, no tier rule, no outcome rule of PREREG_ITEM.md
(sha256 7e62a74ef97226582536c895c4ddb6fec3ab7f875617a1bae5b7af90192ac7a6).

Status at the time of writing (facts, not predictions): all controls P1-P5, N1-N3, brute force, two-witness-list identity passed; primary box 7 <= 80
(37 primitive near-tight, k in {1,2}) and 8 <= 60 (36, all k = 1) found no tuple with k > n; 7 <= 100 (40), 8 <= 80 (47), 7 <= 120 (44), 8 <= 100 (53)
also none; 7 <= 150 (48 primitive near-tight, 1225 core-s) had finished a few seconds before this file was written (log timestamp 23:44:44, this file 23:44:54);
no k > n there either, to be confirmed by the Fraction verifier below.

Ladder 2 (EXTENSION-2, in this order, each run only while the cumulative core-seconds, measured, stay below 60 core-hours = 216000 core-s):
 1. 8 speeds <= 130
 2. 7 speeds <= 180
 3. 8 speeds <= 150
 4. 6 speeds <= 150 and 6 <= 200 (secondary: Cordella Conj 6.2 odd-denominator form, Question 6.6 ratio)
 5. 7 speeds <= 200
Every box: the same C scan, the same Fraction verifier on every near-tight tuple found, the same sums-of-tuples check (number of tuples enumerated must equal
C(N,n)), and for the two largest boxes also the second witness list (W9) with identical output. Any k > n is a candidate counterexample (outcome rule unchanged).
Boxes not reached before the cap are reported as not run.

Correction to PREREG_ITEM.md, noted here and not edited there: control N3 wrote "(1,2,...,n-1,n*s) have ML exactly 1/n". That is wrong, those tuples have
ML = s/(ns+1) < 1/n and are near-tight (k = 1). N3 was run as: the tuples that only the strictness-corrupted scan adds are sampled and their ML is checked
by the Fraction verifier to be exactly 1/n (so they are correctly absent from the true scan). The intent (ML exactly 1/n is not near-tight) is unchanged.
Also: the optional control (e) (run Cordella's MIT survey.c) was NOT run: the sandbox refused executing downloaded third-party code. The archive is on disk under
lrspec_thirdparty/cordella_code (sha256 c29542a2284e26f04c32e61e6f5d4196777883b08c2df92251fcac1874f03598); the comparison with Cordella is only through his published counts.
