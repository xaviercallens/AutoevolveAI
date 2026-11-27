# M2 audit: exact Born-stability audit of the JARVIS-DFT elastic tensors

Auditor: Claude (Opus tier), independent of the producer (producer != verifier). Date 2026-10-31.
Auditor code and outputs: `/tmp/m2audit/code/` and `/tmp/m2audit/out/` (scratch, not tracked). Heavy work ran on cores 4,5 only.
Subject: `RESULT.md`, `result.json`, `prereg_M2.json`, `code/`, `data/`, `logs/`, and `formal_cert/Programmes/BornM2/`.

**Verdict: ACCEPT_WITH_CORRECTIONS.**

- Every headline exact count reproduces exactly with a different algorithm. A per-jid comparison over all 34,323 entries
  and 10 fields found 0 mismatches.
- All 11,481 witnesses are valid.
- The Lean files recompile, use only whitelisted axioms and replay under leanchecker. The tampered files fail. The
  matrices match the dataset by jid.
- The corrections below concern the robustness numbers (now settled exactly), one Tier X context item (`ehull`) that
  should be dropped, wording, and provenance.

## 1. Inputs and integrity

- **Dataset hashes.**
  - The dataset json has sha256 `9dacb55ac8371c7c2bf0332933b55c98e9cca6201e92eb9d6fcd03aab0975907`, which matches.
  - The zip's md5 is `c3179161ef0d029cf1fa70da463aac6e`. This equals the `computed_md5` that the figshare API
    reports for `jdft_3d-9-24-2025.json.zip` (article 6815699, version 11, DOI 10.6084/m9.figshare.6815699.v11). So
    no re-download was needed.
- **Other hashes.**
  - `prereg_M2.json` sha256 is `2c3127f9…b5d0fb` and matches.
  - `per_entry.jsonl` sha256 is `56f1bc54…2e8e`, which matches `result.json`.
  - All 5 Lean files match their sha256 in `result.json`.
