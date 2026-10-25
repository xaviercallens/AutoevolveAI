# Stage 4 independent audit: H2 / ar_yukawa_crystal

Date: 2026-10-25. The auditor is a separate AI agent instance. It is not the producer of the Lean files, the numerics or
the paper, and not the paper-stage verifier of `YukawaMix.lean`. This is an AI audit. It is not a human
statement-adequacy audit, so the ledger's `audit: null` / `LEDGER_UNAUDITED_TIER_A` flags stay correct.

**Verdict: ACCEPT_WITH_CORRECTIONS.** No blocking defect was found. Five wording or traceability corrections are listed
in section 8. None of them changes a Tier A statement or a reported number.

Scratch files for this audit are in `/tmp/h2stage4audit/`, outside the repo. Nothing in the repo or in the rusty
worktree was edited, except this file.

## 1. Lean: recompile, own `#print axioms`, own planted controls

The source files have the sha256 values the paper prints (checked with `sha256sum`):
- Yukawa.lean `a16397de…`
- YukawaMix.lean `6a940a7c…`
- YukawaControls.lean `ff7f11da…`
- YukawaMixControls.lean `028a3936…`
- VerifyYukawaMix.lean `f347d67d…`

Line counts are 197 and 233, as the paper states.

Each compile below used the pinned Lean 4.34.1 via `taskset -c 4-7 python3 scripts/certified_numerics/lean_pinned.py
compile FILE --json-out /tmp/h2stage4audit/…`, without `--olean`, so no shared olean was overwritten.

| file (auditor copy or original) | rc | s | result |
|---|---|---|---|
| `/tmp/h2stage4audit/S4YukawaCopy.lean` (byte copy of Yukawa.lean) | 0 | 22.0 | all 8 theorems `[propext, Classical.choice, Quot.sound]` |
| `/tmp/h2stage4audit/S4YukawaMixCopy.lean` (byte copy of YukawaMix.lean) | 0 | 22.0 | all 16 theorems `[propext, Classical.choice, Quot.sound]` |
| `formal_cert/Autoresearch/YukawaControls.lean` | 0 | 18.7 | `ctl_sorry` → `[sorryAx]`; `ctl_axiom` → `[AutoresearchYukawaControls.ctl_cheat]`; claimed theorems allowlist only |
| `formal_cert/Autoresearch/YukawaMixControls.lean` | 0 | 20.2 | `ctl_sorry` → `[sorryAx]`; `ctl_axiom` → `[…ctl_cheat]`; `pos_two_length`, `pos_mix_rho3_finite`, `pos_yukawa_rho2` allowlist only |
| `/tmp/h2stage4audit/S4AuditH2.lean` (auditor's own file, imports `Autoresearch.YukawaMix`) | 0 | 21.7 | see below |

The auditor's own file contains the following, with verbatim kernel output:
- **Planted sorry.** `planted_sorry : AdmissiblePotential (c 2) := sorry` reports
  `[propext, sorryAx, Classical.choice, Quot.sound]`. Its downstream use `planted_sorry_use : False` (via
  `c_not_admissible`) reports the same, so `sorryAx` propagates and is caught.
- **Planted axiom.** `axiom planted_ax : ∀ κ, AdmissiblePotential (g (-κ))` is used by `planted_ax_use`, which reports
  `[propext, Classical.choice, Quot.sound, S4AuditH2.planted_ax]`, so the axiom is caught.
- **Attained minimum is finite.** The new theorem `attained_k1 : latticeEnergy (g 1) = energy (g 1) A` (upstream's
  second conjunct, with `A_lf`, `A_d1`) and `energyA_finite_k1 : energy (g 1) A < ⊤` both report the allowlist only.
  So at κ = 1 the bound in `triangular_yukawa_optimal` is a finite value that A attains. It is not `⊤ ≤ ⊤`.
- **Further probes.** All of these compiled:
  - a re-stated density-one statement, closed by `triangular_yukawa_optimal`;
  - singleton mixture = `g κ` (`simp`);
  - a concrete `g_rescale` instance;
  - `signedMix (1/4) = 2 e^{-1/2} - 4 e^{-1}`, checking the human-proof arithmetic of Step 9b.
- **Upstream and prior-work footprints.** The following report `[propext, Classical.choice, Quot.sound]`:
  `OAI.AtomicTriangular.universal_energy_minimum`, `TriangularDensity.universal_any_density`,
  `triangular_optimal_any_density`, `TriangularRiesz.riesz_admissible` and `latticeEnergy_riesz_lt_top`.

The auditor grepped the two claimed files for forbidden tokens, excluding the `#print axioms` lines at the end of each
file. The grep found none of `sorry`, `admit`, `axiom `, `native_decide`, `implemented_by`, `extern`, `unsafe`,
`opaque`. Planted controls exist only in the `*Controls.lean`
files.

Olean freshness:
- `Yukawa.olean` (10:45) and `YukawaMix.olean` (10:55) are newer than their sources (10:26, 10:54).
- `Triangular/Riesz.olean` was rebuilt on 10-25 while `AnyDensity.olean` dates from 10-10. The Triangular sources have
  been unchanged since 10-10 (git log 63b24aa), so this is a rebuild from the same source.
- The byte-copy recompiles above check the claimed proofs from source either way.

Elenchus `tools/elenchus_check.py --json` on the two claimed files returns only `COMPILE_ERROR` (unknown module prefix
`Triangular` / `Autoresearch`). Its rc2 toolchain cannot see the pinned 4.34.1 stack. So the source-level vacuity scan
gives no usable result, as the paper's limitation (9) already says. The kernel footprint checks above replace it.

## 2. Statement adequacy (adversarial)

- `g κ t = exp(-κ√t)/√t`, and the definitions are upstream's. This was confirmed earlier (`verification.md`,
  `verification_mix.md`). The auditor's upstream read agrees:
  - `AdmissiblePotential` is C^∞ on (0,∞), nonnegative there, with (-1)^r g^(r) ≥ 0;
  - `energy` is the liminf of the ordered-pair disk average;
  - `latticeEnergy` is ∑' over A∖0.
