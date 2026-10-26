# Independent adversarial audit of N2 (papers/p3_zero_point_physical)

Auditor: independent AI audit agent (producer != verifier), 2026-10-26. No human has audited this paper.
Scope: main.tex / main.pdf, ledger/, data/, formal_cert/Programmes/ZeroPointPhys/, data/code/n2_certify.py.
Scratch: /tmp/n2audit/. The only files written into the repository are this file and `data/leanchecker_replay.json`.
(Side effect, disclosed: the recompile with `--olean` rewrote `Programmes/ZeroPointPhys/{Taylor,Basic}.olean` in the shared
olean dir `certified_numerics_olean`. Their sources have the sha256 printed in main.tex, and the replay checks these rebuilt oleans.)

## VERDICT: ACCEPT_WITH_CORRECTIONS

The mathematics of the moving-comparison majorant is correct. The certifier is rigorous as far as I could check by
reading it. Two runs reproduce bit for bit (Gaussian a = 2 and Yukawa kappa = 2, see below). The Lean modules recompile
with only the whitelisted axioms, and the leanchecker kernel replay passes (rc 0). Nothing found invalidates the headline
(Tier C). The corrections are statements in the paper that become stale or are overstated. None of them is a mathematical error.

## What I checked, and how

### (1) Mathematics (re-derived by hand)
- **Pointwise majorant.** For X_t positive definite and S_t = D_t^{1/2} symmetric:
  tr(X^{-1}(S-X)^2) = tr(X^{-1}S^2) - 2 tr S + tr X >= 0. Cyclicity gives tr(X^{-1}SX) = tr S, and X^{-1} is positive
  definite while (S-X)^2 is positive semidefinite. So 2 tr S_t <= tr X_t + tr(X_t^{-1} D_t), with equality at t = 0,
  where X_0 = S_0. Correct. It needs D_t >= 0 (checked by the code through det B_u > 0, tr B_u > 0) and X_t > 0 (checked
  through qpd).
- **Sylvester equation.** For symmetric Y, the system QY + YQ = M is the 3x3 matrix [[2q11, 2q12, 0], [q12, q11+q22, q12], [0, 2q12, 2q22]]
  (n2_certify.py:267). Correct, and nonsingular for Q > 0.
- **Exact curvature.** Using (X_t^{-1})' = -X^{-1}YX^{-1} and (X_t^{-1})'' = 2X^{-1}YX^{-1}YX^{-1}, I get
  f''(0) = 2tr(X^{-1}Y^2) - 4tr(X^{-1}Y^2) + tr(X^{-1}D'') = tr(X^{-1}D'') - 2tr(X^{-1}Y^2).
  With D'' = S''X + 2Y^2 + XS'', this equals 2 tr S''. So U2''(0) = E''(0). The general-u formula for phi
  (n2_certify.py:634-635) is d^2/du^2 tr(X_u^{-1}D_u). Correct. The gap U_lin'' - E'' = (1/2) int tr(X^{-1}Y^2) is also correct.
- **Duffy scaling and integrand.** X = sQ and D'' = s^2 B'' give f'' = s phi. The triangle (s, t') -> s(1/2, t'-1/2) has
  Jacobian s/2, so the integrand of M = (1/4) int f'' is s^2 phi/8. The factor 2 for the two mirrored triangles uses
  D(-kappa) = D(kappa). The E(0) integrand is s^2 tr(B_0^{1/2})/4. All correct.
- **Isotropy (Step 4).** The order-3 stabiliser acts on the tangent space at rho as a rotation by 2pi/3, so an invariant
  quadratic form is isotropic, and the gradient vanishes. This is correct only under C^2 and with |tau'(0)| fixed. It is a
  remark: the headline does not use it (Step 8 says so). See NB-6.
- **Mirror symmetry.** sigma = diag(1,-1) maps c(1/2, sqrt3/2) to c(1,0) - c(1/2, sqrt3/2), so it preserves L_rho, and
  sigma P_t sigma = P_{-t}. Correct.
- **Shape.** tau(t) = rho + sqrt3 t + O(t^2), from b/a with a = c(1, t). I verified it to first order.
- **Laplacian side result.** |tau'|^2/y^2 = 3/(3/4) = 4 gives Delta_hyp = E''/2. Correct under the hypotheses stated, and
  the endpoints are M/2.
