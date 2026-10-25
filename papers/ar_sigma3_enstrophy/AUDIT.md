# H7 / ar_sigma3_enstrophy: Stage 4 independent audit

Auditor: a separate AI agent instance (Claude), not the producer, the numerics author or the paper writer. Not a human
audit. Date 2026-10-25. Everything below comes from commands I ran myself. Scratch files are in `/tmp/h7audit/` (outside
the repo). The only file I wrote in the repo is this one. I did not edit or commit anything in the rusty-SUNDIALS worktree.

**Verdict: ACCEPT_WITH_CORRECTIONS.** The Lean results recompile, and my own planted holes are caught. Every paper number
traces to a result file, and a full rerun of the numerics gives a bit-identical summary. The human proof is correct
step by step, and the citations are real and quoted faithfully. One wrong sentence in Section 1 (Tier C) must be fixed.
Smaller wording fixes are listed in Section 8.

## 1. Lean: recompiled by the auditor

Environment: Lean v4.34.0-rc2 run directly with the qf-lake `LEAN_PATH`, the same recipe as `run_lean.py`. My runner is
`/tmp/h7audit/run_all.py`, pinned to cores 4-7. The page cache was cold (lean at 3.5 % CPU), so I warmed 9285 modules
with `warm_siblings.py` from `/proc/PID/maps`.

| file (auditor copy) | sha256 | rc | time | result |
|---|---|---|---|---|
| `AuditFlow.lean` = claimed `Autoresearch_EnstrophyFlow.lean` (sha `4cd74689…8dd4`, verified) + extra `#print axioms` / `#print` / `#check` block | `5a26b6c6…` | 0 | 159.8 s (cold cache) | all 17 producer-audited declarations **plus** 11 helpers (`re_B_zero`, `re_B_succ`, `cross_weights_ok`, `ham3_eq_hamG`, `hasDerivAt_re/_im/_normSq/_cubic`, `weight_eq_one`, `disp_weight`, `sqrt_mul_self_eq_rpow`) print `[propext, Classical.choice, Quot.sound]` |
| `AuditPrior.lean` = `H7/Autoresearch_Enstrophy.lean` | `c7c9f24c…7f03` (matches paper) | 0 | 13.6 s | 6 theorems, all within the allowlist |
| `AuditControls.lean` = producer controls | `7a390424…65ce` (matches paper) | 0 | 10.0 s | `ctl_sorry` → `sorryAx`; `ctl_axiom` → `ctl_flow_cheat` |
| **`AuditPlantSorry.lean`** (my own: proof of `cross_weights_ok` replaced by `sorry`) | `7e72f468…` | **0** | 18.8 s | `sorryAx` appears in exactly the dependents `ham_rate_zero`, `ham_conserved`, `enstrophy_bound_along_flow`, `enstrophy_le_along_flow`; the independent declarations stay clean |
| **`AuditPlantAxiom.lean`** (my own: `energy_rate_zero` routed through a planted `axiom audit_cheat`) | `43c6f6b0…` | **0** | 22.5 s | `audit_cheat` appears in `energy_rate_zero`, `energy_conserved`, `enstrophy_bound_along_flow`, `enstrophy_le_along_flow` only |

Both planted holes exit with rc 0, so the exit code alone would pass them. The axiom audit catches both, and it
attributes each one to the right dependents. The hole grep on the claimed file returns 0 matches.

**Statement fidelity.** I checked this by hand against `#print` output from the compiled owner build:
- The owner's `shellBc` is `0 ↦ -(k0 conj(v0) v1)` and `m+1 ↦ k_m v_m² − k_{m+1} conj(v_{m+1}) v_{m+2}`. This matches paper eq. (1).
- `F = shellBc − I·ω·v` matches eq. (2).
- `dT`, `flux4`, `sum_dT`, `weights_ok`, `shellBc_energy_conservation` (hypothesis `v (N+1) = 0`, applied at `N+1`), `cubic_bound` and `dispersive_norm_le` have the statements the paper quotes.
- `ham3` is the §5 formula with ω_n = D k_n³. `energy` and `enstrophy` sum over `range (N+2)`, consistent with truncation at `v (N+2) = 0`.
- The solution hypothesis covers exactly the shells used (n < N+2). `hamG` reads `v (n+1)` only for n < N+1, so nothing outside the hypothesis enters.

