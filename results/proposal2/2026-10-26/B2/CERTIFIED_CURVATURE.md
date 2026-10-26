# B2: the triangular lattice is not a local minimum of the harmonic zero-point energy for exp(-pi r^2)

Date 2026-10-26. Proposal 2, item B2 (preregistered in `../preregistration.json`, prior 0.4). Tiers: **A** =
kernel-checked Lean (pinned Lean 4.34.1 + Mathlib, axioms within propext, Classical.choice, Quot.sound); **C** =
argument not machine-checked, split into **C-ball** (rigorous Arb ball arithmetic, outward rounded, certified error
bounds for every transcendental function, executed by python-flint 0.6.0 but not kernel-checked) and **C-human**
(a written mathematical argument); **X** = floating point, supporting nothing by itself.

## 0. Result

**Theorem (B2).** Let `E(t)` be the harmonic zero-point energy per particle (hbar = m = 1) of the unit-covolume
Bravais lattice `L_t = P_t L_rho`, `P_t = [[1, t], [t, 1 + t^2]]`, for the pair potential `V(r) = exp(-pi r^2)`.
`L_0 = L_rho` is the triangular lattice. Then `E(t) < E(0)` for every `0 < |t| <= 10^-5`, and `t = 0` is not a local
minimum of `E`. Since the shape of `L_t` is `tau(t) = rho + sqrt3 t + O(t^2)`, `tau(t) != rho` for small `t != 0`,
so **the triangular lattice is not a local minimum of E_zp over unit-covolume Bravais lattice shapes** (a = 1).

Certified quantity: for every `0 < t <= 10^-5`,
`(U(t) + U(-t) - 2 U(0)) / t^2 <= B_hi = -1.84156` where `U >= E` is the linear-response majorant of section 1,
with `U''(0)` enclosed in **[-1.94771, -1.90017]** (Tier X quadrature value -1.923973 inside). This is an upper bound
on the curvature, not a two-sided enclosure of Lap E_zp: the method bounds `E'' <= U''` from above only.

