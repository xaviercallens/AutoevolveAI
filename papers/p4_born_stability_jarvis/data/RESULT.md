# M2: exact Born-stability audit of the JARVIS-DFT elastic tensors

Producer: Claude (Sonnet tier). Status: producer result, UNAUDITED (LEDGER_UNAUDITED_TIER_A flag applies to the Lean items). Date 2026-10-31.
Outcome by the preregistered rule (`prereg_M2.json`, sha256 `2c3127f9f3e779c423293e177c94c4671a9682161deecab7c9b12ff77bf5d0fb`): **KEEP** (all controls pass, whole dataset classified, two implementations agree, certified not-positive-definite fraction 33.4% >= 1%, Lean control certificates kernel-checked). See "Deviations" and "What this does not say".

## Scope and licence
- Data: JARVIS-DFT `dft_3d`, figshare article 6815699, file `jdft_3d-9-24-2025.json.zip` (sha256 of the unzipped json `9dacb55ac8371c7c2bf0332933b55c98e9cca6201e92eb9d6fcd03aab0975907`). Licence recorded before download from the figshare API: **CC BY 4.0**. Attribution: Choudhary et al., npj Comput. Mater. 6, 173 (2020), arXiv 2007.01831. The dataset stays outside the repo (`/home/callensxavier_gmail_com/m2_thirdparty/`); this directory holds code, counts and per-class summaries only, no per-entry table.
- 93,902 records; 59,400 have `elastic_tensor = "na"`; 34,502 carry a 6x6 list; 179 of these contain non-finite numbers and are excluded; **N = 34,323** tensors analysed.
- Reading (an interpretation, not a physical statement): every stored float is taken as the exact rational of its shortest decimal representation. Verdicts are for the energy form of S = (C + C^T)/2. A DFT tensor is a calculation, not "the material's" tensor.

## Controls (run and logged before any dataset number; `logs/controls.log`, 24 lines, all PASS)
Positive: Cu, Si, diamond cubic tensors (literature values) are PD in exact, Bareiss and float, cubic Born conditions agree, interval ROBUST_PD. Mouhat-Coudert 2014 footnote 26 (C11 = 1/2, C22 = C33 = 1, C12 = -1, C13 = C23 = 0; shear constants not given in the footnote, set to 1 here, labelled) passes the incorrect linear criterion, fails exact PD and the orthorhombic Born conditions, rational witness found, ROBUST_NOT_PD. Three known-unstable cubic tensors are NOT_PD. Negative: sign flips of C11 and C44 on each textbook crystal flip the verdict; symmetry-breaking detected, and a large one flips the verdict; singular tensor (C11 = C12) is NOT_PD and rounding-undecided; a tensor 0.1 GPa from the boundary is PD but undecided. Random cross-check: exact LDL^T vs integer Bareiss on 6,000 random rational matrices agree, plus sympy minors on 400. Also: Voigt/Kv/Gv read-sanity on the data (below) acts as a positive control for reading the dataset.

## Headline counts (Tier C: exact rational arithmetic on the stored decimals; not Lean-checked unless stated)
| Quantity | Count (N = 34,323) |
|---|---|
| exact PD | 22,842 |
| exact NOT PD (rational witness x with x^T S x <= 0 verified for every one) | **11,481 (33.45%)** |
| of which boundary (first pivot exactly 0) | 204 |
| numerically null tensors (max abs entry < 1e-6; all are NOT PD) | 234 |
| NOT PD excluding the 234 null tensors (N = 34,089) | 11,247 (32.99%) |
| LDL^T vs Bareiss disagreements | 0 |
| sympy leading-minor check on 14,615 entries (all NOT PD, all undecided, 3,000 random PD) | 0 mismatches (deviation: subset, not all) |

