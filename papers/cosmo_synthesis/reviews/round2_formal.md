# Referee report, round 2 of 3 — formal-methods lens

Paper: `papers/cosmo_synthesis/cosmo_synthesis.tex` (draft of 2026-09-27, revised after round 1; 21 pp.)
Referee: Claude agent (model referee; not a person). Date: 2026-09-27.
Scope: (1) did the round-1 formal issues really get fixed; (2) independent recompilation of the four
Lean modules with the pinned command; (3) faithfulness / non-vacuity of every theorem in Appendix A
against the physics and against the code it claims to mirror; (4) does the text overstate what the
kernel proves; (5) Elenchus ledger tier logic (gate re-run plus a new mutation control of my own).

Recommendation: **minor revision**. No blocking issue. Every round-1 formal fix that the response
letter marks FIXED is real on disk; every one it marks NOT FIXED is disclosed in the text as claimed.
The remaining findings are wording-level overstatements and one limitation of this review itself.

## 0. What I re-ran (all real tool output; the box carried load 4–6 from other sessions' Lean jobs,
so wall times are not reported)

Pinned command for every Lean run: `cd /home/callensxavier_gmail_com/AutoevolveAI/formal && timeout 1800 lake env lean <abs path>`.

| Check | Output file | Result |
|---|---|---|
| `BAO_FlatLCDM.lean` | `/tmp/r2f_flcdm.out` | rc 0; 3/3 `#print axioms` lines `[propext, Classical.choice, Quot.sound]` |
| `DESI_DR2_wCDM.lean` | `/tmp/r2f_dr2.out` | rc 0; 6/6 whitelist-only |
| `BAO_BBN_H0.lean` | `/tmp/r2f_h0.out` | rc 0; 10/10 whitelist-only |
| `BAO_Consistency.lean` | `/tmp/r2f_cons.out` | rc 0; 9/9 whitelist-only |
| Instrument control: copy of `BAO_Consistency.lean` with `tension1D_nonneg := by sorry` | `/tmp/r2f_sorry.out` | rc **0** (exit code alone would accept it), warning `declaration uses sorry`, and `#print axioms` shows `sorryAx` on exactly that theorem. My reading pipeline discriminates. |
| Round-1 claim "`z > -1` proves with the same tactics": `E2_pos_zgtm1`, `E_pos_zgtm1` with hypothesis `-1 < z` and the *identical* tactic scripts appended to a copy of the DR2 file | `/tmp/r2formal/DR2_zgtm1.lean`, `/tmp/r2f_zgtm1.out` | rc 0; both new theorems whitelist-only. **The claim is now tested and true** (see §4 item 3). |
| Elenchus `elenchus_check.py` (run as `lake env python3 …` from `formal/`, per LL.md §11a) on the four real files | `/tmp/r2formal/elenchus_real.txt` | `no findings`, rc 0 |
| Same scanner on a hand-built mutation of `BAO_BBN_H0.lean` with `hrd_strictMonoOn_h`'s conclusion replaced by `True` (LL.md §11b: mutate your own content, not just the tool's self-tests) | `/tmp/r2formal/H0_vacuous.lean`, `elenchus_vacuous.txt` | `VACUOUS_THEOREM … hrd_strictMonoOn_h`, rc 1. The scanner discriminates on this content. |

28/28 kernel claims independently reproduced in environment 1 with whitelist-only axioms, in-file
footprints, no `sorry` warnings. Source hashes: all four worktree files hash to the values printed
in Appendix A (`c85c1e8a…`, `3b451bd5…`, `2b653083…`, `560e3b5d…`), and the shared checkout's
`BAO_FlatLCDM.lean` (the import target of the DR2 file, olean built 12:11) hashes to the same
`c85c1e8a…`. I did not re-run environment 2 (LeanMaster); its recorded results are consistent with
the env-1 recompile and the recorded `unknown module prefix 'ANSE'` error text is the expected
BLOCKED_ENV cause.

