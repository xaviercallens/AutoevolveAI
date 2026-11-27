# Hostile pre-deposit review of v2.1 (HEAD bfdbd2a, branch main)

Reviewer: independent machine + literature check, 2026-10-19. No tracked file was modified.
Scripts and outputs: `papers/dyadic_ns_regulator_elenchus/review_v21/` (`brute_force_checks.py`, `.log`, `.json`,
`lean_gate_rerun.log`, `publish_dry_run.json`, `paper_v21.txt`, `fig{1,2,3}.txt`).

Short verdict: the technical corrections of the first-edition review are real and every number in Tables 2-3, the
witnesses and the torus spectrum reproduce from scratch; the Lean gate reruns clean. But the manuscript still contains
one false formula inside a theorem statement, one fabricated bibliography title (carried as "verified" in the ledger),
an "open band" framing that the paper's own references contradict, and the Section 6 availability claims are false
until `main` is pushed. The deposit bundle as built today would also carry this review directory. Fix the BLOCKING
items (all small) before running the publish script.

File abbreviations: `TEX` = `papers/dyadic_ns_regulator_elenchus/Dyadic_NavierStokes_Regulator_Elenchus_Paper.tex`
(identical to `results/.../*.tex`; the template is `scripts/dyadic_ns_regulator_elenchus/run_pipeline.py`, so every
tex fix must be made in the template and the pipeline rerun); `SPEC` = `formal/ANSE/DyadicNavierStokesRegulatorSpec.lean`;
`LEAN` = `formal/ANSE/DyadicNavierStokesRegulator.lean`; `META` = `papers/dyadic_ns_regulator_elenchus/publication_meta.json`;
`PUB` = `scripts/publish_dyadic_ns_regulator_zenodo.py`.

## Findings

### BLOCKING

1. **False formula in Theorem 3.2 (`TEX:203`, template `run_pipeline.py:1192`).** The "more generally" clause states
   `3S/D_alpha = 5400/(225 + 64*2^(2+2alpha)) * 2^((1-2alpha)m)`. It is off by a factor 17: with a_m = 15/17,
   a_{m+1} = 8/17, k_m = 2^m one gets `3S = 2^{3m} 5400/4913` and `D_alpha = 2^{(2+2alpha)m}(225 + 64*2^{2+2alpha})/289`,
   so `3S/D_alpha = 5400 / (17 (225 + 64*2^{2+2alpha})) * 2^{(1-2alpha)m}`. Check at alpha = 1/2, m = 0: the theorem's own
   numbers give 3S_1/D_{1/2,1} = 5400/12529 = 0.4310, the printed formula gives 5400/737 = 7.327
   (`brute_force_checks.log`: two FAIL lines; 12529 = 17 * 737). The m-dependence `2^{(1-2alpha)m}` and the
   "scale-invariant iff alpha = 1/2" conclusion are correct. This clause is not in the Lean statement
   (`Spec_thm_single_step_coercive_damping_counterexample` covers only m = 0, alpha = 1/2) although the theorem header
   cites Lean, and the consistency report does not test it. Fix: insert the factor 17 (or write the denominator as
   `3825 + 1088*2^{2+2alpha}`) and mark the clause as prose-only.

2. **Fabricated reference title (`TEX:333-334`, template `run_pipeline.py` bibliography; ledger `DNS-L-0003`).**
   The paper cites Barbato, Morandin, Romito as "Smoothness for the dyadic model for fluid equations: the anomalous
   scaling regime", Nonlinearity 24(11), 3083-3097, 2011. The article at DOI 10.1088/0951-7715/24/11/004 (Nonlinearity
   24, 3083, 2011; arXiv:1007.3401) is titled **"Smooth solutions for the dyadic model"** (checked at iopscience.iop.org
   and arxiv.org on 2026-10-19). The Elenchus ledger record `DNS-L-0003` (tier L, status `verified`,
   `results/dyadic_ns_regulator_elenchus/ledger_validation.json`) carries the invented title, so the "verified
   literature tier" is attesting to a title that does not exist. The other two references (Katz-Pavlovic TAMS 357(2)
   695-708; Cheskidov TAMS 360(10) 5101-5120) match the publishers' records. Fix the title in the template and in the
   ledger builder, then rerun the pipeline (Merkle root changes).

