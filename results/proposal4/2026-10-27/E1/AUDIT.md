# E1 independent audit (producer ≠ verifier)

Date: 2026-10-28. Auditor: Claude (Opus), separate agent, did not write any E1 code.
Scope: `RESULT.md`, `result.json`, `code/`, `data/fits.json`, `logs/`, `formal_cert/Programmes/PbIgnition/{Core,Controls}.lean`,
against `docs/proposals/NEXT_STEPS_PROPOSAL_4_2026-10-27.md` (E1), `preregistration.json` and the addendum.
Auditor scratch (not in the repo): `/tmp/e1audit/` (`aud_model.py`, `t2.py`–`t5.py`, `lean_audit.py`, logs/JSON).
Cores: `taskset -c 6,7`, at most 2 processes.

**Verdict: ACCEPT_WITH_CORRECTIONS.** Status PARTIAL, Tier C (enclosures) is the right label.

- **The two Lean lemmas** are kernel-checked, independently recompiled and replayed by leanchecker. They become
  Tier A once a statement-lock entry exists.
- **Rigorous on the auditor's side** (mpmath.iv, different method):
  - D-T T_ign, three readings;
  - the pure-text D-T triple-product bound;
  - NS max P_c/P_B over the box and at x = 1/6;
  - the NS θ* upper side;
  - an iv re-check of the producer's NS θ* witnesses.
- **Float only on the auditor's side (Tier X):**
  - all Wang-fit numbers;
  - the D-T TP/LP minima and minimisers of the gate model;
  - all sensitivities.
- Every producer enclosure contains the auditor's independent value.
- The corrections below are about labels, scope wording and file paths. None changes a conclusion.

## 1. Model re-derived from primary sources

| element | primary source read by the auditor | status |
|---|---|---|
| P_c ≥ P_B ideal-ignition criterion, S_c = f_c n₁n₂⟨σv⟩E, S_B = C_B n_e² √T_e γ, C_B = 5.34e-37 W m³ keV⁻¹ᐟ² | W-H 2105.10954 text (fulltext lines ~655–720, eqs 6–8) | verified |
| γ = Z_eff(1+1.78t^1.34) + 2.12t(1+1.1t+t²−1.25t^2.5), t = T_e/m_ec² | W-H eq. (D2); Ochs–Fisch 2310.18508 eq. (14), read via alphaXiv: prefactor 7.56e-11 eV cm³/s × x^½, Z_eff = Σn_iZ_i²/Σn_iZ_i, "Ref. 6 missed the x² term" | verified. 7.56e-11 eV cm³/s/√511 keV = 5.36e-37 W m³ keV⁻¹ᐟ², which is 0.3% from 5.34e-37 and covered by the producer's K hull |
| optimal mix k_j = 1/(2Z_j) ⇒ x = n_B/n_i = 1/6, Z_eff = 3 | W-H eq. (D3)–(D4) and footnote 138 | verified; n_e = (1+4x)n_i and Z_eff = (1+24x)/(1+4x) re-derived |
| Wang et al. S-factor, Table I, eqs (1)–(6) | 2601.00241 v1, read in full via alphaXiv | every coefficient in `fits.json` (`wang2026_pB11_S_factor`) matches Table I, including A₄ = 4.3430×10⁵ and x = (E−E₁)/100 keV. Seg. 1 reprints NS. ⟨σv⟩ = (8/π)^½ μ^-½ T^-3/2 ∫σE e^{-E/T}dE matches the code |
| Wang Fig. 8 text "T_e = T … bremsstrahlung exceeds fusion over the entire range" | same | verified. Their composition f₁ = 1/2, f₂ = 1/10 is x = 1/6, and their bremsstrahlung is Rider's, not Putvinski's (as RESULT says) |
| Bosch–Hale 1992 D-T C1–C7, B_G, m_rc² and the cross-section Padé coefficients | primary **not obtained** | the code values agree with the auditor's recollection of BH92 Tables IV/VII. The auditor's sv_BH(10 keV) = 1.1362e-22 m³/s matches BH's tabulated 1.136e-16 cm³/s. Not primary-pinned |
| Nevins–Swain 2000 P1–P7, E_G, M_rc², resonant term 5.41e-15 cm³/s·T^-3/2 e^{-148/T} | primary **not obtained** | magnitude check: NR + resonance = 3.39e-22 m³/s at 300 keV. The code's mixed-unit sum is consistent only if P1 yields m³/s, and the internal check below shows that it does. Not primary-pinned |

Internal NS check, re-run independently (scipy quad of the NS S-factor, μ = 859526 keV):

