# K3 independent audit (producer != verifier)

Auditor: an independent AI agent (Claude), 2026-10-31. It did not use any producer code: no `k3lib.py`, `run_*.py` or producer oleans for Core. Cores 4,5 only. Scratch is in `/tmp/k3audit/` and is not part of the bundle. No human expert has reviewed this audit.
Subject: `results/proposal4/2026-10-27/K3/` (prereg sha256 `fc9571ec1eb29f99cd12dd5504efdaaa9dfa55f2b1f1938581573c63a6868699`, rechecked) and `formal_cert/Programmes/CarbonK3/{Core,Controls}.lean` (Core sha256 `00e6ba6c...363a`, matches `result.json`).

**Verdict: ACCEPT_WITH_CORRECTIONS.** Every number I recomputed agrees with the producer's. The corrections concern wording, scope and prior art. None of them changes a certified value.

## 1. Sources and model definitions
* **Joos et al. 2013, Table 5, row IRFCO2** (`k3_thirdparty/joos/j.txt` l.720): a0..a3 = 0.2173, 0.2240, 0.2824, 0.2763 and tau1..tau3 = 394.4, 36.54, 4.304 yr. All nine numbers are confirmed, with a1↔394.4, a2↔36.54, a3↔4.304 as in the producer's code. The sum is exactly 1. The PDF header reads "CC Attribution 3.0 License". Eq. (11) states the fit applies **only for 0 ≤ t ≤ 1000 yr**. Eq. (7) and its text define the IRF as the fraction of an added pulse that is still airborne, and the change in the atmospheric inventory as the convolution of emissions with the IRF.
* **Seshadri (arXiv 1502.00805v3)** defines u(t) = uP + ∫_0^t m(z) h(t−z) dz (eq. 2). Here m is "emissions in concentration units", i.e. the rate of concentration rise if the lifetime were infinite, and u is the concentration. Eq. (1) prints 0.276/0.282/0.224/0.217 (sum 0.999) with τ 4.30/36.5/394, and the text uses τ1 = 4.4. Sect. 3.2 uses (1+r)^t ≈ e^{rt} and "consider[s] only the case where r > 1/τm". All of this is confirmed as the producer reports it.
* **Meaning of "concentration maximum" in K3.** It is a local maximum of the *model* excess u(t) − uP for the linear IRF model. It is not a statement about the real atmosphere. "Two maxima" should mean that u is not quasi-concave: there are two local maxima separated by a strictly lower value. The five-point certificate u(s1)<u(s2)>u(s3)<u(s4)>u(s5) establishes exactly this.
* **Unimodality of the inputs, checked from the node lists in `run_c.py`:**
  * I1 is *weakly* unimodal: non-decreasing on [0,10], non-increasing afterwards, with a plateau on [22,300].
  * S1 is a non-increasing step function, so it is weakly unimodal with its mode at 0.
  * I2, with nodes (0,0),(10,1),(22,0.1),(300,0.05),(310,0), is **strictly** increasing on [0,10] and strictly decreasing on [10,310], then 0. It is continuous.
  * So the existence claim in (c) holds under the strict definition of single-peaked emissions (unique mode, strictly monotone on each side within the support), not only under the weak one.

## 2. Independent recomputation
* **(c) instances.** I used Sage RealBallField at 400 bits (arb, not mpmath), with my own closed-form segment integrals ∫(α+βz)e^{-(t−z)/τ}dz. The u values at all 15 times agree with `results_c.json` to the 20 printed digits. The ball radii are ≤ 5e-116. Lower bounds on the four differences:
  * I1: 3.780, 0.3130, 7.794, 0.5732
  * I2: 3.780, 0.2776, 4.435, 0.5618
  * S1: 3.370, 0.3216, 6.586, 3.349

  All are positive. Sage `numerical_integral` of the convolution at 6 points agrees to about 1e-14.
* **(b) peak times.** I used my own closed form for u′ with mpmath at 50 digits, a scan with step 0.5 yr on [0,3000], then `findroot` (Anderson). For all 21 Joos scenarios there is exactly one +→− sign change of u′. The scan used a different grid and end point from the producer's [0,6000] scan, so this is a Tier X cross-check of that claim. My t2 agrees with the producer's enclosures to ≤ 6.0e-20. t1 agrees in every cell. This is agreement with a floating root-finder, **not** an independent interval certificate of uniqueness.
  * Seshadri-coefficient variants (τ1 = 4.30 and 4.4) for (r, τm) = (0.03,50), (0.015,50), (0.05,120): the delays differ from Joos by 0.06–0.35 yr, which is consistent with the producer's "≤ 0.36 yr".
  * Boundary: at ln(1.03) = 1/τm (τm ≈ 33.83086) the peak time t2 is continuous (98.28871 on both sides). The delay jumps by exactly tg = 60 yr because t1 jumps. This confirms the producer's "not monotone in τm" remark and its explanation.