3. **Section 6 availability claims are false at the moment of writing (`TEX:321`).** `origin/main` is at 69524fc;
   HEAD is 2 commits ahead and unpushed (`git status -sb` -> `[ahead 2]`; GitHub reports `pushedAt 2026-10-16`).
   `git ls-tree origin/main` contains **none** of: `papers/dyadic_ns_regulator_elenchus/`, `results/dyadic_ns_regulator_elenchus/`,
   `scripts/dyadic_ns_regulator_elenchus/`, `formal/ANSE/DyadicNavierStokesRegulator*.lean`, `PUB`. The repository is
   public, so after `git push origin main` every path the paper names is tracked at HEAD (verified with `git ls-files`:
   both Lean files, `run_pipeline.py`, `exact_dyadic_harness.json`, `lean_spec_gate.json`, `ledger.jsonl`,
   `ledger_validation.json`, `consistency_report.json`, `CONSISTENCY_REPORT.md`, tex, pdf, `META`, `PUB`).
   Exception: **"replication manifests"** are not in the repository. `MANIFEST.json` is written to `dist/` (gitignored,
   `.gitignore:8`) and exists only inside the Zenodo bundle. Reword to "the SHA-256 manifest is in the Zenodo bundle".
   Push before depositing; otherwise the deposited PDF points at a repository that lacks every file it names.

4. **The deposit bundle will carry this review and two stale JSON files (`PUB:62-80`).** `bundle_members()` takes
   every file under `papers/dyadic_ns_regulator_elenchus` and `results/dyadic_ns_regulator_elenchus` (only
   `.aux/.log/.out/.pyc` excluded). The dry run (`publish_dry_run.json`, 26 files) already lists
   `papers/dyadic_ns_regulator_elenchus/review_v21/brute_force_checks.{py,json}` and `publish_dry_run.json`; once this
   `REVIEW.md` exists it is bundled too. Also bundled, and tracked at HEAD: `results/.../pipeline_summary.json`
   (contains `"frontier_positive_provability_ratio": 0.6`, i.e. the scorekeeping the response paragraph says was
   removed) and `results/.../zenodo_publication_receipt.json` (the v2.0 deposit receipt; it will be overwritten by the
   v2.1 receipt after publishing, but the copy in the bundle will be the v2.0 one). Before running `PUB` without
   `--dry-run`: move or delete `review_v21/`, or add an exclusion list to `bundle_members()`. No `PEER_REVIEW*` or
   `peer_review_scorecard*` file is in the manifest, on disk, or anywhere in git history for this paper (verified).

### SHOULD-FIX

5. **"Open band alpha in (1/3, 1/2)" framing contradicts the paper's own references** (`TEX:69` Table 1 "Open Band
   alpha = 2/5"; `TEX:160` "Obstruction in the Open Band"; Fig. 2(a) label "Obstructed Band"; `SPEC` docstring item 10
   "open fractional dissipation band"; ledger `DNS-A-0010` "Open-band"). Cheskidov 2008 (cited) proves local regularity
   for alpha > 1/3 and global regularity for alpha >= 1/2; Barbato-Morandin-Romito 2011 (cited) prove well-posedness of
   **positive** solutions in the scaling range corresponding to Navier-Stokes, which is exactly the positive-cone
   setting this paper uses for H6; and Zhang, arXiv:2609.21312 (Sep 2026) states global regularity for alpha >= 1/3
   for non-negative data on classical geometric scales. H5 is an obstruction to one method (single-step Young plus
   L^2_t energy), which is a legitimate and correctly proved statement; it is not evidence that the band is open. Say
   "method obstruction" and cite the known regularity results; otherwise a reader of Table 1 takes "Open Band" at face
   value.

