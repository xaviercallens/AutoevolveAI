# Independent adversarial audit: B1 paper (papers/p2_quantum_transition)

- Auditor: a separate Claude agent, not the producer or the paper writer. It did not write any producer or paper code.
- Date: 2026-10-26.
- Scope: `main.tex`/`main.pdf`, `gen_numbers.tex`, `gen/*.tex`, `data/`, `ledger/`, `publication_meta.json`;
  `results/proposal2/2026-10-26/B1/` (TRANSITION.md, result files, code/); the stored sources in
  `~/programmes-2026-10-26/B1/src*`.
- Auditor scratch: `/tmp/b1audit/indep.py` (independent code, written from scratch) and `/tmp/b1audit/indep_out.json`
  (its output).

## VERDICT: ACCEPT_WITH_CORRECTIONS

The physics and mathematics check out step by step. The headline numbers reproduce independently. The negative result
is mostly well scoped.

The four BLOCKING items below must be fixed before release:

- one is a false statement about a source;
- one is a verdict sentence that overstates how independent the negative verdict is of SCHA;
- one is the scope of the title;
- one is the audit disclosure.

None of them changes the verdict class. The kill criterion is met through the "disappears beyond harmonic (within
SCHA)" leg on its own.

## 1. Independent re-computation (auditor code, cores 6,7)

The auditor's code shares nothing with the producer's:

- real-space D(k) in fractional k coordinates;
- a uniform half-shifted midpoint grid over the reciprocal cell, not the Duffy–Gauss rule;
- a finite-difference Laplacian y²(∂xx+∂yy) at ρ with Richardson extrapolation;
- an SCHA solved by its own mixing iteration with the closed-form Gaussian averages.

All values are at a = 1.

| quantity | auditor | paper / data |
|---|---|---|
| Lap E_st(ρ) | 0.4765235166 | 0.4765235167 |
| c_st | 0.119131 | 0.11913 |
| E_zp(ρ) (n=256) | 1.5033523636 | 1.5033523522 |
| c_zp (n=128 and n=256 agree to 1e-6) | −0.961984 | −0.96198 |
| ħ* = −c_st/c_zp | 0.123839 | 0.1238 |
| γ(ħ*) | 0.3130 | 0.313 |
| γ(0.0942) | 0.2730 | 0.273 |
| Λ_L(0.23) | 0.06686 | 0.0668 |
| E_SCHA(ρ, ħ=0.1) (n=64 → 128, converging) | 0.2267499684 → 0.2267499075 | 0.2267498988 |
| Lap E_SCHA(ρ, ħ=0.15) | +0.116975 | +0.117 (scha.json 0.1169747) |
| harmonic Lap at ħ=0.15 | −0.10067 | −0.101 |
| SCHA ΔE of 0.30+0.96i at ħ=Λ_1=0.0942 | +1.652e-3 | +1.651e-3 (scha.json edge point) |
| harmonic ΔE of 0.30+0.96i at ħ=0.10 | −2.858e-4 | −2.86e-4 |
| harmonic ΔE of 0.30+0.96i at ħ=0.0942 | +2.1e-6 (≈ a tie) | Λ_1 = 0.09424 |

The SCHA verdict at a = 1, ħ = 0.15 is reproduced with a different quadrature and code: the triangular lattice is
SCHA-stiff while the harmonic curvature is negative. This is a stronger independence check than the Python/Rust
cross-check (see N2).

## 2. Physics and mathematics, step by step

- **Units (Step 0).** Units: H/ε = −½ħ_eff²∇² + V, with ħ_eff = ħ/√(mεl²).
  - The phonon energy is ħω/ε = ħ_eff√λ(D).
  - Hence E = E_st + ħ_eff E_zp, with E_zp = ½⟨√λ1+√λ2⟩.
  - Hess V = (−2πaI + 4π²a²RRᵀ)e^{−πa|R|²}.
  - Per mode, ⟨|u|²⟩ = ħ/(2mω), so ⟨|u|²⟩/l² = ħ_eff·½⟨tr D^{−1/2}⟩.
  - GCM conversions: ρσ² = 1/(πa) and ħ/√(mεσ²) = ħ_eff√(πa).
  - All correct.
