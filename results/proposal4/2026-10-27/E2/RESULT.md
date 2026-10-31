# E2: certified surface-saturation time in the single-particle model (SPM), Chen2020 parameters

Outcome: **PARTIAL** (producer, unaudited). Enclosures and all preregistered controls pass; the SPM versus PyBaMM check passes; the SPMe/DFN comparison is incomplete (DFN does not integrate for C >= 3, and for C = 2 only up to the local-saturation crossing); no Lean (declared in the preregistration), so nothing is Tier A.
Preregistration: `prereg_E2.json`, sha256 514d7fddec830319fa0cdaab327819d657961a4413de6e74fa1517eb898d9269 (written before any attempt; parent preregistration unchanged). Cores 2,3 only.

## What is computed
Constant-flux diffusion in a sphere (uniform start x0, inward flux j from the imposed current I = C*5 A through a = 3 eps_s/R, L, A_cell; parameters printed from PyBaMM 26.10.1.1 Chen2020, `data/params_chen2020.json`).
Surface stoichiometry x_s = x0 + beta F(tau), tau = D t/R^2, beta = 0.0826678577331 per 1C, F(tau) = 3 tau + 1/5 - 2 sum exp(-a_n^2 tau)/a_n^2, tan a_n = a_n. F is strictly increasing, so t* is unique. t* depends on (x* - x0)/(C beta) only (for example 2C from x0=0.5 equals 3C from x0=0.25).

Certification (Tier C, python-flint Arb at 300 bits): roots of tan a = a bracketed in (n pi, n pi + pi/2) by rigorous sign change of sin a - a cos a (monotone there), width about 1e-42; the series tail bounded using a_n >= n pi with a geometric bound (below 2^-100); t* bracketed by interval bisection, a side decided only when the F ball lies strictly on one side of the target. Relative width of every t* interval is at most 9.8e-14 (preregistered target 1e-9). Kill criterion (i) did not fire.

## Certified t*(C) in seconds (full table with exact rational tau bounds: `data/certified_t_star.json`)
x* = 1.0 (full saturation of the surface); intervals are about 1e-10 s wide, shown to 3 decimals.

| C | x0 = 0.05 | x0 = 0.25 | x0 = 0.50 |
|---|---|---|---|
| 1 | 3916.716 | 3077.539 | 2028.568 |
| 2 | 1923.671 | 1504.083 | 979.598 |
| 3 | 1259.323 | 979.598 | 629.941 |
| 4 | 927.149 | 717.355 | 455.117 |

x* = 0.9014 (29866/33133, the 100 percent state of the set): 3502.991, 2663.814, 1614.844 (C=1); 1716.809, 1297.221, 772.735 (C=2); 1121.415, 841.689, 492.035 (C=3); 823.718, 613.924, 351.719 (C=4), same x0 order. The x0 values are hypothetical start states.

## Controls (all pass; `data/cert_controls.json`, `data/p3_checks.json`)
- P1 short time: relative difference of F from 2 sqrt(tau/pi) is 2.87e-2 at tau=1e-3 and 2.81e-3 at 1e-5 (ratio 0.098, expected about 0.1).
- P2: F(1e-5)=0.003578 (small); sum rule sum 1/a_n^2 = 1/10 holds within the rigorous tail bound (deficit 2.527e-4 against bound 2.533e-4 at N=400; weaker than the preregistered 1e-12, see deviations); F(2) - 6 - 1/5 equals the first-exponential term to 5e-54.
- P3: mpmath (50 digits, independent root finding) inside the Arb balls at all 20 points (tau 0.05 to 3.4); finite-volume method of lines (400 cells, scipy BDF, rtol 1e-10) agrees with the series to a maximum relative error 7.7e-6 (Tier X).
- P4 (Tier X): PyBaMM SPM (Chen2020, initial negative concentration set to x0 cmax, current -C*5 A, wide voltage cut-offs): first crossing of the level agrees with the certified interval, maximum relative difference 4.2e-4 with 20 radial points and 1.7e-5 with 100 points, all 24 cases; shrinks with the mesh. Kill criterion (ii) did not fire. `data/pybamm_compare.json`.
- N1: D x 1.1 gives intervals disjoint from the originals in all 24 cases. N2: a root bracket shifted by 0.005 and a wrong interval are not certified; a series with alpha_1 + 0.01 shifts F(1e-5) by 4.4e-4. N3: reversed flux sign returns "unreachable"; the 2 tau factor gives t* of 4616 s against 3078 s (disjoint). N4: PyBaMM discharge from x0=0.5 for 1500 s does not cross either level (surface concentration 16566 to 15363 mol/m3).