**Scope of the solution hypothesis.**
- Existence is assumed, not proved.
- `HasDerivAt` is two-sided at the endpoints.
- For T < 0 the statement is vacuous.
- The zero-trajectory witness shows only that the hypothesis is consistent.

The paper states all of this correctly.

The owner's docstring really does list "the chain-rule step … the dispersive (`D`) … extensions … not in Lean". I read it
in `lean_src/ShellHamiltonian.lean` lines 15-17, QuantumFluids HEAD `10f74daf1b39d2ac51a785452329fff0003cfc83`, which
matches the paper. So the claim of what is new relative to the owner's files is accurate.

Two more provenance checks:
- `git diff --stat HEAD` on `lean_src/QuantumFluidsShell.lean` and `lean_src/ShellHamiltonian.lean` is empty. The only
  modified path in that repo is `lean_src/.lake`, so the cited sources are the committed ones.
- I reran `make_listings.py` on a copy. The `listings/` directory it produces is byte-identical to the published one, so
  the "verbatim" Lean listings in the paper are verbatim.

## 2. Numbers trace to result files; rerun

- **`gen_numbers.py`.** I reran it on a copy of the paper directory. It regenerates `gen_numbers.tex`, both tables and
  the three `axioms_*.txt` files byte-identically (`diff -r` is empty).
- **Data files.** `data/{summary.json, sigma3_study.json, sigma2_probes.jsonl}` are byte-identical to the files committed
  in the rusty worktree (`crates/qf-shell-cascade/results/sigma3/`).
- **Rebuild.** I rebuilt `sigma3_study` from the worktree HEAD (`dfa9a08`; code commit `99f5df8`, based on origin/main
  `47ef5044…`, as the paper states).
- **Full-study rerun.** I reran the full study once: `sigma3_study full`, 167.4 s on one core, against the paper's 143.7 s.
- **Summary comparison.** I ran the author's `summarise.py` on that rerun. The resulting summary equals the published
  `summary.json` exactly once wall times are removed: all drifts, ratios and BDF step counts match, and `all_gates_pass` is True.
- **Unit tests.** I reran `cargo test --release -p qf-shell-cascade`: 32 unit tests and 2 positive-control tests pass. The paper
  says these were not rerun at paper stage; they now have been.
- **Hand-typed numbers checked against the summary.**
  - The S drifts −2.8e-5 (σ=3, n_max=6) and −1.3e-4 (σ=2, n_max=10, probes) match the result files.
  - The ratios 0.6667 to 1004 match.
  - The neg/pos ratios match: for example 2.6e-3/4.0e-10 ≈ 6.5e6, printed 6.6e6 from the unrounded values.

## 3. Human proof, step by step (Section 2)

I re-derived each step myself:
- **Step 1.** Correct.
- **Step 2.** The telescoping and the boundary term R_{N+1} ∝ v_{N+2} = 0 are correct.
- **Step 3.** I checked the dispersive pieces 2ω_nR_n and −ω_{n+1}R_n, and the owner's dT_0 = −k_1X_0 and
  dT_{m+1} = 2k_mX_m − k_{m+2}X_{m+1}. I also checked the X_m coefficient 2g_{m+1}k_m − g_mk_{m+1} and the survivor
  −g_Nk_{N+1}X_N. All are correct.