- **Curvature (Steps 2–3).** The D3 stabiliser makes the Hessian scalar, so c(ħ) = c_st + ħ c_zp and
  ħ* = −c_st/c_zp. Correct, and reproduced numerically (above). Montgomery gives a minimum, i.e. c_st ≥ 0; strict
  positivity is the numerical value (N8).
- **Cubic invariant (Step 4).** The algebra is correct:
  - With the order-3 rotation w→ωw, the allowed monomials are w^m w̄^n with m ≡ n (mod 3).
  - The reflection −τ̄+1 fixes ρ, so the invariant is Re w³.
  - T(w) = ħ* + κ r cos3θ + O(r²) with κ = (s3 + ħ* z3)/|z2|.
  - At ρ the rays Re τ = ½ (90°) and |τ| = 1 (tangent at 150°) differ by 60°, and the Cayley map is conformal.
  - So the prediction "equal and opposite slopes" is right. The measured ratios are −1.023, −1.010, −1.009 and −1.010
    for a = 1, 0.5, 0.7 and 0.8, and −0.950 at a = 1.2 with both signs reversed (gen/tab_rays.tex, extra_checks.json).
  - The paper correctly says that the first-order claim rests on Λ_1 < ħ*, because κ must vanish between a = 1 and
    a = 1.2. See N5 on what "first order" means here.
- **Lindemann (Step 6).**
  - Λ_L = γ_c² a_nn²/U and Λ_1/Λ_L = (γ(Λ_1)/γ_c)². Correct and reproduced.
  - The convention matches Astrakharchik et al.: the definition of a_L **is** in the source (B1). The QMC γ_c are
    true-⟨u²⟩ values, while the paper's γ is harmonic. The paper notes this mismatch; it is not like-for-like (N10).
- **SCHA (Step 7).** Checked:
  - C_R = ħ_eff⟨(1−cos k·R)D_eff^{−1/2}⟩;
  - the Gaussian average det(I+2bC)^{−1/2}exp(−bRᵀ(I+2bC)^{−1}R);
  - the kinetic term (ħ_eff/4)⟨tr D_eff^{1/2}⟩, which is half the zero-point energy;
  - the stationarity condition;
  - the small-ħ limit E_SCHA = E_st + ħE_zp + O(ħ²): the ½tr(C_R Hess V) term sums to another (ħ/4)⟨tr D^{1/2}⟩.

  The variational (Rayleigh–Ritz) property is stated correctly, including that differences of upper bounds do not order
  the true energies. The curvature is taken from E_SCHA by stencil, which is the right object.
- **Does SCHA justify "removes the transition"?** Only within SCHA, and the paper says so in Limitations.
  - The stiffening is an O(ħ²) effect. SCHA misses the second-order cubic term at exactly that order, and that term's
    sign on the shear curvature is unknown.
  - Worse, a quadratic through the three slope-control points gives the expansion
    (Lap E_SCHA − Lap E_st)/ħ = −3.8477 + 16.5ħ − 141ħ².
    - The intercept matches 4c_zp = −3.8479.
    - The ħ³ coefficient is a 3-point interpolation and therefore unreliable.
    - At ħ ≈ 0.1 the ħ² and ħ³ terms are comparable (0.165 against −0.141).
  - So no perturbative O(ħ²) argument settles the question, and the SCHA result is a non-perturbative statement within
    a variational ansatz.
  - The abstract's "The decisive test is anharmonic … the transition disappears" therefore needs scoping (B3).

## 3. Numbers and provenance

- **Data copies.** `data/{result_numbers,scha,scha_extend,summary,b1a_curvature}.json` and TRANSITION.md are
  byte-identical to the producer tree.
- **Rust.** `ledger/rust_test.log` contains "63 passed; 0 failed; 1 ignored". The sha256 of `scha.rs` is
  35c65007…e98a, matching publication_meta.
- **Generated values.** The tables and macros in gen/ match the data files at the spot-checked points: tab_main a = 1
  row, tab_lindemann a = 1 row, tab_scha a = 1 row, the scha.json lap_ladder, and the extra_checks rydberg and
  shoulder_ft blocks.
