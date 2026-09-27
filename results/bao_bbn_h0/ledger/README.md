# bao_bbn_h0 claim ledger (Elenchus format)

The ledger holds 43 claims in `SocrateAI-Scientific-Elenchus`'s tier-capped format (X < C < L < B < A). It uses the same schema as `results/bao_flcdm/ledger/`. Every claim has a content-addressed evidence blob in `evidence/`. A blob's filename is the sha256 of its exact bytes, and `ledger.py --evidence-dir` recomputes that hash rather than trusting the name.

`scripts/bao_bbn_h0/build_ledger.py` builds it (last rebuilt in the referee fix round, 2026-09-27). Every number comes from regenerated result files: `fit.json`, `controls/*.json`, `rd_camb_validation.json`, `anchor_reproduction.json`, `chains_pointer.json`, `fixround_diagnostics.json`, the Lean re-check log and the Elenchus log. None was retyped. The fix round re-ran the Lean compile and Elenchus (`scripts/bao_bbn_h0/lean_recheck.py`) on the revised Lean file before building.

The build refuses to run if any of these holds:
- A hash lock has drifted. The locks are:
  - the Lean source (`2b653083…`, fix-round revision);
  - `preregistration.json` (must equal `fit.json.preregistration_sha256`);
  - amendment 1 (`b0c7b80d…`);
  - the locked pre-amendment fit (`b7fe5608…`);
  - the CAMB r_d table (must equal `fit.json.rd_camb_table_sha256`).
- The Lean re-check log is not clean, or it was produced from a different source hash.
- The Elenchus log does not say `no findings` with `elenchus_rc=0` for the same source hash.
- The Lean theorem list changed.
- A citation quote is not a verbatim substring of `docs/literature/BAO_BBN_H0_LITERATURE_REVIEW_2026.md`.
- The `common.py` lines quoted by the Tier C claim are missing.

| Tier | Kind | Claims | Content |
|---|---|---|---|
| A | lean_axioms | BBNH0-A-0001..0010 | All 10 theorems of `formal/ANSE/BAO_BBN_H0.lean`. Each has footprint exactly `[propext, Classical.choice, Quot.sound]`, from the fix-round compile (`../lean_compile_5_fixround.txt`, rc=0, source sha256 `2b653083…`). Elenchus `elenchus_check.py` reported `no findings` (`../elenchus_check.txt`). A-0001..0008 carry a MODEL referee's audit (see below); A-0009/0010 (the identifiability theorems added in the fix round) have `audit: null`. |
| B | exact_harness | BBNH0-B-0001..0004 | Primary (CAMB r_d) and secondary (Aubourg eq. 16) BAO+BBN fits on DESI DR2 (T1) and DR1 (T2) |
| B | exact_harness | BBNH0-B-0005..0006 | BAO-only (Omega_m, h r_d) gate fits G1 (DR2) and G2 (DR1) |
| B | exact_harness | BBNH0-B-0007..0009 | CAMB r_d table vs direct CAMB; CLASS vs CAMB and eq. 16 vs CAMB; analytic background vs CAMB background and vs astropy (P4) |
| B | exact_harness | BBNH0-B-0010..0011 | Positive controls P1, P2 and negative controls N1, N2, N3, each for both analyses |
| B | exact_harness | BBNH0-B-0012 | Measured primary minus secondary ΔH0, plus sensitivity runs S1 to S3 |
| B | exact_harness | BBNH0-B-0013 | Bit-identical re-run of the hash-locked pre-amendment fitting-formula output. This shows reproducibility, not independent correctness. |
| B | exact_harness | BBNH0-B-0014 | CAMB r_drag at the Planck 2018 Table 1 best-fit inputs (N_eff = 3.046) |
| B | exact_harness | BBNH0-B-0015 | CAMB and CLASS at the Planck 2018 Table 2 lensing means: reproduction of the amendment's 147.1027 / 147.0971 anchors, and CLASS at matched N_eff |
| B | exact_harness | BBNH0-B-0016 | Fix-round diagnostics: numerical h·r_d(h) monotonicity (CAMB table and eq. 16), the threshold below which it fails, d ln(h r_d)/d ln h, and the CAMB table's h dependence |
| B | exact_harness | BBNH0-B-0017 | Post-hoc control N4 (not preregistered): a neutrino-bookkeeping error in r_d shifts H0 by +0.164 with Δχ² ≈ 5e-5 |
| L | citation | BBNH0-L-0001..0007, L-0014 | Published values: the DR2 and DR1 DESI+BBN targets, both BAO-only gates, the BBN prior, Aubourg eq. 16 and its stated accuracy, the Planck 2018 best-fit r_drag and posterior r_drag |
| L | citation | BBNH0-L-0008..0013, L-0015 | Comparisons with the published numbers: primary T1 PASS (headline), primary T2 PARTIAL, secondary verdicts, gate pulls, the CAMB anchors, the measured eq. 16 deviation, and the T2 h r_d propagation (heuristic). They rest on L citations, so they are capped at L. |
| C | argument | BBNH0-C-0001 | "The Lean definitions are what `common.py` computes." This is a reading of the code, not a kernel fact. It includes a caveat: the h·r_d-only dependence is exact only at fixed E(z). In the BBN fits, E depends on h through the radiation term. |

"exact_harness" follows the earlier templates. It means a seeded numerical harness, re-run, on sha256-verified inputs. It does not mean exact rational arithmetic. The emcee moments are Monte Carlo estimates.

## Gate output (real, 2026-09-27, `ledger_check.txt`)

```
python3 .../SocrateAI-Scientific-Elenchus/tools/ledger.py --evidence-dir results/bao_bbn_h0/ledger/evidence results/bao_bbn_h0/ledger/ledger.json
  flag  LEDGER_UNAUDITED_TIER_A    BBNH0-A-0009
  flag  LEDGER_UNAUDITED_TIER_A    BBNH0-A-0010
rc=1
```

- **There are zero block-severity findings.**
- **The exit code is 1.** `ledger.py` returns 1 whenever any finding exists, flags included.
- **Audit provenance.** Per the fix-round instruction, A-0001..0008 carry an `audit` object from the fix-round model referee, which judged all 8 statements faithful (`referee_statement_audit_fixround.json`, transcribed from the orchestrator-supplied report). Its `by` field reads "model referee …; NOT a person". Elenchus `ledger.py` describes an audit as a person's certification ("audit must be an object or null; it is never a model"), so the missing flags on these rows mean *model-audited*, not human-audited. No person has audited any statement.
- The referee's 'at fixed E' caveat for A-0006/0007 is recorded in both the audit comment and the revised glosses.
- A-0009/0010 were added after the review, so they keep `audit: null`. Those are the two open flags.
- `referee_statement_audit.json` is an older model review from an interrupted attempt. It is not used.

## Gate negative controls (`gate_check.json`, `scripts/bao_bbn_h0/ledger_gate_check.py`, re-run on this ledger)

Three hand-built mutations were each caught with a block finding:

1. BBNH0-L-0008, the headline PASS, which is a comparison with a published number, was refiled as Tier B. The gate returned `LEDGER_TIER_INVERSION`.
2. One byte of BBNH0-B-0001's evidence blob was changed. The gate returned `LEDGER_EVIDENCE_MISMATCH`.
3. BBNH0-L-0001, a citation, was refiled as Tier A. The gate returned `LEDGER_KIND_OVERCLAIM`. It also returned `LEDGER_ORPHAN`, because the renamed ID broke the claims that depend on it.
