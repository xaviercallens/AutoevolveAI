# PH-2 RESULT: PARTIAL

Rigorous enclosure of Robertson's problem reached T = 4000 (largest output time with relative width <= 1e-6 in every component: 4000). Steps 2850083, attempts 4389852, driver CPU 8.306 core-hours (getrusage; controls extra, small, not metered). Finished flag: False; stopped: cpu_cap (cumulative 29900 s, main-session cap; the checkpoint omits the flag because of a bookkeeping order bug in run(), ph2_enclose.py:342-343: res["stopped"] is set after save(). The code was left unchanged so that it matches the code that produced the run); failed: None.

## Enclosure (y(t) in box; y1 = 1 - y2 - y3)

| t | y1 mid | y2 mid | y3 mid | rel.width y1 | rel.width y2 | rel.width y3 | abs.width y2 |
|---|---|---|---|---|---|---|---|
| 0.1 | 9.960777474424568e-01 | 3.580437235042240e-05 | 3.886448185192815e-03 | 1.28e-21 | 1.31e-17 | 2.06e-19 | 4.68e-22 |
| 0.4 | 9.851721138609899e-01 | 3.386395378974904e-05 | 1.479402218522039e-02 | 2.41e-21 | 2.64e-17 | 1.00e-19 | 8.93e-22 |
| 1 | 9.664597373330035e-01 | 3.074626578578674e-05 | 3.350951640121071e-02 | 9.56e-21 | 1.17e-16 | 1.68e-19 | 3.61e-21 |
| 4 | 9.055186785842539e-01 | 2.240475687560201e-05 | 9.445891665887049e-02 | 1.31e-19 | 2.30e-15 | 7.10e-19 | 5.16e-20 |
| 10 | 8.413699238414729e-01 | 1.623390937990472e-05 | 1.586138422491472e-01 | 8.19e-19 | 1.99e-14 | 2.31e-18 | 3.23e-19 |
| 40 | 7.158270687194050e-01 | 9.185534764557764e-06 | 2.841637457458304e-01 | 7.84e-18 | 3.02e-13 | 1.00e-17 | 2.77e-18 |
| 100 | 6.172348823960877e-01 | 6.153591274639123e-06 | 3.827589640126376e-01 | 2.31e-17 | 1.16e-12 | 1.87e-17 | 7.11e-18 |
| 400 | 4.505186684711024e-01 | 3.222901441674611e-06 | 5.494781086274559e-01 | 7.52e-17 | 5.25e-12 | 3.08e-17 | 1.69e-17 |
| 1000 | 3.368745306607069e-01 | 2.013702318261393e-06 | 6.631234556369748e-01 | 9.41e-16 | 7.87e-11 | 2.39e-16 | 1.58e-16 |
| 4000 | 1.832022577767093e-01 | 8.942371252775910e-07 | 8.167968479861654e-01 | 5.84e-15 | 5.99e-10 | 6.55e-16 | 5.35e-16 |

Exact midpoints/radii as rationals: enclosures.json.

## Solver comparison: rusty-SUNDIALS cvode crate (Rust port of CVODE; BDF/Newton/dense; analytic Jacobian), atol = 1e-3*rtol scalar for rtol 1e-4, 1e-6, 1e-8; rtol 1e-10 rows use atol = 1e-10 (NON-preregistered: the preregistered atol 1e-13 run failed with ErrTestFailure and produced no output)

