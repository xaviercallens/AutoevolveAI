# Independent AI audit of M1 / p4_zero_point_dipolar (producer != verifier)

Auditor: an AI agent (Claude), separate from the producer lane. Date 2026-10-28. **No human audit is implied or exists.**
Scratch: /tmp/m1audit/ (scripts/, float_results.jsonl, transforms.json, points/, lean/lean_audit.json, replay/, pdf/, gate_output_audit.txt).

## Verdict: ACCEPT_WITH_CORRECTIONS (provisional; see "incomplete at handback")

## 1. Independent numerics (auditor's own code, Tier X)
Own float64 code (scripts/zp_float.py), two independent methods for D_t(kappa): (a) brute-force real-space sum,
|R0| < 300, plus continuum tail of the non-oscillating part; (b) own Ewald split at alpha = 1/4 and 1 (producer: 1/10),
own Poisson step, dipole transform by quadrature. Duffy Gauss-Legendre N = 32 (N = 48 checked for Riesz 3), central
differences h = 1e-3 with Richardson.

| potential | E(0) own | E''(0) own (direct / Ewald) | paper Tier X E''(0) | M enclosure | inside, sign |
|---|---|---|---|---|---|
| Riesz 3 | 4.2449757 | -2.41791 / -2.41791 | -2.439 | [-3.17029,-1.66310] | yes, < 0 |
| d = 1/10 | 4.2096272 | -2.59522 / -2.59522 | -2.616 | [-3.33620,-1.85185] | yes |
| d = 1/2 | 3.5284909 | -4.75304 / -4.75304 | -4.767 | [-5.38812,-4.11598] | yes |
| d/a 0.06 | 4.2301863 | -2.49295 / -2.49295 | -2.51419 | [-3.23699,-1.74649] | yes |
| d/a 0.09 | 4.2119010 | -2.58403 / -2.58403 | -2.60506 | [-3.32496,-1.84069] | yes |
| d/a 0.1 | 4.2041875 | -2.62189 / -2.62189 | -2.64284 | [-3.36115,-1.88023] | yes |
| d/a 0.5 | 3.4422047 | -4.87312 / -4.87312 | -4.88677 | [-5.49473,-4.24958] | yes |

All E(0) lie in the paper's E(0) enclosures. Direct vs Ewald agree to about 1e-6. Results are independent of alpha
(0.05 to 1) and converged in N and in R_c (100 -> 300 changes E'' by 4e-7). The tail bound is
|sum_{|R|>R_c}(1-cos) Hess r^-3| <= 2*12*2pi/(3 R_c^3), about 1.9e-6 at R_c = 300.
The sign is known for one case: Riesz s = 4 gives E''(0) = +2.789 (N2 Tier X +2.754, local minimum), so the method is
not sign-biased. The paper's Tier X E''(0) values are N2's central differences with hE = 1e-2 and carry a bias of
about 0.02 (reproduced: h = 1e-2 gives -2.4389). That is harmless, but the 5-6 digits quoted overstate their precision.

What this audit did NOT do: an independent rigorous re-derivation of M. That would mean re-implementing N2's
moving-comparison certifier. The M enclosures remain the producer's Tier C-ball.

## 2. Derivations and controls of the reciprocal-space (Ewald) code
- Re-derived the mixture representations, 0 <= w_d <= w_3, and the Poisson step D = sum_G [F(G+k)-F(G)], F = q q^T Vhat.
- Vhat_3 closed form vs quadrature: max diff 5e-18 (n = 0..4).
- Dipole series (m <= 6) vs quadrature: max diff 6.1e-15 at d = 0.5373, n = 4. This is within the producer's remainder
  1.16e-14 for d = 0.5373. The paper quotes only 4.3e-15 (d = 1/2).
- Short-part incomplete-gamma closed forms vs quadrature: rel. diff 3e-28.
- New negative / known-answer controls on the producer's Recip code (scripts/producer_points.py, compare_points.py):
  - Known answer: producer's Recip.sums2 with Vhat replaced by the transform of exp(-r^2/10). The first completed point
    equals the auditor's own direct real-space mpmath sum to all printed digits (95.91576559051371).
  - Corruption detection: dropping the -2 pi x erfc term changes B at small s by about 5 (154.53 -> 159.74, ball radius
    1e-10). An alpha mismatch (1/8 vs 1/10) changes it by about 0.9. Both are detectable far beyond the balls.
  - Neither corruption is detectable at large s (erfc ~ 1e-11), and neither flips the sign of E''. In the auditor's own
    Ewald code, noerfc / sign-flipped erfc / halved long part give E'' = -2.414 / -2.409 / -2.419.
  - Conclusion: the reciprocal part contributes only about 1e-2 to E''. A sign-flipping negative control confined to the
    reciprocal code does not exist; the lattice-sum-level control is the meaningful one.

## 3. Lean (pinned Lean 4.34.1, fresh /tmp olean dir, repo .olean_out not on LEAN_PATH)
- The whole chain ZeroPoint.Basic -> ZeroPointCert.Basic -> ZeroPointPhys.Taylor -> ZeroPointPhys.Basic ->
  ZeroPointDipolar.Basic compiles with rc 0.
- leanchecker rc 0 for all five modules, empty output, run by the auditor.
- Basic.lean prints 14 axiom lines, all within {propext, Classical.choice, Quot.sound}.
- Controls.lean: ctl_sorry shows sorryAx and ctl_axiom shows ctl_cheat (caught). RejectGauss2.lean gives rc 1,
  "unsolved goals ⊢ False".
