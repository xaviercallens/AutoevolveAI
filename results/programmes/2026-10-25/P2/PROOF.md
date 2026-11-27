# P2 gate G2: QU-1 refuted. Independent verification, mechanism, and the parts that are proved

Date 2026-10-25. Lane P2 (zero-point optimality). Input: `GATE.md` (G1, verdict REFUTED, Tier X).

Tiers used below: **A** = kernel-checked Lean (pinned Lean 4.34.1 + Mathlib, axioms within propext, Classical.choice,
Quot.sound); **L** = cited literature, pinned to page and statement; **C** = human argument, not machine-checked;
**X** = floating point (supports no claim by itself).

## 0. Verdict and what this file is

**QU-1 stays REFUTED.** QU-1 says the triangular lattice minimises the harmonic zero-point energy E_zp among
unit-covolume planar Bravais lattices for every completely monotone (CM) potential. It is false (Tier X) already for
the Gaussian g(r^2) = exp(-pi r^2), the Montgomery case. G2 reproduces the counterexample with a method that shares
no code or formula with G1 (section 1).

Because the statement is false, **no proof of QU-1 was attempted.** The "proof" part of this gate is limited to:

- the exact finite and algebraic facts behind the curvature analysis (Tier A, section 4);
- an exact sum rule linking the mean-square phonon frequency to theta functions (Tier C identity, verified to 1e-15);
- its consequences from published theorems (Tier L, section 3.3).

The mechanism analysis itself (section 3) is Tier X, with Tier C interpretation. The restricted conjecture QU-1' in
section 5 is Tier C (suggested by Tier X numerics).

No result here rests on openai/math material. The refutation needs only that exp(-pi a r^2) is CM in r^2, which is
elementary.

## 1. Independent verification of the counterexample (Tier X)

### Method (independent of G1)

G1 used a real-space folded sum and uniform k-grids with n^-3 extrapolation, in Rust and in a numpy re-implementation
of the same formula. G2 uses a different formula, a different quadrature and a different stability test
(`scripts/phonon_poisson_check.py`):

- **Reciprocal-space (Poisson) dynamical matrix.** For V = exp(-pi a r^2), with kappa = k/2pi and L* the dual lattice:
  D(k) = (4 pi^2/a) sum_{xi in L*} [(xi+kappa)(xi+kappa)^T e^{-pi|xi+kappa|^2/a} - xi xi^T e^{-pi|xi|^2/a}].
  This is derived by Poisson summation (Tier C). The R = 0 term can be included because 1 - cos 0 = 0.
- **Duffy-transformed Gauss-Legendre quadrature over the Brillouin zone.**
  - The reduced cell [-1/2, 1/2]^2 is split into four triangles with apex at Gamma.
  - The Jacobian s/2 cancels the conical singularity sqrt(D) ~ |k|.
  - The integrand sqrt(lam1) + sqrt(lam2) is evaluated as sqrt(tr D + 2 sqrt(det D)), which is smooth across branch
    crossings.
  - Convergence is spectral: at the triangular point, N = 64 and N = 128 agree to 2.9e-15.
- **Stability.**
  - lam_min(D(k))/|k|^2 is minimised over the zone, using an n = 192 seed grid and Nelder-Mead from the 12 lowest seeds.
    The minimiser is restricted to |k| >= 3e-3 (see the note on round-off below).
  - The long-wave limit is checked by the exact elastic tensor C(t) = (1/2) sum_R (t.R)^2 Hess V(R), evaluated over
    3600 directions with no k-grid (`phonon_elastic_check.py`, section 2).

### Controls