* **T3/T2 numerics (floats).**
  * Joos, d = 5, h(5) = 0.7712. For θ = B/A ∈ {0.8, 0.95} the staircase has **exactly two** maxima (t = 5 and t = z3) and one minimum, at the predicted d+x*. For θ ∈ {0.5, 0.65, 0.7} (< h(d)) there is exactly one maximum, at z3.
  * a0 = 0 two-exponential IRF (τ = 100, 5; L = e^{-0.05} = 0.9512): two maxima for θ in (h(d), L), one maximum for θ < h(d) and for θ > L.
  * ρ(x) = h(x+d)/h(x) is strictly increasing on a [0,500] grid for both IRFs. A first double-precision run reported "not increasing" for the a0 = 0 IRF; this was float saturation of e^{-x/5}. At 60 digits it is strictly increasing, with ρ(500) = L to 15 digits.
  * T2 adversarial test: 400 random weakly unimodal staircases with h = e^{-t/30} gave at most one +→− sign change of u′ and no −→+ change.

## 3. Hand re-derivation
* **T3 is correct.** For staircase jumps c_j, u′(t) = Σ c_j h(t−z_j). For a CM h = ∫e^{-λt}μ(dλ), Cauchy–Schwarz gives log-convexity, with equality only if μ is a point mass. So ρ is strictly increasing unless h is a single exponential, with ρ(0) = h(d) and ρ(∞) = L (L = 1 if a0 > 0, else e^{-d/τmax}).
  * The producer's justification of u′(z3+) < 0, "use h(x) ≤ 1", is incomplete. The correct reason is u′(z3+) = −A(1−h(z3)) + B(1−h(z3−d)) < 0, because A > B and h(z3) < h(z3−d) ≤ 1.
  * The same argument gives more than the producer states. u′ = A h(t) > 0 on (0,d), and u is completely monotone after z3, so the staircase has **exactly** two maxima.
  * Within this family the window is also necessary. If θ ≤ h(d), then u′ > 0 on (d, z3) and the only maximum is at z3. If θ ≥ L, then u′ < 0 on (d, z3) and the only maximum is at d.
* **T2 is correct as unimodality, but its wording is literally false for non-strict maxima.** With g = e^{t/τ}u′ we have dg = e^{t/τ}dm, so u′ is ≥ 0 and then ≤ 0, i.e. u is quasi-concave. Counterexample to "at most one local maximum": h = e^{-t/τ}, an impulse cτ at 0 (allowed in the discrete setting), then constant emission c until T. Then u′ = c − u/τ = 0, u ≡ cτ on (0,T), and every point there is a local maximum. I found no counterexample to the quasi-concave formulation.
* **Prior art for T2 and for the mechanism.** By Ibragimov (1956, "On the composition of unimodal distributions", Teor. Veroyatn. Primen. 1(2), 283–288; English transl. Theory Probab. Appl. 1; "strong unimodality"), convolution with every unimodal density preserves unimodality if and only if the kernel is log-concave.
  * The one-sided exponential e^{-t/τ}1[t≥0] is log-concave, so **T2 is a special case of Ibragimov's theorem.**
  * A CM kernel that is not a single exponential is strictly log-convex on (0,∞), so Ibragimov's converse already implies, for integrable kernels (a0 = 0), that *some* unimodal input yields a non-unimodal output.
  * For a0 > 0 the IRF is not integrable, so Ibragimov's theorem as stated does not apply directly. T3 covers this case by explicit construction.
  * What K3 adds is the explicit staircase window B/A ∈ (h(d), L), its necessity within the family, the certified Joos instances, and the carbon-cycle framing. I have not checked Ibragimov's original text; the statement above comes from secondary sources (Encyclopedia of Mathematics, "Unimodal distribution"; Watanabe, Nagoya Math. J. 1991).

