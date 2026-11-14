# N2: certified "the triangular lattice is not a local minimum of the harmonic zero-point energy" for physical potentials

Date 2026-10-26. Proposal 3, item N2 (preregistered in `../preregistration.json`, priors 0.5 per potential, 0.3 all six).
Producer run, not yet independently audited. Tiers as in B2: **A** = kernel-checked Lean (pinned Lean 4.34.1 + Mathlib,
axioms within propext, Classical.choice, Quot.sound); **C-ball** = Arb ball arithmetic (python-flint 0.6.0, outward
rounded, not kernel-checked); **C-human** = written argument; **X** = floating point.

## 0. Result per potential

Statement (as in B2): for the unit-covolume lattice `L_t = P_t L_rho`, `P_t = [[1, t], [t, 1 + t^2]]`, the harmonic
zero-point energy `E(t)` (hbar = m = 1) satisfies `E(t) < E(0)` for `0 < |t| <= 10^-5`, so `t = 0` (triangular) is not a
local minimum of `E`; since `tau(t) = rho + sqrt3 t + O(t^2)`, rho is not a local minimum of E_zp over lattice shapes.

| potential | P2 verdict (GATE.md) | Tier X E''(0) (this item) | B2 majorant U_lin''(0) | N2 result | certified bound |
|---|---|---|---|---|---|
| Yukawa e^{-r}/r (kappa 1) | REFUTED, local MAX (c = -0.39) | -3.107 | Arb: [2.393, 2.464] > 0 | **CERTIFIED** | M in [-4.16483, -2.03704], M_hi = -1018521206953/(5 x 10^11) < 0 |
| Yukawa e^{-2r}/r (kappa 2) | REFUTED, local MAX (c = -0.32) | -2.549 | Arb: [2.688, 2.723] > 0 | **CERTIFIED** | M in [-3.21751, -1.86854], M_hi = -1868541510831/10^12 < 0 |
| dipolar, d = 0.1 | REFUTED, local MAX (c = -0.33) | -2.616 (rc 40 and 100) | +16.6 | not certified | obstacle: r^-3 tail (section 4) |
| dipolar, d = 0.5 | REFUTED, local MAX (c = -0.59) | -4.767 (rc 40 and 100) | +9.26 | not certified | obstacle: r^-3 tail |
| Riesz r^-3 | REFUTED, local MAX (c = -0.30) | -2.439 (rc 40 and 100) | +17.1 | not certified | obstacle: r^-3 tail |
| Riesz r^-4 | REFUTED only by a far competitor (tau = 0.3 + 0.954i); local MIN (c = +0.34) | **+2.754** | +33.2 | not attempted | the local statement is false at Tier X |

Controls (same code, same settings): Gaussian a = 1 (B2's case) certified with M in [-8.23325, -7.15778] (B2 had only
U_lin'' <= -1.84; Tier X E'' = -7.699 inside); Gaussian a = 2 (P2: strict local minimum) gives M in [+3.44960, +4.46308]
and is rejected by the certifier, by LeanFlow (`false-statement`) and by the Lean kernel (`RejectGauss2.lean`, rc 1).

