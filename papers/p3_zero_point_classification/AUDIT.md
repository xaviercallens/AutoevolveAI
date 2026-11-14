# Independent adversarial audit of N1 (papers/p3_zero_point_classification)

Auditor: an independent AI audit agent (producer != verifier), 2026-10-26. No human has audited this paper.
Scope: main.tex / main.pdf, ledger/, data/, formal_cert/Programmes/ZeroPointClass/, data/code/n1_certify2.py and n1_certify.py.
Scratch: /tmp/n1audit/. I wrote only two files in the repository: this file and `data/leanchecker_replay_audit.json`.
I made no git writes. I did not write to the shared olean dir `certified_numerics_olean`: every olean I built went to /tmp/n1audit/olean{,2}.

## VERDICT: ACCEPT_WITH_CORRECTIONS

I found no mathematical error. The headline (Tier C) stands as scoped:
- F < 0 on [0.425, 1.579] and F > 0 on [1.584, 4], for |t| <= 1e-8;
- a zero of F(., 0) in (0.3745, 0.379) and one in (1.579, 1.583).

What supports it:
- The chains cover both ranges with no gap. I checked this independently in exact rationals.
- Every record has its sign.
- Every Lean record equals its run JSON digit for digit.
- Three certifier re-runs reproduce the stored records bit for bit.
- The Lean files recompile with only the whitelisted axioms.
- The leanchecker kernel replay of `Programmes.ZeroPointClass.Cert` passes: **rc 0**.

The corrections below are about wording, counts, tier tags and stale status lines. None is blocking.

## BLOCKING

None.

## NONBLOCKING (with exact fixes)

1. **Title overclaim.** main.tex:32 (and publication_meta.json "title") says "not a local minimum below $a\approx1.58$".
   Left of a_- the certified sign is F > 0 at the points 0.33 to 0.3745, so "below 1.58" is false as written for a < 0.3745.
   Fix: replace it with "not a local minimum for $a\in[0.425,1.579]$ and a strict minimum along the shear for $a\in[1.584,4]$".
2. **"The sign changes ... are enclosed".** This wording is at main.tex:57-58, and the same sentence is in the publication_meta.json description.
   It reads as "all sign changes lie in the two brackets". Only existence is proved.
   - (0.33, 0.3745) and (0.383, 0.425) contain uncertified sub-intervals.
   - (1.583, 1.584) is not whole-interval certified.
   - Nothing below 0.33 is certified.
   So further zeros are not excluded there. Fix: "Each of $(0.3745,0.379)$ and $(1.579,1.583)$ contains a zero of $a\mapsto F(a,0)$
   (intermediate value theorem). Uniqueness, and the absence of other zeros in the uncertified gaps, are not certified."
   Also use "a zero $a_-\in\ldots$" in place of "$a_-\in$" at main.tex:57, :99 and :176.
3. **T7 tier tag.** main.tex:103 tags T7 as \tA. T7 rests on `Encloses` (C-ball) exactly as T1/T2 do, and there is no Lean theorem for it.
   Fix: change the tier cell to "\tA{} logic (not formalised as one theorem); \tCb{} (T1, T2 and the 1.583 record)".
4. **Cell count double-counts the duplicate record.** main.tex:65, main.tex:278 and ledger PZC-C-0005 give
   "1,284,310 certified cells (232,178 refined) over 203 records". My script deduplicates the 19 input files the same way
   `n1_make_cert.py` does (keyed by (a_lo, a_hi)), and that gives 202 distinct ok records with **1,276,022** cells (232,146 refined).
   The difference of 8,288 cells (32 refined) is exactly the duplicated thin record a = 198/125 in runs/sweep_ap_tight.json.
   Fix: write "1,284,310 cells over 203 run records, one of which (a = 1.584) is a duplicate; 1,276,022 over the 202 distinct records".
   The CPU total at main.tex:278 (13,685 s) has the same issue: it is 13,599 s over distinct records.
   The 609-check cross-check (main.tex:256) is 3 x 203. It includes the duplicate too, so say so.