Interval analysis (each printed value within +-1/2 unit of its last printed place; exact sufficient tests): ROBUST_PD 22,708; ROBUST_NOT_PD 11,244; UNDECIDED_BY_BOUND 371 (237 nominally NOT PD, 134 nominally PD). The bounds are sufficient, not necessary, so "undecided" means not certified either way, not truly ambiguous. 33,399 tensors print every entry at 1 decimal; 874 tensors have an entry printed with more than 6 places (numerical noise, down to denormal numbers), where the +-1/2-unit rule gives absurdly small intervals. Sensitivity with half-width floored at 0.05 (half of the dominant 0.1 resolution): ROBUST_PD 22,708; ROBUST_NOT_PD 11,216; UNDECIDED 399 (Tier C, an addition to the prereg).

Q3, incorrect linear orthorhombic criterion (Wu et al., MC Eq. 19, applied to all entries regardless of class): 23,184 pass it; **342 (1.00% of N) pass it yet are exactly NOT PD** (328 of them robustly); 0 fail it while PD (consistent with necessity). By class (pass-linear-but-not-PD): cubic 87, tetragonal_I 63, trigonal_I 57, monoclinic 47, triclinic 41, hexagonal 29, orthorhombic 15, trigonal_II 3, tetragonal_II 0.

DFT-uncertainty context, exact test PD(S - theta*||S||_F I) among the 22,842 PD tensors: theta = 1%: 22,074; 2%: 21,224; 5%: 17,983; 10%: 10,703; 20%: 611. The thresholds are illustrative stand-ins (the dataset stores no uncertainty); they are not statements about JARVIS accuracy.

## Float pipelines versus exact (Tier X for the float verdicts)
numpy `eigvalsh(S).min() > 0`: 0 disagreements. With absolute tolerance -1e-8: 236 disagreements (all call a not-PD tensor stable); 234 of them are the numerically null tensors, 2 are not. With relative tolerance -1e-6*lambda_max: 3 disagreements (2 not null). So the disagreements are essentially "stable by tolerance" verdicts on null-like tensors, plus 2 near-singular tensors.

## Crystal-system conditions versus exact PD (Tier C, with an important frame caveat)
Mouhat-Coudert closed-form class conditions (cubic, hexagonal, tetragonal I/II, trigonal I/II, orthorhombic) evaluated on the stored entries (VASP order xx,yy,zz,xy,yz,zx mapped to Voigt; order confirmed on 2,659 hexagonal entries: median relative error of C_xy vs (C11-C12)/2 is 2e-4 against 0.41 for the other index) for 30,203 entries: 555 disagree with exact PD of the full tensor (544 class-stable but full tensor not PD; 11 class-unstable but PD). Most are expected: the class formulae assume the idealised zero pattern and standard axes, which noisy Cartesian-frame DFT tensors need not have, so this is not an error in either method. Monoclinic/triclinic reduce to the generic test, so no cross-check is reported for them.

## Dataset observations (factual, neutral; for the owner to decide whether to forward to the dataset authors)
- 59,400 of 93,902 records have `elastic_tensor = "na"`; 179 tensors contain NaN/inf.
- 234 stored tensors are numerically zero (entries 1e-14 down to 5e-324), 12 tensors have a literal zero row; 922 tensors are not exactly symmetric (for 7 of them the verdict depends on which triangle is mirrored).
- 18 tensors have an entry above 1e4 GPa; the smallest float eigenvalue reaches -6.3e5.
- Read-sanity: Voigt K and G recomputed from the tensor match the stored `bulk_modulus_kv` / `shear_modulus_gv` within 1% for 97.9% / 98.1% of entries (median relative error 3e-5).
- Tier X context only: among entries with `min_ir_mode`, a negative lowest IR mode is stored for 40 of 480 NOT-PD tensors (8.3%) versus 221 of 2,959 PD tensors (7.5%) (no association visible; meaning of the field not verified). NOT-PD fraction is 11.3% for entries with an ICSD id versus 41.1% without, and 30.3% for ehull <= 0.025 eV/atom versus 33.0% for ehull > 0.1. A large fraction of the dataset is hypothetical structures; we do not know the convergence state of individual calculations.

