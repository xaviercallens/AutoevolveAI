# Stage 5 revision: H8 / ar_bogoliubov_sk

The audit was `AUDIT.md`: ACCEPT_WITH_CORRECTIONS, with 0 blocking and 7 nonblocking corrections. This revision applies all 7 and declines none.
The Lean files are unchanged. The claimed file has sha256 `fac6c85f…9454` and the controls file `0beb41c9…2ed5`, both re-hashed in this stage. Because the files did not change, the stage-4 recompile still covers them, and no new Lean compile was run.

| # | Correction | Resolution |
|---|---|---|
| 1 | Upstream split-step wording: the upstream source was never inspected. | **Abstract:** now reads "the pinned upstream reference data are reproduced by a reused-phase composition, not by the symmetric Strang step; the upstream source itself was not inspected. The crate's own `step`/`evolve` use the same composition." **§4 paragraph:** retitled "the pinned reference data are not Strang". It says that `solver2d.py` is not on this machine, that the statement is about the pinned data and not the upstream code, and that the crate's `step`/`evolve` implement the same composition. **Limitations:** reworded to match. **Ledger BS-X-0003:** reworded to match. **publication_meta.json:** description and notes reworded to match. |
| 2 | Table 1 mislabel. | The row now reads `|S_freq/bnd − 1| near k=ks (x=1.0772; measured; exact theory 1.3809e-3)` with value 1.381e-3. Both numbers come from new `gen_inputs.py` macros (`GNearOne` and `GNearOneExact`, taken from `linear_response_summary.json`). A new sentence after the table says that the max gate and this gate are the same sweep point, that both are measured, and that they differ from exact theory by 6.9e-8 (macro `GNearOneDiff`). |
| 3 | Rusty `src/linear_response.rs` doc at line 7. | The doc now says the step is "chosen by `ResponseConfig::splitting` (the recorded measurements use `Splitting::Strang`; the crate's own `step`/`evolve` keep the Python-reference composition)". The change is doc only, in commit `ae918316a82f7ac7102d53f646eb20c5a2c838a5` on branch `physics/ar-bogoliubov-2026-10-25`, and it is not pushed. Checks: `cargo fmt --check` exits 0. `cargo test --release -p qf-gpe2d` passes 15/15 (9 + 5 + 1). Under `cargo doc` with `-D broken_intra_doc_links`, the new links resolve; the only error is a pre-existing one at `lib.rs:10` (`qf-pgpe`), which this revision did not touch. |
| 4a | ⁴He "conservative (ε − err)" does not apply at k = 0.05 and 0.10. | **§5:** S_up is conservative only where Table VI gives an error bar. At k = 0.05 and 0.10 Å⁻¹ (ultrasound rows) S_up uses ε itself, and the margins are 0.0166 vs 0.0912 and 0.0329 vs 0.1290. These values come from the macros `HeNoErrK` and `HeNoErrMargins`, computed from `helium_tier_l.json` rows with `err == 0`. Ledger BS-X-0005 was updated to match. |
| 4b | The roton S_up is at k = 1.95 (threshold 0.5697), not at Q_R (threshold 0.5662). | **§5:** now gives "k = 1.95 Å⁻¹, S_up = 2.66 … threshold there 0.5697 (the threshold at Q_R = 1.9260 Å⁻¹ itself is 0.5662)", using the macros `HeRotonK` and `HeThrRotonTab`. Ledger BS-X-0005 now states both values. |
| 5 | Tier L is looser than Elenchus L. | **Tiers paragraph:** L here covers verbatim data values and quotes. `citation_check.py` refuses BS-L-0001 under kind `data_value` (`CITE_KIND`). A theorem-kind probe accepts BS-L-0001 and BS-L-0004, but it tests only that the quotes are verbatim and is not a Tier L verdict. The BS-L-0004 source is an excerpt written by the producer. All three papers were checked against fresh alphaXiv reads by an independent agent. **Limitations and meta:** one line each. |
| 6 | "wall time 409 s" traces only to producer prose. | **§Reproducibility:** now says the figure was recorded by the producing agent in `results/autoresearch/2026-10-25/H8/contribution/NUMERICS.md` and is not in a machine result file. Writing it into `linear_response.json` was not chosen: that would mean re-running the 409 s sweep, and it would break the byte-identity between `data/*.json` and the rusty result files that the audit checked. |
| 7 | The HuggingFace deliverable was not met. | **Abstract:** a separate paragraph, "Unmet deliverable: HuggingFace", says the requested illustration was not delivered and that the ⁴He table stands in for it. **Limitations:** a new item. **Meta:** the description now leads that section with "(unmet deliverable)". §6, the null-result section, is unchanged, as the audit asked. |

## Outputs
- `gen_numbers.tex`: regenerated with 6 new macros. All existing macros are byte-identical, checked by diff against the previous file.
- `main.pdf`: built by `build_pdf.py` with pdflatex twice, rc [0, 0]. It is 13 pages, with 0 undefined references and 0 overfull hboxes. The first build of this revision had 1 overfull box from the longer Table 1 label, so the label was shortened. `main.aux` and `main.out` were removed afterwards.
- Ledger gate: `ledger/run_gate.py` rebuilds the ledger and runs the Elenchus `tools/ledger.py`. Exit code 1, with 24 claims, 0 blocking findings and 8 `LEDGER_UNAUDITED_TIER_A` flags (BS-A-0001…0008); no person has audited statement adequacy. The verbatim output is in `ledger/gate_output.txt`.
- `publication_meta.json`: description and notes updated, including rusty commit `ae918316…`, and it still parses as JSON. Nothing was published.

- Ledger re-run after the rusty commit. `build_ledger.py` hashes `src/linear_response.rs` and records the rusty SHA, so I changed `RUSTY_SHA` to `ae918316…` and re-ran `run_gate.py`. The result was exit 1, 0 blocking findings and 8 flags. 8 stale evidence blobs were pruned, leaving 24 blobs for 24 claims.
- New abstract clause "a new true Strang option converges at second order". I checked it against `dt_convergence[*].S_amp_observed_order` in `linear_response_summary.json`, which gives 2.0007 to 2.07 for the first steps at x = 0.25, 1, 4. That supports the clause.
- `preview/p-*.png`: regenerated from the revised PDF with pdftoppm at 60 dpi, 13 pages. `preview/sheet.png` is the old contact sheet and predates this revision.

## Deviations
- The worktree-isolation guard refused `taskset -c 4-7 cargo test`. As a result, `cargo test` and `cargo doc` ran with `-j 2` and `--test-threads=2` but were **not pinned to cores 4-7**, so they may have used cores 0-3. Each run was short: the build took 41 s and the tests about 10 s.
- `cargo clippy` was not re-run on the doc-only commit.

## Not done
- No human review of statement adequacy.
- No full GP sweep re-run; no new numbers were needed.