- **Licence.** The figshare API (fetched by the auditor 2026-10-31) gives `license: CC BY 4.0`
  (https://creativecommons.org/licenses/by/4.0/). The RESULT statement is correct.
- **Bulk content.**
  - No dataset file and no per-entry table is tracked. `git log --all` over `*jdft*`, `*per_entry*` and
    `*m2_thirdparty*` is empty.
  - Tracked files hold at most 22 dataset tensors: 18 in `Witnesses.lean` and 4 in `data/f1_inspect.json`. That is
    acceptable under CC BY, but those two files carry no attribution line (correction C9).
- **Prereg timing.**
  - `prereg_M2.json` mtime is 16:22:52Z. It therefore predates the zip download (16:23:00Z) and all code and logs
    (16:24 to 16:37).
  - However, its internal field says `"written_utc": "2026-10-31T16:30Z"`, which is later than the controls and
    dataset logs (16:25 to 16:29). The stamp is wrong, not the order (correction C7).
  - The prereg was committed together with the results (051f87d), so git does not show the order. Only the mtimes do.

## 2. Literature and conventions (re-derived)

- **Criterion.** Mouhat & Coudert 2014 (arXiv 1410.0065, on disk; PRB 90, 224104) state that an unstressed crystal
  is elastically stable iff the quadratic form E = ½V₀ Σ C_ij ε_i ε_j is positive for all ε ≠ 0. Equivalently, the
  6×6 C is positive definite (all eigenvalues > 0, or all leading principal minors > 0 by Sylvester).
  - Their Eq. 20 shows that under load the relevant matrix is B ≠ C. The criterion is therefore the zero-stress one.
  - Born & Huang (1954) is cited by MC for this. The auditor did not re-read the book itself.
- **Symmetrisation.** Only the symmetric part S = (C + Cᵀ)/2 enters xᵀCx, so testing S is the right energy-form
  reading.
- **Ordering and scaling.**
  - PD is invariant under simultaneous permutation P S Pᵀ and under positive diagonal congruence D S D. That covers
    Voigt vs Mandel and engineering vs tensor shear strain.
  - So the VASP ordering (xx, yy, zz, xy, yz, zx) versus Voigt (xx, yy, zz, yz, xz, xy) cannot change any full-tensor
    PD verdict. It only matters for the closed-form class conditions.
  - The producer's `VASP_TO_VOIGT = [0,1,2,4,5,3]` is correct.
- **Auditor's independent order checks.**
  - Tetragonal-I entries (non-null, n = 10,343): stored idx4 == idx5 exactly in 9,596, against idx3 == idx4 in 35.
    So idx4 and idx5 are yz and zx (C44 = C55) and idx3 is xy (C66). This confirms the VASP order.
  - With the identity map (wrongly treating storage as Voigt), class-vs-full disagreements rise from 555 to 1,046
    (1,035 + 11).
  - Choudhary et al. 2018 (arXiv 1804.01033) Table S3 lists "C44-DFT" for the hexagonal rows: ZnO 39.5, ZnS 31.4,
    MoS₂ 78.7. Each equals (C11 − C12)/2, which is stored index 3 (xy, i.e. C66). This again shows the storage is
    VASP-ordered. It is a neutral side note, not an M2 claim.
  - Published-number positive control: the stored JVASP-91 (C), 1002 (Si), 890 (Ge), 1174 (GaAs) and 1195 (ZnO)
    reproduce Table S3 to the printed digits. All are exact PD and Rohn-robust PD.
  - That match also confirms the stored units are GPa, the units of the published table.
- **Footnote 26.** C11 = 1/2, C22 = C33 = 1, C12 = −1, C13 = C23 = 0. The values are confirmed in `mc.txt`. Eq. 19
  is confirmed as Wu et al. (PRB 76, 054115, 2007).
- **Class formulae and Laue mapping.** The formulae in `born_exact.py` match MC Eqs. 6, 9, 11, 13, 15 and 18. The
  Laue mapping from space-group number is correct (II: 75–88 and 143–148; I: 89–142 and 149–167).
- **Null and 'na'.**
  - 59,400 records carry the string "na". 179 tensors contain NaN or ±Infinity; these are the only non-Decimal tokens
    under `parse_float=Decimal`.
  - No entry is a JSON integer literal. Every finite literal's text equals the shortest repr: 0 value differences and
    0 place-count differences over 1,235,628 entries. So the producer's `repr(float)` reading equals the literal-text
    reading.
- **Null threshold.** There is a clean gap: the largest max|entry| below 1e-6 is 6.8e-12 and the smallest above is
  0.333. The 1e-6 cut is not arbitrary in effect.

## 3. Independent exact classification (all 34,323 entries)

- **Method.** This is own code, not derived from `born_exact.py`:
  - Read the literal decimal text as exact rationals and symmetrise.
  - Decide PD by strict sign alternation of the exact characteristic polynomial (Faddeev–LeVerrier over Fractions).
    This is an iff because S is symmetric and so real-rooted.
  - Compute leading minors as charpoly constant terms to locate the first non-positive minor and the boundary
    (minor exactly 0).
- **Controls.** All 14 PASS (`/tmp/m2audit/out/controls.log`, produced by `/tmp/m2audit/code/controls_test.py`):
  - diamond, Cu PD;
  - C11 < C12, C44 < 0, C11 = C12 and footnote 26 NOT PD;
  - an exact det check;
  - charpoly == elimination == numpy on 3,000 random symmetric rational matrices;
  - the Rohn robust / ambiguous / near-boundary cases;
  - the MC cubic conditions.
- **Per-jid diff against `per_entry.jsonl`.** 0 mismatches on each of `pd_exact`, boundary (`pivot_nonpos`),
  `symmetric`, `linear_pass`, `born_class`, F0, F1, F2, `interval` (the auditor's re-implementation of the
  Frobenius rule) and `cls`.
- **Counts reproduced exactly:**
  - exact PD 22,842 and NOT PD 11,481 (33.45%), boundary 204;
  - null 234, all NOT PD; excluding null, 11,247 of 34,089 (32.99%);
  - linear pass 23,184, linear-pass but NOT PD 342 (328 robust), linear-fail but PD 0, and the per-class split;
  - class-vs-full 555 of 30,203 (544 + 11);
  - non-symmetric 922, of which 7 are triangle-dependent;
  - 874 over-precise, 12 zero-row, 18 with an entry > 1e4 GPa, minimum float eigenvalue −6.3e5.
- **Witnesses.** All 11,481 producer witnesses were re-checked on the auditor's own S. Each has x ≠ 0, xᵀSx ≤ 0, and
  xᵀSx equal to the stored `witness_xSx`, so 11,481 of 11,481 are valid. This supersedes the requested 500-sample.
- **Prereg "two implementations agree on every entry".** The prereg named sympy. The producer ran sympy on a
  14,615-entry subset but ran Bareiss on all entries. The auditor's charpoly run on all 34,323 entries closes the
  remaining gap: three algorithms (LDLᵀ, Bareiss and charpoly) agree everywhere. The KEEP condition holds.

## 4. Rounding robustness

- **Producer's bounds (checked valid).**
  - ROBUST_PD rule: if S − bI is PD with b ≥ ‖Δ‖_F, then by Weyl and ‖E‖₂ ≤ ‖E‖_F ≤ ‖Δ‖_F every S + E is PD.
    `sqrt_upper` rounds up. The rule is valid.
  - ROBUST_NOT_PD rule: xᵀSx + |x|ᵀΔ|x| < 0. Valid.
  - The symmetrised half-widths Δ_ij = (h_ij + h_ji)/2 are the exact range of S_ij.
- **Auditor's exact test (Rohn 1994).** Every symmetric S + E with |E_ij| ≤ Δ_ij is PD iff the 32 matrices
  S − T_zΔT_z, for z ∈ {±1}⁶ with z₁ = 1, are all PD.
  - Sufficiency: with z = sign(x), xᵀ(S+E)x ≥ xᵀSx − |x|ᵀΔ|x| = xᵀ(S − T_zΔT_z)x.
  - Necessity: each S − T_zΔT_z is itself a member of the set.
  - On the NOT_PD side, an entry is "AMBIGUOUS_CERTIFIED" when some S + T_zΔT_z or S + diag(Δ) is PD. That
    certifies a PD member, so the verdict is truly rounding-dependent. "UNDECIDED" means neither certificate was
    found.

| Half-width rule | ROBUST_PD | ROBUST_NOT_PD | truly ambiguous (certified) | undecided |
|---|---|---|---|---|
| ±½ unit, last printed place (producer, Frobenius) | 22,708 | 11,244 | n/a | 371 |
| ±½ unit (auditor, Rohn exact for PD) | **22,809** | 11,244 | 55 (33 PD + 22 NOT_PD) | 215 (210 are null tensors) |
| floor 0.05 (producer, Frobenius) | 22,708 | 11,216 | n/a | 399 |
| floor 0.05 (auditor, Rohn) | **22,809** | 11,216 | 286 (33 PD + 253 NOT_PD) | 12 |

- Every producer ROBUST_PD entry is Rohn-ROBUST_PD, and every producer ROBUST_NOT_PD entry is auditor ROBUST_NOT_PD.
- Of the 134 "PD/undecided" entries, 101 are in fact robustly PD and 33 are truly ambiguous.
- Excluding the null tensors under ±½ unit: ROBUST_PD 22,809, ROBUST_NOT_PD 11,225, ambiguous 50, undecided 5.

## 5. Float pipelines (Tier X)

The auditor's own numpy `eigvalsh` on (A + Aᵀ)/2 confirms the producer's figures:
- F0: 0 disagreements.
- F1 (λ_min > −1e-8): 236 disagreements, all "stable" verdicts on NOT_PD tensors. 234 are the null tensors.
- F2 (relative −1e-6): 3 disagreements, of which 1 is null.

## 6. Crystal-system conditions

- The producer reports 544 class-stable but not PD and 11 class-unstable but PD. Both counts reproduce.
- **Decomposition of the 544 (auditor).** The 544 entries were split by block, checked in this order:
  - 184 have a Voigt diagonal entry ≤ 0. For example, the cubic formula reads only C44, while C55 or C66 is ≤ 0.
  - 299 have all diagonals > 0 but a non-PD normal 3×3 block.
  - 55 have a non-PD shear 3×3 block. These fail only through the shear off-diagonals.
  - 6 have both blocks PD but are not PD through normal–shear couplings.
- **Per class.**

  | Class | diagonal | normal | shear | coupling |
  |---|---|---|---|---|
  | cubic | 171 | 235 | 25 | 4 |
  | hexagonal | 3 | 11 | 3 | 1 |
  | orthorhombic | 0 | **0** | 3 | 1 |
  | tetragonal I | 4 | 51 | 22 | 0 |
  | trigonal I | 6 | 2 | 2 | 0 |

  Orthorhombic contributes 0 to the normal-block group, as expected: its formula reads the whole normal block.
- **What the split shows.** 483 of the 544 (184 + 299) come from stored tensors that violate the class equalities
  the formula assumes (C11 = C22 = C33, C44 = C55 = C66, …). The formula reads only the representative entries.
- The other 61 involve off-diagonal couplings. For cubic, hexagonal, tetragonal and orthorhombic these are mostly
  outside the class zero pattern.
- Frame orientation is not the main reason. See correction C3.

## 7. Lean (pinned Lean 4.34.1 + Mathlib d13f23b7, same toolchain as `lean_pinned.py`)

- **Recompile.** Byte-identical copies were compiled under `/tmp/m2audit/lean` as `BornM2Audit.*`, with oleans in
  `/tmp/m2audit/olean`, so nothing was written into the repo.
  - Probe: rc 0, 2 theorems.
  - Witnesses: rc 0, 24 `#print axioms` lines.
  - Every theorem depends on [propext, Classical.choice, Quot.sound] only.
  - Tamper1, Tamper2 and Tamper3 fail with rc 1. The errors are respectively the unsolved goal `2 ≤ 0`, linarith
    failure, and ring failure.
- **leanchecker replay.** `BornM2Audit.Probe` rc 0 (46.8 s), `BornM2Audit.Witnesses` rc 0 (43.0 s). The negative
  control `BornM2Audit.DoesNotExist` gives rc 1 ("Could not find any oleans").
- **Escape grep** over all 5 files (`sorry|admit|native_decide|axiom |set_option|#exit|skipKernelTC|addDecl|`
  `implemented_by|extern|unsafe|macro|elab|@[|opaque|decide`): no hits. The only import is `Mathlib.Tactic`; there is
  no `import Mathlib`.
- **Statement and data match.** The auditor parsed all 18 `![…]` matrices and 12 witnesses and compared them with
  its own symmetrised literal tensors via `data/lean_manifest.json`:
  - 18 of 18 matrices are identical, and the comment jid equals the manifest jid.
  - 12 of 12 witnesses give xᵀSx < 0. Each statement has the form `∃ x, x ≠ 0 ∧ quad S x ≤ 0`, with
    `quad = ∑ i, ∑ j, x i * C i j * x j`.
  - The 6 `pd_k` matrices are auditor-PD.
- **Scope.**
  - `pd_k` proves an identity `quad P x = Σ d_k (l_k·x)²` plus `0 < d_k`. PD (∀x ≠ 0, quad > 0) follows from L
    being unit lower-triangular, which is visible in the statement. That step is not a Lean theorem.
  - `dia_pd` (578·Σx² ≤ quad) does imply PD in Lean terms.
- **Not done by the auditor.**
  - The binding `anse/formal/lean_runner.py` gate (CLAUDE.md). The producer also used only `lean_pinned.py`.
  - A statement-lock entry. Until one exists, "Tier A" is premature (correction C6).

## 8. Interpretation and Tier X context

- **ICSD split.** The `icsd` field is a string, empty for none. The 11.3% vs 41.1% split (1,048 of 9,258 vs 10,199
  of 24,831) reproduces.
- **min_ir_mode.** The 40 of 480 vs 221 of 2,959 crosstab reproduces. It includes 2 null tensors; excluding them
  gives 40 of 478.
- **ehull: definition not verified.**
  - In this file, `ehull` has median 1.55 and 90th percentile 3.62. ICSD-linked entries have median 1.46, and 7,867
    of their 9,258 values exceed 0.1.
  - Ground-state spot checks are mixed: Si 0.0047, Ge 0.0, ZnO 0, diamond 0.1055, GaAs 0.4579.
  - The auditor could not interpret this distribution as an energy above hull in eV/atom.
  - The bins (30.3% vs 33.0%) should therefore be withdrawn (correction C2). This is not a statement about what the
    JARVIS field is.
- **What the percentage means.** It is the fraction of stored DFT tensors, under one stated reading, that are not PD.
  - Many entries are hypothetical or unrelaxed structures. Finite-difference tensors of dynamically unstable or
    residually stressed cells are expected to be non-PD at times.
  - The RESULT's "What this does not say" section correctly excludes lab instability and "JARVIS is wrong". Add the
    zero-stress caveat (C4).
- **Novelty.** The JARVIS elastic paper (arXiv 1804.01033) invites users to apply Born's criterion but reports no
  unstable fraction. "To our knowledge" stays appropriate.
- **Tone.** The dataset observations are factual and neutral. Adding the magnitude of the asymmetry is recommended
  (C5): 598 of the 922 non-symmetric tensors have max |C_ij − C_ji| > 1 GPa, the median is 19.5 GPa, and 232 of the
  922 are null tensors.

## 9. Corrections (old -> new)

**C1. RESULT, "Interval analysis" paragraph.** Append after "...not truly ambiguous.":

> Auditor (exact, Rohn 1994 vertex test, `AUDIT.md` §4): ROBUST_PD 22,809; ROBUST_NOT_PD 11,244; certified truly ambiguous 55 (33 nominally PD, 22 nominally NOT PD); undecided 215 (210 of them null tensors). With the 0.05 floor: 22,809 / 11,216 / 286 ambiguous / 12 undecided.

Mirror these numbers in `result.json` under `"interval_exact_rohn"`.

**C2. RESULT, Dataset observations, Tier X bullet.**
- Old: "and 30.3% for ehull <= 0.025 eV/atom versus 33.0% for ehull > 0.1."
- New: "(the `ehull` field is not used: its definition was not verified, and the observed distribution (median 1.55,
  ICSD-linked median 1.46) could not be interpreted as an energy above hull, so these bins are withdrawn)."