## 1. Round-1 formal issues: were they really fixed?

| Round-1 item | Letter says | What I found on disk |
|---|---|---|
| F-M1 hand-edited `lean_dual_check.json` | FIXED | `run_lean_dual_check.py` rev. 2 computes `accepted`, `accepted_count`, `pairs_total`, `status`, `summary`, `caveat`, `history`, per-env `lean --version`, `lean-toolchain`, Mathlib `inputRev`/`rev`; counts `#print axioms` on comment-stripped source with an anchored regex (`print_axioms_commands_in_source` 3/6/10/9 vs the rev-1 substring count 4/6/10/9). The v1 file is kept and its sha256 (`bc09047f…`) is recorded in `history`. `gen_numbers.py` re-run by me: rc 0, "439 macros, 459 manifest rows", and all generated files (`gen_numbers.tex`, `gen_lean_appendix.tex`, `gen_axioms.tex`, `gen_tab_*.tex`, `number_manifest.json`) came back **byte-identical**. The reproducibility command no longer breaks the paper. Real fix. |
| F-M2 H0 theorem scope overstated | FIXED | Sec. 3.4 now states: degeneracy only for D_H/r_d at fixed E; identifiability only for the secondary Aubourg r_d on ω_ν ≤ (1−2a)Ω_m h²; nothing about CAMB r_d. Repeated in Limitations. Real fix. |
| F-M3 H0 audits bound to stale hash | DISCLOSED, not fixed (out of scope) | Confirmed: all 8 `BBNH0-A-0001..0008` audits carry `reviewed_source_sha256 = c0663994…`; current file `2b653083…`; ledger unchanged. New Table 10 column "audit hash = current file" reads 0/0, 6/6, 0/8, 0/9 and `gen_numbers.py` computes it (`lCBound`, `lDBound`). My own diff of `h0_prefix_scratch_copy.lean` (sha `d0638cc2…`) against the current file shows, at declaration level, only the two added theorems and the control's `sorry`; so the 8 audited statements are unchanged, as the paper says. Disclosure is accurate. |
| F-M4 gate passes swapped evidence | FIXED (disclosure) | Sec. 3.5 and Limitations now say claim↔blob correspondence is checked only by reading; macros `\mtMtwo`/`\mtMfour` = "0/0" trace to `referee_round1_formal_ledger_mutations.json` (manifest verified). |
| F-m1 DR2 z-domain drift | disclosed | Sec. 3.4, 3.6, Limitations say it stays in the file and why. |
| F-m2 "28 theorems" | FIXED | The 7 trivial ones are named in the abstract and Sec. 3.4. |
| F-m3 audit schema | partly | `gen_numbers.py` `named()` now requires a non-empty object with a string `by`/`auditor`/`auditor_kind`; caption says so. |
| F-m4 toolchain asserted | FIXED | Both envs measured: `Lean (version 4.34.0-rc2, … commit 6a10ac8c…)`, Mathlib rev `85e3a25e006c…`. |
| F-m5 axiom-smuggling control | FIXED | `axiom smuggled_E_pos_fact : False` control recorded in both envs: rc 0, axiom appears, whitelist rejects. |
| F-m6 wall times | FIXED | Re-measured; caption and text say single measurements on a shared machine; load average recorded. |
| F-m7/m8/m9 | disclosed | `kind: citation` rows, the `BAO_TensionStatistic`→`BAO_Consistency` rename, and the inert `z ≠ -1` hypothesis are all in Sec. 3.4/3.5 and Sec. 5 item 3. |

Paper build, by me: `pdflatex` ×2, rc 0/0, zero `!` errors, no undefined or multiply-defined
references, 1 overfull hbox (disclosed), 21 pages.

## 2. Ledger gate, re-run by me (real output)

`venv-pta/bin/python .../tools/ledger.py --evidence-dir <dir>/evidence <dir>/ledger.json`:

