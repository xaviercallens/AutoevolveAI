# H7 / ar_sigma3_enstrophy: Stage 5 revision after AUDIT.md

Date 2026-10-25. Every correction in AUDIT.md (verdict ACCEPT_WITH_CORRECTIONS) was applied. None was declined.
No theorem, Lean file, Rust code or result file changed. Only the paper text, the number generator, the ledger builder
and the metadata changed. The rusty-SUNDIALS worktree has no new commits.

## Blocking

1. **Scaling remark (Section 1, Tier C).** "D ↦ D/λ" is now "D ↦ λD". The sentence now shows the map
   w(s) = λ v(λs), which gives ẇ = B(w) − i(λD)k³w, and adds S ↦ λ²S, so the D/√S invariance can be read off. I
   re-derived it: B is quadratic, so λ²B(v(λs)) = B(w), and the rotation term becomes −iλ·ω·w. **Fixed.**

## Non-blocking

2. **Verification status.** The AI disclosure, the Limitations "Verification" item and the numerics method paragraph
   were updated. The method paragraph said tests were "not rerun at paper stage"; it now says the audit reran
   `cargo test` (32 + 2 pass) and the full study. The updated text says a separate AI-agent instance ran an independent
   audit (`AUDIT.md`): it recompiled the files, its own planted sorry and axiom were caught, and it reran the numerics
   and tests. It also says no human has audited the work. Other places updated:
   - Ledger: the producer field in each Tier A blob now has an `independent_audit` entry pointing to `AUDIT.md` by hash,
     plus `human_verifier: null`. SE-X-0005 also points to `AUDIT.md`.
   - `publication_meta.json`: the description and the notes.

   Ledger `audit` fields stay null. **Fixed.**
3. **Title.** "cutoff-uniform" is now "cutoff-independent" in `\title`, `pdftitle` and the meta title. The body already
   says what this means: uniform only for N-uniform Ω(0), S(0). **Fixed.**
4. **Negative-control drift.** The audit's correction holds, and the ledger was wrong at both ends. From
   `data/summary.json`, the drifts across S and H₃, n_max = 4 and 6, and rtol 1e-6 to 1e-10 range from 2.3e-3 to 5.9e-3.
   - Constant at the printed precision: S (2.6e-3 for n_max = 4, 4.6e-3 for n_max = 6) and H₃ for n_max = 4 (2.3e-3).
   - Not constant: H₃ for n_max = 6 goes 5.9e-3 → 5.5e-3 → 5.4e-3.

   Changes:
   - `gen_numbers.py` now generates `\NegAllMin`, `\NegAllMax`, `\NegHsixMin` and `\NegHsixMax`.
   - The main.tex sentence now reads "does not converge … between 5.4e-3 and 5.9e-3" for n_max = 6 H₃.
   - Ledger SE-X-0001 now reads these values from `gen_numbers.tex`, so they are not typed by hand.

   **Fixed.**
5. **Top-shell supremum vs t = 0.** The audit is right that "equals" was literally false. I recomputed the gaps from
   `summary.json` and `sigma2_probes.jsonl`. For the probes, which have no `ratio_t0` field, the t = 0 ratio is
   2·D·Ω₀/bound_rhs, with Ω₀ from `trace_t_S_H_Omega[0]`.
   - **σ = 3** (C2 rows n_max = 2..6): the largest absolute gap is 3.2e-7 (n_max = 3), which matches the audit.
   - **σ = 2:** the audit's "about 3e-6" is not right in absolute terms. The absolute gaps are 3.1e-6 (n_max = 4), 3.7e-6
     (5), 2.5e-5 (6), and up to 3.4e-5 in the probes (n_max = 7). The ratios themselves reach 1004, so the paper now
     states the **relative** gap instead: at most 5.2e-7 (n_max = 6).

   Both numbers are generated (`\CthreeGapAbs`, `\CtwoGapRel`). They are used in the abstract, in the σ = 2 paragraph of
   Section 4 (which said "the supremum is the t = 0 value"), in Limitations, in ledger SE-X-0003 and in the meta
   description. The Limitations sentence "attained at t = 0, before any integration error enters" now reads: "exceeds the
   t = 0 value by at most 3.2e-7, far below the margin 1 − 0.995".

   I also checked the decaying-data and Well runs. "Sup above t = 0" in 12/12 and 24/24 counts strict `>`, so I
   measured the gap there too. The smallest is 0.150 for the decaying sweep and 0.0027 for the Well runs, so the
   dynamics really do move the ratio and that text is unchanged. **Fixed.**
6. **Citations.**
   - The SUNDIALS bibitem now lists D. J. Gardner, D. R. Reynolds, C. S. Woodward and C. J. Balos, ACM Trans. Math.
     Softw. I verified the authors and venue myself in the alphaXiv full text of arXiv:2011.10073. The preprint's
     header gives "Vol. 0, No. 0", so no volume is given.
   - The Waleffe Theorem 1 source text and claim from the auditor's run were copied byte for byte into
     `ledger/sources/` (`waleffe_thm1_source.txt`, sha256 f0a93161…4ccaf, and `claim_thm1.json`). The text is an alphaXiv
     page-7 extraction of arXiv:math/0410380v2 by the H7 auditor; the provenance is recorded here and in the ledger, not
     inside the text file, because the claim hashes it.
   - I reran `citation_check.py ledger/sources/claim_thm1.json ledger/sources/waleffe_thm1_source.txt`: ACCEPTED, exit 0,
     tier ceiling L. The output is in `ledger/sources/citation_check_output.txt`. SE-L-0001 evidence now references these
     three files, and the ledger section of the paper mentions them.

   **Fixed.**
7. **Optional: T < 0.** The Limitations "Solution hypothesis" item now says that for T < 0 the interval is empty and the
   along-flow statements are vacuous. **Fixed.**

## Rebuild

`python -I build.py` ran gen_numbers.py (70 macros) and make_listings.py, then pdflatex twice, both rc 0.
- Log: 0 `undefined`, 0 `Error`, 0 `Overfull`. The single "Rerun" hit is the `rerunfilecheck` package banner, not a
  warning.
- PDF: 12 pages.
- Ledger: 18 claims (7 A, 2 L, 4 C, 5 X; unchanged) and 18 evidence blobs.
- Elenchus gate: 0 blocking findings and 7 `LEDGER_UNAUDITED_TIER_A` flags, exit 1 (`ledger/gate_output.txt`). This is
  the same as before, and expected while no human has audited.
