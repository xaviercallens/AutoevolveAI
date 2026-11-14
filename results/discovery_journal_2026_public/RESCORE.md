# Rescore with the final kernel replay record (2026-10-26)

`RUBRIC.md` was not changed. `scores.json`, `TOP20.json` and `SELECTION.md` (the scoring against the 71-row snapshot) were not changed either. The new outputs are `scores_final.json`, `TOP20_final.json` and `SELECTION_final.md`. They were built by `scripts/score_build_final.py` and `scripts/top20_build_final.py`, which are copies of the original builders.

## Bottom line

**The set of 20 changes by one record.**

- **Leaves:** N2. This is "The triangular lattice is not a local minimum of zero-point energy for planar Yukawa kappa = 1, 2" (doi:10.5281/zenodo.23663551), a physics lesson. It was pick 12 (chapter 12) in `TOP20.json`.
- **Enters:** ED-15. This is "Does the triangular lattice minimise the harmonic zero-point energy? (numerical counterexample)" (doi:10.5281/zenodo.23653833), a physics lesson. It is pick 12 (chapter 12) in `TOP20_final.json`.

The other 19 records stay selected, but the order changes: ED-14 moves from pick 13 to pick 5. N2's score did not change (18). N2 leaves only because it now loses a same-day date tie and the cap of 7 per domain then removes it. That swap rests entirely on the C1 rise of ED-15 described below, so the parent decides whether to adopt it.

## What changed in the evidence

The final `results/kernel_replay_2026-10-26/replay.jsonl` has 93 rows, all rc 0. Its `result.json` reads OK 93, SKIPPED 778, `failures` []. The file has been tracked since commit 2b0dba1. Rows 1-71 are the snapshot used by `SELECTION.md` and are unchanged. Only rows 72-93 are new:

- CalcLamE9 and CalcLamF0-F9
- Chain, ChainLink, Constants, IV and SignedEndpoints
- SandierSerfatyStatement
- ZeroPoint.Basic
- ZeroPointCert.Basic
- ZeroPointClass.Basic
- ZeroPointPhys.Basic and Taylor

So only a justification that cites one of these modules can move. Every candidate whose justification mentions a replay was checked. Nothing else was re-scored.

## Scores that changed

| id | criterion | old | new | total old -> new | rank old -> new | evidence line (new) |
|---|---|---|---|---|---|---|
| ED-14 | C1 rigour | 2 | 3 | 18 -> 19 | 13 -> 5 | `replay.jsonl` (final, 93 rows): Programmes.SandierSerfatyStatement replayed rc 0. The source sha256 is 35add509, the same as the published file (`papers/prog_sandier_serfaty_audit/publication_meta.json`). The LeanFlow data certificate (SSA-A-0007) is not in the replay. The reproduced certificate is upstream's own code, not an independent checker. |
| ED-15 | C1 rigour | 2 | 3 | 17 -> 18 | 17 -> 12 | `replay.jsonl` (final, 93 rows): Programmes.ZeroPoint.Basic replayed rc 0. The source sha256 is 7d59f181, the same as the published file (`papers/prog_zero_point_optimality/publication_meta.json`). The 8 Tier A rows certify none of the E_zp statements, and the headline is Tier X. |

Both old justifications gave "not replayed" as the only reason for a 2.

- **ED-14:** the 5 non-control Tier A rows (SSA-A-0001..0005) are all in `SandierSerfatyStatement.lean`. SSA-A-0006 is the planted-controls row; control files are excluded from the replay by design.
- **ED-15:** ZP-A-0001..0007 are all in `ZeroPoint/Basic.lean`, and ZP-A-0008 is the controls row.
- **Same rule as before:** C1 is "the highest Elenchus tier reached by a claim the record itself states", so a Tier X headline does not cap it. ED-20, N2 and ED-22 already scored 3 with parts outside the kernel.

No other criterion changed. C2 and C3 for ED-14 and ED-15 rest on their AUDIT.md and REVISION.md, not on the replay.

