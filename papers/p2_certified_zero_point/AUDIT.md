# Independent adversarial audit: B2 (proposal 2, 2026-10-26)

Paper: `papers/p2_certified_zero_point/main.tex` (v1, "The triangular lattice is not a local minimum of the harmonic
zero-point energy for exp(-pi r^2)"). Auditor: a separate Claude Opus agent instance, acting as verifier. The producer and
the verifier are different agents, but both are Claude agents of the same pipeline. No human has reviewed this work.
Date 2026-10-26. Scratch work is in `/tmp/b2audit/`. Files written: this file and
`results/proposal2/2026-10-26/B2/STATEMENT_LOCK.json`.

## VERDICT: ACCEPT_WITH_CORRECTIONS

The headline chain holds up under every check I ran:

- a 2x2 concavity inequality;
- a majorant U >= E with U(0) = E(0);
- a second-difference window bound with a certified negative constant;
- mirror symmetry;
- restriction from lattice shapes to one continuous path.

The Lean part recompiles, the axiom set is the whitelist, and planted holes propagate to the headline. The ball-arithmetic
certificate keeps its sign when I rerun it with much coarser cells, and an independent floating-point reimplementation
agrees with every certified enclosure. Tiers, the deviation from the preregistration and the non-preregistered a = 1/2
result are all labelled honestly.

Two blocking items must be fixed before release. Both are text corrections and neither changes the result:

- status text that this audit makes false;
- one incorrect mathematical sentence that justifies the deviation from the preregistration.

---

## 1. Lean: recompilation, axioms, controls (done by the auditor)

All runs use the pinned stack via `taskset -c 6,7 python3 scripts/certified_numerics/lean_pinned.py compile ...`.

| file | auditor rc | result |
|---|---|---|
| `Basic.lean` (`--olean Programmes.ZeroPointCert.Basic`) | 0 (10.5 s) | all 18 `#print axioms` = `[propext, Classical.choice, Quot.sound]` |
| auditor file `/tmp/b2audit/Programmes/Audit/Check.lean` (imports Basic) | 0 | see below |
| `Controls.lean` | 0 | `ctl_sorry` -> `sorryAx`; `ctl_axiom` -> `ProgZeroPointCert.ctl_cheat`; `tampered_false`, `a2_not_certifiable` whitelist only |
| `RejectTampered.lean` | **1** | `unsolved goals ⊢ False` (as intended) |
| `RejectA2.lean` | **1** | `unsolved goals ⊢ False` (as intended) |
| auditor `/tmp/b2audit/Programmes/Audit/BasicSorry.lean` (Basic with `cert_B_neg` replaced by `sorry`, renamed namespace, no olean written) | 0 | `cert_B_neg` **and** `triangular_not_localMin_of_certificate` both list `sorryAx` |

What the auditor's own `Check.lean` shows:

- **`#print axioms`.** The following all depend only on `[propext, Classical.choice, Quot.sound]`:
  `triangular_not_localMin_of_certificate`, `two_trace_le_of_inverse`, `two_trace_eq_of_eq`,
  `not_isLocalMin_of_majorant`, `lt_of_majorant_window_symm`, `cert_B_neg`, `cert_window`, `cert_stability` and
  `hasDerivAt_gaussS'`.
- **Planted sorry.** `theorem audit_planted : Upp0_hi > 0 := sorry` compiles with rc 0, and only `#print axioms` exposes
  `sorryAx`. The exit code is therefore not a gate, and the paper says so correctly.
- **Literals.** `Upp0_hi = -475041875131/250000000000` and `t0 = 1/100000` hold by `rfl`.
- **Non-vacuity.** The assembled theorem applies to the explicit instance `E = U = -t^2`, `Upp0 = -2`, `trW = esum = 0`, so
  its hypotheses are jointly satisfiable.

Planted holes propagate: a `sorry` inside the certificate chain reaches the headline theorem, and the axiom gate catches
it there. The reject files fail for the intended reason, a false inequality that `norm_num` reduces to `False`, and not
for a syntax or import error.

Disclosure: my `--olean` compile of `Basic.lean` rewrote `formal_cert/.olean_out/Programmes/ZeroPointCert/Basic.olean`.
That olean was built from byte-identical source (sha256 `0241b6af...`), but the file is outside my two-file write scope.

## 2. Statement adequacy

The elaborated statement (`#check @triangular_not_localMin_of_certificate`; locked in `STATEMENT_LOCK.json`, source-text
sha256 `d6947d201166fcf578e8e2ba130bd1d87057a906df6bc23ecca226af9ba6bd24`):

```
∀ (E U : ℝ → ℝ) (Upp0 trW esum : ℝ),
  (∀ t, |t| ≤ t0 → E t ≤ U t) → U 0 = E 0 →
  (∀ t, 0 < t → t ≤ t0 → U t + U (-t) - 2 * U 0 ≤ t ^ 2 * (Upp0 + trW * esum)) →
  Upp0 ≤ Upp0_hi → 0 ≤ trW → trW ≤ trW_hi → 0 ≤ esum → esum ≤ esum_hi → (∀ t, E (-t) = E t) →
  ¬IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0
```

Every analytic input is an explicit hypothesis. `E` and `U` are arbitrary real functions, so the theorem carries no hidden
physics. The hypotheses, each mapped to where the paper discharges it:

| hypothesis | content | discharged by (tier) |
|---|---|---|
| `hEU` | E <= U on \|t\| <= t0 | Step 2 pointwise via `two_trace_le_of_inverse`, then integration; needs D_t >= 0, i.e. the stability certificate (C-human + C-ball) |
| `h0` | U(0) = E(0) | `two_trace_eq_of_eq` + integration (C-human) |
| `hwin` | second-difference window bound | Step 3: entrywise MVT, sum/integral interchange, operator-norm bound (C-human) |
| `hU` | Upp0 <= Upp0_hi | Arb enclosure of (1/4) ∫ tr X^-1 G (C-ball) |
| `hW0`, `hW` | 0 <= ∫ tr X^-1 <= trW_hi | Arb enclosure (C-ball); positivity since X^-1 > 0 |
| `he0`, `he` | 0 <= esum <= esum_hi | Arb enclosure incl. tails (C-ball) |
| `hsym` | E(-t) = E(t) (stated for all t; only \|t\| <= t0 is needed, harmless) | Step 4 (C-human) |

The conclusion matches what the paper attributes to the Lean theorem: Section 2, Step 7, and the explicit disclaimer "It
does not certify that E and U are the stated integrals". The Lean conclusion is stated for t > 0. The paper's
"0 < |t|" follows from `hsym`, which is correct.

`cert_stability` is proved, but it is not a hypothesis of the assembled theorem. It enters only through the C-human
discharge of `hEU` (see NB-3).

**Literals vs the run file.** I re-derived these with `Fraction` from `run_a1_shear_main.json`:

- `Upp0_hi >= Upp0.hi`, `Upp0_lo <= Upp0.lo`, `trW_hi >= int_trW.hi`, `esum_hi >= sum_e.hi`,
  `lmin_lo <= lambda_min_B0_lower` and `dB_hi >= dB_upper` all hold, so every endpoint is rounded outward.
- All five Lean literals equal `cert_rationals` exactly.
- `B = Upp0_hi + trW_hi*esum_hi = -1.84156... < 0`, and the margin `lmin_lo - dB_hi = 0.911361 > 0`.
- The a = 2 literals in `RejectA2.lean`, and `Upp0_lo_a2` in `Controls.lean`, equal `run_a2_shear_negctl.json`
  `cert_rationals`.
- `data/` is byte-identical to `results/proposal2/2026-10-26/B2/`, including `data/lean/*.lean` and `data/code/*.py`.
- The certifier sha256 in the run file equals the file on disk (`168115eb...`).

## 3. The human argument, step by step

1. **Trace inequality** `2 tr S <= tr X + tr(X^-1 S^2)`, with X > 0 and S symmetric. The difference equals
   `tr(P(S-X)^2) = Σ_j m_jᵀ P m_j >= 0`. This is correct, and the Lean proof is an exact `linear_combination` plus two
   `quad_nonneg` calls. With S = D_t^{1/2} (needs D_t >= 0) and X = D_0^{1/2} (needs D_0 > 0 for kappa != 0), it gives
   `tr D_t^{1/2} <= (1/2)(tr X + tr X^-1 D_t)`. Correct.
2. **Majorant.** `U(t) = (1/4)∫[tr X + tr X^-1 D_t]` gives E <= U after integration, and U(0) = E(0) because the equality
   case holds pointwise. Integrability: `tr X^-1 ~ 1/|kappa|` at Γ is integrable in 2D. After the Duffy map the integrand is
   `tau/(2d)`, which is bounded. Correct.
3. **Window bound.** U is affine in D_t, so the `tr X` terms cancel in the second difference. Entrywise,
   `H(t)+H(-t)-2H(0) = t^2 H''(xi_ij)`. The ξ depend on n and on the entry but not on kappa, and they lie in [-t0, t0],
   which the code encloses as a ball. The remainder matrix R satisfies:
   - `|r_ij| <= 2 Σ_n |ΔH''_n,ij|`, using 1 - cos <= 2;
   - `||R||_op <= |r11|+|r12|+|r22| <= 2·esum` for a symmetric 2x2 matrix;
   - `tr(X^-1 R) <= tr(X^-1)||R||_op`, since X^-1 >= 0.

   With the 1/4 prefactor, the bound needed is `(1/2)·trW·esum`. The paper uses `trW·esum`, so the claimed factor-2 slack
   is real. Upp0 is U''(0) by differentiating under the integral (absolute convergence). Correct.
4. **Mirror symmetry.** σ = diag(1,-1) satisfies σ c(1/2, √3/2) = c(1,0) - c(1/2, √3/2) ∈ L_rho and σP_tσ = P_{-t},
   so L_{-t} = σL_t. E is an isometry invariant, because the zone mean is basis independent and the dynamical matrix
   transforms by conjugation. Correct. My independent check, on a midpoint grid that is not σ-invariant, gives
   E(h) - E(-h) = -9.6e-9, -1.2e-9 and -1.5e-10 at N = 128, 256 and 512. The difference shrinks with N, so it is a grid
   artifact.
5. **Shapes (Step 8).** Sympy, run by me: τ(0) = 1/2 + i√3/2, τ'(0) = √3 (real), and |τ'(0)|²/y² = 4. Matches
   `b2_tau_speed.py`. The deduction is valid. If ρ were a local minimum of E_zp over unit-covolume shapes, then
   E = E_zp∘τ, with τ continuous and τ(0) = ρ, would have a local minimum at t = 0, which `¬IsLocalMin E 0` contradicts.
   The strict inequality E(t) < E(0) by itself already forces τ(t) ≠ ρ (mod SL2(Z)), so the "τ(t) ≠ ρ" argument is not even
   needed.
6. **Wording.** Lean proves "not a local minimum along this path" (`¬IsLocalMin E 0` for the function E of t). The paper
   upgrades this to "not a local minimum over lattice shapes" only at Tier C-human, by the argument in step 5. That is
   correct: along a continuous path through the point, "not a local minimum" is the stronger statement. Nowhere does the
   paper claim that Lean proves the shape-space statement.
7. **Corollary (Step 9).** E''(0) = 2 Lap E_zp(ρ) needs three things:
   - isotropy of the Hessian at ρ;
   - criticality, ∇E_zp(ρ) = 0, because the chain rule has a ∇E_zp·τ''(0) term;
   - E_zp in C² as a function of τ, not only E in C² as a function of t.

   Criticality follows from the order-3 stabilizer of ρ, but it is not stated (NB-2).

## 4. Ball arithmetic (rerun with larger boxes) and rigor of the code

python-flint 0.6.0 imports from `.scratchpad/b2_pylib`. All runs use the venv Python with `-I` on cores 6 and 7, and
write to `/tmp/b2audit/`.

| run | cells | Upp0 enclosure | B_hi | certified | stability margin |
|---|---|---|---|---|---|
| producer a=1 (N=64, depth 3, tol 0.01) | 206,468 | [-1.94771, -1.90017] | -1.84156 | yes | 0.91136 |
| **auditor a=1, N=64, depth 0** | 8,192 | [-2.25898, -1.58913] | **-1.52980** | **yes** | 0.81472 |
| **auditor a=1, N=32, depth 1, tol 0.05** | 6,797 | [-2.27114, -1.57675] | **-1.51726** | **yes** | 0.81472 |
| **auditor a=2, N=64, depth 0** | 8,192 | [+12.0097, +13.4407] | B in [12.09, 13.52] | **no** (as required) | n/a |
| auditor a=1 and a=2, N=16, depth 2 | n/a | crashed: `fprime_enc: ball too wide` | n/a | n/a | n/a |

The sign survives boxes 8 to 25 times wider, and the coarse enclosures contain the producer's. With N = 16 the code fails
loudly instead of returning a wrong ball, which is the right failure mode (NB-7). The coarse runs' positive controls (the
E(0) value from P2, and ⟨tr D⟩ against the lattice sum) also pass.