## 4. Lean (recompiled by the auditor)
I compiled Core with the pinned Lean 4.34.1 toolchain and LEAN_PATH taken from `scripts/certified_numerics/lean_pinned.py`. The Core olean went to a private directory `/tmp/k3audit/olean`. The dependency oleans `Programmes.CompletelyMonotone.*` and `Autoresearch.KeldyshCM` were **reused, not rebuilt**. `#print axioms` and leanchecker are transitive, so they still cover those dependencies.
* Core: rc 0 in 13.6 s. All six theorems (`irf_cm`, `excess_cm_after`, `excess_antitone`, `excess_convexOn`, `excess_tendsto`, `neg_ctl_not_cm`) depend on `[propext, Classical.choice, Quot.sound]`.
* `leanchecker Programmes.CarbonK3.Core`: rc 0 in 61.4 s.
* Escape grep on Core.lean (sorry, native_decide, admit, unsafe, extern, implemented_by, axiom, opaque, set_option, csimp): no match.
* Controls: rc 0, as expected for planted controls. The axiom gate catches both:
  * `ctl_sorry` → `[propext, sorryAx, Classical.choice, Quot.sound]`
  * `ctl_axiom` → `[propext, CarbonK3.ctl_cheat, Classical.choice, Quot.sound]`
* `IsCompletelyMonotoneOn` (ProgCM, `Basic.lean` l.28) is the genuine definition: C^∞ on (0,∞) and (−1)^n f^(n) ≥ 0.
* **What is proved.** The IRF a0 + Σ a_i e^{-r_i t} with a0, a_i, r_i ≥ 0 is CM. For finitely many nonnegative point masses w_j at z_j ≤ T, s ↦ Σ w_j h(s+T−z_j) is CM, antitone and convex on (0,∞). It tends to a0Σw_j if all r_i > 0; this limit statement needs no sign hypotheses. h = 1 − e^{-t} is not CM.
* **What is not proved in Lean.** Continuous emission paths, T2, T3 and (b).
* Note that `excess` is defined for all t without a Heaviside factor. It equals the model excess only for t ≥ max z_j, which is the only range the theorems use.
* Tier A candidate status is confirmed for the discrete case.

## 5. Literature (to our knowledge)
I read Joos 2013 and Seshadri 2016 and ran two web searches (carbon-cycle IRF multiple peaks; rebound after a drop to a low plateau). I found no carbon-cycle paper that states that a single-peaked emission path can give two concentration maxima in a linear IRF model. The search was not systematic: MacDougall, Ricke & Caldeira 2014 and Zickfeld & Herrington 2015 concern the delay to peak *warming* and were not read for this question. The mathematical mechanism is classical (Ibragimov, §3). The physical intuition is also elementary: with a0 > 0, any sustained positive emission makes the model u grow, so the end of a long low plateau produces a second maximum. The result should therefore be labelled an explicit, certified instance of a known phenomenon class, not a new phenomenon.