No LLNL C CVODE exists on this host; nothing here is a statement about the C library. Error interval = |y_solver - y| using the enclosure; ratio = error / (rtol|y|+atol), shown as [lo,hi]. NOTE: 'provably > tol' compares the GLOBAL error with the per-component tolerance scale; CVODE controls a local error estimate, so this is not a breach of the solver's contract.

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
| 0.0001 | 1.0e-07 | 100 | y1 | [7.03e-05, 7.03e-05] | [1.14e+00, 1.14e+00] | True | False |
| 0.0001 | 1.0e-07 | 100 | y2 | [1.88e-09, 1.88e-09] | [1.87e-02, 1.87e-02] | False | True |
| 0.0001 | 1.0e-07 | 100 | y3 | [7.03e-05, 7.03e-05] | [1.83e+00, 1.83e+00] | True | False |
| 1e-06 | 1.0e-09 | 100 | y1 | [2.20e-06, 2.20e-06] | [3.56e+00, 3.56e+00] | True | False |
| 1e-06 | 1.0e-09 | 100 | y2 | [5.36e-11, 5.36e-11] | [5.33e-02, 5.33e-02] | False | True |
| 1e-06 | 1.0e-09 | 100 | y3 | [2.20e-06, 2.20e-06] | [5.73e+00, 5.73e+00] | True | False |
| 1e-08 | 1.0e-11 | 100 | y1 | [3.43e-08, 3.43e-08] | [5.55e+00, 5.55e+00] | True | False |
| 1e-08 | 1.0e-11 | 100 | y2 | [8.32e-13, 8.32e-13] | [8.27e-02, 8.27e-02] | False | True |
| 1e-08 | 1.0e-11 | 100 | y3 | [3.43e-08, 3.43e-08] | [8.94e+00, 8.94e+00] | True | False |
| 1e-10 | 1.0e-10 | 100 | y1 | [2.76e-09, 2.76e-09] | [1.71e+01, 1.71e+01] | True | False |
| 1e-10 | 1.0e-10 | 100 | y2 | [6.79e-14, 6.79e-14] | [6.79e-04, 6.79e-04] | False | True |
| 1e-10 | 1.0e-10 | 100 | y3 | [2.76e-09, 2.76e-09] | [2.00e+01, 2.00e+01] | True | False |
| 0.0001 | 1.0e-07 | 400 | y1 | [2.46e-05, 2.46e-05] | [5.46e-01, 5.46e-01] | False | True |
| 0.0001 | 1.0e-07 | 400 | y2 | [3.13e-10, 3.13e-10] | [3.12e-03, 3.12e-03] | False | True |
| 0.0001 | 1.0e-07 | 400 | y3 | [2.46e-05, 2.46e-05] | [4.48e-01, 4.48e-01] | False | True |
| 1e-06 | 1.0e-09 | 400 | y1 | [2.76e-06, 2.76e-06] | [6.12e+00, 6.12e+00] | True | False |
| 1e-06 | 1.0e-09 | 400 | y2 | [3.51e-11, 3.51e-11] | [3.50e-02, 3.50e-02] | False | True |
| 1e-06 | 1.0e-09 | 400 | y3 | [2.76e-06, 2.76e-06] | [5.02e+00, 5.02e+00] | True | False |
| 1e-08 | 1.0e-11 | 400 | y1 | [3.92e-08, 3.92e-08] | [8.68e+00, 8.68e+00] | True | False |
| 1e-08 | 1.0e-11 | 400 | y2 | [4.98e-13, 4.98e-13] | [4.96e-02, 4.96e-02] | False | True |
| 1e-08 | 1.0e-11 | 400 | y3 | [3.92e-08, 3.92e-08] | [7.12e+00, 7.12e+00] | True | False |
| 1e-10 | 1.0e-10 | 400 | y1 | [2.13e-09, 2.13e-09] | [1.47e+01, 1.47e+01] | True | False |
| 1e-10 | 1.0e-10 | 400 | y2 | [2.70e-14, 2.70e-14] | [2.70e-04, 2.70e-04] | False | True |
| 1e-10 | 1.0e-10 | 400 | y3 | [2.13e-09, 2.13e-09] | [1.37e+01, 1.37e+01] | True | False |
| 0.0001 | 1.0e-07 | 1000 | y1 | [9.12e-05, 9.12e-05] | [2.70e+00, 2.70e+00] | True | False |
| 0.0001 | 1.0e-07 | 1000 | y2 | [8.35e-10, 8.35e-10] | [8.33e-03, 8.33e-03] | False | True |
| 0.0001 | 1.0e-07 | 1000 | y3 | [9.12e-05, 9.12e-05] | [1.37e+00, 1.37e+00] | True | False |
| 1e-06 | 1.0e-09 | 1000 | y1 | [1.60e-06, 1.60e-06] | [4.73e+00, 4.73e+00] | True | False |
| 1e-06 | 1.0e-09 | 1000 | y2 | [1.42e-11, 1.42e-11] | [1.42e-02, 1.42e-02] | False | True |
| 1e-06 | 1.0e-09 | 1000 | y3 | [1.60e-06, 1.60e-06] | [2.41e+00, 2.41e+00] | True | False |
| 1e-08 | 1.0e-11 | 1000 | y1 | [4.22e-08, 4.22e-08] | [1.25e+01, 1.25e+01] | True | False |
| 1e-08 | 1.0e-11 | 1000 | y2 | [3.76e-13, 3.76e-13] | [3.75e-02, 3.75e-02] | False | True |
| 1e-08 | 1.0e-11 | 1000 | y3 | [4.22e-08, 4.22e-08] | [6.35e+00, 6.35e+00] | True | False |
| 1e-10 | 1.0e-10 | 1000 | y1 | [1.99e-09, 1.99e-09] | [1.49e+01, 1.49e+01] | True | False |
| 1e-10 | 1.0e-10 | 1000 | y2 | [1.77e-14, 1.78e-14] | [1.77e-04, 1.78e-04] | False | True |
| 1e-10 | 1.0e-10 | 1000 | y3 | [1.99e-09, 1.99e-09] | [1.20e+01, 1.20e+01] | True | False |
| 0.0001 | 1.0e-07 | 4000 | y1 | [2.71e-05, 2.71e-05] | [1.47e+00, 1.47e+00] | True | False |
| 0.0001 | 1.0e-07 | 4000 | y2 | [5.62e-11, 5.62e-11] | [5.61e-04, 5.61e-04] | False | True |
| 0.0001 | 1.0e-07 | 4000 | y3 | [2.71e-05, 2.71e-05] | [3.31e-01, 3.31e-01] | False | True |
| 1e-06 | 1.0e-09 | 4000 | y1 | [1.48e-06, 1.48e-06] | [8.05e+00, 8.05e+00] | True | False |
| 1e-06 | 1.0e-09 | 4000 | y2 | [8.83e-12, 8.83e-12] | [8.82e-03, 8.82e-03] | False | True |
| 1e-06 | 1.0e-09 | 4000 | y3 | [1.48e-06, 1.48e-06] | [1.81e+00, 1.81e+00] | True | False |
| 1e-08 | 1.0e-11 | 4000 | y1 | [3.04e-08, 3.04e-08] | [1.65e+01, 1.65e+01] | True | False |
| 1e-08 | 1.0e-11 | 4000 | y2 | [1.81e-13, 1.81e-13] | [1.81e-02, 1.81e-02] | False | True |
| 1e-08 | 1.0e-11 | 4000 | y3 | [3.04e-08, 3.04e-08] | [3.72e+00, 3.72e+00] | True | False |
| 1e-10 | 1.0e-10 | 4000 | y1 | [2.49e-09, 2.49e-09] | [2.11e+01, 2.11e+01] | True | False |
| 1e-10 | 1.0e-10 | 4000 | y2 | [1.46e-14, 1.51e-14] | [1.46e-04, 1.51e-04] | False | True |
| 1e-10 | 1.0e-10 | 4000 | y3 | [2.49e-09, 2.49e-09] | [1.37e+01, 1.37e+01] | True | False |

