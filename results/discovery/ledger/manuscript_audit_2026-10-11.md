# Elenchus manuscript audit — universal_optimality_tiered.tex (Preprint v1, 2026-10-11)

Auditor: a separate, read-only instance of the same AI model (not the drafting session), run under ELENCHUS.md §7.
The auditor's file write was refused by the harness, so this file was saved by the producer from the auditor's
returned text. The findings are reproduced here; the editing below is the producer's.

## VERDICT: ACCEPT_WITH_CORRECTIONS (3 blocking text/table findings; no mathematical error)

### Blocking
- **B1.** The abstract said the ledger "passes" the Elenchus gate. The gate exits 1 (0 blocks, 6
  LEDGER_UNAUDITED_TIER_A flags), and ELENCHUS §8 requires exit 0 for publication.
- **B2.** "Every end state is a local minimum" and Table 2's Hess.<0 = 0 were also reported for runs that were never
  Hessian-checked: the incommensurate-box runs (`hess=false`) and the disk runs. summarize.py counted a missing value
  as 0. For the 120 checked runs: two translation modes with |λ| ≤ 1.8e-15, and all other eigenvalues ≥ 5.0e-5.
- **B3.** The abstract presented non-uniqueness without attributing it to CKMRV (after Thm 1.4) and to upstream
  ("identifies the minimum value, not all minimizers"), and it quoted an unsourced "popular gloss".

### Non-blocking (summarised)
1. "Strictly weaker" is unproven: no witness is filed. "Weaker" is certain.
2. The UO transcription matches CKMRV Defs 1.1–1.3 item by item. The only gap is the existence of the energy limit.
   Upstream Basic.lean has definitions identical to the challenge file, and the proof chain imports the proved
   Energy/Universal.lean.
3. The proof sketch is correct, but it uses `p` without defining it.
4. "Periodic uniqueness is open in dimension 2" has no Tier L source. Replace with "not claimed by upstream".
5. The corrected "statements" in §4 are unnamed; cite them or drop the sentence. The history itself is verified
   (CKMRV text lines 362-366, 416-417, 466-468, 482-484).
6. The Yukawa Tier C argument is correct (footnote 2, lines 506-521). The "truncation size" macro is V(r_c).
7. The preregistration order holds (636c514 before 968b0f2; criteria fixed before the results). Three deviations
   were undisclosed:
   - the defect cutoff is 1.35·d0 in the code, not 1.4a;
   - κ = 1 used 10/10/5 runs;
   - the incommensurate pass test checks only min gap > 0, although the data also satisfy "defected".
   Results commit: 1f46e70.
8. Number interpretation:
   - "100 relaxations" includes 20 control relaxations;
   - "defected or strained" should read "defect-free states above e_tri";
   - "families behave alike" holds at κ = 2 only (at κ = 1, 0/10 vs 2/10, and one uniform T = 0 quench reached the
     lattice);
   - the lowest gaps are the perfect runs.
9. All macros and all 12 Table 2 rows recompute from the jsonl. "22 audited" = 24 in the audit file minus 2 planted
   controls. The rebuild claim traces only to a commit message (no log committed). The d12 DOI resolves.
10. Ledger: the UO-A-0001 evidence has no source hash. The CKMRV excerpts point to a transient tool-results path;
    pin a durable reference.
11. AI-use: mention the DeepSeek-Prover-V2 Cloud Run queries (none of their output used).
12. The title wording is optional.
13. Presentation: Table 1 floats away from §1 (empty heading), a 0.9pt column overflow, a badly spaced Thm 2 header.
