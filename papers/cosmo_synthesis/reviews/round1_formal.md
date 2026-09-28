# Referee report, round 1 of 3 — formal-methods lens

Paper: `papers/cosmo_synthesis/cosmo_synthesis.tex` (draft of 2026-09-27, 17 pp.)
Referee: Claude agent (model referee; not a person). Date: 2026-09-27.
Scope of this lens: independent recompilation of the four Lean modules, faithfulness and
non-vacuity of every theorem in Appendix A, whether the text overstates what the kernel proves,
and the Elenchus ledger tier logic (gate re-run plus my own mutation controls).

Recommendation: **major revision**. No blocking issue: every kernel claim in the paper
reproduces, and the ledger exit codes reproduce. Four issues are major because they concern
provenance of numbers the paper prints, an overstatement of theorem scope, an audit binding
that violates the project's own rule, and an undisclosed limitation of the ledger gate.

## 1. What I re-ran (all real tool output)

### 1.1 Lean, pinned build command (env 1)

Script: `results/cosmo_synthesis/referee_round1_formal_lean_recheck.py`, sequential
`cd /home/callensxavier_gmail_com/AutoevolveAI/formal && timeout 1800 lake env lean <abs path>`
on the four worktree files. Output: `results/cosmo_synthesis/referee_round1_formal_lean_recheck.json`.

| File | sha256 (matches appendix) | theorems | `#print axioms` outputs | rc | axiom union | wall [s] |
|---|---|---|---|---|---|---|
| `BAO_FlatLCDM.lean` | `c85c1e8a…d702` yes | 3 | 3 | 0 | {propext, Classical.choice, Quot.sound} | 11.5 |
| `DESI_DR2_wCDM.lean` | `3b451bd5…5adc` yes | 6 | 6 | 0 | same | 16.2 |
| `BAO_BBN_H0.lean` | `2b653083…6e38` yes | 10 | 10 | 0 | same | 17.9 |
| `BAO_Consistency.lean` | `560e3b5d…3d8b` yes | 9 | 9 | 0 | same | 10.1 |

28/28 outputs whitelist-only, no `sorry` warnings, every declared theorem has its own
`#print axioms` line. This confirms the paper's environment-1 claims (Sec. 3.4, Table 9,
Appendix A). The env-1 wall times I measured (10–18 s) are far below the recorded 73.7 / 1099.2 /
33.4 / 20.0 s, which supports the paper's own caveat that the recorded times reflect load.

Note on the import chain: for `DESI_DR2_wCDM.lean`, `import ANSE.BAO_FlatLCDM` resolves to the
shared checkout's olean (`formal/.lake/build/lib/lean/ANSE/BAO_FlatLCDM.olean`, built 12:11);
the shared checkout's `formal/ANSE/BAO_FlatLCDM.lean` hashes to the same `c85c1e8a…`, so the
dependency is the audited source. The other three files exist only in the worktree.

Toolchain: both `formal/lean-toolchain` and the LeanMaster `lean-toolchain` read
`leanprover/lean4:v4.34.0-rc2`; both `lake-manifest.json` pin Mathlib `inputRev v4.34.0-rc2`.
(See minor issue 7: the dual-check JSON asserts this string rather than measuring it.)

I did not re-run environment 2 (LeanMaster). The recorded env-2 results are consistent with the
env-1 recompile and with the recorded error text for the BLOCKED_ENV case.

### 1.2 Elenchus ledger gate

`venv-pta/bin/python .../tools/ledger.py --evidence-dir <dir>/evidence <dir>/ledger.json`:

| Ledger | rc | findings |
|---|---|---|
| `results/bao_flcdm/ledger` | 1 | 3 × `LEDGER_UNAUDITED_TIER_A` (BAO-A-0001..0003) |
| `results/desi_dr2_bao/ledger` | 0 | 25 claims, no findings |
| `results/bao_bbn_h0/ledger` | 1 | 2 × `LEDGER_UNAUDITED_TIER_A` (BBNH0-A-0009, -0010) |
| `results/eboss_vs_desi/ledger` | 0 | 27 claims, no findings |

These match Table 10 (rc 1 / 0 / 1 / 0; "A audited" 0/3, 6/6, 8/10, 9/9).