- **Producer-vs-writer discrepancies:**
  - **Slope −3.843 vs −3.846.** Both are legitimate. The writer used a least-squares line through the 3 points
    (gen_inputs.py l.114, −3.84328); the producer used the 2-point extrapolation 2s(0.0025) − s(0.005) = −3.84592. A
    quadratic gives −3.8477, the closest to −3.8479. The paper does not say which method it used (N1).
  - **27 µs vs 130 µs.** The paper is correct and TRANSITION.md is wrong. Source (1602.06313 l.289–290, 473–476): the
    bare 31P1/2 lifetime is ≈27 µs; the extracted dressed loss time is 130(20) µs, against 2.2 ms expected.
    TRANSITION.md calls 27 µs the "dressed-state lifetime" (N3).
  - **SCHA range.** The paper's 0.27–0.33 and γ_SCHA 0.60–0.87 follow from scha.json (a = 1: interval (0.30, 0.3347);
    first stable competitor below at 0.3347 with γ = 0.87). TRANSITION.md's "0.27–0.31 … γ 0.6–0.75" omits a = 1. The
    paper resolved this correctly.
  - **Rydberg energy.** The paper's 100.7 Hz is right; TRANSITION.md has 100.5. Auditor arithmetic: ħ²/(m_Rb87 R_c²)/h
    = 100.706 Hz, U0/E = 17.87, ħ/√(mU0R_c²) = 0.2365.
  - **TRANSITION.md mislabel.** It says the harmonic Λ_1 winner is "2.6e-5 above triangular". In scha.json, 2.58e-5 is
    the **arc point nearest ρ** (x = 0.4826). The winner (0.30, 0.96) is +1.65e-3 above, which the auditor
    reproduced. main.tex does not repeat the mislabel (the macro \SchaMinDEOne is unused in the prose), but see N3.

## 4. Literature

- **Quotes checked verbatim against the stored pdftotext:**
  - Astrakharchik p.3: γ = 0.230(6), hard disks 0.279, Yukawa 0.235(15), Coulomb bosons 0.24(1).
  - Prestipino p.11 "The Gaussian repulsion (n = 2) is a marginal case: despite there is no evidence of a cluster
    crystal in two or three dimensions…", p.15 "swept away at zero temperature", p.25 "freezing is completely washed
    out in the Gaussian, n = 2 case" and "realistic for weak interparticle forces".
  - Henkel p.2 "due to the inner potential plateau at r < Rc, the momentum space potential Ũ has negative attractive
    contributions around k = krot ∼ 2π/Rc", and footnote [26] "C̃6 M/h̄² Rc⁴ < 10−2".
  - Zeiher: 1.8 kHz, 532 nm, Rc/alat = 2.02, τr = 27 µs, 130(20) µs, 2.2 ms.
  - All match.
