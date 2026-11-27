# E3 RESULT: kernel-checking the zeta-monotonicity behind the low-dissipation efficiency-power bound (2026-10-31)

Outcome: **KEEP** (producer, unaudited; Tier A pending statement lock). Model statement about a phenomenological low-dissipation
Carnot engine, no claim about any real engine. Preregistration `prereg_E3.json` sha256 `aee87a670acbe5819a79b289a7c2e0e1a0f7c59b2e7d878eca5e2394717daf5a`
(written before any attempt); parent preregistration unchanged (sha256 7f7d5ac1...b438). Cores 2,3 only. Within the first budget.

## Pinned statement
Ma, Xu, Dong, Sun, arXiv:1802.09806v4: Eq. (13) `eta+(P,zeta,eta_C)`, Eq. (1) universal bound, Appendix B ("analytical proof ... tedious and difficult. Instead numerical calculate the derivative").
PDF in `/home/callensxavier_gmail_com/e3_thirdparty/` (outside the repo).

## What was proved (Lean 4.34.1, pinned Mathlib, `formal_cert/Programmes/LowDissE3/`)
For `0<c<1` (eta_C), `1<K` (K = 2/(1-sqrt(1-P)), any P in (0,1]), `zeta in [-1,1]`, with `etaPlus c K zeta := (1 - w+^2)/c`, `w+` the explicit positive root of the paper's tangency quadratic:
* `etaPlus_strictMono`: zeta1 < zeta2 implies etaPlus(zeta1) < etaPlus(zeta2) (strict, full box). This is Appendix B's claim, for the root form of the paper's own definition (see E3link).
* `etaPlus_le_one_value`, `eq1_of_P`: etaPlus(zeta) <= etaPlus(1) = (K-1)/(K-c) and Eq. (1): `eta/eta_C + (1-c)P/(2(1+s)-cP) <= 1` for P in (0,1] (P=0 trivial, not formalised).
* `engine_bound` (Engine.lean): the engine-level Eq. (1) for every engine (a=sqrt Mh, b=sqrt Mc, q, c, th, tc > 0, P > 0, positive hot-bath heat) from the paper's Eqs. (3)-(4) directly, without zeta and without Eq. (13) (uses Cauchy-Schwarz, the quadratic P tau^2 - q tau + M <= 0, and w <= 1). Heartbeat limit raised (`set_option maxHeartbeats 3000000 in`), compile 387 s.
* `esposito_sandwich` (positive control): at P = 1, 1/2 <= etaPlus <= 1/(2-c) (Esposito et al. EMP bounds eta_C/2 <= eta* <= eta_C/(2-eta_C)), endpoints attained at zeta = -1, 1.
* Not proved in Lean: that Eq. (13) as printed equals the root form (numerical link only, Tier C/X below); that eta+ is attained; P = 0 case; the physics of the model.

Audit: `#print axioms` of all 27 theorems = {propext, Classical.choice, Quot.sound} (`logs/lean/axioms.json`). `leanchecker` rc 0 for Core, Instances, Engine (`logs/leanchecker_replay.json`). Escape grep (sorry, native_decide, admit, unsafe, extern, implemented_by, axiom, opaque, macro, elab, set_option) on Core and Instances: no match; Engine.lean has exactly one `set_option maxHeartbeats` (benign, declared). Axioms.lean matches `axiom` only through `#print axioms`.

## Numerical link (Tier C/X, not Lean)
* Eq. (13) as printed vs the root form: after one transcription correction (see deviations), max |difference| 1.6e-58 over 3000 random (c,P,zeta) at 60 digits (`logs/link.log`).
* Eq. (1): 0 violations by the root form (3000 points) and 0 violations in 17,355 random exact-rational engines (max LHS 0.99999091, so the bound is nearly attained) (`data/numerics2.json`).
* Root-form monotonicity grid: 124,800 consecutive-zeta pairs at 60 digits, 0 non-increasing.
* Root form is a tight upper bound on a brute-force float optimum of the actual engine (8 points, root - brute in [4.8e-7, 2.2e-3], all >= 0), Tier X.
* E3x (Tier X, float, implicit differentiation, 801,900 grid points): d eta+/d zeta > 0 everywhere; minimum 1.2e-5 at the corner c = 0.01, P = 0.01, zeta = 1; maximum 0.34 at c = 0.99, P = 1, zeta ~ 0.575. The derivative vanishes as c -> 0 (at P = 0.5, zeta = 0: 6.3e-4, 6.3e-3, 3.4e-2, 6.9e-2 for c = 0.01, 0.1, 0.5, 0.9), consistent with the paper's remark that the curves merge for small eta_C; for c in (0,1) it is strictly positive (Lean).