- **Step 4.** The R_m coefficient and the identity for q = 2⁻ⁿω, g = 2⁻ⁿk hold for every ω. Correct.
- **Step 5.** Correct.
- **Step 6.** q_n = Dk_n², |T_n| ≤ |v_n|²√S, and the sum is ≤ S^{3/2}. Correct.
- **Sharpness (i).** 2DΩ = 5 and H₃ = 1 + 4 − 1 = 4. Correct.
- **Sharpness (ii).** The hand value −2 + 16 − 6 = 8 is correct, and with the correct weights it is −2 + 8 − 6 = 0.
- **Corollary 1.** Correct: 2DΩ(t) ≤ 2DΩ(0) + 2S^{3/2}.
- **σ=2 remark.** D4ⁿ/(D2ⁿ+1) is correct.
- **Waleffe remark.** The reduction is correct: interior 2^{n−1}(…) = ½·2ⁿ(…), boundary −v₀v₁ = ½(−2v₀v₁), and v(t) = a(t/2).

**Error, Section 1 (Tier C).** The paper says: "Under v ↦ λv, t ↦ t/λ the nonlinearity is invariant and **D ↦ D/λ**, so
only D/√S is meaningful."

The correct map is D ↦ **λD**. If w(s) = λ v(λs), then dw/ds = B(w) − i(λD)k³w. With S ↦ λ²S, the combination D/√S is
then invariant, so the conclusion is right. With D ↦ D/λ as written, D/√S would not be invariant (D√S would be), so the
sentence contradicts itself. **Must fix** (one symbol). It does not affect any theorem or number.

## 4. Tiers and overclaim

- Tier A is used only for what the kernel checked. Tier C covers the corollary, the scaling argument and the remarks.
  Tier X is explicitly "supports no claim", and the ledger's X rows carry `claim_licence: false`. No numeric result
  is used as support.
- No openai/math result is used, so the triangular-lattice conditionality does not apply. The paper states this correctly.
- The "inf ≤ inf" style vacuity cases are covered:
  - For D ≤ 0 the bound "carries no information on Ω".
  - For T < 0 the statement is vacuous; the paper does not mention this, but it is harmless.
- Cutoff uniformity is conditional on N-uniform Ω(0), S(0), and the paper says so in the abstract, Section 2 and the
  limitations. The **title**, however, says "A cutoff-uniform enstrophy bound" without that qualifier. I recommend
  "cutoff-independent" or "…for H¹-type data" (non-blocking).
- Novelty wording is careful: "short corollary of the owner's dispersive_norm_le", "no novelty is claimed for the
  inequality", and the literature check is listed as not done. There is no breakthrough wording.
- **Verification status will be outdated.** The disclosure and the limitations say "no independent verifier has run".
  After this audit, they should say that an independent AI-agent recompile and audit (this file) was done, and that no
  human has audited it. The ledger `audit` fields stay null, because the Elenchus `audit` slot is for a person.

## 5. Citations

All checked against primary text through alphaXiv (`answer_pdf_queries`):
- **Waleffe, arXiv:math/0410380v2.**
  - Eq. (12), eqs. (19)-(20) with the sentence on energy conservation, and Theorem 1 (hypotheses a_j(0) ≥ 0,
    E_{B(J)}(0) ≥ q^J, λ⁻² < q < 1) all match the ledger excerpts.
  - I also ran `citation_check.py` on Theorem 1. The claim is `/tmp/h7audit/cite/claim_thm1.json`, and the source is
    `/tmp/h7audit/cite/waleffe_thm1_source.txt`, an alphaXiv page-7 extraction with sha256 `f0a93161…`. The result is
    **ACCEPTED** (exit 0, tier ceiling L).
  - The author's ledger notes that its own extraction file was not persisted. Persisting a source text file would let
    the citation gate be rerun (non-blocking).
- **The Well, arXiv:2412.00568.** The title and first authors are verified (Ohana, McCabe, …; NeurIPS 2024 D&B). It lists
  `turbulent_radiative_layer_2D` (Athena++), cites Fielding et al. ApJL 894 L24 (2020) as ref. [95], and gives the same
  t_cool set as the card.