- **Soft shoulder.** The claim that Rydberg dressing is a soft shoulder is supported by two re-read sources (Zeiher's
  and Henkel's functional forms) and by the paper's own Hankel transform (min −0.0448 at kRc = 4.82; Gaussian control
  8.9e-16). The "therefore cluster/supersolid class" step leans on a [sub] criterion (N7).
- **Cluster-crystal criterion.**
  - The negative-Fourier-component criterion itself is attributed only to [sub] sources; Likos was not opened. The
    paper says so.
  - The ledger row B1-C-0008 depends only on the closed-form positive Gaussian transform (B1-C-0007) and the re-read
    Prestipino p.11 quote (B1-C-0102), and explicitly excludes the [sub] sources. Correct.
  - No [sub] item appears as a ledger dependency (checked B1-C-0008 and B1-C-0009).
- **Astrakharchik a_L definition: wrong in the paper (B1).**

## 5. Overclaim review

The paper does honestly say:

- harmonic plus SCHA only;
- PIMC not run, BLOCKED with numbers;
- Bravais lattices only;
- winners sit on the stability edge;
- the Lindemann reading at Λ_1 is "inconclusive to adverse".

The remaining overclaims are B2 and B3.

## 6. publication_meta.json

It is accurate on these points:

- the numbers;
- 38 ledger rows (confirmed);
- the Rust commit, hash and test counts;
- the PIMC finite-size percentages (2.0e-4/2.86e-4 = 70 % at M = 8; 7.0e-5/2.86e-4 = 24 % at M = 10).

It needs these changes: B1 (a_L note is false), B3 (title), B4 (audit status), N11 (wording of the continuation run).

---

## BLOCKING

**B1. The a_L definition is in the source; the paper says it is not.**

Source: Astrakharchik et al. cond-mat/0608246v2, p.3, verified with `pdftotext -layout`. It reads: "In the solid phase
static structure factor is discontinuous and has a δ-function peak at inverse lattice site length
a_L⁻¹ = (√3n/2)^{1/2} = 0.93...n^{1/2}." At n = 1 this gives a_L = (2/√3)^{1/2} = 1.0746 = a_nn. The producer was
right; the writer's correction was wrong.

Fixes:

- **main.tex l.169.** Replace "reading $a_L$ as the nearest-neighbour distance and $\langle(r-r_c)^2\rangle$ as the
  total 2D displacement is our assumption (\tier{C, B1-C-0011}); we did not find the definition of $a_L$ in the text."
  with: "the same page defines the 'inverse lattice site length' $a_L^{-1}=(\sqrt3 n/2)^{1/2}$, i.e.\ $a_L=a_{nn}$
  (\tier{C, quote, B1-C-0116}); reading $\langle(r-r_c)^2\rangle$ as the total 2D displacement (r is a 2D position) is
  our reading (\tier{C, B1-C-0011})."
- **Limitations bullet 2.** Change "our reading of $a_L$ is an assumption" to "our reading of $\langle(r-r_c)^2\rangle$
  as the total 2D displacement is a reading, not a quoted definition".
- **Ledger.** Add the quote row B1-C-0116, with a verbatim file run through `run_citation.py` as for the others.
  Rewrite B1-C-0011 to drop "The definition of a_L was not found in the text; this reading is an assumption." Rebuild
  the ledger and rerun the gate.
- **publication_meta.json.**
  - Description, Caveats: delete "and our reading of the lattice length in the cited QMC value is an assumption (not
    found in the source text)".
  - Notes: replace "The producer's note that the QMC source defines a_L^-1 = (sqrt(3) n/2)^(1/2) was not found in the
    source text; a_L = nearest-neighbour distance is recorded as an assumption." with "The QMC source defines
    a_L^-1 = (sqrt(3) n/2)^(1/2) (p.3), i.e. a_L = nearest-neighbour distance."

**B2. The claim that the verdict "does not rest on SCHA alone" is false where it matters, and the spinodal reading
depends on γ_c.**

- B1b puts the *spinodal* ħ* at or beyond the Lindemann point only for γ_c ≤ 0.28. With the harmonic γ_c = 0.30, which
  the paper itself plots and which is consistent with the prereg's "harmonic ⟨u²⟩" estimate, γ(ħ*) = 0.299, 0.280, 0.280, 0.286 and 0.298
  for a = 0.5–0.9 (tab_main). The spinodal then *precedes* the 0.30 Lindemann point.
- The physically relevant point is Λ_1, not ħ*. At Λ_1, B1b is inside the band for a = 0.5–1.
- So in the window where Λ_1 is inside the band (a ≈ 0.5–1 for γ_c ≤ 0.28, i.e. \BBInsideNarrow; a ≈ 0.45–1.1 for γ_c = 0.30, i.e. \BBInsideWide), the negative verdict rests on SCHA alone.

Fixes:

- **l.174, Reading (a).** Change "the spinodal is at or beyond melting for every $a$" to "the spinodal is at or beyond
  melting for every $a$ if $\gamma_c\le0.28$; for $\gamma_c=0.30$ it precedes the Lindemann point for $a=0.5$--$0.9$
  ($\gamma(\hb^*)=0.280$--$0.299$)".
- **Abstract l.57–58.** After "at or beyond the top of the quantum-Monte-Carlo band $\gamma_c\in[0.23,0.28]$", add "(but
  below the harmonic value $0.30$ for $a=0.5$--$0.9$)".
- **l.197.** Replace "The negative net result does not rest on SCHA alone: B1b already puts $\hb^*$ at or beyond the
  Lindemann point." with "Where $\Lambda_1$ lies inside the Lindemann band ($a=\BBInsideNarrow$ for $\gamma_c\le0.28$, $a=\BBInsideWide$ for $\gamma_c=0.30$) the negative verdict on the
  first-order point rests on SCHA alone; B1b puts only the spinodal $\hb^*$ at or beyond the Lindemann point, and that
  only for $\gamma_c\le0.28$. (For comparison, $\gamma_{\rm SCHA}(\rho)$ at $\hb^*$ is $0.30$ at $a=0.5$ and $0.34$ at
  $a=1$, Table~\ref{tab:ext}.)"
