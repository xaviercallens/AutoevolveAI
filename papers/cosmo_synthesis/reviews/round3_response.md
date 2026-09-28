# Response to round-3 referee reports

Manuscript: `papers/cosmo_synthesis/cosmo_synthesis.tex`. Revising agent: a Claude model in Claude Code, not a person.
Build after revision: `pdflatex -interaction=nonstopmode` twice, rc 0 / rc 0, no `!` errors, no undefined references, 0 overfull boxes, **26 pages** (was 23). `gen_numbers.py` now writes 523 macros and 549 manifest rows (was 472 and 494). `pdftotext` shows no `??`.

New files. Everything is under `results/cosmo_synthesis/` unless a path is given:
- `round3_env_rerun_setup.py`: builds two isolated copies of the frozen H0 pipeline under `/tmp/r3resp/{cosmo,pta}`. The only patch is the chain output directory.
- `round3_response_checks.py` → `round3_response_checks.json`. Contents: interpreter versions; both re-runs compared with the committed `fit.json`; MAP and posterior-mean formula shifts; Aubourg ω_cb convention; overlap X vs X+Xᵀ; strict-window terms; DR1 interpreter check.
- `round3_m6_sorry_blob_mutation.py` → `round3_m6_mutation.json`. This is the formal referee's M6 control, copied and re-run on ledger copies.
- `literature_search_log_round3.json`.
- `round3_rerun_fit_venv_pta.json` and `round3_rerun_fit_venv_cosmo.json`: copies of the two re-run `fit.json` outputs, kept as on-disk evidence. Their hashes are in the paper's sha256 table (`tab:sha`).
- `papers/cosmo_synthesis/gen_numbers.py`: adds `round3()`, the Table 4 marker, relabelled derived-table rows and two new hashed JSONs.
- `papers/cosmo_synthesis/make_figures.py`: Fig. 2 shows the re-run point and a two-label title. The Fig. 1 T2 label shows both labels.

Nothing outside `papers/cosmo_synthesis/` and `results/cosmo_synthesis/` was written. The only other writes were scratch files under `/tmp/r3resp/`.

---

## Statistics / cosmology referee (recommendation: major)

### M1 (major): the primary T2 verdict depends on the environment. FIXED by disclosure; no verdict re-tuned.
**Reproduced first.** I re-ran the frozen `fit_real.py` under both interpreters (`round3_response_checks.json`, key `h0_env_rerun`):
- **venv-pta** (Py 3.10.12, numpy 1.26.4, scipy 1.15.3): 0 of 943 numeric leaves differ from the committed `fit.json`. The recorded H0 run therefore came from venv-pta.
- **venv-cosmo** (Py 3.11.16, numpy 2.4.6, scipy 1.17.1): 751 of 943 leaves differ.
  - Primary T2: H0 = 68.675 and |ΔH0| = 0.1455, which is **PASS**. The recorded values are 0.167, PARTIAL.
  - Primary T1: PASS, secondary T1: PASS, secondary T2: PARTIAL (0.1725).
  - The primary T2 shift is 1.5 committed MC errors.

Both environments have emcee 3.1.6. The referee's numbers are confirmed.

**Changes:**
- **Abstract:** "verdict PARTIAL in the recorded run", followed by the re-execution result (PASS, 0.1455, 1.5 MC errors, "depends on the numerical environment and the strict boundary is not resolved").
- **Sec. 3.2:**
  - The identity with the locked file is now "expected from fixed seeds, the same code path *and the same numerical environment*". Under venv-cosmo the secondary differs from the locked file by −0.0015 (DR2) and 0.0011 (DR1), so the comparison shows same-environment reproducibility only.
  - "The verdicts stay as preregistered" is replaced by: no tolerance was changed after the fits; the verdicts are what the rule gives for the recorded run; the primary T2 label is not stable under re-execution.