| control | result |
|---|---|
| (+) Poisson D vs explicit real-space sum at 200 random k, all 12 cases | max relative difference 7e-16 to 1.4e-14 |
| (+) exact sum rule: 4 pi a - (4 pi^2/a) sum_{L*} \|xi\|^2 e^{-pi\|xi\|^2/a} vs sum_{R != 0} Lap V(R) | agree to <= 5.9e-15 |
| (+) Duffy <tr D> vs the exact sum rule | <= 2.7e-14 |
| (+) Duffy N = 128 vs uniform grids n = 512, 1024 (centred and shifted) with n^-3 Richardson extrapolation | about 1e-14 at the triangular point and at 0.5 + 0.966i |
| (+) Rust real-space grid at n = 768 (finer than G1's 384), `g2/rust_fine_*.csv` | n^-3 trend; 2.5e-9 from the spectral value at n = 768 |
| (-) planted bug: drop the -xi xi^T term | real-space match broken by a relative 0.03 to 17.7 |
| (-) planted bug: a <-> 1/a in the transform | invisible at a = 1 (self-dual, as expected); broken by a relative 0.9 (a = 0.5) and 7.5 to 9.4 (a = 2) |
| (-) square lattice tau = i, gauss:1 | flagged unstable, min ratio -0.1475 |
| (-) gauss:2, which survived G1, at the gauss:1 competitor shapes | no stable lower lattice: dE_zp = +4.53e-3 at 0.5 + 0.966i; unstable at x = 0.295 and x = 0.3 |

### Results

E_zp from the Duffy-Gauss rule with N = 128. Stability is the minimum of lam_min/|k|^2 over the zone and the exact
long-wave limit.

| potential | tau | E_zp | dE_zp vs triangular | min lam/\|k\|^2 (zone, \|k\| >= 3e-3) | long-wave (exact tensor) | Rust n = 768 E_zp |
|---|---|---|---|---|---|---|
| gauss:1 | 0.5 + 0.866025i (triangular) | 1.50335235220736 | 0 | 0.03222 (zone corner) | 0.23826 | 1.50335234967 |
| gauss:1 | 0.5 + 0.966025i | 1.49027831827965 | **-1.30740e-2** | 0.03493 | 0.10466 | 1.49027831567 |
| gauss:1 | 0.295 + 0.9555i | 1.45212196187 | -5.12304e-2 | 1.317e-4 | 1.317e-4 (marginal) | 1.45212196123 |
| gauss:1 | 0.3 + 0.953939i | 1.45468498145 | -4.86674e-2 | 4.979e-3 | 4.979e-3 | n/a |
| gauss:0.5 | triangular | 1.50628947025 | 0 | 0.01171 | 0.08081 | 1.50628946750 |
| gauss:0.5 | 0.5 + 0.966025i | 1.49997793320 | -6.3115e-3 | 0.01462 | 0.02695 | 1.49997793033 |
| gauss:0.5 | 0.5 + 1.016i | 1.49170696629 | -1.45825e-2 | 1.380e-3 | 1.379e-3 | n/a |

What this establishes (Tier X):

- **The headline counterexample is confirmed.** For gauss:1, tau = 0.5 + 0.966025i, dE_zp = -1.30740e-2. The value
  agrees with G1 to every digit G1 resolved. The lattice is stable with a clear margin (0.035 on the zone, 0.105 at
  long wavelength).
- **The quadrature error is negligible.** It is about 1e-14, so the margin is about 1e12 times the quadrature error.
  The remaining error is modelling: the harmonic approximation.

**Correction to G1's "largest margin" point.** The point tau = 0.295 + 0.9555i (dE_zp = -5.12e-2) is dynamically
stable, but only marginally: its long-wave eigenvalue is lam/|k|^2 = 1.32e-4, which is 0.06 % of the triangular
lattice's 0.238. It sits on the edge of the stability region. The Duffy rule also converges slowly there (N = 96 to
128 changes E_zp by 3.3e-9), but the value agrees with the n = 768 grid and with the 512/1024 Richardson value to
about 1e-10. It should not be the headline; 0.5 + 0.966i is.

**Round-off artefact, recorded.** The first run (`g2/poisson_check_v1_unbounded_optimizer.json`) flagged this point
unstable, with a ratio of -3.2e-5 at |k| = 4.6e-7. That came from round-off: at such small |k| the Poisson D is a
difference of O(1) sums, and lam ~ 1e-17 is below machine precision. The re-run keeps the optimiser at |k| >= 3e-3
and covers smaller |k| with the exact elastic tensor.

## 2. Long-wave stability of every competitor used in a G1 verdict (Tier X, `g2/elastic_check.json`)

G1's long-wave table covered only Gaussian and Yukawa potentials at x = 0.5. G2 computes the exact long-wave limit
min_t lam_min C(t), with C(t) = (1/2) sum_R (t.R)^2 H(R):

- a lattice sum to rc = 200 and 400, plus a continuum tail by quadrature;
- V', V'' from sympy, independent of phonon.rs;
- rc = 200 and 400 agree to <= 1e-6 for every potential, including the 1/r^3-tailed ones.

