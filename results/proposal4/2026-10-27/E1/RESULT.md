# E1 (proposal 4): certified ideal-ignition windows for p-¹¹B in the Wurzel–Hsu 0-D power balance

**Status: PARTIAL.** The certified-numeric gate passes, but the preregistered kill criterion is only met through
its own listed fallback. The Bosch–Hale and Nevins–Swain coefficients could not be read from the primary papers.
They were pinned from the authors' public code (Wurzel–Hsu, MIT licence), which the preregistration lists as a
fallback. All enclosures are Arb ball arithmetic that is not replayed in Lean, so they are **Tier C** under the
proposal's interval rule; the preregistration had asked for Tier A. Two small algebraic lemmas are kernel-checked
in Lean (Tier A, see §6).

Date: 2026-10-27/28. Agent: Claude (Opus), producer only; no independent verifier has re-run this.
Cores: `taskset -c 6,7`, one Python process at a time.

**Time.** From 2026-10-27 about 11:50 UTC to 2026-10-28 about 11:15 UTC: about 23.5 h wall clock, inside the
first 24 h budget. Most of it was single-core certification runs; the agent-active time is well under that.

## 1. Claim, in the model's own terms

Model, as in Wurzel & Hsu (W-H), arXiv 2105.10954 v4.
- Equations (6)–(8), (16), (22), (41) and (D1)–(D5), with ideal confinement and no conduction loss in the
  ignition criterion. The fusion side is S_c = f_c n₁n₂⟨σv⟩E_F and the bremsstrahlung side is
  S_B = C_B n_e² √T_e γ(Z_eff).
- The relativistic bracket γ = Z_eff(1+1.78t^1.34) + 2.12t(1+1.1t+t²−1.25t^2.5), with t = T_e/m_ec². This is
  W-H eq. (D2), which equals Ochs–Fisch eq. (14) including the x² term.
- No synchrotron loss, no kinetic enhancement, no ash, no α-to-electron heating, and T_e/T_i taken as a free
  parameter θ. No mechanism that would maintain T_e < T_i is modelled.
- For p-¹¹B: f_c = 1, E = 8.68–8.70 MeV, boron fraction x = n_B/n_i, n_e = (1+4x)n_i and
  Z_eff = (1+24x)/(1+4x). The ratio R = S_c/S_B does not depend on density.

**E1b, older fit (Nevins–Swain 2000 high-T fit, valid 50–500 keV), Tier C.** Box: T_i ∈ [50, 500] keV,
x ∈ [0.05, 0.5].
- θ* ∈ **[0.4223, 0.4308]**.
- For every θ = T_e/T_i ∈ [0.4308, 1], P_c < P_B on the whole box (certified max R ≤ 1 at θ_hi). P_B increases
  with θ; see the monotonicity argument in §5.
- At θ = 0.4223, the point (T_i, x) = (243.5 keV, 0.0922) has a certified R ≥ 1.0077.
- At the W-H optimal mix x = 1/6 (Z_eff = 3): θ* ∈ **[0.3753, 0.3828]**, with witness T_i = 243.5 keV and
  R ≥ 1.0082 at θ = 0.3753.

**E1c, at T_e = T_i, two fits, Tier C.** On the same box, P_c < P_B everywhere: there is no ideal-ignition
window in this model under either fit.

| fit | certified max over box of P_c/P_B | argmax (T_i, x) | m* (reactivity multiplier needed for any window) |
|---|---|---|---|
| Nevins–Swain 2000 (via W-H code) | [0.42139, 0.42556] | (202 keV, 0.100) | [2.350, 2.373] |
| Wang et al. 2026 S-factor (Mazzucconi 2025 data), Maxwellian-integrated | [0.42869, 0.43260] | (208.5 keV, 0.101) | [2.312, 2.333] |
| NS at the W-H mix x = 1/6 | [0.39016, 0.39240] | (204.5 keV) | [2.548, 2.563] |
| Wang at the W-H mix x = 1/6 | [0.39732, 0.40083] | (211.4 keV) | [2.495, 2.517] |