| T (keV) | 50 | 100 | 200 | 250 | 300 | 400 | 500 |
|---|---|---|---|---|---|---|---|
| NS fit / NS integral | 0.985 | 0.996 | 0.986 | 0.977 | 0.965 | 0.940 | 0.917 |

This is identical to `logs/ns_consistency.json`. It excludes gross transcription errors in P1–P7, but it cannot detect
an error of a few percent. Sensitivity: the T_e = T_i exclusion holds for any reactivity up to 2.35× NS. θ* moves
roughly in proportion to the reactivity (see §3), so θ* inherits the unverified NS digits directly.

## 2. Independent computation (auditor's own code, different method)

- **Method.**
  - mpmath interval arithmetic (`mpmath.iv`, 30 digits) for the closed-form fits.
  - A uniform geometric T grid (ratio 1.0002, 11,513 cells) × a uniform x grid (4,500 cells). Each cell gets an upper
    bound from monotonicity, not a direct Arb evaluation of R: x(1−x) is maximised exactly, and a(x) = (1+4x)(1+24x),
    b(x) = (1+4x)², A(t) and B(t) are taken at the lower corner.
  - B(t) is increasing on [0,1] by the Lean lemma. t is taken with m_ec² = 511 for a smaller t, K at the hull top
    and E = 8.70 MeV. Floats are combined with a 1+1e-9 safety factor.
  - Wang reactivity: scipy quad point values (rel. tol 1e-11, with a 1e-6 safety factor) and the monotone T-cell
    bound. The Wang numbers are therefore **not** rigorous on the auditor's side (Tier X); NS and D-T are.
  - θ*: bisection on the upper bound; the lower side is checked by evaluating the producer's witness points.

| quantity | producer (certified) | auditor |
|---|---|---|
| D-T T_ign, authors' code model (fig6, f_c = 0.2, NRL C_B, 6.242e18) | [4.2989514, 4.2989523] | **[4.2989517, 4.2989519]**, iv, single sign change certified on [0.2, 100] keV |
| D-T T_ign, text C_B and 1.6e-16 J/keV, f_c = 0.2 | [4.299592, 4.299593] | [4.2995924, 4.2995926], iv |
| D-T T_ign, **pure text** (f_c = 3.5/17.6) | not reported | **[4.3071225, 4.3071227]**, iv; still "4.3" |
| TP min, gate model (integrated BH σ, relativistic γ, code constants) | [2.94410, 2.94502]e21 at [14.13, 14.44] keV | 2.94502e21 at 14.285 keV (float) |
| LP min, gate model | [1.55227, 1.55279]e20 at [25.59, 26.21] keV | 1.55279e20 at 25.90 keV (float) |
| TP / LP min, param. non-rel., text C_B/J, f_c = 0.2 | [2.94923, 2.95056]e21 / [1.5570, 1.5577]e20 | 2.95047e21 / 1.5577e20 (float) |
| TP / LP min, **pure text** (f_c = 3.5/17.6), param. non-rel. | not reported | TP: **certified (iv, adaptive cells) n T τ_E ≥ 2.95e21 on all of (T_ign, 100] keV**, and iv value 2.968458e21 at 14.2486 keV, so min ∈ [2.95e21, 2.96846e21] and it **prints 3.0e21**. LP: 1.56693e20 at 25.98 keV (float) |
| TP min, param. rel., code constants | [2.96275, 2.96409]e21 | 2.96409e21 (float) |
| p-¹¹B max R at θ = 1, NS, box | [0.42139, 0.42556] | **[0.42140, 0.42470]**; argmax (201.9 keV, x = 0.1005) |
| same, NS, x = 1/6 | [0.39016, 0.39240] | [0.39016, 0.39311] at 204.5 keV |
| same, Wang, box | [0.42869, 0.43260] | [0.42905 (float), 0.43212] at (208.4 keV, 0.1008) |
| same, Wang, x = 1/6 | [0.39732, 0.40083] | [0.39765 (float), 0.40038] at 211.4 keV |
| m*, NS | [2.350, 2.373] | [2.355, 2.373] |
| θ*, NS box | [0.4223, 0.4308] | float θ_c = 0.42868. Upper bound < 1 certified at θ = 0.43125. Producer witness (243.48 keV, 0.0921875, θ = 0.422282) re-evaluated with iv at the low ends of all constants: R ∈ [1.0077322, 1.0077331] |
| θ*, NS x = 1/6 | [0.3753, 0.3828] | float 0.38107. U < 1 at θ = 0.38281. Producer witness at θ = 0.375251: iv R ∈ [1.0082393, 1.0082399] |
| θ*, Wang box | [0.4381, 0.4470] | float 0.44510; U < 1 at θ = 0.446875. Producer witness at θ = 0.438142: float R = 1.0094 |
| θ*, Wang x = 1/6 | [0.396, 0.402] | float 0.39878; U < 1 at θ = 0.400. Witness (261.65 keV, θ = 0.396): float R = 1.0015 (producer L = 1.00037, a thin margin) |
| max R at θ = 1/3, x = 1/6 (Fig. 28 check) | ≈1.11 (NS), ≈1.16 (Wang), Tier X | 1.1132 at 248.1 keV (NS); 1.1606 at 268.5 keV (Wang) |
| Wang/NS reactivity ratio at 50, 100, 150, 200, 300, 400, 500 keV | 1.016, 1.000, 1.005, 1.016, 1.070, 1.154, 1.262 | 1.0160, 1.0002, 1.0050, 1.0164, 1.0698, 1.1542, 1.2616 (float) |