| potential | competitor tau (used for G1 verdict) | min lam C(t) | triangular | square (negative control) |
|---|---|---|---|---|
| dipolar:0.1 | 0.3 + 0.953939i | 1.6655e-2 | 1.6347 | -0.9727 |
| dipolar:0.5 | 0.3 + 0.953939i | 1.4140e-2 | 1.0763 | -0.6422 |
| gauss:0.5 | 0.5 + 1.016i / 0.5 + 0.966i | 1.379e-3 / 2.695e-2 | 0.08081 | -0.04491 |
| gauss:1 | 0.295 + 0.9555i / 0.5 + 0.966i | 1.317e-4 / 0.1047 | 0.2383 | -0.1475 |
| riesz:3 | 0.3 + 0.953939i | 1.6676e-2 | 1.6674 | -0.9919 |
| riesz:4 | 0.3 + 0.953939i | 2.2578e-3 | 2.8917 | -1.7134 |
| yukawa:1 | 0.3 + 0.953939i | 3.454e-3 | 0.2250 | -0.1343 |
| yukawa:2 | 0.3 + 0.953939i | 2.401e-3 | 0.1753 | -0.1047 |

- All eight refutation competitors are stable at long wavelength. The ones at x = 0.3 have small margins (0.1 % to
  1.5 % of the triangular value).
- The two points G1 had already dropped are long-wave **unstable**: gauss:0.5 at 0.3 + 0.954i (-3.8e-4) and
  yukawa:1 at 0.295 + 0.9555i (-9.5e-4). This agrees with G1 dropping them.
- riesz:3 at 0.5 + 1.036i is long-wave stable (2.4e-5). G1 found it unstable on finer grids, so its instability is at
  finite k.

**Scope limit.** For the dipolar, Riesz and Yukawa points, stability at finite k rests on G1's grids (n up to 384) plus
this long-wave limit. G2 did not run an independent finite-k optimiser for them; the Poisson form is Gaussian-only.
The refutation for "every CM g" needs only one potential, and the gauss:1 case is fully re-verified.

## 3. Mechanism

### 3.1 The triangular point is a critical point with isotropic curvature (Tier A algebra + Tier C glue; Tier X check)

**Statement (Tier C).** E_zp(tau) depends only on the lattice up to rotation, so it is SL2(Z)-invariant. The element
gamma(tau) = (tau - 1)/tau fixes rho = e^{i pi/3}, and gamma'(rho) = rho^{-2} = e^{-2 pi i/3}, a rotation by -120
degrees. For a C^2 invariant function, the chain rule then gives a zero gradient and an isotropic Hessian at rho:

E(tau) - E(rho) = (Lap E/4) |tau - rho|^2 / y^2 + O(|tau - rho|^3), with Lap = y^2 (d_xx + d_yy).

The sign of c = Lap E/4 decides local minimum (c > 0) versus local maximum (c < 0). This c is the quantity G1
tabulated.

**Proved (Tier A).**

- gamma fixes rho: `gamma_fixes_rho`, `rho_sq`.
- gamma'(rho) = 1/rho^2: `hasDerivAt_gamma`.
- rho^2 (-1/2 - i sqrt 3/2) = 1, so 1/rho^2 is the -120 degree rotation: `rho_sq_mul_rot`.
- A symmetric 2x2 matrix commuting with the 120 degree rotation is scalar: `rot120_comm_symm`.
- A vector fixed by that rotation is zero: `rot120_fixed_vec`.

**Not proved.** The invariance and smoothness of E_zp, and the chain rule step, are Tier C.

**Check (Tier X).** At rho, d_xx E_zp = d_yy E_zp to 1e-6 relative, d_xy E_zp is about 1e-9, and the gradient is
about 1e-7, at the O(h^2) level of the stencil (`g2/mechanism.json`).

### 3.2 Exact curvature of any pair energy at a lattice shape (Tier A algebra + Tier C summation)

Let Q = |m + n tau|^2 / y be the squared length of m a1 + n a2.

**Proved (Tier A).**