- κ > 0 is needed twice: for the sign in `phi_sign` and for finiteness in `g_le`. At κ = 0, `g = riesz 1`, whose
  lattice sum diverges.
- Every-density form. `yukawa_any_density` bounds `latticeEnergy (g κ (ρ⁻¹·))` by `energy (g κ) C`.
  `latticeEnergy_yukawa_rho_lt_top` makes that bound finite, and D2's `attained` identifies it with the energy of
  ρ^{-1/2}A. So no case in the every-density statement is `⊤ ≤ ⊤`, and the same holds for the mixture versions
  (`latticeEnergy_yukawaMix_rho_lt_top`).
- An empty Finset or all-zero weights give the zero potential. There the theorem is true and trivial. This is not an
  overclaim, but "every finite mixture" includes this degenerate case.
- Scope of the negative controls. `signedMix_not_admissible` and `c_not_admissible` show that the *admissibility
  hypothesis* fails for those potentials. They do not show that triangular optimality *fails* for `g₁ - 2g₂` or for
  `e^{-κ√t} cos t`. See correction C1.

## 3. Human proof (Section 3), step by step

Every step was checked and is correct:
- **Step 1.** Derivative formula for t^{-s/2}.
- **Step 2.** Leibniz sign lemma, with the split (-1)^n = (-1)^i (-1)^{n-i}.
- **Step 3.** φ' = -(κ/2) t^{-1/2} φ on (0,∞). The strong induction uses the signs of φ only up to order n, which
  matches `phi_sign`.
- **Step 4.** Restriction to (0,∞) and the junk value g(0) = 0.
- **Step 6.** e^x ≥ x²/2 gives g ≤ (2/κ²) t^{-3/2}. The shell count is O(k).
- **Step 7.** The cone property.
- **Step 8.** The rescaling identity √ρ g_{κ/√ρ}.
- **Step 9b.** 2e^{-1/2} - 4e^{-1} = 2e^{-1}(e^{1/2} - 2) < 0. The value is -0.25845644526, from `fig_signs.json`,
  which equals the closed form.

Two expository gaps, both non-blocking:
- **Step 6.** The cells of the points in a shell k ≤ |a| < k+1 lie in the shell *enlarged by the cell circumradius δ*,
  not in the shell itself. The bound is still O(k).
- **Step 8.** The proof skips one step: energy(h(·/ρ), √ρ C) = energy(h, C), because pairwise distances scale and
  disk radii rescale inside the liminf. D2's `energy_smul` covers this in Lean.

## 4. Tiers and overclaim

