# PH-2 RESULT: PARTIAL

Rigorous enclosure of Robertson's problem reached T = 40 (largest output time with relative width <= 1e-6 in every component: 40). Steps 15900, attempts 24487, driver CPU 0.036 core-hours (getrusage; controls extra, small, not metered). Finished flag: False; stopped: None; failed: None.

## Enclosure (y(t) in box; y1 = 1 - y2 - y3)

| t | y1 mid | y2 mid | y3 mid | rel.width y1 | rel.width y2 | rel.width y3 | abs.width y2 |
|---|---|---|---|---|---|---|---|
| 0.1 | 9.960777474424568e-01 | 3.580437235042240e-05 | 3.886448185192815e-03 | 1.28e-21 | 1.31e-17 | 2.06e-19 | 4.68e-22 |
| 0.4 | 9.851721138609899e-01 | 3.386395378974904e-05 | 1.479402218522039e-02 | 2.41e-21 | 2.64e-17 | 1.00e-19 | 8.93e-22 |
| 1 | 9.664597373330035e-01 | 3.074626578578674e-05 | 3.350951640121071e-02 | 9.56e-21 | 1.17e-16 | 1.68e-19 | 3.61e-21 |
| 4 | 9.055186785842539e-01 | 2.240475687560201e-05 | 9.445891665887049e-02 | 1.31e-19 | 2.30e-15 | 7.10e-19 | 5.16e-20 |
| 10 | 8.413699238414729e-01 | 1.623390937990472e-05 | 1.586138422491472e-01 | 8.19e-19 | 1.99e-14 | 2.31e-18 | 3.23e-19 |
| 40 | 7.158270687194050e-01 | 9.185534764557764e-06 | 2.841637457458304e-01 | 7.84e-18 | 3.02e-13 | 1.00e-17 | 2.77e-18 |

Exact midpoints/radii as rationals: enclosures.json.

## Solver comparison: rusty-SUNDIALS cvode crate (Rust port of CVODE; BDF/Newton/dense; analytic Jacobian), atol = 1e-3*rtol scalar

No LLNL C CVODE exists on this host; nothing here is a statement about the C library. Error interval = |y_solver - y| using the enclosure; ratio = error / (rtol|y|+atol), shown as [lo,hi].