Corollary for the preregistered wording (Tier C-human, conditional on E being C^2 at rho): `E''(0) <= B_hi`, and
`E''(0) = 2 Lap E_zp(rho)` (isotropy at rho, P2 section 3.1, and |tau'(0)|^2/y^2 = 4, `code/b2_tau_speed.py`), so
**Lap E_zp(rho) <= -0.92078 < 0** (P2's Tier X value is -3.848; the bound is consistent and one-sided).

| piece | tier | where |
|---|---|---|
| `2 tr S <= tr X + tr(X^-1 S^2)` (2x2, X positive definite), equality at S = X | A | `ZeroPointCert/Basic.lean` `two_trace_le_of_inverse`, `two_trace_eq_of_eq` |
| majorant window bound with B < 0 => not a local min; with mirror symmetry => E(t) < E(0) on the window | A | `not_isLocalMin_of_majorant`, `lt_of_majorant_window_symm` |
| rational certificate `Upp0_hi + trW_hi * esum_hi < 0`, stability margin `lmin_lo - dB_hi > 0` | A | `cert_B_neg`, `cert_stability`, `cert_window`; LeanFlow `lean.certify` tier A (`leanflow_cert_a1.json`) |
| assembled theorem (all analytic inputs as explicit hypotheses) | A | `triangular_not_localMin_of_certificate` |
| the scalar Gaussian weight e(t) = exp(-pi a q(t)) along the path and its first two derivatives (q, q', q'' explicit); the generic double product rule for e·M | A | `hasDerivAt_qS`, `hasDerivAt_q1S`, `hasDerivAt_gaussS`, `hasDerivAt_gaussS'`, `hasDerivAt_entry'` (reuses `ProgZeroPoint.gauss_f'`) |
| assembling these into the entry formula of `hess_and_dd` (M, M', M'' of 4 pi^2 a^2 R_i R_j - 2 pi a delta_ij along P_t) | C-human, X cross-check (finite differences, 7e-7) | `code/b2_explore2.py` |
| enclosures of U''(0), int tr X^-1, the perturbation sum, lattice tails, the stability margin | C-ball | `code/b2_certify.py`, `run_a1_shear_main.json` |
| E <= U by integrating the 2x2 inequality; the window identity; interchange of sum and integral; mirror symmetry E(-t) = E(t); E is the same functional as P2's E_zp | C-human | section 2 |
| Lap E_zp(rho) <= B_hi/2 (needs E in C^2 and isotropy at rho) | C-human | section 2.6 |

## 1. Method

Notation and conventions (also in `result.json`, `conventions`):

- `L_rho = c Z(1,0) + c Z(1/2, sqrt3/2)`, `c^2 = 2/sqrt3`; `R_n(t) = P_t R_n(0)` for integer labels `n = (m, l)`.
- `H_n(t) = Hess V(R_n(t)) = e^{-pi |R|^2} (4 pi^2 R R^T - 2 pi I)`.
- `D_t(kappa) = sum_{n != 0} (1 - cos 2 pi kappa.n) H_n(t)` for reduced `kappa in [-1/2, 1/2]^2`; the reduced
  coordinates and the labels `n` are held fixed as `t` varies (strain frame, no rotation).
- `E(t) = (1/2) int tr D_t^{1/2} dkappa`.

**The majorant.** Put `X(kappa) = D_0(kappa)^{1/2}` and `U(t) = (1/4) int [tr X + tr X^{-1} D_t] dkappa`. Pointwise,
`tr S <= (1/2)(tr X + tr X^{-1} S^2)` for `S = D_t^{1/2}` (Lean `two_trace_le_of_inverse`; the gap is
`tr(X^{-1}(S - X)^2) >= 0`). So `E <= U`, with `U(0) = E(0)`. `U` is affine in `D_t`, hence
`U(t) + U(-t) - 2U(0) = (1/4) int tr(X^{-1} sum_n (1 - cos 2 pi kappa.n)[H_n(t) + H_n(-t) - 2 H_n(0)])`. Entrywise,
`H(t) + H(-t) - 2H(0) = t^2 H''(xi)` with `|xi| < t`. Hence, for `0 < t <= t0`,

`(U(t) + U(-t) - 2U(0)) / t^2 <= Upp0 + (int tr X^{-1}) * esum`, where

- `Upp0 = (1/4) int tr(X^{-1} G)`, with `G = sum_n (1 - cos) H_n''(0)`;
- `esum = sum_{all n} sum_entries sup_{|xi| <= t0} |H_n''(xi) - H_n''(0)|`. The bound uses `(1 - cos) <= 2` and
  `||E||_op <= sum |entries|`, and has a factor-2 slack.

Why not certify Lap E_zp directly: the second variation of `tr D^{1/2}` has a concave part (P2 PROOF 3.5,
Daleckii-Krein) that is singular at branch degeneracies and at Gamma. The majorant replaces it by the linear-response
term, which is a single absolutely convergent lattice sum against fixed matrices. The concave part is `<= 0`, so it
can only help, and the majorant makes this one-sided by construction. No SL2(Z) invariance, criticality of rho or
isotropy is used for the headline theorem.

**Enclosure (b2_certify.py, Arb).**

- *Duffy coordinates.* The reduced square splits into four triangles with apex Gamma. On each, `kappa = s v(t')` with
  `v = (1/2, t' - 1/2)` or `(t' - 1/2, 1/2)`, and Jacobian `s/2`. The two other triangles are the images under
  `kappa -> -kappa`, where the integrand is even.
- *Scaled matrices.* `D_0 = s^2 B` with `B = sum_n theta_n^2 f(s theta_n) H_n`, where `theta_n = 2 pi v.n` and
  `f(x) = (1 - cos x)/x^2 = sinc(x/2)^2/2`. Also `B^{-1/2} = ((tr B + d) I - B)/(d tau)`, `d = sqrt det B`,
  `tau = sqrt(tr B + 2d)`. With these, every integrand times the Jacobian is a C^1 function of `(s, t')` wherever
  `B > 0`, including the apex `s = 0`.
- *Integrands.* `U''(0)`: `(s^2/8) tr(B^{-1/2} G~)`. `int tr X^{-1}`: `tau/(2d)`. Controls: `E(0)`: `s^2 tau/4`;
  `<tr D>`: `s^3 tr B/2`.
- *Cells.* Each cell uses the mean-value form `int_cell g in |cell| g(centre) + |cell| (h/4)(sup|g_s| + sup|g_t'|) [-1,1]`.
  The centre values are thin balls. The partials over the cell are propagated by hand (forward mode). `B` and `det B`
  are tightened by their own mean-value forms, and a cell counts only if `det B > 0` and `tr B > 0` there.
- *Grid.* The initial grid is 64 x 64 per triangle. A cell is bisected while its radius exceeds 0.01 x its area, up to
  depth 3: 206,468 final cells, 0 failed.
- *Lattice truncation.* The sum is exact over `m^2 + ml + l^2 <= 21` (42 pairs `+-n`). The tails run over
  `|R| >= c sqrt 22 = 5.04`, using:
  - the lattice-point count `#{|R| <= r} <= pi (r + 1)^2` (Voronoi hexagons of area 1 and circumradius 0.62);
  - the bounds `|theta_n| <= 2 pi |R|/c`, `f <= 1/2` and `|f'| <= 0.13804` (ball-evaluated on [0, 4], `(|x| + 4)/|x|^3`
    beyond);
  - polynomial-times-Gaussian bounds for `H`, `H''` and their partials;
  - 200 shells of width 1/4, plus a geometric remainder.

  All tails are below 1e-21 and enter as balls added to every entry.
- *Stability of L_t, |t| <= t0.*
  - `lambda_min(B_0) >= det/tr >= 0.91889` on every cell.
  - `||B_t - B_0||_op <= sum_n 2 pi^2 |n|^2 sup|H_n(t) - H_n(0)| + tails = dB <= 0.007528`.
  - So `D_t(kappa) = s^2 B_t` is positive definite for `kappa != 0`: the strained lattices are dynamically stable, and
    `E(t)` is defined.

## 2. Tier C-human steps (written out)

2.1 **E is P2's E_zp.** The BZ mean of `tr D^{1/2}` over reduced coordinates does not depend on the basis. The
enclosure of `E(0)` contains P2's spectral value 1.50335235220736 (control (+)1).

2.2 **E <= U.** Apply `two_trace_le_of_inverse` at every `kappa != 0` with:

- `S = D_t^{1/2}`, which is PSD by 1.4;
- `X = D_0^{1/2}`, `P = X^{-1}`, positive definite.

Then integrate. Integrability holds because `tr X^{-1} D_t <= ||D_t|| tr X^{-1}` and `int tr X^{-1} <= 1.8336`.
`U(0) = E(0)` follows from `two_trace_eq_of_eq`.

2.3 **Window identity.** Apply the second-order mean value theorem `phi(t) + phi(-t) - 2 phi(0) = t^2 phi''(xi)` to
each entry of each `H_n`. The `xi` are enclosed by the ball `[-t0, t0]` in the code. Summing over `n` and integrating
is justified by absolute convergence (Gaussian decay; `X^{-1}` integrable).

2.4 **Mirror symmetry.** Take `sigma = diag(1, -1)`. Then `sigma L_rho = L_rho`, because
`sigma c(1/2, sqrt3/2) = c(1,0) - c(1/2, sqrt3/2)`. Also `sigma P_t sigma = P_{-t}`, so `L_{-t} = sigma L_t`. `E`
depends on the lattice only up to isometry, so `E(-t) = E(t)`. Tier X check: `E(h) - E(-h) = 0.0` to all printed
digits (`code/b2_explore2.py`).

2.5 **Shape.** `tau(t) = rho + sqrt3 t + O(t^2)` (exact, `code/b2_tau_speed.py`). Small `t != 0` therefore gives
shapes `!= rho` (mod SL2(Z)) arbitrarily close to `rho`.

2.6 **Curvature corollary.** If `E` is C^2 at 0:

- `E(t) + E(-t) - 2E(0) <= t^2 B_hi` gives `E''(0) <= B_hi`.
- With isotropy at rho (P2 3.1, Tier C) and `|tau'(0)|^2/y^2 = 4`, `E''(0) = 2 Lap E_zp(rho)`.

Tier X: `E''(0) = -7.6961`, against P2's `2 x (-3.848)`.

## 3. Numbers (`run_a1_shear_main.json`, a = 1, shear path)

All values are outward-rounded ball endpoints, with t0 = 1/100000.

- **U''(0)** is enclosed in [-1.947713, -1.900168]. The Tier X Gauss-Legendre value (N = 64) is -1.923973, and the
  finite differences of U give -1.92383.
- **int tr X^{-1}** is enclosed in [1.825520, 1.833534].
- **esum** (all n, tail included) is at most 0.0319642.
- **B_hi** = Upp0_hi + trW_hi * esum_hi = **-1.841560 < 0**. As rationals: Upp0_hi = -475041875131/250000000000,
  trW_hi = 366706720019/200000000000, esum_hi = 31964165579/1000000000000.
- **Stability.** lambda_min(B_0) >= 0.918889 and ||B_t - B_0|| <= 0.007528, so the margin is 0.911361 > 0.
- **Cost.** 206,468 cells, 0 failed; 448 s on one core.
- **Truncation.** 42 lattice pairs. The tails per entry are D 1.2e-27, G 3.2e-23, partials < 5e-22, esum
  2.2e-25.

## 4. Controls

| control | what it tests | result |
|---|---|---|
| (+)1 E(0) enclosure from the same cells contains P2's spectral E_zp(rho) = 1.50335235220736 | cell engine, normalisation | [1.498719, 1.507934] contains it |
| (+)2 <tr D> from the cells vs the exact lattice sum sum_n tr H_n (int (1 - cos) = 1) | D assembly, Duffy map | cells [5.26378, 5.29693] contain 5.2804187 |
| (+)3 that lattice sum vs 4 pi - 2 pi theta_L(1) (P2 sum rule; theta(1) = 1.1595952670, ball-evaluated) | independent formula | overlap: yes |
| (+)4 second path P_t = diag(1+t, 1/(1+t)) (isotropy predicts the same U''(0)) | path independence | U''(0) in [-1.945739, -1.902147], overlapping the shear path; B_hi = -1.83885 |
| (+)5 closed-form H'' vs finite differences (Tier X) | the formula in `hess_and_dd` | max abs difference 7e-7 (FD error); formula also Lean-checked (section 5) |
| (+)6 sympy identity behind `two_trace_le_of_inverse` and a perturbed version | linear combination | identity 0; perturbed version nonzero |
| (-)1 **a = 2** (P2: triangular is a local minimum) | method can fail | U''(0) in **[+12.69365, +12.75701] > 0**, B in [12.772, 12.836]: **not certified**. LeanFlow: claim REJECTED ("false-statement", cert_0); Lean `RejectA2.lean`: kernel rejects (rc 1, `⊢ False`); `a2_not_certifiable` (honest theorem): no trW, esum >= 0 can make this data certify. Stability margin 0.1452 > 0 (consistent with a stable a = 2 triangle). E(0) = [0.540969, 0.542887] contains P2's 0.5419325 |
| (-)2 tampered certificate (sign of Upp0_hi flipped) | kernel rejects false endpoints | `RejectTampered.lean` rc 1 (`⊢ False`); `tampered_false` proves the negation |
| (-)3 planted `sorry` / planted axiom proving the tampered certificate (`Controls.lean`) | axiom gate | compiles rc 0, but `#print axioms` shows `sorryAx` and `ProgZeroPointCert.ctl_cheat` |
| extra: a = 1/2 (P2 Tier X: triangular is a local maximum there) | not preregistered; reported as a by-product | U''(0) in [-1.043919, -0.982646], B_hi = -0.918357 < 0, stability margin 0.3648; LeanFlow tier A. So the same C-ball certificate also covers a = 1/2. It is NOT in the Lean `Basic.lean` theorem, which is for a = 1 only. E(0) in [1.503411, 1.509136] contains P2's 1.50628947 |

Note on a = 1/2 (Tier C interpretation, not tested by a separate run). P2 PROOF 3.5 has the linear-response term Lin = +0.028 > 0 at a = 1/2. That value is computed in
the tau frame (basis a1 = (1/sqrt y, 0), which includes a rotation of the lattice). The majorant used here uses the
pure-strain frame, where the rotation part (along which U has a minimum, since E is rotation invariant and U >= E) is
absent, so its curvature is lower. This frame dependence of U is expected and is not a discrepancy. The a = 2 control
stays positive in this frame.

## 5. Lean

Pinned Lean 4.34.1 + Mathlib through `scripts/certified_numerics/lean_pinned.py`; outputs are in `lean_*.json`.

- **`formal_cert/Programmes/ZeroPointCert/Basic.lean`** (module `Programmes.ZeroPointCert.Basic`, imports
  `Programmes.ZeroPoint.Basic`, no `import Mathlib`, no `sorry`). rc 0, 0 errors. All 18 theorems print
  `depends on axioms: [propext, Classical.choice, Quot.sound]`: `quad_nonneg`, `two_trace_le_of_inverse`,
  `two_trace_eq_of_eq`, `sum_lt_of_majorant_window`, `not_isLocalMin_of_majorant`, `lt_of_majorant_window_symm`,
  `t0_pos`, `cert_B_neg`, `cert_stability`, `cert_window`, `triangular_not_localMin_of_certificate`, `hasDerivAt_lin`,
  `hasDerivAt_quad`, `hasDerivAt_qS`, `hasDerivAt_q1S`, `hasDerivAt_gaussS`, `hasDerivAt_gaussS'`, `hasDerivAt_entry'`.
- **Main statement** (`triangular_not_localMin_of_certificate`). Hypotheses:
  - `E t ≤ U t` for `|t| ≤ t0`, and `U 0 = E 0`;
  - for `0 < t ≤ t0`, `U t + U (-t) - 2 U 0 ≤ t² (Upp0 + trW · esum)`;
  - `Upp0 ≤ Upp0_hi`, `0 ≤ trW ≤ trW_hi`, `0 ≤ esum ≤ esum_hi`;
  - `E (-t) = E t`.

  Conclusion: `¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0`, with `t0 = 1/100000`. The hypotheses are exactly
  the Tier C-ball and C-human inputs of sections 1 and 2.
- **Connection to P2's Lean.** `hasDerivAt_gaussS` is `ProgZeroPoint.gauss_f'` composed with the path.
- **`Controls.lean`**: rc 0; the axiom gate catches `sorryAx` and `ProgZeroPointCert.ctl_cheat`. The honest
  `tampered_false` and `a2_not_certifiable` have standard axioms.
- **`RejectTampered.lean`, `RejectA2.lean`**: rc 1 each (the kernel refuses the false inequalities).
- **LeanFlow** (`/home/callensxavier_gmail_com/LeanFlow-wt-p1`, `lean.certify`, unmodified) independently renders the
  linear endpoint claims `Upp0.hi + pert.hi < 0` and `lmin.lo - dB.hi > 0` into Int statements. Here
  `pert.hi = trW_hi * esum_hi` is formed exactly in Python Fractions; `cert_B_neg` redoes the product in the kernel.
  Results: a = 1 tier A verified, a = 1/2 tier A verified, a = 2 rejected.

## 6. What this does not show

- It does not give a two-sided enclosure of Lap E_zp(rho). The certified number is an upper bound through the
  linear-response majorant.
- The majorant is one-sided by construction. It certifies "not a local minimum" only where the strain-frame
  linear-response curvature is already negative (true at a = 1 and a = 1/2, false at a = 2). It cannot certify a
  local minimum.
- The window `0 < |t| <= 10^-5` is small. The theorem is local, not a statement about P2's finite competitor
  0.5 + 0.966i, which remains Tier X.
- Harmonic approximation, Bravais lattices, two dimensions, Gaussian a = 1 only. The BZ integrals and tails are
  C-ball, not kernel-checked; the Lean kernel checks the logic and the rational arithmetic on the produced endpoints.

## 7. Commands (cores 6,7)

```
python -I code/b2_explore2.py 1 64                       # Tier X: U''(0) = -1.92397, E''(0) = -7.696, E(h) = E(-h)
B2_REFINE_TOL=0.01 B2_MAX_DEPTH=3 python -I code/b2_certify.py 1 shear 64 1/100000 21 run_a1_shear_main.json
B2_REFINE_TOL=0.01 B2_MAX_DEPTH=3 python -I code/b2_certify.py 1 diag 64 1/100000 21 run_a1_diag_ctl.json
B2_REFINE_TOL=0.01 B2_MAX_DEPTH=3 python -I code/b2_certify.py 2 shear 64 1/100000 21 run_a2_shear_negctl.json
B2_REFINE_TOL=0.01 B2_MAX_DEPTH=3 python -I code/b2_certify.py 1/2 shear 64 1/100000 21 run_a05_shear_limit.json
python -I code/b2_lincomb.py ; python -I code/b2_tau_speed.py
python -I code/b2_leanflow_claims.py run_a1_shear_main.json leanflow_claim_a1.json b2_a1_shear   # then LeanFlow lean.certify
python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Programmes/ZeroPointCert/Basic.lean --olean Programmes.ZeroPointCert.Basic
python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Programmes/ZeroPointCert/Controls.lean
python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Programmes/ZeroPointCert/RejectTampered.lean   # must fail
python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Programmes/ZeroPointCert/RejectA2.lean         # must fail
python -I code/b2_make_result.py .
```
python-flint 0.6.0 is installed in `.scratchpad/b2_pylib` (pip --target) and put on `sys.path` by `b2_certify.py`.