## Lean (Tier A only for the listed specific statements; `formal_cert/Programmes/BornM2/`, pinned Lean 4.34.1 via `scripts/certified_numerics/lean_pinned.py`)
- `Probe.lean`: footnote-26 witness `exists x != 0, x^T C x <= 0`; diamond-type tensor `578 * sum x_i^2 <= x^T C x`. Axioms: propext, Classical.choice, Quot.sound only.
- `Witnesses.lean`: 12 dataset NOT-PD witnesses (4 pass the linear criterion; cubic 2, hexagonal 2, tetragonal_I 2, orthorhombic 1, monoclinic 1; the deterministic sample is documented in `code/gen_lean.py`) and 6 randomly chosen ROBUST_PD entries with an LDL^T identity `x^T S x = sum d_k (l_k . x)^2` plus `d_k > 0` (unit lower-triangular L is syntactic). All compile, axioms within the whitelist, no `sorry`.
- Tampered certificates `Tamper1/2/3.lean` (wrong witness; lower bound 600 > 578; altered pivot) are REJECTED (rc 1). The Lean files state facts about the exact matrices written in them, which are the symmetrised stored decimals; matching them to the dataset is a Python/hash step (Tier C).
- Not done: Lean certificates for all 11,481 unstable entries and for a larger stable sample (prereg M2a asked for all unstable; the full-scale Lean pass was a stretch and is not claimed). Those 11,469 other witnesses are verified exactly in Python only.

## Deviations from the preregistration (logged)
1. sympy third implementation ran on a 14,615-entry subset, not all entries (Bareiss ran on all).
2. Added post hoc after seeing long-decimal entries: half-width-floor sensitivity, null-tensor exclusion counts, Kv/Gv sanity, ehull/ICSD/min_ir_mode context (Tier X), asymmetry-triangle test.
3. The prereg listed `numpy eigvalsh with tolerance` loosely; two tolerance conventions (F1, F2) were fixed in the prereg and used as written.
4. Lean limited to controls plus an 18-entry sample (the prereg called it a stretch).
5. `-I` isolated mode was not used for our own code (it drops the script directory); the downloaded JSON was only parsed with `json.load`.

## What this does not say
No claim that any material is synthesisable, stable or unstable in the laboratory; no claim that JARVIS-DFT is wrong. A tensor with a negative eigenvalue is a calculated tensor that is not positive definite; finite-difference noise, unrelaxed or hypothetical structures, magnetism and convergence all remain possible reasons. Novelty: to our knowledge no exact-rational Born audit of the whole JARVIS elastic dataset has been published; we did not search exhaustively.

## What an independent auditor must redo
Re-download `jdft_3d-9-24-2025.json.zip` and check the sha256; rerun `code/controls.py` then `code/run_dataset.py`, `analysis2.py`, `final_summary.py`; confirm the 11,481 count with a separate implementation (e.g. Sage or PARI, not our Fractions/Bareiss/sympy); check witnesses independently (x^T S x <= 0 for all); recompile the Lean files under the pinned toolchain and match the Lean matrices to the dataset entries by `jid` (`data/lean_manifest.json`); review the interval bounds (Frobenius sufficient test) and the null-tensor definition; check the Born-class mapping (space group -> Laue class, VASP-to-Voigt permutation).

## Files
`prereg_M2.json` (+ `.sha256`), `code/` (born_exact.py, controls.py, run_dataset.py, analysis2.py, final_summary.py, inspect_f1.py, gen_lean.py, make_result_json.py), `data/` (summary.json, analysis2.json, final_summary.json, f1_inspect.json, lean_manifest.json), `logs/`, `result.json` (sha256 of all files). Per-entry results `m2_thirdparty/per_entry.jsonl` are kept outside the repo (hash in result.json).