- Conditionality on upstream `universal_energy_minimum` (AI-generated, Comparator-accepted, not peer reviewed) is stated
  in several places: abstract, Section 2, Section 4, Limitations (1), publication_meta and every YK-A row.
- Tier X is never used as evidence:
  - the ledger has no A or C row that depends on an X row;
  - the paper says "consistent with … not evidence" in several places.
- Novelty wording is restrained: "the mathematics is classical; only the kernel-checked corollaries are new". No
  breakthrough language.
- Precision issues (no false claims):
  - The abstract (iv), Step 9 heading, ledger rows YK-A-0007/0011 and publication_meta say "the sign condition …
    cannot be dropped" or "the hypotheses matter". See C1.
  - "None fall below the exact triangular energy" uses `below_exact_floor = exact_gap < 0` with zero tolerance
    (`scripts/exact_figures.py:81`). One stage, κ=1 `uniform_00` anneal_quench, sits at `exact_gap = 0.0`. That is
    within f64 noise: the perfect lattice in the box differs from the lattice sum by -2.2e-16. For that row the
    outcome comes from rounding, not from the physics. See C2.

## 5. Numbers trace to result files; spot re-run

- `gen_numbers.py` builds every macro from `data/*.json[l]`, `figures/fig_signs.json`, `H2/contribution/*.json` and the
  re-run Elenchus gate.
- The auditor rechecked the following against the sources. All match:
  - lattice energies, erratum differences, gaps and gap changes;
  - tail bounds: max(tri, square) = 5.59e-17 and 1.2e-16;
  - box differences and the self-image term 5.16e-9;
  - saddle modes 64 and 72, and the after-relax gaps;
  - mpmath maxima 1.661e-16 and 5.18e-29;
  - relaxation counts: 24 stages, 24 reproduce (max |published - rerun| = 4.4e-16 < 1e-13), 24 converge, 0 below,
    0 with negative modes;
  - MaxGapCh 5.3e-7 and 3.0e-10, MinGap 4.584e-4. The ratio 4.584e-4 / 5.3e-7 ≈ 865 supports "about 860 times";
  - OC20 revision, sha, size and license;
  - ledger counts: 24 claims (11 A, 4 L, 3 C, 6 X), exit 1, 0 blocks, 11 flags. Exit 1 here reflects the 11 flags
    only.
- `data/NUMERICS.md` is byte-identical to `H2/contribution/NUMERICS.md`.
- Spot re-run (about 7 s):
  `taskset -c 4-7 .venv/bin/python -I …/qf-yukawa-crystal/scripts/mpmath_lattice_control.py <crate> /tmp/h2stage4audit/mpmath_rerun.json`.
  Every printed value is identical to `data/mpmath_control.json`, including mp_direct, direct-Ewald, abs_diff_rust,
  the published-sf differences and positive/negative control pass = true.
- Code review of `src/exact.rs` (read-only):
  - The Voronoi tail bound derivation is correct, both in the doc comment and in the code `(π/A)(1+δ/s0)e^{-κ s0}/κ`,
    s0 = R - 2δ.
  - The Ewald identity `e^{-κr}/r = (2/√π)∫₀^∞ e^{-r²s²-κ²/(4s²)} ds` is correct.
  - The relaxations are compared against `e_tri_exact`, the partial lattice sum (`main.rs:810`).
- Ledger row YK-X-0006 says "g = g_1, orders 0..8". `numeric_gate_mix.json` covers orders 0..8 for the mixtures, while
  `fig_signs.json` covers g_1 for orders 0..6 only. See C4.
- Not re-run:
  - `cargo test` for the crate. The session's isolation guard refused the command. The paper's "24 passed, 0 failed,
    1 ignored" therefore rests on the producer's `check_crate.sh` output.
  - The exact relaxations, which take minutes to 25 min each.

## 6. Citations

- **CKMRV.** Verified with alphaXiv (arXiv:1902.05438v3): authors, title, Ann. Math. 196 (2022). The quoted Definition
  1.3 (p. 6), the lattice p-energy without a 1/2 (p. 3: "we include each pair of points twice") and footnote 2 (p. 7)
  appear verbatim in substance, matching the ledger evidence blobs.
