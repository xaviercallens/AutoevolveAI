# PH-2 independent audit (auditor: Opus agent, producer != verifier), 2026-11-14

VERDICT: ACCEPT_WITH_CORRECTIONS (independent check confirmed t=1 and t=10; the t=40 auditor run was still in progress at handback, see aud_encl.log)

Auditor scratch (scripts and outputs): ~/.claude/jobs/6ecda88c/tmp/ph2audit/ (aud_lohner.py, aud_encl.json, compare.py, resume_test.py/.out, ctrl_rerun.json/.log, radau_check.py, radau.json). The auditor used none of the producer's step logic. The producer's code was run only as the object under test: the controls rerun and the resume test.

## 1. Preregistration
- `sha256sum PREREG_ITEM.md` = 193f1d90...a5703 = PREREG_ITEM.md.sha256. MATCH.
- Anchoring caveat: PREREG_ITEM.md was first committed in 00328e1 (2026-11-13 21:26), two days after the 2026-11-11 13:34 production launch. The freeze therefore rests on file mtimes (11:11) and a self-hash, not on git. logs/cvode_raw.jsonl has mtime 13:36, after the freeze. That fits the appended non-preregistered atol=1e-10 run, but the prereg line-3 claim that the comparator outputs predate the freeze cannot be verified from git.
- Deviations (all disclosed below, none blocks):
  D1. A non-preregistered rusty-SUNDIALS run used rtol=1e-10 with atol=1e-10. The preregistered rtol=1e-10/atol=1e-13 run failed with ErrTestFailure and produced no output. Every rtol=1e-10 row in the table comes from the non-preregistered run.
  D2. The driver cap was raised by the main session in several relaunches (21600 -> 11000 -> 27700 -> 29900 s cumulative). The total, 8.31 core-hours, is within the preregistered 10. CPU used between the last checkpoint and each kill is not in the ledger, so the ledger slightly undercounts.
  D3. Three relaunches followed session ends or reboots. Section 2(f) covers why resume cannot change the results.
  D4. O1 (simplex invariance used to restrict the region) was NOT used. The region is all of R^2. This is the safe direction.
  D5. O6 is implemented with the exact 2x2 spectral norm, not the preregistered Frobenius norm. It is valid and tighter.
  D6. The controls (logs/controls.json, 12:52) were run on an EARLIER version of ph2_enclose.py: the final file is dated 13:34. A rerun on the final code (auditor, ctrl_rerun.log) gives identical containment and broken-control verdicts. Relative widths differ only in about the 8th digit, for lin y2 and lin p24 y1 at t=10. The auditor's rerun is the control evidence for the production code.
  D7. The preregistered "second implementation/second precision" in PREREG_DRAFT was not done by the producer. This audit supplies it up to t=40 only.
- Outcome rule: PARTIAL is correct (width <= 1e-6 holds to T=4000; T=40000 was not reached). The run ended on the CPU budget, not on a method failure. The log's last line is `stopped: cpu_cap` at t ~ 4007.8. RESULT.md's "stopped: None" is a bug: `run()` sets `res["stopped"]` after `save()` (ph2_enclose.py:342-343), so the checkpoint never records it.

## 2. Proof obligations

