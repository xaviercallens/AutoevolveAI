# K3 (Proposal 4): completely monotone carbon-cycle impulse responses, concentration peaks

Producer run, 2026-10-31, cores 4,5 only, Sonnet-tier producer, **not audited** (LEDGER_UNAUDITED_TIER_A applies to the Lean items). AI-drafted; no human expert has reviewed it.
Preregistration: `prereg_K3.json`, sha256 `fc9571ec1eb29f99cd12dd5504efdaaa9dfa55f2b1f1938581573c63a6868699` (written and hashed before any attempt; parent `preregistration.json` unchanged, sha256 `7f7d5ac1...b438`).

**Outcome: PARTIAL.** (a) and (c) done as preregistered (Lean covers the discrete-emission case only), (b) done for a stated scenario family, with a parameter inconsistency in the source.

## Scope and what is NOT claimed
All statements are about a stylised **linear** impulse-response model with the Joos et al. 2013 multi-model-mean coefficients. No tonnes, no climate effect, no warming, no emission-pathway or deployment advice. The Joos fit is a multi-model mean for one pulse experiment; real carbon-cycle responses are state-dependent and nonlinear, so "concentrations fall after emissions stop" is a model statement only. The two-peak emission paths below are mathematical test inputs, not scenarios.

## Sources (read in full where needed; third-party PDFs kept outside the repo in `/home/callensxavier_gmail_com/k3_thirdparty/`)
* Joos et al. 2013, ACP 13, 2793, doi:10.5194/acp-13-2793-2013, **CC BY 3.0** (landing page). Table 5, row IRFCO2: a0..a3 = 0.2173, 0.2240, 0.2824, 0.2763; tau1..tau3 = 394.4, 36.54, 4.304 yr; sum of a exactly 1.0000 (control P1). Used as exact decimals.
* Seshadri, arXiv 1502.00805v3: his eq. (1) prints 0.276, 0.282, 0.224, 0.217, **sum 0.999**, tau 4.30 / 36.5 / 394, and the text uses tau1 = 4.4 (inconsistent, as the proposal noted). His emission family m = m0 (1+r)^(min(t,tg)-t0) exp(-(t-t0)/tau_m). His Fig. 5 scenario "tg-t0 = 60 yr, r = 0.015 %/year, tau_m = 50 yr" is internally inconsistent with his own condition r > 1/tau_m (ln 1.015 = 0.0149 < 0.02; the unit "%/year" is also ambiguous). I did not resolve this; I report both readings.
* Ciais et al. arXiv 2609.34226 (licence not checked; only the printed numbers are quoted, with citation): control P4.

## (a) Post-cessation complete monotonicity
**Paper proof (Tier C), continuous m.** For m >= 0 supported on [0,T] and t > T, u(t) = a0 W + sum_i b_i exp(-t/tau_i) with W = int m and b_i = a_i int exp(z/tau_i) m(z) dz >= 0. Hence (-1)^n u^(n)(t) = sum_i b_i tau_i^(-n) exp(-t/tau_i) >= 0 for all n: completely monotone on (T, inf), non-increasing, convex, limit a0 W. This is elementary (a positive mixture of shifted completely monotone functions); to our knowledge it is standard, so the value is an independent kernel check, not a new theorem.