- **Sec. 4.3:**
  - "PARTIAL is reported and stays" is removed.
  - New paragraph "Numerical-environment dependence (found by the round-3 referee, confirmed here)" (label `sec:env`). It gives both environments with versions, the leaf counts, all four re-run verdicts and the G2 shift. It states that the preregistration names no interpreter, so both executions are equally valid. It includes the referee's recommendation that such a rule needs either a chain long enough that the MC error is much smaller than the margin, or a deterministic estimator.
  - The DR2 bit-identity in both interpreters is attributed to the referee; I did not repeat it.
  - The G2 implied shift is now computed with the round-2 `g2_attribution` formula: 0.140 under venv-cosmo, the referee's value. The check script asserts that the formula reproduces the recorded 0.183.
  - Integer leaves (chain lengths, burn-in) also differ, because the chains stop adaptively. The max |ΔH0_MAP| between environments is 9.2e-8, now a macro. venv-pta shows no non-numeric differences.
- **Table 4:** the primary T2_H0 row now reads "no (soft: yes) [re-run: yes]‡". This text is generated from `round3_response_checks.json`. The caption explains ‡ and names venv-pta as the recorded run.
- **Fig. 2:** hollow diamond at the venv-cosmo primary mean. The panel title reads "PARTIAL (recorded run) / PASS (re-run)", generated from the JSON. **Fig. 1:** the T2 label shows both labels.
- **Limitations:**
  - "Partial result" becomes "Partial result, environment-dependent".
  - New item "Unrecorded numerical environment".
- **Sec. 5, item 3** (process failures): adds the verdict flip and the unrecorded interpreter.
- **Reproducibility:** rewritten. It gives both interpreters with versions, the interpreter behind each recorded JSON and how that was established, and one interpreter per command.

**Not fixable here:**
- The run JSONs cannot record their interpreter after the fact.
- The `fit.json` note "secondary re-run identical ... is expected" is in `results/bao_bbn_h0/`, outside the write scope.

Both are disclosed in Limitations. LL.md is outside scope. The lesson is stated in Sec. 4.3 and should be carried to LL.md by the orchestrator.

### m1: MAP differences replace the MC-noise-dominated formula systematic. FIXED.
The MAP differences are −0.0419 (DR2) and −0.0411 (DR1). In my venv-cosmo re-run they agree to 1e-7.

The posterior-mean differences are now quoted with their MC errors: −0.034 ± 0.015 and −0.0044 ± 0.020. Under venv-cosmo they are −0.029 and −0.027. The text states that the smaller DR1 value is not a smaller systematic.

Changed in Sec. 4.3 ("Formula-versus-CAMB shift"), Table 7 (MAP rows, plus a posterior-mean row with ± MC) and Sec. 4.5(c).

The deterministic numbers changed a conclusion. The referee wrote that 4.5(c)'s "confirms Aubourg's stated accuracy" would become stronger. It does not. The MAP shift of 0.042 equals the propagation of the **measured** formula error at the first validation point: −0.029% gives −0.0408 via Δln h = −ε/slope, and the stated 0.021% would give only −0.029.

Sec. 4.5(c) and the Table 7 label now say that the shift equals the propagated measured error. That error exceeds the stated 0.021%, which is consistent with the Sec. 4.3 exceedances. The earlier claim of confirming the stated figure is withdrawn. The prediction is computed in `round3_response_checks.json`, key `h0_env_rerun.formula_prediction`.

### m2: "X" should read "X + Xᵀ". FIXED.
Changed in Sec. 4.5(b), which now says "(the covariance of a difference)", and in the Table 7 label.

I checked the referee's number. Subtracting the literal X alone gives N_σ = 1.06 and PTE 0.29 (`overlap_x_only.X_only`). Subtracting X + Xᵀ reproduces 1.344. The 1.06 value is not printed in the paper.

### m3: part of the Aubourg remainder is a convention. FIXED as a description of both conventions.
`rd_camb_table.py` compares CAMB and eq. (16) at equal Ω_m h², which is what the fit samples. That comparison places eq. (16) at ω_cb offset by +2.9e-6 from the grid point's ω_b + ω_cdm.

At the grid point's own ω_b + ω_cdm (Aubourg's convention), the worst deviation from CAMB at N_eff = 3.046 is 0.0219%. One point is still above 0.021%. Sec. 4.3 now says that the N_eff convention and this ω_cb convention together explain most of the excess, and that a residual of order 1e-5 was not traced. The code is not called a bug.