Theorem used for one step. Notation:
- [0,h] is the step. q is the polynomial reference with q(0)=m. P is an invertible constant matrix and ||v||_P = ||P^-1 v||_2. z is the true solution of z'=f(z), with ||z(0)-m||_P <= eps0.
- dbar >= sup_[0,h] ||P^-1 (f(q)-q')||_2. rho > 0.
- U is a box containing every segment [q(t), q(t)+P w] with ||w|| <= rho, t in [0,h].
- nu >= sup over J in J(U) of lambda_max(sym(P^-1 J P)).

If (eps0 + dbar h) e^{max(nu,0) h} < rho, then z exists on [0,h] and ||z(t)-q(t)||_P <= eps0 e^{nu t} + dbar int_0^t e^{nu s} ds for all t in [0,h].

Proof:
- Set e = z - q and w = P^-1 e.
- Then w' = P^-1 (f(z)-f(q)) + P^-1 D with D = f(q) - q'.
- f(z)-f(q) = J(q+e/2) e. This is exact because f is quadratic and J is affine.
- While ||w|| <= rho, the point q+e/2 lies in U. Hence <w, P^-1 J P w> <= nu |w|^2 and D^+ |w| <= nu |w| + dbar.
- Comparison gives the Gronwall bound. That bound is < rho on [0,h], so a first exit from the closed tube is impossible.
- The solution stays in a compact set, so it extends to the whole step.

This is the standard log-norm a-posteriori argument. It holds for the nonlinear system because J is taken over the whole tube U, not just at q.

| Obligation | Status | Where |
|---|---|---|
| (a) Defect | DISCHARGED. The reference q is a polynomial, so D = f(q)-q' is an exact polynomial of degree 2p-2 with no truncation remainder. Its coefficients come from ball Cauchy products of the exact dyadic q_k (`Fk`; the convolution index range was checked). dbar = sum_k ||P^-1 D_k|| h^k bounds sup over the WHOLE interval [0,h] by the triangle inequality, t^k <= h^k. No a-priori tube is needed for the defect. | ph2_enclose.py:98-113, 208-218 |
| (b) One-sided Lipschitz | DISCHARGED. U = interval-Horner range of q over [0,h] plus row_i(P)*rho*[-1,1], ph2_enclose.py:228-234. This contains every point z(t) in the tube and every segment point. J is affine, so `jac_ball` over U encloses J(U) exactly up to rounding. M = Pi J P is computed in balls. nu is the closed-form lambda_max of the symmetric part, evaluated in balls (inclusion-isotonic, so an upper bound over all matrices in the box). The norm is ||P^-1 .||_2 for a fixed P per step, consistent at both ends. The condition number of P enters only through O5, O6 and O7, and each of those is converted explicitly. | 77-88, 228-240 |
| (c) Bootstrap | DISCHARGED. The check is emax.upper() < rho.lower(), with emax = (eps0+dh) e^{nu_+ h} >= the Gronwall bound on the whole step. eps_end is evaluated over the nu ball and rounded up. The bound is monotone increasing in nu and the ball contains nu.upper, so this is valid. Both branches of g are valid, including the case where nu contains 0. | 225-248 |
| Jump / basis change (O5, O6) | DISCHARGED. ||P_new^-1(z - m')|| <= sigma_max(P_new^-1 P_old) eps_end + ||P_new^-1 (q_old(h) - m')||. The jump ball encloses q_old(h) - m'. The spectral-norm formula is correct for 2x2. | 199-207, 249-251 |
| Output (O7) | DISCHARGED. |e_i| <= ||row_i P|| ||w|| (Cauchy-Schwarz). y1 = 1 - y2 - y3 is exact, because sum f_i = 0 identically for the 3-D system, so the 2-D reduction is an equivalence, not an assumption. Output times are hit exactly by truncating the last step. | 252-255; finalise.py:27 |
| (d) Positivity / invariants | NOT USED, so nothing to discharge. Conservation is an algebraic identity of the reduction. | RESULT.md l.189 |
| (e) Rounding | DISCHARGED-WITH-CAVEAT. Floats appear only in: the choice of h; the eigenvector basis P (floats converted exactly to balls, P^-1 by the ball adjugate, and det containing 0 is rejected); the comparisons with `tau` (step control only); `info`/history display; and `B(float)`, which is exact via as_integer_ratio. numpy is used only in `jac_float`/`choose_basis`. `sq`/`rsqrt` clip lower ends to 0, which is valid because the arguments are mathematically >= 0. `up()` rounds up. The caveat is that rigor rests on Arb/Sage 9.5 being correct; that is not independently re-verified beyond this audit's MPFI cross-check to t=40. | 17-47, 149-175 |
| (f) Resume | DISCHARGED. Checkpoints serialize t, h, m and P as exact dyadic rationals, eps_end as its exact upper bound, and jump as an exact mid plus a radius added outward. Any resumed state is therefore a valid enclosure state, bitwise or not. Test (resume_test.out): a run to t=0.4, interrupted twice and resumed, gives BITWISE identical boxes to an uninterrupted run, and both equal the production checkpoint's t=0.1 and t=0.4 boxes. This covers t <= 0.4 only; for the production resumes after t ~ 1000 the structural argument above applies. A crash-only edge case remains: if a run is killed between the last step onto an output time and the output save, the next resume raises NameError on `out`. That would be visible, not silent. | 260-303 |

## 3. Independent check (auditor's own integrator, different method)
Method: Lohner interval Taylor (order 18) with an a-priori enclosure by Moore's lemma (X + [0,h] f(Y) subset Y), a Lagrange remainder h^p T_p(Y), the mean-value form with forward-mode variational coefficients, and a QR-reorthogonalised parallelepiped. It uses MPFI intervals (Sage RealIntervalField, 128 bits), a different library from Arb, and no logarithmic norm. File: aud_lohner.py.

| t | comp | producer mid (rad) | auditor mid (rad) | aud box inside producer box |
|---|---|---|---|---|
| 1 | y1 | 0.96645973733300350 (4.6e-21) | same to 9.5e-27 (2.1e-24) | yes |
| 1 | y2 | 3.0746265785786744e-05 (1.8e-21) | same to 5.5e-29 (5.6e-28) | yes |
| 1 | y3 | 0.033509516401210707 (2.8e-21) | same to 9.6e-27 (2.1e-24) | yes |
| 10 | y1 | 0.84136992384147291 (3.5e-19) | same to 4.0e-27 (7.2e-25) | yes |
| 10 | y2 | 1.6233909379904724e-05 (1.6e-19) | same to 2.0e-27 (5.7e-29) | yes |
| 10 | y3 | 0.15861384224914718 (1.8e-19) | same to 2.1e-27 (7.2e-25) | yes |
| 40 | all | PENDING: the auditor run (aud_encl.json) was still in progress at handback | | |

Each of the auditor's boxes lies inside the producer's, and is narrower by about 1e3 to 1e8. The producer's midpoints lie within the producer's radius of the auditor's midpoints. This is strong independent evidence for t <= 10.

Non-rigorous cross-check: scipy Radau (double precision) with rtol/atol of 1e-12/1e-20 and 1e-13/1e-22, run to t=4000.
- y(4000) = (0.18320225777671084, 8.942371252775939e-07, 0.8167968479861689) at 1e-13.
- Producer mid: (0.1832022577767093, 8.942371252775910e-07, 0.8167968479861654).
- The two agree to about 8e-15 relative in y1 and 4e-15 in y3. That is OUTSIDE the producer's y1/y3 boxes (radius about 5e-16), but the two Radau runs themselves differ by 7e-16 to 3e-15, and that floor is double-precision roundoff.
- The Radau y2 lies inside the producer's y2 box (relative width 6e-10).
- Conclusion: the Radau check is consistent to about 1e-14 relative and cannot discriminate at the box's resolution.
- For 40 < t <= 4000, the enclosure has NO independent check at its own width. It rests on this code audit plus a single implementation.

## 4. Controls (rerun by auditor on the final code)
- C+1 and C+2 are contained at every time (p=24 and p=6, intact).
- C-2 broken (defect dropped, p=6): containment is lost at every time for both lin and log. The control has power. PASS.
- C-1, (1+1e-6) shift must be outside:
  - lin y1 is rejected at p=24, and both log components at p=24.
  - lin y2 is NEVER rejected, in any run, at any time. The prereg's literal kill rule (C-1 not rejected -> BLOCKED) is therefore technically triggered for that component.
  - Auditor's adjudication: the test has no power there, so this is not a soundness failure. y2 = e^{-1e4 t} is e^{-1000} at t=0.1, and its enclosure has an absolute width of order 1e-60 or more with relative width 3e7. A 1e-6 relative shift of a number of size e^{-1000} lies far below any representable absolute width.
  - The components where the test has power all pass.
  - In the Robertson run itself, y2 has a relative width of at most 6e-10 at y2 ~ 1e-6 to 1e-5, so a 1e-6 relative error would be rejected.
  - This must be stated in RESULT.md, not left implicit.

## 5. Rust-port comparison
- Solver: the rusty-SUNDIALS `cvode` crate via a path dependency (code/rob_runner/Cargo.toml). Current HEAD of ~/rusty-SUNDIALS branch merge-mcp-temp = af4886f23188baef113e47f3309d64b2bf440e47, matching result.json.
- Caveat: Cargo pins a path, not a commit, so the binary's source revision is recorded but not enforced. No LLNL C CVODE was used.
- Error intervals: d = exact(double y_solver) - Y_enclosure, using ball subtraction. lo = lower|d| (0 if d contains 0) and hi = max endpoint (finalise.py:50-58). This is interval subtraction, not midpoint only. CORRECT.
- The flags follow the prereg: exceeds = lo > rtol*upper|y| + atol; within = hi <= rtol*lower|y| + atol.
- Tolerances: rtol 1e-4, 1e-6 and 1e-8 use atol = 1e-3*rtol (scalar). rtol 1e-10 uses atol 1e-10 (D1). The RESULT.md table header saying "atol = 1e-3*rtol" is wrong for the rtol=1e-10 rows.
- y2 "none among the reached output times" holds ONLY because atol dominates the tolerance for y2 (y2 <= 3.6e-5, so rtol*y2 << atol). Measured against rtol*|y2| alone, the Rust port's y2 error exceeds rtol by up to 169x (rtol=1e-10, t=4000), by up to 20x (rtol=1e-8), up to 11x (1e-6), and up to 4.1x (1e-4). Throughout, err/atol <= 0.16.
- "provably > tol" compares a GLOBAL error with a per-component tolerance scale. CVODE controls a local WRMS error estimate, so these rows document the size of the global error, not a breach of the solver's contract.
- "Secondary literature values": cvRoberts_dns is run at rtol=1e-4 with vector atol, so its printed values are SOLVER OUTPUT at rtol=1e-4, not the true solution. The "5e-6 rounding" framing is misleading; for example, t=4 y2 differs by 5.5e-5, which is 11x that figure, and is consistent with solver error at rtol=1e-4. The values are recalled, not fetched.

## 6. Literature (2026-11-14)
- alphaXiv, 'validated integration Robertson stiff problem rigorous enclosure': no validated Robertson result. The only hit was the Taylor tube method for validated IVPs, arXiv 2604.19068, which is generic.
- WebSearch (standard): no validated Robertson enclosure, and no CVODE-versus-rigorous-enclosure study. Related items: Neumaier's log-norm enclosures for stiff problems (arnold-neumaier.at/ms/ivpBounds.pdf), and Lin-Stadtherr/VSPODE and Flow*/CAPD evaluations on kinetics models.
- No scoop was found. Absence is not proof: VNODE-LP, CAPD and COSY papers were not checked individually.

## 7. Allowed wording and tiers
- Allowed, Tier C: "A validated enclosure of Robertson's problem (k = 1/25, 1e4, 3e7, y(0)=(1,0,0); exact rationals) at the output times 0.1 to 4000, under the stated assumptions (rigorous Arb ball arithmetic; the a-posteriori log-norm lemma argued in prose, not formalized). Independently confirmed by an MPFI Lohner integrator at t=1 and 10; the later times rest on one implementation plus this code audit."
- Allowed, Tier C: "The true global error of the rusty-SUNDIALS cvode crate (Rust port, af4886f2) on this problem, for the listed rtol/atol, against the enclosure."
- Not allowed (Tier X or false): any statement about LLNL C CVODE; any statement about general stiff problems; anything about t >= 1e4 or t=1e11; "proved"/"formally verified" without the qualifier "computer-validated, not formalized"; a "first validated Robertson enclosure" priority claim, unless one says "none found in a limited search".

## 8. Corrections to RESULT.md (old -> new)
1. l.3 "stopped: None" -> "stopped: cpu_cap (cumulative 29900 s, main-session cap; the checkpoint omits the flag because of a bookkeeping order bug in run(), ph2_enclose.py:342-343)". Also fix the code: move `res["stopped"]` before `save()`.
2. l.22 "atol = 1e-3*rtol scalar" -> "atol = 1e-3*rtol scalar for rtol 1e-4, 1e-6, 1e-8; rtol 1e-10 rows use atol = 1e-10 (NON-preregistered: the preregistered atol 1e-13 run failed with ErrTestFailure and produced no output)".
3. l.153/156/159/162 "y2: none among the reached output times" -> "y2: none, because the tolerance for y2 is atol-dominated (y2 <= 3.6e-5); relative to rtol*|y2| alone the error exceeds rtol by up to 169x (1e-10), 20x (1e-8), 11x (1e-6), 4.1x (1e-4)".
4. l.165 "{0.0001: 12, 1e-06: 12, 1e-08: 12, 1e-10: 12}" -> add "(the 1e-10 count is the non-preregistered atol=1e-10 run; the preregistered 1e-10/1e-13 run gave 0 outputs)". Also: only 10 of the 12 times have an enclosure.
5. Before the table at l.26, add: "'provably > tol' compares the GLOBAL error with the per-component tolerance scale; CVODE controls a local error estimate, so this is not a breach of the solver's contract."
6. l.167 heading -> "Secondary values: SUNDIALS cvRoberts_dns printout (solver output at rtol=1e-4, NOT the true solution; recalled, not fetched)". Delete "(rounding of the 5-digit print is about 5e-6 relative)" or replace it with "(differences are consistent with rtol=1e-4 solver error)".
7. Controls section, add: "C-1 has no power for lin y2 (y2 = e^{-1e4 t}, relative width >= 2e4): never rejected; this is adjudicated as a powerless test, not a soundness failure (AUDIT.md section 4). The controls in logs/controls.json were run on a pre-final ph2_enclose.py; the auditor's rerun on the final code gives the same verdicts."
8. Unproved assumption 1, "no independent second implementation ... (producer != verifier NOT satisfied)" -> "independent MPFI/Lohner integrator by the auditor (AUDIT.md section 3) confirms t=1 and 10; t>40 is single-implementation".
9. l.189 "quasi-positivity ... NOT needed" (keep) and add: "O6 uses the exact 2x2 spectral norm (prereg: Frobenius); tighter and valid."
10. l.209 "Step history (every 20th step ...)" -> "Step history (a subsample of the every-20th-step history)".
11. Add the prereg anchoring caveat: "PREREG_ITEM.md was first git-committed 2026-11-13 (00328e1), after the launch; the freeze rests on mtimes and a self-hash."

## Remaining unverified
- The enclosure for 40 < t <= 4000 at its stated width: no independent rigorous check.
- The correctness of Arb (Sage 9.5) itself.
- The prose lemma, which is not formalized.
- That the rusty-SUNDIALS binary was built from af4886f2 (path dependency, not pinned).
- The cvRoberts_dns numbers, which were recalled rather than fetched.

## Addendum (main session, 2026-11-14 08:30 UTC): the auditor's t=40 run finished
Written by the main session from the auditor's own output files (`aud_encl.json`, `aud_encl.log`, and the auditor's
`compare.py` run unchanged on `enclosures.json`), not by the auditor. The auditor's Lohner/MPFI integrator reached t = 40
(263,061 steps, 1,360 s wall). At t = 40 its box lies inside the producer's box on all three components, midpoints agree
to about 1.6e-27 (y1, y3) and 8.9e-30 (y2), and the auditor's radii are about 1e7 times narrower (2.4e-25 against
2.8e-18). So the condition stated in the verdict, that the t = 40 run must come out inside the producer's box, is met,
and the verdict stays ACCEPT_WITH_CORRECTIONS. Independent confirmation now covers t = 1, 10 and 40. Still unverified
by any second method: 40 < t <= 4000. (At t = 10 for y2 the producer's midpoint lies outside the auditor's much narrower
box; that is consistent, since the auditor's box is inside the producer's.) Correction 8 should therefore read
"independent check exists for t <= 40".
