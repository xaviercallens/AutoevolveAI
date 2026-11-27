# E3 independent audit (2026-11-01)

Auditor: independent agent (producer != verifier). Scope: `results/proposal4/2026-10-27/E3/` and
`formal_cert/Programmes/LowDissE3/{Core,Instances,Engine,Axioms,Controls}.lean`. Nothing in the subject was edited;
scratch work under `/tmp/e3audit/` (cores 2,3 only). Hashes: `prereg_E3.json` sha256
`aee87a670acbe5819a79b289a7c2e0e1a0f7c59b2e7d878eca5e2394717daf5a` (matches); all 32 `files_sha256` entries of
`result.json` match the files on disk.

**Verdict: ACCEPT_WITH_CORRECTIONS.** The Lean mathematics checks (see section 2). Two wording claims must change
(literature status of Eq. (1); "tight"), and the physical meaning of `etaPlus` still rests on a hand derivation,
not on Lean. Tier A stays pending the statement lock.

## 1. Source and model (read from the PDF page images, arXiv:1802.09806v4 pp. 1-3, Appendix B)

* Model: low-dissipation Carnot cycle, Q_x = Q_x^(r) - M_x/t_x (Eq. 2), P and eta from Eqs. (3), (4), with
  q = eta_C Q_h^(r): P = (q - Mh/th - Mc/tc)/(th+tc), eta = (q - Mh/th - Mc/tc)/(Q_h^(r) - Mh/th). `engine_bound`'s
  hypotheses `hP`, `he`, `hQ` (denominator Q_h > 0) are exactly these with a = sqrt Mh, b = sqrt Mc, Q_h^(r) = q/c.
  Pmax = q^2/(4M) (Eq. 6), so `hPt : Pt q^2 = 4 (a+b)^2 P` is P~ = P/Pmax. Faithful.
* eta~+ (Eq. 11): the paper maximises eta over th + tc = tau+ (Eq. 10, the largest cycle time compatible with power
  P via Eq. 9), using that eta increases in th and tc. It is therefore an UPPER BOUND on the efficiency of every engine
  with normalised power P~ and asymmetry zeta (Eq. 14), obtained by relaxing the exact power constraint. It is not
  the exact constrained maximum: the paper itself says "it is not a supremum for all the P~" (p. 3).
* My own derivation of the root form: eta >= u c is reachable on th + tc = tau+ iff
  q(1-u) tau+ >= min_{th+tc=tau+} (w^2 a^2/th + b^2/tc) = (w a + b)^2 (Cauchy-Schwarz, attained at th/tc = w a/b),
  w = sqrt(1 - c u), and q tau+ = K M with K = 2/(1 - sqrt(1-P~)). This is G(w,zeta) = K(w^2-(1-c)) - c((1-zeta)+(1+zeta)w)^2/4 >= 0;
  G(0) < 0 and G is a convex quadratic (qA > 0), so the feasible set is w >= w+ and eta~+/eta_C = (1 - w+^2)/c.
  This is exactly Lean's `G`, `wPlus`, `etaPlus` (Core.lean). Defining `etaPlus` as the root form is faithful to Eq. (11).
* Eq. (13) as printed (300 dpi crop): the square-root vinculum ends after "+ 1 - eta_C"; the term
  -((1+zeta)/4) eta_C (1 - sqrt(1-P~)) is OUTSIDE the root, inside the square bracket. The producer's corrected
  transcription (`code/link_funcs.py`) is right; the preregistered one was wrong, as the producer reported.
* Eq. (13) = root form, independently (`/tmp/e3audit/sym_audit.py`):
  - symbolic (sympy): eliminating w from the tangency equality by squaring twice gives a quadratic R(u) = 0 in u;
    R(u13(x)) reduces to 0 modulo x^2 - radicand, so both sign branches of Eq. (13) are roots of R (an identity, not a
    numerical fit);
  - branch selection (mpmath, 50 digits, 5000 random (c, P~, zeta)): + branch vs root form max |diff| 5.0e-48;
    - branch 0.47; "term inside the root" reading 0.23. Minimum radicand over the sample 2.0e-3 > 0.
  So Eq. (13) is the root form, with the branch identified numerically. This is stronger than the producer's
  numerical-only link but is still not in Lean.
