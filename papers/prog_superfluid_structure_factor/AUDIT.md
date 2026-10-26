# AUDIT — P6 `prog_superfluid_structure_factor` (programmes 2026-10-25)

Auditor: a separate AI agent (Claude), stage AUDIT. I did not write the paper, the Lean code, or the analysis
(producer != verifier at the agent level). No human audit has taken place. I edited nothing except this file. My own
scripts and outputs are in `/home/callensxavier_gmail_com/programmes-2026-10-25/P6/audit/` (`audit_lean.py`,
`audit_he4.py`, `audit_diff.py`, `audit_cite.py`, `audit_bec.py`, and `out/*.json`).

## Verdict: ACCEPT_WITH_CORRECTIONS (no blocking findings)

The Lean module recompiles independently and stays inside the axiom whitelist. The planted controls and my own
mutations are caught. Every He-4 and trapped-gas number I re-derived matches. The hand proofs are correct. Every
citation I checked is real. The tiers are honest, and the paper is unusually explicit about its limits. The
corrections (C1–C4) cover stale verification-status wording, one wrong author initial, one ambiguous scope
statement and one overstated "verbatim". All four should be fixed before Zenodo publication.

---

## 1. Lean: independent recompile, own axiom audit, own planted sorry/axiom

Method (`audit_lean.py`): I called the pinned toolchain (`leanprover--lean4---v4.34.1`, `lake env` of the pinned
openai/math `lean/`) directly. I used a **private olean directory** (`audit/olean`) and did **not** use the
producer's `formal_cert/.olean_out`, so NegativeControls, PositiveControls and Controls import oleans that I built
myself from the current sources.

| file | sha256 (matches paper and publication_meta) | rc | s | `#print axioms` lines | non-whitelist |
|---|---|---|---|---|---|
| Basic.lean | a8ed4357…5cb6432 | 0 | 8.9 | 21/21 declared theorems+lemmas | none |
| NegativeControls.lean | 182f8135…bfc3a | 0 | 6.5 | 4/4 | none |
| PositiveControls.lean | 1555d75c…ffc05 | 0 | 6.4 | 3/3 | none |
| Controls.lean (planted) | a0f2e8ed…0099 | 0 | 6.1 | 2 | `ctl_sorry: sorryAx`, `ctl_axiom: ProgFeynmanBijl.ctl_cheat` (caught) |

Every printed line of the three main files is exactly `[propext, Classical.choice, Quot.sound]`. The three main
outputs contain no `warning` and no `sorry` message. `Controls.lean` is imported by nothing: the only imports in
`formal_cert/` are Basic <- NegativeControls <- PositiveControls, and Basic <- Controls.

Auditor-planted controls (my files; not in the repository):
- **M1, mutation:** in a copy of Basic.lean I replaced the proof of `sector_eigenvalue_le` with `sorry`. The copy
  compiles with rc 0, and `#print axioms` then shows `sorryAx` in `sector_eigenvalue_le`, `feynman_bijl_bound`,
  `feynman_bijl_bound_ground` and `feynman_bijl_gap`. This is exactly the transitive set, so the gate detects a
  hidden gap that sits below the headline theorems.
- **M2, planted:** a new file that imports my Basic olean, with `axiom aud_cheat : False` used to "prove"
  `∀ x : ℝ, x ≤ x - 1`, and a `sorry` "proof" of `sBog 1 ks k ≤ 0`. Both are exposed (`AuditP6.aud_cheat`,
  `sorryAx`). `sBog_le_sqrt`, re-printed in the same file, stays whitelisted.

Elenchus `elenchus_check.py` does not apply in this environment.
- It runs the plain `lean` of the Elenchus repository's own toolchain (4.34.0-rc2) with no Mathlib on the search
  path.
- So all four files return `COMPILE_ERROR: unknown module prefix 'Mathlib'/'Programmes'` (output in
  `audit/out/elenchus_check.json`, rc 1).
