# Stage 4 independent audit: H8 / ar_bogoliubov_sk

Auditor: a separate AI agent instance (Claude), acting adversarially. I am not the producer, and this is not a human audit.
Date: 2026-10-25. Scope: `main.tex`/`main.pdf`, `gen_numbers.tex`, `gen_inputs.py`, `ledger/`, `publication_meta.json`, `data/`,
`results/autoresearch/2026-10-25/H8/` (round 1 + `contribution/`), and the rusty-SUNDIALS worktree
`/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h8`, which I read only. Scratch files are in `/tmp/h8audit/`, outside the repo.

## Verdict: ACCEPT_WITH_CORRECTIONS (no blocking findings)

The mathematics is correct and the Lean statements say what the paper says they say. Every number I traced
comes from a result file. The tiers are honest, and the citations are real and quoted faithfully. The
corrections below concern wording and labels only.

## 1. Lean: recompile, own axiom audit and planted sorry

The environment was QuantumFluids: Lean v4.34.0-rc2 run directly, with `LEAN_PATH` set to the qf-lake build, the qf-lake
packages and the rc2 `lib/lean`, through the producer's `contribution/run_lean_rc2.py` on cores 4-7. Disk 2 was I/O-starved
during these runs. I warmed the page cache with `warm_siblings.py` using `h8_maps.txt`.

| File compiled | sha256 | rc | time | Result |
|---|---|---|---|---|
| copy of `contribution/Autoresearch_SkBoundShape.lean` (copy sha `fac6c85f…9454`, identical to the claimed file) plus my appendix | `5b642c05…13ca` | 0 | 1115.8 s | 26 claimed `#print axioms` lines, all `[propext, Classical.choice, Quot.sound]`. My planted `s4_planted_sorry` shows `[propext, sorryAx, Classical.choice, Quot.sound]`. |
| `contribution/Autoresearch_SkBoundShapeControls.lean`, unchanged | `0beb41c9…2ed5` | 0 | 1112.7 s | `ctl_sorry` shows `sorryAx`. `ctl_axiom` shows `…ctl_cheat`. Both are caught, and the file still exits 0. |
| copy of round-1 `H8/Autoresearch_SkBound.lean` (sha `7ca35dd1…1c75`) plus a fidelity appendix | `e060ee53…ff15` | 0 | 10.4 s (warm) | 11 round-1 lines within the allowlist. A planted sorry shows `sorryAx`. |

My appendix adds the following checks. Each compiled with axioms only from the allowlist:
- `s4_val : sBog 1 1 2 ^ 2 = 4/5`. The definition is not degenerate.
- `s4_strict : sBog 1 1 2 < √(2/(2·1))`. The bound is strict away from `k = ks`, so it does not hold trivially as an equality.
- `s4_disp_nonvacuous`. The hypotheses of `diffraction_test_dispersion` (`hfeyn`, `hpeak`, `S > 0`) can all hold at once: with `S = 1` and `epsSq = 0` it concludes `0 ≠ bogoliubovSq 1 1 1`.
- `#print axioms` on the owner lemmas `not_bogoliubov_of_structure_factor` and `feynman_ge_iff`, both within the allowlist.
- Definition fidelity, by `rfl` against the imported `DualLength.olean`: `bogoliubovSq hc ks k = (hc*k)^2 + (hc*k^2/ks)^2`, `ell ks k = 1/k + k/ks^2` and `dualLength hc k ε² = ε²/(hc^2 k^3)`. These match `lean_src/DualLength.lean` (sha `a28ce47e…`, the value in the paper). The QuantumFluids `.git/HEAD` is `10f74daf1b39d2ac51a785452329fff0003cfc83`, as the paper says.

I also ran Elenchus `tools/elenchus_check.py` on the claimed file and the controls file, with the same `LEAN_PATH`. It exited 1. Its only findings
are `INHERITED_SORRY` on `ctl_sorry` and `BAD_AXIOM` (`ctl_cheat`) on `ctl_axiom`, both in the Controls file, which is the tool's own positive
control. It reported nothing for `Autoresearch_SkBoundShape.lean`.

Statement adequacy:
- The hypotheses `0 < hc, 0 < k, 0 < ks` are natural.
- `feynman_sBog_exact` and `epsBog_eq_epsFree_div_sBog` hold by construction, and the paper says so in three places.
- `diffraction_test_dispersion` carries Feynman's inequality as the explicit hypothesis `hfeyn`, and the paper and ledger say Tier A covers only the implication.
- The claimed module imports only `DualLength`. It imports no openai/math module and depends on no triangular-lattice theorem, so the upstream `universal_energy_minimum` conditionality and the inf <= inf cases do not apply. The paper says this correctly.

## 2. Numbers trace to result files

