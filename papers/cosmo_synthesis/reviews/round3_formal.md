# Referee report, round 3 of 3 — formal-methods lens

Paper: `papers/cosmo_synthesis/cosmo_synthesis.tex` (draft of 2026-09-27, revised after round 2; 23 pp.)
Referee: Claude agent (model referee; not a person). Date: 2026-09-27.
Scope: (1) were the round-2 formal items really fixed; (2) independent recompilation of every Lean
module with the pinned command, plus one module in environment 2; (3) faithfulness and non-vacuity
of every theorem in Appendix A against the physics and the code; (4) does the text overstate what
the kernel proves; (5) ledger tier logic: gate re-run, a content-level claim-to-blob audit that no
earlier round did programmatically, one new mutation control, and the tier semantics themselves.

Recommendation: **minor revision**. No blocking issue: every kernel claim reproduces, every ledger
exit code reproduces, and every round-2 fix marked FIXED is real on disk. Two new findings, one of
them major, concern the ledger tier semantics and a sharper form of the gate limitation the paper
already discloses. Neither makes a cosmological claim false.

## 0. What I re-ran (all real tool output; box load 4–8 from other sessions' Lean jobs)

Pinned command: `cd /home/callensxavier_gmail_com/AutoevolveAI/formal && timeout 1800 lake env lean <abs path>`.
Driver script `/tmp/r3f/lean_recheck.py`, output `/tmp/r3f/lean_recheck.json` and per-file `/tmp/r3f/*.out`.

