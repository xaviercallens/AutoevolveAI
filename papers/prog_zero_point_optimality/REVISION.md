# REVISION — P2 `prog_zero_point_optimality` (stage REVISE, after AUDIT.md)

Reviser: an AI agent (Claude). No result, Lean file or Lean hash changed. Two table presentation changes: Table 3 (tab:pot) gained a dagger on the gauss:1 row, and Table 4 (tab:elastic) now shows an already-computed competitor for gauss:0.5 (0.5+1.016i, long-wave 1.379e-3, replacing 0.5+0.966i, 2.695e-2); the ledger gained one row (ZP-X-0013, 37 claims). Every other change is wording, a derivation of a previously hand-typed number, a documentation/hardening commit in the rusty crate, or a ledger row.
No human has reviewed any of this. I declined nothing: every item below was applied, except the part of N8 that needs a
commit or push in AutoevolveAI, which this stage is not allowed to do (listed under "Left open").

## Required corrections (C1-C5)

| item | what was done | where |
|---|---|---|
| C1 "false as stated" | Abstract: "it fails numerically (Tier X, below): we do not claim a proof that it is false". Meta description: same. Setting section: "G1 numerically refuted QU-1 (Tier X)". The Tier-C logical statement ZP-C-0011 ("if a stable lattice has lower E_zp for some CM g, QU-1 is false as stated") is a conditional and was kept, as the audit allowed. | main.tex abstract, Sec. 1; publication_meta.json |
| C2 "four narrower" | Replaced by a neutral list: "Four potentials (Gaussian a = 0.25, 2, 4 and Riesz s = 6) are not refuted, on a sample and two dense paths". Same in the meta description. | main.tex abstract; meta |
| C3 stale audit statements | Disclosure: the paper-stage rerun is still "not a producer != verifier check"; a separate AI audit (AUDIT.md) is described and "not a human audit". Limitations "Verification status": no human audit; one separate AI audit with its scope, and the list of things checked only through the producer's data. New Section 8 "Separate AI audit: scope and result" states what was recomputed and what was not. Meta description updated the same way. The 8 LEDGER_UNAUDITED_TIER_A flags stay open (gate output: 0 blocking, 8 flags, exit code 1). Ledger status string and a new Tier-X row ZP-X-0013 record the audit (audit output files copied to `data/audit/`). | main.tex; ledger/build_ledger.py; meta |
| C4 riesz:4 caveat in abstract | Added one clause: single competitor, long-wave margin 0.08 % of the triangular value, finite-k stability from G1 grids only, triangular point a local minimum (c > 0). | main.tex abstract |
| C5 competitor tables | Table 3 (tab:pot) gauss:1 row now carries a dagger; caption says the lowest robust competitor is the marginal 0.295+0.9555i (0.06 %), demoted in the text, and that the refutation uses 0.5+0.966025i. Table 4 (tab:elastic) now uses the Table 3 competitor for every potential (gauss:0.5 changed from 0.5+0.966i to 0.5+1.016i; its long-wave eigenvalue 1.379e-3 is 1.71 % of the triangular 0.0808, matching Table 3), except gauss:1, where it uses 0.5+0.966i, stated in the caption. Caption wording "the competitor used in each refutation" changed to "one competitor sufficient for each refutation". | gen_inputs.py; main.tex captions |

## Non-blocking items