- **OC20.** Verified with alphaXiv (arXiv:2010.09990, Chanussot et al., "The Open Catalyst 2020 (OC20) Dataset and
  Community Challenges").
- **Upstream scope remark (YK-L-0003).** Quoted from openai/math commit fd4aeeb2 with an extraction sha. This was not
  re-fetched.
- **Own Zenodo DOIs.** 23285631 (D1/D2), 23293429 (uo2 v2) and 23295142 (textbook) are consistent with the project
  record. They were not re-resolved online.
- **`citation_check.py`.** Not applicable as designed. It accepts only kind ∈ {theorem, lemma, proposition, corollary},
  while the L rows cite a definition, a remark and a footnote, so it would refuse them on kind. The auditor's alphaXiv
  read is the substitute check. See C5.
- **Vacancy remark.** In the physics paragraph, `\cite{oai}` is attached to "upstream identifies the minimum value,
  not all minimisers". That clause is correctly sourced (YK-L-0003). The clause after the semicolon, "the lattice with
  a vacancy has the same energy", has no citation. A verified source is CKMRV p. 8 ("removing a single particle
  changes neither the density nor the energy"); the uo2 non-uniqueness theorem is another. See C3.

## 7. Dataset provenance, license, publication_meta

- **Local shard.** The auditor ran `sha256sum` on the local OC20 shard and got `9e4249ba…e748b`.
- **Hub check.** The auditor queried the Hub independently (`/tmp/h2stage4audit/hub_check.py`, unauthenticated). At
  revision `6a1dfef12aec878b4cda99edd54b16a6a254e135`, `co/co_10.parquet` has size 142986687 and LFS sha256
  `9e4249ba…e748b`, and the license is `cc-by-4.0`.
- **Dataset card.** The card, downloaded to /tmp, gives DOI 10.60732/b4005525 and the OC20 authors. That matches the
  bibliography. The card also gives the journal version, doi:10.1021/acscatal.0c04525, which the paper could add.
- **Download date.** The paper says "original download date is unknown". The local file's mtime, 2026-10-10 20:04
  UTC, gives at least a latest possible date.
- **Hub search.** The search hits and their licenses match `inspect.json` and `hub_search.json`:
  `YangyangTan/yukawa-2d-diffusion` is MIT, and `VIJAYALAKSHMI10/Colloidal_model` has no license. Only metadata was
  stored (80 KB under hf-data). The Tier C absence-by-search wording is correct.
- **publication_meta.json.** Title, version, numbers (24 claims, 1.77e-2, -2.2e-6, 24 stages, 1.7e-16, revision
  6a1dfef1, exit 1 / 0 / 11) and commit SHAs agree with the paper and the result files. The related identifiers
  resolve to the cited works. The fields match the earlier `publication_meta_v2.json` style. The "cannot be dropped"
  bullet inherits C1.
- **Commit state.** The rusty worktree has 2 local commits on origin/main 47ef5044 (cc5a8aed code, 7f2a45c3 results),
  not pushed, as stated. The Lean files in AutoevolveAI are uncommitted (limitation 8). They should be committed before
  any Zenodo upload so that the cited sha256 values are reproducible from git.

## 8. Corrections (non-blocking)

- **C1 (scope clarification, not a false claim).** "The sign condition on the weights cannot be dropped" is
  literally true of `yukawaMix_admissible`: `signedMix` is a counterexample to the lemma once `hw` is removed. A reader
  may still take it to mean that the optimality conclusion fails for signed mixtures, and nothing here shows that.
  Suggested wording for abstract (iv), Step 9, YK-A-0007/0011 and publication_meta: "the admissibility lemma needs the
  sign condition: g₁ - 2g₂ is not admissible, so the theorem does not apply to it".
- **C3.** The vacancy clause in Section 5 has no citation. Add CKMRV p. 8 or the uo2 non-uniqueness theorem. The
  existing `\cite{oai}` on the preceding clause is correct.
- **C2.** For the relaxation outcome, say "none below the exact triangular energy beyond f64 resolution". Also note
  that κ=1 `uniform_00` anneal_quench is at gap 0 (the perfect lattice).
- **C4.** Make YK-X-0006 match the files: g_1 orders 0..6 (fig_signs); mixtures orders 0..8 (numeric_gate_mix).
- **C5.** Say in the paper or the ledger that the L rows cite a definition, a remark and a footnote, outside
  `citation_check.py`'s theorem-only intake, and that they were checked against the alphaXiv full text instead.
  Optionally:
  - add the enlarged-shell remark to Step 6 and the energy-rescaling step to Step 8;
  - give the shard mtime;
  - commit the Lean files before publishing.