- The partial derivatives of Q: `hasDerivAt_Q_x`, `hasDerivAt_Q_y`, `hasDerivAt_Qx_x`, `hasDerivAt_Qy_y`.
- Lap Q = 2Q: `lap_Q`.
- |grad Q|^2_hyp = Q^2: `grad_Q`.
- The algebraic identity y^2 [f2 (Q_x^2 + Q_y^2) + f1 (Q_xx + Q_yy)] = Q^2 f2 + 2Q f1 for arbitrary reals f1, f2:
  `lap_comp`.

**Not proved (Tier C).** That this expression equals Lap f(Q) when f1 = f'(Q) and f2 = f''(Q) is the chain rule; it
is not formalised. With it, Lap f(Q) = Q^2 f''(Q) + 2Q f'(Q) = (u^2 f')'|_{u=Q}.

**Consequence (Tier C, chain rule plus termwise differentiation of an absolutely convergent sum).** For any pair
energy F = sum_{R != 0} f(|R|^2):

Lap F = sum_{R != 0} h(|R|^2), with h(u) = d/du (u^2 f'(u)).

The two h used numerically are Lean-checked derivatives:

- `gauss_h`: h(u) = (-2 pi a u + pi^2 a^2 u^2) e^{-pi a u} for f = e^{-pi a u};
- `m2_h`: h(u) = (16 pi^2 a^2 u - 20 pi^3 a^3 u^2 + 4 pi^4 a^4 u^3) e^{-pi a u} for the second-moment density
  f = Lap V = (-4 pi a + 4 pi^2 a^2 u) e^{-pi a u}.

**Positive control of the finite-difference Laplacian (Tier X).** The stencil value of Lap E_static and of
Lap <tr D> agrees with the exact lattice sum of h for a in {0.25, 0.5, 1, 2, 4}:

- to <= 2.5e-10 relative for a >= 0.5;
- at a = 0.25, to 8e-8 relative (absolute 9e-11, on a value of 1.1e-3).

For example, at a = 1, Lap E_static is 0.47652351661 by stencil and 0.47652351667 exact. Montgomery's theorem (Tier L, section 6)
requires Lap E_static(rho) >= 0; all five values are positive.

### 3.3 The phonon sum rule is a theta-function derivative (Tier C identity + Tier L consequences)

Averaging tr D(k) over the zone kills every cos(k.R) with R != 0:

<tr D>_BZ = sum_{R != 0} Lap V(R) = 4 pi a - (4 pi^2/a) S(1/a; L), with S(alpha; L) = sum_{P in L} |P|^2 e^{-pi alpha |P|^2}.

The second form is Poisson summation, using that the dual of a unit-covolume planar lattice is a rotation of it
(Tier C). Both forms agree to <= 5.9e-15 in all 12 cases of section 1.

By Jensen's inequality (concavity of sqrt), E_zp <= E_E := sqrt(<tr D>/2), the "Einstein" bound, with equality only
for a flat spectrum.

**Consequence 1 (Tier L, conditional only on the cited theorem).** For a <= 1, the triangular lattice is a **global
maximiser** of the mean-square phonon frequency <tr D> among unit-covolume lattices, and hence of the Einstein bound.
This follows because Luo and Wei prove that, for alpha >= 1, S(alpha; L) is minimised by the hexagonal lattice
(section 6). The exact identity above turns their minimum into our maximum.

**Consequence 2 (Tier A step + Tier C + Tier L). At a = 1, <tr D> = 4 pi - 2 pi theta(1; L).**

- The abstract step is Lean-checked (`deriv_at_one_of_inversion`): if f(1/alpha) = alpha f(alpha) for alpha > 0, then
  f'(1) = -f(1)/2. Applied to f = theta_L, it gives S(1) = -theta'(1)/pi = theta(1)/(2 pi).
- The Jacobi identity theta_L(1/alpha) = alpha theta_L(alpha) is Tier C (classical, not formalised). The same identity
  is Luo-Wei's Lemma 3.5.
- Checked at five shapes to <= 2e-15 (`g2/sumrule_identity.json`; theta_hex(1) = 1.1595952670).
- With Montgomery's theorem, the triangular lattice is the unique maximiser of <tr D> at a = 1.

**Local version (Tier X).** Lap <tr D>(rho) < 0, so rho is a local maximum of <tr D>, exactly for a < 1.09361 (root by
bisection). This matches Luo-Wei (alpha = 1/a >= 1 gives a <= 1). It also matches Bétermin's assertion, quoted by
Luo-Wei, that hexagonal optimality of S fails for some small alpha (here alpha < 0.914). This is a literature-consistency
control on the code.

**The sum rule alone does not decide the sign of c(a)** (table 3.4). On a in (0.123, 0.377), Lap <tr D> < 0 but
c > 0. On a in (1.094, 1.581), Lap <tr D> > 0 but c < 0.

### 3.4 Curvature c(a) of E_zp at rho for the Gaussian family, and its sign changes (Tier X)

Method: Duffy-Gauss rule with 3 x 48 radial nodes, five-point stencil with h = 2e-3 and 1e-3, Richardson-combined
(`g2/mechanism.json`). Robustness was checked with 3 x 80 nodes (`g2/smalla_check.json`). c agrees with G1's
independent Rust grid values at a = 0.25, 0.5, 1, 2, 4 (G1: +0.19, -0.46, -0.96, +0.49, +0.31).

| a | 0.1* | 0.15 | 0.2 | 0.25 | 0.3 | 0.35 | 0.4 | 0.5 | 0.6 | 0.8 | 1.0 | 1.2 | 1.4 | 1.6 | 1.8 | 2.0 | 2.5 | 3.0 | 4.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c(a) | -0.0062 | +0.0254 | +0.115 | +0.188 | +0.178 | +0.080 | -0.080 | -0.461 | -0.786 | -1.071 | -0.962 | -0.660 | -0.304 | +0.029 | +0.299 | +0.495 | +0.692 | +0.626 | +0.313 |
| Lap <tr D> | -5.6e-10 | -2.8e-5 | -4.7e-3 | -0.084 | -0.51 | -1.67 | -3.78 | -9.90 | -15.5 | -16.4 | -5.99 | +6.28 | +14.8 | +18.3 | +18.1 | +15.7 | +8.05 | +3.14 | +0.31 |

**Sign changes (bisection; robust to node count and stencil step).**

- a1 = 0.37668.
- a2 = 1.58148.
- a0 is about 0.123, uncertain by about 1e-3: the 48- and 80-node rules shift c by 1e-5 there.

**Triangular as a strict local maximum of E_zp.** This holds for **a in (a1, a2) = (0.3767, 1.5815)**, which contains
the refuted gauss:0.5 and gauss:1. The triangular lattice is a local minimum on (a0, a1) and on (a2, 4], which contain
the G1 survivors gauss:0.25, gauss:2 and gauss:4.

Caveats on the range:

- At a = 6 and 8, c is positive (0.034, 0.0025), but the Poisson form loses relative precision when E_zp is tiny, so
  these are flagged, not claimed.
- *For a <= 0.123, the triangular lattice's long-wave shear eigenvalue is <= 1.5e-9 (exact tensor: 1.4e-9 at
  a = 0.1227, 6.6e-11 at a = 0.11, 3.3e-12 at a = 0.1). The lattice is marginal there and the harmonic picture is
  doubtful.