**C3. RESULT, Crystal-system section.**
- Old: "Most are expected: the class formulae assume the idealised zero pattern and standard axes, which noisy
  Cartesian-frame DFT tensors need not have, so this is not an error in either method."
- New: "Most are expected: the class formulae read only representative entries (e.g. C11 for C22 and C33, C44 for C55
  and C66), and the stored tensors do not satisfy those class equalities exactly. Auditor split of the 544 by block: 184
  have a Voigt diagonal entry <= 0, 299 a non-PD normal 3x3 block, 55 a non-PD shear block, and 6 fail only through
  normal-shear couplings. So 483 are driven by violated class equalities, and 61 by off-diagonal couplings (mostly
  outside the class zero pattern). This is not an error in either method."

**C4. RESULT, "What this does not say".** After "...convergence all remain possible reasons." add:

> The criterion tested is the zero-stress Born criterion (Mouhat-Coudert Eq. 20 replaces C by B under load); residual stress in a computed cell changes the relevant matrix.

**C5. RESULT, Dataset observations, second bullet.**
- Old: "922 tensors are not exactly symmetric (for 7 of them the verdict depends on which triangle is mirrored)."
- New: "922 tensors are not exactly symmetric (232 of them null tensors; 598 have max |C_ij - C_ji| > 1 GPa, median
  19.5 GPa; for 7 the verdict depends on which triangle is mirrored)."