| item | what was done |
|---|---|
| N1 two conventions for min lambda/|k|^2 | Step 9 now states (checked against `human_check.py` line 34: nearest equivalent dual-lattice point; the printed listing omits that line) that the code reduces kappa to the Wigner-Seitz cell (0.097 tri, 0.068 head), Table 2 and the Rust code to the parallelogram [-1/2,1/2]^2 (0.03222 tri, 0.03493 head), that the order differs, and that only the sign (positive) is used. |
| N2 QU-1' "iff" / "exactly" | QU-1' restated as "strict local minimiser if a < a1 or a > a2; strict local maximiser for a1 < a < a2 (numerical c)"; the endpoints are bisected numerical roots, c = 0 there, nothing is stated at them. "Negative exactly" replaced by "numerically negative" everywhere (abstract, Result 3, meta, ledger ZP-X-0005 and ZP-X-0011). The scan is described as 23 values of a in [0.1, 8] plus bisection, which does not exclude further sign changes between scan points (23 is the length of `scan` in data/mechanism.json; the audit text said 21). |
| N3 isotropy | The "1e-6 / 1e-9" sentence replaced by generated macros from data/mechanism.json: for a >= 0.5 relative |dxx-dyy| <= 1.5e-6, |dxy| <= 2.0e-8, |grad| <= 1.5e-6; at a = 0.25 the relative difference is 4.3e-4 and |grad| about 1.2e-5. (The old "dxy about 1e-9" was also loose: a = 4 gives 2.0e-8.) Ledger ZP-X-0005 updated. |
| N4 bibliography | Betermin pages now printed as in Luo-Wei ref. [7] ("3236--269"), assertion cited at Luo-Wei pp. 2-3 (Betermin p. 3249, Subsection 4.3, as Luo-Wei state), Luo-Wei journal version J. Math. Phys. 65 (2024) 071901 added second-hand via Deng-Luo ref. [27] (verified in the fetched Deng-Luo text, line 5571) and stated as not opened. |
| N5 Tier-L sources | `ledger/sources/MANIFEST.md` (made by `make_sources_manifest.py`): arXiv ids, pdf sha256, default-pdftotext sha256, recipe; both text hashes equal the `source_sha256` in `data/claim_*.json` and a fresh `pdftotext` extraction of the PDFs is byte-identical. The full texts are not redistributed (arXiv licences differ per paper); local paths are recorded. |
| N6 hard-coded macro | `max_stable_dist.py` computes it from the 48 committed G1 scan CSVs into `data/max_stable_dist.json` (0.2274, gauss:0.25); gen_inputs.py reads it (macro still 0.23 after rounding). |
| N7 hardening | rusty-SUNDIALS commit 609338e6485fc96002e4c60c0c3e34f9130c0108 on `physics/p2-zero-point-optimality-2026-10-25`: `DuffyResult::is_stable`, `ezp_gauss_duffy_stable` (returns `None` for an unstable shape), doc comments on `omega_sum`, `ezp_gauss_duffy`, `curvature_at_rho_gauss`, one test with a positive and a negative control. No existing behaviour changed; `cargo test -p qf-yukawa-crystal` 60 passed, 0 failed, 1 ignored; fmt exit 0; `cargo clippy --workspace --features experimental -- -D warnings` exit 0 (`data/revise_cargo_*.txt`). The paper's reported numbers were all produced at 6ad3cf7 and are not rerun. |
| N8 uncommitted / unpushed | Paper text now says plainly that the AutoevolveAI files were uncommitted at build time and that the rusty branch is local and not pushed. The commit/push itself is left to the parent session (see below). |
| N9 non-CM controls | Item (k) reworded: they are detection-power controls, not false-positive controls (the survivors, gauss:2 at gauss:1's competitor shapes and the frozen-phonon check play that role); the morse:3 stable lower-E_zp competitor at 0.5+0.966i is now mentioned. Ledger ZP-X-0009 updated. |

## Left open (not applied, with reason)

* **Commit and push of AutoevolveAI files and the rusty branch (N8).** This stage may not commit in AutoevolveAI or push. Before Zenodo the parent
  session must commit `papers/prog_zero_point_optimality/`, `formal_cert/Programmes/ZeroPoint/`, and `results/programmes/2026-10-25/P2/`, and push the rusty
  branch (3 audited commits plus 609338e) so that the cited hashes resolve. The Reproducibility section says they were uncommitted at build time; update the
  HEAD line after committing if you want the paper to cite the new HEAD.
* **The 8 LEDGER_UNAUDITED_TIER_A flags** stay open on purpose (the audit asked for it).
* **Items the audit did not recompute** (dipolar/Riesz/Yukawa refutations, long-wave tensor, Lin/Conc, Result 5, c(a) beyond a = 1, 2, phonon.rs) are listed in the
  paper (Section 8 and Limitations), not fixed.

## Rebuild and gates (real output)

* `python -I papers/prog_zero_point_optimality/ledger/build_ledger.py` -> 37 claims (A 8, L 3, C 13, X 13).
* `ledger/run_gate.py` (Elenchus `tools/ledger.py`): 0 blocking findings, 8 flags LEDGER_UNAUDITED_TIER_A, **exit code 1** (flags only), `ledger/gate_output.txt`.
* `gen_inputs.py` -> 173 macros; `build_pdf.py` (clean, pdflatex twice): **15 pages**, 0 undefined references, 0 multiply defined, 0 overfull hboxes.
* Lean files untouched: `Basic.lean` sha256 7d59f181...0d64f0, `Controls.lean` sha256 c725bdcb...acd90 (re-verified by `sha256sum`); the 19 Tier A theorems are as listed in Section 3 (axioms within propext, Classical.choice, Quot.sound; planted sorry/axiom controls in `Controls.lean` caught). Not recompiled in this stage because nothing in the Lean files changed; the audit recompiled them.