| rtol | atol | t | comp | err in | ratio in | provably > tol | provably <= tol |
|---|---|---|---|---|---|---|---|
| 0.0001 | 1.0e-07 | 0.1 | y1 | [2.24e-07, 2.24e-07] | [2.25e-03, 2.25e-03] | False | True |
| 0.0001 | 1.0e-07 | 0.1 | y2 | [7.54e-10, 7.54e-10] | [7.28e-03, 7.28e-03] | False | True |
| 0.0001 | 1.0e-07 | 0.1 | y3 | [2.24e-07, 2.24e-07] | [4.58e-01, 4.58e-01] | False | True |
| 1e-06 | 1.0e-09 | 0.1 | y1 | [2.17e-09, 2.17e-09] | [2.18e-03, 2.18e-03] | False | True |
| 1e-06 | 1.0e-09 | 0.1 | y2 | [1.06e-13, 1.06e-13] | [1.02e-04, 1.02e-04] | False | True |
| 1e-06 | 1.0e-09 | 0.1 | y3 | [2.17e-09, 2.17e-09] | [4.44e-01, 4.44e-01] | False | True |
| 1e-08 | 1.0e-11 | 0.1 | y1 | [5.64e-11, 5.64e-11] | [5.65e-03, 5.65e-03] | False | True |
| 1e-08 | 1.0e-11 | 0.1 | y2 | [1.59e-14, 1.59e-14] | [1.54e-03, 1.54e-03] | False | True |
| 1e-08 | 1.0e-11 | 0.1 | y3 | [5.59e-11, 5.59e-11] | [1.14e+00, 1.14e+00] | True | False |
| 1e-10 | 1.0e-10 | 0.1 | y1 | [1.92e-10, 1.92e-10] | [9.60e-01, 9.60e-01] | False | True |
| 1e-10 | 1.0e-10 | 0.1 | y2 | [3.41e-14, 3.41e-14] | [3.41e-04, 3.41e-04] | False | True |
| 1e-10 | 1.0e-10 | 0.1 | y3 | [1.89e-10, 1.89e-10] | [1.88e+00, 1.88e+00] | True | False |
| 0.0001 | 1.0e-07 | 0.4 | y1 | [3.21e-06, 3.21e-06] | [3.25e-02, 3.25e-02] | False | True |
| 0.0001 | 1.0e-07 | 0.4 | y2 | [5.69e-10, 5.69e-10] | [5.51e-03, 5.51e-03] | False | True |
| 0.0001 | 1.0e-07 | 0.4 | y3 | [3.21e-06, 3.21e-06] | [2.03e+00, 2.03e+00] | True | False |
| 1e-06 | 1.0e-09 | 0.4 | y1 | [5.11e-08, 5.11e-08] | [5.18e-02, 5.18e-02] | False | True |
| 1e-06 | 1.0e-09 | 0.4 | y2 | [1.00e-11, 1.00e-11] | [9.70e-03, 9.70e-03] | False | True |
| 1e-06 | 1.0e-09 | 0.4 | y3 | [5.11e-08, 5.11e-08] | [3.24e+00, 3.24e+00] | True | False |
| 1e-08 | 1.0e-11 | 0.4 | y1 | [1.47e-09, 1.47e-09] | [1.49e-01, 1.49e-01] | False | True |
| 1e-08 | 1.0e-11 | 0.4 | y2 | [2.76e-13, 2.76e-13] | [2.67e-02, 2.67e-02] | False | True |
| 1e-08 | 1.0e-11 | 0.4 | y3 | [1.47e-09, 1.47e-09] | [9.29e+00, 9.29e+00] | True | False |
| 1e-10 | 1.0e-10 | 0.4 | y1 | [6.76e-10, 6.76e-10] | [3.41e+00, 3.41e+00] | True | False |
| 1e-10 | 1.0e-10 | 0.4 | y2 | [1.27e-13, 1.27e-13] | [1.27e-03, 1.27e-03] | False | True |
| 1e-10 | 1.0e-10 | 0.4 | y3 | [6.74e-10, 6.74e-10] | [6.64e+00, 6.64e+00] | True | False |
| 0.0001 | 1.0e-07 | 1 | y1 | [3.32e-06, 3.32e-06] | [3.43e-02, 3.43e-02] | False | True |
| 0.0001 | 1.0e-07 | 1 | y2 | [5.42e-10, 5.42e-10] | [5.26e-03, 5.26e-03] | False | True |
| 0.0001 | 1.0e-07 | 1 | y3 | [3.32e-06, 3.32e-06] | [9.62e-01, 9.62e-01] | False | True |
| 1e-06 | 1.0e-09 | 1 | y1 | [1.78e-07, 1.78e-07] | [1.84e-01, 1.84e-01] | False | True |
| 1e-06 | 1.0e-09 | 1 | y2 | [2.59e-11, 2.59e-11] | [2.51e-02, 2.51e-02] | False | True |
| 1e-06 | 1.0e-09 | 1 | y3 | [1.78e-07, 1.78e-07] | [5.17e+00, 5.17e+00] | True | False |
| 1e-08 | 1.0e-11 | 1 | y1 | [2.13e-09, 2.13e-09] | [2.20e-01, 2.20e-01] | False | True |
| 1e-08 | 1.0e-11 | 1 | y2 | [3.35e-13, 3.35e-13] | [3.25e-02, 3.25e-02] | False | True |
| 1e-08 | 1.0e-11 | 1 | y3 | [2.13e-09, 2.13e-09] | [6.17e+00, 6.17e+00] | True | False |
| 1e-10 | 1.0e-10 | 1 | y1 | [1.24e-09, 1.24e-09] | [6.30e+00, 6.30e+00] | True | False |
| 1e-10 | 1.0e-10 | 1 | y2 | [2.06e-13, 2.06e-13] | [2.06e-03, 2.06e-03] | False | True |
| 1e-10 | 1.0e-10 | 1 | y3 | [1.24e-09, 1.24e-09] | [1.20e+01, 1.20e+01] | True | False |
| 0.0001 | 1.0e-07 | 4 | y1 | [6.04e-06, 6.04e-06] | [6.66e-02, 6.66e-02] | False | True |
| 0.0001 | 1.0e-07 | 4 | y2 | [7.02e-10, 7.02e-10] | [6.87e-03, 6.87e-03] | False | True |
| 0.0001 | 1.0e-07 | 4 | y3 | [6.04e-06, 6.04e-06] | [6.33e-01, 6.33e-01] | False | True |
| 1e-06 | 1.0e-09 | 4 | y1 | [2.37e-07, 2.37e-07] | [2.61e-01, 2.61e-01] | False | True |
| 1e-06 | 1.0e-09 | 4 | y2 | [2.88e-11, 2.88e-11] | [2.82e-02, 2.82e-02] | False | True |
| 1e-06 | 1.0e-09 | 4 | y3 | [2.37e-07, 2.37e-07] | [2.48e+00, 2.48e+00] | True | False |
| 1e-08 | 1.0e-11 | 4 | y1 | [7.34e-09, 7.34e-09] | [8.10e-01, 8.10e-01] | False | True |
| 1e-08 | 1.0e-11 | 4 | y2 | [8.09e-13, 8.09e-13] | [7.91e-02, 7.91e-02] | False | True |
| 1e-08 | 1.0e-11 | 4 | y3 | [7.34e-09, 7.34e-09] | [7.69e+00, 7.69e+00] | True | False |
| 1e-10 | 1.0e-10 | 4 | y1 | [2.11e-09, 2.11e-09] | [1.11e+01, 1.11e+01] | True | False |
| 1e-10 | 1.0e-10 | 4 | y2 | [2.51e-13, 2.51e-13] | [2.51e-03, 2.51e-03] | False | True |
| 1e-10 | 1.0e-10 | 4 | y3 | [2.11e-09, 2.11e-09] | [1.93e+01, 1.93e+01] | True | False |
| 0.0001 | 1.0e-07 | 10 | y1 | [1.47e-05, 1.47e-05] | [1.74e-01, 1.74e-01] | False | True |
| 0.0001 | 1.0e-07 | 10 | y2 | [1.33e-09, 1.33e-09] | [1.31e-02, 1.31e-02] | False | True |
| 0.0001 | 1.0e-07 | 10 | y3 | [1.47e-05, 1.47e-05] | [9.18e-01, 9.18e-01] | False | True |
| 1e-06 | 1.0e-09 | 10 | y1 | [8.31e-07, 8.31e-07] | [9.87e-01, 9.87e-01] | False | True |
| 1e-06 | 1.0e-09 | 10 | y2 | [4.30e-11, 4.30e-11] | [4.23e-02, 4.23e-02] | False | True |
| 1e-06 | 1.0e-09 | 10 | y3 | [8.31e-07, 8.31e-07] | [5.21e+00, 5.21e+00] | True | False |
| 1e-08 | 1.0e-11 | 10 | y1 | [2.06e-08, 2.06e-08] | [2.44e+00, 2.44e+00] | True | False |
| 1e-08 | 1.0e-11 | 10 | y2 | [1.56e-12, 1.56e-12] | [1.53e-01, 1.53e-01] | False | True |
| 1e-08 | 1.0e-11 | 10 | y3 | [2.06e-08, 2.06e-08] | [1.29e+01, 1.29e+01] | True | False |
| 1e-10 | 1.0e-10 | 10 | y1 | [2.42e-09, 2.42e-09] | [1.32e+01, 1.32e+01] | True | False |
| 1e-10 | 1.0e-10 | 10 | y2 | [1.91e-13, 1.91e-13] | [1.91e-03, 1.91e-03] | False | True |
| 1e-10 | 1.0e-10 | 10 | y3 | [2.42e-09, 2.42e-09] | [2.09e+01, 2.09e+01] | True | False |
| 0.0001 | 1.0e-07 | 40 | y1 | [3.46e-05, 3.46e-05] | [4.82e-01, 4.82e-01] | False | True |
| 0.0001 | 1.0e-07 | 40 | y2 | [1.45e-09, 1.45e-09] | [1.44e-02, 1.44e-02] | False | True |
| 0.0001 | 1.0e-07 | 40 | y3 | [3.46e-05, 3.46e-05] | [1.21e+00, 1.21e+00] | True | False |
| 1e-06 | 1.0e-09 | 40 | y1 | [2.32e-06, 2.32e-06] | [3.23e+00, 3.23e+00] | True | False |
| 1e-06 | 1.0e-09 | 40 | y2 | [9.10e-11, 9.10e-11] | [9.02e-02, 9.02e-02] | False | True |
| 1e-06 | 1.0e-09 | 40 | y3 | [2.32e-06, 2.32e-06] | [8.12e+00, 8.12e+00] | True | False |
| 1e-08 | 1.0e-11 | 40 | y1 | [3.92e-08, 3.92e-08] | [5.46e+00, 5.46e+00] | True | False |
| 1e-08 | 1.0e-11 | 40 | y2 | [1.56e-12, 1.56e-12] | [1.55e-01, 1.55e-01] | False | True |
| 1e-08 | 1.0e-11 | 40 | y3 | [3.92e-08, 3.92e-08] | [1.37e+01, 1.37e+01] | True | False |
| 1e-10 | 1.0e-10 | 40 | y1 | [2.92e-09, 2.92e-09] | [1.70e+01, 1.70e+01] | True | False |
| 1e-10 | 1.0e-10 | 40 | y2 | [1.16e-13, 1.16e-13] | [1.16e-03, 1.16e-03] | False | True |
| 1e-10 | 1.0e-10 | 40 | y3 | [2.92e-09, 2.92e-09] | [2.27e+01, 2.27e+01] | True | False |