- **Window lemma (Step 5).** The hand proof is correct, and the Lean proof (Taylor.lean) checks it.
- **Step 7 logic.** It is correct, and not vacuous. Witness: E = U = -(3/2)t^2, U1 = -3t, U2pp = -3, M = yuk1_M_hi.
  These satisfy every hypothesis of `yukawa1_not_localMin_of_certificate`. The conclusion is not trivial, because it
  needs the window lemma and the majorant logic.

### (2) Lean
- **Recompile.** I recompiled with `taskset -c 6,7 python3 scripts/certified_numerics/lean_pinned.py compile`, pinned
  Lean 4.34.1:
  - Taylor.lean: rc 0.
  - Basic.lean: rc 0. All 12 printed declarations depend on exactly [propext, Classical.choice, Quot.sound].
  - Controls.lean: rc 0, and `#print axioms` exposes `sorryAx` (ctl_sorry) and `ProgZeroPointPhysCtl.ctl_cheat` (ctl_axiom).
  - RejectGauss2.lean: rc 1, `unsolved goals ⊢ False`.

  This matches data/lean_*.json. The source sha256 values equal those in main.tex:227-230, and data/lean/ is identical to formal_cert/.
- **Grep.** I searched `formal_cert/Programmes/ZeroPointPhys/*.lean` and `ZeroPointCert/Basic.lean` for
  `skipKernelTC|addDecl|native_decide|implemented_by|extern|unsafe|set_option|axiom|sorry|admit|macro|elab`. The only
  hits are in Controls.lean (the planted controls, as intended) and the `#print axioms` lines.
- **Kernel replay (leanchecker 4.34.1, cores 6,7).**
  - Programmes.ZeroPointPhys.Taylor: rc 0, 68.3 s.
  - Programmes.ZeroPointPhys.Basic: rc 0, 75.8 s.
  - Programmes.ZeroPointCert.Basic (B2, imported): rc 0, 60.0 s.

  The record is in `data/leanchecker_replay.json`. Replay rc 0 says nothing about axioms; the axiom gate is the
  `#print axioms` output above.
- **Faithfulness.** E, U, U1 and U2pp are arbitrary functions ℝ → ℝ. The analysis lives entirely in the hypotheses
  hEU, h0, hd1, hd2, hK and hsym, as the paper says (main.tex:151, 233). The Yukawa-1 and Yukawa-2 theorems differ only
  in the rational constant: nothing in Lean refers to the Yukawa potential. `t0` is B2's `1/100000`, which matches the runs.
- **`gauss2_not_certifiable` is near-trivial.** From M >= positive it concludes ¬ M < 0. The RejectGauss2 control shows
  only that norm_num cannot prove a false rational inequality. Both are honest, but weak as "rejections" (NB-8).

### (3) Certifier code (n2_certify.py, sha256 6fa38af9...; read in full)
- **Second-order cell rule.** On a square of side h, the remainder bound
  (1/2)[E dx^2 sup|g_ss| + 2 E|dx dy| sup|g_st| + E dy^2 sup|g_tt|] = h^2/24 (sup|g_ss| + sup|g_tt|) + h^2/16 sup|g_st|.
  Correct.
- **The u ball.** u is the ball [-t0, t0] in both Hu (the Hessian column) and Qu = Q + u Yt. Treating these as
  independent balls only widens the enclosure. For every fixed u, the centre value and the box jets enclose g_u and its
  second partials. So the cell sum encloses (1/4) int f''(u) for every |u| <= t0 (sup_u int, as erratum (a) says).
  Rigorous.
- **Jets and Taylor tightening.** The jets (Dl2: compose, inv, sqrt, product rule) are correct. The Taylor-form
  tightening at :593-595 uses centre values plus box second partials, then intersects with the box enclosure. Valid.
  The partials of 2θ²f(sθ) in sums/sums2 (:543-545, :565-570) are all correct.
- **f, f', f''.**
  - The monotonicity of f on [0, 2π] is correct (y cos y < sin y on (0, π)).
  - The alternating-series remainders hold for |x| <= 2 (term ratio < 1).
  - The global bounds (|x|+4)/|x|^3 and 1/x^2 + 4/|x|^3 + 12/x^4 = 11/64 at x = 4 are correct.
  - F1 and F2 are computed by ball evaluation on [0, 4].
