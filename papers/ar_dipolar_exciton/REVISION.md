# Stage-5 revision: lane H1 (ar_dipolar_exciton)

Producer revision of 2026-10-25, done in response to the stage-4 independent AI audit (`AUDIT.md`, verdict
ACCEPT_WITH_CORRECTIONS, no blocking findings). Every correction was applied; none was declined. AUDIT.md, `audit/`
and the auditor's probe `formal_cert/Autoresearch/DipolarExcitonAuditH1Controls.lean` were not edited.

## Corrections and resolutions

| id | correction | resolution |
|---|---|---|
| C1 | Non-vacuity is proved for g_d only, not for the shiftDiff family; at c = 0 the family is identically 0 | Abstract now reads "For g_d (d>0) we also prove that the optimal energy is finite ... no finiteness theorem is proved for the rest of the family". New Remark "scope of non-vacuity" after Step 9 says that at c = 0 the family statement is the trivial 0 <= energy. Listing caption of the density theorems says "non-vacuity for g_d". publication_meta bullet qualified to "for g_d (d > 0) only". Ledger DX-A-0009 statement carries the same note. |
| C2 | The Multipolar module is no longer producer-checked only | Tiers paragraph, Lean section, both listing captions, Limitations and publication_meta now say that it was re-elaborated from source by a separate AI auditor at stage 4 (rc 0 in 56.9 s; allowlist axioms; the auditor's planted sorry and planted axiom caught). "No human audit" is kept everywhere. `MULTI_STATUS` in `ledger/build_ledger.py` points to `audit/recompile_multipolar_src.json`, `audit/audit_controls.json` and AUDIT.md. The sentence that the paper-stage reruns do not separate producer from verifier is kept, because it is still true of those reruns. |
| C3 | "two to five orders" is too strong at the low end; meV values use the gap at the simulated d_tilde | Text now reads "about 1.5 to 5 orders of magnitude below the moire depths of 10s-100 meV". A new sentence says the meV values multiply the physical d_tilde^2 by the gap taken at the nearest simulated d_tilde (0.0209, 0.066, 0.114), and quotes the auditor's 0.224 meV at d_tilde = 0.1143 (a 0.5% difference). Nothing was re-run; the printed values (0.0014, 0.0438, 0.223 meV) still come from `data/summary.json`. Ledger DX-X-0007 and publication_meta carry the same wording. |
| C4 | (withdrawn by the auditor: co/co_0.parquet is the only shard) | No change needed. |
| C5 | 7 of the 21 competitors are designed negative controls; anneal_01 and uniform_04 end in the same state | New generated macros `\DXNOpen` = 14 (12 quenches + 2 anneals) and `\DXNDesignedNeg` = 7 (`gen_inputs.py`, counted from `summary.json`). Used in the abstract, the P1 paragraph and Limitations. The duplicate final state was checked against `data/main_d0.066.jsonl` before writing: e_exact 4.439367455732614 (uniform_04) and 4.439367455732605 (anneal_01), psi6_global 0.998112 for both. The paper now says that there are fewer independent outcomes than runs. Ledger DX-X-0004 and publication_meta updated. |
| C6 | Killed first attempts at d_tilde = 0.0209 and 1 not disclosed in the paper | One sentence added to the P1 caveats (wording from NUMERICS.md: killed after about 34 min for budget, finished jobs never printed because the driver kept them in memory, rerun with 2 quenches each with the patched driver 916fc88). Also in ledger DX-X-0004. |
| C7 | Switch from preregistered image-sum-plus-tail to Ewald energies not labeled as a deviation | §num Method now says "Deviation from DIP-TRI-1: the preregistered reported_potential was the periodic image sum to radius R plus the analytic uniform tail; we report Ewald energies instead", with the reason (non-monotone truncated residual, Figure 2 right). Also in Limitations, ledger DX-X-0004 and publication_meta. |
| C8 (optional) | Move the auditor's `audit_g_sqrt` into a claimed module | Done, as a new claimed module so that the two audited modules keep their sha256 values. `formal_cert/Autoresearch/DipolarExcitonStep1.lean` (namespace `AutoresearchDipolarStep1`): `g_sqrt` (the auditor's proof, moved unchanged), `g_inplane` (r form, via `Real.sqrt_sq`), `g_inplane_pos` (positivity for d != 0, r > 0). Compiled with pinned Lean 4.34.1 to `formal_cert/.olean_out/Autoresearch/DipolarExcitonStep1.olean`: rc 0 in 22.7 s (`results/autoresearch/2026-10-25/H1/contribution/compile_step1.json`). `grep -c sorry` = 0. Planted controls in the separate file `DipolarExcitonStep1Controls.lean` (rc 0 in 16.4 s, `compile_step1_controls.json`): `ctl1_sorry` gives [sorryAx], `ctl1_axiom` gives [AutoresearchDipolarStep1Controls.ctl1_cheat], `ctl1_wrong_sign_false` (the wrong-sign in-plane form is false at r = d = 1) and the three claimed theorems give [propext, Classical.choice, Quot.sound]. New ledger rows DX-A-0013 (the identity) and DX-A-0014 (its controls); DX-C-0001 is narrowed to the physical pair counting and now depends on DX-A-0013. Step 1 of the human demonstration, the abstract, a new Listing and the reproducibility list (two new sha256 values) were updated. The module is producer-checked only, and the paper says so. |