Solver error lines in the raw log (rtol=1e-10, atol=1e-13, the preregistered setting, failed at the first output time with no output; an extra NON-preregistered run with atol=1e-10 was added): ['ERROR FAIL 3: local error test failed > max times']

First output time per rtol/component with a provable tolerance violation:
- rtol 1e-10 atol 1.0e-10 y1: 0.4
- rtol 1e-10 atol 1.0e-10 y2: none among the reached output times
- rtol 1e-10 atol 1.0e-10 y3: 0.1
- rtol 1e-08 atol 1.0e-11 y1: 10.0
- rtol 1e-08 atol 1.0e-11 y2: none among the reached output times
- rtol 1e-08 atol 1.0e-11 y3: 0.1
- rtol 1e-06 atol 1.0e-09 y1: 40.0
- rtol 1e-06 atol 1.0e-09 y2: none among the reached output times
- rtol 1e-06 atol 1.0e-09 y3: 0.4
- rtol 0.0001 atol 1.0e-07 y1: none among the reached output times
- rtol 0.0001 atol 1.0e-07 y2: none among the reached output times
- rtol 0.0001 atol 1.0e-07 y3: 0.4

Solver outputs available per rtol (12 requested each): {0.0001: 12, 1e-06: 12, 1e-08: 12, 1e-10: 12}. Missing rtol/time = the solver returned an error (see logs/cvode_err.txt: e.g. ErrTestFailure); it is reported as such, not retried.