5. **"5 straddling".** main.tex:256 and ledger PZC-C-0006 say "12 do not (7 with failed cells, 5 straddling)".
   Of the 5 ok-but-unsigned runs, only 2 straddle a root: [0.3745, 0.379] and [1.579, 1.583].
   The other 3, [0.41, 0.415], [0.415, 0.42] and [0.42, 0.425], lie where F < 0 is expected. Their enclosures are merely too wide.
   Fix: "7 with failed cells, 2 straddling a root, 3 inconclusive (too wide)".
   Also, the caption at main.tex:243 says "The 7 uncertified runs", but `cert_summary.json` "uncertified" has 12 entries. Fix: "the 12 unsigned runs (7 failed, 5 inconclusive)".
6. **"20 theorems" in Basic.** main.tex:283 says Basic.lean has 20 theorems. The file prints axioms for 21 declarations (`root_in_gap'` included), and both my compile and data/lean_basic.json show 21 lines.
   Fix: change it to 21.
7. **The "12 vs 9" thin points (resolved, consistent).** There are 22 thin records:
   - 10 positive: 0.33, 0.35, 0.36, 0.37, 0.372, 0.3745, 1.583, 1.584, 1.587, 1.593;
   - 12 negative: 9 near a_- (0.379, 0.381, 0.383, 0.39, 0.40, 0.42, 0.45, 0.5, 0.55) and 3 near a_+ (1.57, 1.576, 1.579).

   main.tex:226-228, CLASSIFICATION.md:31-33 (6 + 9 + 7) and the ledger agree. I found no place that writes 9 where 12 is meant.
   The other "12, 9, ..." in the paper is the failed-cell counts "12, 9, 5, 12, 3" of the five intervals on [0.3925, 0.41] (main.tex:238). I verified them against the run JSONs: they are failed-cell counts, not thin-point counts.
   Note for the producer: "84 negative" = 71 chain + 1 interval [0.381, 0.383] + 12 thin. "113 positive" = 103 chain + 10 thin.
   The 114 vs 113 discrepancy (main.tex:319) is real: it is the duplicate a = 198/125, and the Lean list is deduplicated. I confirm this.
8. **Lean hypotheses over-quantified in a.** Cert.lean:440-442, :464-466 and :515-517: `hE`, `hE'`, `hsym` are stated `∀ a t`, so for every real a,
   including a <= 0, where the physical E_zp is undefined.
   This is not unsound: E and F are free variables, and one can extend them arbitrarily outside the range. But it makes instantiation awkward, and the hypotheses are stronger than the gloss.
   Fix in n1_make_cert.py: quantify `∀ a, lo ≤ a → a ≤ hi → ∀ t ∈ Icc (-t0) t0, ...`. The proofs only use a in range.
9. **Reject controls fail at elaboration ("Reduction got stuck"), not by a kernel "false" verdict.**
   data/lean_reject_inside.json and lean_reject_tampered.json both show `decide` "did not reduce". The rc 1 alone would not distinguish "false" from "stuck".
   The real evidence is Honest.lean, which proves `allPos [rInH] = false` and `allPos [rTH] = false` by `decide +kernel`. It compiles with standard axioms and replays with rc 0 (below).
   Fix: say this at main.tex:251-252 ("the negative proof is Honest.lean; RejectInside/RejectTampered only show the claim cannot be proved").
10. **Stale status lines after this audit.**
    - main.tex:43-46 and :315 ("No independent audit ... pending");
    - main.tex:292 and :316 ("no line for Cert ... rests on the compile and the axiom audit only");
    - main.tex:307 ("no AI audit recorded").

    Fix: cite this audit and `data/leanchecker_replay_audit.json`: Cert, Controls, Honest and Basic replay with rc 0, and so do the rebuilt imports ZeroPoint.Basic and ZeroPointCert.Basic.
    Record the AI audit in the ledger's audit fields. I did not edit them. The LEDGER_UNAUDITED_TIER_A flags remain correct, because no *human* has audited the statements.