- **m\*** is a certified statement that needs no updated fit. R is linear in ⟨σv⟩, so any reactivity with
  ⟨σv⟩(T) ≤ 2.349 × NS(T) on [50, 500] keV gives P_c < P_B on the whole box at T_e = T_i.
- Context (both far below m* ≈ 2.35):
  - Putvinski et al. report about +20% from cross sections and about +10% from kinetic effects. This is
    *unpinned*: seen only in small-model OCR summaries, so it is not Tier L.
  - Sikora–Weller report "10–15 % higher than … Angulo et al." between 200 and 600 keV. This is Tier L
    (J. Fusion Energy 35, abstract p. 538 and p. 541), against a NACRE baseline, not NS.
- **Caveat on the NS-to-Wang comparison.** It compares an *integrated* S-factor (Wang) with a *fitted*
  reactivity (NS).
  - Our Tier X check shows the NS fit lies 2.4–3.5% below the Maxwellian integral of the NS S-factor at
    250–300 keV, where θ* is set, and 8% below at 500 keV.
  - So part of the Wang/NS ratio and of the θ* shift below is method mismatch, not new data.
  - The T_e = T_i exclusions do not depend on this: they hold with a margin of about 2.3× either way.
- **Robustness across fits.** Both conclusions survive the change of fit:
  - there is no window at T_e = T_i;
  - a window needs T_e/T_i below about 0.42–0.45;
  - between the fits, max R moves by +1.7% (box) or +2.1% (x = 1/6).
- Certified Wang/NS reactivity ratio at single temperatures:

  | T (keV) | 50 | 100 | 150 | 200 | 300 | 400 | 500 |
  |---|---|---|---|---|---|---|---|
  | Wang/NS | 1.016 | 1.000 | 1.005 | 1.016 | 1.070 | 1.154 | 1.262 |

  - At 500 keV the Wang fit includes the new 4.7 MeV resonance.
  - These are point enclosures with relative radius below 1e-4; the full table is in `logs/certify.json`.

**E1b repeated under the updated fit (Wang 2026), Tier C.**
- Box: θ* ∈ **[0.4381, 0.4470]**. The certified max R at θ_hi is ≤ 0.99999999, and the witness
  (243.5 keV, x = 0.092) has R ≥ 1.0082 at θ_lo.
- Mix x = 1/6: θ* ∈ **[0.396, 0.402]**. At θ = 0.402, max R ≤ 0.99995 (certified). At θ = 0.396, there is a
  witness with R ≥ 1.00037.
  - This comes from the explicit θ scan in `code/e1_wang_mix.py` / `logs/certify_wang_mix.json`. The bisection
    driver had returned "not separated" because of an early-exit bug; see Deviation 7.
- The threshold therefore rises by about 3.7% (box) and 5% (mix) from NS to Wang. The qualitative structure is
  identical: no window at T_e = T_i, and a window only for T_e/T_i below about 0.43–0.45, near T_i ≈ 240–260 keV
  and x ≈ 0.09–0.1.

**W-H Fig. 28 caption check (model-internal).** The caption says "P_B always exceeds P_c when T_e ≳ T_i/3".
- At the authors' own mix and fit, the certified threshold is 0.375–0.383, not 1/3.
- So for T_e/T_i between 1/3 and 0.375 there are temperatures, around T_i ≈ 243 keV, where P_c > P_B in their
  model. At T_e = T_i/3 the Tier X float gives max P_c/P_B ≈ 1.11 (NS, T_i ≈ 248 keV) and ≈ 1.16 (Wang); see
  `logs/third_check.txt`.
- The caption's "≳" makes it a rough reading of a figure that plots the T_e = T_i/3 curve. It is not an error in
  their conclusions; we report the sharper certified value.

## 2. Positive control first (E1a, D-T): reproduction of W-H to the printed digits