- **Tails.**
  - The shell count by Voronoi annulus is correct (covolume 1, ρ_V = c/√3).
  - |θ| <= 2π|R0|/c: from |(m,l)|^2 <= 2(m^2+ml+l^2), since (m+l)^2 >= 0.
  - |be| <= √2 θ_max.
  - The weights at :468-474 are conservative: an extra factor of at least 2, and f <= 1/2 is dropped.
  - Complete monotonicity of e^{-κ√q}/√q and of e^{-πaq} gives |g^(j)| decreasing.
  - The far-tail majorant C_j e^{-p√q} holds for q >= 1.
  - Geometric ratio: the polynomial degree is 11 and the code uses 12, which is valid (erratum (b) is correct).
  - Tails are added as balls on every entry and every partial.

  Rigorous.
- **Lambdified constants.** I printed the sources of g^(j). The constants are dyadic (1/2, 1/4, 1/8, 1/16) and the
  exponents are half-integers, so the float literals are exact.
- **Rounding.** M endpoints are exact via `exact_frac` with outward ceil/floor. The lmin, lminu and qpd lower bounds pass
  through `float()` (:695, :759-761) and are not outward-rounded. The margins are >= 0.57, so this is harmless (NB-5).
- **Failed cells.** A cell that fails at maximum depth is skipped in the sum (:684-688), but certification requires
  failed == 0. All certified runs have failed = 0.
- **Merge.** n2_merge.py checks that the parts tile the grid exactly once and sums exact rationals. Part A hi + part B hi
  = 0.0790 - 2.1161 = -2.0371, which matches.
- **Cheap re-runs (core 7, 30-min box).**
  - Gaussian a = 2 negative control: `N2_MAX_DEPTH=1 N2_REFINE_TOL=0.5 ... gauss 2 64 1/100000 21` (202.5 s). Its M, E0,
    U_lin'', cert_rationals, positivity flags and cell counts are **identical** to `data/runs/negctl_g2_N64.json`:
    M in [+3.44960, +4.46308], not certified.
  - Yukawa kappa = 2, which exercises the Yukawa tail branch: `N2_MAX_DEPTH=1 N2_REFINE_TOL=0.5 ... yukawa 2 64 1/100000 150`
    (890.6 s). Its M, E0, U_lin'', tails, cert_rationals (M_hi = -1868541510831/10^12) and positivity flags are
    **identical** to `data/runs/o2_y2_N64.json`; certified_not_local_min = true. Yukawa kappa = 1 (7098 CPU-s) was not
    re-run.
- **Copies.** All 46 files in `data/` (other than data/lean/) are byte-identical to `results/proposal3/2026-10-26/N2/`.
- **Preregistration.** The quote at main.tex:74 is verbatim, including "e.g. Riesz s = 6 or Gaussian a = 2". The priors
  are 0.5 / 0.3. The prereg commit 186039fc (03:40 UTC) predates every run file (earliest 07:32 UTC).
- **LeanFlow.** Yukawa 1, Yukawa 2 and Gaussian 1 are `verified`; Gaussian 2 is `rejected` / `false-statement`, as main.tex:232 says.

### (5) Ledger gate
I re-ran `tools/ledger.py ledger.json --evidence-dir evidence` without writing anything: exit 1, 0 blocking findings,
8 `LEDGER_UNAUDITED_TIER_A` flags. This is identical to `ledger/gate_output.txt`. The headline PZP-C-0012 is Tier C and
depends on A-0003/0004/0007, C-0001..0003 and C-0007..0010. Its tier is consistent.

## BLOCKING

None.

## NONBLOCKING (corrections to make before release)