**Independent float reimplementation (Tier X, `/tmp/b2audit/indep.py`).** It uses a different code path:

- a Cartesian lattice with |m|, |l| <= 9;
- H'' by central finite differences, not the closed form;
- a uniform midpoint κ-grid instead of Duffy coordinates;
- matrix square roots by `eigh`.

Results:

- **a = 1:** E0 = 1.503352, which matches P2's value of 1.50335235. U''(0) = -1.92396, inside the certified enclosure.
  The finite-difference E''(0) is -7.6960.
- **∫ tr X^-1** = 1.82476, 1.82714 and 1.82833 at N = 128, 256 and 512. The midpoint rule converges from below on the
  1/|κ| singularity at Γ. The N = 128 value lies just below the certified lower end, 1.825520, and this is quadrature
  error, not a contradiction. N = 256 and N = 512 lie inside the certified interval.
- **a = 2:** U''(0) = 12.725, inside [12.694, 12.757]. E''(0) = +3.96.
- **a = 1/2:** U''(0) = -1.013, inside [-1.044, -0.983]. E''(0) = -3.68.

In all three cases U''(0) >= E''(0), which is the direction the majorant requires.

Code review of `b2_certify.py` (sha256 `168115eb...`):

| part | status |
|---|---|
| Duffy map, Jacobian s/2; four triangles, two computed ×2 by κ → -κ | correct |
| B^{-1/2} formula; tr B^{1/2} = τ; integrand formulas for Upp0, trW, E(0), ⟨tr D⟩ | correct; I re-derived each from 2x2 identities |
| θ_n(t') for both triangles, and the label/vector convention R_n = m a1 + l a2 | correct |
| `hess_and_dd` closed form | correct; it agrees with my finite-difference Upp0 |
| mean-value cell rule | correct: ∫\|x_s - c_s\| = h³/4 per cell; partials evaluated on the whole cell box; B and det B tightened by their own mean-value forms intersected with the naive box; a cell counts only if det > 0 and tr > 0 on the box |
| f, f′ enclosures | correct: f via arb `sinc`; f′ via a closed form for \|x\| >= 1 and an alternating series with a first-omitted-term remainder otherwise, raising an error if a ball is too wide |
| lattice-point count #{\|R\| <= r} <= π(r+1)² | correct (Voronoi circumradius 0.62 < 1); each shell is over-counted by the full disc, which is conservative |
| θ_n bound | correct: \|θ\| <= 2π\|R0\|/c uses \|n\|² <= 2\|R0\|²/c², which holds because (m+l)² >= 0 |
| \|β\| bound | correct: \|β\| <= 2π√2\|R0\|/c |
| tail bounds BH, BH2 | correct: they use σ_min, σ_max, \|\|P′\|\| and \|\|P″\|\| over \|t\| <= t0 |
| stability `dB` | correct: weight 2θ²f <= θ² <= 2π²\|n\|² per ±n pair; tail 6·D_entry; λ_min >= det/tr |
| **pert tail** | **under-counted by a factor of 2** (NB-1); harmless |
| remainder beyond 200 shells, "≤ 2·last" | not proved in code (NB-6); the margin is astronomical |

**The k → 0 acoustic point is handled rigorously.** D_0 = s²B, and B is a smooth matrix function of (s, t'), including at
s = 0. Every integrand times the Jacobian is therefore a smooth function of B, which the code evaluates on boxes that
include s = 0. The certified bound λ_min(B) >= 0.9189 on every cell keeps d bounded away from 0 there. No cutoff or
excision is used.

## 5. Overclaim check

- **Tier C overall.** Stated in the abstract, the tier split, Step 7, the ledger headline `CZP-C-0012` and the Limitations.
  OK.
- **Deviation from the preregistration.** Section 1 says explicitly that the preregistered literal statement, a two-sided
  certified Lap E_zp < 0 checked in Lean, is "not established". The Laplacian appears only as a conditional C-human
  corollary. OK, but the stated reason for the deviation is mathematically wrong (BLOCKING-2).
- **a = 1/2.** Labelled "NOT preregistered" in the paper, the ledger (`CZP-C-0004`) and the metadata. It is excluded from
  the Lean theorem, which carries the a = 1 literals only. OK.
- **Negative control.** a = 2 is not certified (my coarse rerun confirms), the kernel rejects it, and
  `a2_not_certifiable` holds. OK.
- **Disclosures.** Guards failing (pre-existing), the missing main-run log, python-flint outside the venv and no novelty
  search are all disclosed. OK.

## 6. `publication_meta.json`

The following match the paper and the run files: the numbers (-1.84156, 206,468 cells, -0.92078), the tier split, the
deviation, the a = 1/2 labelling, the hash prefixes (Basic `0241b6af`, Controls `2e95e21b`, RejectTampered `02f6930b`,
RejectA2 `ab0f5f29`), the certifier sha256 and the related identifiers. Three problems:

- the status sentence becomes false once this audit exists (BLOCKING-1);
- the keyword "negative result" is misleading (NB-4);
- the corollary hypotheses are incomplete (NB-2).

I did not verify the claimed commit hashes (`b687db2`, HEAD at writing `74b90812...`), because git was out of scope for
this audit.

---

## BLOCKING (fix before release)

**BLOCKING-1. Status text made false by this audit.** These must change:

- **`main.tex`, AI-assistance disclosure.** Replace "At the time of writing \emph{no independent audit} of this paper
  exists (the statement lock and the independent audit of the programme are pending), and the reruns reported here were
  made by the same pipeline, which is not a producer~$\neq$~verifier check." with:
  > An independent adversarial audit by a separate AI agent instance (`AUDIT.md`, verdict ACCEPT\_WITH\_CORRECTIONS)
  > recompiled the Lean files, re-ran the ball arithmetic with coarser cells and re-implemented the quantities in
  > floating point. The main theorem statement is locked in `results/proposal2/2026-10-26/B2/STATEMENT_LOCK.json`. No human
  > has audited the work.
- **`main.tex`, Limitations.** Replace the bullet "Statement lock and independent audit pending at writing" with:
  > Statement locked and independently audited by an AI agent (not a human); the audit's corrections are applied; the
  > Tier A adequacy flags are closed by that audit only to the extent recorded in the ledger's audit fields.
- **`main.tex` Section 7 and `publication_meta.json` ("8 flags ... remain open", "audit field is null").** Set the ledger
  `audit` field of `CZP-A-0001`..`0008` to reference `papers/p2_certified_zero_point/AUDIT.md` and the statement-lock
  hash `d6947d20...`. Rebuild the ledger, rerun the gate, and quote the new gate output verbatim.
- **`publication_meta.json` (description "Status" paragraph, and `notes`).** Replace "the statement lock and an
  independent audit are pending" and "Producer and writer are AI agent instances of the same pipeline" with the audited
  wording above, and keep "no human has reviewed the work".

**BLOCKING-2. Incorrect justification for the deviation.**

- **The wrong sentence.** `main.tex` Section 1 says: "the second variation of tr D^{1/2} contains a concave part that is
  singular at branch degeneracies and at Γ (P2, Daleckii--Krein)". `CERTIFIED_CURVATURE.md` §1 says the same.
- **Why it is wrong.** For 2x2 matrices, `tr D^{1/2} = sqrt(tr D + 2 sqrt(det D))` is real-analytic on the positive
  definite cone. In Daleckii–Krein form, the second divided difference of √· is
  `-1/(2√λ1√λ2(√λ1+√λ2))`, which is smooth at λ1 = λ2. The only singular point is λ → 0, at Γ. In this paper's own Duffy
  variables, `tr D_t^{1/2} = s·τ(B_t)` is smooth in (s, t', t) wherever B_t > 0, which the certificate proves.
- **Fix.** Replace the sentence with:
  > A direct enclosure of Lap E_zp was not attempted; the producer chose the linear-response majorant because it is affine
  > in D_t and needs no matrix square root of the perturbed lattice. (The second variation of tr D^{1/2} is smooth away from
  > Γ; a direct certified enclosure of E''(0) with the same Duffy machinery appears feasible and is left open.)

  Make the same correction in `CERTIFIED_CURVATURE.md` §1.

## NONBLOCKING (recommended)

**NB-1. Factor-2 under-count in the esum tail.** In `tail_bounds`, `acc["E"] += cnt * 3 * bh2` bounds
Σ_entries sup|H''(ξ)|, but `|H''(ξ) - H''(0)| <= 2·bh2` per entry, so the bound should be `6 * bh2`. Compare `dB`, which
correctly uses `6 * D_entry`. This is harmless, for two reasons:

- the tail is 2.2e-25, while the outward rounding of `esum_hi` already adds 9.2e-13 over `sum_e.hi` (checked with
  Fractions);
- the main bound has a genuine factor-2 slack.

The certificate stands. Fix: change 3 to 6. Also correct the module docstring, which says `e_n = max_entries`; the code
sums over entries.

**NB-2. Corollary hypotheses incomplete.** E''(0) = 2 Lap E_zp(ρ) also needs ∇E_zp(ρ) = 0 and E_zp ∈ C² in τ near ρ.
Criticality follows from SL2(Z) invariance, since ρ is fixed by an order-3 elliptic element. Fix: write "(E_zp of class
C² near ρ; ρ critical and the Hessian isotropic, both by the order-3 stabilizer, P2 3.1)" in each of these places:

- the abstract;
- Step 9;
- `CERTIFIED_CURVATURE.md` §0 and §2.6;
- the ledger row `CZP-C-0013`;
- `publication_meta.json`.

Optional: by BLOCKING-2's smoothness observation, C² of E in t is provable, by differentiating `s·τ(B_t)` under the
integral.

**NB-3. Stability is not inside the Lean assembly.** Add one sentence after the Step 5 listing:
> `cert_stability` is proved but is not a hypothesis of `triangular_not_localMin_of_certificate`; it supports the C-human
> discharge of `hEU` (D_t must be positive semidefinite for S = D_t^{1/2}).

This keeps readers from thinking the Lean theorem consumes the stability margin.

**NB-4. Keyword.** Drop "negative result" from `publication_meta.json` keywords. The B2 kill rule did not fire, and the
headline is a positive certified statement.

**NB-5. `hsym` is global.** It is stated for all t, although |t| <= t0 suffices. It is true globally, so nothing is wrong;
optionally note it in Step 7.

**NB-6. Tail remainder.** "Beyond r_K the terms decay faster than geometrically (ratio < 1/2), bounded by 2·last" is
asserted in a comment and not computed. Fix: state the explicit ratio bound. At r ≈ 55 with Δ = 1/4 and a >= 1/2, the
ratio is below exp(-π·a·σ_min²·2rΔ) < e^{-40}. Alternatively, ball-evaluate the ratio at r_K in the code.

**NB-7. Robustness.** With N = 16 the certifier raises `fprime_enc: ball too wide`, so it cannot run on coarse grids. This
is the correct failure mode, but it is undocumented. Either note it in the Commands section or split straddling balls.

**NB-8. Reproducibility list.** The paper's command block omits the `Controls.lean` and `RejectTampered.lean` compiles
and the diagonal-path control run. `CERTIFIED_CURVATURE.md` §7 has them; copy them over.

**NB-9. Step 8 can be simplified.** Strict E(t) < E(0) already implies a different shape, so the τ-speed argument is
needed only for the corollary.

## Auditor commands (reproducible)

```
taskset -c 6,7 python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Programmes/ZeroPointCert/Basic.lean --olean Programmes.ZeroPointCert.Basic --json-out /tmp/b2audit/basic.json
taskset -c 6,7 python3 scripts/certified_numerics/lean_pinned.py compile /tmp/b2audit/Programmes/Audit/Check.lean --json-out /tmp/b2audit/check.json
taskset -c 6,7 python3 scripts/certified_numerics/lean_pinned.py compile /tmp/b2audit/Programmes/Audit/BasicSorry.lean --json-out /tmp/b2audit/basicsorry.json
taskset -c 6,7 python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Programmes/ZeroPointCert/{Controls,RejectTampered,RejectA2}.lean
B2_REFINE_TOL=1000 B2_MAX_DEPTH=0 python -I code/b2_certify.py 1 shear 64 1/100000 21 /tmp/b2audit/red_a1_N64d0.json   # 16 s
B2_REFINE_TOL=0.05 B2_MAX_DEPTH=1 python -I code/b2_certify.py 1 shear 32 1/100000 21 /tmp/b2audit/red_a1_N32d1.json
B2_REFINE_TOL=1000 B2_MAX_DEPTH=0 python -I code/b2_certify.py 2 shear 64 1/100000 21 /tmp/b2audit/red_a2_N64d0.json
python -I /tmp/b2audit/indep.py {1|2|1/2} {128|256|512}
python -I /tmp/b2audit/make_lock.py <repo> results/proposal2/2026-10-26/B2/STATEMENT_LOCK.json
```