## SPM versus SPMe versus DFN (Tier X, exploratory)
- SPMe equals SPM on the negative-particle surface concentration (crossing times agree to about 1e-7 relative at the same mesh): in PyBaMM's SPMe the particle sees the same x-uniform current, so "t* survives SPM to SPMe" is true by construction, not a finding.
- DFN (x* = 0.9014 only; positive electrode started at 0.99 so it is not depleted): the x-averaged surface concentration crosses at the certified SPM time to 1e-4 at 1C (3 of 3 start states, plus the 100-point mesh at x0=0.25), but the **maximum over x** (separator side) crosses much earlier: at 1C by 24 percent (x0=0.05: 2667 s against 3503 s), 30 percent (x0=0.25) and 37 percent (x0=0.5); at 2C at 891.6 s against 1716.8 s (x0=0.05), 574.9 against 1297.2 (x0=0.25), 301.7 against 772.7 (x0=0.5). For C = 3, 4, and for 2C up to 1.05 t*, IDA fails (error test failures); I did not diagnose it (an untested guess: exchange current going to zero at local saturation). First failed configurations are kept in `logs/*first_attempt*`. This is a model-versus-model observation under one parameter set, not a statement about cells. Files: `data/pybamm_dfn.json`, `data/pybamm_dfn_early.json`.

## Literature (to our knowledge)
The series is classical (Crank, constant surface flux in a sphere; SPM per Marquis et al. 2019, arXiv 1905.12553); neither Crank nor the Chen et al. 2020 paper was read here. The contribution is only the certified evaluation at stated parameters plus the check against PyBaMM; no new formula. No search was made for prior certified-interval treatments of this time.

## Tiers
C: Arb enclosures of roots, F and t* (given the closed form and the printed parameter decimals; not replayed in Lean). X: float checks (mpmath, finite volume, PyBaMM SPM/SPMe/DFN). L: closed form and parameter values. A: none.

## Not claimed
No battery charges faster or is safe; no lithium plating prediction (x* is a model proxy); models are not devices; the SPM is known to be inaccurate at high C-rate (Marquis et al.); x0 are hypothetical; one parameter set; Butler-Volmer kinetics and OCV do not enter the particle surface concentration at imposed current; the DFN max-over-x result is an uninterpreted model observation.

## Deviations from the preregistration
1. No Lean (declared in `lean`); the proposal's Tier A lemmas and 20 core-h Lean were not attempted.
2. P1/P2 evaluated at tau = 1e-3, 1e-5 (not 1e-4, 1e-6, 1e-12): the series needs about 1/sqrt(tau) roots, too slow at 1e-12. P2's sum-rule check reaches 2.5e-4 absolute (400 roots, tail 1/(pi^2 N)), not 1e-12; the F(2) match at 5e-54 and the mpmath check cover the roots much more tightly.
3. N2 used a shifted bracket and an alpha_1 + 0.01 series; the "root of tan a = 2a" variant was replaced by a wrong-interval probe.
4. DFN rerun with positive electrode start 0.99 and restricted to x* = 0.9014 after the first setup failed (kept in logs). DFN for C >= 3 is not achieved.
5. PyBaMM electrode height is 0.065 m in this version (A_cell = 0.1027 m2). The positive-electrode start in PyBaMM runs was changed (affects voltage only).
6. Faraday constant taken from scipy.constants (what pybamm.constants uses), not a PyBaMM parameter key.

## An independent auditor must redo
Re-derive F and the constant-flux boundary sign and factor from Crank; recheck the parameter reading (j = I/(a L A_cell F), a = 3 eps_s/R) against the Chen et al. 2020 paper and the PyBaMM source; re-run `code/run_cert.py` and an independent interval implementation (for example mpmath.iv) for roots and tail; check the monotonicity of g on (n pi, n pi + pi/2) and the tail inequality a_n >= n pi, and the exact-endpoint bookkeeping in `spm_cert.py`; re-run PyBaMM from a clean venv; investigate the DFN failures and whether the max-over-x finding is real or setup-dependent; decide on Lean replay.

Licences: PyBaMM BSD-3-Clause (LICENSE read in the wheel); third-party install in /home/callensxavier_gmail_com/e2_thirdparty/ (not in the repo).
