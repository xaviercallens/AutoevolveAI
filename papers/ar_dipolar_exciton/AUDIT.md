# Stage-4 independent audit: lane H1 (ar_dipolar_exciton)

Auditor: an AI agent instance (Claude) separate from the producer, run 2026-10-25. It is not a human referee.
Scope: `main.tex`/`main.pdf`, `ledger/`, `publication_meta.json`, `data/`, `results/autoresearch/2026-10-25/H1/contribution/`,
`formal_cert/Autoresearch/DipolarExciton*.lean`, and the rusty-SUNDIALS worktree diff (`git diff origin/main` in
`/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h1`, read only).

**Verdict: ACCEPT_WITH_CORRECTIONS.** Nothing blocks publication. The corrections listed in section 8 are wording and
precision fixes.

Audit artifacts. These are new files; no existing file was edited.
- `formal_cert/Autoresearch/DipolarExcitonAuditH1Controls.lean`: the auditor's own probe file. It contains a planted
  `sorry` and a planted axiom, so it is **not** a claimed module. It carries the `*Controls.lean` suffix, following the
  planted-control rule.
- `papers/ar_dipolar_exciton/audit/audit_controls.json`, `recompile_multipolar_src.json`, `recompile_prior_src.json`:
  verbatim compile output.
- `papers/ar_dipolar_exciton/audit/gate_rerun.txt`: the auditor's own Elenchus gate run.
- `papers/ar_dipolar_exciton/audit/audit_epstein_check.py`: an independent numerical check that does not use Ewald
  summation.

## 1. Lean: recompiled by the auditor, own `#print axioms`, planted controls

The source hashes match the paper (`sha256sum`):
- `DipolarExciton.lean`: b85389a5…f27d
- `DipolarExcitonMultipolar.lean`: 7f52ea64…f98a
- `DipolarExcitonMultipolarControls.lean`: 1754e1a9…106d
- `Triangular/AnyDensity.lean`: 0a6d86ee…5168

`grep -c sorry` gives 0 on both claimed modules.

Each compile used `taskset -c 4-7 python3 scripts/certified_numerics/lean_pinned.py compile …`, with Lean 4.34.1 and
Mathlib `d13f23b7…` (the pinned lake-manifest rev was checked).

| run | what it re-elaborates | rc | time | axioms |
|---|---|---|---|---|
| `recompile_prior_src.json` | `DipolarExciton.lean` from source | 0 | 62.9 s | all 4 theorems: [propext, Classical.choice, Quot.sound] |
| `recompile_multipolar_src.json` | `DipolarExcitonMultipolar.lean` from source, no olean written | 0 | 56.9 s | all 10 printed theorems: [propext, Classical.choice, Quot.sound] |
| `audit_controls.json` | auditor probe file `DipolarExcitonAuditH1Controls.lean`, importing the built module | 0 | 19.6 s (final run; an earlier run under the old name took 55.2 s) | see below |

Results from the auditor's probe file:
- **Planted `audit_sorry : 2+2=5 := sorry`** gives `depends on axioms: [sorryAx]`. It is caught.
- **Planted `axiom audit_cheat : (0:ℝ) = 1`** used in `audit_axiom` gives
  `[propext, Classical.choice, DipolarAuditH1.audit_cheat, Quot.sound]`. It is caught.
- The file still exits with rc 0, which confirms the paper's point that the exit code is not the gate.
- All 16 claimed declarations re-printed by the auditor stay within the allowlist. These are the 4 prior-round
  theorems plus 12 from the new module: `shiftDiff_admissible`, `admissible_const_mul`, `g_eq_shiftDiff`,
  `dipolar_admissible_all`, `shiftDiff_neg_of_neg`, `shiftDiff_not_admissible_of_neg`, both `*_any_density`,
  `triangular_shiftDiff_optimal`, `g_scaled_le`, `latticeEnergy_dipolar_scaled_lt_top` and
  `energy_dipolar_any_density_lt_top`.