- Its syntactic-only mode is refused outside the ratchet self-test.
- The footprint check it would have run is the pinned-toolchain `#print axioms` audit above.
- A source scan found no `sorry` token outside Controls.lean, and no `Prop := True` or `True` conclusion.

Statement-adequacy review (by eye, not machine-checked):
- `double_comm_expect` carries only the hypotheses claimed (H symmetric, Hψ = E₀ψ). `excess_eq_half`,
  `trial_energy_eq` and `feynman_bijl_bound` take the f-sum value and `hsym` as explicit hypotheses, as the paper
  says. The f-sum value enters as a real number coerced to ℂ.
- `feynman_bijl_gap` uses the ground-state property in the form `E0‖x‖² ≤ re⟪x,Hx⟫` and orthogonality of ρψ to the
  whole E₀-eigenspace (`horth`). Both are correctly stated as hypotheses.
- `gap_witness` together with `gap_witness_applies` and `orthonormal_pair_fin2` gives non-vacuity. Each is stated
  for an arbitrary E with a given orthonormal pair, and the existence of such a pair in ℂ² is a separate theorem.
  Combining them is trivial, but it is not stated as a single theorem.
- Caveat: the witness uses a Hermitian ρ, so there `hsym` holds trivially (ρ† = ρ). The physical ρ_k is not
  Hermitian, and no witness exercises a non-trivial `hsym`. This is acceptable for a non-vacuity control, but worth
  one clause in the paper.

## 2. Numbers trace to result files; independent spot re-runs

- `data/` copies are byte-identical to `results/programmes/2026-10-25/P6/` (`test_he4.csv`, `results.json`,
  `analysis.py` checked with `cmp`).
- Raw page `vapor15.htm` sha256 = `b5a3bc07c0fceef753fb4168e5918c5b6cb817c5783a85d688e4906f92f304b8`, as stated.
- **Independent He-4 re-run** (`audit_he4.py`, no producer code):
  - I parsed Table 14.1 myself from the raw page text. My parse gives the same 100 (Q, S, key) triples as the
    producer CSV. My first parse produced one spurious header triple (from "4He" and "Å-1"); I traced it, fixed
    my parser, and the triples then agreed exactly.
  - k* from CODATA ħ, N_A, m₄ = 4.0026032 g/mol and c = 238.3 m/s:
    - k* = 3.003790 Å⁻¹ (paper 3.00379), and 3.00253–3.00505 for c ± 0.1 m/s.
    - ħc = 1.56852 meV Å (paper 1.5685).
  - Δ_ds = |1.458 − 1.376| = 0.082.
  - Verdicts: **29 CONSISTENT / 7 UNDECIDED / 63 REFUTED** (32 X-ray, 31 neutron).
  - Roton region 1.7–2.4: 21 points, all REFUTED, S/B 1.6167–2.4911, minimum margin 0.3280.
  - Free-particle control: 95 nominal / 89 strict.
  - All of these equal `gen_numbers.tex`.
  - I hand-checked the peak point: B(2.058) = √(2.058/6.00758) = 0.5853, S/B = 2.49.
- **Independent trapped-gas spot re-run** (`audit_bec.py`):
  - q = 2.5055 µm⁻¹ from ħq²/2m = h·1.38 kHz (Na-23).
  - S_LDA/B_LDA = 0.5522/0.5829, 0.4149/0.4796 and 0.3633/0.4422 at µ/h = 3.08, 6.72 and 9.30 kHz. These match
    Table 3 (0.552/0.583, 0.415/0.480, 0.363/0.442).
  - Phonon closed form 15π/32·√(ε₀/2µ): relative error 9.99e-7 at ε₀/µ = 1e-6 (paper 1.0e-6).