- **l.250 (Limitations).** Replace "Hence B1c holds within SCHA; the net negative verdict also rests on B1b." with
  "Hence B1c holds within SCHA, and in the window where $\Lambda_1$ is inside the Lindemann band ($a=\BBInsideNarrow$ for $\gamma_c\le0.28$, $a=\BBInsideWide$ for $0.30$), the net negative
  verdict rests on SCHA alone."
- **l.245.** Change "and the harmonic spinodal lies at or beyond melting" to "and the harmonic spinodal lies at or
  beyond melting for $\gamma_c\le0.28$".
- **Generated numbers.** The numbers in these replacement sentences (0.280–0.299, 0.30, 0.34, the a-windows) should be
  emitted as macros by gen_inputs.py from tab_main, tab_ext and the band readings, not typed in by hand.
- **Elsewhere.** Make the same qualification in ledger B1-X-0013 and B1-X-0004, and in the TRANSITION.md-derived
  sentence in publication_meta ("at or beyond the top of the quantum-Monte-Carlo band").

**B3. The title and abstract present SCHA's verdict as physical absence.**

The evidence is a Gaussian variational theory that omits the second-order cubic O(ħ²) term, and the stiffening it finds
sits at exactly that order (§2: non-perturbative even within SCHA).

Fixes:

- **Title (main.tex l.30–33 and pdftitle l.36).** Use "The harmonic triangular-to-oblique instability of the quantum
  Gaussian-core crystal: first order, near the Lindemann melting estimate, and absent in the self-consistent harmonic
  approximation — a preregistered negative result". The original subtitle phrase "a harmonic first-order instability at
  or beyond Lindemann melting" is withdrawn for the reason given in B2: the first-order point Λ_1 lies inside the γ_c
  band for a ≈ 0.45–1.1. An equivalent scoping, such as "No quantum triangular-to-oblique
  transition within the self-consistent harmonic approximation …", is also acceptable.
- **Abstract l.59.** Change "The decisive test is anharmonic:" to "The anharmonic test, within SCHA:".
- **Abstract l.60.** Change "the transition disappears." to "the transition disappears within SCHA."
- **publication_meta.json.** Apply the same title change.

**B4. The audit disclosure is now out of date.**

These passages say no audit was done and must point to this AUDIT.md (independent AI audit, ACCEPT_WITH_CORRECTIONS,
corrections applied; still no human audit):

- main.tex l.41 "(not peer reviewed; unaudited)";
- l.44–46 "No human has audited the work, and no separate AI audit has been done … that audit is still to come";
- l.254 "No audit: unaudited by human or AI";
- publication_meta description "No audit has been done, by a human or by a separate AI agent; … still to come";
- publication_meta notes "UNAUDITED (no human audit, no separate AI audit)".

The ledger rows' `audit: null` fields should record the audit as the ledger tool allows.

## NONBLOCKING

- **N1. Slope method.**
  - In Controls (iv), state "least-squares line through the three points ($\hb=0.0025,0.005,0.01$) extrapolates to
    $-3.843$ (two-point extrapolation $-3.846$, quadratic $-3.848$)".
  - Give the ħ² coefficient as "≈15–16.5 (secant 14.7, quadratic fit 16.5)".
  - Add one sentence: the fitted ħ³ term is comparable to the ħ² term at ħ ≈ 0.1, so the SCHA stiffening is not a
    controlled O(ħ²) correction there.
- **N2. Rust independence.**
  - scha.rs uses the *same* Duffy–Gauss rule (four triangles with apex at Γ) as b1_lib.py, re-implemented; only the
    real-space D differs.
  - Agreement to 1e-16, against a producer N-convergence of 3e-11, means identical discrete sums.
  - main.tex l.233 should say "its own implementation of the same Duffy–Gauss zone rule". The abstract's "two
    independent implementations" should become "two implementations".
  - The independent-quadrature check is this audit's midpoint-grid code (E_SCHA to 9e-9; Lap E_SCHA(0.15) to 3e-7).
    Cite it after B4.