- **Definition fidelity.** I printed the upstream definitions (`#print`, plus the pinned source
  `OAI/Analysis/Triangular/Energy/Basic.lean` for `diskEnergy`):
  - `AdmissiblePotential g` = `ContDiffOn ℝ ⊤ g (Ioi 0) ∧ (∀ t>0, 0 ≤ g t) ∧ ∀ r t, 0<t → 0 ≤ (-1)^r iteratedDeriv r g t`.
    This is C^∞ (not analytic), nonnegative and completely monotone, which matches §Setting.
  - `energy g C` = `liminf_{R→∞} diskEnergy g C R`, where
    `diskEnergy = (diskCount C R)⁻¹ · Σ_{x ∈ diskPoints} Σ_{y ≠ x} ofReal (g ‖x−y‖²)`. This is the ordered-pair disk
    average with no ½, as in Petrache–Serfaty (1.1).
  - `latticeEnergy g` = `Σ'_{a ∈ A, a ≠ 0} ofReal (g ‖a‖²)`.
  - `LocallyFinite C` = every closed ball meets C in a finite set.
  - `DensityOne` and `DensityRho` are `Tendsto (diskCount C R / (π R²)) atTop (𝓝 ρ)`.

  These match the §Setting gloss. The normalization latticeEnergy(g_d) = 2d²·e_tri (DX-C-0006, e = ½Σ'U) follows.
  One feature is not mentioned in the paper: values pass through `ENNReal.ofReal`, so a negative g would be clipped to
  0. This is harmless here because admissibility forces g ≥ 0.
- The `#check` statements match Listings `prior`, `multi` and `density`. In particular:
  - `triangular_dipolar_optimal_any_density` needs `0 < d` and `0 < ρ`. Its conclusion is the conjunction of
    LocallyFinite, `DensityRho ρ` and energy ≤ for every locally finite `DensityRho ρ` configuration C.
  - `universal_energy_minimum` has the form the paper states.
  - `DensityRho ρ C` is `Tendsto (diskCount C R / (π R²)) atTop (𝓝 ρ)`, which is a faithful density definition.
- **Extra probe `audit_g_sqrt`** (axioms within the allowlist) proves the Step-1 identity
  `g d t = 2(1/√t − 1/√(t+d²))` for `t > 0` in one `simp` call. The paper files this identity at Tier C because the
  verifier's scratch file was deleted. It can move to Tier A if the lemma is added to a claimed module (for `r > 0`,
  `√(r²) = r` closes the r-form).

Producer ≠ verifier: the paper says the Multipolar module is "producer-checked only". After this audit it has been
re-elaborated from source by a separate AI agent, with the same axiom output. The status sentence (main.tex l.77–79,
§Limitations, publication_meta) can be updated. It is still not human-audited, and the 12 `LEDGER_UNAUDITED_TIER_A`
flags remain correct.

## 2. Numbers trace to files, plus an independent re-derivation

I traced the following `gen_numbers.tex` macros to `data/*.json(l)` and `data/run_table.md`. Some were recomputed
with python -I from `references.jsonl`, `summary.json` and `lattice_gaps.jsonl`:
- η and box checks: EtaRefs = 1.32e−13 (the paper's 1.3e−13 is correct; NUMERICS.md says "at most 1.5e−13", a
  producer-note slip, not in the paper); BoxCell = 2.55e−14; EtaGrid = 4.81e−13
- the 41-point grid: d̃ 0.01–3, e_tri(0.01) = 4.4462; square relative gap 1.584e−2 → 1.361e−3; honeycomb 9.53e−2 →
  8.75e−3. The minima are the endpoint values, so both gaps stay positive.
- meV values come from `summary.json` `physical_square_minus_tri_meV_eps1`: 0.0014, 0.0438 and 0.2226. See C3.

The rest:
- counts: 21 competitors = 12 quenches + 2 anneals + 2 incommensurate + 5 square+noise; 0 undercut; 3 of 12 quenches
  and 1 of 2 anneals reach the lattice; 7 quenches end defected
