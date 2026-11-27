# N1: zero-point classification for Gaussian potentials (certified signs of the exact curvature)

Date 2026-10-26. Proposal 3, item N1 (preregistered in `../preregistration.json`; priors N1a 0.5, N1b inside 0.45,
N1b outside 0.3, full iff theorem 0.25). Builds on B2 (doi:10.5281/zenodo.23655392) and P2. Tiers as in B2:
**A** = kernel-checked Lean (pinned Lean 4.34.1 + Mathlib, axioms within propext, Classical.choice, Quot.sound);
**C-ball** = rigorous Arb ball arithmetic (python-flint 0.6.0, 96 bits, outward rounded), not kernel-checked;
**C-human** = written argument; **X** = floating point only.

## 0. Result

Let `F(a, t) = d^2/dt^2 E_zp(L_t)` be the exact second variation of the harmonic zero-point energy (hbar = m = 1)
along the unimodular shear `L_t = P_t L_rho`, `P_t = [[1, t], [t, 1 + t^2]]`, for `V(r) = exp(-pi a r^2)`
(B2's setting). Window `|t| <= t0 = 10^-8`. Certified (Tier C-ball enclosures, kernel-checked logic and signs):

**N1a, root enclosures.** `a -> F(a, 0)` has a zero in each of

- **a- in (0.3745, 0.379)**: `F(0.3745, t) in [0.0177, 0.0949] > 0` and `F(0.379, t) in [-0.0978, -0.0235] < 0`
  (thin points, N = 64);
- **a+ in (1.579, 1.583)**: `F(1.579, t) in [-0.0423, -0.0195] < 0` and `F(1.583, t) in [0.0075, 0.0303] > 0`.

P2's Tier X roots 0.37668 and 1.58148 lie inside. Existence uses continuity of `a -> F(a, 0)` (Tier C-human).
Uniqueness is NOT certified (no sign of `d_a F` was certified on the enclosures).

**N1b, signs on whole a-intervals (every a in the interval, every |t| <= t0).**

| a-range | sign of F | how | records |
|---|---|---|---|
| **[0.425, 1.579]** | **F < 0** (inside) | chained intervals, Lean `segment_neg0` | 71 |
| **[1.584, 4]** | **F > 0** (outside) | chained intervals, Lean `segment_pos0` | 103 |
| [0.381, 0.383] | F < 0 | one interval | 1 |
| thin points 0.33, 0.35, 0.36, 0.37, 0.372, 0.3745 | F > 0 (outside, left of a-) | thin points | 6 |
| thin points 0.379, 0.381, 0.383, 0.39, 0.40, 0.42, 0.45, 0.5, 0.55 | F < 0 | thin points | 9 |
| thin points 1.57, 1.576, 1.579 / 1.583, 1.584, 1.587, 1.593 | F < 0 / F > 0 | thin points | 7 |

Consequently (a direct consequence of `segment_neg0`, `segment_pos0` and the 1.583 record, not separately kernel-checked) every zero of `a -> F(a, t)` in [0.425, 4] lies in (1.579, 1.584) minus {1.583}.
NOT certified: whole intervals in [0.33, 0.3745] (left of a-), in (0.383, 0.425) (inside, near a-), and anything
below 0.33; thin points a = 0.25 and 0.30 failed (det B > 0 could not be certified on 104 resp. 9 cells near Gamma at
refinement depth 2: the long-wave shear mode is soft there). So the preregistered full "iff" theorem on a compact
range is obtained **on the right of the window only** ([0.425, 4]); on the left of a- only thin points are certified
(kill rule: best certified sub-intervals reported).

**Physical reading (tiers).**

- *Inside, not a local minimum (Tier A logic + C-ball + C-human):* for every a in [0.425, 1.579] (and at each certified
  inside point), along the shear path the triangular lattice is not a local minimum of E_zp and
  `E(a, t) < E(a, 0)` for `0 < t <= 10^-8` (Lean `segment_neg0_path`, `along_path`). C-human inputs: E is C^2 in t on
  the window with second derivative F (differentiation under the BZ integral: the Duffy integrand is jointly smooth and
  certified bounded on the compact domain because det B > 0 is certified everywhere), and the mirror symmetry
  `E(-t) = E(t)` (B2 section 2.4). Since `tau(t) = rho + sqrt3 t + O(t^2)` (B2 2.5), this is "not a local minimum
  over unit-covolume lattice shapes". No criticality or isotropy is used.
- *Outside, strict local minimum (Tier A along the path; Tier C-human over shapes):* for every a in [1.584, 4] (and at
  the certified outside points) `E(a, 0) < E(a, t)` for `0 < |t| <= 10^-8` along the path (Lean `segment_pos0_path`).
  The step to a **strict local minimum over unit-covolume lattice shapes** additionally needs, all Tier C-human:
  E_zp of class C^2 near rho; rho critical and the Hessian isotropic (order-3 stabilizer; P2 3.1, whose Lean has the
  algebra `rot120_comm_symm`, `rot120_fixed_vec`); then `F(a, 0) = 2 Lap E_zp(rho)` (B2 2.6) and `F > 0` gives a positive
  definite Hessian, hence a strict local minimum (second-derivative test in 2D, not formalised).
- Equivalently `c(a) = Lap E_zp/4 = F(a, 0)/8` (P2's curvature) is certified negative on [0.425, 1.579], positive on
  [1.584, 4] and at the left points, with the two sign changes in the stated enclosures.
- **The unrestricted iff for all a > 0 is false**: P2 finds another sign change near a ~ 0.123 (c(0.1) < 0), and P2's
  values at a = 6, 8 are precision-flagged. Nothing here concerns a < 0.33 or a > 4.
- Harmonic approximation, Bravais lattices, two dimensions, Gaussian family only, local statements only.

## 1. The quantity: the exact second variation (not B2's majorant)

Setting as B2: `L_rho` the unit-covolume triangular lattice, `P_t = [[1, t], [t, 1 + t^2]]` (det 1), `L_t = P_t L_rho`,
`H_n(t) = Hess exp(-pi a |P_t R_n|^2)`, `D_t(kappa) = sum_{n != 0} (1 - cos 2 pi kappa.n) H_n(t)`,
`E(a, t) = (1/2) int tr D_t^{1/2} dkappa`. N1 encloses **`F(a, t) = d^2/dt^2 E(a, t)` itself, two-sided**, from the
2x2 identity `tr sqrt(D) = sqrt(tr D + 2 sqrt(det D))`:

- Duffy coordinates as B2 (`kappa = s v(t')`, Jacobian `s/2`, `D_t = s^2 B_t`, `B_t = sum_n theta_n^2 f(s theta_n) H_n(t)`);
  integrand `g = s^2 tau''/4`, `tau = sqrt(T + 2 delta)`, `T = tr B_t`, `delta = sqrt det B_t`,
  `delta'' = det''/(2 delta) - det'^2/(4 delta^3)`, `tau'' = (T'' + 2 delta'')/(2 tau) - (T' + 2 delta')^2/(4 tau^3)`,
  with `B', B''` from the closed forms of `H_n', H_n''` (B2's Lean `hasDerivAt_*` cover the scalar pieces).
- Why not B2's majorant: `U'' >= E''` and the gap is large (`code/n1_explore.py`, Tier X, N = 64,
  `runs/explore_tierX_N64.txt`): `U''(0) < 0` at a = 0.5, 0.7, 1 and > 0 at the other 14 values, so its sign changes lie in (0.4, 0.5) and (1.0, 1.3) (`U'' = -1.013` at 0.5, `+3.877` at 1.3,
  `+2.79` at the root 0.3767, `+8.77` at the root 1.5815). The majorant can never reach the roots.
- Tier X check of the closed form against finite differences of E (same file): agreement to <= 4.92e-4 (maximum, at a = 2) over all 17 a
  values, e.g. `E''(0) = -7.695875` (closed form) vs `-7.695997` (FD) at a = 1, and `c = E''/8` reproduces P2's c(a)
  (a = 0.25: 0.18806 vs P2 0.188; a = 2: 0.49451 vs 0.495).

## 2. The certifier (`code/n1_certify2.py`, Tier C-ball)

For an a-interval `[a_c - delta, a_c + delta]` (delta = 0 for a thin point) and the window `|t| <= t0 = 10^-8`
(`t` enters as the ball `[-t0, t0]` inside `H_n(t)`), the code returns three balls Q, D, R with

`F(a, t) - (a - a_c) d  in  Q + R`  for some `d in D`, for every a in the interval and every |t| <= t0.

- `Q = sum_cells |cell| g(c, a_c)`, `D = sum_cells |cell| d_a g(c, a_c)`: midpoint sums at the exact cell centre and
  the exact centre `a_c` (thin balls; first-order jets in (s, t', a)).
- `R`: the second-order Lagrange remainder in the three variables (s, t', a) on the convex set cell x a-interval,
  `R_cell in |cell| [ (h^2/24)(g_ss + g_t't') + (h^2/16)|g_st'| [-1,1] + (delta h/4)(|g_sa| + |g_t'a|) [-1,1]
  + hull(0, (delta^2/2) g_aa) ]`; the first-order terms in s, t' integrate to zero over the square cell and the
  first-order term in a is `(a - a_c) d`. The second partials are enclosed by second-order forward-mode jets over the
  cell ball x a-interval x t-window.
- Tightening (essential, else det B > 0 cannot be certified at small a): every quantity is computed twice in lockstep
  (`class P`), a first-order jet at the thin centre and a second-order jet over the ball; after each operation the ball
  value and gradient are replaced by mean-value forms around the centre (`grad in grad(c) + Hess(ball) Delta`,
  `value in value(c) + grad(ball) Delta`, intersected with the naive enclosures). Per-n Gaussian Hessians over the
  a-interval use Taylor forms in a around `a_c`.
- `f(x) = (1 - cos x)/x^2` and its derivatives over balls by centred forms with `|f^(k)| <= 1/((k+1)(k+2))`, from
  `f(x) = int_0^1 (1 - u) cos(u x) du` (sympy residual 0, and 3000 random balls x 11 samples against mpmath,
  0 containment failures: `code/n1_fcheck.py`, `runs/fcheck.txt`).
- Stability: a cell counts only if `det B > 0` and `tr B > 0` are certified on the whole cell ball x a-interval x
  t-window, so `D_t = s^2 B_t > 0` for kappa != 0 (every strained lattice in the window is dynamically stable) for
  every a of the interval. Any failed cell (after refinement) makes the run uncertified; it never enters Lean.
- Lattice tail: one bound T added to every jet component of every entry (`tail_bound`): shells of width 1/4,
  polynomial factors at the outer radius and Gaussian factors at the inner radius (no monotonicity assumed), point count
  `pi (r + 1)^2`, weight bounds for all partials of `theta^2 f(s theta)` up to order 2, a-factor `1 + L + L^2`,
  geometric remainder with the ratio computed (must be < 1). Truncation `QMAX = max(6, ceil(20/a_lo))`.
  (This also fixes two B2 shortcuts flagged by its audit: B2 evaluated the theta weights at the inner shell radius and
  asserted the remainder ratio; here both are computed.)
- Cost driver: small a needs many lattice terms (99 half-terms at a = 0.37, 147 at 0.25) and a nearly singular B near
  Gamma (the long-wave shear mode softens towards a ~ 0.123, P2), and R grows fast with the a-width; this is why the
  left side of a- is certified at thin points only (section 4).
- Positive control on the final engine: the 609-check Tier X cross-check (section 4). All 19 Lean input files were produced by one version of `n1_certify2.py` (single script sha256, equal to the current file). Earlier engine versions, for orientation only: (a = 1, thin point, N = 32, before the lockstep tightening, `runs/v2test2_a.json`): `Q = -7.69410`, `D = 9.3929` against Tier X `E'' = -7.69588`,
  `dE''/da = 9.3927` (`code/n1_explore_da.py`); a = 1 with the first-order engine `code/n1_certify.py` (version before its a-jet extension)
  (N = 64, depth 2): `E''` in [-7.768, -7.623], `E(0)` in [1.49776, 1.50890] contains P2's 1.50335235220736, and the
  majorant `U''(0)` in [-1.9531, -1.8948] overlaps B2's [-1.94771, -1.90017] (`runs/test_a1_N64.json`).

## 3. Lean (pinned Lean 4.34.1 + Mathlib via `scripts/certified_numerics/lean_pinned.py`, cores 4,5)

Files under `formal_cert/Programmes/ZeroPointClass/` (no `import Mathlib`, no `sorry` outside `Controls.lean`).

- **`Basic.lean`** (module `Programmes.ZeroPointClass.Basic`, imports `Programmes.ZeroPointCert.Basic`): rc 0, 0 errors,
  20 theorems, every one `depends on axioms: [propext, Classical.choice, Quot.sound]`:
  `window_upper`, `window_lower` (second-derivative bound on [-t0, t0] gives `E t + E(-t) - 2E 0 <= B t^2` resp. `>=`,
  via Mathlib `concaveOn_of_hasDerivWithinAt2_nonpos` / convexity), `not_localMin_of_curv_neg` (reuses B2's
  `not_isLocalMin_of_majorant`, `lt_of_majorant_window_symm` with U := E), `strict_gt_of_curv_pos`, `covers_of_chain`,
  `mul_le_corners`, `corners_le_mul`, `Encloses.left/right`, `allPos_left/right`, `allNeg_left/right`, `rec_upper`,
  `rec_lower`, `neg_on_of_chain`, `pos_on_of_chain`, `pos_of_mem`, `neg_of_mem`, `root_in_gap`, `root_in_gap'`.
- **`Cert.lean`** (generated by `code/n1_make_cert.py` from the run JSONs, endpoints verbatim): rc 0, 0 errors,
  197 records (113 positive, 84 negative). Kernel-checked by `decide +kernel`: `sign_pos`, `sign_neg` (every corner
  bound has its sign), `brackets_ordered`, `chain_pos0` (`chainFrom (198/125) 4 Lposseg0`), `chain_neg0`
  (`chainFrom (17/40) (1579/1000) Lnegseg0`). All 11 theorems print `[propext, Classical.choice, Quot.sound]`.
  Statements (the hypotheses are exactly the Tier C inputs):
  - `segment_neg0 (F) (h : Encloses F t0 Lneg) : ∀ a, 17/40 ≤ a → a ≤ 1579/1000 → ∀ t, |t| ≤ t0 → F a t < 0`;
  - `segment_pos0 (F) (h : Encloses F t0 Lpos) : ∀ a, 198/125 ≤ a → a ≤ 4 → ∀ t, |t| ≤ t0 → 0 < F a t`;
  - `classification (F) (hp : Encloses F t0 Lpos) (hn : Encloses F t0 Lneg) (hcm : ContinuousOn (fun a => F a 0)
    (Icc 0.3745 0.379)) (hcp : ContinuousOn ... (Icc 1.579 1.583))`: F > 0 on every record of Lpos, F < 0 on every
    record of Lneg, `∃ a ∈ Ioo 0.3745 0.379, F a 0 = 0`, `∃ a ∈ Ioo 1.579 1.583, F a 0 = 0` (bracket points are the
    records r_i with lo = hi; rationals 749/2000, 379/1000, 1579/1000, 1583/1000);
  - `segment_neg0_path (E E' F) (h) (hE : ∀ a t, t ∈ Icc (-t0) t0 → HasDerivAt (E a) (E' a t) t) (hE' : ... HasDerivAt
    (E' a) (F a t) t) (hsym : ∀ a t, E a (-t) = E a t) : ∀ a ∈ [17/40, 1579/1000], ¬ IsLocalMin (E a) 0 ∧ ∀ t, 0 < t →
    t ≤ t0 → E a t < E a 0`; `segment_pos0_path`: `∀ a ∈ [198/125, 4], ∀ t, t ≠ 0 → |t| ≤ t0 → E a 0 < E a t`;
    `along_path`: the same per record (thin points included).
  - `Encloses F t0 L` := for every record and every a in its interval and |t| <= t0 there is `d in [dlo, dhi]` with
    `F a t - (a - a_c) d in [qlo, qhi]` (the engine's affine form).
- Not kernel-checked: the enclosures themselves (C-ball), that F is the second derivative of E_zp along the path,
  differentiation under the integral, the mirror symmetry, continuity in a (C-human), and the 2D step (C-human).
- **LeanFlow** (`/home/callensxavier_gmail_com/LeanFlow-wt-p1`, commit 06084ef, unmodified, `decide_kernel`;
  `code/n1_leanflow.py`): the 197 sign claims on the exact corner bounds: status ok, code verified, tier A,
  `leanflow/leanflow_result_exact.json`; a copy with the first sign planted false: rejected, false-statement, failed
  `[cert_0]` (`leanflow_result_planted.json`).

`#print axioms` verbatim (Cert.lean):

```
'ProgZeroPointClass.sign_pos' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgZeroPointClass.sign_neg' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgZeroPointClass.brackets_ordered' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgZeroPointClass.classification' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgZeroPointClass.along_path' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgZeroPointClass.chain_pos0' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgZeroPointClass.segment_pos0' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgZeroPointClass.segment_pos0_path' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgZeroPointClass.chain_neg0' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgZeroPointClass.segment_neg0' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgZeroPointClass.segment_neg0_path' depends on axioms: [propext, Classical.choice, Quot.sound]
```

## 4. Controls

| control | expected | result |
|---|---|---|
| (-) a = 0.40, just inside the window: must not certify "local minimum" | negative enclosure; Lean refuses `allPos` | F(0.40) in [-0.692, -0.587]; `RejectInside.lean` rc 1 (decide fails); `Honest.lean` proves `allPos [r] = false` and `allNeg [r] = true` (rc 0, standard axioms). Also 0.379, 0.381, 0.383, 0.39 certified negative |
| (-) tampered certificate (real a = 0.372 record, sign of qlo flipped) | rejected | `RejectTampered.lean` rc 1; `Honest.lean` `tampered_not_pos`, `untampered_pos` rc 0 |
| (-) a-intervals straddling each root must certify neither sign | sign "none" | [0.3745, 0.379]: F in [-0.151, 0.147], none; [1.579, 1.583] (N = 64): F in [-0.048, 0.036], none (`runs/ctl_straddle*.json`) |
| (-) planted `sorry` / planted axiom (`Controls.lean`) | compiles but the axiom gate shows them | rc 0; `ctl_sorry` shows `sorryAx`, `ctl_axiom` shows `ProgZeroPointClass.ctl_cheat`; honest `ctl_false` standard |
| (-) LeanFlow planted false sign | rejected | rejected, `[cert_0]` |
| (+) Tier X cross-check: every certified enclosure contains the independent float value E''(0; a) (closed form, Gauss-Legendre N = 32, `code/n1_crosscheck.py`) at a_lo, a_c, a_hi of every run | 0 misses | 609 checks, 0 not contained (`crosscheck_tierX.json`) |
| (+) a = 1 point vs Tier X and vs B2 (section 2) | agree | agree |
| (+) f helpers: integral representation and containment | exact / 0 misses | sympy residual 0; 0 of 33000 samples outside |

Not done: the diag-path cross-check of the full engine (v2 supports the shear path only); B2's majorant code was not
re-run.

## 5. What failed or was superseded (reported, not hidden)

- B2-style a-balls with relative half-width ~2.5% (first engine): det B > 0 not certifiable (B moves ~30% across
  the ball); replaced by the affine form with lockstep tightening.
- Wide a-intervals at large a: on [2.2075, 2.9687] with half-widths 0.013-0.036 the remainder R grew from 4.9 to 73.8
  (`runs/superseded_right_wide.json`, 11 of 12 uncertified); re-run with width 0.025 (`runs/sweep_right2.json`,
  72 of 72 positive). Only the re-runs enter Lean.
- Inside near a-: intervals of width 0.005 below a = 0.425 and of width 0.0025 in [0.3925, 0.4] did not certify
  (R up to 32, or failed cells); [0.42, 0.43] at width 0.01 had R = 1.3e4 (`runs/sweep_inside_lo.json`, not an input).
- Thin points a = 0.25 (147 half-terms, 104 failed cells) and a = 0.30 (9 failed cells) at depth 2.
- Total sweep CPU of the Lean inputs: 13,686 s (cores 4,5; other users' jobs shared core 5 for part of the time).
- Repo guards: `antigravity_guard.py` rc 1 and `test_rigor_guard.py` rc 1, both on pre-existing repo-wide findings (hallucinated imports in other trees, hollow tests in tests/); neither output mentions any N1 file (`guard_antigravity.txt`, `guard_test_rigor.txt`). `pytest tests/` was not run.

## 6. Commands (from `results/proposal3/2026-10-26/N1`, cores 4,5)

```
python -I code/n1_explore.py 64 0.15 0.2 ... 4          # Tier X, runs/explore_tierX_N64.txt
python -I code/n1_explore_da.py 64 0.2 0.3 ...          # Tier X d/da
python -I code/n1_fcheck.py                             # runs/fcheck.txt
python -I code/n1_certify2.py OUT.json N 1/100000000 0 TOL DEPTH A_LO:A_HI ...   # every run JSON in runs/; queues via code/n1_queue.py
python -I code/n1_make_cert.py ../../../../formal_cert/Programmes/ZeroPointClass/Cert.lean cert_summary.json 749/2000 379/1000 1579/1000 1583/1000 <the 19 run files listed in cert_summary.json "inputs">
python -I code/n1_make_controls.py ../../../../formal_cert/Programmes/ZeroPointClass 2/5 93/250 runs/sweep_pts_extra.json runs/sweep_left_pts.json
python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Programmes/ZeroPointClass/Basic.lean --olean Programmes.ZeroPointClass.Basic   # then Cert (--olean), Controls, Honest, RejectInside, RejectTampered
python -I code/n1_leanflow.py leanflow <run files>
python -I code/n1_crosscheck.py crosscheck_tierX.json <run files>
python -I code/n1_make_result.py .
```
