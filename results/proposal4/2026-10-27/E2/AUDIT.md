# E2 independent audit (producer != verifier)

Auditor: Claude Opus 5.5, separate session, 2026-10-31. Nothing in E2 was changed except that this file was added. Scratch code and outputs are in `/tmp/e2audit/` (`my_cert.py`, `my_cert.json`, `pb_audit.py`, `pb_audit2.py` and their `.log`/`.json` files); they are not in the repo. All heavy runs used `taskset -c 2,3` with at most 2 processes.

**Verdict: ACCEPT_WITH_CORRECTIONS.** The enclosures are correct: all 24 rational tau intervals contain the auditor's independent enclosure. The PyBaMM SPM check reproduces. The DFN max-over-x observation is a real model effect at the stated mesh, but its size depends on the mesh by a few percent. The corrections below are needed. One of them is a genuine certification bookkeeping error: the seconds endpoints were not rounded outward.

## 1. Derivation (auditor's own, Crank not consulted)
- Model. c_t = D r^-2 (r^2 c_r)_r, c_r(0) = 0, uniform start c0 = x0 cmax. During charge the molar flux j > 0 goes into the particle, so **D c_r(R) = +j**.
- Scaling. With u = (c - c0)/(beta cmax), rho = r/R, tau = D t/R^2 and beta = j R/(D cmax), the problem becomes u_tau = rho^-2 (rho^2 u_rho)_rho with u_rho(1) = 1.
- Mean. Mass balance gives d/dtau of the volume mean of u equal to 3, so the mean is 3 tau.
- Quasi-steady part. The profile is 3 tau + rho^2/2 - 3/10. The 3/10 is the volume mean of rho^2/2.
- Transient. It satisfies the homogeneous Neumann problem. The eigenfunctions are sin(a rho)/rho, and phi'(1) = 0 gives tan a = a.
- Surface coefficient. The auditor computed the coefficient at rho = 1 by quadrature (mpmath) for n = 1, 2, 5 and got -2/a_n^2 to 30 digits.
- Result. F(tau) = 3 tau + 1/5 - 2 sum exp(-a_n^2 tau)/a_n^2. This agrees with the producer's formula, factor and sign.
- Prereg sign slip. `prereg_E2.json` writes "-D c_r(R) = j (constant, inward under charge)". With j > 0 inward the sign is wrong. The code uses the correct sign (x_s increases, and N3 checks this).
- beta. beta = j R/(D cmax) with j = I/(a L A_cell F) and a = 3 eps_s/R, so beta = I R^2/(3 eps_s L A_cell F D cmax).
- beta value. The auditor evaluated beta with mpmath.iv from the decimal strings of the PyBaMM 26.10.1.1 Chen2020 set (D 3.3e-14, R 5.86e-6, eps_s 0.75, L 85.2e-6, height 0.065, width 1.58, cmax 33133, I = 5 A, F = 96485.33212331001). The result is **beta = 0.0826678577330640 per 1C**, the same as the producer's 0.0826678577331.
- Cross-check on beta. Over 3600 s at 1C the mean stoichiometry rises by 0.858, and the negative-electrode capacity between 0.0279 and 0.9014 is about 5.1 Ah. Both are consistent with 5 Ah = 1C.
- Agreement with PyBaMM. PyBaMM's SPM reproduces the crossing to 4e-6 (section 3), so PyBaMM uses the same j and a.
- x* = 0.9014. This is 29866/33133, PyBaMM's default initial negative concentration, which is the set's 100 % SOC state.
- Source for 0.9014. Secondary sources (arXiv 2311.05482) quote Chen et al. 2020 as reporting a negative stoichiometry window of 0.0279 to 0.9014. The auditor did not read the Chen paper.
- 0.9014 is a cell-balancing limit, not a saturation. "Saturation" applies only to x* = 1.

## 2. Independent certified evaluation (all 24 cases verified)
- Method. mpmath.iv at 60 digits.
  - Roots: interval Newton (contraction N(X) ⊂ X proves a unique root) starting from mp-Newton seeds. Each box is checked to lie inside (n pi, n pi + pi/2).
  - Tail: an **integral** bound, sum_{n>N} <= int_N^inf exp(-pi^2 tau x^2)/(pi^2 x^2) dx <= erfc(N pi sqrt tau)/(2 sqrt(pi tau) pi^2 N^2), with erfc(z) <= e^{-z^2}/(z sqrt pi). N = 40.
  - tau: interval Newton on F(tau) - T, after checking the bracket [(T-1/5)/3, T/3] by evaluation.
  - None of this shares code with `spm_cert.py`.
- Result. Enclosure widths are about 1e-56 s.
  - Every auditor tau enclosure lies inside the producer's rational [tau_lo, tau_hi] (24/24).
  - The auditor's beta matches the producer's.
  - The table values in RESULT.md are confirmed to their 3 decimals.