- extreme relative gaps: −2.3e−14 among competitors, −2.6e−14 including the positive controls, 2.6e−14 maximum |positive
  control|
- smallest gap above the lattice 1.54e−4; square+noise gaps 1.73e−3 to 4.77e−3; negative Hessian modes 64–72
- independent-check deviations: 8.5e−14, 1.9e−13, 1.9e−5, 3.14e−2
- HF spacings: 6.5827, 6.6151, 6.2371 Å, proxy 6.599 Å; d̃ = 0.0209, 0.0660, 0.1143
- Lean sha256 values, ledger counts (31 = 12 A + 4 L + 7 C + 8 X), gate result (0 blocking, 12 flags)

All of these match.

I re-ran the Elenchus ledger gate myself, without a pipe (`audit/gate_rerun.txt`): 12 `LEDGER_UNAUDITED_TIER_A` flags,
0 blocking lines, ledger.py exit code 1. This is identical to `ledger/gate_output.txt`.

I did not re-run the crate tests. The worktree-isolation guard of this session refused
`cargo test --manifest-path <rusty-wt>`. The 28 passed / 0 failed / 1 ignored figure traces to the producer's
`contribution/rerun_cargo_test_paper_stage.txt` only.

The rusty commit SHAs were read with `git rev-parse`: 4feb027e…, 17ea6bec…, 916fc88c…, 272a09e6…, on branch
`physics/ar-dipolar-exciton-2026-10-25`. The preregistration commit precedes the code commit.

**Independent numerics (Tier X).** Instead of re-running the Rust driver, which would write into the producer's
worktree, I re-derived the lattice energies by a different method that uses no Ewald sum
(`audit/audit_epstein_check.py`, mpmath at 30 digits). It expands U in d²/r² and uses the closed-form Epstein zeta
functions: triangular 6ζ(u)L(u,χ₋₃), square 4ζ(u)β(u).

| d̃ | e_tri: paper (Rust Ewald) | e_tri: audit (Epstein) | e_sq: paper | e_sq: audit |
|---|---|---|---|---|
| 0.0209 | 4.445599702966 | 4.445599702965 | 4.515977301801 | 4.515977301800 |
| 0.066 | 4.438685393575 | 4.438685393575 | 4.508522037703 | 4.508522037703 |
| 0.114 | 4.423567867904 | 4.423567867904 | 4.492234433068 | 4.492234433068 |
| 0.3 | 4.295977545078 | 4.295977545078 | 4.355436261238 | 4.355436261238 |

The two methods agree to about 1e−13 relative.

Controls for the audit check:
- **Positive:** closed-form Z_tri(5) = 4.7194917 and Z_sq(5) = 5.0902582, against brute-force sums of 4.7194917 and
  5.0902582, which differ by about 6e−8, the expected truncation tail.
- **Negative:** putting the square zeta in place of the triangular one gives 4.5085 at d̃ = 0.066 instead of 4.4387.

The paper says it did not compare its d̃ → 0 limit (4.4462 at d̃ = 0.01) with a closed form. The exact half Riesz-3
triangular sum at density one is **4.446373**, and the d̃ → 0 limit of e_sq/e_tri − 1 is 0.015842. Both are
consistent with the grid values 4.4462 and 1.58e−2.

**Physical gaps.** Using e²/4πε₀ = 1.43996 eV·nm, with the gap Δe evaluated at the physical d̃, I get 0.00140, 0.0438
and **0.2237** meV at n = 10¹¹, 10¹² and 3×10¹² cm⁻². `summary.json` shows how the paper's numbers were made:
- the physical d̃² (0.11430²) was multiplied by Δe taken at the simulated reference d̃ = 0.114 (`d_tilde_of_ref_used`)
- this gives 0.2226 meV, printed as 0.223

The difference is 0.5%. See C3.

## 3. Human proof: checked step by step