- Other macros traced in `results.json` or `lean/feynman_bijl_numeric.json`:
  - Steinhauer: 3/13 nominal, max z 0.314, 0 raw, open circles rms 0.026 / max 0.059.
  - Convention failures 16/8/4/0 of 24.
  - Grid 0/42, free 38/42.
  - FP checks 1.7e-15, 6.7e-16, 1.1e-16, 1.8e-16, 200/200, 2000/2000, neg min/median 0.0019/0.079.
  - Feynman self-check 2/68 at Q = 0.213, 0.267.
  - rms about the spline 0.0189.
- Lean rc and seconds in the paper match the result files:
  - `lean/compile_{basic,negctl,posctl,controls}.json` (WORK2): rc 0, 10.5/6.9/6.7/6.2 s.
  - `rerun/summary.json` (paper stage): rc 0, 12.4/8.4/7.5/6.1 s.
- The PDF (14 pp) is newer than main.tex. `main.log` shows no undefined references and no overfull boxes, and the
  PDF text has no "??".

## 3. Human proofs, step by step

All checked by hand:
- **Step 1:** terms (a)–(d) and their signs.
- **Step 2.**
- **Step 3.**
- **Step 4:** the weighted-mean contradiction needs Σw > 0 for strictness, which is given.
- **Step 6, f-sum:**
  - [p, e^{−ik·r}] = −ħk e^{−ik·r}.
  - [e^{ik·r}, k·p] = −ħk² e^{ik·r}.
  - The double commutator equals ħ²k²/m per particle, and cross terms vanish.
  - The CCR trace argument is correct.
- **Step 7:** A(ρ†) ≥ 0 from the ground-state property, giving the factor-2-weaker bound.
- **Step 8:** λᵢ ≥ E₀ by testing on eᵢ, and λᵢ ≠ E₀ from `horth`.
- **Step 9:** ρ†ψ = 0, A(ρ) = 1, f = 1.
- **Step 10:** f = 2 = Nħ²k²/m with m = 1/2, S = 1, bound 1, attained.
- **Step 11:**
  - ε₀ = h_c k²/k* = ħ²k²/2m.
  - S_B² = k²/(k*² + k²).
  - k(k* − k)² ≥ 0.
  - The test logic, and the one-sidedness of the test.
- **Step 12:**
  - w(x) = (15/4)x√(1−x) follows from n(r) = n₀(1 − r²/R²) with r²dr measure, and B(2, 3/2) = 4/15.
  - k*(x) ∝ √x.
  - The phonon limit (15/4)·B(3/2, 3/2) = 15π/32 agrees with Stamper-Kurn p.4.

No errors found.

## 4. Tiers and overclaim

- The tier usage is honest. Tier A attaches to Lean statements only. The f-sum value, the symmetry and momentum
  conservation are hypotheses or C. All Bose-gas values are X. The He-4 arithmetic is X with a C reading. The paper
  says the He-4 outcome is textbook and the formalisation is a textbook argument.
- The post hoc Δ_ds is flagged as a preregistration deviation in four places. I found no "proved/breakthrough"
  language beyond what the tiers support.
- The preregistration entry for P6 (priors 0.6/0.45, kill rule "figures -> Tier X; Lean two budgets") is reported
  accurately.
- Nothing rests on an openai/math theorem; only its pinned toolchain is used. This is stated correctly.

## 5. Citations

`citation_check.py` accepts only theorem-kind quotes, and every L row here is prose or data. I therefore did
**not** relabel the rows as theorems to force it through. Instead (`audit_cite.py`) I used the tool's own
`normalise()` to search each excerpt fragment in the locally held source texts, and checked by eye the fragments
that failed:

- **Stamper-Kurn et al., PRL 83, 2876 (1999), cond-mat/9906035:**
  - The ratio sentence, the Fig. 3 caption (ω⁰_q = 2π × 1.38 kHz), Eq. 3, the LDA density f(n) = 15n/(4n₀)√(1 − n/n₀)
    and the 15π/32 limit are all present in `raw/bec/sk_raw.txt`.
  - The verbatim match fails only because of linearised maths (µ → mu, √ lost, ω → omega) and two-column
    interleaving.
