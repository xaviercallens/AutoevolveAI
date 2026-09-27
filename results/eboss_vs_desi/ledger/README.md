# eboss_vs_desi claim ledger (Elenchus format)

There are 27 claims in `SocrateAI-Scientific-Elenchus`'s tier-capped ledger format (X < C < L < B < A), with the same schema as `results/bao_flcdm/ledger/`. Each claim has a content-addressed evidence blob in `evidence/`. A blob's filename is the sha256 of its exact bytes, and `ledger.py --evidence-dir` recomputes that hash rather than trusting the name.

Built by `scripts/eboss_vs_desi/build_ledger.py` (ledger + paper stage, 2026-09-27). Every number is read from the regenerated result files: `fit.json`, `positive_control.json`, `negative_controls.json`, `instrument_check.json` and `camb_crosscheck.json`. None was retyped by hand. The build fails in four cases:
- the Lean source's sha256 is no longer `560e3b5d8266a2e2…` (the file as compiled in the round-2 fix stage, after a docstring-only edit to `tension1D_eq_zero_iff`; the Lean stage's version was `bafdfab48eba8d67…`);
- the saved diff between those two versions (`../lean_BAO_Consistency_fixround2_docstring.diff`) touches a declaration or proof line;
- the Lean compile log `../lean_BAO_Consistency_compile_fixround2.log` is not clean (needs `rc=0`, no `sorryAx`, no `error`), or a footprint is not exactly the trusted set;
- `preregistration.json` no longer matches the sha256 recorded in `fit.json`;
- a citation quote is not a verbatim substring of `docs/literature/EBOSS_VS_DESI_LITERATURE_REVIEW_2026.md`.

| Tier | Kind | Claims | Content |
|---|---|---|---|
| A | lean_axioms | EVD-A-0001..0009 | The 9 theorems of `formal/ANSE/BAO_Consistency.lean`. Each has footprint exactly `[propext, Classical.choice, Quot.sound]` in `../lean_BAO_Consistency_compile_fixround2.log` (exit 0). Each row carries an audit object from the round-2 automated model referee (`auditor_is_person: false`, `human_audit: "open"`); see below. |
| B | exact_harness | EVD-B-0001..0008 | DESI DR2 fit, SDSS baseline fit, SDSS Gaussian-summary variant, tension statistic, positive control, negative controls, instrument check, CAMB background cross-check |
| L | citation | EVD-L-0001..0005 | Published values and statements (arXiv:2007.08991, 2503.14738, 2404.03002) |
| L | citation | EVD-L-0006..0008 | Comparisons of this run's numbers with published ones: the pulls, the secondary-sourced SDSS h r_d pull, and "N_sigma < 2 agrees with DESI's qualitative claim". These rest on L citations, so they are capped at L. |
| C | argument | EVD-C-0001 | "N_sigma is a lower bound with respect to survey overlap, provided K + K^T is PSD". A Loewner-order argument that uses the cited C ≈ 0.57; K itself was not estimated. |
| C | argument | EVD-C-0002 | "The Lean definitions are the statistic `bao_lib.tension` computes". This is a reading of the code against the Lean statement, not a kernel fact. |

"exact_harness" here follows the `bao_flcdm` template: a seeded, re-run numerical harness whose inputs are sha256-verified. It is not exact rational arithmetic. The emcee moments are Monte Carlo estimates, and the grid and MAP cross-checks agree with them to about 0.02 sigma.

## Gate output (real, this stage)

Round-2 fix stage (after the Tier A audits below were recorded):

```
python3 .../SocrateAI-Scientific-Elenchus/tools/ledger.py --evidence-dir results/eboss_vs_desi/ledger/evidence results/eboss_vs_desi/ledger/ledger.json
  27 claims checked, no findings. (Bookkeeping only: this licenses nothing.)
rc=0
```

Before this stage (ledger + paper stage, every Tier A `audit: null`) the same command gave 0 block findings, 9 `LEDGER_UNAUDITED_TIER_A` flags, rc=1.

### What the Tier A audits are, and what they are not

- The orchestrator's fix-round instruction was to record the round-2 referee's Lean statement audit in the ledger: an audit object on each Tier A row the referee judged faithful, naming the referee as auditor, and null otherwise. The referee judged all 9 statements faithful (`../referee_report_round2.json`, `lean_statement_audit`), so all 9 rows now carry an audit object.
- **The auditor is an automated model referee, not a person.** Each audit object says so (`auditor_is_person: false`, `human_audit: "open"`). Elenchus's own doctrine (`docs/VALIDATION.md` §5.3) describes the Tier A audit as a person reading the statement. So rc=0 here means "a model referee read the statements against the code and judged them faithful". It does **not** mean a human audit took place. That audit is still open.
- The referee audited source sha256 `bafdfab48eba8d67…`. The only change since then is the docstring rewording it asked for, on `tension1D_eq_zero_iff`. `build_ledger.py` refuses to carry the audit over if the saved diff touches any declaration or proof line.
- **How this differs from the earlier attempt (round-1 fix round, `../fixround_outcomes.json` item 7c).** That attempt copied audits from the round-1 report (`../referee_report.json`). The round-1 report predates the regenerated fit (17:10Z) and the final Lean source (17:58Z), and the ledger + paper stage correctly removed those audits. The round-2 report was written against the current statements and reproduces the current fit numbers.
- Mutation 4 below shows that the rc=0 depends on these recorded audits. Remove one and the flag comes back.

## Gate negative controls (`gate_check.json`, `scripts/eboss_vs_desi/ledger_gate_check.py`)

Four hand-built mutations of this ledger, all caught. Mutations 1-3 each raised a block finding. Mutation 4 raised the unaudited flag with rc=1. The real ledger has 0 findings, rc=0.

1. EVD-L-0006, a comparison with published values, was refiled as Tier B `exact_harness`. The gate returned `LEDGER_TIER_INVERSION`.
2. One byte was changed in the evidence blob of EVD-B-0001. The gate returned `LEDGER_EVIDENCE_MISMATCH`.
3. EVD-L-0002, a citation, was refiled as Tier A. The gate returned `LEDGER_KIND_OVERCLAIM`. It also returned `LEDGER_ORPHAN`, because the renamed id broke EVD-L-0006's dependency, plus `LEDGER_UNAUDITED_TIER_A`, because the new Tier A row has no audit.
4. The audit object of EVD-A-0004 was removed. The gate returned the `LEDGER_UNAUDITED_TIER_A` flag, rc=1.

The gate therefore discriminates on this ledger's content, and its zero block count means something.

## Provenance records the frozen preregistration cannot carry

- **Amendment time.** `preregistration.json`'s field `timestamp_last_amended_utc` reads 15:58Z. The file's own last-modified time on disk is **2026-09-27T15:54Z**, so the field is not the actual write time, and this index records 15:54Z as the amendment time. The frozen file is not edited (sha256 `e0eca89f…`, matching `fit.json`). `prereg_inputs.json` (15:53Z) already contains the literature-only computation behind amendment (a). The first control output of the interrupted run was written at 15:59Z.
- **Lean module rename.** The preregistration planned `formal/ANSE/BAO_TensionStatistic.lean`, which covered only the diagonal case. It shipped as `formal/ANSE/BAO_Consistency.lean` (namespace `ANSE.BAOConsistency`), which covers the full 2x2 covariance and the link to Mathlib's matrix inverse. It is not yet imported from `formal/ANSE.lean`; the line to add is `import ANSE.BAO_Consistency`.