## Other items from the audit

- **eta-independence slip (producer note).** NUMERICS.md said "at most 1.5e-13"; recomputed from `data/references.jsonl`
  it is 1.3186e-13. Fixed in NUMERICS.md (with an erratum note) and in ledger row DX-X-0001, which had the same slip.
  The paper already printed 1.3e-13 (generated macro).
- **d_tilde -> 0 limit.** The paper said it had not compared 4.4462 with a closed form. It now also cites the auditor's
  independent Epstein-zeta check (`audit/audit_epstein_check.py`), which reproduces e_tri and e_sq at four d_tilde to
  about 1e-13 relative and gives the exact limit 4.446373. This is still Tier X and still not a literature comparison.
- **Crate tests not re-run by the auditor.** I tried to re-run `cargo test -p qf-yukawa-crystal` in this revision. The
  worktree-isolation guard of this session refused it as well ("this session is isolated in the worktree ..."), so the
  28 passed / 0 failed / 1 ignored figure still traces only to `contribution/rerun_cargo_test_paper_stage.txt`. The
  Limitations item says so.
- **rusty-SUNDIALS.** No code or result changed in this revision; no new commit. The branch
  `physics/ar-dipolar-exciton-2026-10-25` stays at 272a09e62c1b9b36eabc167cdafaa2845fbe9198 (not pushed).

## Rebuild

1. Lean: the two compiles above (Step1 with `--olean Autoresearch.DipolarExcitonStep1`, then its controls).
2. `python -I ledger/build_ledger.py`: 33 claims (14 A, 4 L, 7 C, 8 X), 33 evidence blobs.
3. `python -I ledger/run_gate.py`: 14 `LEDGER_UNAUDITED_TIER_A` flags, 0 blocking, exit code 1
   (`ledger/gate_output.txt`). The 2 extra flags are the two new Tier A rows; no person has audited their statements.
4. `python -I gen_inputs.py`: 71 macros, Lean sha256 values match (both the stage-1 set and the revision set).
5. `python -I build_pdf.py`: aux files removed, pdflatex run twice: 14 pages, 0 undefined references, 0 overfull hboxes.

## Files changed by this revision

- `papers/ar_dipolar_exciton/`: `main.tex`, `main.pdf`, `gen_inputs.py`, `gen_numbers.tex`, `gen/step1.{lean,lst}`,
  `gen/axioms_step1_controls.txt` (and the other regenerated `gen/` files, unchanged in content),
  `ledger/build_ledger.py`, `ledger/ledger.json`, `ledger/evidence/`, `ledger/gate_output.txt`,
  `publication_meta.json`, new `build_pdf.py`, new `REVISION.md`.
- `formal_cert/Autoresearch/DipolarExcitonStep1.lean`, `DipolarExcitonStep1Controls.lean` (new).
- `results/autoresearch/2026-10-25/H1/contribution/`: new `compile_step1.json`, `compile_step1_controls.json`;
  `NUMERICS.md` (eta erratum). The refused cargo attempt wrote no file.