### m4: the G2 source string cites the DR1 abstract. FIXED in the Table 5 caption.
The preregistration string cannot be edited. The caption says the fetched abstract quotes only Ω_m and H0, and that r_d h is in eq. (4.1) and Sec. 8.

### m5: interpreter-less commands; stale docstring. FIXED in the paper; the docstring is NOT FIXED (outside scope).
Every command now carries its interpreter.

I re-ran `fit_desi_bao.py`:
- Under venv-cosmo it reproduces the committed JSON; only `generated_at` differs.
- Under venv-pta it fails with `ImportError: cannot import name 'UTC' from 'datetime'`.

The docstring lives in `scripts/`, outside the write scope, so it is listed in Limitations.

### m6: the strict window was quoted without its MC term. FIXED.
Sec. 3.2 now gives √(0.139² + 0.05²) = 0.148 → 0.15 and names the 0.05 MC and numerics allowance, together with the preregistration's own MC estimate ("posterior-mean MC error ~0.58/sqrt(ESS~1000) = 0.02", verified in `preregistration.json`). It also says the post-hoc re-budget of 0.050 is that same 0.05 plus a 0.0044 interpolation term. These values are read from `preregistration.json` and `fixround_diagnostics.json` and are recomputed in `strict_window`.

---

## Formal-methods referee (recommendation: minor)

### Major: "B is exact harness output" misdescribes Elenchus's Tier B. FIXED by disclosure in the paper; ledgers NOT CHANGED (outside scope).
I checked the tool's own text. `docs/ELENCHUS.md` line 21 defines B as "an identity verified in exact rational arithmetic". Line 24 files floats, sampling and model output at X ("may never support a claim").

**Sec. 3.5** now has a paragraph "Our Tier B is not Elenchus's Tier B". It states:
- All 34 Tier B rows (1/8/17/8, from the ledger tier-count macros) are seeded floating-point or MC harness outputs.
- Under the tool's semantics they would be X, and by closure so would the L comparison rows that rest on them.
- The gate cannot see this because `kind` is self-declared.
- The H0 and eBOSS READMEs disclose the redefinition; the DR1 and DR2 READMEs do not. I checked this by grep: `results/bao_bbn_h0/ledger/README.md` line 37 and `results/eboss_vs_desi/ledger/README.md` line 21 contain "not ... exact rational arithmetic", and the DR1/DR2 READMEs contain no such text.
- The round-1/2 closure mutation tests presuppose the redefinition.

The Table 10 caption carries a note. Limitations adds the re-kinding (for example a `float_harness` kind, or refiling at X) to the out-of-scope ledger list.

### Minor: M6, a sorryAx blob passes the gate. FIXED.
I copied the referee's script to `round3_m6_sorry_blob_mutation.py` and re-ran it on fresh copies under `/tmp/r3resp/m6`. The gate rc was unchanged in 3 of 3 ledgers: 0/0/1 for DR2/eBOSS/H0, the same as the originals.

Sec. 3.5 now says that the gate never parses a `lean_axioms` blob, so the kernel-checked meaning of Tier A rests on the blob's author. It also cites the referee's content-level audit (28 of 28 blobs consistent). That audit was not re-run by me and is attributed. Limitations is updated to match.

### Minor: "not re-tested on z > −1". FIXED.
Sec. 3.4 and Limitations now read "were not tested on z > −1 (the preregistration fixed no domain for them; its z > −1 applies to the positivity statement only)".

### Cosmetic: "(per the round-1 formal referee)". FIXED.
The text now credits the Lean file header and `fixround_diagnostics.json` (`omega_m_threshold`).

The referee's optional item 5 (Sec. 3.4's list omits `chi2_eq_dotProduct_inv_mulVec` and the DR2 nesting identity) was not changed. It is an understatement, not an overstatement.

---

## Novelty / positioning referee (recommendation: minor)

All six papers below were fetched with alphaXiv `answer_pdf_queries` in this session before being cited. The details are in `literature_search_log_round3.json`.

### F1 (major): SHARP and the two Huang papers were not cited. FIXED.
Sec. 5 now opens with SHARP (2604.18752) as the most direct precedent for agent-executed reproduction against numeric targets. The attributes cited are:
- Claude Code with claude-opus-4.6, and a prompt that fixes the target metrics;
- Critic and other subagents, and human checkpoints;
- three runs;
- an external human-written evaluation script;
- truth-label leakage "undetected by automated tests".