### 1.3 My own mutation controls on the gate

Script: `results/cosmo_synthesis/referee_round1_formal_ledger_mutations.py` (copies under /tmp,
originals untouched). Output: `results/cosmo_synthesis/referee_round1_formal_ledger_mutations.json`.

| Mutation (per ledger) | DR1 | DR2 | H0 | eBOSS |
|---|---|---|---|---|
| unmodified copy | rc 1 (flag) | rc 0 | rc 1 (flag) | rc 0 |
| M1: comparison row (tier L) refiled as Tier B `exact_harness` | TIER_INVERSION | TIER_INVERSION (+ORPHAN) | TIER_INVERSION | TIER_INVERSION |
| M2: Tier A row's evidence digest pointed at a *different, intact* blob | not detected | **rc 0, not detected** | not detected | **rc 0, not detected** |
| M3: Tier A audit replaced by a string | SCHEMA block | SCHEMA block | SCHEMA block | SCHEMA block |
| M4: Tier A audit replaced by `{}` | (already flagged) | **rc 0, flag cleared** | (already flagged) | **rc 0, flag cleared** |

M1 and M3 confirm the tier-cap and schema logic. M2 and M4 are the substance of major issue 4
and minor issue 3 below.

### 1.4 Paper build

`pdflatex` twice, rc 0, zero `!` errors, 17 pages, 3 overfull hboxes (cosmetic: lines 46–56,
330–336, 340–344).

## 2. Theorem-by-theorem audit (faithfulness, non-vacuity)

All hypotheses are satisfiable and no conclusion is trivially implied by its hypotheses, so
none of the 28 theorems is vacuous. Findings per file:

**`BAO_FlatLCDM`** (3). `E` is flat ΛCDM without radiation, matching the DR1 primary model.
`E_pos`, `E_strictMonoOn` on `[0,∞)` for `0<Ωm<1`: faithful, tight enough. `distance_duality`:
pure algebra; the hypothesis `z ≠ -1` is not needed in Lean (at `z=-1` both sides are 0 under
`x/0=0`), so the docstring's "for any z>-1 (so 1+z≠0)" overstates the role of the hypothesis.
Harmless.

**`DESI_DR2_wCDM`** (6). `E2` uses `Real.rpow`, matching `zp1 ** (3*(1+w))`; `Dc` is the
dimensionless interval integral. `E2_pos`/`E_pos` for every real `w` on `z ≥ 0`: faithful.
`E_w_neg_one`: unconditional, correct because `x^(0:ℝ)=1` for every real `x`. The nesting is
with the *DR1 file's* `E`, as the ledger says. `E_strictMonoOn_of_neg_one_le`: sufficient
hypothesis `w ≥ -1`, honestly scoped. `invE_continuousOn`, `Dc_strictMonoOn`: the integrability
step is genuinely established (a non-integrable interval integral would be 0 and the statement
false), so this is the one theorem in the set with real analytic content. Deviation: the
preregistration said `z > -1`; the file proves `z ≥ 0` (see minor issue 1).

**`BAO_BBN_H0`** (10). `rdAubourg`, `omegaNu`, `omegaCb` match the literature review's transcription
of Aubourg eq. 16 (`55.154`, `−72.3`, `0.25351`, `0.12807`, `ω_ν = 0.0107·0.06`) and the DESI
Ωm-includes-neutrinos convention. `rd_numerator_pos` is trivial (positivity of a constant).
`rdAubourg_pos`, `_strictAntiOn_cb`, `_strictAntiOn_b`, `rd_strictAntiOn_Om`: faithful; the
`Om` domain equals the sampler's `omega_cb > 0` mask. `DH_over_rd_eq_hrd`, `DH_over_rd_degenerate`,
`gate_reparam_exact`: field identities about `D_H/r_d` only, at fixed `E`; correct as glossed in
the file. `hrd_mono_generic`: I checked the condition analytically: `d ln(h (Ωm h² − w)^{−a})/d ln h
> 0 ⇔ (1−2a) Ωm h² > w`, so the hypothesis at `h₁` is exactly the sharp condition and the theorem is
tight. `hrd_strictMonoOn_h`: the set `{h>0 : ω_ν ≤ (1−2a)Ωm h²}` is non-empty for `Ωm>0`; threshold
`Ωm h² ≥ 0.000642/0.49298 = 0.001302`, matching the file's `0.0013`. **These two theorems are about
the secondary (Aubourg) r_d only and say nothing about the CAMB r_d of the headline PASS** — the
file says so; the paper body does not (major issue 2).