## 6. Corrections (old → new), to `RESULT.md` (and `result.json` where it mirrors the text)
1. (c) headline. Old: "**Answer in this model: yes, whenever the IRF is not a single exponential. "At most one peak" holds for a single exponential and fails for the Joos IRF.**" → New: "**Answer in this model: yes, for every IRF h with h(0) = 1 that is completely monotone, strictly decreasing and not a single exponential (in particular the Joos IRF). For a single exponential, u is quasi-concave for every unimodal emission path (T2). "Two maxima" means two local maxima of the model excess u separated by a strictly lower value.**"
2. Literature sentence. Old: "To our knowledge (one alphaXiv query and the Seshadri and Joos texts; no systematic search) this is not stated in the literature read; Seshadri studies the delay and the condition for a peak to exist, not the number of peaks." → New: "The mechanism is classical. By Ibragimov (1956), convolution preserves unimodality for every unimodal input if and only if the kernel is log-concave. T2 is the special case of the (log-concave) one-sided exponential. For an integrable CM kernel that is not a single exponential (strictly log-convex), the converse implies that some unimodal input gives a non-unimodal output. For a0 > 0, T3 gives an explicit construction. To our knowledge (Joos 2013, Seshadri 2016, an alphaXiv query and two web searches; not systematic), the two-maximum behaviour is not stated in the carbon-cycle literature read. What is added here is the explicit window B/A ∈ (h(d), L), which is necessary and sufficient within the staircase family, and certified Joos instances."
3. T2. Old: "u has at most one local maximum … thus u′ is ≥ 0 then ≤ 0." → New: "u is non-decreasing then non-increasing (quasi-concave). Its maximizers form an interval, and it never has two local maxima separated by a strictly lower value. Non-strict maxima can fill an interval: an impulse cτ at 0 followed by constant emission c gives u ≡ cτ."
4. T3 proof. Old: "since u′(z3−) > 0 > u′(z3+) (use h(x) <= 1)" → New: "since u′(z3−) > 0 and u′(z3+) = −A(1−h(z3)) + B(1−h(z3−d)) < 0 (A > B, h(z3) < h(z3−d) ≤ 1). Because u′ = A h > 0 on (0,d) and u is CM after z3, the staircase has exactly two maxima. If θ ≤ h(d) or θ ≥ L it has exactly one, so the window is necessary within the family." Also add "(strict log-convexity: Cauchy–Schwarz on the Bernstein measure, with equality only for a point mass)".
5. I1 bullet. Old: "I1, **continuous** piecewise-linear unimodal emission" → New: "I1, **continuous** piecewise-linear, *weakly* unimodal emission (non-decreasing to year 10, then non-increasing with a plateau on [22,300])". I2 bullet. Old: "same but strictly decreasing after the peak (level 1/20 at 300)" → New: "strictly increasing on [0,10], strictly decreasing on [10,310] (level 1/20 at 300), zero afterwards. This is the instance that meets the strict definition of single-peaked." S1: add "(non-increasing step function, weakly unimodal, mode at 0)".
6. Fit window. Add to (a) and to the (b) scan bullet: "Joos eq. (11) fits only 0 ≤ t ≤ 1000 yr. The limit a0W, the P5 check u(10^6), and the single-sign-change scan on [0, 6000] yr are properties of the fitted formula beyond its stated range, not of the multi-model response. The certified (b) peaks (≤ 287 yr) and (c) times (≤ 500 yr) are inside the window."
7. Seshadri wording. Old: "His Fig. 5 scenario … is internally inconsistent with his own condition r > 1/tau_m (ln 1.015 = 0.0149 < 0.02; the unit "%/year" is also ambiguous). I did not resolve this" → New: "The parameters of his Fig. 5 (tg − t0 = 60 yr, r = 0.015 %/year, τm = 50 yr) fall outside the case r > 1/τm to which his Sect. 3.2 restricts attention, under either reading of "0.015 %/year" (0.015/yr or 0.00015/yr; both below 1/τm = 0.02, and ln 1.015 = 0.0149). This is not resolved here." Keep the 0.999 coefficient sum as a neutral factual note.
8. (b) table, cell r = 0.05, τm = 20: add "convention-dependent: ln(1.05) = 0.0488 < 1/τm = 0.05 gives t1 = 0 in our exact (1+r)^t reading. Under Seshadri's e^{rt} approximation r = 1/τm exactly, emissions are flat on [0,60] and t1 is undefined."
9. (b) comparison bullet: add "Our setup puts the origin at t0 and ignores pre-t0 emissions. Seshadri integrates from an earlier origin 0 < t0 (his m′av0 term), so agreement with his figures is Tier X only." Optional neutral note: his eq. (4) as printed omits the boundary term Σμ_i e^{-t/τ_i} m(0) from the integration by parts, and is exact only when m(0) = 0.
10. Exploratory line "1364 one, 117 two, 2 three": add "(the 3-maximum cases are float-grid counts and not certified; this audit did not check them)".
11. Mechanism bullet: add "With a0 > 0 any sustained positive emission makes the model u grow, so the second maximum is the end of the low plateau. This is expected once stated and is a model property only."
12. Header: add "Independent audit: AUDIT.md (ACCEPT_WITH_CORRECTIONS)". Lean status: "Tier A (discrete emission measures only), recompiled, axiom-audited and leanchecker-replayed by an independent auditor. Dependency oleans reused, not rebuilt."

## 7. What remains unverified
* The 63-scenario uniqueness of the peak is certified (by the producer, with intervals) only within each 0.01-yr bracket. The global single-peak claim and my cross-check are float scans, Tier X. I checked only the 21 Joos scenarios plus 6 Seshadri-variant cells; I did not check the other 36 variant cells.
* The float maps in (c) (plateau table, 1500 random paths, the 3-maximum cases) and the a0 = 0 and two-term checks were not reproduced as certificates. My own analogous numerics agree qualitatively.
* Ibragimov's theorem was checked from secondary sources only. The search of the carbon-cycle literature was not systematic.
* The continuous-emission version of (a) is a paper proof only (it is elementary; I checked it by hand).
* I did not check the ordering of the prereg relative to the work (the git history does not show it). The prereg hash matches.
* I did not check the P4 Ciais arithmetic beyond noting that 10.38 − 2.04 − 3.15 − 2.06·2.124 = 0.81456 (exact).

## 8. Wording and scope
The text keeps to a linear IRF model: no tonnes, no climate effect, no policy, and no "discovery" or "breakthrough" language. With corrections 1, 2 and 11 applied, (c) reads as an explicit, certified instance of a classical phenomenon class. It is not a statement about the real carbon cycle or about realistic emission paths.
