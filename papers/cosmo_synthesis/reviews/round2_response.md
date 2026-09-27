# Response to round-2 referee reports

Manuscript: `papers/cosmo_synthesis/cosmo_synthesis.tex` (rebuilt: pdflatex twice, rc 0, 0 errors, no undefined references, pass-2 stdout in `papers/cosmo_synthesis/pdflatex_pass2_stdout.txt`, **0 overfull boxes** (the one disclosed box is fixed), **23 pages**).
Written by the revising agent (Claude, Claude Code), not a person. Every new number comes from tool output produced in this session.

## What was run

- New script `results/cosmo_synthesis/round2_response_checks.py` writes `results/cosmo_synthesis/round2_response_checks.json`. It covers:
  - the G2 attribution range and MC error;
  - the T2 resolution with DESI's MC error;
  - a CAMB re-run at N_eff = 3.046 for the five Aubourg validation points;
  - the DR1 grid step;
  - the P2 Omega_m moments;
  - the DR2 z > -1 Lean test;
  - Mathlib .olean counts;
  - the lake-root imports.
- The exact Lean bytes that were checked are kept as `results/cosmo_synthesis/dr2_zgtm1_check.lean` (sha256 `ca31d646…`). Both new files are in the paper's sha256 table.
- `gen_numbers.py` has a new `round2()` section and now produces 472 macros (was 439). Every new number in the text is a macro traced in `number_manifest.json`.
- `results/cosmo_synthesis/literature_search_log_round2.json` records how the new citations were found.
- `round1_response_checks.py` was **not** re-run. It would re-query `gh` and change a hashed JSON for no scientific reason.
- Papers re-fetched or newly fetched via alphaXiv `answer_pdf_queries` before citing: 2411.00072, 2603.20179, 2504.03424, 2511.14631, 2510.26887 (Sec. 3.7), 2503.14738 (Sec. III.C.2, footnote 12) and 2404.03002 (Sec. 2.5).

## Statistics / cosmology referee

**M1 (major) — "The T2 PARTIAL is this mechanism". FIXED.**
- Sec. 3.2 now says the PARTIAL is "*consistent with* this mechanism, but the numbers do not establish it". The same sentence gives:
  - 0.183 for DR1 Sec. 8's 101.8 and 0.046 for Sec. 6's 101.9;
  - 0.11–0.25 across the ±0.05 rounding of 101.8;
  - the 2000-step G2 chain (ESS 2115), with an MC error of 0.028 Mpc on its mean, i.e. ±0.038 km/s/Mpc.
- It concludes that the mechanism accounts for about 0.05–0.25 of the observed 0.167, and that 0.183 ≈ 0.167 is not evidence for it.
- Sec. 4.3 and the Limitations "Partial result" bullet now use the same macros and the same wording.
- For symmetry, the T1 sentence ("The T1 strict PASS partly reflects G1 landing at ...") now reads "is likewise only consistent with G1 landing at ...; we do not attribute it to that offset".
- All values are recomputed by the script. They agree with the referee's numbers to the printed rounding.

**m1 — footnote 12. FIXED.** Sec. 4.5(a) now reads "per galaxy/quasar tracer (C = 0.61 for Lyα)". It also says the nested form holds for the galaxy and quasar bins, which is all the argument needs. Re-read in 2503.14738v3, footnote 12.

**m2 — DESI's own MC error at the T2 boundary. FIXED.**
- Sec. 4.3 now says that DESI's convergence floor (ESS ≳ 10³, DR1 Sec. 2.5, re-read) implies up to ≈0.025 on 68.53, plus ±0.005 rounding.
- The combined resolution is ≈0.029. The 0.017 margin is 0.58 of it, so the boundary is not statistically resolved, as fit.json's note says.
- The text says explicitly that the verdict is PARTIAL "and stays".
- The 0.025 is labelled an upper estimate, because ESS ≳ 10³ is a floor.

**m3 — DR1 grid step. FIXED.** Sec. 4.1 now gives the 141×141 grid, the steps 0.00143 (Omega_m) and 0.179 Mpc (hr_d), and the grid chi2 12.7562. It adds that the grid minimum is 1.3 and 0.8 grid steps from the optimizer minimum, computed by `gen_numbers.py`, not typed, and words this as "within about one grid step". The step values are parsed from `fit_desi_bao.py`.