Solver error lines in the raw log (rtol=1e-10, atol=1e-13, the preregistered setting, failed at the first output time with no output; an extra NON-preregistered run with atol=1e-10 was added): ['ERROR FAIL 3: local error test failed > max times']

First output time per rtol/component with a provable tolerance violation:
- rtol 1e-10 atol 1.0e-10 y1: 0.4
- rtol 1e-10 atol 1.0e-10 y2: none, because the tolerance for y2 is atol-dominated (y2 <= 3.6e-5); relative to rtol*|y2| alone the error exceeds rtol by up to 169x (1e-10), 20x (1e-8), 11x (1e-6), 4.1x (1e-4)
- rtol 1e-10 atol 1.0e-10 y3: 0.1
- rtol 1e-08 atol 1.0e-11 y1: 10.0
- rtol 1e-08 atol 1.0e-11 y2: none, because the tolerance for y2 is atol-dominated (y2 <= 3.6e-5); relative to rtol*|y2| alone the error exceeds rtol by up to 169x (1e-10), 20x (1e-8), 11x (1e-6), 4.1x (1e-4)
- rtol 1e-08 atol 1.0e-11 y3: 0.1
- rtol 1e-06 atol 1.0e-09 y1: 40.0
- rtol 1e-06 atol 1.0e-09 y2: none, because the tolerance for y2 is atol-dominated (y2 <= 3.6e-5); relative to rtol*|y2| alone the error exceeds rtol by up to 169x (1e-10), 20x (1e-8), 11x (1e-6), 4.1x (1e-4)
- rtol 1e-06 atol 1.0e-09 y3: 0.4
- rtol 0.0001 atol 1.0e-07 y1: 100.0
- rtol 0.0001 atol 1.0e-07 y2: none, because the tolerance for y2 is atol-dominated (y2 <= 3.6e-5); relative to rtol*|y2| alone the error exceeds rtol by up to 169x (1e-10), 20x (1e-8), 11x (1e-6), 4.1x (1e-4)
- rtol 0.0001 atol 1.0e-07 y3: 0.4