- **Steinhauer et al., PRL 88, 120407 (2002), cond-mat/0111438:**
  - The ×2.3 factor ("increased by a factor of 2.3, giving rough agreement…"; Fig. 4 caption "multiplied by an
    overall constant of 2.3") and Eq. 2 are present.
  - The journal reference is independently confirmed as ref. [4] of Shammass et al.
- **Godfrin et al., arXiv:2012.09067v1** (confirmed on alphaXiv):
  - Title and the seven authors are as cited.
  - "c=238.3 ± 0.1 m/s at saturated vapor pressure" (p.2) and m₄ = 4.0026032 g/mol (p.3) are present. The excerpt
    writes "+-" for "±".
- **Morresi and Garberoglio, arXiv:2501.08730v1** (confirmed on alphaXiv):
  - The title and authors are as cited.
  - The Fig. 2 caption says "Pair distribution function at T = 2 K … experimental measurements are taken from Ref.
    [50]".
  - Ref. [50] = Svensson, Sears, Woods, Martel, PRB 21, 3638–3651 (1980). This confirms the 1989 misprint in
    Donnelly–Barenghi's ref. 10, which I also saw in the raw page.
- **Donnelly–Barenghi web edition:** the keys, ranges, note 4 (the discrepancy, verbatim match) and the Robkoff–Hallock
  title "Structure Factor Measurements at Saturated Vapor Pressure for 1.38 < T < 4.24 K", PRB 24, 159–182 (1981)
  are all in the raw page.
- **Shammass et al., arXiv:1207.3440** (confirmed on alphaXiv, v2): "The experimental values in Fig. 3 have been
  multiplied by a factor of 1.5". The first author is **I. Shammass**, not "Y." (see C2).
- **Feynman 1954, Bijl 1940, Bogoliubov 1947 and the primary PRB papers** are correctly marked "not read".
- The Elenchus ledger gate, which I re-ran myself, prints exactly what `gate_output.txt` records: 11 ×
  `LEDGER_UNAUDITED_TIER_A` flags and 0 blocking findings, rc 1.

## 6. Data provenance

- The He-4 data are a secondary compilation, and all its caveats are disclosed:
  - web edition assumed to match the journal;
  - primary tables unseen (HTTP 403);
  - no σ;
  - no per-point T;
  - the Svensson T = 2 K is inferred.
- The raw HTML and the BEC PDFs and figure crops are kept outside the repository with their hashes and scripts. The
  digitisation scripts are copied into `data/`.
- Not mentioned: Donnelly–Barenghi themselves recommend "X-ray data for Q < 1, and the neutron data for Q > 1". The
  paper uses both sets throughout. The roton-region conclusion does not depend on this, because every point there,
  neutron included, is refuted with a margin of at least 0.328 (see N2).

## 7. publication_meta.json

- Title, sha256 values, Mathlib/openai commit, base commit, arXiv ids and keywords are accurate.
- The related DOIs match each paper's `zenodo_doi.txt`:
  - 23646117 = ar_bogoliubov_sk ("continues" and `bsk`);
  - 23646103 = dipolar exciton;
  - 23646105 = Yukawa;
  - 23646107 = Keldysh;
  - 23646111 = σ=3 enstrophy.
  This is the order the `ar` bib entry assigns.
- Description numbers (k*, 63/29/7, 21 roton points, 1.62–2.49, 0.082, 0 blocking / 11 flags, no rusty/LeanFlow
  change) match.
- **Stale after this audit:** the description and notes say "producer-checked only, no independent recompile, no
  human audit" and "no human and no separate AI agent has audited it". The second half of the first phrase stays
  true; "no independent recompile" and "no separate AI agent" are no longer true (see C1).

---

## Corrections (non-blocking, should be applied before publication)

- **C1. Verification-status wording.** Update the following places to say: independently recompiled by a separate
  AI auditor with a private olean build; axioms identical; planted controls and two auditor mutations caught; no
  human audit; ledger Tier-A rows remain `audit: null`, i.e. no person certified them.
  - In main.tex: the AI-assistance disclosure ("no separate AI agent has audited this preprint or its Lean file";
    "producer≠verifier condition is not met"), the abstract ("producer-checked"), the Step-table and Section 2 tags
    "(producer-checked, no human audit)", Limitations bullet 1 and Reproducibility ("not producer≠verifier").
  - In publication_meta.json: the "description" and "notes" fields.
- **C2. Bibliography `sham`.** Change it to: I. Shammass, S. Rinott, A. Berkovitz, R. Schley, J. Steinhauer, *The
  phonon dispersion relation of a Bose-Einstein condensate*, arXiv:1207.3440 (v2 read on alphaXiv). It currently
  reads "Y. Shammass et al.".
- **C3. Scope of the counterexample.** The abstract ("shows that the symmetry hypothesis cannot be dropped") and
  Step 9 should say "cannot be dropped from the halving step `excess_eq_half`". The Lean file proves A(ρ) ≠ f/2. It
  does **not** prove that the conclusion of `feynman_bijl_bound` fails. That the final bound also fails in this
  example (the only eigenvector overlapping ρψ = e₁ has λ = 1 > 1/2 = ħ²k²/(2mS)) is a correct hand computation,
  and should be tagged C.
- **C4. "Quoted verbatim".** Section 9 says the alphaXiv-read papers are "quoted verbatim" in `excerpts.json`. The
  prose is verbatim, but mathematics is transcribed linearly (± → +-, µ → mu, √ dropped), so a normalised
  character-level match fails for most fragments. Say "prose verbatim; mathematics transcribed linearly", as the
  `_note` in excerpts.json already does.

## Non-blocking notes

- **N1. Threshold sensitivity.** The strict-run endpoint Q = 5.129 is refuted by 0.0830 against Δ_ds = 0.082, and
  Q = 5.18 is undecided at 0.0774. So the "strict run 1.55–5.129", the region-row counts above 2.4 Å⁻¹ and the X-ray
  refuted count (32) move with the third decimal of a post hoc threshold. The roton result is robust (minimum
  margin 0.328 ≈ 4Δ_ds). One sentence would make this clear.
- **N2.** Mention Donnelly–Barenghi's own Q < 1 / Q > 1 dataset recommendation, and that the roton-region
  conclusion is unchanged under it.
- **N3. Ledger closure hygiene.** PH-C-0004 restates the numerical content of PH-X-0001 ("exceeding … from the roton
  region outward") without listing PH-X-0001 among its dependencies. The paper discloses this design in Section 8,
  and the comparison is checkable by hand (I did the peak point). Still, either cite the hand-checkable peak
  inequality inside the C row, or list the X dependency explicitly.
- **N4. rusty-SUNDIALS / LeanFlow.** The user asked for improvements "along the way". This lane made none, and it
  says so plainly (Section 4, Limitations, PH-C-0006). I found no P6 worktree in `git worktree list` of
  rusty-SUNDIALS, and the only LeanFlow worktree is `LeanFlow-wt-p1`. This is honest, but the parent session should
  record it as an unmet part of the request for this lane.
- **N5.** `results/.../P6/DATA.md` §2 prints ħc = 1.5687 meV Å. The correct value is 1.5685 (results.json and the
  paper both have 1.5685). This is a typo in the work note only.
- **N6.** The positive control's Hermitian ρ makes `hsym` trivial (see §1). A one-clause remark would suffice.
- **N7.** The Steinhauer bib note "journal reference not checked" can now say "confirmed as cited in Shammass et al.
  ref. [4]".