- **N3. Errors in the producer record (TRANSITION.md, copied into data/).**
  - 2.6e-5 is mislabelled as the "harmonic Λ_1 winner": it is the nearest arc point, and the winner is +1.65e-3.
  - "dressed-state lifetime (~27 µs)" should read "bare Rydberg lifetime 27 µs; dressed loss time 130(20) µs".
  - 100.5 Hz should be 100.7 Hz.
  - Append an erratum to TRANSITION.md (do not hand-edit numbers).
  - In main.tex l.189, add that the "≥1e-5" minimum is set by the sampled point nearest ρ (local curvature), and that
    the harmonic edge winners are +1.6e-3 (a = 1) and ≥7.6e-4 (a = 0.5; the tabulated winner (0.305, 0.955) is +8.1e-4) above triangular in SCHA.
- **N4. Ledger row B1-C-0102 abridgement.**
  - "no cluster crystal in 2D or 3D" should read "no evidence of a cluster crystal in 2D or 3D".
  - In main.tex l.220 the p.11 sentence is introduced as part of "the only quantum result is mean-field". In the source
    it is the authors' summary of the (classical) GEM cluster literature (refs [37,38]), not their mean-field result.
    Introduce it as such.
- **N5. Meaning of "first order".**
  - The competitor at Λ_1 is the minimiser of E over the harmonically stable set, and it sits on that set's boundary.
    The producer records that no interior minimum other than ρ exists in the sampled stable set.
  - So this is an energy crossing with a constrained finite-distortion competitor, not a crossing of two local minima.
  - Add one clause in the abstract and §3.2: "first order in the sense that a finite-distortion stable lattice ties with
    ρ before c(ħ) vanishes; the competitor is not an interior local minimum".
- **N6. Rydberg time scale.**
  - "far below the motional time ≈1/(100.7 Hz) ≈ 10 ms" uses the slowest scale.
  - The interaction-set scale √(U0·E_Rc)/h ≈ 426 Hz gives a period of 2.3 ms and 1/ω ≈ 0.37 ms. That is still longer
    than 130 µs, but by a factor of about 3–18, not 75.
  - Replace with "shorter than the interaction-set motional time $1/\omega\sim0.4$ ms (period $\sim2$ ms)".
- **N7. Rydberg class inference.**
  - "The dressed gas therefore belongs to the cluster/supersolid class" uses the negative-Fourier criterion, which is
    sourced only to [sub] papers (Likos not opened).
  - Reword: "it has the negative Fourier component that the cluster criterion (Likos; [sub]) requires, and Henkel et al.
    (re-read) find roton softening and supersolid formation for it".
- **N8. Step 3 wording.** Change "Montgomery gives $c_{\rm st}>0$" to "Montgomery gives $c_{\rm st}\ge0$ (a minimum);
  $c_{\rm st}>0$ is the computed value".
- **N9. Abstract, Tier C sentence.** "ordinary quantum melting does [preempt]" is an inference from the Tier X numbers
  and the Lindemann heuristic, not a literature statement. Move it out of the "Tier C (quotation-checked literature)"
  sentence.
- **N10. Like-for-like comparison.** The γ_c anchors are QMC true-⟨u²⟩ values, while γ is harmonic. The γ_SCHA values
  already computed (Table ext: 0.30 at a = 0.5 and 0.34 at a = 1 at ħ*; 0.287 at Λ_1 for a = 1) are closer to the true
  ⟨u²⟩. Quoting them next to the harmonic γ in §B1b would strengthen Reading (c).
- **N11. publication_meta wording.** Change "a continuation-seeded run over 150 shapes per case beyond the harmonic
  stability edge finds none below triangular" to "a continuation-seeded run over 150 shapes per case (103–114 of them
  beyond the harmonic stability edge) finds none below triangular".

## What was verified as correct

- Units and ħ_eff;
- the harmonic energy, D(k), Hess V and ⟨u²⟩ normalisation;
- the curvature balance and ħ*(1) = 0.1238;
- the κ expansion, D3 invariants and mirror-ray geometry;
- the measured ray ratios;
- the Lindemann identities, sensitivity numbers and table values;
- the SCHA closed-form averages, kinetic term, stationarity condition, small-ħ limit and variational scope;
- the SCHA a = 1 numbers (independently reproduced);
- the PIMC feasibility percentages;
- all spot-checked quotations (verbatim);
- the Rydberg arithmetic;
- the [sub] exclusion from ledger dependencies;
- the Rust test counts and hash;
- the data-copy integrity;
- the kill criterion, verbatim from preregistration.json.