- Grep for sorry, axiom, native_decide, implemented_by, skipKernelTC, addDecl, unsafe, extern, opaque, set_option,
  run_cmd and elab: hits only in the planted Controls.lean.
- All 28 rationals in Basic.lean equal the run JSONs' cert_rationals. Each M_hi is >= the ball's upper end and matches
  the paper's table.
- Content: each *_not_localMin theorem is N2's generic window lemma for arbitrary E, U with M_hi plugged in. The kernel
  checks only the logic and the endpoint signs. It does not connect to the numerics, and the paper correctly says so
  (Section 6, "What the kernel does not know").
- Deviation: the Lean checks were not run through anse/formal/lean_runner.py. The paper discloses this.

## 4. Ledger and gate
- 15 claims (4 A, 1 L, 7 C, 3 X). The tiers match the evidence, and the headline is Tier C.
- Gate run into scratch: only 4x LEDGER_UNAUDITED_TIER_A, exit_code = 1, as expected. gate_output.txt was not touched.

## 5. Provenance
- sha256 n2_certify.py = 6fa38af9e1043473cc60a2ca7c9bb27b8030c1d64135ec8c320d9f086f9fa0f6 (matches, and is the same at
  28a1ac0).
- m1_certify.py = 360ebbcb...b929 (matches in both copies and in every run JSON).
- DOIs: 23663551 = N2 (Yukawa), 23655392 = B2 (exp(-pi r^2)), 23667863 = N1 (Gaussian classification). Titles and
  roles are described correctly.
- Controls: Gaussian a = 1 and 2 and Yukawa kappa = 2 are bit-identical to the N2 runs. Yukawa kappa = 1 contains N2's
  interval.
- Lindemann 0.31 is mentioned only as unsourced and not relied upon. Nothing in the paper, ledger or meta depends on it.
- PDF rebuilt in scratch: two passes rc 0, 10 pages, 0 undefined references, 0 overfull boxes.

## Required corrections (old -> new)
1. main.tex l.44-45, Limitations l.218, publication_meta (description, notes, verdict):
   - Old: "At the time of writing no independent audit of this work exists, by an AI or by a person ..."
   - New: "An independent AI audit (producer ≠ verifier, papers/p4_zero_point_dipolar/AUDIT.md) re-ran the kernel
     replay of the whole import chain, re-derived the Ewald formulas, recomputed E(0) and E''(0) for all seven
     potentials by two independent methods (all inside the enclosures, all negative) and added a negative control
     for the reciprocal-space code. It did not independently re-derive the M enclosures. No human audit exists."
2. l.79: "N2~\cite{n2} proved (Tier" -> "N2~\cite{n2} certified (Tier".
3. l.95: "the smallest certified lower bounds are $\lambda_{\min}(B)\ge4.244$ and $q_{\rm pd}\ge1.529$ (the $d=1/2$ run)"
   -> "the smallest certified lower bounds are $\lambda_{\min}(B)\ge4.0078$ and $q_{\rm pd}\ge1.5000$ (the $d/a=0.5$ run,
   $d=5373/10000$)". This is per dipolar_da0.5.json.
4. l.229 and publication_meta notes: "the M1 results and Lean files were untracked or uncommitted in that tree" ->
   "the M1 results, code and Lean files are committed in that commit (unchanged since); the paper directory was
   committed later (4094011)". `git ls-tree 28a1ac0` lists 46 M1 files and the 3 ZeroPointDipolar Lean files.
5. l.81 prereg quote:
   - Old: "``certified sign ... for the bilayer point-dipole potential"
   - New: "``Certified sign ... for the bilayer point-dipole exciton potential"
   - This makes it verbatim with preregistration.json.
6. After "The Tier~\tX{} value $E''(0)$ lies inside each enclosure $M$" (l.95), add: "(the Tier X values are N2's
   central differences with step $10^{-2}$ and are biased by about $0.02$; step-converged values are $-2.418$,
   $-2.595$, $-4.753$, $-2.493$, $-2.584$, $-2.622$, $-4.873$, AUDIT.md)".
7. Step 3 l.113: "and $4.3\times10^{-15}$ for $d=1/2$" -> "$4.3\times10^{-15}$ for $d=1/2$ and $1.2\times10^{-14}$ for
   $d=5373/10000$".
8. Abstract l.69, l.154, Limitations l.221: "the reciprocal-space code has no negative control of its own" -> "the
   producer run had no negative control of the reciprocal-space code. The independent audit added one: corrupted
   transforms are detected far beyond the ball radii, and a known Gaussian is reproduced through the Poisson code. No
   corruption confined to the reciprocal code flips the sign, because that part contributes only about $10^{-2}$ to
   $E''$."

Recommended, not required: soften the title "Closing the long-range gap".

## Incomplete at handback (stated honestly)
- **Replays.** Reproducibility replays of the producer certifier (riesz3, dipolar_da0.5; producer's code, not
  independent) were still running in /tmp/m1audit/replay. Partial traces match the producer logs exactly at
  2000/4000/6000 cells. Bit-identity of the final rationals is unverified.
- **Point comparisons.** The auditor's own mpmath point jets (riesz3 and d = 0.5373 at alpha = 1; Gaussian known-answer
  at 6 points) had completed only 1 Gaussian point, which matched. The full 54-number comparisons are pending. Rerun
  /tmp/m1audit/scripts/compare_points.py when the points/my_*.json files are complete.