I re-derived every step.
- Step 1: four Coulomb pairs give 2/r − 2/√(r²+d²); the large-r expansion is d²/r³.
- Step 2: the falling factorial; induction is correct.
- Step 3: (−1)^r desc_r(−½) = ∏(½+k) > 0.
- Step 4: monotonicity of x^e for e ≤ 0.
- Step 5: the Bernstein formula holds, with Γ(½) = √π.
- Step 7: a² − b² = c·a²b² because a² = 1/t and b² = 1/(t+c); 2b² ≤ a² + ab follows from b ≤ a; dividing by a + b > 0
  gives a − b ≤ (c/2)t^{−3/2}.
- Step 8: density scaling by √ρ. Disk-average energies are invariant under rescaling radii. The identities
  g_d(t/ρ) = √ρ·g_{d√ρ}(t) and g_d(t/ρ) ≤ d²ρ^{3/2}t^{−3/2} both hold.
- Step 9: h_d(d²) = (1 − √2)/d < 0; and t = −2c gives t + c = −c ∈ (0, t).

The Ewald identity V = (4/√π)∫e^{−r²u²}(1−e^{−d²u²})du holds. So does its 2D Fourier kernel
4√π∫t⁻²e^{−G²/4t²}(1−e^{−d²t²})dt, which is finite at G = 0, so no background term is needed (dipolar_ewald.rs).

The normalization latticeEnergy(g_d) = 2d²e_tri holds with the paper's ½ convention.

I found no mathematical error.

## 4. Tiers and overclaim

- Conditionality on upstream `universal_energy_minimum` (AI-generated, not peer reviewed) and on definition fidelity
  is stated in the abstract, §Setting, §Lean, §Limitations and publication_meta. Petrache–Serfaty's "remains open in
  dimension 2" is stated correctly. Wording is restrained: "no breakthrough"; "novelty is small"; the literature search
  is called weak evidence.
- Tier X is kept as illustration only (§num, first sentence; ledger `claim_licence: false`).
- **⊤ ≤ ⊤:** non-vacuity is kernel-checked for g_d at density one (`latticeEnergy_dipolar_lt_top`) and at every
  density (`energy_dipolar_any_density_lt_top`). **It is not proved for the shiftDiff family** (DX-A-0009,
  `triangular_shiftDiff_optimal*`). At c = 0, shiftDiff is the zero function and the statement is trivially 0 ≤ E.
  The abstract sentence "We also prove that the optimal energy is finite" follows the family sentence, and the
  publication_meta bullet "finiteness … at every density" is unqualified. Both should say this is for g_d only. See C1.
- The planted controls live only in `*Controls.lean` and the auditor's probe file. Neither claimed module contains
  them.

## 5. Citations

I checked these against primary text through alphaXiv (`answer_pdf_queries`):
- **arXiv:1908.09714v3** (Petrache, Serfaty). Title is correct. Eq. (1.1) is the lower energy. The quoted sentence
  "Then Conjecture 1 was recently proved in dimensions 8 and 24 — it remains open in dimension 2" appears verbatim.
  The non-uniqueness under finite perturbations appears on p. 6.
- **arXiv:2001.03812v5** (J. Wang, … X.-Y. Zhu). The title and all 11 authors match. These are verbatim:
  - "n_Mott = 1.6-3x10^12 cm^-2" (p. 2)
  - "depth of the order of 10s-100 meV" (p. 4)
  - "n_t-g ~1-5x10^11 cm^-2" (p. 6)
  - "only exists in the narrow density range around 10^11 ~ 10^12 cm^-2" (p. 8)
  - h-BN encapsulation and 4 K (p. 2)
- **arXiv:2007.01831v2** (Choudhary et al., JARVIS). Title is correct. "we use vdW-DF-OptB88 consistently for all the
  3D, 2D, 1D and 0D materials … accurate predictions for lattice-parameters" (p. 14) is verbatim.