Solver outputs available per rtol (12 requested each): {0.0001: 12, 1e-06: 12, 1e-08: 12, 1e-10: 12} (the 1e-10 count is the non-preregistered atol=1e-10 run; the preregistered 1e-10/1e-13 run gave 0 outputs). Only 10 of the 12 times have an enclosure. Missing rtol/time = the solver returned an error (see logs/cvode_err.txt: e.g. ErrTestFailure); it is reported as such, not retried.

## Secondary values: SUNDIALS cvRoberts_dns printout (solver output at rtol=1e-4, NOT the true solution; recalled, not fetched)

- t=0.4 y1: literature 9.85170e-01 vs enclosure mid 9.85172e-01, relative difference 2.1e-06 (differences are consistent with rtol=1e-4 solver error)
- t=0.4 y2: literature 3.38640e-05 vs enclosure mid 3.38640e-05, relative difference 1.4e-06 (differences are consistent with rtol=1e-4 solver error)
- t=0.4 y3: literature 1.47940e-02 vs enclosure mid 1.47940e-02, relative difference 1.5e-06 (differences are consistent with rtol=1e-4 solver error)
- t=4 y1: literature 9.05510e-01 vs enclosure mid 9.05519e-01, relative difference 9.6e-06 (differences are consistent with rtol=1e-4 solver error)
- t=4 y2: literature 2.24060e-05 vs enclosure mid 2.24048e-05, relative difference 5.5e-05 (differences are consistent with rtol=1e-4 solver error)
- t=4 y3: literature 9.44590e-02 vs enclosure mid 9.44589e-02, relative difference 8.8e-07 (differences are consistent with rtol=1e-4 solver error)
- t=40 y1: literature 7.15830e-01 vs enclosure mid 7.15827e-01, relative difference 4.1e-06 (differences are consistent with rtol=1e-4 solver error)
- t=40 y2: literature 9.18560e-06 vs enclosure mid 9.18553e-06, relative difference 7.1e-06 (differences are consistent with rtol=1e-4 solver error)
- t=40 y3: literature 2.84160e-01 vs enclosure mid 2.84164e-01, relative difference 1.3e-05 (differences are consistent with rtol=1e-4 solver error)

## Controls (code/controls.py, logs/controls.json)