## Checked and unchanged

- **ED-22 (C1 3):** its justification cited "CalcK*/CalcLam* replayed rc 0". CalcLamE9 and CalcLamF0-F9 are rows 72-90, outside the 71-row snapshot. The log mtimes (`.scratchpad/rescore_check_snapshot.py`) confirm this for part of that range: the logs of CalcLamF6-F9 were written after `scores.json` (11:37:42 UTC), so those four modules had not finished replaying when ED-22 was scored. The logs of CalcLamE9 and F0-F5 predate `scores.json` but postdate the 71-row read, because rows 1-71 match the 71 earliest logs, with no extra and none missing. So the old line claimed more than the record held at the time. The final record covers all of them, so the score is unchanged and the evidence is now complete. The justification text in `score_build_final.py` says this. The swap below does not depend on this point: the two raised modules were explicitly "not replayed" in the old text.
- **ED-20 and N2 (C1 3):** both cite their paper's own `data/leanchecker_replay.json`. The final record corroborates it: ZeroPointCert.Basic and ZeroPointPhys.Basic/Taylor are rc 0.
- **ED-12 and ED-13 (C1 2):** the QuantumFluids stack (H7, H8, P6) was not replayed (REPLAY.md, "Not replayed"), so both stay at 2.
- **ZeroPointClass.Basic (N1, commit 9efd4f8):** no candidate record. It is unpublished and its producer is unaudited, so no candidate was added for it.
- **Other replay citations are unchanged** because all of their modules were already in rows 1-71:
  - ED-09 (DipolarExciton*)
  - ED-10 (Yukawa*)
  - ED-11 (KeldyshCM)
  - ED-16 (CompletelyMonotone.*)
  - ED-17 (FeynmanBijl)
  - ED-18 (PopGen.*)
  - ED-23 (EvoGraph.*)
  - Z-RIESZ, D3 and D4 (Triangular.*)
- **No score went down.** All 93 rows are rc 0.

## Hard rules re-applied (`select()` unchanged)

- **Ties (total, then C1, then C2, then earlier `created`):** ED-15, ED-20 and N2 are now all 18 with C1 3 and C2 3. Their `created` values decide the order:
  - ED-15: `2026-10-26T01:30:35.626601+00:00`
  - ED-20: `2026-10-26T03:41:10.272051+00:00`
  - N2: `2026-10-26T10:50:08`, the mtime of `papers/p3_zero_point_physical/zenodo_doi.txt`, hard-coded in `score_build.py`. The host is on UTC.

  The pure ranks become ED-15 12, ED-20 13, N2 14. Before the rescore, ED-15 was 17 at total 17.

  The order is robust. The Zenodo record ids give the same order, 23653833 (ED-15) < 23655392 (ED-20) < 23663551 (N2), so the result depends neither on N2's hand-entered mtime nor on the time zone.
- **Domain minimums:** the reserved records are the same, except that ED-14 now sits at pure rank 5 instead of 13:
  - mathematics: ED-14, ED-22
  - physics: Z-UO-TIERED, ED-10
  - genetics/biology: ED-18, ED-23
  - numerics/software: G-RUSTY, L-STELLARATOR
  - AI methodology/verification: Z-GWAYA, G-AUTOEVOLVE
- **Lessons (at least 3):** L-STELLARATOR is the only lesson among the reserved records. The two top-ranked lessons are added next: these are now **ED-15 and ED-20** (before the rescore, ED-20 and N2).
- **Cap of 7 per domain:** physics fills with Z-UO-TIERED, ED-10, ED-15, ED-20, ED-17, ED-09 and ED-11. **N2 (pure rank 14) and Z-QFLIB (17) are skipped by the cap.** Before the rescore, the cap skipped Z-QFLIB and ED-15.
- **Result:** the domain counts are unchanged:

  | domain | count |
  |---|---|
  | physics | 7 |
  | mathematics | 4 |
  | cosmology | 2 |
  | genetics/biology | 2 |
  | numerics/software | 2 |
  | AI methodology/verification | 2 |
  | education/textbook | 1 |

  There are still 3 lessons: ED-15, ED-20 and L-STELLARATOR. The harness counterfactual is unchanged (Z-CLAIMS-AUDIT and Z-LEANFLOW would replace G-RUSTY and G-AUTOEVOLVE).

