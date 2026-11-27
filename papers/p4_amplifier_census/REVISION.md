# REVISION of C1 (papers/p4_amplifier_census), v1 after the independent audit

Source: `AUDIT.md` (independent AI audit agent, ACCEPT_WITH_CORRECTIONS, nothing blocking) and `data/leanchecker_replay_audit.json`.
Nothing was committed, pushed or published. Historical result files (`data/census_*.json`, `data/logs/*`, `data/result.json`,
`data/controls.json`, etc.) were not altered. Only `main.tex`, `main.pdf`, `publication_meta.json`, `ledger/*`, the census script copy
`data/code/census_enclosure.py`, and wording in `data/RESULT.md` changed.

No mathematical claim changed. Items below follow the numbering of AUDIT.md.

1. **Allen eq. (3).** Reworded neutrally and factually: the misprint is in arXiv v1 only; the published PLoS version (Eq. (3)) prints
   `r^{-(N-3)}` and agrees with the exact chain. main.tex negative control (Controls section) and Limitations ("Open discrepancies"; eq. (3)
   dropped) and ledger AMC-C-0007 updated. The bibliography entry for Allen and Section "Setting" now say that eqs. (5)-(9) and the
   definitions are identical in the published version (published pp. 4-6, checked by the auditor). publication_meta.json updated likewise.
2. **Richter's r_max.** Now a second discrepancy, not "a different quantity": Richter states r_max ~ 1.00075 (text p. 8, Fig. 1 caption);
   our certified (+) signs at 1.0007, 1.000775, 1.0008125 and the auditor's (+) at 1251/1250 and 16013/16000 contradict it; cause not
   investigated. Added to main.tex (Finite-r subsection and Limitations), ledger AMC-C-0012 and AMC-X-0001, RESULT.md, publication_meta.json.
3. **Rounding direction.** Bracket printed as [1.00082333, 1.00082349] (rounded outward; exact fractions kept) in the text, the bisection
   table (lower end shown as 1.0008233398), the headline table, ledger AMC-C-0012, RESULT.md, publication_meta.json. Gap column rounded down:
   N = 9 is 0.0173 (exactly 13/748), N = 4 is 0.1555 (exactly 7/45), in the census table, the nearest-miss table, Step 5, ledger AMC-C-0002/-0005.
   The nearest-miss table now gives the exact N_eff 6719/748 (N = 9) and 6257/627 (N = 10) from the audit recheck, with a note. N = 10 (13/627 >= 0.0207) unchanged.
4. **Slope-control count.** Text, ledger AMC-C-0006 and RESULT.md now say all 141 connected graphs with N = 3..6 and 22 graphs (every 40th)
   at N = 7, 163 in total (main.tex Step 7 and Controls section both).
5. **Bibliography.** Tkadlec is J. Tkadlec, with title and PLoS CB 16(1):e1007494; Richter 2020 and 2022 titles and the journal versions (J. Math. Biol. 82, 61 (2021);
   87(1):3 (2023)); Svoboda et al. title and PLoS CB 20(3):e1012008; Brewster et al. title and authors. The four "Title not re-verified" notes are removed.