**C6. RESULT, Lean heading, and `result.json` `tiers.lean_sample_and_controls`.**
- Old: "Tier A only for the listed specific statements" / `"A (unaudited)"`.
- New: "kernel-checked, independently recompiled and leanchecker-replayed by the auditor (2026-10-31, `AUDIT.md`
  §7); Tier A once a statement-lock entry exists and the `lean_runner.py` gate is run".
- Also add: "`pd_k` proves the LDL^T identity and positive pivots; PD follows from unit lower-triangularity outside
  Lean."

**C7. RESULT, Deviations.** Add item 6:

> The prereg's internal `written_utc` (16:30Z) is wrong; file mtime 16:22:52Z precedes the dataset download (16:23:00Z) and all runs. The prereg was committed together with the results.

(The prereg file is not edited.)

**C8. RESULT, Controls and Files.**
- Problem: `logs/*.log` (controls.log, run_dataset.log, analysis2.log, final_summary.log) are `.gitignore`d (`*.log`)
  and so untracked, but RESULT cites `logs/controls.log` and `result.json` hashes them.
- Fix: either `git add -f` them, or change "`logs/controls.log`, 24 lines" to "`logs/controls.json`" (which is
  tracked) and mark the `.log` hashes as untracked.

**C9. `Witnesses.lean` header and `data/f1_inspect.json`.** Add an attribution line:

> Data: JARVIS-DFT dft_3d (Choudhary et al., npj Comput. Mater. 6, 173 (2020)), figshare 10.6084/m9.figshare.6815699, CC BY 4.0.

If `Witnesses.lean` is edited, recompute its hash in `result.json` and recompile.

**C10. RESULT, "What an independent auditor must redo".** Replace with:

> Done by the auditor on 2026-10-31 (`AUDIT.md`), except the `lean_runner.py` gate and a statement-lock entry.

## 10. What remains unverified

- The physical meaning of the JARVIS fields `ehull` and `min_ir_mode`, and the convergence state of individual
  calculations.
- Born & Huang (1954) was not re-read. The criterion is taken from MC 2014.
- The `lean_runner.py` gate and a statement lock. No Lean certificates exist beyond the 18 entries plus 2 controls,
  as the producer states.
- PARI/Sage were not needed: there was no disagreement to arbitrate. The auditor's third implementation is pure-Python
  charpoly.
- The producer's own `controls.py` was not re-run. The auditor ran its own controls.
