# Stage 5 revision: H2 / ar_yukawa_crystal

Date: 2026-10-25. This revision responds to AUDIT.md (verdict ACCEPT_WITH_CORRECTIONS, no blocking items). Every
correction is about wording or traceability. No Tier A statement, Lean file or reported number changed. The four Lean
files still have the sha256 values printed in the paper (`a16397de…`, `6a940a7c…`, `ff7f11da…`, `028a3936…`, checked
again with `sha256sum`).

| # | Correction | Resolution | Where |
|---|---|---|---|
| C1 | "sign condition cannot be dropped" reads as if optimality fails for signed mixtures | **Applied.** The new wording says the admissibility lemma needs the sign condition, that g1-2g2 is not admissible, so the theorem does not apply to it, and that this does not show optimality fails. | Changed in four places: (1) abstract (iv). (2) Step 9, now titled "where the admissibility lemmas stop", with an explicit "do not show" sentence. (3) Physics "What is not said" (4), now "left open". (4) Ledger YK-A-0011, plus the same scope sentence on YK-A-0007. publication_meta bullet updated too. |
| C2 | `below_exact_floor` uses zero tolerance; κ=1 `uniform_00` anneal_quench sits at gap 0.0 | **Applied.** The wording is now "none below the exact triangular energy beyond f64 resolution". The paper names the stage at gap 0 and says why it is a rounding outcome. The stage name, its count and the box-versus-lattice difference (-2.2e-16) are generated from `data/exact_summary.json` and `data/exact_refs.jsonl`: new macros `\NZeroGap`, `\ZeroGapStage`, `\TriBoxDiffOne` in `gen_numbers.py`. | Changed in the abstract, "Results: relaxed configurations", ledger YK-X-0004 (counts computed in `build_ledger.py`) and the publication_meta description. |
| C3 | Vacancy clause uncited | **Applied.** I checked the quote myself: the alphaXiv extraction of arXiv:1902.05438 (the ledger's CKMRV file), line 549, reads "because removing a single particle changes neither the density nor the energy". It sits in the remark after Theorem 1.4 on page 8, since the page-8 running head is at line 523 and the page-9 head at line 659. | Added `\cite[arXiv version, p.~8, remark after Thm.~1.4]{ckmrv}` with the quote in Section 5 (1). The page is the arXiv pagination, so the ckmrv bibitem now also names arXiv:1902.05438 and says so. New ledger row **YK-L-0005** (excerpt lines 548-549), and YK-C-0002 now depends on it. Ledger is now 25 claims (11 A, 5 L, 3 C, 6 X). |
| C4 | YK-X-0006 says "g_1, orders 0..8" | **Applied.** The row now says: g_1 at orders 0..6, 159 points on [0.05, 4] (`figures/fig_signs.json`); g_1+0.5g_3 and its ρ=3 rescaling at orders 0..8, t=k/20, k=1..80 (`contribution/numeric_gate_mix.json`). | `ledger/build_ledger.py` |
| C5 | L rows are outside `citation_check.py`'s intake | **Applied.** I checked this against the source: `citation_check.py` line 35 has `KINDS = ("theorem", "lemma", "proposition", "corollary")`. Section 1 now says this, and says the quotations were checked against the alphaXiv full text (and the pinned upstream source for YK-L-0003) by the producer and the auditor. | Every L evidence blob now has a `quote_check` field saying the same. |
| Step 6 | Cells lie in the shell enlarged by the circumradius δ | **Applied.** The text now says the Voronoi cells are disjoint and lie in k-δ ≤ \|x\| < k+1+δ, of area O(k). | main.tex Step 6 |
| Step 8 | energy(h(·/ρ), √ρ C) = energy(h, C) used but not stated | **Applied.** The step is now stated, with the reason (squared distances scale by ρ; the disk radius is absorbed in the liminf) and a pointer to D2's `energy_smul`. That lemma is `energy g (c • C) = energy (fun t => g (c^2 * t)) C` (formal_cert/Triangular/AnyDensity.lean:136), used with c = √ρ. | main.tex Step 8 |
| cargo test not re-run | rests on producer output | **Resolved.** I re-ran `scripts/check_crate.sh` (fmt --check, clippy, tests; cores 4-7, 2 threads) in this stage. It exited 0 with: `test result: ok. 24 passed; 0 failed; 1 ignored` (lib), plus 0 tests in the binary and 0 doc-tests. clippy printed no warning or error lines. Output is saved at `results/autoresearch/2026-10-25/H2/contribution/check_crate_stage5.txt`. | Reproducibility block notes the re-run. |
| elenchus_check.py | returned only COMPILE_ERROR | **Applied (wording).** Limitation (9) used to say it "was not run". It now says the auditor ran it, that it returned only COMPILE_ERROR because its rc2 toolchain cannot see the pinned 4.34.1 stack, and that the kernel footprint checks, recompiles and planted controls replace it. | main.tex Limitations (9) |
| Commit Lean files before Zenodo | sha256 reproducibility from git | **Not done in this stage (declined for this lane, deferred).** The lane rules for this stage forbid committing in AutoevolveAI. It stays a required pre-upload action for the parent session. Limitation (8) and publication_meta `notes` now say so. | main.tex (8), publication_meta notes |
| Optional: OC20 shard mtime | latest possible download date | **Applied.** `stat` on the local shard gives 2026-10-10 20:04 UTC. It is generated by `os.stat` (`\OcMtime`) and also appears in YK-X-0005. | main.tex Section 6, ledger YK-X-0005 |
| Optional: OC20 journal DOI | doi:10.1021/acscatal.0c04525 | **Applied, DOI only.** I downloaded the dataset card (README.md) at revision 6a1dfef1 (sha256 `e9113732…`, 3196 bytes, into /home/callensxavier_gmail_com/hf-data/yukawa_crystal/oc20_card/) and extracted its DOIs into `data/oc20_card.json`: 10.1021/acscatal.0c04525 and 10.60732/b4005525. | The card gives only the DOI link, with no journal name or year, so the bibliography gives it as "journal version doi:10.1021/acscatal.0c04525 (as given on the dataset card)" with no year. It is also in publication_meta related_identifiers and YK-X-0005. |
| Also | Producer ≠ verifier paragraph | Added one sentence on the stage-4 audit's recompiles and planted controls. | main.tex Section 4 |

Two layout fixes were made along the way. The ledger table's Tier column was widened from 0.6 cm to 0.7 cm, which
removes a pre-existing 0.9 pt overfull box, and the table now says "Def. 1.3".

## Rebuild

1. I deleted `ledger/evidence/` and rebuilt it with `python -I ledger/build_ledger.py`. Output: `claims 25; evidence blobs 25`.
2. `python -I gen_numbers.py` re-runs the Elenchus gate (`tools/ledger.py ledger.json --evidence-dir evidence --json`).
   Output: `74 macros; ledger exit 1; 24 relax rows`. The gate reports 25 claims, `evidence_verified: true`, 0 block
   findings and 11 flags, all `LEDGER_UNAUDITED_TIER_A`. Exit 1 comes from the flags only.
3. `pdflatex` ran twice through `results/autoresearch/2026-10-25/H2/contribution/build_pdf_stage5.py`. Both passes
   had rc 0, with 0 undefined references, 0 overfull boxes and 0 warnings. The PDF has **13 pages** (pdfinfo). The
   aux, log and out files were removed; build1.log and build2.log are kept.
4. publication_meta.json was updated by `contribution/update_meta_stage5.py`. Its counts are read from the gate output.

## Unchanged

- The rusty-SUNDIALS worktree has no new commit, because no correction touches Rust. The commits are still
  cc5a8aed81b3228bd9e9eb69f2c326f926903a34 (code) and 7f2a45c32a9eb9722ca36c334329cb7a5a541951 (results), on base
  47ef5044. They are not pushed.
- Nothing was pushed, merged or published.