**Independent cross-check of the brackets (Rust real-space uniform grid, n = 768).** The quantity is
E_zp(rho +/- 0.02 along x) - E_zp(rho) (`g2/rust_curv/`):

| a | value | sign |
|---|---|---|
| 0.35 | +4.220e-5 | minimum |
| 0.40 | -4.279e-5 | maximum |
| 1.50 | -7.064e-5 | maximum |
| 1.65 | +5.404e-5 | minimum |

The n = 768 grid error is about 2e-9, so both sign changes are confirmed by the second code.

### 3.5 Decomposition of the curvature: linear response vs concavity (Tier X numbers, Tier C sign)

With Phi(D) = tr D^{1/2} at fixed reduced k, Lap E_zp = Lin + Conc, where:

- Lin = (1/2) < y^2 sum_i tr(Phi'(D) d_i^2 D) >;
- Conc = (1/2) < y^2 sum_i Phi''(D)[d_i D, d_i D] >.

Conc <= 0 by operator concavity of the square root (Tier C), in the Daleckii-Krein form with a diagonal (per-branch)
part and a branch-mixing (cross) part. Lin + Conc reproduces the stencil Lap to <= 2.3e-5.

| a | Lap E_zp | Lin | Conc (diag + cross) | Einstein curvature Lap E_E |
|---|---|---|---|---|
| 0.25 | +0.753 | +9.683 | -8.930 (-0.506 - 8.425) | -0.017 |
| 0.5 | -1.842 | +0.028 | -1.870 (-0.733 - 1.137) | -1.441 |
| 1.0 | -3.848 | -0.799 | -3.048 (-1.189 - 1.859) | -0.921 |
| 2.0 | +1.978 | +6.400 | -4.422 (-1.644 - 2.777) | +6.817 |
| 4.0 | +1.250 | +2.294 | -1.044 (-0.396 - 0.648) | +2.432 |

- **At a = 1, both terms are negative.** 63 % of Lap E_zp comes from the outer Duffy shell s in [2/3, 1] (the zone
  boundary): Lin -0.532, Conc -1.884 there. The long-wave inner shell [0, 1/3] contributes -0.217.
- **At a = 0.25 and 2, a large positive linear-response term beats the concavity term.**

### 3.6 Where the energy is lost in the headline counterexample (Tier X, finite differences, `split_*` in mechanism.json)

For gauss:1, E_zp(0.5 + 0.966i) - E_zp(rho) = -1.3074e-2.

**By branch and by shell.**

- Lower branch: -1.751e-2. By shell: long-wave -1.3e-5, middle -2.53e-3, zone boundary -1.497e-2.
- Upper branch: +4.44e-3.

The loss is a **softening of the lower branch near the zone boundary**, not a long-wave (sound-speed) effect, although
the transverse sound speed also drops (elastic eigenvalue 0.105 vs 0.238).

**By mechanism.** <tr D> falls by 2.03e-2, which moves the Einstein bound by only -3.13e-3 (24 % of the gain). The
remaining 76 % (+9.94e-3 of Jensen gap) is a **wider spread of the spectrum**, i.e. the concavity of sqrt.

For the marginal point 0.295 + 0.9555i, the split is: lower branch -5.74e-2 (outer shell -3.82e-2), and the Einstein
share is 18 %.

**Negative control.** For gauss:2 at 0.5 + 0.966i, <tr D> rises by 5.39e-2, the upper branch gains 2.44e-2, and the
total is +4.53e-3.

**Interpretation (Tier C, not tested separately).**

1. For wide and intermediate Gaussians, the triangular lattice maximises the mean-square phonon frequency. This is an
   exact theta-function statement (Luo-Wei for a <= 1).
2. E_zp is a concave functional of D, so shear deformations that both lower the second moment and spread the spectrum
   (zone-boundary softening of the lower branch) lower E_zp.
3. For a in (a1, a2), this wins over the linear stiffening term, and the triangular point becomes a local maximum.
4. QU-1 also fails structurally: E_zp is not a pair sum (it is a trace of a square root of a lattice sum). The
   Bernstein-mixture argument that transfers Montgomery's theorem from Gaussians to all CM potentials is linear in V
   and does not apply.

## 4. Lean (Tier A): `formal_cert/Programmes/ZeroPoint/`

**`Basic.lean`.** Module `Programmes.ZeroPoint.Basic`, sha256
`7d59f1817767ae64cc37d017348e1eb5f5b9ed83ed068086fae839baff0d64f0`. `Controls.lean` has sha256
`c725bdcba93362681c58f65eaf00d717eea37254c10f364bab4e039d645acd90`.

- 19 theorems:
  - Q derivatives and Laplacian identities: `hasDerivAt_Q_x`, `hasDerivAt_Q_y`, `hasDerivAt_Qx_x`,
    `hasDerivAt_Qy_y`, `lap_Q`, `grad_Q`, `lap_comp`;
  - Gaussian and second-moment formulas: `gauss_f'`, `gauss_h`, `m2_f'`, `m2_h`;
  - symmetry at rho: `rot120_comm_symm`, `rot120_fixed_vec`, `sqrt3_half_sq`, `rho_sq`, `gamma_fixes_rho`,
    `rho_sq_mul_rot`, `hasDerivAt_gamma`;
  - the inversion step: `deriv_at_one_of_inversion`.
- Compiled with `scripts/certified_numerics/lean_pinned.py compile` (Lean 4.34.1, pinned Mathlib): rc = 0. Output is in
  `g2/lean_basic.json`.
- `#print axioms` gives [propext, Classical.choice, Quot.sound] for all 19, with no sorryAx. The file contains no
  `sorry`.

**`Controls.lean`.**

- Planted `ctl_sorry` and `ctl_axiom` prove the false identity y^2 (Q_xx + Q_yy) = Q (factor 2 dropped).
- The file compiles with rc = 0, as `sorry` does. The axiom audit catches both: `sorryAx`, and
  `ProgZeroPoint.ctl_cheat`.
- `lap_wrong_false` is an honest theorem proving that the planted statement is false (instance m = 1, n = 0, x = 0,
  y = 1).
- Output is in `g2/lean_controls.json`.

**What Tier A certifies.** Tier A certifies these statements only: derivatives of Q and of the Gaussian densities, two
Laplacian identities, the algebraic identity of `lap_comp` (the chain-rule link to Lap f(Q) is Tier C), 2x2 rotation
linear algebra, Möbius facts at rho, and the inversion step.

**What it does not certify.** It does not certify any statement about E_zp, about the lattice sums themselves, or about
the counterexample, which is Tier X.

## 5. Restricted conjecture QU-1' (Tier C; suggested by Tier X, not proved)

**QU-1'.** For g_a(r^2) = exp(-pi a r^2) with **0.15 <= a <= 4**, the triangular lattice is a strict local
minimiser of E_zp among unit-covolume Bravais lattices if and only if a lies outside [a1, a2], with a1 = 0.37668 and
a2 = 1.58148.

Caveats kept outside the statement:

- Below a about 0.123, c changes sign again (c(0.1) = -0.0062 < 0). There the lattice is marginal (shear eigenvalue
  <= 1.5e-9) and the quadrature uncertainty of c is about 1e-5.
- At a = 6 and 8, c > 0, but these values are precision-flagged.

**Global version.** The global version, that triangular is the E_zp minimiser among dynamically stable lattices for
a > a2, is supported only by G1's scan for a = 2 and 4 (567 shapes plus two dense paths). It is open, not claimed.

**Proof route if pursued.** Lap E_zp(rho) has no theta-function closed form, because E_zp is not a pair sum. A proof
would need rigorous bounds on the Lin and Conc integrals, for example by interval arithmetic over the Duffy rule. This
was not attempted within this gate.

## 6. Literature used (Tier L), with what was verified

- **Montgomery's theorem.** Verified as restated in K. Deng and S. Luo, arXiv:2411.17199v1, p. 3, "Theorem A
  (Montgomery 1988). For all alpha > 0, up to rotations and translations, Minima_{z in H} theta(alpha; z) =
  e^{i pi/3}". The original is H. Montgomery, Glasgow Math. J. 30 (1988) 75-85; I did not open the original.
- **S. Luo and J. Wei, arXiv:2302.05042v1.**
  - p. 3, Corollary 1.1: "For any alpha >= 1, min_L sum_{P in L,|L|=1} |P|^2 e^{-pi alpha |P|^2} is achieved at
    hexagonal lattice".
  - p. 12, Lemma 3.5 (W_{1/(2pi)}(1; z) = 0, i.e. S(1) = theta(1)/(2 pi)).
  - pp. 2-3: the quoted assertion of Bétermin (SIAM J. Math. Anal. 48 (2016), Subsection 4.3) that this optimality
    cannot hold for all alpha > 0.
  - Journal version per ref. [27] of arXiv:2411.17199: J. Math. Phys. 65 (2024) 071901.
- **Deng-Luo, arXiv:2411.17199v1, p. 3.** Theorem 1.1 (hexagonal minimises sum |P|^4 e^{-pi alpha |P|^2} for
  alpha >= 3/2) and Conjecture 1.1 (sum |P|^{2k} e^{-pi alpha |P|^2}, alpha >= k). These are related; they are not
  used in an argument here.

**Elenchus citation gate** (`tools/citation_check.py`; `g2/citation_check.json`, `g2/claim_*.json`).

- Method:
  - Source texts were fetched from arxiv.org and extracted with pdftotext.
  - Their sha256 is recorded in each claim.
  - Quotes were copied programmatically from the extraction, located by their headers.
- **ACCEPTED, tier ceiling L** for all three claims: Luo-Wei Corollary 1.1, Luo-Wei Lemma 3.5, and Montgomery's
  Theorem A as restated by Deng-Luo.
- What this does and does not show:
  - The gate certifies that each quotation is faithful to the fetched text.
  - `statement_match = match` is my judgement.
  - Montgomery's theorem is cited via the secondary source.

**Elenchus seed detector** (`tools/elenchus_check.py`; `g2/elenchus_check.json`). It could not run on these Lean
files. It **SKIPPED** both files with exit code 2, "toolchain mismatch: lean-toolchain pins 4.34.0-rc2, `lean`
reports 4.34.1". The files need the pinned openai/math stack (Lean 4.34.1 + Mathlib); under the detector's own
4.34.0-rc2 toolchain, Mathlib is absent and the files do not compile. The axiom audit was therefore done with
`lean_pinned.py` and `#print axioms` (section 4).

**Prior art on E_zp.** One alphaXiv search (keywords: zero-point energy, triangular lattice, lattice energy
minimization, phonon, theta function) returned no paper on lattice-shape optimality of the harmonic zero-point energy.
This is "not found in one search", not a novelty claim.

## 7. rusty-SUNDIALS improvement (made along the way)

Branch `physics/p2-zero-point-optimality-2026-10-25`, worktree `/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-p2`,
commit `6ad3cf7e5e171479d1481e5fd17e7d432aae21d1`. Not pushed.

**`crates/qf-yukawa-crystal/src/phonon_spectral.rs` (new).**

- Gauss-Legendre nodes.
- `GaussPoisson`: the reciprocal-space Gaussian dynamical matrix, with the exact sum rule.
- `ezp_gauss_duffy`: the spectral zone rule, giving E_zp to about 1e-14 instead of the n^-3 grid error.
- `curvature_at_rho_gauss`.

**`lattice_phonon` subcommands.**

- `duffy a x y N`. For example, `duffy 1 0.5 0.966025403784 64` gives 1.490278318279654.
- `curv a N h`. For example, `curv 1 48 0.002` gives c = -0.96198435.

**Tests.**

- 5 new unit tests: Gauss-Legendre exactness; Poisson vs real-space D on grids at three shapes to 1e-12; Duffy vs
  Richardson grids; QU-1 regression dE = -1.3074e-2 with the square lattice as a negative control; sign of c at
  a = 0.25, 1, 2.
- The crate now has 59 passing tests (1 ignored, as before).
- `cargo fmt` is clean, and `cargo clippy --workspace --features experimental -- -D warnings` is clean.

**Python scripts.** `phonon_poisson_check.py`, `phonon_elastic_check.py`, `phonon_mechanism.py`,
`phonon_smalla_check.py`, `phonon_sumrule_identity.py`.

## 8. Caveats

- **Harmonic, Bravais, two-dimensional only.**
  - The harmonic approximation is the modelling assumption behind every number here.
  - Competitors are not stress-free (G1).
  - Anharmonic and quantum-melting effects are outside scope; they are large where the shear eigenvalue is tiny
    (a <= 0.12, or marginal points such as 0.295 + 0.9555i).
- **Finite-k stability for non-Gaussian potentials.** For the dipolar, Riesz and Yukawa competitors, stability at
  finite k rests on G1's grids; G2 adds only the exact long-wave limit (section 2).
- **Coulomb and Keldysh** remain excluded (G1).
- **Tier X vs Tier A.** Nothing in sections 1-3 is kernel-checked. The Lean file certifies only the identities listed
  in section 4.

## 9. Commands (cores 4-7, at most two threads per job)

Python is `/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I`. Scripts live in the rusty worktree under
`crates/qf-yukawa-crystal/scripts/`. Outputs are copied to `g2/`.

```
python -I phonon_poisson_check.py poisson_check.json        # section 1 (2 min)
python -I phonon_elastic_check.py elastic_check.json        # section 2
python -I phonon_mechanism.py mechanism.json                # sections 3.2-3.6 (2 min)
python -I phonon_smalla_check.py smalla_check.json          # robustness of c(a) near the roots
python -I phonon_sumrule_identity.py sumrule_identity.json  # a = 1 theta identity
bash g2/rust_fine.sh ; bash g2/rust_curv.sh                 # Rust n = 768 runs
bin/lattice_phonon duffy 1 0.5 0.966025403784 64 ; bin/lattice_phonon curv 1 48 0.002
python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Programmes/ZeroPoint/Basic.lean --olean Programmes.ZeroPoint.Basic
python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Programmes/ZeroPoint/Controls.lean
```