6. **Lean coverage of H10a is much weaker than the prose claims** (`TEX:43` "Every positive theorem ... is formally
   proved in Lean 4"; `TEX:45` item (vi); `TEX:250` theorem header). `Spec_thm_torus_two_section_spectral_degree_identity`
   (`SPEC:150-158`) quantifies over a real number n >= 2 and proves `6(n-2)+4 = 6n-8`, `0 < deg`,
   `1 - (-4)/deg = (6n-4)/(6n-8)` and `> 1`, with the eigenvalue -4 introduced by `let lam_odd_adj := -4`. Nothing in
   Lean counts triads, builds A, proves `A = 6(J-I) - 2P`, or computes any spectrum; those are prose-only
   (Theorem 5.1(3) proof) and the harness `torus_two_section_spectrum` table is formula evaluation, not enumeration.
   I enumerated the 2-section for m = 3 (n = 26) and m = 5 (n = 124) from the triad definition: `A = 6(J-I) - 2P`
   holds exactly, degree 6n-8, adjacency spectrum {6n-8 (x1), -8 (x n/2-1), -4 (x n/2)}, normalized Laplacian
   {0, 6n/(6n-8), (6n-4)/(6n-8)}; for m = 4 (2-torsion) the closed form fails, as the odd-order hypothesis predicts.
   So the mathematics is right; the attribution is not. State in the abstract and in Theorem 5.1 that Lean certifies
   the arithmetic consequences only. Same remark, milder, for Theorem 2.2(2) "every state with k_0^2 a_0^2 < Omega_N
   violates ..." (Lean proves the N = 2 witness only) and Theorem 3.2's general-m clause (item 1).

7. **Stale docstrings in the shipped Lean files (both in the bundle, both "frozen" by sha256 in `lean_spec_gate.json`).**
   `SPEC:10-12`: "structured at the 60% positive-provability / 40% formal-obstruction frontier", "6 / 10 hypotheses =
   60.0%", "4 / 10 hypotheses = 40.0%"; `LEAN:11-12`: "60.0% positively proved ... 40.0% formally refuted". `SPEC:30`
   (item 11, H6) still describes the **old** scaling-defeated formulation: "fails ... at alpha = 1, nu = 1 (a_0 = 10,
   a_1 = 2 yields net production +436 > 0)", which contradicts the Prop it documents (unit sphere, 15/17, 8/17) and the
   paper. `SPEC:21` (item 5) writes `2 D Omega_{N+2}` where the paper writes `Omega_{N+1}` (the index-convention fix of
   review item 5 was not propagated). `SPEC:24-25` and the theorem name still say "T-dual ... self-dual" where the paper
   now says "Kolmogorov UV/IR" (naming only). The consistency check `no_percentage_scorekeeping`
   (`run_pipeline.py:1374`) scans only the tex; `exact_dyadic_harness.json` (`positive_provability_ratio: 0.6`) and
   `pipeline_summary.json` (item 4) still carry the ratio. Editing the Lean files changes `spec_sha256`/`lean_sha256`
   and the ledger Merkle root quoted in `TEX:318`, so the pipeline must be rerun after the edit.

8. **`META` description over-claims and mis-states** (`META` "description"). (a) "ten coupled **frontier** hypotheses"
   and "Rather than restricting formalization to known textbook identities, we evaluate an open ten-hypothesis
   research programme" contradict the paper's own abstract, which says three items are elementary controls "rather
   than ... frontier claims". (b) "(i) we prove the general ratio-r cutoff-uniform enstrophy production bound
   S_N^2 <= 2 Omega_N^3" conflates H1 (an identity, ratio r) with H3 (a bound, dyadic r = 2 only, and not
   "cutoff-uniform" in the sense used for H7). (c) "(iii) we prove exact quadratic cancellation" - the phrase occurs
   nowhere in the paper (grep count 0). (d) "98.73% cross-scale triads" is a count ratio 3744/3792; the paper
   (`TEX:306`) calls it "98.73% cross-scale energy transfer", which is an interpretation, not a measurement. The title
   in `META` carries "(Revised Edition v2.1)" while the tex title does not; acceptable, but the tex title still says
   "Ten Frontier Hypotheses" (`TEX:33`) and `\newtheorem{hypothesis}{Frontier Hypothesis}` (`TEX:28`) is unused.