**`BAO_Consistency`** (9). `chi2_eq_dotProduct_inv_mulVec` is the load-bearing statement (ties the
closed form to Mathlib's `Matrix.inv` under `det ≠ 0`, where Mathlib's inverse of a singular matrix
is 0, so the hypothesis is the right one). `chi2_nonneg`, `chi2_eq_zero_iff`: Sylvester hypotheses
`a>0`, `ac−b²>0` are exactly 2×2 PD; correct. `posdef_add`, `surveyTension_nonneg_and_zero_iff`:
faithful to `bao_lib.tension`. `tension1D_symm`, `tension1D_nonneg`, `surveyTension_symm` are
`ring`/`positivity` trivialities. `tension1D_eq_zero_iff` needs only `σ₁>0`; correctly glossed
after the round-2 docstring fix (diff on disk is docstring-only, verified).

Trivial-but-true count: about 7 of 28 (`rd_numerator_pos`, `DH_over_rd_eq_hrd`,
`DH_over_rd_degenerate`, `gate_reparam_exact`, `tension1D_symm`, `tension1D_nonneg`,
`surveyTension_symm`). Not a defect, but see minor issue 2 on the headline count.

## 3. Issues

### Major

**M1. `lean_dual_check.json` is hand-edited and cannot be regenerated by the committed script;
two paper numbers come from hand-typed fields.** `run_lean_dual_check.py` writes neither
`accepted_count`, `print_axioms_commands_in_source`, `status`, `note`, `summary` nor `caveat`
(grep: no matches), and its acceptance test counts every `#print axioms` substring including the
comment on line 71 of `BAO_FlatLCDM.lean`, so it would still set `accepted: false` for that file.
`gen_numbers.py` reads `accepted_count` (→ `\lnPairs` = 7) and `print_axioms_commands_in_source`
(→ the `#print axioms` column of Table 9). The values are correct (my recompile: 3 commands, 3
outputs) and Sec. 3.4 discloses the correction, but (a) the AI-use statement's "every number …
is a macro … from the result JSONs" is only formally true for these two, and (b) the
Reproducibility command `python results/cosmo_synthesis/run_lean_dual_check.py` would overwrite
the JSON with a version on which `gen_numbers.py` raises `KeyError`. Fix: count commands with
`^\s*#print axioms` (comments stripped), have the script emit every key the paper reads, re-run,
and keep a `provenance` note in the JSON recording the earlier hand correction.

**M2. Sec. 3.4 and Sec. 6 item 1 overstate the scope of the H0 theorems.** The paper says the
files prove "the (h, r_d)→hr_d degeneracy of BAO observables" and "identifiability of h from
hr_d(h)". The kernel proves: (i) the degeneracy for `D_H/r_d` only, at fixed `E` (in the BBN fits
`E` depends on `h` through radiation, ~1e-4, per the file and ledger BBNH0-A-0006/0007); (ii)
identifiability for the *secondary* Aubourg `r_d` only, on the set `ω_ν ≤ (1−2a) Ωm h²`, which
excludes part of the sampled secondary prior; nothing is proved about the CAMB `r_d` that produces
the headline `H₀ = 68.545`. These caveats live in docstrings that Appendix A strips, so the paper
reader never sees them. Add one sentence to Sec. 3.4 and to the "Tier A is model-audited" bullet.