**m4 — the 0.029% vs 0.021% question. FIXED, but the result differs from the referee's proxy conclusion.**
- We did not adopt the eq.-17 proxy. We re-ran CAMB 2.0.4 at N_eff = 3.046 for the five validation points.
- CAMB's r_d(3.044)/r_d(3.046) − 1 is (6.7–6.9)×10⁻⁵, close to the eq.-17 factor of 6.5×10⁻⁵.
- Against the 3.046 CAMB values:
  - the worst point moves from −0.0292% to **−0.0224%**, which is still above 0.021%;
  - the other offending point moves from −0.0272% to −0.0204%, which is inside.
- So 1 of 5 points still exceeds the stated accuracy. The paper says that the N_eff convention explains most but not all of the excess, and that a ~10⁻⁵ remainder was not traced.
- The preregistered comparison (2 of 5 against the 3.044 table) stays the reported one.
- The referee's proxy said the worst point would sit "at the stated 0.021%". The direct run puts it 0.0014 percentage points above.

**m5 — P2 Omega_m pull moments. FIXED.** Sec. 3.3 lists them as report-only: mean −0.131, s.d. 0.944, standard error of the mean **0.094**. The referee wrote "SE 0.10"; 0.944/√100 = 0.094.

**m6 — DR2's own lower-bound sentence, and the scope of rho = 0.57. FIXED, with one wording departure.**
- Sec. 4.5(b) now quotes DR2 Sec. III.C.2: "~2.6σ" for C ≈ 0.57, and "sets a lower limit of the discrepancy at the 1.9σ level" with no correlation.
- It states that applying 0.57 to the whole parameter-level covariance is an illustration, not an estimate.
- So that the quote is not selective, it also gives DR2's 2.3σ / 1.5σ for DESI's reanalysis of SDSS. It notes that our eBOSS run uses the published SDSS DR16 likelihoods, which are what the 1.9–2.6σ figures refer to.
- We did **not** write that 0.57 belongs to "the bin pair with the largest footprint overlap". The fetched text supports only that it is the one pair for which DR2 quotes C, and the text says exactly that.

## Formal-methods referee

1. **Abstract, "each model". FIXED.** The abstract now says "each closed-form model", and adds that for the H0 run only the secondary fitting-formula r_d has a Lean skeleton and the primary CAMB r_d has none.
2. **"Second environment" not an independent toolchain. FIXED.**
   - The abstract now says the re-check is "against a fully built Mathlib (same Lean binary and Mathlib commit, so this tests independence from the partial build, not from the toolchain)".
   - Sec. 3.4 gives the measured counts: 3431 Mathlib .olean files for 8370 sources in env 1, and 8370 in env 2. They are counted by the script and match the referee's counts.
   - The Limitations bullet on the Lean gate says the same.
3. **z > −1 "which we did not test". FIXED; re-tested by us, not taken from the referee's /tmp file.**
   - `E2_pos_zgtm1` and `E_pos_zgtm1`, with hypothesis −1 < z, were appended to a copy of the DR2 file:
     - the E2_pos tactic script is byte-identical (checked by the script);
     - E_pos differs only in the lemma it calls (also checked).
   - Both compile in the pinned build with `lake env lean`: rc 0, both `#print axioms` outputs are `[propext, Classical.choice, Quot.sound]`, no sorry warning.
   - The bytes are kept at `results/cosmo_synthesis/dr2_zgtm1_check.lean`.
   - These sections are updated: Sec. 3.4, the Sec. 3.6 referee bullet, novelty item 3 and the Limitations bullet "Lean statements not changed".
   - All of them say the preregistered domain is recoverable at no proof cost for these two theorems. The shipped file stays drifted only for audit binding.
   - The monotonicity and D_C theorems were **not** re-tested on z > −1, and the paper says so.
4. **Modules not in the project's lake build. FIXED (disclosed).**
   - Sec. 3.4 and Limitations now say that all kernel checks are single-file runs and that no `lake build` of the root is recorded.
   - The script counted the imports:
     - the worktree's `formal/ANSE.lean` imports all four modules;
     - the main checkout's imports `ANSE.BAO_FlatLCDM` twice and none of the three new modules.
   - We did not run `lake build`. It would write build products into the shared checkout's `.lake`, which is outside this synthesis' write scope.
5. **"one-line". FIXED.** The wording is now "short identities or positivity statements", with a parenthetical saying that "short" refers to mathematical content and that some proofs take three tactics.

## Novelty / positioning referee

**Major 1 — TOPO (2411.00072) uncited. FIXED.**
- Fetched and read. The Blind-analysis paragraph now describes it from the paper:
  - a signed Analysis-Hash of code commits and input files, published on a timestamped medium (a public blockchain in their example) before running;
  - Merkle-tree roots over the time-ordered MCMC chain, with a verifier;
  - a demonstration with Cobaya and CLASS on BAO likelihoods that include SDSS DR16.