- Reading of `spm_cert.py`.
  - g'(a) = a sin a has constant sign on (n pi, n pi + pi/2), so a certified sign change there gives exactly one root. That root is the n-th positive root, because there is none in (n pi - pi/2, n pi) or in (0, pi/2).
  - The bisection endpoints are exact midpoints, nudged 2^-100 inside the interval, and the root stays at distance about 1/(n pi) from both ends.
  - The tail bound is correct: a_n >= n pi, and the term ratio is at most exp(-2 m pi^2 tau)^k.
  - The tail is added as the ball [0, tb]; `arb(mid, rad)` semantics were checked.
  - `enclose_tau` decides a side only when the ball lies strictly on one side.
  - The lower end lo = 0 relies on the analytic F(0) = 0. That is acceptable.
- **Error (bookkeeping).** `run_cert.py` converts endpoints with `float(tlo.lower())` and `float(thi.upper())`, which round to nearest, not outward.
  - In **4 of 24 cases** the true t* lies below the published `t_lo_s`:
    - C=1, x0=0.05, x*=1: 1.5e-13 s below
    - C=1, x0=0.05, x*=0.9014
    - C=1, x0=0.50, x*=1
    - C=2, x0=0.05, x*=1
  - Exact rational arithmetic also shows that the published seconds interval fails to contain the producer's own tau interval times R^2/D in 23 of 24 cases.
  - The rational tau intervals are rigorous; the seconds column is not. The physical size is negligible (about 1e-13 s), but the word "certified" requires the fix.
- **Framing finding.** For every case t* equals the long-time two-term formula t = (R^2/(3D))[(x* - x0)/(C beta) - 1/5] up to the exponential correction. For example, C=1, x0=0.05: (0.95/beta - 0.2) R^2/(3D) = 3916.7158 s.
  - The relative size of that correction, 2 e^{-a_1^2 tau}/(a_1^2 T), ranges from 8.5e-36 (C=1, x0=0.05, x*=1) to 8.9e-5 (C=4, x0=0.5, x*=0.9014).
  - It is below 1e-12 in 11 of 24 cases.
  - So the certified series contributes only that correction, and "t* depends only on (x*-x0)/(C beta)" follows at once.
- Controls.
  - P1: confirmed (the ratio 0.098 fits the sqrt(tau) scaling).
  - P2 sum rule: weak as run, but not a soundness issue, because the 1/5 constant comes from the derivation. A two-sided version is cheap: the deficit 2.5267e-4 lies in [1/(pi^2 (N+3/2)), 1/(pi^2 N)] = [2.5236e-4, 2.5330e-4].
  - N2 is weak but discriminates. The shifted bracket and the probe [4.40, 4.45] both exclude a_1 = 4.4934, and the alpha_1 + 0.01 series moves F(1e-5) by 4.4e-4.
  - N3: the preregistered second half ("the P2 long-time check must fail" with 2 tau) is only a comment in `run_cert.py`. It would fail trivially (F(2) - 6.2 = -2). The 2 tau versus 3 tau discrimination is in fact supplied by P4 (PyBaMM).

## 3. PyBaMM rerun (producer venv, run by the auditor's own script)
- SPM setup. r_n = 200 (the producer used 20 and 100), dt = 0.25 s, positive start 0.99.
- SPM results. The crossing times agree with the auditor's enclosure to the following relative errors:
  - 3.7e-7 for C1, x0=0.05, x*=1
  - 9.6e-7 for C2, x0=0.25, x*=1
  - 1.3e-6 for C3, x0=0.05, x*=0.9014
  - 4.3e-6 for C4, x0=0.5, x*=0.9014
  - P4 is confirmed and the error shrinks with the mesh.
- DFN at 1C, x0=0.25 (x_n=20). The auditor reproduced the producer's numbers bit-for-bit: the max over x crosses 0.9014 at 1870.76 s, and the node average at 2663.96 s against the certified 2663.81 s.
  - The positive start (0.99 or 0.60) changes nothing in c_s; only the voltage changes.
  - The maximum sits at the node next to the separator (83.07 of 85.2 µm).
  - At t = 10 s the interfacial current near the separator is 1.39 times that near the collector.
  - **The effect is real in the model.** It is the classical non-uniform reaction distribution of porous-electrode theory, not a mis-definition. The quantity is c_s on the negative electrode only, and avg/max are taken over x_n nodes.
  - **Its size depends on the mesh.** With x_n = 40 the max crossing is 1843.5 s instead of 1870.8 s (1.5 % shift). At 3C, x0=0.25 the 0.9014 crossing moves from 206.0 s to 194.2 s. The producer refined r_n only, never x_n, so the "24/30/37 %" figures are not mesh-converged in x.