1. **Stale replay statements.** main.tex:234 ("No leanchecker replay ... is recorded") and main.tex:248 ("No kernel
   replay recorded") are now false. Replace them with: "Kernel replay (leanchecker, Lean 4.34.1, auditor run):
   Programmes.ZeroPointPhys.Taylor rc 0, Programmes.ZeroPointPhys.Basic rc 0, Programmes.ZeroPointCert.Basic rc 0
   (data/leanchecker_replay.json); replay does not check axioms, the #print axioms audit does." Delete the limitation bullet at :248.
2. **Stale audit statements.** main.tex:45 ("has not yet been audited by an independent agent"), :247 ("Not independently
   audited") and :239 ("no independent AI audit") are now false. Replace them with a reference to AUDIT.md (independent AI
   audit, verdict ACCEPT_WITH_CORRECTIONS, no human audit). Fill the `ai_audit` field in ledger/build_ledger.py the way B2
   did, and re-run the gate. The `LEDGER_UNAUDITED_TIER_A` flags remain, because they ask for a person.
3. **Riesz 4 overstated.** main.tex:209 ("the triangular lattice *is* a local minimum of E_zp for s = 4"), main.tex:58
   ("local statement false"), main.tex:244 ("Riesz 4 is a local minimum") and the publication_meta.json description
   ("the local statement is false") present a one-path finite-difference curvature (Tier X) as a fact. Reword all of them
   to: "Tier X evidence (finite-difference E''(0) = +2.754 along the shear, cutoff 40/100) that ρ is a local minimum for
   s = 4; not certified in either direction". Keep "prereg error" only as "the prereg item appears to conflate global and
   local refutation".
4. **No quantum-transition implication.** The paper never claims a transition, which is good, but it should say why there
   is none. Add one sentence to the Limitations (main.tex:246): "The result concerns E_zp alone. The classical energy has
   positive curvature at ρ, so nothing follows for E_cl + ħE_zp at small ħ, and no structural transition is claimed."
5. **Positivity rationals are decorative in Lean.** Basic.lean:155-160 and :173-179: `yuk*_lmin_lo`, `yuk*_lminu_lo` and
   `yuk*_qpd_lo` are proved positive, but no theorem consumes them. The `*_not_localMin_of_certificate` theorems use only
   `yuk*_cert.1`, and positivity enters only through the hypothesis `hEU`. State this at main.tex:146/151 and in
   PZP-A-0003/0004. Also note that these three lower bounds go through `float()` (n2_certify.py:695, :759-761) and are
   therefore rounded to nearest, not outward. With margins >= 0.57 this is harmless; say so in Section 4 or fix it with
   `lower_frac` kept as a Fraction.
6. **Step 4 wording.** main.tex:120: "E''(0) does not depend on the strain direction ... as good as any other" holds only
   if E_zp is C^2 at ρ and the paths are normalised to the same |τ'(0)|. Add "(assuming E_zp is C^2 at ρ, for paths with
   equal |τ'(0)|; not used by the headline)".
7. **Endpoint differentiability gap.** `hd1`/`hd2` at u = ±t0 (Basic.lean:186) need U_2 to be differentiable on an open
   neighbourhood of ±t0. The positivity checks cover only the closed window |u| <= t0. The gap is closed by continuity,
   because the margins are strict, but say so in PZP-C-0009 / main.tex:132.
8. **Weak negative controls in Lean.** `gauss2_not_certifiable` (Basic.lean:211) and RejectGauss2.lean only show that a
   positive rational is not negative. main.tex:188-189 should say that the substantive negative control is the certifier
   run (M_lo > 0), and that the Lean and LeanFlow rejections are arithmetic sanity checks.
9. **Wrong ledger ID.** main.tex:72 tags the Hessian formula H = 2g'I + 4g''RR^T with `PZP-C-0010`, but that ID is the
   mirror/shape claim. Use the correct ID or drop the tag.
10. **"Classically optimal" source.** Title (main.tex:31-32) and abstract (:49) state classical optimality unconditionally,
    citing H2, which is itself conditional. Either add "(H2, conditional)" or also cite Montgomery (1988, minimality of
    the triangular lattice for lattice theta functions). Montgomery's result covers e^{-κr}/r among lattices, because it
    is completely monotone in r^2. Check that before citing it.
11. **P2 c-to-Laplacian factor.** main.tex:216-217: the conversion "c = -0.39 (about -1.55 in this normalisation)" (factor
    about 3.97) is asserted, not derived. Give the formula, or drop the comparison and keep only the Tier X E''/2 values.
12. **Docstring errata.** The docstring errata (a) and (b) at main.tex:250 are correct. Also correct the docstring of
    `tail_bounds` (n2_certify.py:455, "1 + 4 + 4 = 9"), which is the same erratum, in a later code version. The hash
    pins this version, so do not edit it in place.

## Replay rc

leanchecker replay: rc 0 (Taylor, Basic, and B2's ZeroPointCert.Basic). Details in `data/leanchecker_replay.json`.