- The paper calls our hash-locked unread fit a one-file instance of that idea, "timestamped only by file mtime".
- Novelty item 1's hash-lock bullet uses the same phrase ("a local version, timestamped only by file mtime, of the commitment that TOPO timestamps publicly").
- The "Preregistration provenance" limitation now names a timestamped pre-fit commitment as the fix.

**Major 2 — agentic prior work. FIXED, with scoped claims.**
- **AI Cosmologist (2504.03424):** described as an autonomous agentic system for cosmology/astronomy data analysis, shown on ML tasks (Galaxy Zoo 2, Quijote), not on reproductions.
- **JFC (2603.20179):** read this time; round 1 had left it unread. It is named as the closest architectural precedent. The paper quotes "multi-agent review replaces the human feedback loop" and "human oversight is concentrated at a single formal unblinding gate", and mentions the append-only experiment log. For the CMS H→ττ analysis we use JFC's own wording, "checked against, and consistent with, a published CMS measurement"; we do not call it a reproduction.
- **We added what the referee did not ask for:** JFC is *stronger* than our pipeline in one respect. It has staged blinding (Asimov, then 10%, then full) and a human unblinding gate, whereas we have neither. This is stated in the Blind-analysis paragraph and in novelty item 1.
- **2511.14631:** described as plots treated as VLM-judged checkpoints with auditable traces.
- **What we did not claim:** the referee asked us to say that JFC and cmbagent do not preregister or hash-lock. We wrote only that we did not find these in the pages we read, and that we do not claim the systems lack them.
- **Referee specifics we could not verify and did not use:**
  - "cited by 2507.07257";
  - "cited by the already-cited Grosso et al.";
  - "no-repeat-trial cross-model comparison".
  They are listed in `literature_search_log_round2.json`.

**Minor — DR2's 1.9/2.6σ next to N_σ = 0.88. FIXED.** This is the same passage as stats m6. Sec. 4.5(b) now says the parameter-level number does not mean "no tension anywhere", and the Limitations bullet carries the 1.9–2.6σ figure.

**Minor — Denario Review module as a model-referee precedent. FIXED.** Sec. 5 cites Denario Sec. 3.7 (`referee.md`) and the VLM judge of 2511.14631 as the nearer, cosmology-native precedents, ahead of the AI Scientist.

**Minor — search log. FIXED.** `literature_search_log_round2.json` names the two missed axes. It also says honestly that the round-2 papers were supplied by arXiv id in the referee report and were fetched and read by us, and that we ran no new keyword sweep. 2603.20179 is now read and cited. The round-1 log is left unchanged as a historical record.

**Optional items:**
- (i) PhysProver 2601.15737 and AxQM 2609.05157: **not done.** We did not read them, so they are not cited. They are logged as named but unread.
- (ii) The Ferri et al. caveat (RSD, older Planck likelihood): **not done.** We did not re-verify it this round. The existing sentence already limits the Ferri comparison to "combined with Planck in the CPL model".
- (iii) ReplicationBench Sec. 5.3: **not done.** Not verified by us this round.
- (iv) Subtitle: **FIXED.** It now reads "three preregistered DESI/SDSS reproductions and one earlier reproduction as one methodology study".

## Unchanged and still open (all disclosed in the paper)

- **T2 stays PARTIAL.**
  - The gate-tolerance explanation is now stated only as consistent with the result and post-hoc.
  - The boundary is not statistically resolved.
- **One of five Aubourg validation points still exceeds 0.021%** after the N_eff correction (0.0224%). The remainder was not traced.
- **The DR1 χ² offset (0.08) is unexplained.**
- **The Tier A audits are model audits.**
  - The H0 audits are bound to a stale source hash.
  - Two H0 theorems are unaudited.
  - The ledger gate does not check claim-to-blob correspondence.
  - The ledgers are outside this synthesis' write scope.
- **The DR2 drift remains in the shipped file.** z ≥ 0 is kept for audit binding, and only E2_pos/E_pos were re-tested on z > −1.
- **The four Lean modules are not in a recorded `lake build`.**
  - Env-2 is not an independent toolchain.
  - `lean_runner.py` was not used.
- **The preregistrations were not committed or timestamped before the fits.**
- **No blinding, and no human review of any component.**
- **The repository completion checks** (`antigravity_guard.py`, `test_rigor_guard.py`, `pytest tests/`) were not re-run for this synthesis, and the recorded runs do not all pass.