- Zenodo DOIs:
  - 23285631 (D2) and 23295142 (textbook) match the project records.
  - 23293429 matches `papers/universal_optimality_tiered/zenodo_doi_v2.txt`.
  - The ColabFit DOI 10.60732/e9e65ccd and the publication DOI 10.1038/s41524-020-00440-1 appear verbatim on the HF card.
- `citation_check.py` was not run, and that is correct. It accepts only theorem/lemma/proposition/corollary excerpts,
  and the L rows are prose. The paper says so.

## 6. Dataset provenance and license

- `co/co_0.parquet` sha256 recomputed: 9f6c21a2…510b, matching `hf_provenance.json`.
- The card front matter reads `license: unknown`, verbatim. "Original data link https://doi.org/10.6084/m9.figshare.6815699"
  is on the card. The paper correctly says the figshare license was not checked and that only derived numbers are
  reproduced.
- The JARVIS-2D set was used only for monolayer values, not for d.

- The file listing at that revision (`results/dipolar/hf_files.json` in the rusty worktree) shows `co/co_0.parquet` is
  the **only** configuration shard, plus `ds.parquet`. So the whole dataset was scanned, and "no WS₂ row passed" is a
  statement about the whole mirror. NUMERICS.md's "in this shard" is therefore not a limitation.
- The selection rule was "fixed before seeing the output". That is the producer's statement and cannot be verified
  after the fact.

## 7. publication_meta.json

The title, numbers, DOIs, SHAs, dataset revision and license all match the paper and the files. The schema is the same
as the published `universal_optimality_tiered/publication_meta_v2.json`.

Inaccuracies:
- "the new … module is producer-checked only". This is now outdated: an AI auditor has independently recompiled it.
- The unqualified finiteness bullet (C1).

## 8. Corrections

**Blocking:** none.

**Non-blocking:**
- **C1.** Non-vacuity applies to g_d only. Qualify the abstract sentence (main.tex l.57–58) and the publication_meta
  bullet: finiteness is proved for g_d (d > 0), not for the shiftDiff family. Optionally add a remark that at c = 0
  the family is identically zero.
- **C2.** Update the verification status. The Multipolar module was re-elaborated from source by an independent AI
  auditor (rc 0, axioms within the allowlist, planted sorry and axiom caught). Keep "no human audit".
- **C3.** "two to five orders of magnitude below the moiré depths" (l.295–296): with 0.223 meV against 10 meV, the low
  end is about 1.65 orders. Write "about 1.5 to 5 orders". Also, the meV values use Δe at the simulated d̃ (0.0209,
  0.066, 0.114) with the physical d̃² prefactor. Either say so, or evaluate Δe at d̃ = 0.1143, which gives 0.224 meV.
- **C4 (withdrawn).** My draft claimed that only one shard was scanned. `hf_files.json` shows co_0 is the only
  shard, so there is no correction to make.
- **C5.** Competitor count. The 2 incommensurate boxes and the 5 square+noise relaxations are designed negative
  controls, and they are bound to sit above triangular. Only 14 of the 21 "competitors" are open searches (12 quenches
  and 2 anneals). In addition, `anneal_01` and `uniform_04` (different seeds 601/901 and 504) end in the same state:
  e = 4.4393674557326 in both, ψ₆ = 0.998112. The paper's "two zero-defect states" is consistent with this, but the
  count of independent outcomes is smaller than 21 suggests. Tier X is unaffected.
- **C6.** The two killed first attempts at d̃ = 0.0209 and d̃ = 1 are disclosed in NUMERICS.md but not in the paper. Add
  one sentence. Their completed jobs were never printed (the reason for fix 916fc88), so this is not selective
  reporting.
- **C7.** Deviation from the preregistration: the preregistered "reported_potential" was the image sum plus tail; the
  paper reports Ewald energies. The change is justified by the measured non-monotone residual and is explained in
  §num. Label it explicitly as a deviation from DIP-TRI-1.
- **C8 (optional upgrade).** Move `audit_g_sqrt`, or an r-form of it, into a claimed module so that Step 1's algebraic
  identity becomes Tier A. The physics reading stays Tier C.