- **SUNDIALS, arXiv:2011.10073.** The title is verified. The bibitem has no authors (Gardner, Reynolds, Woodward, Balos;
  ACM TOMS). Adding them is recommended (non-blocking).
- **Fielding et al.** The paper marks it "as given in the dataset card; not read by us". That is honest.
- **Own DOIs 10.5281/zenodo.23293429 and 23295142.** Both are recorded as published in the repo (`zenodo_doi_v2.txt`) and
  in memory.

## 6. Dataset provenance and licence

- **Revision and licence.** HF API, queried live: `polymathic-ai/turbulent_radiative_layer_2D` at revision
  `2ee7756575ff6f90981d0308cbcb6a2ab5995bdc` is also the current `main`. The card's licence is `cc-by-4.0`.
- **HDF5 file.** The LFS sha256 of `data/test/turbulent_radiative_layer_tcool_0.32.hdf5` is `06cbd36c…f747`, size
  109,051,904 B. The local copy hashes to the same value.
- **README.** The local README.md sha256 `53aadbad…1501` matches `download_record.json`.
- **Card contents.** Athena++, periodic in x and zero-gradient in y, and cooling −E/t_cool all appear in the card, as
  the paper says.
- **Use is honest.** The data serve only as a spectral-shape illustration (Tier X), with explicit caveats: compressible,
  cooling, velocity only, random phases, top shells not filled.
- **Attribution.** CC-BY attribution is given (The Well, the dataset id and the Fielding paper).

## 7. publication_meta.json

- **Title.** It matches the paper title.
- **Description.** Its numbers match `gen_numbers.tex`: 0.360, 0.631, 0.995, 24 runs, revision `2ee77565`, and the gate
  result "0 blocking, 7 flags, exit 1". I reproduced that gate output by running `ledger.py` myself.
- **Notes.** The shas match: Lean `4cd74689…` and `c7c9f24c…`, owner commit, rusty commits `99f5df8`, `e869e5f`,
  `dfa9a08` and base `47ef5044`, and the HDF5 sha.
- **Related identifiers.** All are real (Section 5).
- **Format.** The key set is the same as `universal_optimality_tiered/publication_meta_v2.json`.
- **Needs updating.** "Producer and verifier have not been separated" should be amended after this audit, in the same
  way as the paper.

## 8. Corrections

Blocking (must fix before publication):
1. In Section 1, change "D ↦ D/λ" to "D ↦ λD" (the D/√S invariance is then consistent).

Non-blocking (recommended):
2. Update the AI disclosure, the Limitations "Verification" item, ledger SE-X-0005 context and the publication_meta notes.
   They should say an independent AI-agent audit recompiled the files and caught planted holes (this file), and that no
   human has audited it yet.
3. Title: qualify "cutoff-uniform", for example "cutoff-independent", or say so for N-uniform H¹-type data.
4. The n_max=6 negative control's H₃ drift is 5.9e-3 / 5.5e-3 / 5.4e-3 across rtol, not "at 5.4e-3 at every rtol".
   Ledger SE-X-0001 says "2.6e-3 to 5.5e-3", but the maximum is 5.9e-3.
5. Top-shell rows (Table 2, C2 in `summary.json`): the supremum is slightly above the t=0 value, not equal to it.
   - σ=3: by up to about 3e-7. For example, n_max=2 gives 0.44444417 against 0.44444390, and n_max=3 gives 0.76190442
     against 0.76190410. At n_max=6 the gap is about 9e-10.
   - σ=2: by up to about 3e-6 (n_max=4).
   - Wording to fix: the abstract's "the supremum equals the t = 0 value" and the Limitations sentence "the supremum is
     attained at t = 0, before any integration error enters" are literally false. Write "equals the t = 0 value to within
     about 3e-7".
   - The argument still stands: 3e-7 is far below the 0.005 margin at ratio 0.995.
6. Add the SUNDIALS paper authors to the bibitem, and persist the Waleffe source text for `citation_check.py`.
7. Optionally, note that for T < 0 the along-flow statements are vacuous.
