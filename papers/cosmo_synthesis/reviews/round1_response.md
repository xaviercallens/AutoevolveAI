# Response to round-1 referee reports (cosmo_synthesis.tex)

Date: 2026-09-27. Revised files: `papers/cosmo_synthesis/cosmo_synthesis.tex` and `gen_numbers.py`, plus new or rewritten scripts and
JSONs under `results/cosmo_synthesis/`:
- `run_lean_dual_check.py` (revision 2) -> `lean_dual_check.json`. The hand-edited revision 1 is kept as `lean_dual_check_v1_handedited.json`.
- `dr1_chi2_offset_check.py` -> `dr1_chi2_offset_check.json`
- `round1_response_checks.py` -> `round1_response_checks.json`
- `literature_search_log_round1.json`, which records the exact queries.

Every new number in the paper is a macro that `gen_numbers.py` reads from these JSONs. Nothing outside `papers/cosmo_synthesis/` and
`results/cosmo_synthesis/` was written. Where a fix would need a file outside that scope (run ledgers, frozen run scripts, Lean sources), the
defect is disclosed in the paper's Limitations section and marked NOT FIXED below. No verdict or tolerance was changed.

Three referee statements did not match the sources we fetched. The paper follows the sources, and the entries below give the details:
- stats minor 4 (DR2 convention)
- stats minor 5 (numeric consequence of the CAMB sign)
- novelty minor on ReplicationBench (which table holds the 22%)

---

## Referee 1: statistics / cosmology (recommendation: minor)

**S-M1 (major): H0 tolerances not coherent.** FIXED (disclosure; verdicts unchanged).
- `round1_response_checks.py` (key `h0_gate_propagation`) propagates the 0.25 sigma gate tolerance using the measured slope 0.49.
- Admitted |dH0|: 0.251 km/s/Mpc for DR2 (G1) and 0.445 for DR1 (G2). Both exceed the strict window of 0.15, and the DR1 value also exceeds the soft window of 0.33.
- The G2 offset of +0.134 Mpc (pull 0.10) implies +0.183, against an observed +0.167.
- The G1 offset of -0.020 Mpc implies -0.027.
- Added as a bold paragraph at the end of Sec. 3.2, in the abstract ("PASS versus PARTIAL does not isolate the BBN/r_d step"), and as a Limitations bullet.

**S-M2 (major): DR1 matched target and chi2 offset.** FIXED (comparison added); the offset itself remains OPEN.
- Sec. 4.1 and the abstract now compare against DESI's best fit: Om = 0.294, H0 r_d = 1.0194e4 km/s (Fig. 1 caption), chi2 = 12.66 for 10 dof (Sec. 3.2), all re-read from arXiv:2404.03002. Our 0.29389 / 101.937 matches to the printed precision.
- New `dr1_chi2_offset_check.py` refits DR1 with four background models:
  - primary: chi2 12.7405, i.e. +0.081
  - plus radiation: 12.7373
  - CAMB with massless neutrinos: 12.7374
  - CAMB with one 0.06 eV neutrino: 12.7378, i.e. +0.078
- Background physics changes chi2 by at most 0.003, so the candidate the referee suggested (radiation or neutrinos in the background) does not explain the offset. It is reported as unexplained in Sec. 4.1, the abstract and Limitations.

**S-m1: PTE versus N_sigma bound.** FIXED.
- The abstract, Sec. 4.5(b) and Limitations now say that N_sigma is a lower bound and the PTE an upper bound, and only if the cross-covariance is positive. The bound is model-dependent.
- `round1_response_checks.json` (key `overlap_sensitivity`) reproduces the referee's check. N_sigma is 0.877 at rho = 0 (equal to fit.json) and 1.344 at rho = 0.57 (PTE 0.18). The covariance stays positive definite over the whole rho grid.
- rho = 0.57 is labelled an illustration. DR2's C ~ 0.57 applies to the LRG2 / eBOSS LRG pair only.

**S-m2: nested sigma stated as fact.** FIXED, with a correction to the referee's reading.
- arXiv:2503.14738 Sec. III.C.1 does describe its DR1-DR2 comparison as assuming perfect correlation. Its joint sigma, however, uses C = sqrt(N_DR1/N_DR2) per distance (footnote 12). With sigma proportional to N^-1/2, that equals our nested form.
- The paper now states this and adds the literal C = 1 bracket: sigma = |s1 - s2| = 0.0061, giving 0.46 sigma. That row is also in Table 7.
- All three conventions (0.17 / 0.24 / 0.46) agree that the shift is insignificant.