- lin_p24_intact: steps 9961; t=0.1: contained [True, True], rel.width [9.816496342077915e-22, 34740123.974972844], x(1+1e-6) disjoint [True, False]; t=1: contained [True, True], rel.width [1.7123660867718856e-20, 334603320.11393404], x(1+1e-6) disjoint [True, False]; t=10: contained [True, True], rel.width [2.2150379062505902e-16, 555213.4235362752], x(1+1e-6) disjoint [True, False]
- log_p24_intact: steps 68; t=1: contained [True, True], rel.width [6.791459515785733e-22, 1.1640794517790372e-21], x(1+1e-6) disjoint [True, True]; t=5: contained [True, True], rel.width [2.042140169639968e-22, 4.240936227717779e-18], x(1+1e-6) disjoint [True, True]; t=10: contained [True, True], rel.width [4.124961212331221e-24, 2.0004702217704396e-15], x(1+1e-6) disjoint [True, True]
- lin_p6_intact: steps 28870; t=0.1: contained [True, True], rel.width [5.980299147023776e-05, 904991.3969013809], x(1+1e-6) disjoint [False, False]; t=1: contained [True, True], rel.width [0.0010077010766601842, 1025012.7605412557], x(1+1e-6) disjoint [False, False]; t=10: contained [True, True], rel.width [12.995098155643873, 20980.44116598106], x(1+1e-6) disjoint [False, False]
- log_p6_intact: steps 94; t=1: contained [True, True], rel.width [7.676111717357906e-06, 1.3157123905539664e-05], x(1+1e-6) disjoint [False, False]; t=5: contained [True, True], rel.width [2.226450668847112e-06, 0.046242703307896656], x(1+1e-6) disjoint [False, False]; t=10: contained [True, True], rel.width [1.7775266591468427e-07, 86.62621721235736], x(1+1e-6) disjoint [True, False]
- lin_p6_broken: steps 28667; t=0.1: contained [False, False]; t=1: contained [False, False]; t=10: contained [False, False]
- log_p6_broken: steps 84; t=1: contained [False, False]; t=5: contained [False, False]; t=10: contained [False, False]

C-1 has no power for lin y2 (y2 = e^{-1e4 t}, relative width >= 2e4): never rejected; this is adjudicated as a powerless test, not a soundness failure (AUDIT.md section 4). The controls in logs/controls.json were run on a pre-final ph2_enclose.py; the auditor's rerun on the final code gives the same verdicts.

## Method and proof obligations (mapping to code/ph2_enclose.py)
Reduction: (a,b)=(y2,y3), y1 = 1 - a - b (conservation, exact in balls). Region of the vector field: all of R^2 (no positivity used; quasi-positivity / simplex invariance is NOT needed because the tube argument O4 is self-contained. The prereg listed O1 as a region restriction; it was not used.)
- O2 defect: `attempt`: coefficients D_k of f(q(t)) - q'(t) (k=0..2p-2) by exact ball Cauchy products from the dyadic coefficients of q (`Fk`, `taylor_q`); dbar = sum_k ||P^-1 D_k||_2 h^k >= sup_{[0,h]} ||P^-1 D(t)||_2 (triangle inequality).
- O3 one-sided Lipschitz: `attempt`: U = hull_t q([0,h]) + row-norm(P)*rho box (superset of every point on a segment between z(t) and q(t)); `Quad.jac_ball` interval Jacobian (affine in y, exact enclosure of J over U); S = sym(P^-1 J P); nu = upper bound of lambda_max(S) by the closed 2x2 formula in balls (monotone, so the ball evaluation bounds all matrices in the set). Lemma: <e, P^-T P^-1 (f(z)-f(q))> <= nu |e|_P^2 for z,q with segment in U.
- O4 bootstrap: `attempt`: rho = 8(eps0 + dbar h); require (eps0+dbar h) exp(max(nu,0) h) < rho strictly (checked with .upper()/.lower()), so the exact solution cannot leave the rho-tube on [0,h]; global existence on the step follows (it stays in a compact set). Then eps_end = eps0 e^{nu h} + dbar int_0^h e^{nu s} ds (ball).
- O5 jump: m' = mid(q(h)); jump = q(h) - m' as a ball, added in the next norm (`attempt`, eps0).
- O6 basis change: factor sigma_max(P_{k+1}^-1 P_k) by the exact 2x2 singular-value formula in balls (`attempt`). Correction (audit): O6 uses the exact 2x2 spectral norm (prereg: Frobenius); tighter and valid.
- P exact balls from floats (`choose_basis`), P^-1 by ball adjugate (`inv2`; rejects det containing 0).
- O7 output: |e_i| <= ||row_i P||_2 eps (Cauchy-Schwarz); box = q(h) +/- that, `attempt`. Output times are hit exactly by truncating the last step (`run`); h as exact rational in a ball H.
- Initial value exact: eps_0 = 0.
Floats: only h choice, eigenvector choice for P, display.