Every producer enclosure contains the auditor's independent value. The θ ≥ θ_hi ⇒ R < 1 reduction (P_B increasing in
T_e for T_e ≤ 500 keV < m_ec²) is correct.

## 3. Box, fit range and omitted terms

- **Box artefacts.** None found. The maxima are interior: (202 keV, x ≈ 0.10) at θ = 1 and (235–259 keV, x ≈ 0.093)
  at θ_c. Widening x to [0.005, 0.95] (NS), or T_i to [20, 1000] keV as well (Wang), leaves max R and θ_c unchanged
  (float).
- **Fit-validity artefacts.** NS is used only inside its stated 50–500 keV range. Wang is used inside its 0–10 MeV
  S-factor support.
- **Sensitivity** (float, Tier X).
  - Rider bremsstrahlung (Wang's choice): max R at θ = 1 is 0.438 (NS) and 0.447 (Wang); θ_c is 0.434 and 0.452.
  - E = 8.682 MeV: θ_c is 0.4277.
  - Removing Wang's 4.7 MeV resonance: θ_c moves from 0.4451 to 0.4450.
  - Uniform NS reactivity × 1.1 / 1.2 / 1.32: θ_c is 0.477 / 0.524 / 0.579. ×1.32 is an illustrative "+20% cross
    section, +10% kinetic" product, not a pinned value.
  - So "no window at T_e = T_i" is robust. **θ* is not a property of p-¹¹B.** It is a property of the chosen
    reactivity and bremsstrahlung fits.
- **Not included in the model** (RESULT §1/§8 mostly says this already):
  - synchrotron radiation;
  - conduction and transport losses (ideal ignition, not Lawson);
  - any mechanism that keeps T_e < T_i, i.e. the ion–electron collisional coupling that a self-consistent T_e would
    need (as in Wang Fig. 8 and Putvinski);
  - α heating of electrons;
  - ash and impurities;
  - kinetic or non-Maxwellian enhancement (bounded only through m*);
  - the uncertainties of the fits themselves.
- Every claim must read "in this ideal 0-D model, with these fits, in this box". RESULT §8/§9 is consistent with that.
  The θ-robustness sentence in §1 needs a qualifier (correction C4).

## 4. Controls

- **N1** (reactivity × 0.5) and **N2** (bremsstrahlung removed) both FAIL the gate, as required. The auditor read the recorded check
  vectors in `logs/certify.json`; the gate code itself was not re-run.
- **The D-T gate checks the D-T pipeline, not the p-¹¹B conclusion.** G3 ("no window") still passes under N1, because
  halving the reactivity only strengthens an exclusion. What does show that the p-¹¹B pipeline can detect a window are
  the certified θ* witnesses (R > 1 at θ_lo), the θ = 1/3 check (R ≈ 1.11) and N2. RESULT should say this explicitly
  (correction C6).
- **Gate thresholds were fixed after a float run.** The gate window for G2 is [2.85e21, 2.95e21), and the gate model
  (integrated BH, relativistic γ, f_c = 0.2) was chosen after a float run had shown that another reading rounds to
  3.0e21. This is disclosed (Deviation 6). The positive control therefore passes for the authors'-code model only. The
  most literal text reading prints 3.0e21 (see C1). The kill criterion "(a) reproduces the published D-T numbers to the
  printed digits" is met only in that conditional sense, and the status line should say so (C2).
- **Lean N3.** Each planted control fails because the same proof script (nlinarith/linarith) fails. The auditor
  checked that each planted statement is actually false:
  - at x = 1/6: 21·5/36 = 2.917 > 25/9 = 2.778;
  - at t = 1: 1 + 2.2 + 3 − 7 = −0.8;
  - at t = 2: 1 + 4.4 + 12 − 4.375·2^2.5 ≈ −7.35.
  So the controls are valid. They show that the script cannot prove these statements; the falsity check above shows
  that no proof exists.

## 5. Lean (auditor recompilation)

- **`scripts/certified_numerics/lean_pinned.py compile Core.lean`** (Lean 4.34.1 + Mathlib d13f23b7).
  - rc 0 in 5.5 s, with no warnings.
  - `#print axioms` gives [propext, Classical.choice, Quot.sound] for all four declarations (`optimal_mix`,
    `optimal_mix_eq`, `rpow_25_le_sq`, `ee_term_deriv_pos`).
- **Separate compile and kernel replay.** The auditor compiled a byte-identical copy of Core.lean to an olean under
  `/tmp/e1audit/olean` and ran `leanchecker PbIgnition.Core`: rc 0 in 40.2 s.
- **Controls.lean.** rc 1, with errors at lines 23, 28, 32 and 33 (`ctl_mix_21`, `ctl_coeff_7`, `ctl_wrong_range`).
- **Escape grep** over both files for `sorry|admit|native_decide|axiom |set_option|#exit|skipKernelTC|addDecl|`
  `implemented_by|extern|unsafe|macro|elab|@[|opaque|decide`. The only hit is "elab" inside the word "elaborate" in
  the Controls.lean docstring (no code hit).
- **Statement match.** 4.375 = 3.5 × 1.25, so the lemma is the exact derivative of t(1+1.1t+t²−1.25t^2.5). The real
  literals are exact decimals in ℝ.
- **leanchecker negative control.** Same LEAN_PATH, module `PbIgnition.DoesNotExist`: rc 1 ("Could not find any
  oleans"). The rc 0 above therefore reflects a real replay of `PbIgnition.Core`.
- **Not re-run by the auditor:** the binding `anse/formal/lean_runner.py` gate (the producer ran it,
  `logs/lean_runner_core.json`).
- **Still missing:** a statement-lock entry. Until then the two lemmas are kernel-checked and independently replayed,
  but not yet Tier A under the repo's definition. They cover only these two algebraic facts. No interval enclosure is
  in Lean.

## 6. Fig. 28 remark

- W-H caption (fulltext): "showing that P_B always exceeds P_c when T_e ≳ T_i/3. This plot uses the parameterized
  p-¹¹B reactivity in Ref. 23 [Nevins–Swain]". The mix is the k_j = 1/(2Z_j) optimum, x = 1/6.
- In the same model, the auditor finds max P_c/P_B = 1.113 at T_e = T_i/3, at 248 keV. The threshold is
  θ_c ≈ 0.381; the certified interval is [0.3753, 0.3828].
- So the literal reading of the caption fails between 1/3 and about 0.38. The "≳" makes it an approximate figure
  reading.
- RESULT's wording is accurate and neutral: "not an error in their conclusions; we report the sharper certified value";
  §9 says "Not that W-H's 'T_e ≳ T_i/3' is wrong". No correction needed.

## 7. Wording

- RESULT contains no reactor, feasibility, climate or medical claims. The Ochs–Fisch reactor-breakeven numbers appear
  only as out-of-scope context.
- RESULT does not use "breakthrough".
- The tier is stated as C, with Tier A only for the two lemmas. That is correct.

## 8. Corrections (old → new)

- **C1, RESULT §2, D-T variants table, first row label.**
  - Old: "parameterized σv, non-rel., text constants (pure eq. 8/22 reading)"
  - New: "parameterized σv, non-rel., text C_B and keV→J, code f_c = 0.2"
  - Add a row: "parameterized σv, non-rel., all text constants incl. f_c = 3.5/17.6 (pure eq. 8/22 reading) |
    T_ign [4.3071225, 4.3071227] | argmin TP ≈14.25 | min TP ∈ [2.95e21, 2.96846e21] → **3.0** |
    argmin LP ≈25.98 | min LP ≈1.567e20 → 1.6". The T_ign and the TP bound are rigorous (auditor, mpmath.iv); the
    argmins and LP are float (Tier X). The producer should certify the row with their own pipeline before quoting it
    as Tier C.
  - The third row, "integrated σv, non-rel., text constants", also uses f_c = 0.2 (`FC_CODE` in
    `e1_certify.py:391–399`). Relabel it the same way.
  - Control P2 in §3, "text constants": the code (`e1_float_indep.py` lines 99 and 104) uses f_c = 0.2. Relabel as
    "text C_B/J, f_c = 0.2".
- **C2, RESULT §2 Finding and status line.**
  - Add to the Finding: "The most literal reading of the text (eq. 8/22, Bosch–Hale parameterized, f_c = 3.5/17.6,
    C_B = 5.34e-37, 1.6e-16 J/keV) gives 2.968e21, which prints as 3.0e21."
  - Old status sentence: "The certified-numeric gate passes"
  - New: "The certified-numeric gate passes for the model the authors' code ran (the gate model was chosen after a
    float run; Deviation 6)".