## Secondary literature values (recalled from the SUNDIALS cvRoberts_dns example printout, 5 digits, NOT fetched or verified here)

- t=0.4 y1: literature 9.85170e-01 vs enclosure mid 9.85172e-01, relative difference 2.1e-06 (rounding of the 5-digit print is about 5e-6 relative)
- t=0.4 y2: literature 3.38640e-05 vs enclosure mid 3.38640e-05, relative difference 1.4e-06 (rounding of the 5-digit print is about 5e-6 relative)
- t=0.4 y3: literature 1.47940e-02 vs enclosure mid 1.47940e-02, relative difference 1.5e-06 (rounding of the 5-digit print is about 5e-6 relative)
- t=4 y1: literature 9.05510e-01 vs enclosure mid 9.05519e-01, relative difference 9.6e-06 (rounding of the 5-digit print is about 5e-6 relative)
- t=4 y2: literature 2.24060e-05 vs enclosure mid 2.24048e-05, relative difference 5.5e-05 (rounding of the 5-digit print is about 5e-6 relative)
- t=4 y3: literature 9.44590e-02 vs enclosure mid 9.44589e-02, relative difference 8.8e-07 (rounding of the 5-digit print is about 5e-6 relative)
- t=40 y1: literature 7.15830e-01 vs enclosure mid 7.15827e-01, relative difference 4.1e-06 (rounding of the 5-digit print is about 5e-6 relative)
- t=40 y2: literature 9.18560e-06 vs enclosure mid 9.18553e-06, relative difference 7.1e-06 (rounding of the 5-digit print is about 5e-6 relative)
- t=40 y3: literature 2.84160e-01 vs enclosure mid 2.84164e-01, relative difference 1.3e-05 (rounding of the 5-digit print is about 5e-6 relative)