| Ledger | rc | findings |
|---|---|---|
| `results/bao_flcdm/ledger` | 1 | 3 × `LEDGER_UNAUDITED_TIER_A` (BAO-A-0001..0003) |
| `results/desi_dr2_bao/ledger` | 0 | "25 claims checked, no findings" |
| `results/bao_bbn_h0/ledger` | 1 | 2 × `LEDGER_UNAUDITED_TIER_A` (BBNH0-A-0009, -0010) |
| `results/eboss_vs_desi/ledger` | 0 | "27 claims checked, no findings" |

Matches Table 10 (rc 1/0/1/0; A audited 0/3, 6/6, 8/10, 9/9).

**New mutation control M5 (dependency closure), `/tmp/r2formal/ledger_closure_mutation.py`, on
copies.** Round 1 tested the kind cap (M1) but not the closure cap on its own. I refiled the Tier B
harness row that the headline Tier L comparison rests on (`DR2-B-0001`, `EVD-B-0001`,
`BBNH0-B-0001`) as Tier C `argument`, renamed its id consistently and repointed every dependent so
that neither `LEDGER_ORPHAN` nor `LEDGER_KIND_OVERCLAIM` could fire. Result: `LEDGER_TIER_INVERSION`,
rc 1, in all three ledgers (H0 additionally its two pre-existing flags). The closure rule the paper
describes ("capped by the tiers of its dependencies") does what the paper says. I also confirmed
in `ledger.py` source that `KIND_CAP` is exactly {lean_axioms:A, exact_harness:B, citation:L,
argument:C, numeric/llm_output/solver_reading:X} and that the audit check is `audit is None` plus
"must be an object" (`_schema_errors`), i.e. the paper's "the gate only type-checks the audit field"
is literally correct.