- **C3, RESULT §6 "Not done".**
  - Old: "leanchecker kernel replay; a statement-lock entry; producer ≠ verifier recompilation"
  - New: "a statement-lock entry. (Independent recompilation and leanchecker replay done by the auditor on 2026-10-28,
    `AUDIT.md` §5.)"
  - Old: "Tier A *pending independent verification*"
  - New: "kernel-checked, independently recompiled and leanchecker-replayed by the auditor; Tier A once a
    statement-lock entry exists"
  - Apply the same change to `result.json` → `tiers.lean_lemmas`.
- **C4, RESULT §1 "Robustness across fits", second bullet.**
  - Old: "a window needs T_e/T_i below about 0.42–0.45"
  - New: "under these two fits and Putvinski's bremsstrahlung, a window needs T_e/T_i below about 0.42–0.45. The
    threshold scales with the reactivity: a uniform ×1.2 on NS raises it to about 0.52, and Rider's bremsstrahlung
    moves it by about +1% (auditor, Tier X)".
- **C5, RESULT §1 E1c.**
  - Old: "there is no ideal-ignition window in this model under either fit."
  - New: "there is no ideal-ignition window in this ideal 0-D model (no synchrotron, no transport, Maxwellian, no
    T_e-maintaining mechanism) under either fit, on T_i ∈ [50, 500] keV, x ∈ [0.05, 0.5]. The maximum is interior, and
    widening the box does not change it (auditor float check)."