## Unproved assumptions / what an auditor must check
1. Arb ball arithmetic (Sage 9.5 RealBall) is rigorous; independent MPFI/Lohner integrator by the auditor (AUDIT.md section 3) confirms t=1, 10 and 40 (the t=40 run finished after the first audit text; AUDIT.md Addendum); t>40 is single-implementation. Independent check exists for t <= 40.
2. The lemma in O3/O4 (log-norm comparison, first-exit argument) is argued here, not formalized in Lean.
3. Boundary subtleties of ball comparisons: rsqrt/sq helpers clip lower ends at 0 (valid because the quantities are mathematically >= 0); auditors should read them.
4. The solver comparison uses exact doubles of the Rust solver's printed shortest round-trip floats and exactly representable output times (0.1 and 0.4 are the doubles passed to the solver). The Rust right-hand side uses fl(0.04) != 1/25 and fl(1e4*y...) roundings: that is the solver's own arithmetic, counted as solver error.
5. CVODE (Rust port) is not LLNL CVODE; the port's behavior says nothing about the C library.
6. Literature numbers are recalled, not retrieved.
7. Step history: code/ph2_enclose.py stores [t,h,nu,eps_end] every 20 steps in logs/enclosure_ckpt.json (res.history).

## Step history (a subsample of the every-20th-step history)

- t=2.01471e-05 h=7.556e-06 nu=9.906e+00 eps=1.326e-53
- t=267.89 h=1.897e-03 nu=1.203e-03 eps=7.002e-18
- t=473.687 h=2.224e-03 nu=1.040e-03 eps=9.057e-18
- t=662.522 h=1.936e-03 nu=3.744e-04 eps=1.066e-17
- t=841.664 h=2.127e-03 nu=3.884e-04 eps=6.318e-17
- t=1014.23 h=1.832e-03 nu=9.303e-05 eps=7.961e-17
- t=1181.88 h=2.110e-03 nu=1.967e-04 eps=9.374e-17
- t=1345.73 h=1.078e-03 nu=-3.304e-04 eps=1.239e-16
- t=1506.47 h=9.460e-04 nu=-3.655e-04 eps=1.309e-16
- t=1664.63 h=1.817e-03 nu=-2.943e-05 eps=1.447e-16
- t=1820.5 h=1.748e-03 nu=-6.476e-05 eps=1.798e-16
- t=1974.48 h=1.804e-03 nu=-5.629e-05 eps=2.042e-16
- t=2126.75 h=1.368e-03 nu=-1.824e-04 eps=2.752e-16
- t=2277.53 h=1.705e-03 nu=-9.505e-05 eps=2.932e-16
- t=2426.94 h=9.532e-04 nu=-2.724e-04 eps=2.943e-16
- t=2575.12 h=1.107e-03 nu=-2.299e-04 eps=2.927e-16
- t=2722.19 h=1.068e-03 nu=-2.311e-04 eps=2.902e-16
- t=2868.24 h=1.543e-03 nu=-1.349e-04 eps=2.872e-16
- t=3013.36 h=1.367e-03 nu=-1.655e-04 eps=2.839e-16
- t=3157.59 h=1.411e-03 nu=-1.556e-04 eps=2.810e-16
- t=3301.03 h=1.100e-03 nu=-2.028e-04 eps=2.842e-16
- t=3443.72 h=1.509e-03 nu=-1.367e-04 eps=2.811e-16
- t=3585.71 h=1.276e-03 nu=-1.688e-04 eps=2.778e-16
- t=3727.03 h=1.063e-03 nu=-1.949e-04 eps=2.744e-16
- t=3867.74 h=1.714e-03 nu=-1.064e-04 eps=2.709e-16
- t=4007.84 h=9.685e-04 nu=-1.987e-04 eps=2.675e-16

## Preregistration anchoring caveat
PREREG_ITEM.md was first git-committed 2026-11-13 (00328e1), after the launch; the freeze rests on file mtimes and a self-hash.

## Audit status
Independently audited once by an AI agent (AUDIT.md, ACCEPT_WITH_CORRECTIONS); the eleven corrections of AUDIT.md section 8 are applied to this file (correction 8 per the Addendum). No human audit.

## CPU ledger
Driver CPU 29900.0 s (checkpoint field cpu_s; cumulative across restarts). Rusty-SUNDIALS runs: a few seconds. Controls: not metered (minutes).