Tier-cap reading of the rows the paper names: `DR2-L-0006`, `BBNH0-L-0008`, `EVD-L-0006` each depend
on at least one L row, so their L cap follows from closure regardless of the `citation` kind label, as
the paper states. Tier C rows (`DR2-C-0001`, `BBNH0-C-0001`, `EVD-C-0002`: "the Lean definitions are
what the code computes") correctly sit below the A rows they cite; this is the right tier for a
code-reading claim.

## 3. Theorem-by-theorem audit (faithfulness to the physics and to the code; non-vacuity)

I read all four sources and compared the Lean definitions with the code they name.

**`BAO_FlatLCDM`** (3). `E` is √(Ω_m(1+z)³ + 1−Ω_m): flat ΛCDM, no radiation, the DR1 primary model.
`E_pos`, `E_strictMonoOn` on `[0,∞)` for `0<Ω_m<1`: faithful and tight. `distance_duality`:
statement true for all z (at z = −1 both sides are 0 under `x/0 = 0`), the hypothesis `z ≠ −1` is
used only by the proof (`field_simp`). Paper's description is exact.

**`DESI_DR2_wCDM`** (6). `E2` = Ω_m(1+z)³ + (1−Ω_m)(1+z)^{3(1+w)} with `Real.rpow`, which is
`dr2_model.e_of_z` at `orad = 0` (`ode = 1 - om - orad`, `zp1 ** (3.0*(1.0+w))`, checked at
`dr2_model.py:128-132`). `Dc` is the interval integral of 1/E. `E2_pos`/`E_pos` on `z ≥ 0` for every
real w (prior `w ∈ [−3, 1]` covered). `E_w_neg_one` nests with the DR1 file's `E`.
`E_strictMonoOn_of_neg_one_le` honestly restricted to `w ≥ −1`. `invE_continuousOn`,
`Dc_strictMonoOn`: integrability is established (a non-integrable interval integral is 0 in Mathlib,
so the statement would be false otherwise); this is the one theorem with real analytic content.
Deviation from the preregistered `z > −1` (`preregistration.json.lean_plan`) confirmed; disclosed.

**`BAO_BBN_H0`** (10). `rdAubourg` = 55.154·exp(−72.3(ω_ν+0.0006)²)/(ω_cb^0.25351 ω_b^0.12807),
`omegaNu` = 0.0107·0.06, `omegaCb` = Ω_m h² − ω_ν: identical to `common.py:53,114-117,131-132`
(`OMEGA_NU_AUBOURG = 0.0107*MNU`, `rd_aubourg16`, `omega_cb_of`) and to Aubourg et al. eq. 16.
`DH_over_rd` = c/(100h)/E/r_d matches `distances_manual_vec` (`dh0 = C_KM_S/(100 h)`, `dh = dh0/E`)
and `obs_from_distances`. `gate_reparam_exact` matches `make_logpost_hrd` (distances at fixed
`h_rad`, `hrd/h_rad` passed as r_d, `common.py:337-349`). `hrd_mono_generic`: hypothesis
`w ≤ (1−2a)Ω_m h₁²` is the sharp condition (d ln[h(Ω_m h²−w)^{−a}]/d ln h > 0 ⇔ (1−2a)Ω_m h² > w);
`a ≤ 1/3` is satisfied by 0.25351. `hrd_strictMonoOn_h`: the set {h>0 : ω_ν ≤ 0.49298·Ω_m h²} is
non-empty for Ω_m > 0; threshold Ω_m h² ≥ 0.000642/0.49298 = 0.0013023, matching the file's
"0.0013" and `fixround_diagnostics.json.omega_m_threshold = 0.00130228`. With the preregistered
priors H0 ∈ [20,100], Ω_m ∈ [0.01,0.99] the excluded band (e.g. Ω_m = 0.01, h ∈ [0.253, 0.361]) is
inside the sampled secondary prior, and the diagnostics record `strictly_decreasing_below: true`
there; so the paper's "excludes part of the sampled secondary prior" is right and the preregistered
bare hypothesis "1−2a>0" was indeed insufficient. `rd_numerator_pos` is positivity of a constant
(trivial, as the paper now says). Nothing in the file concerns the CAMB r_d; the paper now says so.

**`BAO_Consistency`** (9). `chi2_eq_dotProduct_inv_mulVec` ties the closed form to Mathlib's
`Matrix.inv` under `ac − b² ≠ 0` (the right hypothesis: Mathlib's inverse of a singular matrix is 0).
`chi2_nonneg`, `chi2_eq_zero_iff` under Sylvester `a>0`, `ac−b²>0`. `surveyTension` = χ² of
(C_S + C_D, p_S − p_D), which is `bao_lib.tension` (`dp = p1 - p2; C = c1 + c2; dp @ solve(C, dp)`,
`bao_lib.py:477-479`). `posdef_add`, `surveyTension_nonneg_and_zero_iff` faithful.
`tension1D_eq_zero_iff` needs only σ₁ > 0 and the docstring (post round-2 fix) says exactly that.

**Non-vacuity.** Every hypothesis set is satisfiable and no conclusion is implied by its hypotheses
alone; the 7 trivial-but-true theorems are the 7 the paper names. The Elenchus scanner reports
`no findings` on all four real files and flags my hand-built vacuous mutation (§0), so "none vacuous"
is supported by a discriminating instrument, not only by my reading.

**Ledger glosses vs statements.** I read all 28 Tier A `statement` fields against the Lean
statements. They are faithful, including the "at fixed E" caveat on `BBNH0-A-0006/0007` and the
scope note on `BBNH0-A-0010`. All audit objects name a model auditor (`auditor_kind: "model"`,
`"NOT a person"`, or `auditor_is_person: false`); none claims to be a person.

## 4. Does the text overstate what the kernel proves?

Mostly no; the revised Sec. 3.4 is careful. Remaining wording issues, all minor:

1. **Abstract, "the algebraic skeleton of each model is stated and kernel-checked in Lean 4".** For
   the H0 run's *primary* model the r_d is a CAMB table; it has no Lean skeleton at all (the body
   says so in Sec. 3.4 and Limitations, the abstract does not). Suggest "of each closed-form model"
   or add "(for the H0 run, the secondary fitting-formula model only)".
2. **"Two environments" / "a second Mathlib environment" (abstract, Sec. 3.4, Table 9).** Both
   environments run the same Lean binary (commit `6a10ac8c`) against the same Mathlib commit
   (`85e3a25e006c`). What differs is build completeness: I counted 3431 Mathlib `.olean` files in the
   pinned project versus 8370 (of 8370 sources) in the LeanMaster copy. The dual check therefore
   tests independence from the partial build, not from the compiler or the Mathlib version. Sec. 3.4
   prints the shared versions, but one sentence should say explicitly what the second environment
   does and does not add.
3. **Sec. 3.6, "the referee expected z > −1 to prove with the same tactics, which we did not test."**
   Now tested by me (§0): `E2_pos` and `E_pos` with hypothesis `-1 < z` compile with the byte-identical
   tactic scripts, whitelist-only axioms. The sentence should become "which the round-2 referee
   confirmed" (or the authors re-run `/tmp/r2formal/DR2_zgtm1.lean`). The preregistered domain is
   therefore recoverable at zero proof cost; the only reason it stays drifted is audit binding, and
   the paper should say that plainly rather than leaving the provability open.
4. **Sec. 3.4, "7 … are one-line identities or positivity statements".** `DH_over_rd_eq_hrd` and
   `gate_reparam_exact` are 3-tactic proofs; "one-line" reads as mathematical content, not tactic
   count. Cosmetic.
5. **Project hygiene, outside this paper's scope but relevant to "kernel-checked in the pinned build".**
   The worktree's `formal/ANSE.lean` imports all four modules, but no `lake build` of that root with
   the three new modules is recorded anywhere; the main checkout's `formal/ANSE.lean` still imports
   `ANSE.BAO_FlatLCDM` twice and none of the three new modules. All kernel checks are `lake env lean`
   on single files, as the paper discloses. Worth one sentence in Reproducibility ("the modules are
   not yet part of the project's `lake build`").

## 5. What holds up

- The round-1 formal fixes are real, not cosmetic: the checker was rewritten and its output is
  reproducible (byte-identical regeneration of every generated file), the smuggled-axiom control
  exists and is recorded, the toolchain is measured, the H0 scope limits are in the body text.
- All four ledger gate exit codes and Table 10 counts reproduce; the closure cap works (new M5).
- Appendix A is a faithful statement-only extraction; every Lean definition matches the named code
  lines; no theorem is vacuous; the H0 identifiability domain and threshold check out analytically
  and against the recorded numerics.
- All 28 kernel claims recompiled by me in the pinned build, rc 0, whitelist-only axioms; the sorry
  control shows my pipeline would have caught a `sorry`; Elenchus clean on the real files and
  discriminating on a mutation.

## 6. Files written by this review

- `papers/cosmo_synthesis/reviews/round2_formal.md` (this report)
- Scratch, under `/tmp/r2formal/` and `/tmp/r2f_*.out`: `ledger_closure_mutation.py` + `.json` (M5
  control), `DR2_zgtm1.lean` (+ `/tmp/r2f_zgtm1.out`), `Consistency_sorry.lean` (+ `/tmp/r2f_sorry.out`),
  `H0_vacuous.lean`, `elenchus_real.txt`, `elenchus_vacuous.txt`, `gen_before.sha`/`gen_after.sha`
  (byte-identity check), `pdflatex1.txt`/`2.txt`; the four compile logs `/tmp/r2f_{flcdm,dr2,h0,cons}.out`.
- Nothing under `results/` was modified; the authors' ledgers, Lean files and scripts are untouched.
  The paper directory was rebuilt (`gen_numbers.py`, `pdflatex` ×2) with byte-identical generated files.