**S-m3: CAMB cross-check sign.** FIXED, with a numeric correction.
- `camb_crosscheck.py` line 97 confirms the convention shift = primary fit - CAMB truth = +0.032 sigma.
- Sec. 3.1 now states the direction and gives the shifted DR2 Om pull: +0.037 becomes +0.005 with a CAMB model and -0.009 with radiation (`camb_shifted_pull`). The referee's range "about -0.01 to -0.04" does not match these computed values.

**S-m4: "6 positive controls".** FIXED. `gen_numbers.py` now counts distinct PC<n> ids, giving 5 (PC0-PC4). Sec. 3.3 notes that PC0 has quadrature and GL entries, which is why there are 6 JSON keys.

**S-m5: N4 wording.** FIXED.
- Abstract: "only marginally catches".
- Sec. 3.3 states:
  - margin 0.0137 = 1.3 times the T1 posterior-mean MC error of 0.0107 (std/sqrt(ess)), in key `n4_margin`
  - the shift is between MAP points, while the verdict uses posterior means
  - the wrong model has the lower chi2

**S-m6: `verdict_T2` uses G1.** DISCLOSED; the code is NOT FIXED (frozen script, outside write scope).
- Confirmed at `scripts/bao_bbn_h0/fit_real.py` line 262.
- Sec. 4.3 and Limitations state the deviation and that G2 passed (its `passed` field is true), so the verdict is unchanged.
- Also added to the list of process failures in Sec. 5.

**S-m7: 0.029% versus Aubourg's 0.021%.** FIXED.
- Sec. 4.3 now says that 2 of the 5 validation points (not 1) exceed 0.021%: -0.029% and -0.027%.
- The largest is at (omega_b, omega_cdm) = (0.02218, 0.119), inside the proxy validity window.
- Our CAMB table uses N_eff = 3.044 against Aubourg's 3.046, which may contribute. This is stated as unresolved (`aubourg_points`).

**S-m8: 7 issues versus 9 fix items.** FIXED in Sec. 3.6 (issue 7 was split into 7a/7b/7c).

**S-m9: eBOSS rc 0 over the referee's preference.** FIXED. Sec. 3.6 quotes both sides: fix item r2_8b ("per the orchestrator's fix-round instruction") and the round-2 referee ("this is the honest outcome"). It states that rc 0 was reached over the referee's stated preference.

**S-m10: PR #61 unevidenced.** FIXED. `round1_response_checks.py` runs `gh pr view 61` and records state MERGED, mergedAt 2026-09-27T17:29:02Z and merge commit 7c9c3c3. These are macros in Sec. 3.7.

**S-m11: pulls are not independent significances.** FIXED.
- Sec. 4 now says pulls measure reproduction accuracy, not independent-sample significance. The DR2 MC error on the Om mean is 0.007 sigma (macro `dr2_mc_error`).
- The Fig. 1 caption says the grey bands are tolerances, not error bars.

## Referee 2: formal methods (recommendation: major)

**F-M1 (major): hand-edited `lean_dual_check.json`.** FIXED.
- `run_lean_dual_check.py` has been rewritten (revision 2). It:
  - counts `#print axioms` commands on comment-stripped source with an anchored regex
  - computes `accepted`, `accepted_count`, `pairs_total`, `status` (BLOCKED_ENV), `summary` and `caveat`
  - records the measured Lean version, the lean-toolchain file and the Mathlib inputRev/rev of each environment
  - adds an axiom-smuggling negative control
  - writes a `history` block that records the earlier hand correction and the sha256 of the preserved revision-1 file
- The script was re-run in both environments. `gen_numbers.py` checks that `accepted_count` equals the per-pair flags.
- Sec. 3.4 describes the correction, and the AI-use statement names the preserved v1 file.

**F-M2 (major): H0 theorems overstated.** FIXED.
- Sec. 3.4 now states the scope limits:
  - the degeneracy theorems cover D_H/r_d only, at fixed E
  - identifiability holds only for the secondary Aubourg r_d, on omega_nu <= (1-2a) Omega_m h^2, which excludes part of the sampled prior
  - nothing is proved about the CAMB r_d behind the headline PASS