## Controls
* P1 Esposito sandwich: Lean-proved and numerically checked (exact 1/2 and 1/(2-c) values at P=1). Passed.
* P2 known monotone / machinery: root-monotonicity run on the exact rational instance c = 48/49, K = 2: roots 5/7 (zeta=-1) and 1/5 (zeta=1), eta 1/2 and 49/50 (Lean `inst_*`). Passed.
* P3 Eq. (13) transcription agreement: passed after the correction.
* N1 perturbed factor (zeta -> -zeta): on the same instance the perturbed roots increase (1/5 < 5/7) and the perturbed eta decreases 49/50 -> 1/2; Lean `pert_eta_not_mono` kernel-checks that monotonicity fails for it; grid: 15,200/15,200 pairs non-increasing. Caught.
* N2 other perturbations (grid): B sign flipped 5,920 bad pairs, K halved 611, C sign flipped 13,256 (558 undefined): all caught; true formula 0 bad.
* N3 planted `sorry` and planted axiom (`Controls.lean`, not imported): axiom gate shows `sorryAx` and `LowDissE3.ctl_cheat`. Caught.
* N4 mistyped Eq. (13) (sign of zeta inside the root): differs by up to 0.156. Caught.
* Perturbed Eq. (1) (`1-c` -> `1+c`): violated by 11,522 of 17,355 random engines. Caught.

## Literature (kill criterion ii)
Web search found no paper giving an analytic proof; the arXiv paper itself says it only checked numerically. Holubec-Ryabov 2016 (1603.02551), Ye-Holubec 2021 (2112.08923) and Esposito et al. 2010 are NOT re-read here, so a published proof cannot be excluded. To our knowledge there is no machine-checked proof of this statement. The mathematical content is elementary (a root of a quadratic is monotone because the quadratic is monotone in the parameter); the proof does not use Eq. (13) in closed form, and the paper's "tedious" difficulty looks like an artefact of working with the closed form. Not presented as a deep result; no breakthrough claim.

## Scope and honesty
* `etaPlus` is defined as the root form; the identification with Eq. (13) is numerical (1.6e-58), not proved in Lean. The identification of the root form with the paper's own optimisation (tangency, Eq. (12)) is by the hand derivation in `code/derivation.md` and independently by the engine-level Lean theorem (which gives the zeta-free Eq. (1)) and by brute force numerics; an auditor should check it.
* zeta-monotonicity as stated for the paper's eta+ (not an engine optimum): the engine-level Lean theorem proves the universal bound Eq. (1) only; it does not prove that eta+ is the supremum.
* The low-dissipation model is an idealisation; nothing here concerns a real engine or power plant.

## Deviations from the preregistration
1. The preregistered transcription of Eq. (13) put the term `-((1+zeta)/4) eta_C (1-sqrt(1-P))` inside the square root. The page image shows it outside. First reading disagreed with the root form by up to 0.23 (`logs/link_first_transcription.log`); corrected reading agrees to 1e-58. Recorded, prereg file not edited. The preregistered "E3link disagreement is reported first" rule was followed (diagnosed as a transcription error by the symbolic structure `code/sym.py` and the page image).
2. `set_option maxHeartbeats 3000000` in Engine.lean (one declaration).
3. Two Lean reformulations of the preregistered statements: root form parametrised by K = 2/(1-sqrt(1-P)); P = 0 not formalised.
4. The preregistered N1 "w=3/5, c=4/5, u=4/5" data was replaced by c = 48/49, K = 2, roots 5/7 and 1/5 (both rational).

## What an independent auditor must redo
1. Re-read arXiv 1802.09806 Eq. (13)/(14)/(1)/(3)/(4) from the PDF and confirm the transcription in `code/link_funcs.py` and `etaPlus`'s root form (derivation.md steps 1-3); check `engine_bound`'s hypotheses against Eqs. (3)-(4).
2. Statement lock: review `Core.lean` (`G`, `wPlus`, `etaPlus`, theorem statements), `Engine.lean`, `Instances.lean`.
3. Rerun: `python3 scripts/certified_numerics/compile_modules.py <dir> 1 Programmes.LowDissE3.Core Programmes.LowDissE3.Instances`, compile `Engine.lean` (about 6.5 min), `Axioms.lean`, `Controls.lean`, `code/leanchecker_replay.py` (args: three module names), `code/link.py`, `code/numerics2.py`.
4. Read Holubec-Ryabov 2016 and Ye-Holubec 2021 for an existing analytic proof of the monotonicity or of bounds (34).

## Files
`prereg_E3.json`, `prereg_E3.sha256`, `code/` (link.py, link_funcs.py, diag.py, sym.py, numerics2.py, leanchecker_replay.py, derivation.md, make_result_json.py), `data/numerics2.json`, `logs/`, `result.json` (sha256 of every file). Lean: `formal_cert/Programmes/LowDissE3/{Core,Instances,Engine,Axioms,Controls}.lean`.
