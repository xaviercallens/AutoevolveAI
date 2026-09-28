# desi_dr2_bao claim ledger (Elenchus format)

This ledger holds 25 claims in the tier-capped format from `SocrateAI-Scientific-Elenchus` (tiers X < C < L < B < A). Each claim points to a content-addressed evidence blob in `evidence/`. A blob's filename is the sha256 of its exact bytes, and `ledger.py` re-hashes every blob when it checks.

To regenerate:

```
python3 scripts/desi_dr2_bao/build_ledger.py   # rebuilds ledger.json + evidence/ from the regenerated results JSONs
python3 scripts/desi_dr2_bao/check_ledger.py   # runs the gate with controls; writes gate_check.json/.log
```

The gate command, as run:

```
python3 <elenchus>/tools/ledger.py --evidence-dir results/desi_dr2_bao/ledger/evidence results/desi_dr2_bao/ledger/ledger.json
```

## Claims

| Tier | IDs | What the claims cover |
|---|---|---|
| A (`lean_axioms`) | DR2-A-0001..0006 | The six theorems in `formal/ANSE/DESI_DR2_wCDM.lean` (sha256 `3b451bd5…`). Each is kernel-checked and its footprint is exactly `[propext, Classical.choice, Quot.sound]`. Each carries a statement audit from the automated model referee (see below). |
| B (`exact_harness`) | DR2-B-0001..0008 | Our own computations:<br>• DR2 ΛCDM fit<br>• DR2 wCDM fit<br>• positive controls<br>• negative controls<br>• CAMB cross-check<br>• radiation sensitivity<br>• DR1 posteriors<br>• DR1→DR2 shift |
| L (`citation`) | DR2-L-0001..0005 | Published values and priors. Each excerpt is page text fetched with alphaXiv on 2026-09-27. |
| L (`citation`) | DR2-L-0006..0010 | Comparisons of our numbers with published ones: pulls, widths, χ², r, DR1 instrument checks, the shift, and the overall verdict. These rest on citations, so they are capped at L. |
| C (`argument`) | DR2-C-0001 | An argument, by reading, that the Lean definitions match `dr2_model.e_of_z` (with orad = 0) and its distance integral. |

## Gate result (verbatim in `gate_check.log`)

- **Fix-round real run: exit code 0, 25 claims, no findings.** This is because the six Tier A rows now carry `audit` objects.
- **Who audited.** The audits come from the workflow referee's `lean_statement_audit` in `../referee_report.json`, which is saved verbatim from the referee output. The referee judged all six statements faithful.
  - The referee is an automated model, not a person. Every audit object says so, with `by: "... NOT a person"` and `auditor_kind: "model"`.
  - Each audit object carries the referee's comment verbatim, the audited file and its sha256 `3b451bd5…5adc`, and the report's sha256.
  - Elenchus's flag text asks for a person's certification. So rc 0 here means "audited by a model referee", not "audited by a human". A human statement audit is still outstanding.
- **Audit binding.** `build_ledger.py` attaches an audit only when two conditions hold: the Lean file's sha256 equals the audited sha256, and the referee marked that theorem faithful. The build refuses to run if the file has changed.
  - The control is in `audit_binding_control.json`: the genuine sha gives an audit, a changed sha gives null, and an unknown theorem gives null.
- **Pre-audit state (kept).** Before the audits were added, the gate exited 1 with 0 blocks and 6 `LEDGER_UNAUDITED_TIER_A` flags. That run is kept in `gate_check_pre_audit.{json,log}` and `ledger_pre_audit.json`.
- **Positive control.** On the parent `results/bao_flcdm/ledger` the gate gave 0 blocks, plus that ledger's own 3 unaudited-Tier-A flags.
- **Negative controls.** Each ran on a `/tmp` copy, and each was caught with a block and exit code 1:
  - refiling L-0006 as Tier B gave `LEDGER_TIER_INVERSION`;
  - changing one character in the B-0001 blob gave `LEDGER_EVIDENCE_MISMATCH`;
  - filing L-0001 at Tier A gave `LEDGER_KIND_OVERCLAIM`.

## Disclosures carried in the blobs

- **Lean gate (a process deviation).** The gate that ran was `scripts/desi_dr2_bao/lean_gate.py`. It runs `lake env lean` from the shared checkout's `formal/`, reads the in-file `#print axioms` output, rejects `sorryAx`, applies the whitelist, and runs Elenchus.
  - It is not `anse/formal/lean_runner.py`, which the preregistration and CLAUDE.md name.
  - That runner imports the module from a `lake build`, and `ANSE.DESI_DR2_wCDM` has no olean. It also writes `.tmp_axiom_check.lean` into the shared `formal/` directory.
- **Preregistered Lean domain.** `lean_plan` stated E^2 > 0 for z > -1, but E2_pos and E_pos are proved for z >= 0. This domain is strictly narrower, but it still covers every data redshift and the prior box. The file was left unchanged so that the audit applies to exactly the file that was audited.
- **`mcmc_fit.py` edit (closed).** An annotation-only edit at 16:16Z came after the first chains were written. In the fix round all 6 chains and both grids were regenerated from the current scripts, and every chain came out bit-identical (`../fixround_rerun_check.json`).
- **Source values.** The DR1 wCDM r_d·h = (101.7 +2.9/−3.5) Mpc value (2404.03002v3, printed p.36) was re-fetched with alphaXiv in the fix round. Its excerpt is in L-0004. The Table V wCDM row was read in v3 only.
- **Prior source.** That `[38]` = 2404.03002 is inferred from context (DR2-L-0005).
- **NC5.** NC5 passes only in aggregate: 6 of the 20 single scrambled-covariance fits have PTE > 1e-3 (see B-0004).