The gate (`code/e1_gate.py`, written before the certified run) passed. It passed in run 4 (`logs/certify_gates.json`) and again in the final clean run
(`logs/certify.json`, `logs/certify_final_stdout.txt`).

| quantity | W-H printed | certified enclosure (authors' code model) | constant-hull enclosure |
|---|---|---|---|
| ideal ignition T (eq. 8, Fig. 6) | 4.3 keV | [4.2989514, 4.2989523] | [4.2608, 4.3468] |
| argmin of n_iTτ_E, Q = ∞ (Table III) | 14 keV | [14.128, 14.442] | corners [14.127, 14.448] |
| min n_iTτ_E, Q = ∞ (Table III) | 2.9e21 m⁻³ keV s | [2.94410, 2.94502]e21 | [2.94400, 2.96351]e21 |
| argmin of n_iτ_E, Q = ∞ (Table II) | 26 keV | [25.590, 26.212] | corners [25.590, 26.214] |
| min n_iτ_E, Q = ∞ (Table II) | 1.6e20 m⁻³ s | [1.55227, 1.55279]e20 | [1.55224, 1.56219]e20 |

**"Authors' code model"** means the paths that produced the paper's numbers in
github.com/swurzel/lawson-criterion-paper @ 4ae563b.
- Fig. 6 / eq. (8): parameterized Bosch–Hale reactivity, non-relativistic, with the code's W/m³ constants.
- Tables II/III: the `integrated` path, a Maxwellian average of the Bosch–Hale cross section over
  E ∈ [0.5, 4700] keV, certified here with rigorous Arb integration.
  - It uses the Putvinski relativistic bracket with Z_eff = 1, f_c = 0.2, E = 17.6 MeV and C_B from the NRL value
    1.69e-32.

**Constant hull.** The hull combines C_B/(J per keV) from three sources: the W-H text (5.34e-37; 1.6e-16 J/keV),
the code (NRL, 6.24e18 or 6.242e18 eV/J, CODATA) and the Ochs–Fisch eq. (14) prefactor 7.56e-11 eV cm³/s. It also
includes f_c ∈ [3.5/17.6, 0.2].
- For the TP and LP minima, the hull is evaluated at its two corners. This is valid because TP = 3T²/D with D
  increasing in f_c and K, so the minimum is monotone in both.

**Finding (fragility of the printed 2.9e21).** The Table III minimum sits 0.17% below the rounding edge, 2.95e21.
- With the text's α-energy fraction f_c = 3.5/17.6 instead of the code's 0.2, the minimum rises to 2.9626–2.9635e21.
  That would print as **3.0e21**.
- With the parameterized instead of the integrated reactivity, it is 2.9506e21 (Tier X float), which would also
  print as 3.0.
- So "to the printed digits" holds for the model the authors actually ran, not for every reading of the text.
- The ignition temperature (4.3) and Table II (26 keV, 1.6e20) are robust over the whole hull.

Other D-T model readings, all certified (`logs/certify.json`, `dt_variants`):

| variant | T_ign (keV) | argmin TP | min TP (e21) | argmin LP | min LP (e20) |
|---|---|---|---|---|---|
| parameterized σv, non-rel., text constants (pure eq. 8/22 reading) | [4.29959, 4.29959] | [14.09, 14.40] | [2.94923, 2.95056], **straddles the 2.95 rounding edge** | [25.67, 26.29] | [1.5570, 1.5577] |
| parameterized σv, relativistic, code constants | [4.32619, 4.32620] | [14.10, 14.42] | [2.96275, 2.96409] → 3.0 | [25.61, 26.23] | [1.5647, 1.5655] |
| integrated σv, non-rel., text constants | – | [14.11, 14.43] | [2.93077, 2.93168] → 2.9 | [25.64, 26.27] | [1.5446, 1.5452] |
| integrated σv, relativistic, code constants (the gate model) | – | [14.13, 14.44] | [2.94410, 2.94502] → 2.9 | [25.59, 26.21] | [1.5523, 1.5528] |

Every variant gives 4.3 keV, 14 keV, 26 keV and 1.6e20. Only the second significant digit of the Table III
minimum depends on the reading.

## 3. Controls

| control | expectation | outcome |
|---|---|---|
| P1: D-T reproduction (above) | gate PASS | **PASS** (G1, G2, G2b, G3, G4 all true) |
| P2: independent float implementation (`code/e1_float_indep.py`: scipy, text constants, separate code) | inside the certified hull | **inside**: T_ign 4.29959, TP min 2.94518e21, LP min 1.55284e20 |
| P3: W-H Table II/III "–" for p-¹¹B (NS, T_e = T_i, x = 1/6) | certified P_c < P_B on [50, 500] | **certified**, max R ≤ 0.39222 |
| P4: independent float implementation vs the p-¹¹B certificates | float values inside the certified intervals | **inside**: θ_c,max 0.4286 ∈ [0.4223, 0.4308] (NS box); 0.3811 ∈ [0.3753, 0.3828] (NS mix); 0.4451 ∈ [0.4381, 0.4470] (Wang box); 0.3988 ∈ [0.396, 0.402] (Wang mix). max R at θ = 1: 0.4232 ∈ [0.4214, 0.4256] (NS); 0.4309 ∈ [0.4287, 0.4326] (Wang) |
| N1: reactivity × 0.5 (same pipeline) | gate FAIL | **FAIL**: T_ign = 5.3724, TP min 6.285e21, LP min 3.230e20 |
| N2: bremsstrahlung removed (the planted wrong loss term) | changes the conclusion, gate FAIL | **FAIL**: no ignition temperature at all (S_c > S_B for every T); TP min 2.758e21; the p-¹¹B ratio becomes infinite, so the "no window" conclusion flips |
| N3 (Lean): tampered optimum 1/21, tampered e-e coefficient 7 instead of 4.375, wrong range [0, 2] | each must fail to elaborate | see §6 |
| S-factor positivity (needed for the T-interval reactivity bound) | certified ≥ 0 | **certified** for BH (both pieces) and all three Wang segments |

## 4. Literature actually read

- **Wurzel & Hsu 2021/22, arXiv 2105.10954 v4.** Full text via alphaXiv, saved at
  `data/papers/wurzel_hsu_2105.10954_fulltext.txt`, 10,602 lines.
  - Read: lines 60–1720 (Sec. I–III G, eqs 1–22, Tables I–III); 2640–2760 (impurities, eqs 41–44); 3900–4057
    (Appendices C, D intro); 8740–9420 (Appendix D: D-³He, p-¹¹B, Figs 28–29, catalyzed D-D); reference list
    entries 20–25 and 133–141.
  - Not read: lines 1720–2640 (Q_eng, profiles), 2760–3900 (experimental data extraction), Appendix B data tables
    (4058–8740), lines 9420–9880 (Appendices E/F). None of these enter the 0-D criterion.
  - Quoted claim (Fig. 28 caption): "P_B always exceeds P_c when T_e ≳ T_i/3"; Table II/III list "–" for p-¹¹B.
- **Ochs & Fisch 2023, arXiv 2310.18508 v1.** Full text via alphaXiv.
  - Eq. (14) bremsstrahlung (prefactor 7.56e-11 eV cm³/s, x² term; "Ref. 6 missed the x² term").
  - The 11.8 s reactor-breakeven and 450 s ignition figures come from a 4-species optimisation whose rate
    coefficients are in their Ref. 6 (Ochs et al., PRE 2022), which we did not read. They are **out of scope and
    not reproduced**; they are not ideal-ignition windows.
- **Sikora & Weller 2016, J. Fusion Energy 35, 538.** Full text via alphaXiv (CC-BY 4.0).
  - Gives no reactivity fit: only Legendre A₀ tables and a figure of the rate.
  - "10–15 % higher than … Angulo et al. … between 200 and 600 keV". **Not used as a fit**; turning its tables
    into a reactivity would be building a fit, not reading one.
- **Wang, Li, Wu, Cui, arXiv 2601.00241 v1 (Jan 2026).** Full text via alphaXiv.
  - Eqs (1)–(6) and Table I: an updated S-factor parametrisation from Becker, Mazzucconi 2025 and Buck data.
    Its E ≤ 0.4 MeV segment reprints the NS coefficients, identical to the W-H code values, which independently
    confirms that part of the transcription.
  - Its Fig. 8 text: "if electron-ion thermal equilibrium is assumed (T_e = T), the resulting bremsstrahlung loss
    … exceeds the fusion power density over the entire temperature range". This agrees with E1c (Tier L), but
    they use Rider's bremsstrahlung, not Putvinski's.
- **Putvinski, Ryutov, Yushmanov 2019, Nucl. Fusion 59, 076018.** Not a primary read.
  - IOP is behind a bot challenge. The TAE-hosted flipbook pages 1–7 were seen only through WebFetch small-model
    OCR summaries.
  - Seen in those summaries: bremsstrahlung eq. (7) with coefficients 8.511, 1.78, 1.34, 2.12, 1.1, 1.25 and 2.5;
    Y = 8.68 MeV; "~20%" from cross sections and "~10%" kinetic; no reactivity fit formula on those pages.
- **Nevins & Swain 2000, Nucl. Fusion 40, 865.** Abstract only, via the IOP landing page through WebFetch: the
  "50 keV ⩽ T ⩽ 500 keV" high-T range. Full text not obtained.
- **Bosch & Hale 1992, Nucl. Fusion 32, 611.** Not obtained (OpenAlex: closed access; INIS returned 403).
- **Tentori & Belloni 2023, Nucl. Fusion 63, 086001.** Gold OA, but IOP's bot challenge blocked every access
  route. Not read.

## 5. Method

- `code/e1_model.py`: the model in python-flint 0.6.0 Arb balls at 128-bit precision. Every coefficient is a
  decimal string from `data/fits.json`, with provenance recorded per block.
- **Certified reactivity of a cross-section fit (BH integrated, Wang).**
  - Rigorous `acb.integral` on each analytic segment, plus a rigorous bound on (0, 1 keV].
  - Enclosure over T ∈ [a, b] from point integrals: sv(a)(a/b)^{3/2} ≤ sv(T) ≤ sv(b)(b/a)^{3/2}, valid because
    σ ≥ 0 (certified).
  - p-¹¹B reduced mass μc² ∈ [859500, 859650] keV, covering NS's 859526 and AME nuclear masses.
- **Ignition temperature.** Bisection, then certified signs on [0.2, T_lo] and [T_hi, 100] keV by adaptive
  interval subdivision.
- **Minima.**
  - U is an upper bound at the float minimiser.
  - The edges a < T₀ < b are chosen where h ≥ U(1+10⁻⁴). The tool then certifies h > U on [1, a] ∪ [b, 100] keV,
    and L is the minimum of cell lower bounds on [a, b].
- **max R over (T, x) boxes.** Best-first branch and bound with outward rounding.
- **θ\*.** Bisection, then two-sided certification: certified max R < 1 at θ_hi, and a certified witness R > 1 at
  θ_lo.
- **Reduction from the θ_hi face to all θ ∈ [θ_hi, 1].**
  - S_B ∝ √T_e γ(T_e/m_ec²) is increasing in T_e for t ≤ 1. The Z_eff term is increasing.
  - The e-e term's derivative 1 + 2.2t + 3t² − 4.375t^2.5 is > 0 on [0, 1]. This is certified twice: by Arb
    subdivision, and by the kernel-checked Lean lemma `ee_term_deriv_pos`.
  - The step "positive derivative ⇒ monotone" is Tier C.
  - T_e = θT_i ≤ 500 keV < m_ec², so the whole range stays inside the fit's range.
- **Independent check.** `code/e1_float_indep.py` is a separate float implementation (scipy quad and brentq,
  text constants). It agrees with all certified enclosures, and its p-¹¹B grid scan gives θ_c,max: NS box 0.4286,
  NS x = 1/6 0.3811, Wang box 0.4451, Wang x = 1/6 0.3988.

## 6. Lean (optional gate)

`formal_cert/Programmes/PbIgnition/Core.lean` (Tier A once compiled) holds two exact facts:
- `optimal_mix`: 20x(1−x) ≤ (1+4x)², and `optimal_mix_eq`: equality iff x = 1/6. This is W-H footnote 138; the
  optimum at x = 1/6 gives n_pn_B/n_e² = 1/20.
- `ee_term_deriv_pos`: 0 < 1 + 2.2t + 3t² − 4.375t^2.5 on [0, 1].

The planted failures are in `Controls.lean`.

**Outcome.**
- `Core.lean` passes on two runs, `logs/lean_core.json` and `logs/lean_runner_core.json`.
  - The first is the pinned Lean 4.34.1 + Mathlib d13f23b7 run via `scripts/certified_numerics/lean_pinned.py`.
  - The second is the binding `anse/formal/lean_runner.py` `verify_file` gate, with `lean_cmd` pointed at the
    pinned toolchain. The main `formal/` build lacks `Mathlib/Tactic.olean`, so its default command fails before
    any proof is checked; see `code/e1_lean_runner_gate.py`.
  - Both give rc 0, no `sorry`, no warnings, and for all 4 theorems `#print axioms` = [propext, Classical.choice,
    Quot.sound].
  - A grep finds no `sorry`, `native_decide`, `axiom`, `set_option`, `#exit`, `skipKernelTC`, `addDecl` or
    `implemented_by` in either file.
- `Controls.lean`: rc 1, and every planted control fails to elaborate (`ctl_mix_21` line 23, `ctl_coeff_7`
  line 28, `ctl_wrong_range` lines 32–33); see `logs/lean_controls.json`.
- **Not done:**
  - leanchecker kernel replay;
  - a statement-lock entry;
  - producer ≠ verifier recompilation.
  
  The Lean rows are therefore Tier A *pending independent verification*, and they cover only these two
  algebraic facts. The interval enclosures are not in Lean.

## 7. Deviations from the preregistration (preregistration.json was not edited)

1. **Sources.**
   - Bosch–Hale and Nevins–Swain coefficients come from the W-H public code (the preregistered fallback), not from
     the primary papers, which could not be obtained.
   - The NS low-energy S-factor block is independently corroborated by Wang 2026 Table I.
   - The NS high-T reactivity coefficients P1–P7 are corroborated only indirectly, by a Tier X check
     (`code/e1_ns_consistency.py`, `logs/ns_consistency.json`). The transcribed fit and the Maxwellian integral of
     the transcribed NS S-factor agree as follows:

     | T (keV) | 50–200 | 250–300 | 400 | 500 |
     |---|---|---|---|---|
     | fit / integral | 0.985–0.996 | 0.976 / 0.965 | 0.940 | 0.917 |

     - This rules out gross transcription errors.
     - The high-T drift is unexplained. It may come from the code's NS S-factor itself; W-H's own docstring flags
       the low-T NS branch as giving "incorrect results".
     - It does not affect the T_e = T_i exclusion (margin m* ≈ 2.35).
     - It is of the same size as the NS-to-Wang threshold shift.
   - The kill criterion's literal wording ("pinned from primary sources") is therefore **not** met. We proceeded
     because the preregistration lists this fallback.
2. **"Updated" fit.**
   - The proposal named Sikora–Weller/Putvinski. Neither publishes a reactivity fit we could read, and
     Tentori–Belloni 2023 could not be accessed.
   - The updated fit used is Wang et al. 2026 (arXiv 2601.00241), the only updated p-¹¹B parametrisation whose
     coefficients we read in full.
   - Its "reactivity" is our certified Maxwellian integral of their S-factor, with σ := 0 above 10 MeV, their
     stated fit range.
3. **Tier.** The preregistration states Tier A for the inequalities. Delivered: Tier C (Arb, not replayed in
   Lean), plus two Tier A lemmas.
4. **θ range.** The preregistration says "whenever T_e/T_i ≥ θ*". We certify only θ ∈ [θ_hi, 1]. Beyond 1,
   T_e can leave the 500 keV box and approach m_ec², where the bremsstrahlung fit and the monotonicity argument
   stop.
5. **E1c is answered twice.** Once as an exclusion under both fits, and once as the certified multiplier m\*,
   which needs no updated fit.
6. **Gate timing and model choice.** The gate file was written after a first Tier X float run.
   - That run showed the parameterized-reactivity variant gives 2.9506e21, which rounds to 3.0e21.
   - The gate therefore tests the code path that produced Table III (integrated reactivity, relativistic γ).
     The paper's Fig. 4 caption states that D-T reactivities come from the integrated cross sections.
   - The fragility is reported as a finding (§2), not hidden.
7. **Certification-method changes between runs.** No model change in any of these. Run logs are kept.
   - The minimum-bracket rule changed from a relative-T bracket to a value margin of 1e-4.
   - The hull minimum is computed by corners (monotonicity) instead of a direct interval.
   - Non-finite cells are subdivided.
   - An early-decision flag was added for the θ bisection.
   - Runs 1 and 2 were aborted (hang or too wide). Run 3 reached a FAIL on G4 only, for the hull reason; see
     `logs/certify_run3_aborted_stdout.txt`. Run 4 gives the gate results.
   - The p-¹¹B stage was rerun as a separate stage (`e1_certify.py pb`) after the early-decision change.
     - Two p-¹¹B stage runs were aborted. The first was too slow (adaptive Wang integrals). The second crashed
       because a grid edge rounded below 50 keV. Their logs are `logs/certify_pb_run{1,2}_aborted_stdout.txt`.
     - The final NS results come from `logs/certify_pb_NS.json`. Wang and the D-T variants come from
       `certify_pb.json`, run as `pb wangonly`. That run uses a fixed certified grid of 4608 Wang integrals at
       ratio 1.0005 with the same monotone T-interval bound.
   - **Early-exit bug.** In the early-decision mode, max_R stopped as soon as an unsplittable cell had U ≥ 1.
     - It cannot create a false certificate: certified_below_1 always uses the maximum over all kept and stuck
       cells, and witnesses are point lower bounds.
     - It could, however, return "undecided". That is what happened for Wang at x = 1/6, which is why that entry
       in `certify_pb.json` reads "not separated".
     - The bug is fixed in `e1_certify.py`. Wang at x = 1/6 was then certified by the explicit θ scan
       `e1_wang_mix.py`.
   - **Provenance, resolved.** After all edits, the final hashed `e1_certify.py` was rerun once end to end:
     `logs/certify.json` and `logs/certify_final_stdout.txt`.
     - It reproduces every gate verdict and every enclosure quoted here.
     - `result.json` is built from that file plus `certify_wang_mix.json`.
     - Earlier logs (`certify_gates.json`, `certify_pb*.json`) were made by earlier code versions. They are kept
       only as history.
   - **Wang at x = 1/6 in the final run.** `theta_threshold` again returns "not separated". In decide mode, the
     rel-tol stopping test (rtol = d/4) can fire before the decide test. This cannot create a false certificate,
     because both outcomes are re-checked against the global U and the point witness.
     - The certified two-sided result for that case is the explicit θ scan `e1_wang_mix.py`, which uses the same
       final `max_R`: [0.396, 0.402].
     - Fixing the stopping order is left for a later version, so that the hashed code is exactly what ran.
8. **Not done.**
   - CVODE (rusty-SUNDIALS) Tier X transient: not run; it is optional.
   - Synchrotron / kinetic-enhancement sensitivity (E1x): only the m\* statement above. No synchrotron model.
   - The Ochs–Fisch 450 s / 11.8 s numbers: out of scope, as noted in §4.

## 7b. Repository guards (CLAUDE.md completion commands), actual output

| command | exit code | what it found |
|---|---|---|
| `antigravity_guard.py` (`logs/guard_antigravity.txt`) | **1 (FAIL)** | 38 findings, none in `results/proposal4/2026-10-27/E1/`. They are in other rounds' `papers/*/data/code`, mostly "Hallucinated import: 'flint'" (python-flint lives in `.scratchpad/b2_pylib`, outside the venv) and local-module imports. |
| `test_rigor_guard.py` (`logs/guard_test_rigor.txt`) | **1 (FAIL)** | Zero-assertion tests in the pre-existing `tests/` (e.g. `tests/test_k3_anse_improvements.py`, `tests/test_scientific_rigor_v14.py`); nothing from E1, which adds no tests. |
| `pytest tests/` | not run | E1 adds no tests. The suite takes about 15 min and rewrites tracked files (verification-traps note). |

## 8. Limits

- Every statement is about an idealised 0-D power-balance model with the stated fitted formulas.
  - Ideal ignition only: no conduction, no confinement time. It is not reactor breakeven; Ochs–Fisch show
    breakeven is a different, weaker condition.
- The fits' own uncertainties are not propagated: ±3–10% on the 0.6 MeV resonance per Wang, and NS's quoted
  errors.
- The T_e/T_i results do not say that T_e < T_i is achievable. No ion–electron equilibration, no α heating of
  electrons and no mechanism are modelled.
- Synchrotron radiation is absent; it would only make every window smaller.
- Tier C: the Arb code is not kernel-replayed, and no independent agent has re-run it.

## 9. What is NOT claimed

- Nothing about any reactor design, device, cost, or the feasibility of fusion energy.
- Not that p-¹¹B fusion is possible or impossible.
- Not that W-H's "T_e ≳ T_i/3" is wrong: it is a figure reading, and the certified threshold at their mix is
  0.375–0.383, close to and somewhat above 1/3.
- Not that Wang 2026 or any other fit is correct.
- Not that 2.9e21 is wrong: it is reproduced for the model the authors ran.
- Public data only; no inertial-confinement, burn or yield content.

## 10. Files

- `code/`
  - `e1_model.py`: Arb model.
  - `e1_certify.py`: certification driver.
  - `e1_gate.py`: gate.
  - `e1_float_indep.py`: independent float check.
  - `e1_wang_mix.py`: Wang θ* at x = 1/6.
  - `e1_ns_consistency.py`, `e1_third_check.py`: Tier X checks.
  - `e1_lean_runner_gate.py`: lean_runner file-mode gate.
  - `e1_smoke.py`, `e1_time_integrals.py`: probes.
  - `e1_hashes.py`: hashing.
- `data/`
  - `fits.json`: coefficients plus provenance.
  - `papers/wurzel_hsu_2105.10954_fulltext.txt`
  - `downloads/wurzel_hsu_code/`: MIT; commit 4ae563bfc409db5fb4afb2f9930a3a4fafba4f0d, dated 2026-08-17, after
    the 2022 paper. Used as data only, never executed.
  - `downloads/*/*.html`: paywall and challenge pages, kept as evidence of failed access.
- `logs/`
  - `certify_gates.json` and `certify_gates_stdout.txt`: gates.
  - `certify_pb.json` and `certify_pb_stdout.txt`: Wang fit and D-T variants.
  - `certify_pb_NS.json` and `certify_pb_NS_stdout.txt`: NS fit.
  - `certify_wang_mix.json` and `certify_wang_mix_stdout.txt`: Wang at x = 1/6.
  - `ns_consistency.json`, `third_check.txt`
  - `lean_core.json`, `lean_controls.json`, `lean_runner_core.json`
  - Aborted runs: `certify_run3_aborted_stdout.txt` and `certify_pb_run{1,2}_aborted_stdout.txt`.
  - `float_indep.json`
  - `certify_run3_aborted_stdout.txt`
  - `lean_*.json`
  - `sha256.json`
- `formal_cert/Programmes/PbIgnition/{Core,Controls}.lean`