9. **Related identifier (`PUB:107`).** The script hard-codes `isNewVersionOf 10.5281/zenodo.23458238` (first edition).
   With `--new-version-of 23459268` Zenodo itself places v2.1 in concept 23459267 and links it to v2.0, so the manual
   link to the first edition (a different concept, otherwise unlinked) is the right one to keep. Do **not** point it
   at the concept DOI 10.5281/zenodo.23459267 (a record cannot be a new version of its own concept). Optionally add a
   second `isNewVersionOf 10.5281/zenodo.23459268` for explicitness; and after publishing, edit record 23458238 by
   hand to add `isPreviousVersionOf` -> the v2.1 DOI, which the script cannot do. The version string "2.1" and the
   edition-history sentence in `META` are consistent with `TEX:321`.

10. **Unverifiable framing in Section 4 (`TEX:211`).** "the truncated dynamics conserves both the mass S ... and the
    graded SHG Hamiltonian H_sigma" - no equations of motion are written anywhere, so the conservation claim cannot be
    checked and nothing downstream uses it. Either give the dynamics or present H_sigma as a functional and drop
    "conserves". Likewise the attribution of `p(alpha) = 1/alpha - 1`, `q(alpha) = 4 - 1/alpha` to [Cheskidov2008]
    (`TEX:152`) carries no equation reference; I did not verify it against the source.

11. **Response paragraph (`TEX:324`), item by item against this tex.** (1) true (924, harness-produced table, enriched
    1.3305; the stale 0.4278/894 appear only inside this paragraph as quotations). (2) true (`-1 - 4 + 18 = 13`,
    `TEX:136`). (3) "the '60% proved' scorekeeping is removed" - true of the tex, **false of the bundle** (item 7).
    (4) proofs present for Thms 2.2, 3.1, 4.1, 5.1 including `A = 6(J-I) - 2P` and the `(u,u,2u)` case - true.
    (5) inclusive index - true in the tex, not in `SPEC:21`. (6) Laplacian 0 - true (`TEX:264`, Fig. 3(b) plots only
    the non-trivial eigenvalues). (7) typography - Fig. 3(a) labels no longer overlap in the extracted text; "-0"
    absent from Table 2. (8) "both are above" - true only after the push (item 3). The withdrawal sentence is accurate:
    the "Peer Review Report" was never tracked in git, is not on disk, and is not in the manifest; the title no longer
    says "peer-reviewed". The three corrected v2.0-description statements are indeed absent from the paper and from
    `META`.

### MINOR

12. `TEX:45` (abstract, item ix): "fails at supercritical Reynolds number nu = 1/3" - nu is the viscosity; write
    "at nu = 1/3 (Re = 3)" as Table 1 and Theorem 3.2 do.
13. `TEX:45`, `TEX:306`, Fig. 3(a) legend: "D = 0.5716 in (0, 0.75)" / "Genuine Nonlinear Depletion Band 0 < D < 0.75" -
    the 0.75 threshold is never defined or justified.
14. `TEX:258-262`: "n >= 2 ... the adjacency eigenvalues are {6n-8, -8, -4}". At n = 2 (G = Z_3) the even zero-sum
    subspace is trivial and the spectrum is {4, -4} (brute force). State the multiplicities (1, n/2-1, n/2) or require
    n >= 4; `SPEC` uses `2 <= n` over the reals, where the statement is pure arithmetic and the issue does not arise.
15. "Unconditional" cubic bound (`TEX:45`, `TEX:67`, `TEX:119`): the Lean statement requires `k_{n+1} = 2 k_n`;
    "unconditional" means "no smallness condition on a". One clause would remove the ambiguity.