Huang 2604.12198 is cited for 111 papers, T1–T4 verdicts, a 12-paper cross-machine check and 75.8% of 571 claims within 5%. Huang 2607.02329 is cited for the pilot reproduction of k = 5 anchors, fresh-context adversarial review "prompted to find rather than confirm", the no-pilot ablation, and "consistency with published literature, not truth". That last phrase is tied to our DESI targets and the DR1 χ² offset.

cmbagent is now named "for cosmology, the most direct precedent". The sentence "faithful reproduction is hard for agents" is replaced by "benchmark results on reproduction are mixed", which contrasts whole-paper benchmarks with pipelines that start from public inputs and a stated method (including ours). Novelty item 1 names SHARP next to JFC.

**Not used:** the referee described a camera-ready "Note added" in 2604.12198 about a human reviewer. That passage was not in the pages returned to me, so it is not asserted.

### F2 (major): 2609.12065 and 2607.28918 were not cited. FIXED.
- **(a) Akharman et al., 2609.12065.** Quoted in Sec. 3.2 and in the "Incoherent H0 tolerances" limitation: h = 0.6833 (+0.0048/−0.0053) with PRIMAT, "up to roughly 0.5σ" across reaction networks, and "the DESI DR2 analysis uses a prior on the baryon density from just one reaction network". The text says this systematic is larger than our strict window. It notes that the σ units differ: theirs is their own σ(h), ours is DESI's σ. It plays no role in the verdicts, and no window was changed.
- **(b) Kim, Mota & Tamosiunas, 2607.28918.** Cited in Sec. 4.5(a) for the explicit nesting model and the per-bin ratios, which "straddle" 1/3 at 0.22–0.49 (median 0.32). The text says σ_nested is an approximation, bracketed by the C = 1 and independent conventions.
- **2602.18761** (optional) was not fetched this round and is not cited.

### F3 (minor): same model family; single execution. FIXED.
The AI-use statement now says that the referees are Claude models reviewing Claude-written work, with 2607.28631 (Gemini–Claude ρ = 0.907, GPT-5.4 ρ ≈ 0.32; verified). It also says each problem was executed once, and that the DR2 regeneration is a fixed-seed re-execution, not an independent agent run.

The same points appear in the abstract's last sentence and in the Limitations items "Tier A is model-audited, by the same model family" and "Single execution per problem".

### F4 (minor): the search log did not cover agentic reproduction. FIXED.
`literature_search_log_round3.json` records my sweep with its exact inputs and its hits. SHARP and 2604.12198 did not appear in my sweep; the log says they came from the referee and were read by id. Sec. 5's search paragraph says the earlier searches missed this axis.

The optional SA-Bench semantic-drift framing was not added. I saw 2608.24252 only as a listing line and did not read it.

### F5 (minor): TOPO missing from Sec. 3.2. FIXED.
It is now cited at the point where the hash-lock is introduced.

### F7 (wording)
- The SHARP sentence is FIXED: "SHARP's prompt does fix numeric targets, without tolerances, controls or a lock".
- The JFC "independent Combine implementation" clause is NOT ADDED. I did not re-fetch JFC Sec. 4 this round.

---

## Remaining open issues (disclosed in the paper)
1. The primary H0 DR1 verdict is environment-dependent: PARTIAL as recorded, PASS on re-run. It cannot be resolved without a longer chain or a deterministic estimator, and either would be a new, non-preregistered analysis.
2. The ledgers' Tier B redefinition, the missing DR1/DR2 README disclosures, and the gate not parsing blob contents (M6) are outside the write scope.
3. The run JSONs do not record their interpreter. The `fit.json` "expected identical" note and the `fit_desi_bao.py` docstring are outside the write scope.
4. A residual Aubourg-vs-CAMB excess of order 1e-5 is untraced.
5. Carried over from earlier rounds: the unexplained DR1 χ² offset, the stale H0 audit hash, the z ≥ 0 drift in the shipped file, the `lean_runner.py` deviation, preregistrations not committed before the fits, no human review, and the repository completion checks not passing.