**M3. The eight H0 statement audits are bound to a stale source hash, against LL.md §12b.** Every
`BBNH0-A-0001..0008` audit carries `reviewed_source_sha256 = c0663994…`, while the row's evidence,
the ledger README and the paper all use `2b653083…`. LL.md §12b: "The audit must be bound to the
Lean file's sha256." The eBOSS ledger handles the same situation correctly (`audited_source_sha256`
+ `current_source_sha256` + `change_since_audit` + a diff file); the H0 audit objects do not name
the current hash or the change. I checked, using the pre-fix scratch copy
`/tmp/BAO_BBN_H0_negctrl.lean`, that the eight audited theorem statements are textually unchanged
(diff: header/docstrings, one import, the two new theorems and their `#print axioms` lines, plus
the control's own `sorry`), so this is a binding defect, not a content defect. Fix: add
`current_source_sha256` and `change_since_audit` (the text already exists in
`lean_verification.json.fix_round_changes`) to the eight audit objects and rebuild the ledger.

**M4. Undisclosed gate limitation: the ledger cannot detect a Tier A row that cites the wrong,
intact blob.** My mutation M2 (evidence digest of an A row pointed at another existing blob)
returns rc 0 on the DR2 and eBOSS ledgers. `ledger.py` binds digest→bytes, not claim→evidence;
the "tampered blob" control in the paper only exercises byte corruption. The paper's sentence
"Mutation controls were run … The gate caught each one" is true of the mutations run, but the
Limitations should say that claim↔blob correspondence is checked only by reading.

### Minor

1. **DR2 domain drift remains in the shipped file.** `E2_pos`/`E_pos` prove `z ≥ 0`; the
   preregistration said `z > -1`. The referee found it; the fix round left it (blob note: "so the
   audit binds to the audited file"). Sec. 3.6 lists it as a problem found; Limitations should say
   it was not fixed and why. (`z > -1` proves with the same tactics.)
2. **"28 Lean theorems" as a headline** (abstract, Sec. 3.4). About 7 are one-line identities or
   positivity of a constant. State how many carry analytic content or qualify the count.
3. **Audit field is any object.** Three ledgers use three audit schemas (`auditor_kind`,
   `auditor_is_person`, free-text `by`); `gen_numbers.py` counts `isinstance(audit, dict)`, and my
   mutation M4 shows `{}` alone clears the flag. Table 10's column header "A audited (model)" is
   correct today only because all objects happen to be model audits. Standardise on one schema
   with an `auditor_kind` field and have `gen_numbers.py` check it.
4. `\lnToolchain` is a hard-coded string in the JSON ("(both envs, per task)"), not read from
   either environment. It is true (both `lean-toolchain` files: v4.34.0-rc2), but the script should
   record `lean --version` and each `lake-manifest.json` Mathlib `rev`; the paper does not give the
   Mathlib revisions at all.
5. The negative controls (dual check and every per-run gate) exercise only `sorry`; the whitelist
   test is never exercised against a smuggled `axiom` declaration, which LL.md notes also exits 0.
   Add one `axiom foo : …` control.
6. Table 9 wall times: my env-1 re-run gives 10–18 s per file; either report re-measured times or
   drop the column.
7. Comparison rows (e.g. DR2-L-0006, BBNH0-L-0008, EVD-L-0006) are filed with `kind: citation`
   although they are computed comparisons; the L cap would follow from closure anyway. A kind that
   describes how the claim was established would be more honest.
8. eBOSS preregistered `BAO_TensionStatistic.lean` (diagonal χ²); shipped `BAO_Consistency.lean`
   (full 2×2). Disclosed in the eBOSS README and paper, not in this synthesis' list of deviations.
9. `distance_duality`'s hypothesis `z ≠ -1` is inert in Lean (both sides are 0 at `z = -1`); the
   docstring implies it is needed.
10. Three overfull hboxes in the PDF (cosmetic).

## 4. What holds up

- All 28 kernel claims: recompiled independently, whitelist-only axioms, in-file footprints.
- All four ledger exit codes and tier counts in Table 10.
- The paper's characterisation of the gate's audit weakness ("only type-checks the audit field")
  and of the env-2 BLOCKED_ENV case.
- The sorry negative control (recorded output shows `sorryAx` with rc 0 in both envs).
- Appendix A is a faithful statement-only extraction of the committed files (hashes match).

## 5. Files written by this review

- `papers/cosmo_synthesis/reviews/round1_formal.md` (this report)
- `results/cosmo_synthesis/referee_round1_formal_lean_recheck.py` / `.json`
- `results/cosmo_synthesis/referee_round1_formal_ledger_mutations.py` / `.json`