16. Table 1 H10 (`TEX:74`): "prime depletion D = 0.5716 (Proved)" is a tier-B exact computation, not a theorem; and
    what is "Refuted" for the odd shell is the hypothesis that it carries nonlinear dynamics - the amputation itself is
    Theorem 5.1(4). Reword the cell.
17. The spec gate's `spec_drift_rejected` control (`run_pipeline.py:526-533`) is a string replacement followed by a line
    count; it never invokes Lean and cannot fail. `spec_check_passed` is kernel verification plus the count of
    `example : Spec_thm_` lines (12). The real statement-matching is Lean elaboration of those 12 examples (which I
    reran); the gate does not compare Lean statements with the paper's prose, which is what items 1 and 6 are about.
18. Section 6 "5-tier ledger (A > B > L > C > X)": tiers C and X are empty (12 A, 5 B, 3 L); fine, but say so.
19. `TEX:37` date "October 18, 2026" (deposit is 2026-10-19); figure PDFs in `papers/` and `results/` differ in md5
    (matplotlib timestamps) but are textually identical - harmless.
20. Harness `frontier_summary.hypotheses[H9].exact_witness` reads "R_eff(4, 1) = 4 >= 2", comparing R_eff with
    sqrt(alpha) rather than R_eff^2 with alpha as stated; cosmetic.
21. Other pipelines in the repository still generate scripted referee reports with invented personas and scores
    (reported, not fixed): `scripts/he3_kinetic_elenchus/run_pipeline.py:1544-1599` (three referees 9.7/9.6/9.8,
    overall 9.70, writes `peer_review_scorecard.json` and `PEER_REVIEW_REPORT.md`);
    `scripts/openai_math_mavnan_elenchus/run_pipeline.py:1449-1454` (aggregate 9.8, "ACCEPT");
    `scripts/ec_bsd_elenchus/run_pipeline.py:931-970` (three referee reports plus "Author / Pipeline Response");
    `scripts/phd_k3_pipeline/peer_review_k3.py:95-268` ("ACCEPTED FOR PUBLICATION", composite score /10). Tracked
    outputs of that kind: `paper/runux_formal_verification/PEER_REVIEW_REPORT.md`, `results/phd_k3_pipeline/review/*`.
    The literal strings "ACCEPTED_FOR_PUBLICATION" and "9.88" occur only in `vendor/` and `uv.lock`. If those papers
    were deposited with such reports, the same withdrawal is owed.

## Verified (independent recomputation unless stated)

- `|Lambda_6| = 924` for the closed ball `0 < |k|^2 <= 36` in Z^3 (open ball gives 894, the first-edition number).
- Ordered resonant triads `(k1, k2, k3) in Lambda_6^3`, `k1 + k2 = k3`: 398,190. Baseline balls M = 2..6: 32/426,
  122/6642, 256/30360, 514/122472, 924/398190 - all equal to the harness.
- Table 3, every row except the seed-dependent random control: |S|, f, |T(S)|, null `f^3 |T|`, D to 4 decimals:
  even sublattice 122/6642/7.2468; coordinate planes 300/25518/1.8724; perfect-square shell 108/846/1.3305
  (null 635.8); mod-3 shell 336/20034/1.0463; prime shell 236/3792/0.5716 (null 6634.5); odd shell 466/0/0.0000.
  Random control checked for internal consistency (f = 149/308, D = 1.0143). Densities 233/462, 9/77, 59/231 exact.
- Prime shell: 12 modes of norm 2; all 3792 triads contain a norm-2 mode; no axis mode; prime list = all primes <= 36.
  Square shell contains all 36 axis modes. Cross-scale fractions match the harness (prime 0.9873 = 3744/3792).
- Arithmetic witness: terms (-1, -4, 18), sum 13, and the NL-side sum `sum k_n^2 a_n NL_n = 13`; `3(1 + 8) = 27`.
- H2b witness: flux 40, Omega_2 = 161/2, 40 = 161/4 - 1/4 > 161/8 = 20.125. H3 witness: S_2 = 98, 9604 <= 4173281/4.
  H1 witness: 294 = 3 * 98. Shell progression N = 1..16 (Fig. 1) and ratio-r table (r in {1, 3/2, 2, 5/2, 3}) reproduce.