6. **Novelty paragraph.** Richter's ref. [6] identified as Allen et al. 2021, PLoS CB 17:e1008695 (Bd only, read via the article page, not in full); added Alcalde Cuesta et al.
   (IWBBIO LNCS 10209; not opened) and the companion "Suppressors of selection" (Bd only). Wording now "to our knowledge", naming what was searched
   (the auditor's alphaXiv searches and ten papers read); explicitly not a proof of absence and not a priority claim. New references allen21 and alc17.
7. **Quote attribution.** "the smallest known unweighted dB-amplifier" is attributed to Svoboda et al. (p. 5); Richter 2020 (p. 6) and Richter 2022 (p. 8) are quoted as the auditor gave them.
8. **tau_max discrepancy.** Kept unexplained; added the auditor's finding: our parent values confirmed (10066/569 at vertex 9; 18.294102 for N = 12), the perturbed-graph hypothesis ruled out
   (max tau_i 20.158 and 22.067 do not match), the graph identification otherwise solid. Also in ledger AMC-C-0010 and Limitations.
9. **Replay statement.** Lean section lists all five modules (Core, DataR11, DataP11, Richter11, Controls; rc 0, 57-74 s each, oleans byte-identical to the producer's) citing
   `data/leanchecker_replay_audit.json`, and keeps the producer's own two-module record separately. Ledger evidence blobs for the Tier A rows now also reference the audit replay file.
10. **Stale audit lines replaced.** AI-assistance disclosure, ledger section, Limitations, publication_meta.json (description and notes) and `RESULT.md` now state: independent AI audit,
    ACCEPT_WITH_CORRECTIONS, no human audit, no statement lock, replay rc 0 on Core/DataR11/DataP11/Richter11/Controls, census independently rechecked (N = 3..9 fully, a 20,177-graph
    sample at N = 10), finite-r signs reproduced. `ledger/build_ledger.py` fills an `ai_audit` field on every Tier A row (same convention as the N1 paper); the gate field `audit` stays null
    (no person audited), so LEDGER_UNAUDITED_TIER_A stays open. Ledger rebuilt and `ledger/run_gate.py` re-run: **exit code 1, 0 blocking findings, 4 flags LEDGER_UNAUDITED_TIER_A** (AMC-A-0001..0004), `ledger/gate_output.txt` rewritten.
11. **Overflow guard.** `data/code/census_enclosure.py` now asserts, before the int64 cast, `np.isfinite(x).all()` and `max|x| * 2^30 < 2^50`, and afterwards `max|t| < 2^50`. **The assert was added after the census run**;
    the historical result files were not regenerated or edited. Re-running N = 7 with the modified script gave the same counts (853 graphs, 849 excluded, 4 candidates). The independent audit recheck
    (different exact method; N = 3..9 in full, 20,177 graphs at N = 10) covers the decisions, and the precondition is stated in Step 5 of the paper. The N = 10 enclosure itself was not re-run with the assert.
12. **Reproduction commands.** The printed `nauty-geng ... | census_enclosure.py N` pipeline was wrong. Replaced by commands that were actually run, from a scratch work copy W (scripts write next to their own folder, so running in
    place would write to `data/data/`): `nauty-geng -cq N file; census_enclosure.py <file> N 0 1 enc.json; finish_candidates.py enc.json out.json`, `exact_census.py`, `fixation_cert.py`, `window_bisect.py`, `gen_lean.py` (output identical to `data/lean/DataR11.lean`), `worked_example.py`, the pinned Lean compile (rc 0, same
    three axiom lines), build_ledger and run_gate. Tested at N = 7 and on the Richter graph. `controls.py` (rc 0, controls_failed: []), `richter.py` (265 quartic and 85 cubic graphs, same N_eff and tau_max as the data file) and `regular_check.py` (rc 0) were also run in the work copy to completion. Not tested / layout-dependent
    (stated in the paper): `run_small.py`, `summarize.py`, `leanchecker_replay.py` (they assume the original `results/proposal4/...` directory layout), and the full N = 8..10 census.
13. **Minor.** (a) Timing: the "about 24 minutes" sentence is replaced by "the N = 10 enclosure took 1237 s (plus the candidate solves)". (b) Gap column and nearest-miss table: see item 3. (c) ControlsMustFail now described as failing at
    elaboration ("did not reduce to isTrue or isFalse"), not by a kernel false verdict, the decisive control being `ctl_perturbed_vector_rejected`. (d) Allen page numbers: definitions on v1 pp. 6 and 8 (main.tex and ledger AMC-L-0001).
    Also: the auditor's sha256 of a fresh `nauty-geng -cq 10` (bf530d38...0ab5, equal to the producer's recorded hash) is mentioned in Reproducibility; the Limitations "novelty unchecked" bullet header now reads "established only to our knowledge".

Page count after revision: 11 (was 9). Build: pdflatex run twice, 0 errors, 0 undefined references.