* Appendix B (p. 7): "the analytical proof of its monotonicity is tedious and difficult. Instead numerical calculate
  the derivative" - transcribed correctly by the producer.

## 2. Lean (clean rebuild, pinned Lean 4.34.1, fresh olean dir /tmp/e3audit/olean)

Driver `/tmp/e3audit/build.py` = `scripts/certified_numerics/lean_pinned.py` with `OUT` redirected to an empty
`/tmp/e3audit/olean` (LEAN_PATH = pinned openai/math `.lake` + toolchain lib + `/tmp/e3audit/olean` only; the repo's
`formal_cert/.olean_out` was NOT on the path). Cores 2,3.

| step | rc | seconds |
|---|---|---|
| Core.lean -> olean | 0 | 14.1 |
| Instances.lean -> olean | 0 | 6.7 |
| Engine.lean -> olean | 0 | 400.8 |
| Axioms.lean | 0 | 5.4 |
| Controls.lean (planted, compiled stand-alone) | 0 | 6.4 |
| leanchecker Core / Instances / Engine | 0 / 0 / 0 | 55.0 / 39.8 / 48.9 |
| leanchecker Programmes.LowDissE3.DoesNotExist (negative control) | 1 ("Could not find any oleans") | 42.4 |

* `#print axioms`: 27/27 theorems print exactly `[propext, Classical.choice, Quot.sound]` (whitelist). No warnings or
  errors in Core/Instances/Engine output.