## Controls (code/controls.py, logs/controls.json)

- lin_p24_intact: steps 9961; t=0.1: contained [True, True], rel.width [9.816496342077915e-22, 34740123.974972844], x(1+1e-6) disjoint [True, False]; t=1: contained [True, True], rel.width [1.7123660867718856e-20, 334603320.11393404], x(1+1e-6) disjoint [True, False]; t=10: contained [True, True], rel.width [2.2150379062505902e-16, 555213.4235362752], x(1+1e-6) disjoint [True, False]
- log_p24_intact: steps 68; t=1: contained [True, True], rel.width [6.791459515785733e-22, 1.1640794517790372e-21], x(1+1e-6) disjoint [True, True]; t=5: contained [True, True], rel.width [2.042140169639968e-22, 4.240936227717779e-18], x(1+1e-6) disjoint [True, True]; t=10: contained [True, True], rel.width [4.124961212331221e-24, 2.0004702217704396e-15], x(1+1e-6) disjoint [True, True]
- lin_p6_intact: steps 28870; t=0.1: contained [True, True], rel.width [5.980299147023776e-05, 904991.3969013809], x(1+1e-6) disjoint [False, False]; t=1: contained [True, True], rel.width [0.0010077010766601842, 1025012.7605412557], x(1+1e-6) disjoint [False, False]; t=10: contained [True, True], rel.width [12.995098155643873, 20980.44116598106], x(1+1e-6) disjoint [False, False]
- log_p6_intact: steps 94; t=1: contained [True, True], rel.width [7.676111717357906e-06, 1.3157123905539664e-05], x(1+1e-6) disjoint [False, False]; t=5: contained [True, True], rel.width [2.226450668847112e-06, 0.046242703307896656], x(1+1e-6) disjoint [False, False]; t=10: contained [True, True], rel.width [1.7775266591468427e-07, 86.62621721235736], x(1+1e-6) disjoint [True, False]
- lin_p6_broken: steps 28667; t=0.1: contained [False, False]; t=1: contained [False, False]; t=10: contained [False, False]
- log_p6_broken: steps 84; t=1: contained [False, False]; t=5: contained [False, False]; t=10: contained [False, False]

## Method and proof obligations (mapping to code/ph2_enclose.py)
Reduction: (a,b)=(y2,y3), y1 = 1 - a - b (conservation, exact in balls). Region of the vector field: all of R^2 (no positivity used; quasi-positivity / simplex invariance is NOT needed because the tube argument O4 is self-contained. The prereg listed O1 as a region restriction; it was not used.)
- O2 defect: `attempt`: coefficients D_k of f(q(t)) - q'(t) (k=0..2p-2) by exact ball Cauchy products from the dyadic coefficients of q (`Fk`, `taylor_q`); dbar = sum_k ||P^-1 D_k||_2 h^k >= sup_{[0,h]} ||P^-1 D(t)||_2 (triangle inequality).
- O3 one-sided Lipschitz: `attempt`: U = hull_t q([0,h]) + row-norm(P)*rho box (superset of every point on a segment between z(t) and q(t)); `Quad.jac_ball` interval Jacobian (affine in y, exact enclosure of J over U); S = sym(P^-1 J P); nu = upper bound of lambda_max(S) by the closed 2x2 formula in balls (monotone, so the ball evaluation bounds all matrices in the set). Lemma: <e, P^-T P^-1 (f(z)-f(q))> <= nu |e|_P^2 for z,q with segment in U.
- O4 bootstrap: `attempt`: rho = 8(eps0 + dbar h); require (eps0+dbar h) exp(max(nu,0) h) < rho strictly (checked with .upper()/.lower()), so the exact solution cannot leave the rho-tube on [0,h]; global existence on the step follows (it stays in a compact set). Then eps_end = eps0 e^{nu h} + dbar int_0^h e^{nu s} ds (ball).
- O5 jump: m' = mid(q(h)); jump = q(h) - m' as a ball, added in the next norm (`attempt`, eps0).
- O6 basis change: factor sigma_max(P_{k+1}^-1 P_k) by the exact 2x2 singular-value formula in balls (`attempt`).
- P exact balls from floats (`choose_basis`), P^-1 by ball adjugate (`inv2`; rejects det containing 0).
- O7 output: |e_i| <= ||row_i P||_2 eps (Cauchy-Schwarz); box = q(h) +/- that, `attempt`. Output times are hit exactly by truncating the last step (`run`); h as exact rational in a ball H.
- Initial value exact: eps_0 = 0.
Floats: only h choice, eigenvector choice for P, display.