11. **Prefactor and BZ bookkeeping are Tier C-human (inherited from B2), and the signs do not depend on the prefactor.**
    I re-derived the Duffy bookkeeping (below), and it is right. But the paper should say explicitly (Step 2, main.tex:119-120)
    that a positive overall prefactor cannot change any sign claimed, while a missing BZ region could.
    The BZ coverage is checked only at Tier X (agreement with P2's independent c(a) and roots).
12. **Minor.** main.tex:41 says "Zenodo DOI to be assigned". That is fine for v1.
    The README-style claim "B2's Lean hasDerivAt_* cover the scalar pieces" (main.tex:123) is not used by any N1 theorem. Mark it as context only.

## What I checked, and how

### (1) Mathematics
- **tr sqrt D identity.** For a 2x2 symmetric PSD D with eigenvalues l1, l2 >= 0: (sqrt l1 + sqrt l2)^2 = tr D + 2 sqrt(det D). Both sides are >= 0, so
  tr sqrt D = sqrt(tr D + 2 sqrt det D). This is valid for all PSD D. The code needs det B > 0 and tr B > 0 for differentiability, and it certifies both on every cell
  (`g_integrand`, n1_certify2.py:180-184, applied to the centre jet and to the tightened ball jet).
- **F is the exact second t-derivative.** D_t(kappa) = sum_n (1 - cos 2 pi kappa.n) Hess V(P_t R_n), in reduced kappa. For unimodular P_t the BZ measure is fixed,
  so t enters only through H_n(t). The chain-rule formulas are correct:
  - det' = B0'B2 + B0B2' - 2B1B1';
  - det'' = B0''B2 + 2B0'B2' + B0B2'' - 2(B1'^2 + B1B1'');
  - delta'' and tau'' as at main.tex:121-122 = n1_certify2.py:187-194.

  `hess_derivs` (n1_certify.py:205-225) is correct: e' = -pi a q' e and e'' = (pi^2 a^2 q'^2 - pi a q'') e, with H = e M.
  There is no inequality anywhere, so F is the exact second derivative, given differentiation under the integral (Tier C-human, as stated).
- **Duffy and prefactors, re-derived.** Triangle 0 is kappa = s(1/2, t' - 1/2), so 2 pi kappa.n = s(pi(m - l) + 2 pi l t'), and that is `th` for tri 0.
  Triangle 1 is kappa = s(t' - 1/2, 1/2). Both have Jacobian s/2.
  The two triangles plus their inversion images (factor 2, `tot += 2*r`, D(-kappa) = D(kappa)) tile the reduced square.
  The half-lattice weight 2 theta^2 f accounts for +-n. So E = 1/2 int tr sqrt D = sum 2 int s^2 tau/4, and F = sum 2 int s^2 tau''/4. Correct.
  Signs do not depend on the positive prefactor. The independent P2 roots 0.37668 and 1.58148 lie in the brackets (Tier X).
- **Affine-in-a enclosure (main.tex:129).** Expand for fixed t about the cell centre (s_c, t'_c, a_c) with the Lagrange remainder. The box cell x [a_c - delta, a_c + delta] is convex.
  - The first-order s and t' terms integrate to 0 over the square cell.
  - The first-order a term gives (a - a_c) D(t).
  - The remainder integrates to the code's bound. The coefficients come from int Delta_s^2 = h^4/12 (x 1/2 gives h^2/24 per unit area), int |Delta_s||Delta_t'| = h^4/16 and int |Delta_s| = h^3/4 (x delta gives delta h/4), together with (a - a_c)^2 in [0, delta^2], which gives hull(0, delta^2/2 g_aa).

  This matches n1_certify2.py:385-387. So F(a,t) = Q(t) + (a - a_c) D(t) + R(a,t), with Q(t) in Q, D(t) in D and R in R, uniformly in |t| <= t0 (t is a ball in every quantity).
  This is exactly `Encloses`, with d = D(t). The corner bound (`Rec.cmax`/`cmin`, `mul_le_corners`) is sound.
- **Chaining and coverage (independent script /tmp/n1audit/check_chain.py; exact Fractions parsed from Cert.lean).**
  - `Lnegseg0` chains exactly from 17/40 to 1579/1000 in 71 records.
  - `Lposseg0` chains from 198/125 to 4 in 103 records.
  - Consecutive hi = lo, no gaps, lo <= hi everywhere, and a_c = (lo+hi)/2 in every record.
  - Widths are 0.001-0.02 (negative chain) and 0.003-0.0538 (positive chain).
  - Every one of the 113 positive and 84 negative records satisfies its corner inequality in exact arithmetic.
  - The weakest ends are F <= -0.0151907 on [1.576, 1.579] and F >= 0.0155841 on [1.584, 1.587]. Both match main.tex:206-207.
  - All 197 records equal `rec_vals` of their run JSON, (Q+R).lo/hi and D.lo/hi.
  - Every run has ok, 0 failed cells, t0 = 1/100000000, and engine sign = Lean sign.
  - All runs carry the same script sha256 pair, which equals main.tex:340-341 and the files in data/code/.
- **Non-vacuity of `Encloses`.** No a lies in both a positive and a negative record. At every shared endpoint of two records, the implied F-ranges
  q + (a - a_c)[dlo, dhi] intersect (0 inconsistencies). So a t-independent F that is piecewise affine on each record, with values in the intersection
  at the shared points, satisfies `Encloses F t0 Lpos ∧ Encloses F t0 Lneg`. `classification`, `segment_*` and `along_path` are therefore not vacuous.
- **IVT brackets.** r5 = 749/2000 (F in [0.017732, 0.094875]) and r113 = 379/1000 (F in [-0.097769, -0.023538]); r196 = 1579/1000 (F in [-0.042254, -0.019463]) and r6 = 1583/1000 (F in [0.007479, 0.030273]).
  These are thin records (lo = hi), with the right signs at t = 0 (|0| <= t0). `brackets_ordered` (decide +kernel) checks the order.
  Continuity in a is Tier C-human, which is correctly filed. The argument (a uniformly convergent lattice sum of smooth integrands with det B bounded away from 0) is plausible but needs det B > 0 on the whole bracket, not only at the two thin points. That holds for a near the brackets by continuity, but no certificate covers it. The paper's Tier C-human tag covers this. Optional: add the sentence.
- **Bracket constants.** 17/40 = 0.425, 1579/1000, 198/125 = 1.584 and 4 in `chain_*`/`segment_*`, and 749/2000, 379/1000, 1579/1000, 1583/1000 in `classification`. No off-by-one: each equals the paper's decimals, and each is a record endpoint.
- **Window and stability.** The t-window enters every H_n as the ball [-t0, t0] (`path_R` with `tball`). `path_norms` are valid operator-norm bounds for P_t = [[1,t],[t,1+t^2]]: ||P_t - I|| <= |t| + t^2, ||P_t'|| <= |t| + sqrt(1+t^2) <= 1 + 2t0, ||P''|| = 2.
  det B > 0 and tr B > 0 are certified on each cell ball x a-interval x t-window. So D_t = s^2 B_t > 0 for kappa != 0, and the lattice is dynamically stable on the whole window.
  At the window edge, differentiability needs an open neighbourhood. That follows from strict positivity and continuity (Tier C-human, stated at main.tex:196).
- **Window lemmas (Basic.lean:35-103).** I read them. E - (B/2)t^2 is concave (convex) on [-t0, t0] by Mathlib's second-derivative criterion, and the midpoint inequality gives E(t) + E(-t) - 2E(0) <= B t^2. With the mirror symmetry, B < 0 gives E(t) < E(0) and not IsLocalMin. Correct. The lemmas reuse B2's `not_isLocalMin_of_majorant` with U = E.

### (2) Lean
- **Sources.** The sha256 of all six files equal main.tex:295-300, and data/lean/ is identical to formal_cert/ (diff -r).
- **Grep.** I searched ZeroPointClass/*.lean and ZeroPointCert/Basic.lean for `skipKernelTC|addDecl|native_decide|implemented_by|extern|unsafe|sorry|admit|axiom|set_option|macro|elab`. The only hits are the planted `sorry` and `axiom ctl_cheat` in Controls.lean.
- **Recompile with `taskset -c 6 python3 scripts/certified_numerics/lean_pinned.py compile FILE --json-out /tmp/n1audit/...` (pinned Lean 4.34.1).**
  - Basic.lean: rc 0 (11.7 s, warm cache). 21 `#print axioms` lines, all `[propext, Classical.choice, Quot.sound]`.
  - Cert.lean: rc 0 (18.2 s). 11 lines, all standard.
- **Fresh private build (core 7, oleans in /tmp/n1audit/olean, first on LEAN_PATH).**
  - Basic rc 0, Cert rc 0, Honest rc 0 (4 standard lines).
  - Controls rc 0, with `ctl_sorry` showing `sorryAx` and `ctl_axiom` showing `ProgZeroPointClass.ctl_cheat`; `ctl_false` is standard.
  - RejectInside rc 1 and RejectTampered rc 1.
- **Kernel replay (leanchecker 4.34.1, from my fresh oleans).**
  - Programmes.ZeroPointClass.Cert: **rc 0** (55.5 s).
  - Controls: rc 0 (52.6 s).
  - Honest: rc 0 (49.9 s).
  - Basic: rc 0 (53.1 s).

  The replay does not audit axioms: Controls replays with rc 0 although it holds sorryAx and an axiom. The axiom audit is the `#print axioms` output above.
  The `decide +kernel` proofs (chains, signs, brackets) are re-evaluated by the kernel in the replay.
- **Import layer.** In a second build (/tmp/n1audit/olean2), I rebuilt the whole chain from source: ZeroPoint.Basic -> ZeroPointCert.Basic -> ZeroPointClass.{Basic, Cert, Controls, Honest}. Then I replayed each module.
  - Compiles: all rc 0, and every axiom line is standard except the planted Controls lines.
  - leanchecker: ZeroPoint.Basic rc 0 (53.3 s), ZeroPointCert.Basic rc 0 (53.2 s), ZeroPointClass.Basic rc 0 (50.3 s), **Cert rc 0** (56.1 s), Controls rc 0 (49.9 s), Honest rc 0 (52.6 s).

  So the B2 lemmas that Basic uses are also covered by an auditor-built replay.
  Details are in data/leanchecker_replay_audit.json.
- **Faithfulness.** `Encloses` (Basic.lean:182-185) says exactly main.tex:129. The equivalence of `segment_neg0`/`segment_pos0`/`classification`/`along_path` with T1-T5 holds as conditional statements. See NB-8 for the over-quantification.

### (3) Certifier (n1_certify2.py with n1_certify.py)
- **Rigour, from reading.**
  - All arithmetic is arb (96 bits). Endpoints go to rationals outward (`q_down` floor and `q_up` ceil at 1e-9, from mid -+ rad). Q and R are rounded separately, then summed (sound).
  - f bounds: |f^(k)| <= 1/((k+1)(k+2)) follows from f = int_0^1 (1-u) cos(ux) du. `f3_ball` uses the right Taylor remainders (r^2/24, r^2/40, r/20) and intersects with [0, 1/2], [-1/6, 1/6] and [-1/12, 1/12].
  - `f_thin`'s series remainder (2 x the first omitted term, ratio <= x^2 <= 1/4) is conservative.
  - Mean-value tightening (class P, `ball`) is valid. Value in val(c) + grad(box)·Delta, and grad in grad(c) + Hess(box)·Delta, with Delta covering |x - c| for the exact centre: the centre balls contain the exact rational centre, and rad(dS) >= h/2, rad(dA) >= delta. This holds uniformly in t, because centre and ball jets share the same t-ball.
  - Taylor forms in a for H_n (Model2:281-288) are correct: hull(0, delta^2/2 H_aa).
- **Lattice tail (`tail_bound`).**
  - Shells use polynomials at the outer radius and the Gaussian at the inner radius, with count pi(r+1)^2.
  - |theta| <= 2 pi r/C holds because max(|m-l|, |m+l|) <= 2 sqrt(m^2+ml+l^2). I checked this, and |beta| <= sqrt2 th.
  - The weight bound W dominates every partial of 2 theta^2 f(s theta) up to order 2. I checked it term by term.
  - The a-factor 1 + L + L^2 bounds d/da and d^2/da^2 of e^{-pi a q} P(a), with deg P <= 4 and nonnegative coefficients.
  - The polynomial degree is <= 4 + 6 + 4 = 14 <= DEG = 16.
  - The geometric ratio is computed, and each of its factors decreases in r.

  Rigorous. It is also not load-bearing: max tail T = 2.9e-11 and max rho_K = 3.7e-25, against sign margins >= 0.0152.
- **Re-runs (venv Python 3.11 + python-flint 0.6.0 from .scratchpad/b2_pylib, core 6, timeout 1800 s, copies of the hashed scripts).**
  - Inside, a in [1, 51/50] (N 32, depth 1, qmax 20): sign neg, F in [-7.79198, -7.40485]. Every field (ok, sign, Q, D, R, Epp_window, stats, qmax, n_lattice_half, tail_T, tail_rho_K, script_sha256) is **identical** to runs/sweep_inside_hi.json.
  - Outside, a in [1973/1000, 2] (qmax 11): sign pos, F in [3.46861, 4.26608]. Identical to runs/sweep_right_kept.json.
  - Control, a = 2/5 thin (N 32, depth 2, qmax 50): sign **neg**, F in [-0.69199, -0.58681]. Identical to runs/sweep_pts_extra.json. A "local minimum" claim at a = 0.40 is therefore impossible.
    The kernel side: RejectInside rc 1 and Honest `inside_not_pos` rc 0.
  - Tampered certificate (a = 93/250 with qlo sign flipped): RejectTampered rc 1. Honest `tampered_not_pos` rc 0 (kernel: allPos = false) and `untampered_pos` rc 0.

### (4) Overclaims
- The full iff is explicitly **not** claimed. See the abstract at main.tex:59, :85, :245 and :312.
- The a ~ 0.123 sign change is cited from P2 as Tier X, as the reason no simple iff is expected. It is not a claim of this paper. Correct.
- The uncertified regions are listed honestly in main.tex:233-245: (0.33, 0.3745), (0.383, 0.425), a < 0.33 with the failed points 0.25 (104 cells) and 0.30 (9 cells), and a > 4. I checked every count against cert_summary.json and the runs.
- "Strict local minimum over shapes" (T6, Section 8) is conditional on four Tier C-human items. It is never used for T1-T5. Correctly scoped.
  T4 (inside: not a local minimum over shapes) needs no extra assumption. Correct.
- Remaining wording issues: NB-1, NB-2 and NB-3.

### (5) Ledger gate
I re-ran `tools/ledger.py ledger.json --evidence-dir evidence` into /tmp/n1audit/gate_rerun.txt: exit 1, 0 blocking, 8 flags (LEDGER_UNAUDITED_TIER_A for PZC-A-0001..0008). The output is byte-identical to ledger/gate_output.txt, apart from the `exit_code` line. This is the honest state.