- `data/*.json` is byte-identical (sha256) to `crates/qf-gpe2d/results/bogoliubov_sk/*.json` in the rusty worktree.
- `gen_numbers.tex` macros are computed by `gen_inputs.py` from those files. I spot-checked these against `linear_response_summary.json`:
  - all 14 gate values;
  - `RefEpsB` = `informational.reference_max_rel_err_vs_epsB` = 0.01227853;
  - `TangFine` = −3.5619e-9;
  - the dt-convergence arrays, the Lean shas and the Lean seconds against `compile_main.json`/`paper_recompile_*.json`. The producer's stdout has 0 warnings and 0 errors.
- **Re-run 1 (helium, Tier X evaluation):** `helium_tier_l.py /tmp/h8audit/helium_rerun.json`. The output JSON is identical (`==`) to `data/helium_tier_l.json`. It gives ks = 3.0038 Å⁻¹, threshold 0.5662 at Q_R, a silent set of 18 points from 0.05 to 0.90, 54 undecided points from 0.95, S_up = 2.66 at k = 1.95, and ε/ε_B values of 0.205 and 0.176.
- **Re-run 2:** `which_strang.py tests/python_cross_check.rs` gives reuse 2.48e-16 and strang 0.155, matching `data/which_strang.out`.
- **Table VI transcription:** an independent token-triple match (`/tmp/h8audit/check_table.py`) found all 73 (k, ε, err) rows of `TABLE_VI` in the stored alphaXiv extraction. I also confirmed rows 1.90/0.7427 and 1.95/0.7459 in a fresh alphaXiv read of arXiv:2012.09067 p. 26.
- **Gate audit:** `bound_g1_max_S_over_bound_minus_1` and `bound_g1_ratio_at_x_near_1_minus_1_abs` are bit-identical (−/+1.3808433e-3). I checked whether this means a vacuous gate. It does not. Both are the *measured* `S_freq/bound − 1` at the same sweep point (x = 1.0772173, where the maximum occurs). The exact-theory value there is −1.3809123e-3, so measurement and theory differ by 6.9e-8, which equals the recorded frequency error at that point.
- The cargo test log shows 9 + 5 + 1 = 15 passed. `cargo_fmt.log` (`--check`) shows exit 0, and `cargo_clippy.log` shows exit 0. I could not re-run cargo, because the session's worktree-isolation guard refuses `taskset … cargo test`. That is a limitation of this audit, not a finding.
- **Traces only to producer prose:** "wall time 409 s" (main.tex §Reproducibility) appears only in `contribution/NUMERICS.md` ("wall 409.11 s"), not in a machine-written result file. This is minor.

## 3. Human proof, step by step

I checked Steps 1-12 by hand. All are correct:
- Step 2: the closed form k²/(ks²+k²).
- Step 3: the equivalence with k(k−ks)² ≥ 0.
- Step 5: the identity 1/k + k/ks² − 2/ks = (k−ks)²/(k ks²).
- Step 7: ks < √(ks²+k²) < ks+k, and relative error k/(ks+k) < k/ks.
- Step 8: 1−S ≤ 1−S², since 0 < S < 1.
- Step 10: the sum-rule derivation of ε S ≤ ε₀ from S(k,ω) = 0 below ε, the zeroth moment and the f-sum rule.
- Step 11: the chain ending in 2x ≤ 1+x². It actually gives ε² < ε_B², which is stronger than ≠.

Section 2 conventions check out: ks = 2mc/ħ = √2/ξ, (u−v)² = ε₀/ε_B, and 2gn·ε₀ = (ħck)². The GP linear-response formulas also check out:
A(t) = (n k² ε/ω) sin ωt from continuity after an impulsive phase, S_amp = A_max/(2nε) = ε₀/ω, and the density normalisation in
`density_cos_amplitude`.

## 4. Tiers and overclaiming

- Tier X never supports a claim. BS-X rows carry `claim_licence: false`, and the paper repeats "supports no claim".
- The ⁴He section explicitly does not claim that the roton peak exceeds the threshold. Novelty is disclaimed ("the core inequality is (k−ks)² ≥ 0").
- I re-ran the ledger gate (`tools/ledger.py ledger/ledger.json --evidence-dir ledger/evidence`). It exits 1 with 0 blocks and 8 `LEDGER_UNAUDITED_TIER_A` flags, matching `gate_output.txt`. The run-1 tier inversion (BS-C-0004 resting on BS-X-0003) was removed honestly.
- I found no breakthrough wording.

## 5. Citations

I verified these against fresh alphaXiv reads:
- **Godfrin et al. arXiv:2012.09067v1.** Authors and title match. c = 238.3 ± 0.1 m/s at SVP (p. 2), m₄ = 4.0026032 g/mol (p. 3), and Table VI (p. 26) all match.
- **Beauvois et al. arXiv:1802.08120v3.** Authors and title match. Table I at P = 0 gives Δ_R = 0.7416(10) meV, Q_R = 1.9260(2) Å⁻¹ and μ_R = 0.1240(4), all matching.
- **Shammass et al. arXiv:1207.3440 (v2).** Authors and title match. "The experimental values in Fig. 3 have been multiplied by a factor of 1.5, in order to agree with the 2D GPE simulation for low" is verbatim.
- **Feynman, Phys. Rev. 94, 262 (1954).** This appears in Shammass's reference [16] and at line 6583 of the Godfrin extraction, as the paper says. The paper honestly notes that the original was not read.
- **Zenodo 10.5281/zenodo.23293429.** This DOI is recorded in `papers/universal_optimality_tiered/zenodo_doi_v2.txt`.