* Controls: `ctl_sorry` -> `[propext, sorryAx, Classical.choice, Quot.sound]` (plus "declaration uses sorry" warning),
  `ctl_axiom` -> `[..., LowDissE3.ctl_cheat, ...]`; both rc 0, i.e. only the axiom gate catches them, as claimed.
  Controls.lean is imported by nothing (grep over *.lean/*.toml/*.py; `formal_cert/` has no lakefile globbing it).
* Escape grep over the five files (sorry, admit, axiom, native_decide, implemented_by, extern, unsafe, addDecl,
  ofReduceBool, skipKernelTC, opaque, set_option, macro, elab): hits only in Controls.lean (planted) and one
  `set_option maxHeartbeats 3000000 in` on `engine_bound` (Engine.lean:23). Raising heartbeats is an elaboration
  budget only; the term is re-checked by leanchecker (rc 0), so it is benign.
* Compile time of Engine (401 s) matches the producer's 387 s.

## 3. Reading the proofs for vacuity and scope

* Hypotheses are consistent: `inst_eta_neg`/`inst_eta_pos` instantiate c = 48/49, K = 2 (P~ = 1); `esposito_sandwich`
  holds for every c in (0,1). The box is non-empty.
* `etaPlus_strictMono` quantifies over all c in (0,1), K > 1, -1 <= zeta1 < zeta2 <= 1: strict monotonicity on the
  whole box, quantifiers in the right direction. K > 1 is a superset of the physical K = 2/(1-s) in [2, inf).
* `eq1_of_P` covers P~ = 1 - s^2 with s in [0,1), i.e. P~ in (0,1]; P~ = 0 not formalised (trivial).
* `engine_bound` covers every engine of Eqs. (3)-(4) with Mh, Mc > 0, q > 0, th, tc > 0, P > 0 and positive hot-bath
  heat; no restriction to a sub-family. P~ <= 1 is derived, not assumed. Engines with Mh = 0 or Mc = 0 (zeta = -1, 1)
  are excluded (limits only). There is no Lean instance of `engine_bound`'s hypotheses; non-vacuity is shown
  numerically (53,021 sampled engines below satisfy them).
* GAP (not in Lean): no theorem states that an engine with asymmetry zeta satisfies eta/eta_C <= etaPlus(zeta).
  `engine_bound` avoids zeta (it uses w <= 1). Hence `etaPlus_strictMono` is a theorem about the root form; that the
  root form is the paper's eta~+ rests on the derivation above (and on `code/derivation.md`) and on numerics, not Lean.
  The missing lemma is short (CS => G(w,zeta) >= 0 => w >= wPlus via `root_unique`/convexity) and would close it.
* `pert_eta_not_mono` is a restatement of `inst_eta_pos`/`inst_eta_neg` at negated arguments; it shows the controls
  machinery works but is weak as a negative control.

## 4. Independent numerics (`/tmp/e3audit/num_audit.py`, mpmath 40 digits / floats)

* zeta-monotonicity of the root form: 41 c-values (0.001 ... 0.999) x 41 P~-values (1e-6 ... 1) x 201 zeta:
  336,200 consecutive pairs, 0 non-increasing, smallest increment 1.25e-12 (at small c, consistent with the
  derivative vanishing as c -> 0).
* Random engines from Eqs. (3)-(4) (a, b, q log-uniform in [1e-2, 1e2], th, tc in [1e-3, 1e3], c in (0.001, 0.999),
  kept if P > 0 and Q_h > 0): 53,021 engines, 0 violations of Eq. (1) (tolerance 1e-12), 0 violations of the
  zeta-specific bound eta/eta_C <= etaPlus(zeta); the perturbed (1-c -> 1+c) Eq. (1) is violated by 20,112.
* Brute force (exact power constraint P(th,tc) = P solved for tc, 40,000 th-values): at 8 random (a, b, q, c, P~)
  root form - brute optimum in [1.3e-5, 6.6e-3], all >= 0. eta~+ is a valid upper bound, NOT attained in general
  (the tau = tau+ equality needs th/tc = a/b, the efficiency Cauchy-Schwarz equality needs th/tc = w a/b).

## 5. Literature (alphaXiv, 2026-11-01)

* **Eq. (1) already has analytic proofs.** Ma & Fu, "Unified approach to power-efficiency trade-off of generic
  thermal machines", arXiv:2411.03849 (PRE 112, 054130 (2025)), Appendix B: they prove ANALYTICALLY (sign of
  d eta~+/d delta) that their upper bound eta~+(delta) increases in the dissipation ratio delta in [0,1], and at
  delta = 1 obtain their Eq. (14), identical to Ma 2018 Eq. (1). Yu-Han Ma is the first author of the source paper.
  Zhai, arXiv:2605.02732 (2026), re-derives the same Eq. (1) by a short geometric/linear-programming argument.
  Zhai-Yue-Sun, arXiv:2509.07721, state that Ma 2018 already "rigorously proved" the Holubec-Ryabov conjecture and
  give an exact (tighter) bound. Holubec-Ryabov 2016 (arXiv:1603.02551, read): their Eq. (34) upper bound equals Eq. (1);
  derived analytically only near P~ = 1 and P~ = 0, numerical evidence in between. Ye-Holubec 2021 (2112.08923) is about
  heat pumps (not relevant).
* **zeta-monotonicity of Eq. (13) itself: no analytic proof found.** Ma-Fu's delta-family is a different interpolating
  family: it agrees with the root form at zeta = -1 (delta = 0) and zeta = 1 (delta = 1) but differs in between
  (max 0.038 under delta = (1+zeta)/2; 0.40 and 0.055 under two other natural maps; `/tmp/e3audit/mafu_cmp.py`).
  Their proof is the closest analogue (same "derivative sign" style) and must be cited.
* Consequence: `engine_bound`/`eq1_of_P` are machine checks of a KNOWN result (to our knowledge the first
  machine-checked ones), not new mathematics. Only `etaPlus_strictMono` (zeta-monotonicity of the paper's
  eta~+, which the paper checked numerically) has a modest novelty case, and it is elementary.

## 6. Corrections (exact old -> new)

1. RESULT.md, Numerical link bullet 4: "Root form is a tight upper bound on a brute-force float optimum of the actual
   engine (8 points, root - brute in [4.8e-7, 2.2e-3], all >= 0), Tier X." -> "Root form is a valid upper bound on a
   brute-force float optimum of the actual engine at exactly given power (8 points, root - brute in [4.8e-7, 2.2e-3],
   all >= 0; auditor: 8 other points, [1.3e-5, 6.6e-3]); it is not attained in general (the paper: 'not a supremum for
   all the P~'; Zhai-Yue-Sun arXiv:2509.07721 give the exact, tighter bound), Tier X."
2. RESULT.md, Literature: "Web search found no paper giving an analytic proof; the arXiv paper itself says it only
   checked numerically. Holubec-Ryabov 2016 (1603.02551), Ye-Holubec 2021 (2112.08923) and Esposito et al. 2010 are
   NOT re-read here, so a published proof cannot be excluded." -> "No paper found giving an analytic proof of the
   zeta-monotonicity of Eq. (13); the source paper checked it only numerically (Appendix B). The zeta-free bound Eq. (1)
   IS analytically proved in the literature: Ma & Fu, arXiv:2411.03849 (PRE 112, 054130 (2025)), Appendix B prove
   analytically that their bound is increasing in the dissipation ratio delta and obtain Eq. (1) at delta = 1 (a different
   interpolating family; it coincides with Eq. (13) only at zeta = +-1, auditor check); Zhai, arXiv:2605.02732, re-derives
   it geometrically. Holubec-Ryabov 2016 (read by the auditor) derive the same bound analytically only near P~ = 0 and
   P~ = 1. Ye-Holubec 2021 concerns heat pumps. Esposito et al. 2010 not re-read."
3. RESULT.md, `engine_bound` bullet: append "This is a known result (Ma & Fu 2024 App. B; Zhai 2026); new here is only
   the machine check."
4. RESULT.md, Literature: "To our knowledge there is no machine-checked proof of this statement." -> "To our knowledge
   there is no machine-checked proof of either statement (zeta-monotonicity of eta~+, Eq. (1)); only the
   zeta-monotonicity lacks a published analytic proof."
5. RESULT.md, Scope bullet 2: "it does not prove that eta+ is the supremum." -> "it proves neither that eta+ is attained
   nor that every engine with asymmetry zeta has eta/eta_C <= etaPlus(zeta); the latter rests on code/derivation.md
   steps 1-3 (checked by the auditor) and numerics (0 of 53,021 random engines violate it)."
6. code/derivation.md step 3: "eta+ is the largest u (equivalently smallest w) for which this holds with equality being
   attainable: the tangency" -> "eta+ is the largest u (equivalently smallest w) for which this holds, i.e. the maximum of
   eta over th + tc = tau+ (an upper bound at power P, not attained in general): the tangency"
7. RESULT.md "Numerical link" bullet 1: append "Auditor: symbolically, both sign branches of Eq. (13) are roots of the
   squared-out tangency quadratic R(u) (sympy remainder 0 modulo x^2 - radicand); the + branch equals the root form to
   5e-48 at 5000 random points, the - branch differs by up to 0.47."
8. RESULT.md, Controls N1: append "(`pert_eta_not_mono` is a restatement of inst_eta_pos/inst_eta_neg at negated
   arguments; weak as a negative control)".
9. Any paper/commit text: keep "elementary", "model-conditional (phenomenological low-dissipation model, Eqs. (2)-(4))",
   "no device or power-plant claims", "to our knowledge the first machine-checked proof"; never "first proof of Eq. (1)"
   and never "tight".

## 7. What remains unverified

* Lean link "engine with asymmetry zeta => eta/eta_C <= etaPlus(zeta)" (numerics only, 0/53,021 violations).
* Eq. (13) = root form: symbolic up to the sign branch; branch chosen numerically; not in Lean.
* Statement lock (Tier A pending). P~ = 0 and Mh = 0 / Mc = 0 endpoints not formalised.
* Esposito et al. 2010 not re-read (only used as positive control at P~ = 1; values 1/2 and 1/(2-c) reproduced).
* The two-level-atom engine, any real device: out of scope (idealised model, no device claims).