**Lean (Tier A candidate, discrete emission measures only), `formal_cert/Programmes/CarbonK3/Core.lean`**, pinned Lean 4.34.1 + Mathlib d13f23b7 via `scripts/certified_numerics/lean_pinned.py`: rc 0, 17.7 s. Statements (reusing `ProgCM`, the repository's CM library): `irf_cm` (the sum-of-exponentials IRF with a0, a_i, r_i >= 0 is CM), `excess_cm_after` (for finitely many nonnegative impulses at times <= T the excess is CM on (T, inf)), `excess_antitone`, `excess_convexOn`, `excess_tendsto` (limit a0 * sum w_j when all r_i > 0), `neg_ctl_not_cm` (h = 1 - exp(-t) is not CM). `#print axioms` of all six = {propext, Classical.choice, Quot.sound}. `leanchecker Programmes.CarbonK3.Core` rc 0 (49.5 s). Escape grep (sorry, native_decide, admit, unsafe, extern, implemented_by, axiom) on Core.lean: no match. Planted controls `Controls.lean` compile with rc 0 and are caught by the axiom gate (`ctl_sorry` shows sorryAx, `ctl_axiom` shows `CarbonK3.ctl_cheat`). The continuous-m version is not in Lean. Statement fidelity is not independently audited.

**Numerical (Tier X).** P5: 200 random nonnegative emission histories with the Joos IRF: post-cessation u is non-increasing and convex on a grid in 200/200; limit u(1e6) equals a0 W to about 1e-8 (5 spot checks). N1: with one negative coefficient (a0 = 0.6573, a1 = -0.2240, a2 = 0.2824, a3 = 0.2763; sum 1) 181/200 histories violate monotonicity or convexity (the check fails when it should).

## (b) Concentration-peak time and delay for Seshadri's emission family (Tier C enclosures, given the pinned coefficients)
Method: closed-form u' and u'' (interval arithmetic, mpmath iv, 60 digits), exact rational bisection with certified signs u'(lo) > 0 > u'(hi) and u'' < 0 on the initial bracket, so the peak is a unique local maximum inside the enclosure (width < 1e-19 yr). t1 (emissions peak) is certified from the sign of ln(1+r) - 1/tau_m: t1 = tg if positive, t1 = t0 = 0 if negative. Time origin t0 = 0, emissions before t0 ignored (not varied). 63 scenarios (3 IRFs x 3 r x 7 tau_m) all CERTIFIED; `data/results_b.json`.

Joos Table 5, tg = 60 yr, delay = t2 - t1 in years (values to 2 decimals; the enclosures are in the JSON):

| tau_m | r = 0.03 | r = 0.05 | r = 0.015 (printed) |
|---|---|---|---|
| 20 | 69.55 (t1 = 0) | 79.34 (t1 = 0) | 58.68 (t1 = 0) |
| 40 | 50.47 | 59.52 | 99.01 (t1 = 0) |
| 50 | 70.48 | 79.40 | 119.04 (t1 = 0) |
| 60 | 91.22 | 100.12 | 139.78 (t1 = 0) |
| 80 | 134.32 | 143.31 | 122.80 |
| 100 | 176.95 | 185.99 | 165.36 |
| 120 | 217.35 | 226.37 | 205.73 |

* The delay is **not monotone in tau_m** across the boundary r = 1/tau_m (where t1 jumps from tg to 0); this is a property of the definition of t1, noted so that nobody reads the table as a smooth trend.
* Tier X comparison with Seshadri: his Fig. 5 states delays of about 100-135 yr for the printed scenario; our certified value for r = 0.015, tau_m = 50 is 119.04 yr when t1 = 0 (consistent), and his Fig. 2 range 40-220 yr is reproduced in order of magnitude. This agreement does not show the intended reading of his parameters.
* Variants with his printed eq. (1) coefficients (sum 0.999) and tau1 = 4.30 or 4.4 change the delay by at most 0.36 yr across all 21 matched scenario pairs (`results_b.json`). The 0.001 coefficient defect of his eq. (1) is therefore immaterial for the delays, though it matters for the long-run limit.
* In all 63 float scans of u' on [0, 6000] yr there is exactly one sign change (+ to -): the Seshadri family gave one concentration peak in every tested case (Tier X, not a theorem).
* Positive control: single-exponential h = exp(-t/30), m = exp(-t/50) has the closed-form peak 75 ln(5/3) = 38.311921782449301240...; the certified enclosure [38.31192178244930124039, 38.31192178244930124045] contains it (`data/control_closed_form.json`).

## (c) Can a single-peaked emission path give two concentration maxima?
**Answer in this model: yes, whenever the IRF is not a single exponential. "At most one peak" holds for a single exponential and fails for the Joos IRF.** To our knowledge (one alphaXiv query and the Seshadri and Joos texts; no systematic search) this is not stated in the literature read; Seshadri studies the delay and the condition for a peak to exist, not the number of peaks.

**Theorem T3 (paper proof, Tier C).** Let h be completely monotone, h(0) = 1, strictly decreasing, and not a single exponential, d > 0, A > 0. Then rho(x) = h(x+d)/h(x) is strictly increasing (strict log-convexity of a non-exponential CM function) with rho(0) = h(d) < rho(infinity) = L <= 1 (L = 1 iff a0 > 0). Take theta in (h(d), L), B = theta A, emission m = A on [0,d), (A-B) on [d, z3), 0 afterwards (unimodal, nonnegative), z3 > d + x*, rho(x*) = theta. For t = d + x in (d, z3): u'(t) = A h(t) - B h(x) = h(x) (A rho(x) - B), negative for x < x*, positive for x > x*. With u'(d-) = A h(d) > 0 and u'(d+) = A (h(d) - theta) < 0, u has a local maximum at t = d, a local minimum at d + x*, and since u'(z3-) > 0 > u'(z3+) (use h(x) <= 1) a second local maximum at z3. For a single exponential rho is constant and u has at most one maximum (T2 below).

**Theorem T2 (paper proof, Tier C).** For h = exp(-t/tau) and m unimodal, u has at most one local maximum: g(t) = exp(t/tau) u'(t) = exp(t/tau) m(t) - V(t)/tau with V(t) = int_0^t exp(z/tau) m(z) dz satisfies dg = exp(t/tau) dm, so g is non-decreasing up to the emission peak (with g(0) = m(0) >= 0) and non-increasing after it; thus u' is >= 0 then <= 0.

**Certified instances (Tier C; five interval values each, u(s2) > u(s1), u(s2) > u(s3), u(s4) > u(s3), u(s4) > u(s5); continuity gives a local maximum in (s1,s3) and one in (s3,s5)); exact rational inputs, Joos Table 5; `data/results_c.json`:**
* I1, **continuous** piecewise-linear unimodal emission, nodes (year, level) = (0,0), (10,1), (22,1/10), (300,1/10), (310,0): u at s = 10, 21, 32, 303, 320 = 4.2161, 7.9964, 7.6834, 15.4774, 14.9042 (interval half-width < 1e-56); lower bounds of the four differences 3.78, 0.313, 7.79, 0.573. Float picture: maxima at 20.7 and 303.2 yr, minimum at 31.9 yr.
* I2, same but strictly decreasing after the peak (level 1/20 at 300): s = 10, 21, 40, 305, 330; all four differences positive (min 0.278).
* S1, staircase (jumps +1 at 0, -9/10 at 5 yr, -1/10 at 200 yr): s = 1, 5, 11, 200, 500; differences 3.37, 0.322, 6.59, 3.35, all > 0.
* A first attempt with the wrong middle time (s3 = 100) for S1 returned `two_local_maxima_certified: false`; the times were then chosen from the float minimum (11 yr). This is recorded: the certificate depends on the chosen times, not on a search that hid failures.
* Mechanism, Tier X: a sharp drop to a low positive plateau lets the fast modes (tau 4.3 and 36.5 yr) decay, so the persistent a0 fraction of the plateau emissions pushes concentration up again until emissions cease.

**Where it happens (Tier X, floats).** Plateau family (rise to 1 by yr 10, linear drop to level L over D years, plateau to yr 300, ramp to 0 by yr 310): two maxima for L <= 0.15 for all D in {2,5,12,20,40}; for L = 0.2 for D = 2, 5 and 40 but one maximum for D = 12, 20; one maximum for L >= 0.25. Over 1500 random continuous unimodal piecewise-linear paths (seed 7) with the Joos IRF: 17 have no interior maximum, 1364 one, 117 two, 2 three; the same paths with a single-exponential IRF never give more than one (control P2). A hypothetical IRF with a0 = 0 (decays only, rescaled) also gives 2 maxima with a long plateau; a two-term IRF a0 = a1 = 1/2, tau = 50 gives 2 maxima for jump-down ratios above h(d) and 1 below, as T3 predicts (`logs/check_two_term.log`).

**What is not established.** A sufficient condition for "at most one peak" beyond a single exponential is not found (the preregistered second budget was not used; only the single-exponential case is proved). No statement is made about which realistic emission paths have two peaks.

## Controls (all in `data/` and `logs/`)
| Control | Result |
|---|---|
| P1 Joos coefficients sum to 1; Seshadri printed sum 0.999 | pass (exact rationals) |
| P2 single exponential: closed form u vs random unimodal paths | max 1 maximum in 1500 paths; pass |
| P3 closed-form u equals mpmath quadrature of the convolution | 50/50 inside interval, tolerance 1e-20; pass |
| P4 CARBON-1: 10.38 - 2.04 - 3.15 - 2.06 * 2.124 | exactly 5091/6250 = 0.81456, rounds to the printed 0.81; pass |
| P5 post-cessation antitone and convex; limit a0 W | 200/200; pass |
| Closed-form peak 75 ln(5/3) | enclosed; pass |
| N1 negative coefficient | 181/200 histories violate; Lean `neg_ctl_not_cm`; pass |
| N2 wrong sign in H (1 + exp) | rejected at 50/50 points; pass |
| N3 same emission, single exponential vs Joos | 1 vs 2 maxima (I1 and S1); pass |
| N4 planted sorry / axiom in `Controls.lean` | caught by `#print axioms`; pass |

## Tiers
A candidate (unaudited): Lean discrete-case lemmas. C: interval enclosures (b), certified two-maximum instances (c), hand proofs T1-T3 for the continuous case. X: floats, random searches, comparisons with Seshadri figures. L: Joos and Seshadri formulae.

## Deviations from the preregistration
* The Lean lemma set was extended with `cm_convexOn` and the limit statement; no change of claim.
* (b) uses the family r in {0.03, 0.05, 0.015}, tg = 60, and three IRF variants as preregistered; the table above is Joos only.
* Lean compile took 22 min the first time (cold disk cache) and 17.7 s afterwards; no result changed between runs, the first runs failed on API names.
* Random search for (c) used one budget; the second budget was not needed for the existence result.
* `explore_*.py` scratch scripts were deleted; the instances were found with `k3lib.u_float` (floats) and then certified by `run_c.py`.

## What an independent auditor must redo
1. Re-read Joos Table 5 (row IRFCO2) and confirm the nine numbers; confirm the CC BY 3.0 licence on the journal page.
2. Recompute u for I1/I2/S1 with an independent implementation (not `k3lib.py`), including the closed forms H and K (integrals of h), and check the five-point inequalities with rigorous intervals.
3. Check the Lean statements against T1 (discrete case is the only formalised case), rerun the axiom audit, the leanchecker replay and the escape grep.
4. Re-derive T3 and T2 by hand, including strict log-convexity of non-exponential CM functions and the sign of u'(z3+).
5. Check the Seshadri emission family reading (time origin t0 = 0; r per year and the r vs 1/tau_m inconsistency), and the scan claim of a single peak in all 63 scenarios if it is going to be cited (currently Tier X).
6. Decide whether the answer to (c) is already known in the carbon-cycle literature (the search here was minimal).

## Files
`prereg_K3.json`, `prereg_K3.sha256`, `code/` (k3lib.py, run_c.py, run_b.py, control_closed_form.py, check_two_term.py, leanchecker_replay.py, write_result_json.py), `data/` (results_b.json, results_c.json, control_closed_form.json), `logs/`, `result.json` (sha256 of every file); Lean in `formal_cert/Programmes/CarbonK3/` (Core.lean, Controls.lean). Run with `taskset -c 4,5 .venv/bin/python code/<script>` from the repository root.