| File | sha256 = Appendix A | theorems | `#print axioms` cmds (comment-stripped) | rc | outputs whitelist-only | sorry warning | wall [s] |
|---|---|---|---|---|---|---|---|
| `BAO_FlatLCDM.lean` | `c85c1e8a…` yes | 3 | 3 | 0 | 3/3 | no | 81.7 |
| `DESI_DR2_wCDM.lean` | `3b451bd5…` yes | 6 | 6 | 0 | 6/6 | no | 7.1 |
| `BAO_BBN_H0.lean` | `2b653083…` yes | 10 | 10 | 0 | 10/10 | no | 13.9 |
| `BAO_Consistency.lean` | `560e3b5d…` yes | 9 | 9 | 0 | 9/9 | no | 7.6 |
| `results/cosmo_synthesis/dr2_zgtm1_check.lean` (paper's z > −1 test) | `ca31d646…` yes | 8 | 8 | 0 | 8/8 (incl. `E2_pos_zgtm1`, `E_pos_zgtm1`) | no | 16.8 |

28/28 kernel claims reproduced in environment 1 with whitelist-only axioms. The DR2 file's
`import ANSE.BAO_FlatLCDM` resolves to the shared checkout's olean; that checkout's
`BAO_FlatLCDM.lean` hashes to the same `c85c1e8a…`. Wall times are single measurements under load
(the paper says the same of its own).

Other checks:

| Check | Result |
|---|---|
| `git show` of the only commit touching each file (`d58b63c` for the three new modules, `117cc0e` for `BAO_FlatLCDM`) | committed bytes hash to `2b653083…`, `3b451bd5…`, `560e3b5d…`, `c85c1e8a…`: the appendix is extracted from the committed bytes, and the H0 audit hash `c0663994…` was indeed never committed (paper Sec. 3.5) |
| **New kernel test of a paper claim**: `distance_duality` without the `z ≠ -1` hypothesis (`/tmp/r3f/dd_nohyp.lean`, `by_cases` on `1 + z = 0`) | rc 0, `[propext, Classical.choice, Quot.sound]`. The paper's "the hypothesis is inert in Lean" (Sec. 3.4, Limitations) is now kernel-checked, not only argued |
| Elenchus `elenchus_check.py` on the four real files (`lake env python3 …` from `formal/`, LL.md §11a) | `no findings`, rc 0 (`/tmp/r3f/elenchus_real.txt`) |
| Instrument control (LL.md §11b): `BAO_Consistency.lean` with `chi2_nonneg`'s conclusion replaced by `True` (`/tmp/r3f/Cons_vacuous.lean`) | `VACUOUS_THEOREM … chi2_nonneg`, rc 1 (plus a `COMPILE_ERROR` because the corollary that uses it no longer type-checks). The scanner discriminates on this content |
| Mathlib `.olean` counts, counted by me with `find` | env 1: 3431 of 8370 sources; env 2: 8370 — matches `\mbOne`/`\mbTwo`/`\mbSrc` |
| `formal/ANSE.lean`, worktree vs main checkout | worktree imports all four modules once each; main imports `ANSE.BAO_FlatLCDM` twice and none of the new three — matches `\lrMainFlat = 2`, `\lrMainNew = 0` |
| `anse/formal/lean_runner.py` | runs `lake build` in `formal/` and writes `.tmp_axiom_check.lean` into `formal/` importing a built module: the paper's reason for the documented deviation is accurate |
| Paper build: `pdflatex` ×2 | rc 0/0, 0 `!` errors, no undefined/multiply-defined references, **0 overfull boxes**, 23 pages |
| Environment 2 (LeanMaster full Mathlib), `BAO_Consistency.lean` | see §0b |

### 0b. Environment 2, run by me

No earlier round re-ran environment 2. I ran one file there:
`cd /home/callensxavier_gmail_com/SocrateAI-Scientific-Agora-LeanMaster && timeout 1800 lake env lean
<worktree>/formal/ANSE/BAO_Consistency.lean` → **rc 0, 9/9 `#print axioms` outputs
`[propext, Classical.choice, Quot.sound]`** (`/tmp/r3f/env2_consistency.out`). Wall time was well over
15 minutes under load 5–8 with other sessions' Lean jobs running, versus the paper's recorded 313 s;
this supports the paper's caveat that the times are not benchmarks. The recorded env-2 results for
the other two accepted files and the BLOCKED_ENV case were not re-run by me; they are consistent with
the env-1 recompile and the recorded error text (`unknown module prefix 'ANSE'`) is the expected cause.

## 1. Round-2 formal items: were they really fixed?

| Round-2 item | Letter says | What I found |
|---|---|---|
| 1. Abstract "each model" | FIXED | Abstract now reads "each closed-form model" and states that for the H0 run only the secondary fitting-formula r_d has a Lean skeleton. Real. |
| 2. "Second environment" not an independent toolchain | FIXED | Abstract, Sec. 3.4 and Limitations say same Lean binary and Mathlib commit; the 3431/8370 counts are macros traced to `round2_response_checks.json` (`mathlib_builds.*.n_olean`) and reproduce with `find`. Real. |
| 3. z > −1 "not tested" | FIXED, re-tested by the authors | `dr2_zgtm1_check.lean` exists, hashes to `ca31d646…` (macro `\zgSha`), recompiles rc 0 with 8 whitelist-only outputs (my run). `E2_pos_zgtm1`'s tactic script is byte-identical to `E2_pos`; `E_pos_zgtm1` differs only in calling `E2_pos_zgtm1`. The paper says exactly that and that the other DR2 theorems were not re-tested. Real. |
| 4. Modules not in `lake build` | FIXED (disclosed) | Sec. 3.4 and Limitations say so; import counts are macros. Real. |
| 5. "one-line" | FIXED | "short identities or positivity statements … some proofs take three tactics". Real. |

Round-1 items that were marked NOT FIXED (H0 audit binding, `kind: citation`, z ≥ 0 drift, inert
hypothesis) remain disclosed exactly as before; nothing regressed. `gen_numbers.py` macros that this
lens reads (`\lnPairs`, `\lnCleanTwo`, `\lnTotal`, `\lnAppendixN`, `\lCBound`, `\lDBound`,
`\mtMtwo`, `\mtMfour`, `\zgRc`, `\lnNegSorry`, `\lnAxRejected`, `\lnMathlibRev`) all trace in
`number_manifest.json` to `lean_dual_check.json`, `round1/2_response_checks.json` or the
round-1 mutation JSON.

## 2. Ledger gate, re-run by me

`python3 …/tools/ledger.py --evidence-dir <dir>/evidence <dir>/ledger.json`:

| Ledger | rc | findings | claims |
|---|---|---|---|
| `results/bao_flcdm/ledger` | 1 | 3 × `LEDGER_UNAUDITED_TIER_A` (BAO-A-0001..0003) | 6 |
| `results/desi_dr2_bao/ledger` | 0 | none | 25 |
| `results/bao_bbn_h0/ledger` | 1 | 2 × `LEDGER_UNAUDITED_TIER_A` (BBNH0-A-0009, -0010) | 43 |
| `results/eboss_vs_desi/ledger` | 0 | none | 27 |

Matches Table 10 (rc 1/0/1/0; tier counts 3/1/2/0, 6/8/10/1, 10/17/15/1, 9/8/8/2) and the
`gate_check.json` keys the macros read.

### 2a. Claim-to-blob correspondence checked by content (new)

Rounds 1–2 established that the gate binds digests to bytes, not claims to evidence, and the paper
says correspondence "is checked only by reading". No round had actually done that reading
programmatically. `/tmp/r3f/ledger_audit.py` (`/tmp/r3f/ledger_audit.json`) opens the blob each of
the 28 Tier A rows points at and checks that it contains (i) a `#print axioms` line for the theorem
named in the row's `statement`, with whitelist-only axioms, and (ii) the sha256 of the *current*
Lean file. **All 28 rows pass both checks.** So the Tier A layer of all four ledgers is not only
hash-consistent but content-consistent with the shipped Lean files. This supports the paper.

Audit binding, from the audit objects themselves: DR2 audits carry `audited_file_sha256 =
3b451bd5…` (current) and `report_sha256 = 572146f1…`, which is the sha256 of
`results/desi_dr2_bao/referee_report.json` today, and that report contains the audit text (e.g.
`intervalIntegral_pos_of_pos_on`). eBOSS audits carry `audited_source_sha256 = bafdfab4…`,
`current_source_sha256 = 560e3b5d…` (current), `change_since_audit` naming the docstring diff, whose
file I read (docstring of `tension1D_eq_zero_iff` only), and `referee_report_sha256 = 70aadbb0…`,
which matches `referee_report_round2.json`. H0 audits carry only `reviewed_source_sha256 =
c0663994…` and `evidence_sha256 = e56e32ba…` (matches `referee_statement_audit_fixround.json`,
which contains the audit comments); no current hash, no change record. Table 10's 6/6, 0/8, 0/9
column is therefore right, and the H0 defect is exactly as the paper describes it.

### 2b. New mutation control M6: `sorryAx` inside a Tier A row's own blob

`/tmp/r3f/ledger_sorry_blob_mutation.py`, on copies under `/tmp/r3f/m6/`. For one `lean_axioms` row
per preregistered ledger (DR2-A-0002, EVD-A-0005, BBNH0-A-0002) I rewrote the blob's
`kernel_axiom_footprint` line to `[propext, sorryAx, Classical.choice, Quot.sound]`, stored the
mutated blob under its own sha256 and repointed the row. Gate result: **rc unchanged (0, 0, 1);
not detected** in any ledger. I confirmed in `ledger.py` that the only blob checks are
`LEDGER_EVIDENCE_MISSING`/`_MISMATCH` (hash) and `LEDGER_NO_PROVENANCE` (for `solver_reading`
only); a `lean_axioms` blob's content is never parsed. This is the sharpest form of the limitation
the paper already states (round-1 M2: swapped intact blob). It means the "kernel-verified" meaning of
Tier A rests on whoever wrote the blob, not on the gate; the paper should say this in one sentence.

### 2c. Tier B semantics (new, major)

Sec. 3.5 defines the ladder as "A is kernel-checked Lean, **B is exact harness output**, L is a
literature citation and C is a conjecture". The cited tool defines B differently. Elenchus
`docs/ELENCHUS.md` §1: **B** = "an identity verified in exact rational arithmetic on concrete
instances … a harness using integers and rationals only"; **X** = "Exploratory: floats, sampling,
model output … may never support a claim"; README: "a floating-point number can never rise above the
lowest [tier]". LL.md §11a records the same ("B exact-arithmetic"). Every Tier B row in the four
ledgers (1 + 8 + 17 + 8 = 34 rows) is floating-point or Monte Carlo output: emcee posterior means,
CAMB/CLASS backgrounds, χ² of controls. Under the tool's own kind table these are `numeric` → X, and
by dependency closure the L comparison rows that rest on them (e.g. DR2-L-0006, BBNH0-L-0008,
EVD-L-0006) would be capped at X as well. The gate cannot see this because `kind` is self-declared.

Two of the run ledgers do disclose the redefinition (`results/eboss_vs_desi/ledger/README.md`
line 21: "It is not exact rational arithmetic. The emcee moments are Monte Carlo estimates";
`results/bao_bbn_h0/ledger/README.md` line 37 likewise, "follows the earlier templates"). The DR1
and DR2 ledger READMEs and the synthesis paper do not. Consequences for the paper:

- The sentence "B is exact harness output" misdescribes the tool it cites; the honest version is
  "B, as used here, is a seeded floating-point harness on sha256-verified inputs, re-run bit for
  bit; Elenchus's own B is ℚ/ℤ arithmetic and it files floats at X".
- The mutation controls M1 (round 1) and M5 (round 2) tested that an L row cannot sit above a B
  row and that a B row refiled at C drags its dependents down. Both are correct tests of the closure
  rule, but they presuppose that the fits belong at B. They do under the paper's redefinition, not
  under the tool's.
- Nothing numeric changes. The verdicts, pulls and controls are what they are; only the epistemic
  label "B" is borrowed from a ladder that would not grant it. This is a disclosure defect in the
  paper and a template defect inherited from the DR1 run, not a defect in any number.

Fix in this paper's write scope: one sentence in Sec. 3.5 and a footnote or caption note on
Table 10 ("B here = seeded float harness; Elenchus's B = exact ℚ/ℤ, which would file these rows at
X"). Fixing the ledgers themselves (a `float_harness` kind, or refiling at X) is outside scope, as
the paper already says of other ledger defects; it belongs on the same list.

## 3. Theorem-by-theorem audit (fresh read; agrees with rounds 1–2 where they overlap)

I read all four sources against the code lines they name (`dr2_model.py:128-132`,
`common.py:52-53,114-117,131-132,223-239,321,337-349`, `bao_lib.py:475-484`) and against the
preregistrations' `lean_plan` fields.

- **`BAO_FlatLCDM`** (3): `E`, `E_pos`, `E_strictMonoOn` on `[0,∞)` for `0<Ωm<1`, `distance_duality`.
  Faithful; hypothesis `z ≠ -1` inert (kernel-checked by me, §0). The DR1 grid (0.2–0.4 in Ωm) lies
  inside the hypotheses.
- **`DESI_DR2_wCDM`** (6): `E2` is `e_of_z` at `orad = 0` with `Real.rpow`; `Dc` the dimensionless
  interval integral. `E2_pos`/`E_pos` for every real w on `z ≥ 0` (prior `w ∈ [−3,1]` covered);
  `E_w_neg_one` nests with the DR1 `E` (uses `rpow_zero`, valid even at `1+z = 0`);
  `E_strictMonoOn_of_neg_one_le` honestly restricted to `w ≥ −1`; `invE_continuousOn`,
  `Dc_strictMonoOn` establish integrability (a non-integrable interval integral is 0 in Mathlib, so
  the theorem would be false otherwise). Preregistered `lean_plan`: "E(z)^2 > 0 for 0<Om<1, z>-1 (any
  real w); w=-1 reduces to LCDM E^2; comoving distance integrand positive hence D_C monotone". The
  shipped set covers all three items; only the positivity domain drifted to `z ≥ 0`, as disclosed.
  Note the plan fixes `z > −1` for positivity only; the paper's "the monotonicity and D_C theorems
  were not re-tested on z > −1" implies a planned domain those theorems never had. Cosmetic.
- **`BAO_BBN_H0`** (10): `omegaNu = 0.0107·0.06` = `OMEGA_NU_AUBOURG = 0.0107*MNU` with `MNU = 0.06`
  (`common.py:52-53`); `rdAubourg`, `omegaCb` identical to `rd_aubourg16`, `omega_cb_of`; `DH_over_rd`
  matches `dh0 = C/(100h)`, `dh = dh0/E`, `/ rd`; `gate_reparam_exact` matches `make_logpost_hrd`
  (distances at fixed `h_rad`, `hrd/h_rad` as r_d). `rd_strictAntiOn_Om`'s domain is the sampler's
  `omega_cb_of(...) > 0` mask (line 321). `hrd_mono_generic`: I re-derived the condition
  `d ln[h(Ωm h²−w)^{−a}]/d ln h > 0 ⇔ (1−2a)Ωm h² > w`; the hypothesis at `h₁` is sharp and
  `a ≤ 1/3` is what makes the Bernoulli exponent `e = a/(1−2a) ≤ 1`. `hrd_strictMonoOn_h`: threshold
  `0.000642/0.49298 = 0.0013023` = `fixround_diagnostics.json.omega_m_threshold = 0.00130228`, with
  `strictly_decreasing_below: true` recorded; the excluded band is inside the secondary prior, so the
  preregistered bare `1−2a > 0` was insufficient, as the paper says. Preregistered plan ("positivity
  and strict antitonicity of A·x^(−a)·b^(−c); H0 = 100 h; h·r_d(h) strictly increasing for 1−2a>0")
  is covered, with the hypothesis honestly strengthened. Nothing about the CAMB r_d; paper says so.
- **`BAO_Consistency`** (9): `chi2_eq_dotProduct_inv_mulVec` ties the closed form to Mathlib's
  `Matrix.inv` under `ac−b² ≠ 0` (the right hypothesis: Mathlib's inverse of a singular matrix is 0);
  `chi2_nonneg`, `chi2_eq_zero_iff` under Sylvester; `surveyTension` = `bao_lib.tension`
  (`dp = p1 - p2; C = c1 + c2; dp @ solve(C, dp)`); `tension1D` = the squared `one_d_sigma`.
  Preregistered `BAO_TensionStatistic.lean` (diagonal χ²) shipped as the full 2×2 file, disclosed.

**Non-vacuity.** Every hypothesis set is satisfiable and no conclusion is implied by hypotheses
alone; the 7 trivial theorems are the 7 the paper names; Elenchus reports no findings on the real
files and flags my mutation. **Ledger glosses.** All 28 `statement` fields are faithful to the Lean
statements (including the "at fixed E" caveat on BBNH0-A-0006/0007 and the scope note on
BBNH0-A-0010). All audit objects name a model auditor; none claims to be a person.

## 4. Does the text overstate what the kernel proves?

No. The revised Sec. 3.4 is careful: the H0 degeneracy theorems are labelled D_H/r_d-only and
fixed-E, identifiability is labelled secondary-r_d-only on the stated set, the CAMB r_d has no
skeleton, the second environment is labelled same-toolchain, and the z ≥ 0 drift is stated with the
z > −1 re-test scoped to the two positivity theorems. Remaining wording items, all minor:

1. **Sec. 3.5 "B is exact harness output"** — see §2c. This is the one place the paper describes the
   ledger in terms the cited tool does not support.
2. **Sec. 3.5, gate limitations** — add that a `lean_axioms` blob's content is never parsed, so a
   blob reporting `sorryAx` passes at Tier A (M6, §2b). The current sentence ("binds each evidence
   digest to bytes, not a claim to its evidence") implies it but does not say it.
3. **Sec. 3.4 "(per the round-1 formal referee)"** on the excluded prior band: the Lean file header
   (lines 51–55) and `fixround_diagnostics.json` already state and measure this; attributing it to
   the referee undersells the authors' own record. Cosmetic.
4. **Sec. 3.4 "the monotonicity and D_C theorems were not re-tested on z > −1"** — the
   preregistration set `z > −1` only for positivity (§3). Say "were not tested on z > −1 (the
   preregistration fixed no domain for them)". Cosmetic.
5. **Sec. 3.4 first sentence** omits the eBOSS file's load-bearing statement
   (`chi2_eq_dotProduct_inv_mulVec`, closed form = Mathlib inverse) and the DR2 nesting identity
   from its list of what is stated; an understatement, not an overstatement.

## 5. What holds up

- All 28 kernel claims recompiled by me in the pinned build, rc 0, whitelist-only axioms, in-file
  footprints, no `sorry` warnings; the paper's z > −1 file recompiles; the inert-hypothesis claim
  is now kernel-checked.
- Every appendix hash equals the committed bytes (`git show`), so Appendix A is an extraction of
  what is in git, and the H0 audit hash is provably uncommitted.
- All four ledger exit codes, tier counts and audit-binding counts reproduce; every Tier A blob
  contains the right theorem's whitelist-only footprint and the current source hash (new, §2a).
- Elenchus clean on the real files and discriminating on a hand-built vacuous mutation.
- Every round-2 formal fix is real, and the generated numbers this lens depends on trace through
  `number_manifest.json` to script-written JSON.

## 6. Files written by this review

- `papers/cosmo_synthesis/reviews/round3_formal.md` (this report).
- Scratch under `/tmp/r3f/`: `lean_recheck.py` + `lean_recheck.json` + five `*.out` compile logs;
  `dd_nohyp.lean` (inert-hypothesis kernel test); `ledger_audit.py` + `ledger_audit.json`
  (content-level Tier A audit); `ledger_sorry_blob_mutation.py` + `m6/` (M6 control, copies only);
  `Cons_vacuous.lean` (Elenchus instrument control); `elenchus_real.txt`; `env2_consistency.out`;
  `pdflatex1.txt`, `pdflatex2.txt`.
- Nothing under `results/` or `formal/` was modified. The paper directory was rebuilt with
  `pdflatex` ×2 only (PDF, `.aux`, `.log`, `.out` refreshed; sources untouched).