- **C6, RESULT §3 Controls, a new sentence after the table.** "G3 does not discriminate (N1 passes it). The p-¹¹B
  pipeline's ability to find a window is shown by the θ* witnesses, by θ = 1/3 (R ≈ 1.11) and by N2."
- **C7, RESULT §10 Files.**
  - Old: "`papers/wurzel_hsu_2105.10954_fulltext.txt`", "`downloads/wurzel_hsu_code/`: MIT; …",
    "`downloads/*/*.html` …"
  - New: "Third-party material (W-H full text, W-H code at 4ae563bf, paywall and challenge pages) is not in the
    repository. It was moved out on 2026-10-28; re-fetch it from the sources in `fits.json`. The sha256 values in
    `result.json` / `logs/sha256.json` identify those files."
  - Also annotate the `data/downloads/*` and `data/papers/*` keys in `result.json` with "not in repository". The
    auditor verified that 3 of these hashes match the moved copies.
  - `code/e1_hashes.py` lines 32–34 point at the removed `data/downloads` path. Note this, or make the script skip a
    missing path.
- **C8, result.json `E1b_theta_star.Wang_WHmix_scan["0.396"]`.** Copy the witness location, argmax
  (261.6496 keV, 1/6), from `logs/certify_wang_mix.json`, and note the thin margin (L = 1.00037).
- **C9, RESULT §4 / §7.1.** Add: "The independent auditor also could not obtain Bosch–Hale 1992 or Nevins–Swain 2000;
  the coefficients remain secondary (author code) only."

## 9. What remains unverified

- NS 2000 P1–P7 and the resonant term, and the BH 1992 coefficients, against the primary papers. Both auditor and
  producer are limited to the author code plus internal consistency checks.
  - The auditor's agreement with recalled BH92 values is memory, not a pinned source.
  - One alphaXiv search for an arXiv paper reprinting the coefficients found none: Wang 2601.00241 reprints only the
    NS S-factor, and Cai et al. 2201.12818 uses Sikora–Weller without coefficients.
- The auditor's D-T TP/LP minimisers and the gate-model minima are float (Tier X), not rigorous.
- Putvinski 2019 (bremsstrahlung eq. 7 is seen only through OCR). Its form is consistent with W-H (D2) and Ochs–Fisch
  (14), both of which the auditor read.
- The auditor's Wang-side numbers are float (Tier X), not rigorous. The auditor did not re-run the producer's Arb
  integrals.
- Monotonicity "derivative > 0 ⇒ increasing" is not formalised (Tier C).
- No statement lock for the Lean lemmas.
- Tentori–Belloni 2023 and Sikora–Weller as fits: not used. "Updated fit" means Wang 2026 only.
- The repository guards (`antigravity_guard.py`, `test_rigor_guard.py`) fail on pre-existing files, as RESULT §7b
  reports. The auditor did not re-run them or pytest.