## Unproved assumptions / what an auditor must check
1. Arb ball arithmetic (Sage 9.5 RealBall) is rigorous; no independent second implementation or second precision was run (producer != verifier NOT satisfied; prereg mentioned it).
2. The lemma in O3/O4 (log-norm comparison, first-exit argument) is argued here, not formalized in Lean.
3. Boundary subtleties of ball comparisons: rsqrt/sq helpers clip lower ends at 0 (valid because the quantities are mathematically >= 0); auditors should read them.
4. The solver comparison uses exact doubles of the Rust solver's printed shortest round-trip floats and exactly representable output times (0.1 and 0.4 are the doubles passed to the solver). The Rust right-hand side uses fl(0.04) != 1/25 and fl(1e4*y...) roundings: that is the solver's own arithmetic, counted as solver error.
5. CVODE (Rust port) is not LLNL CVODE; the port's behavior says nothing about the C library.
6. Literature numbers are recalled, not retrieved.
7. Step history: code/ph2_enclose.py stores [t,h,nu,eps_end] every 20 steps in logs/enclosure_ckpt.json (res.history).

## Step history (every 20th step: t, h, nu, eps_end)

- t=2.01471e-05 h=7.556e-06 nu=9.906e+00 eps=1.326e-53
- t=2.53704 h=5.558e-03 nu=7.727e-01 eps=1.207e-20
- t=5.27194 h=4.722e-03 nu=3.556e-01 eps=5.167e-20
- t=7.95012 h=5.582e-03 nu=3.078e-01 eps=1.131e-19
- t=10.426 h=3.577e-03 nu=1.264e-01 eps=1.859e-19
- t=12.8803 h=4.584e-03 nu=1.494e-01 eps=2.696e-19
- t=15.2605 h=2.709e-03 nu=5.330e-02 eps=3.585e-19
- t=17.5637 h=3.640e-03 nu=7.837e-02 eps=4.494e-19
- t=19.809 h=3.645e-03 nu=6.985e-02 eps=5.416e-19
- t=22.0039 h=2.757e-03 nu=3.852e-02 eps=6.331e-19
- t=24.1566 h=2.428e-03 nu=2.685e-02 eps=7.247e-19
- t=26.2643 h=4.176e-03 nu=6.558e-02 eps=8.151e-19
- t=28.3423 h=4.821e-03 nu=7.493e-02 eps=9.046e-19
- t=30.377 h=4.246e-03 nu=5.841e-02 eps=9.922e-19
- t=32.3884 h=3.651e-03 nu=4.356e-02 eps=1.079e-18
- t=34.3716 h=3.216e-03 nu=3.328e-02 eps=1.164e-18
- t=36.3276 h=2.212e-03 nu=1.439e-02 eps=1.248e-18
- t=38.2585 h=4.430e-03 nu=4.982e-02 eps=1.330e-18
- t=40.1129 h=2.271e-03 nu=1.399e-02 eps=1.408e-18
- t=42.004 h=1.953e-03 nu=8.653e-03 eps=1.488e-18
- t=43.8767 h=1.720e-03 nu=4.971e-03 eps=1.566e-18
- t=45.7307 h=2.132e-03 nu=1.043e-02 eps=1.642e-18
- t=47.5688 h=2.642e-03 nu=1.680e-02 eps=1.717e-18
- t=49.3914 h=2.499e-03 nu=1.438e-02 eps=1.791e-18
- t=51.1954 h=2.478e-03 nu=1.363e-02 eps=1.863e-18
- t=52.9893 h=2.182e-03 nu=9.665e-03 eps=1.935e-18

## CPU ledger
Driver CPU 130.5 s (checkpoint field cpu_s; cumulative across restarts). Rusty-SUNDIALS runs: a few seconds. Controls: not metered (minutes).