## Order of the 20 (old -> new)

| pick | `TOP20.json` | `TOP20_final.json` |
|---|---|---|
| 1 | Z-BAO-P1 19 | Z-BAO-P1 19 |
| 2 | Z-BAO-P23 19 | Z-BAO-P23 19 |
| 3 | Z-UO-TIERED 19 | Z-UO-TIERED 19 |
| 4 | ED-10 19 | ED-10 19 |
| 5 | ED-17 19 | **ED-14 19** |
| 6 | ED-18 19 | ED-17 19 |
| 7 | ED-23 19 | ED-18 19 |
| 8 | Z-UO-BOOK 18 | ED-23 19 |
| 9 | ED-09 18 | Z-UO-BOOK 18 |
| 10 | ED-11 18 | ED-09 18 |
| 11 | ED-20 18 | ED-11 18 |
| 12 | **N2 18** | **ED-15 18** |
| 13 | ED-14 18 | ED-20 18 |
| 14 | ED-22 17 | ED-22 17 |
| 15 | ED-24 17 | ED-24 17 |
| 16 | Z-RIESZ 16 | Z-RIESZ 16 |
| 17 | G-RUSTY 16 | G-RUSTY 16 |
| 18 | Z-GWAYA 15 | Z-GWAYA 15 |
| 19 | G-AUTOEVOLVE 14 | G-AUTOEVOLVE 14 |
| 20 | L-STELLARATOR 13 | L-STELLARATOR 13 |

## Builder changes (copies only; the originals were not modified)

- **`score_build_final.py`:**
  - The C1 justifications of ED-14 and ED-15 (2 -> 3) were rewritten as above.
  - The ED-22 justification text was completed (score unchanged).
  - The output goes to `scores_final.json`.
  - Nothing else differs from `score_build.py`.
- **`top20_build_final.py`:**
  - It reads `scores_final.json` and writes `TOP20_final.json` and `SELECTION_final.md`.
  - The ED-14 "checked" line now says replayed, with the LeanFlow certificate not in the replay.
  - A new ED-15 prose entry was written only from its `publication_meta.json` description. It is new text and needs the same review as the other picks' prose.
  - The prose coverage assert is now `sel <= PROSE`, so the unused N2 entry is kept.
  - The snapshot note (71 rows, untracked, still running) was replaced by the final record note.
  - The "lessons rule" sentence now names ED-15 and ED-20.

## Open points for the parent

- Adopting the swap means **replacing the N2 chapter by an ED-15 chapter**. "Chapter 12" above means pick 12; `book/STYLE.md` fixes no chapter numbering. The decisive fact is the date tie-break inside 26 October. It is legitimate under the rubric, and the record-id order confirms it. Of the two, N2 is the certified (Lean + ball arithmetic) negative result, and ED-15 is the earlier numerical refutation that ED-20 and N2 build on.
- No chapter files exist yet in `book/` (only `STYLE.md` and `macros_stub.tex`), so nothing written has to be undone.
- **Stale under the new set (not edited here):**
  - `ARC.md` line 140 lists "QU-1 refuted numerically (23653833)" without "pick ED-15".
  - `ARC.md` line 152 lists "the N2 certificate for Yukawa (23663551, pick N2)".
  - The `ARC.md` table row "5 Oct 23-26" (line 174) names N2 instead of ED-15.
  - `ARC.md` lines 154-156 list the modules the replay reached without ZeroPoint, ZeroPointCert, ZeroPointClass, ZeroPointPhys and SandierSerfatyStatement.
  - The unused N2 prose ("the last result of the year") would leave the book.