- Also repeated in Limitations.

**F-M3 (major): H0 audits bound to a stale hash.** DISCLOSED; the ledger is NOT FIXED (outside write scope).
- `round1_response_checks.json` (key `h0_audit_binding`) records the following:
  - all 8 audits have `reviewed_source_sha256` c0663994, while the current file is 2b653083
  - the only commit of the file has hash 2b65, so the audited bytes were never committed
  - in the pre-fix sorry scratch copy (not hash-linked to c0663994), all 8 statements are textually identical to the current ones. The copy was taken from `/tmp/BAO_BBN_H0_negctrl.lean` and is now kept as `results/cosmo_synthesis/h0_prefix_scratch_copy.lean` (sha256 d0638cc2...), so the check can be reproduced
- Table 10 has a new column, "audit hash = current file". It reads DR2 6/6, H0 0/8 and eBOSS 0/9; the eBOSS change is disclosed in its ledger.
- Sec. 3.5 and Limitations describe the defect. Adding `current_source_sha256` and `change_since_audit` has to be done in `results/bao_bbn_h0/ledger/`, which is outside this paper's scope.

**F-M4 (major): gate passes swapped evidence.** FIXED (disclosure). Sec. 3.5 states that the referee's M2 mutation gives rc 0/0 (DR2/eBOSS) and that an empty audit `{}` gives rc 0/0, both read from the referee's mutation JSON. It says claim-to-blob correspondence is checked only by reading. Also in Limitations and in Sec. 5, item 3.

**F-m1: DR2 z-domain drift persists.** FIXED (disclosure). Sec. 3.4, the Sec. 3.6 bullet and Limitations now say the drift remains in the shipped file and why (the audit stays bound to the audited bytes). That z > -1 proves with the same tactics is attributed to the referee and marked untested.

**F-m2: "28 theorems" headline.** FIXED. The abstract and Sec. 3.4 name the 7 one-line identities or positivity statements. Their proofs were checked by reading: 1-3 tactic lines each.

**F-m3: audit schemas and the empty-audit count.** PARTLY FIXED.
- `gen_numbers.py` now counts an audit only if it is a non-empty object naming an auditor (`by`, `auditor` or `auditor_kind`), and the table caption says so.
- Standardising on one schema has to happen in the ledgers, outside write scope. This is in Limitations.

**F-m4: toolchain asserted rather than measured.** FIXED. The toolchain, Lean version and Mathlib inputRev/rev are measured per environment. Sec. 3.4 prints Lean 4.34.0-rc2 and Mathlib v4.34.0-rc2 at commit 85e3a25e006c.

**F-m5: no axiom-smuggling control.** FIXED. A new control declares `axiom smuggled_E_pos_fact : False` and proves `E_pos` from it. The results in both environments are in Sec. 3.4.

**F-m6: wall-time column.** FIXED. Times were re-measured by the revision-2 run. The caption and text say they are single measurements on a shared machine, and the load average is recorded.

**F-m7: `kind: citation` for computed rows.** DISCLOSED; NOT FIXED (outside write scope). Stated in Sec. 3.5 and Limitations.

**F-m8: eBOSS module rename missing from the deviations list.** FIXED in Sec. 5, item 3.

**F-m9: inert `z != -1` hypothesis.** DISCLOSED in Sec. 3.4 and Limitations. The Lean file is outside write scope.

**F-m10: overfull hboxes.** MOSTLY FIXED. `\emergencystretch` was added and one long path shortened. One cosmetic overfull box (46 pt) remains in the Reproducibility paragraph, caused by a long file-system path.

## Referee 3: novelty / positioning (recommendation: major)

**N-M1 (major): title overclaims "machine-checked".** FIXED. New title: "An agent-executed, preregistered reproduction pipeline for BAO cosmology with kernel-checked model identities". The abstract adds "(the fits and numerics are not machine-checked)".

**N-M2 (major): blinding absent.** FIXED. A new "Blind analysis" paragraph in Sec. 5 cites four fetched sources:
- arXiv:2404.03002 Sec. 2.3.1
- arXiv:2503.14738 Secs. II.A.1 and IX
- Andrade et al. arXiv:2404.07282
- Grosso, Mikuni & Heinrich arXiv:2607.10039, quoted verbatim: "No analogous verification infrastructure exists for physics analyses"