So: **Yukawa kappa = 2 certified; Yukawa kappa = 1 certified; Riesz 3 and both dipolar potentials not certified (obstacle: rigorous
long-range tail); Riesz 4 is not a local counterexample at all (P2's refutation for s = 4 is global, not local).**

## 1. Why B2's certificate fails here, and the fix

B2's linear-response majorant `U_lin(t) = 1/4 int [tr X + tr X^-1 D_t]` (X = D_0^{1/2} fixed) is an upper bound whose
curvature exceeds E'' by the relaxation term `(1/2) int tr X^-1 Y^2 >= 0`. Tier X (`tierx_scan_rc40.txt`): U_lin''(0) > 0
for **all six** N2 potentials (Yukawa +2.4/+2.7, Riesz 3 +17.1, Riesz 4 +33.2, dipolar +16.6/+9.3) although E''(0) < 0 for
five of them. For Yukawa 1 and 2 this is also rigorous: the Arb enclosures of U_lin''(0) are [2.393, 2.464] and [2.688, 2.723] (`runs/o2_y1_merged.json`, `runs/o2_y2_N64.json`).
So B2's method, on any path, cannot certify N2.

**t-dependent comparison matrix.** Let `Y` solve `X Y + Y X = D_0'` (2x2 Sylvester, Cramer) and `X_t = X + t Y`. If X_t is
positive definite, `2 tr D_t^{1/2} <= tr X_t + tr(X_t^-1 D_t) =: f_kappa(t)` (B2's `two_trace_le_of_inverse` with X := X_t),
equality at t = 0. Then `U2(t) = 1/4 int f_kappa(t) dkappa >= E(t)`, `U2(0) = E(0)`, and the pointwise gap is O(t^4), so
**U2''(0) = E''(0) exactly** (check: f'' = 2tr(X^-1YX^-1YX^-1D) - 2tr(X^-1YX^-1D') + tr(X^-1D''), which at t = 0 equals
tr(X^-1 D'') - 2 tr(X^-1 Y^2) = 2 tr (D^{1/2})''). The majorant loses nothing at second order.

**Direction.** At rho the Hessian of E_zp is isotropic (order-3 stabilizer, P2 3.1), so E''(0) does not depend on the
strain direction; since U2 has exactly E's curvature, the shear path of B2 loses nothing for any potential, and no
potential needs a different direction. B2's frame dependence was a property of U_lin only.

## 2. Enclosure (`code/n2_certify.py`, Arb, 80 bits)

- Potential as g(q), q = |R|^2: H = 2 g'(q) I + 4 g''(q) R R^T, t-derivatives up to 2 along R(t) = P_t R_0 with
  g', ..., g'''' from sympy, evaluated in Arb (all constants dyadic; `code/n2_selfcheck.py` prints the sources; closed
  form H', H'' vs finite differences: max error 3e-8, 2e-7).
- Duffy coordinates and scaling as in B2: D_t = s^2 B_t, D_t' = s^2 B1_t, D_t'' = s^2 B2_t, Q = B_0^{1/2},
  Q Yt + Yt Q = B1_0, integrand s^2 phi / 8 with phi = 2 tr(Qi Yt Qi Yt Qi B_u) - 2 tr(Qi Yt Qi B1_u) + tr(Qi B2_u),
  Qi = (Q + u Yt)^-1, **u the ball [-t0, t0]**, t0 = 10^-5. For every fixed |u| <= t0 the cell sum encloses
  M(u) := 1/4 int f_kappa''(u) dkappa; the reported M is an enclosure valid for all such u simultaneously.
  (Erratum to the docstring of `n2_certify.py`: it writes `int sup_u f''`; what is computed is `sup_u int f''`, enclosed
  uniformly in u. The certificate uses the latter, section 3.)
- 18 lattice sums per cell (B, B1, B2 at t = 0 and over the window) via `arb_mat` products; second-order jets in (s, t')
  (forward mode, class `Dl2`) give the second partials over the cell box.
- **Second-order cell rule**: int_cell g = |cell| (g(c) + R), |R| <= h^2/24 (sup|g_ss| + sup|g_tt|) + h^2/16 sup|g_st|
  (Taylor with Lagrange remainder; the linear term integrates to zero). Box values and first partials of the sums are
  tightened by Taylor forms around the centre. (A first-order rule, as in B2, gave widths 10-100x larger.)
- f(x) = (1 - cos x)/x^2 enclosed by monotonicity on [0, 2 pi] (f' < 0 there: x sin x - 2(1 - cos x) =
  2 sin(x/2)(x cos(x/2) - 2 sin(x/2)) < 0); f', f'' by series (|x| <= 2), closed form, or global bounds
  sup|f'| <= 0.13804, sup|f''| <= max(ball sup on [0,4], 11/64); sample check `code/n2_dbg2.py`: 0 violations.
- **Positivity, every cell, every |u| <= t0**: det B_u > 0, tr B_u > 0 (strained lattices dynamically stable; lambda_min
  lower bound `lminu_lo`) and det(Q + u Yt) > 0, tr > 0 (X_u positive definite; `qpd_lo`).
- **Tails** (exponential potentials): exact sum over m^2 + ml + l^2 <= QMAX; beyond, shells of width 1/2 with point count
  <= pi (r + 1/2 + rho_V)^2 - pi (r - rho_V)^2 (Voronoi hexagons, rho_V = c/sqrt3), |g^(j)| decreasing in q (complete
  monotonicity), polynomial factors at the outer radius; beyond r_K = r_tail + 200 an explicit majorant
  |g^(j)(q)| <= C_j decay (sympy coefficient sums for Yukawa) and a geometric series with ratio
  (1 + 2 delta/r_K)^12 e^{-beta delta} < 1 (computed). (Erratum to the docstring: the polynomial degree is <= 1 + 4 + 6 = 11,
  not 9; the bound uses 12, so it is unaffected.) Tails enter as balls on every entry and every partial.

## 3. Logic and Lean (`formal_cert/Programmes/ZeroPointPhys/`)

- `Taylor.lean`: `second_diff_le_of_deriv2_le` - f twice differentiable on [-t, t], f'' <= K there =>
  f(t) + f(-t) - 2 f(0) <= t^2 K (kernel-checked, via `antitoneOn_of_deriv_nonpos`).
- `Basic.lean` (imports `Programmes.ZeroPointCert.Basic` of B2 and `Taylor`):
  `window_of_deriv2` (window bound derived in Lean from U2'' <= M on [-t0, t0]), `not_localMin_of_window_cert`,
  `not_localMin_of_deriv_cert` (reuse B2's `not_isLocalMin_of_majorant`, `lt_of_majorant_window_symm`, `t0`, `t0_pos`),
  `not_certifiable_of_lo_pos`; per potential `yuk2_cert` (M_hi < 0 and the three positivity margins > 0 by norm_num),
  `yukawa2_not_localMin_of_certificate`, `yuk1_cert`, `yukawa1_not_localMin_of_certificate`, `gauss1_cert`, `gauss1_not_localMin_of_certificate` (positive control),
  `gauss2_not_certifiable` (negative control).
- Hypotheses of `yukawa*_not_localMin_of_certificate` = exactly the non-kernel-checked inputs: `E t <= U t` on the
  window (pointwise 2x2 inequality with X_t, needs the positivity checks; C-ball + C-human), `U 0 = E 0`
  (`two_trace_eq_of_eq`), `HasDerivAt U U1`, `HasDerivAt U1 U2pp` on the window with U2pp(u) = 1/4 int f_kappa''(u)
  (differentiation under the integral sign: integrand and its t-derivatives bounded on cells x window; C-human),
  `U2pp u <= M` for |u| <= t0 and `M <= M_hi` (C-ball), mirror symmetry `E(-t) = E(t)` (sigma = diag(1,-1), B2 2.4;
  holds for every radial V). Conclusion: `¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0`.
- C-human, as in B2: E is P2's E_zp (control: E(0) enclosures contain P2's spectral values, below); shape statement
  tau(t) = rho + sqrt3 t + O(t^2).
- LeanFlow (`/home/callensxavier_gmail_com/LeanFlow-wt-p1`, `lean.certify`, tactic `decide`, unmodified; driver
  `code/n2_leanflow.py`) on the run endpoints: M.hi < 0, lmin.lo > 0, lminu.lo > 0, qpd.lo > 0.

Lean compile records: `lean_taylor.json`, `lean_basic.json`, `lean_controls.json`, `lean_reject_gauss2.json`.
All compiled with pinned Lean 4.34.1; `Taylor.lean` rc 0, `Basic.lean` rc 0 (no `sorry`, no `import Mathlib`); every
theorem printed `depends on axioms: [propext, Classical.choice, Quot.sound]`: `second_diff_le_of_deriv2_le`,
`not_localMin_of_window_cert`, `not_certifiable_of_lo_pos`, `window_of_deriv2`, `not_localMin_of_deriv_cert`,
`yuk1_cert`, `yukawa1_not_localMin_of_certificate`, `yuk2_cert`, `yukawa2_not_localMin_of_certificate`, `gauss1_cert`,
`gauss1_not_localMin_of_certificate`, `gauss2_not_certifiable`. LeanFlow: `leanflow_cert_yuk1.json`, `leanflow_cert_yuk2.json`,
`leanflow_cert_gauss1.json` tier A verified; `leanflow_cert_gauss2.json` rejected (`false-statement`, cert_0).

## 4. The algebraic obstacle (Riesz 3, dipolar d = 0.1, 0.5)

Tier X shows the method would apply: E''(0) = -2.439 (Riesz 3), -2.616 (d = 0.1), -4.767 (d = 0.5), unchanged from real-space
cutoff 40 to 100 (`tierx_scan_rc100.txt`), and U2''(0) = E''(0). The obstruction is rigorous control of D:

- Hess r^-3 ~ r^-5. B = D/s^2 near Gamma is the elastic sum sum_n theta_n^2 f H_n ~ sum r^2 r^-5: its real-space tail
  decays only like 1/Rc, because D has a non-analytic |k|^3 term. The shell bound used for Yukawa, applied to V = r^-3
  (`code/n2_riesz3_tail.py`, `riesz3_tail_obstacle.txt`), gives for the annulus [Rc, 2Rc) alone: 818 (Rc 10), 291 (25),
  140 (50), 68.6 (100), 34.0 (200), i.e. about 6800/Rc, against lambda_min(B) >= (2 pi)^2 x 0.39 x 1/4 = 3.8 (Tier X).
  A certificate would need Rc ~ 10^5 (about 3 x 10^10 lattice points per cell evaluation): infeasible.
- The partial s-derivatives used by the cell rule are worse: sum theta^3 f' H ~ sum r^3 r^-5 diverges logarithmically
  termwise near s = 0.
- In P2's normalisation the dipolar potential is r^-3 + O(d^2 r^-5), so one Ewald / Gaussian-mixture treatment of r^-3
  (r^-3 = (pi^{3/2}/Gamma(3/2)) int_0^inf a^{1/2} e^{-pi a r^2} da, split at a*: short part
  Gamma(3/2, pi a* r^2)/(Gamma(3/2) r^3) in real space, long part in reciprocal space with incomplete-gamma transforms)
  would cover Riesz 3 and both dipolar cases, with the remainder (Hessian ~ r^-7) in real space. That requires
  reciprocal-space jets in (s, t', t) and a cancellation-free form of [F(G - xi) + F(G + xi) - 2F(G)]/s^2 for G != 0; it
  was scoped (about 2-3 h of development) and not attempted in this budget. No claim is made for these three potentials.

Riesz 4 (s = 4): Tier X E''(0) = +2.754 > 0 (P2's curvature table: local MIN). "Triangular is not a local minimum" is false
at Tier X, so there is nothing to certify locally; P2 refuted QU-1 for s = 4 only through the finite competitor
tau = 0.3 + 0.954i (a global comparison, not in N2's scope). With no algebraic-path certificate, the Riesz 6 negative
control is not needed and was not run through the certifier (Tier X: E'' = +27.2, U_lin'' = +89.2).

## 5. Numbers

| run | pairs | cells (refined) | seconds | M (window curvature bound) | U_lin''(0) | E(0) enclosure | P2 E_zp in it | lmin_lo / lminu_lo / qpd_lo |
|---|---|---|---|---|---|---|---|---|
| Yukawa 1 `runs/o2_y1_merged.json` = exact merge of `y1_partA.json` (s-index 0-11) + `y1_partB.json` (12-63) (N 64, depth 2, tol 1.0, QMAX 650) | 1173 | 59867 (17225) | 7098 (2 cores, 4918 wall) | [-4.16483, -2.03704] | [2.39298, 2.46426] | [1.765657, 1.766136] | 1.7658983 yes | 0.8776 / 0.8748 / 0.6633 |
| Yukawa 2 `runs/o2_y2_N64.json` (N 64, depth 1, tol 0.5, QMAX 150) | 273 | 26714 (6174) | 650 | [-3.21751, -1.86854] | [2.68830, 2.72310] | [1.459124, 1.459391] | 1.4592747 yes | 0.6769 / 0.6753 / 0.5739 |
| Gaussian 1 (+ctl) `runs/o2_g1_N64d1.json` (QMAX 21) | 42 | 17414 (3074) | 73 | [-8.23325, -7.15778] | [-1.93965, -1.90847] (B2: [-1.94771, -1.90017]) | [1.503147, 1.503478] | 1.50335235 yes | 0.8901 / 0.8896 / 0.6764 |
| Gaussian 2 (-ctl) `runs/negctl_g2_N64.json` (QMAX 21) | 42 | 16682 (2830) | 104 | [+3.44960, +4.46308] | [12.7109, 12.7393] (B2: [12.69365, 12.75701]) | [0.541863, 0.541967] | 0.5419325 yes | 0.1427 / 0.1427 / 0.2668 |

All certificates and controls were produced by the same certifier version, `code/n2_certify.py` sha256 6fa38af9e1043473cc60a2ca7c9bb27b8030c1d64135ec8c320d9f086f9fa0f6 (recorded in every run JSON; Yukawa 1 through the wrapper `n2_certify_part.py`, which imports it unchanged).

Tier X E''(0) from `code/n2_explore.py` (finite differences, N 32, rc 40): Yukawa 1 -3.107, Yukawa 2 -2.549, Gaussian 1
-7.699, Gaussian 2 +3.944: each inside its enclosure.

**By-product (C-human corollary, conditional).** M encloses U2''(u) for every |u| <= t0, in particular E''(0) = U2''(0).
If E_zp is C^2 near rho (rho critical, isotropic Hessian; B2 2.6), Lap E_zp(rho) = E''(0)/2, so Lap E_zp(rho) is enclosed in
[-1.6088, -0.9343] (Yukawa 2), [-4.1166, -3.5789] (Gaussian 1; P2 Tier X -3.848 inside) and [+1.7248, +2.2315] (Gaussian 2;
two-sided, which B2's method could not give). For Yukawa 1: [-2.0824, -1.0185] (P2's c = -0.39 corresponds to Lap ~ -1.55, inside; for Yukawa 2 P2's c = -0.32 gives ~ -1.27, inside). Not kernel-checked.

## 6. Controls

| control | result |
|---|---|
| (+) Gaussian a = 1 through the new code | certified, M_hi = -7.15778; LeanFlow tier A; Lean `gauss1_cert` |
| (+) U_lin''(0) of the new code vs B2's independent code (a = 1, a = 2) | [-1.93965, -1.90847] within B2's [-1.94771, -1.90017]; [12.7109, 12.7393] within [12.69365, 12.75701] |
| (+) E(0) enclosures contain P2's spectral E_zp | yes for Gaussian 1, 2, Yukawa 2 and Yukawa 1 |
| (+) closed-form H', H'' vs finite differences (Tier X) | max 3e-8 / 2e-7 (`n2_selfcheck.py`) |
| (+) f, f' enclosures vs float samples | 0 violations (`n2_dbg2.py`) |
| (-) Gaussian a = 2 (P2: strict local minimum) | M in [+3.4496, +4.4631] > 0: not certified; LeanFlow `rejected` / `false-statement` (cert_0); `RejectGauss2.lean` rc 1 (`⊢ False`); `gauss2_not_certifiable` (standard axioms) |
| (-) planted `sorry` and planted axiom (`Controls.lean`) | `Controls.lean` rc 0, but `#print axioms` shows `sorryAx` (ctl_sorry) and `ProgZeroPointPhysCtl.ctl_cheat` (ctl_axiom): caught by the axiom gate |
| (-) first Yukawa 1 attempt (QMAX 450, depth 1) | M in [-15.80, +9.60]: correctly NOT certified (cell widths near Gamma); kept in `runs/o2_y1_N64.json`. A second single-core attempt (QMAX 650, depth 2, tol 0.3) was stopped after 33 min for time (`runs/o2_y1_N64_q650.log`, no result); the certified run is the split one |

## 7. What this does not show

- Only Yukawa (and the Gaussian controls) are certified; nothing is claimed for Riesz 3, Riesz 4 or the dipolar potentials.
- Local statement on a window 0 < |t| <= 10^-5 along one path, harmonic approximation, Bravais lattices, 2D. P2's finite
  competitors remain Tier X.
- The BZ integrals, lattice sums, tails and positivity checks are C-ball (not kernel-checked); the interchange of
  differentiation and integration and E <= U2 integrated over kappa are C-human. The kernel checks the logic, the 1-D
  calculus step and the signs of the rational endpoints.
- Repository checks (CLAUDE.md): `antigravity_guard.py` rc 1, `test_rigor_guard.py` rc 1, `pytest tests/` rc 2 (28
  collection errors) - all on pre-existing files (`guard_*.txt`, `pytest_tests.txt`); none cites an N2 file.

## 8. Commands (cores 6, 7; worktree root)

```
python -I results/proposal3/2026-10-26/N2/code/n2_explore.py POT PARAM 32 40     # Tier X scan (tierx_scan_rc40.txt; rc 100 too)
python -I .../code/n2_selfcheck.py ; python -I .../code/n2_dbg2.py
N2_MAX_DEPTH=1 N2_REFINE_TOL=0.5 python -I .../code/n2_certify.py yukawa 2 64 1/100000 150 runs/o2_y2_N64.json
N2_MAX_DEPTH=2 N2_REFINE_TOL=1.0 python -I .../code/n2_certify_part.py yukawa 1 64 1/100000 650 0,1 0 12 runs/y1_partA.json   # core 6
N2_MAX_DEPTH=2 N2_REFINE_TOL=1.0 python -I .../code/n2_certify_part.py yukawa 1 64 1/100000 650 0,1 12 64 runs/y1_partB.json  # core 7
python -I .../code/n2_merge.py runs/o2_y1_merged.json runs/y1_partA.json runs/y1_partB.json
N2_MAX_DEPTH=1 N2_REFINE_TOL=0.5 python -I .../code/n2_certify.py gauss 1 64 1/100000 21 runs/o2_g1_N64d1.json
N2_MAX_DEPTH=1 N2_REFINE_TOL=0.5 python -I .../code/n2_certify.py gauss 2 64 1/100000 21 runs/negctl_g2_N64.json
python -I .../code/n2_leanflow.py runs/o2_y2_N64.json n2_yukawa2 leanflow_claim_yuk2.json leanflow_cert_yuk2.json   # etc.
python -I .../code/n2_riesz3_tail.py
taskset -c 6,7 python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Programmes/ZeroPointPhys/Taylor.lean --olean Programmes.ZeroPointPhys.Taylor
taskset -c 6,7 python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Programmes/ZeroPointPhys/Basic.lean --olean Programmes.ZeroPointPhys.Basic
taskset -c 6,7 python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Programmes/ZeroPointPhys/Controls.lean
taskset -c 6,7 python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Programmes/ZeroPointPhys/RejectGauss2.lean   # must fail
python -I .../code/n2_make_result.py results/proposal3/2026-10-26/N2
```
python-flint 0.6.0 from `.scratchpad/b2_pylib` (B2). `code/n2_debug_cell.py`, `n2_dbg3.py` are debugging aids.

`runs/explore_*`, `runs/o2_g1_N32*`, `runs/o2_g1_N64.*`, `runs/o2_y2_N32.log` are exploratory runs of earlier code versions (first-order cell rule, or before the f-enclosure fixes); they support nothing.