- DFN failures for C >= 3: **diagnosed** at 3C, x0=0.25 (x_n = 20 and 40).
  - The electrolyte concentration in the negative electrode falls below 1 mol/m3 at 368.5 s (both meshes).
  - The local surface concentration reaches 0.9999 cmax at about 400 s.
  - IDA fails at 400.5 to 401.2 s with c_e slightly negative and the local c_s above cmax. Chen2020's j0 ∝ c_e^0.5 c_s^0.5 (cmax - c_s)^0.5 then becomes NaN.
  - The positive surface stoichiometry is 0.589, so the positive electrode is not the cause.
  - At 4C, x0=0.05 the failure is at 193.6 s with c_e = -6.6e-4 mol/m3 at 70 µm.
  - So the failure is a genuine loss of validity of the model state: electrolyte depletion followed by local saturation. It is not a solver option problem.
  - The 2C failures were not diagnosed by the auditor.

## 4. Wording and novelty
- RESULT.md stays model-versus-model. It makes no claim about faster charging, safety, plating or cells, which is consistent with sections 6 and 7 of the proposal. "Series classical, no new formula" is correct.
- Quick literature search (2 web queries, not exhaustive). The auditor found no certified-interval treatment of this saturation time.
  - Related analytic onset-time work exists: Li et al. 2025, ACS Energy Lett., an analytic Li-plating onset model.
  - The long-time offset 1/5 = c_surf - c_avg in units of jR/(D cmax) is the same constant as in the parabolic-profile SPM reductions. The auditor believes this includes Subramanian, Diwakar and Tapriyal 2005, J. Electrochem. Soc. 152 A2002, but did not read it.

## 5. Provenance
- All 28 sha256 values in `result.json` match the files.
- The prereg sha256 is 514d7fdd...d9269, which matches.
- The PyBaMM wheel's LICENSE.txt is BSD-3-Clause, Copyright (c) 2018 the PyBaMM team.
- The repo holds only 9 parameter values printed from the set (`params_chen2020.json`) and producer-generated outputs. No third-party data files or code are vendored.

## 6. Corrections (old -> new)
1. `code/run_cert.py`: `t_lo = float(tlo.lower())` -> `t_lo = math.nextafter(float(tlo.lower()), -math.inf)` and `t_hi = float(thi.upper())` -> `t_hi = math.nextafter(float(thi.upper()), math.inf)` (add `import math`). Rerun, regenerate `certified_t_star.json`, and add to RESULT.md: "The rigorous enclosures are the exact rational tau bounds; second bounds are rounded outward."
2. RESULT.md "What is computed": after "so t* is unique." add: "For all 24 cases t* equals the long-time formula (R^2/(3D))[(x*-x0)/(C beta) - 1/5]. The exponential series changes it by a relative amount between 8.5e-36 (C=1, x0=0.05, x*=1) and 8.9e-5 (C=4, x0=0.5, x*=0.9014), below 1e-12 in 11 of 24 cases. The certificate's content is mainly that correction."
3. RESULT.md: "x* = 0.9014 (29866/33133, the 100 percent state of the set)" -> "x* = 0.9014 (29866/33133, the set's default initial = 100 % SOC negative stoichiometry; Chen et al. 2020 report 0.9014 as the upper limit per secondary sources, paper not read; a balancing limit, not a saturation)".
4. RESULT.md DFN paragraph: "I did not diagnose it (an untested guess: exchange current going to zero at local saturation)" -> "Auditor diagnosis at 3C, x0=0.25: electrolyte concentration in the negative electrode falls below 1 mol/m3 at 368 s, the local surface reaches 0.9999 cmax at about 400 s, and IDA fails at 400.5 s with c_e < 0 and c_s > cmax (j0 becomes NaN). The DFN state leaves its validity domain; 2C not diagnosed."
5. RESULT.md DFN paragraph: after "(separator side, ...)" add: "values at x_n = 20; x_n = 40 gives 1843.5 s instead of 1870.8 s (1C, x0=0.25) and 194.2 s instead of 206.0 s (3C), so the percentages are not mesh-converged in x (about 1.5 to 6 %)".
6. RESULT.md Deviations, add: "7. N3's second part (P2 long-time check with 2 tau must fail) was not executed; the 2 tau/3 tau discrimination rests on the disjoint t* and on P4. 8. prereg text '-D c_r(R) = j' has the wrong sign for j > 0 inward; the code uses D c_r(R) = j."
7. RESULT.md Literature: "No search was made for prior certified-interval treatments of this time." -> "An auditor quick search (2 queries) found no certified-interval treatment; the 1/5 long-time offset is the constant of parabolic-profile SPM reductions (e.g. Subramanian et al. 2005, not read)."
8. Optional: replace the one-sided P2 sum-rule check with the two-sided bracket [1/(pi^2(N+3/2)), 1/(pi^2 N)].
9. Regenerate `result.json` hashes after the edits.

## 7. Not verified by the auditor
- Crank and Chen et al. 2020 were not read. The formula was derived independently and the coefficient checked numerically. 0.9014 is checked only against secondary sources.
- The finite-volume P3 check, the SPMe identity and N4 were not rerun.
- The 2C DFN failure was not diagnosed.
- There is no Lean, so nothing is Tier A.
- The float values printed in the RESULT.md table are correct to their 3 decimals.