It states that our setup is weaker than a blind analysis, because the targets were visible and the preregistrations were committed after the fits. This is also in Limitations, and the novelty item 1 caveat is added.

**N-M3 (major): SDSS-DESI claim unpositioned.** FIXED.
- The claim is narrowed to BAO-only (Om, hr_d) with eq. (18).
- Ghosh & Bengaly arXiv:2408.04432 is reconciled: DR1, D_H/r_d only, GP reconstruction with a Planck r_d, no parameter-level test.
- Ferri, Ruchika & Melchiorri arXiv:2607.07348: CPL + Planck, w0/q0 offsets of about 1.1 sigma.
- DR1 Sec. 3.3 is quoted ("no significant difference in Omega_m and a shift of just ~1 sigma in r_d h").

**N-m1: derived quantity (c) is not new.** FIXED. Sec. 4.5(c) and Table 7 call it a confirmation of Aubourg's stated accuracy. It is removed from the "new" list, which now has two items.

**N-m2: cmbagent successors.** FIXED. arXiv:2507.07257 (Planning & Control, "no human-in-the-loop at any point") and Denario arXiv:2510.26887 are cited.

**N-m3: missing precedents.** FIXED. FormalScience arXiv:2604.23002 (semantic-drift taxonomy), Collider-Bench arXiv:2605.13950 (LLM provenance judge, FABRICATED flag) and The AI Scientist arXiv:2408.06292 (automated reviewer) are cited, all read. arXiv:2603.20179 was not read and is not cited.

**N-m4: search undocumented.** PARTLY FIXED. The paper states that the original four query strings and dates were not recorded. Two new queries were run on 2026-09-27 and logged exactly in `literature_search_log_round1.json`. The original search cannot be reconstructed.

**N-m5: Rust wording in the abstract.** FIXED: "a Rust reimplementation of CVODE (rusty-SUNDIALS, not the LLNL library)". Sec. 3.7 was changed the same way.

**N-m6: Elenchus is unpublished.** FIXED in Sec. 2, item 4, and in the bibliography.

**N-m7: bibliography details.** FIXED, with one correction:
- ReplicationBench: 22% for Claude 4.5 Sonnet is in Sec. 5.1 and Table 2 of v2. The referee said Table 3, but Table 3 is task completion. The abstract's "under 20%" is also quoted.
- PRBench: best overall score 34% added.
- "HepLean (now Physlib)", per arXiv:2603.08139.
- Full eBOSS 2007.08991 title.
- Exact 2007.08995 title.
- Borrett et al. labelled a competition entry.

---

## Re-run results (revision-2 dual check, 2026-09-27)
- Environment 1: 4/4 files accepted; all 28 `#print axioms` outputs are whitelist-only. Wall times: 16.0 / 108.2 / 23.2 / 10.6 s.
- Environment 2: 3/4 files accepted; 22 outputs are whitelist-only. `DESI_DR2_wCDM.lean` is BLOCKED_ENV (rc 1, unknown module prefix 'ANSE'). Wall times: 645.0 / 138.0 / 367.6 / 313.1 s.
- Accepted pairs: 7 of 8. Load average at the end of the run: 4.34 / 4.42 / 4.84.
- sorry control: rc 0 in both environments, and `sorryAx` appears.
- Axiom-smuggling control: rc 0 in both environments; `smuggled_E_pos_fact` appears in the axiom output and the whitelist rejects it.
- Build: `pdflatex` run twice, rc 0, no errors, no undefined references, 21 pages. The page count went up from 17 because of the added material.

## Remaining open issues
1. The DR1 chi2 offset (+0.08) is unexplained after excluding radiation and neutrino background choices.
2. The H0 ledger audit binding (stale hash, no change record) needs an edit in `results/bao_bbn_h0/ledger/` (outside scope).
3. The three ledgers need one audit schema, correct `kind` labels, and a gate that checks claim-to-evidence correspondence (ledgers and Elenchus are outside scope).
4. The `fit_real.py` `verdict_T2` gate G1 versus G2 deviation (frozen script; verdict unaffected).
5. The DR2 z >= 0 drift and the inert z != -1 hypothesis in the committed Lean files.
6. The incoherent H0 tolerance design is disclosed, not re-designed. The preregistered verdicts stand.
7. No person has reviewed any component. Every audit is a model's.