- Unit sphere: (15/17)^2 + (8/17)^2 = 1; 3S_1 = 5400/4913; D_{1/2,1} = 737/289 = 12529/4913; -7129/4913 at nu = 1;
  +3671/14739 at nu = 1/3. (The general-m formula fails: item 1.)
- Riccati table (Table 2), all 9 rows and all four identities `p + q = 3`, `2 - p = rho`, `r = (8a-2)/(3a-1)`,
  `s - 1 = 1/rho`; `p < 2 iff alpha > 1/3`; `rho >= 1 iff alpha >= 1/2`; alpha = 2/5 gives rho = 1/2, r = 6,
  theta* = 4, deficit 2. Harness rows agree.
- Torus 2-section (P = antipodal involution `P_{u,v} = delta_{v,-u}`, as `TEX:262` defines it): enumerated for m = 3, 5;
  `A = 6(J-I) - 2P`, degree 6n-8, spectra as in Theorem 5.1(3) and the normalized Laplacian `{0, 6n/(6n-8), (6n-4)/(6n-8)}`
  with the constant mode at 0. Harness torus rows m = 3..11 agree with the formulas. Even m = 4 breaks the closed form.
- Sigma table: weight ratios `2^{(3-sigma)N}` for sigma = 0..4 and N in {2,4,8,12,16}; only sigma = 3 and 4 are
  cutoff-uniform.
- Lean gate rerun (`lean_gate_rerun.log`, 21 s on the prebuilt Mathlib, toolchain v4.34.0-rc2): `lake build` of the
  Spec module and `lake env lean` of `LEAN` succeed; 19 declarations (12 theorems + 7 lemmas) each depend only on
  `propext, Classical.choice, Quot.sound`; zero `sorry`; the 12 `example : Spec_thm_... := thm_...` definitional checks
  elaborate. `sha256` of `SPEC`/`LEAN` equals `spec_sha256`/`lean_sha256` in `lean_spec_gate.json`.
- Lean statement vs prose, H1-H10: H1, H2a, H3, H4, H5, H7 (as an abstract real-sequence inequality with the cubic
  bound taken as hypothesis, which the prose states), H8, H9a, H9b, H10b match the theorem statements. Weaker than prose:
  H10a (item 6), H2b general clause and H6 general-m clause (items 6, 1).
- Ledger: 20 records (12 A, 5 B, 3 L), all `verified`, Merkle root `b201faae...a3a4da` equal in `ledger_validation.json`,
  `CONSISTENCY_REPORT.md` and `TEX:318`; four negative controls recorded.
- PDF: built 2026-10-18 23:31:19 from the HEAD tex (mtime 23:30:53), 10 pages, identical in `papers/` and `results/`;
  theorem numbering 2.1, 2.2, 3.1, 3.2, 4.1, 5.1 so "Thm 5.1(4)" in Table 3 resolves; the response paragraph is in the
  PDF; the stale strings `60%`, `peer-reviewed`, `0.4278`, `894`, `alpha_* = 1/4`, `2H_3` occur only inside that
  paragraph as quotations; `0.4288` absent. Fig. 3(a) bar labels (1.0143, 7.2468 clipped, 1.8724, 1.3305, 1.0463,
  0.5716, 0.0000) equal Table 3; Fig. 3(b) plots `6n/(6n-8)` and `(6n-4)/(6n-8)` only; Fig. 1 and Fig. 2 captions
  match their panel titles.
- Publish dry run (`--dry-run --new-version-of 23459268`): metadata = `META` title/description/keywords, version 2.1,
  licence cc-by-4.0, related identifiers GitHub (isSupplementTo) and 10.5281/zenodo.23458238 (isNewVersionOf). The
  v2.0 receipt confirms concept 23459267 / record 23459268.