Elenchus `tools/citation_check.py` produced the following real output:
- With an honest `kind: data_value`, BS-L-0001 is **REFUSED** with `CITE_KIND`.
- With `kind` forced to `theorem`, used only as a probe of whether the quote is verbatim, both BS-L-0001 (against the Godfrin extraction) and BS-L-0004 (against the Shammass excerpt) are **ACCEPTED**, so the quotes appear verbatim.
- So this paper's Tier L (verbatim data and quote citations) is looser than Elenchus's L (theorem statements only). This is nonblocking, because the cited items are data and I verified them independently. The BS-L-0004 source is a producer-written excerpt file, not the full extraction.

## 6. Dataset provenance and licence

- A re-query (`HfApi.list_datasets`) of "structure factor", "superfluid helium", "neutron diffraction", "Bragg spectroscopy" and "radial distribution function" gave 0, 0, 1, 0 and 0 hits. The single hit is `popoff4rtem/2D-Neutron-Diffraction-Dataset-for-Discriminative-Models` at sha `648119c2030c5352c37a305deb74aa8ec84a4402`, with tags `license:mit` and `region:us`. All of this matches `hf_search.json` (30 queries) and `hf_neutron_card.json`.
- `/home/callensxavier_gmail_com/hf-data/bogoliubov_sk/` holds only `README.md` (24 B) and the HF cache metadata. No `.pkl` was downloaded.
- The null result is reported honestly. It still leaves a gap in the user's request ("select HuggingFace data set to illustrate"): no HF dataset illustrates the paper. The real-data illustration is the Godfrin Table VI, which is not hosted on the Hub.

## 7. publication_meta.json

The following match what I recomputed: Lean shas, Mathlib commit, QuantumFluids commit, rusty commits, 26 statements, 24 ledger claims, 8 flags, 4.1e-5, 14 gates, 0.5662, 0.90/0.95 Å⁻¹ and 30 queries.

The rusty commits were read from loose objects without git:
- HEAD is `fdd6d2d6…`.
- Its parent is `e1449988…`, whose parent is `47ef5044…` = `origin/main`.
- No `origin/physics/ar-bogoliubov…` ref exists, so "not pushed" holds.

The diff itself was not run, because `git` against that worktree is blocked by isolation. I read `src/lib.rs` (Splitting, `step_inplace`, `evolve_observe`), `src/linear_response.rs` and `tests/linear_response.rs` directly. `step`/`evolve` still use `PythonReference`, and `Strang` recomputes |ψ|² after the kinetic step, which is a correct symmetric Strang step.

## Corrections (nonblocking)

1. **Upstream split-step wording.** The abstract says "the upstream split step is not the symmetric Strang composition", and the meta says "the upstream Python split step, as pinned". No `solver2d.py` exists on this machine. The evidence is only that the pinned 4×4 data in `tests/python_cross_check.rs` are reproduced by the reuse composition to 2.5e-16. Reword to: "the pinned reference data are reproduced by a non-Strang (reused-phase) composition; the upstream source was not inspected". Also say that the rusty crate's own `step`/`evolve` use this same composition.
2. **Table 1 label.** The row "|S/bound−1| nearest k=ks (x=1.0772; exact-theory value) 1.381e-3" shows a *measured* value, which agrees with the exact theory −1.3809e-3 to 7e-8. Change the label to "measured; exact theory 1.3809e-3". Also note that the max gate and this gate are the same point.
3. **Module doc.** `src/linear_response.rs` line 7 says it evolves "with the crate's Strang split step". The crate default is PythonReference, and `measure` uses `cfg.splitting`. Reword in a later rusty commit. The paper text is unaffected.
4. **⁴He wording.**
   - Calling the bound "conservative" (ε − err) does not apply at k = 0.05 and 0.10, which have no error bars in Table VI. The margins there are large.
   - The roton S_up = 2.66 is at the tabulated k = 1.95 (threshold 0.5697), but the text sets it beside the Q_R threshold 0.5662. State both.
5. **Tier L scope.** Note in the Tiers paragraph that L here covers verbatim data and quotes, which Elenchus `citation_check.py` does not accept as theorem-kind.
6. **Provenance of "409 s".** Either point it to `NUMERICS.md` or have the example write its wall time into `linear_response.json`.
7. **HF gap.** Keep the null-result section as it is, and state plainly in the abstract or limitations that the requested HuggingFace illustration was not delivered.

## Not checked

- I did not re-run cargo build or test (isolation guard).
- I did not run `git diff origin/main` in the rusty worktree (isolation guard).
- I did not run the full GP sweep (409 s, and it needs cargo).
- No human has reviewed statement adequacy.
