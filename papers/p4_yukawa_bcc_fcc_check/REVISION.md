# REVISION of M3 after the independent audit (AUDIT.md, ACCEPT_WITH_CORRECTIONS, no blocking item)

Revision by the producer lane, 2026-10-27. Nothing committed, pushed or published. No third-party text added to tracked paths.
Result: `main.pdf` 12 pages (pdflatex twice: 0 errors, 0 undefined references; one 12.8 pt overfull hbox in the new table, harmless).
Ledger gate (`ledger/run_gate.py`): **exit code 1**, 0 blocking, 8 x LEDGER_UNAUDITED_TIER_A (unchanged; the flags stay because no person has certified the glosses).

## Items

1. **Lemma A.3 endpoints (NONBLOCKING 1).** Applied. Section 5 paragraph retitled "outward-rounded, not a near-tie"; the "look like double-rounded
   logarithms ... could be misled" sentences are replaced by the auditor's text (numerators 4.2, 1.05, 2.5 units beyond the exact logarithms in the safe
   direction; 11/25 and 147/1000 intermediate with slack about 3e-3 and 5e-4 in Prop. 3.1; only beta tight). Ledger YBC-C-0006 rewritten likewise.
   publication_meta.json "Observation worth a human look" replaced.
2. **"Seventeen finite statements" (NONBLOCKING 2).** Applied. Title now "seventeen Lean statements kernel-checked"; abstract says seventeen Lean theorems,
   ten substantive and seven bridge lemmas or one-line rational facts (`Nc_eq_ncard`, `Mc_eq_ncard`, `lemmaA1_rational`, `lemma61_pb_lt`, `lemma61_a2_gt`,
   `lemma61_prop41_bracket`, `lemmaA6_tail`), says `lemma61_prop41_bracket` is a for-all-x statement, and writes "the BCC multiplicities at the 17 nonzero
   indices" so the two 17s are separated; Section 6 repeats the split and states that the two 17s are unrelated.
3. **Weaker Lean statements (NONBLOCKING 3).** Applied: new Table "Lean statements weaker than, or only linked to, the printed ones" in Section 3 after
   "How to read a Tier A line" (exp_fcc_21 at t = 21/10 only; prop41_bracket rational bracket only; tail_* partial sums of the rational majorants;
   lemmaA5_* over box counts via `Nc_eq_ncard` (n <= 12) / `Mc_eq_ncard` (l <= 48); plus lemmaA6_tail and lemmaA1_rational), and a pointer from the abstract.
4. **Reproducibility (NONBLOCKING 4).** Applied. Commands now carry their positional arguments and full paths from the repository root
   (`m3_shells.py 4200 OUT`, `m3_arb.py SHELLS OUT`, `m3_float.py SHELLS OUT`, `m3_extra.py SHELLS OUT`, `emit_lemmaA5.py OUT_DIR`). `m3_arb.py:25`'s
   hard-wired path resolves to `.claude/worktrees/.scratchpad/b2_pylib` from this location; the scripts were NOT edited (hashes in `data/result.json` stay valid).
   Instead a small new launcher `data/code/with_flint.py FLINT_DIR SCRIPT ARGS...` extends `sys.path` under `python -I` (which ignores PYTHONPATH and the user site).
   Tested from a scratch copy in /tmp/m3rev laid out like the repository (nothing installed): shells (0.3 s), Arb with the worktree's `.scratchpad/b2_pylib`
   (python-flint 0.6.0) under the venv python (4 s), Arb under system `python3 -I` with python-flint 0.9.0 from `~/.local/lib/python3.10/site-packages` (5 s, completed),
   `m3_float.py` (mpmath, several minutes, exit 0), `m3_extra.py` (completed), `emit_lemmaA5.py` (slacks A.6 7.5214e-4, A.7 7.6459e-5, A.8 0.1430 as printed; its OUT is a
   directory). The Lean compile commands were not rerun in this revision (the producer and the audit each ran them); the `--olean Programmes.YukawaBccFcc.<Module>` form was
   added to the printed command and is untested here. Availability note on python-flint added (not in the venv; producer 0.6.0 untracked in `.scratchpad`; auditor 0.9.0 in ~/.local).
5. **IEEE-double wording (NONBLOCKING 5).** Applied in abstract, Section 5, results table (X-0001), limitations, ledger X-0001, meta: 11 digits describes the producer's
   direct sum; the audit's float64 Ewald reaches about 12; double precision cannot resolve the 1e-15 enclosure (rounding 1e-16 moves kappa* by about 1e-12).
6. **Lean route deviation (NONBLOCKING 6).** Disclosure kept; added that the equivalent checks (compile, `#print axioms`, sorryAx rejected, whitelist) were rerun by the audit.
7. **Stale status lines (NONBLOCKING 7).** Replaced everywhere: disclosure paragraph, abstract Tier A, Section 3 table caption, open-items list, ledger section ("There is no AI audit"),
   limitations ("leanchecker replay was run by the producer"), reproducibility timings, `ledger/build_ledger.py` STATUS/ADEQ, `publication_meta.json` description and notes.
   New text: independent AI audit, ACCEPT_WITH_CORRECTIONS, no blocking item; no human audit; no statement lock; audit kappa* = 1.71792186846990386425087416660628171879468538
   (70-digit Ewald, free splitting parameter, eta = 1 and 1.3 agree to < 5e-70, matches direct sum at kappa = 6); Lemma A.6 signs reproduced in an independent interval run
   (python-flint 0.9.0); all 138 declarations of the five modules print only {propext, Classical.choice, Quot.sound} (127 / 2 / 1 / 8 split stated); leanchecker rc 0 on
   Basic/Shells/Chains/LemmaA5/Lemma61 with the auditor's times (59.3, 168.1, 89.7, 1091.2, 55.7 s); oleans byte-identical to the producer's; RejectWitness agreed decisive
   (new text in the controls remains as is; the audit's agreement is recorded in the ledger STATUS and in `AUDIT.md`).
   Ledger: the AUDIT.md allows recording the AI audit only if the convention allows; following the sibling DAC paper's convention, the gate field `audit` stays `null`
   (a person has not certified) and a new `ai_audit` object (auditor, human=false, report, verdict, kernel_replay, revision, note) is attached to each Tier A row; the audit's replay
   file is added to the Lean evidence blobs; ledger rebuilt (21 claims, 21 evidence blobs) and the gate rerun: exit code 1, unchanged flags.
8. **"22 digits" (NONBLOCKING 8).** Applied: (E) and (Q) agree to all 25 printed digits and (D)'s interval of width about 4e-24 contains both; the audit's fourth value is cited in a new
   paragraph. Changed in abstract, Section 5, results table, ledger C-0001, meta.
9. **A.4 / ancillary files (NONBLOCKING 9).** Applied: the date of the arXiv check (2026-10-27, v1 only, no ancillary-file section) and the paper's own p. 4 statement that the data
   accompany the manuscript are given; "we intend to ask the authors for the data" is stated as a plain intention (no request has been sent). Also in abstract and meta.
10. **Bibliography (NONBLOCKING 10).** No change needed (audit confirmed). 11. **"What this is NOT" box** unchanged (audit: accurate).

## Not done / caveats
- Lean modules were not recompiled in this revision (no Lean source changed). Statements in `data/lean/` untouched.
- No human audit, no statement lock; the 8 gate flags remain by design.
- Overfull hbox of 12.8 pt in the weaker-statements table remains.
- Scratch files for testing the recipe are in /tmp/m3rev (outside the repository).
