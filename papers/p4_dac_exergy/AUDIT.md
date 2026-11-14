# Independent adversarial audit of K1 (papers/p4_dac_exergy)

Auditor: an independent AI audit agent (producer != verifier), 2026-10-27. No human has audited this paper.

**Scope.** I read:
- main.tex and main.pdf;
- ledger/ (ledger.json, evidence/, gate_output.txt, run_gate.py);
- data/ (code/k1, logs, RESULT.md, the recount scripts);
- results/proposal4/2026-10-27/K1/code;
- formal_cert/Programmes/DacExergy/.

**Source paper.** I read arXiv:2501.04825v1 myself. I downloaded the PDF to /tmp/k1audit/pdf and extracted the text with pdftotext. I rendered pp. 13 and 20 as images at 150 dpi and looked at them.

**Dataset.** I used the producer's extracted copy of Zenodo 10.5281/zenodo.14452152, read-only. I fetched the Zenodo API record: licence cc-by-4.0, DAC_data.tar.gz md5 a2520f520140c60f8a4663d5b403966c, which matches main.tex:285.

**Independent code.** All of it is in /tmp/k1audit/scripts/ and was written from the NIST Julia sources and the paper text, not from the producer's Python:
- aud_model.py: the model and the exergy ledger;
- pc_audit.py: the positive control;
- h1_scan.py, h1_analyse.py, h1_compress.py: the H1 scan and analysis;
- h2_audit.py, h2_audit_all.py: H2;
- h1_sym.py: the symmetric-degradation variants for H1;
- surr_audit.py, slice_check.py: the surrogate checks;
- replay.py: the leanchecker replay;
- count_xi.py, shares.py: counts and energy-term shares.

The outputs are the *.json files in /tmp/k1audit/.

**Cores.** Only cores 6 and 7 (taskset), with at most 2 processes.

**Files written in the repository.** Two: this file and `data/leanchecker_replay_audit.json`. I made no git writes.

## VERDICT: ACCEPT_WITH_CORRECTIONS

The four BLOCKING items must be fixed before any release.
- The headline (H1 refuted) survives **within the producer's stated accounting**. The scope of the title and abstract must narrow (B3, B4).
- The H2 "five inconsistent entries" finding does not survive and must be withdrawn (B1).
- The repository redistributes the arXiv full text, contrary to the paper's own statement (B2).

**Item (7), tiering.** The headline is filed at Tier X (DAC-X-0011). That is the correct tier: it rests on grid optimisation of the real model, and on no Tier C or Tier A claim. The gate re-run confirms no tier inversion.

**Independently reproduced:**
- **Positive control.** My own energy balance, run on the stored arrays, reproduces the stored E_total to ≤ 1.6e-16 relative on 4 Table 2 rows (BEVQID 9.186, FASJAL 8.186, LETQAE01, PARFOF).
  - The stored posterior means round to the printed Table 2 strings in 8/8 fields on all 4 rows.
  - The nominal ξ differs from the printed posterior mean by −0.39 %, −0.008 %, −0.08 % and −2.2 %.
  - Regenerating the paths from the raw Kcoeff inputs (with the back-solved density) reproduces the stored loadings to ≤ 4.7e-13 and ξ to ≤ 3e-14.
  - That regeneration took C_V from the stored GP values, so it is not an independent test of the producer's GP re-fit.
- **Exergy numbers on the stored paths.** My own ledger gives ξ_NC, ξ_{r=1} and the refrigeration share for the same 4 rows. All match Table 1 of main.tex to the printed digits: 34.3/39.1/0.67, 35.0/37.0/0.47, 36.8/38.5/0.76, 25.4/40.0/0.80.
- **H1 (the headline).** My own joint grid covers 3 rows (FASJAL 8.186, BEVQID 9.186, VANNIK 11.259) over the *published* optimiser domain: T1 up to 400 K, ΔT ≤ 200 K, so T_end up to 600 K, which is wider than the producer's grid. It finds T1* in [200.0, 236.8] K in all 18 producer variants: VANNIK at 200.0 K, BEVQID at 208.7–210.5 K, FASJAL at 231.7–236.8 K. The producer's range is 200.0–236.5 K.
  - The cold/warm ratios are face value 11.6 / 87.4 / 33.8, r=0 4.09 / 20.7 / 13.8, and r=1 1.30 / 1.54 / 5.48. The producer's are 10.2 / 78.2 / 30.6, 3.5 / 16.8 / 11.9 and 1.2 / 1.5 / 5.3.
  - Within the producer's accounting, **H1 is refuted**, as claimed.
- **Lean.**
  - Core.lean recompiles: rc 0, all 12 theorems on exactly [propext, Classical.choice, Quot.sound].
  - Controls.lean: compiled (rc 0) and, by design, not replayed. Both plants are exposed (sorryAx; DacExergy.ctl_cheat).
  - Non-vacuity: every hypothesis set in Core.lean is satisfiable, for example T0 = 1, T = 2; T0 = 2, T = 1.5; R = 1, q = 2, Tc = 1, T0 = 2; B = 1; R·D = 1; x = 1/2; γD = 0, r = 0. instance_r1 has no hypotheses.
  - **The leanchecker replay of Programmes.DacExergy.Core passes: rc 0** (118 s).
  - The sha256 of both sources match main.tex:257 and the data/lean copies.
- **Surrogate.**
  - 20 of 20 interval signs (both "ex" and "fv") reproduce with my own mpmath code. I evaluated C(T0) − C(Tc) directly, not through the producer's A + λB + (1−r)γRD split, and the midpoints match the producer's to 1e-6.
  - The aggregates reproduce: 151/8 (298.15 K, r=0) and 131/28 (r=1).
  - The derivation of λ* and of the γ threshold is correct (see N7).
- **Unit sentence.** The typeset page image (p. 20) prints "1.0 × 10⁵ mol/J" with a **positive** superscript 5. On the next line, "2.46 × 10⁻⁶" shows its minus. So the positive exponent is in the typeset source, not an extraction artefact. That it should have been 10⁻⁵ remains an inference from Table 2, the dataset and the next sentence (N1).
- **Ledger gate (re-run read-only).** exit 1, 0 blocking, 5 flags (LEDGER_UNAUDITED_TIER_A × 5), identical to gate_output.txt.

## BLOCKING

### B1. H2's "five inconsistent dataset entries" are an artefact of the producer's own step-3 quadrature, not of the dataset

**Where:**
- main.tex:55-57 (abstract)
- main.tex:180-181 (§3.5)
- main.tex:225 (G3)
- ledger DAC-X-0005
- data/RESULT.md

**What I did.** I recomputed B_rev (r = 1, T0 = 273.15 / 298.15 / 313.15 K) with my own code on every stored path of all **10 materials** listed in `h2_violators.json`, plus the 5 Table 2 materials (37 paths; /tmp/k1audit/h2_audit_all.json). The 10 materials are:
- CSMNOX_clean, GUSNEN_SL, PACYIE_clean, SABWAU01_clean;
- UJOJAG_clean, UJOJOU01_clean;
- UJOKIP02/03/04/05_clean.

**Reproduction.** With the producer's convention (trapezoid step 3), I reproduce the producer's counts **exactly**:
- against the low-P floor: 14 / 18 / 21 pairs at 273.15 / 298.15 / 313.15 K, in 3 / 5 / 7 materials;
- against the P0 floor: 16 + 22 + 25 = **63** pairs.

**The result.** Discretise the step-3 sensible return with **the same right-point rule the published step 2 uses** (cv[i]·ΔT_i, which makes the sorbent heating/cooling loop close exactly) instead of the producer-introduced trapezoid. Then the number of violations is **0 of 37 paths at every T0, against both the low-P and the P0 floor**.

This switch costs nothing elsewhere. On the 5 Table 2 materials (11 paths), ξ_rev changes by ≤ 1.8e-4 relative (PARFOF 39.963 → 39.955 µmol/J), so the Table 1 digits and the G3 pass are unchanged.

**Scope of this check.** It covers every material the producer flagged. I did not rerun the whole record (15,161 paths), so a statement for the full record needs the producer's rerun with the closure-consistent rule.

**Why.** The violators all have tiny working capacities:
- Δn_CO2 = 3e-9 to 1.4e-4 mol/kg;
- ξ_fv = 6e-8 to 9e-4 µmol/J.

The O(dCv/dT·ΔT_step) mismatch between the two quadratures, once divided by such a Δn_CO2, gives B_rev down to −1.2e9 J/mol.

**Two further errors in the text:**
- main.tex:180 says SABWAU01 has "B_rev = −42 J/mol". The value is **−41.9 kJ/mol**, so the unit is wrong.
- main.tex:180 says SABWAU01 and UJOKIP05 "are not" degenerate. They have purity 0.91 and 0.67, but Δn_CO2 is only 4.2e-5 and 1.4e-4 mol/kg, and ξ_fv is 2.4e-4 and 8.8e-4 µmol/J. They are degenerate in working capacity.

**Fix.**
- Keep the preregistered H2 answer: no published ξ exceeds 1/W_min. The dataset max is 11.259 µmol/J (checked, see N10).
- Withdraw "five dataset entries … inconsistent with the second law, which we read as inconsistent inputs" from the abstract, §3.5, the ledger and RESULT.md.
- Replace it with: "Our G3 floor check first flagged 18 path/T0 pairs at 298.15 K, in five materials, all with Δn_CO2 ≤ 1.4e-4 mol/kg. These flags, and all 63 P0-floor flags in ten materials, vanish when the step-3 return uses the same right-point quadrature as the published step 2. They are a discretisation artefact of our floor, amplified by tiny working capacities, and are not evidence about the dataset entries."
- Rerun h2_all.py with the closure-consistent rule before stating any full-record count.
- G3 (main.tex:225) and negative control 4 (main.tex:222) can stay as gate descriptions. Add that G3 must be run with closure-consistent quadrature, and with a Δn floor.

### B2. Third-party material is redistributed in a public, pushed repository, and the paper says the opposite

`git ls-files` shows the following tracked under results/proposal4/2026-10-27/K1/data/, committed in e298698:
- `paper_2501.04825_fulltext.txt`: the full text of the arXiv paper;
- the NIST tarball `zenodo/IntrinsicDACCycle-0.0.2.tar.gz` plus its extracted `code_untrusted/` tree;
- 51 dataset members (`zenodo_members/…`).

Commits e298698 and 92f8953 are on `origin/worktree-openai-math-discovery`. `gh repo view` reports xaviercallens/AutoevolveAI as **PUBLIC**.

The arXiv abs page gives the licence as `arxiv.org/licenses/nonexclusive-distrib/1.0/`, which does not grant third parties a right to redistribute the full text. The NIST code is redistributable with its notice (LICENSE.md is kept intact in the tarball, and NIST_NOTICE.txt is identical to it). The dataset is CC-BY-4.0, so redistribution with attribution is allowed.

**The statements are false at repository level:**
- main.tex:284 ("Not redistributed: … the NIST Julia code; the paper PDF or its text");
- main.tex:287 ("nothing was pushed or published"; HEAD e298698 is stale, since 92f8953 exists).

**Fix (owner's decision on the history):**
- Remove `paper_2501.04825_fulltext.txt` from the tracked tree. History rewriting is the owner's call; the hooks forbid force pushes, so ask the owner.
- Rewrite main.tex:284-287 to state accurately:
  - the repository contains the NIST code (with its licence) and 51 CC-BY-4.0 dataset files, with attribution;
  - the K1 commits are pushed to a public branch;
  - the arXiv text is not redistributed, once it has been removed.

### B3. "Survives exergy accounting" must name its load-bearing assumptions; with the feed air priced, the result changes

**Where:**
- title (main.tex:27)
- main.tex:49 ("sub-ambient cooling is priced")
- main.tex:51-52 ("in every one of 18 variants")
- main.tex:118 ("record every heat once")
- main.tex:176 ("it does not here")
- main.tex:203 (headline)
- the "What this is NOT" box (main.tex:69-73)
- DAC-X-0011

**The two unpriced assumptions.**
- **(a) Feed-air chilling is not priced at all.** Adsorbing at T1 < T0 means the contacted air must be at T1: at least (1−x)/x ≈ 2,500 mol N2 per mol CO2 at capture fraction 1. Only the sorbent and its adsorbate are cooled in the ledger.
- **(b) Refrigeration is at Carnot COP** (η_II = 1).

**My variants** (same grid, T0 = 298.15 K; /tmp/k1audit/h1_analysis.json, h1_sym.json, h1_compress.json).

Two parameters appear below:
- ε is the effectiveness of a recuperator on the feed-air chill: unrecovered share 1−ε, n_air = Δn_CO2/x at capture fraction 1 (the most favourable case for a cold start), c_p = 7/2 R.
- η is a second-law efficiency.

| row | (a) T1* at r=0, air priced, ε=0 | (a) ε* at r=1 (warm wins below) | (b) η* at r=1, refrigeration only degraded | (b) η* at r=0 | (b′) symmetric degradation, any η in [0.01, 1] |
|---|---|---|---|---|---|
| FASJAL 8.186 | 290 K (from 236.8) | **0.84** | 0.67 | 0.055 | cold wins; the ratio rises, e.g. 4.6 at η = 0.3, r = 1 |
| BEVQID 9.186 | 280 K (from 210) | **0.68** | 0.59 | 0.031 | cold wins (23 at η = 0.3) |
| VANNIK 11.259 | 280 K (from 200) | none (cold wins at ε = 0) | 0.13 | 0.037 | cold wins (11 at η = 0.3) |

In (b′), heat-pump costs above T0 are divided by η, refrigeration is divided by η, and credits are multiplied by η.

Restricting the warm side to T_end ≤ 400 K (the C_V training range) changes none of these thresholds by more than 0.005.

**Reading:**
- **Feed air (a).** This is the load-bearing omission.
  - At r = 0 the cold start still wins (ratios 1.7 / 3.9 / 2.4 at ε = 0). But T1* moves from 200–237 K up to 280–290 K, the grid cell just below ambient. So the quantitative "start at ~200 K" does not survive pricing the air, although the preregistered criterion T1* ≥ T0 is still not met.
  - At r = 1, warm wins for 2 of 3 audited rows when the air recuperator is below 68–84 %. Note that r = 1 with ε < 1 is a mixed bookend: reversible for the sorbent heats, irreversible for the air.
- **Refrigeration COP (b, b′).** Degrading only the refrigerator (b) flips r = 1 for FASJAL and BEVQID below η ≈ 0.6–0.67. This is again a mixed bookend: reversible heat pump, irreversible refrigerator. Degrading both machines symmetrically (b′) *strengthens* the cold start, because the warm alternatives depend on heat supplied above T0. So the COP question is not, by itself, a reason to doubt the result; the asymmetric case should be reported only as a sensitivity.
- **Other directions.** Dropping the PV work terms leaves the r = 1 ratios at 1.30 / 1.45 / 2.93. Charging the product's recompression from P_end to P0 raises them to 1.57 / 2.30 / 12.4. The conclusion is not fragile in those directions.

**Fix (text only):**
- Title / abstract / headline: "…survives exergy weighting of the model's own heat terms (ideal machines; chilling of the feed air not priced)".
- main.tex:49 and :118: say that the heats of the sorbent and adsorbate are recorded, and the contacted air is not.
- main.tex:176: rephrase "it does not here". Either report the feed-air sensitivity (T1* moves to just below ambient at r = 0; warm wins at r = 1 below ε ≈ 0.7–0.85 for two of three rows), or rerun it with the producer's code. The η sensitivity is optional, with the symmetric/asymmetric caveat.
- Add the feed-air omission and the ideal-machine assumption to the "What this is NOT" box and to §8.

### B4. The "18 variants" robustness count includes 9 variants that cannot fail

In my grid, **0 of about 1,380 warm cells** (T1 ≥ 298.15 K, or ≥ 313.15 K) meet the row's purity_min, for all 3 audited rows. The best-ξ warm paths have purities of 0.85, 0.67 and 0.08 for FASJAL, BEVQID and VANNIK (r = 1, 298.15 K), against a purity_min of 0.995, 0.993 and 0.939. The producer's warm_best.json records only unconstrained warm alternatives, with VANNIK's warm purity at 0.055.

With the purity constraint on, the warm side is empty, so "T1* < T0" holds by construction.

**Fix.**
- Run the per-row check over all 14 rows: does any warm cell reach purity_min? I showed vacuity for 3 of 3 audited rows only.
- main.tex:51-52, :172 and DAC-X-0003: count only the informative variants, and state for which rows the constrained variants are vacuous (no warm path reaches the stored purity).

This is blocking because it is the abstract's main robustness claim. It could also be folded into B3's rewording, which would not change the verdict.

## NONBLOCKING (with exact fixes)

**N1. Unit sentence (main.tex:227-228; DAC-L-0003).** Replace "not against the page image" with "the typeset PDF (p. 20, rendered at 150 dpi) prints 1.0 × 10⁵ mol/J with a positive exponent, while 2.46 × 10⁻⁶ on the next line shows its minus".
- Keep "consistent with 1.0 × 10⁻⁵ mol/J" as an inference.
- The present wording is neutral and non-accusatory, which is good. Keep it that way, and do not call it an error of the authors.
- The count "60 of 8,765 materials" with a path above 1e-5 mol/J: see N10.

**N2. Eq. 4 versus the code (main.tex:109-113).** The p. 13 image is legible. Eq. 4 prints "− RT(s)n_CO2(s) − RT(s)n_N2(s)", consistent with eq. 2's "− W2", and "(n_N2 + n_CO2) RT log(P(s))" with no absolute value and no d/ds. The Julia code instead *adds* W_desorb = +d·R·T_mid and takes |n R T ln(P_i/P_{i−1})|.
- Table 2 is reproduced only with the code's sign. With eq. 4's −W2, BEVQID's nominal ξ would be 9.59 instead of 9.15 µmol/J.
- Fix: replace "the argument of the logarithm … is not legible in our text extraction" with a neutral statement that the code differs from eq. 4 as typeset in the sign of the desorption work term and in the abs(). Add that the published numbers follow the code, and that our exergy ledger keeps the code's convention.

**N3. Eq. 10 (main.tex:112).** "T1 ≥ 200 K" should read "T1 ~ U(200, 400) K". The optimiser bound (Path_optimizer.jl) is also [200, 400].

**N4. Search domain (main.tex:171, :233).** The grid is T1 ≤ 320 K and T_end ≤ 400 K. The published domain is T1 ≤ 400 K and ΔT ≤ 200 K, so T_end ≤ 600 K. The code comment in run_joint.py, "T_end <= 400", misreads the bound.
- On 3 rows the wider domain does not change the result (B-section numbers above). State the restriction as a choice.
- "P_end ∈ [100, 60000] Pa" is also inaccurate: the refinement multiplies by up to 2, and the stored scan_joint.json reaches 84,000 Pa (VANNIK, fv). Write "P_end ∈ [100, P1]".

**N5. Reading (1) in §3.2 (main.tex:167) is wrong for these rows.** On the stored Table 2 paths, the sorbent heating is only 15 %, 11 %, 1 % and 45 % of the face-value E_total (BEVQID, FASJAL, LETQAE01, PARFOF). The heats of adsorption plus desorption are 49–88 %.
- The real driver: face value prices the step-1 heat removal at weight 1, against a Carnot refrigeration weight T0/T1 − 1 = 0.26–0.49 at T1 = 200–237 K. It prices the desorption heat at weight 1, against 1 − T0/T ≈ 0.05–0.25 at 315–390 K.
- Fix: replace the sentence accordingly. Add that, for T1 > T0/2, the published face-value E1 already *over*-prices sub-ambient heat removal relative to Carnot. This is what Lean `refrig_weight_lt_one` states. The only sub-ambient cost the face value omits is the step-3 return.

**N6. Surrogate wording (main.tex:137, Step 5).** The "why" reading is offered as an explanation. Yet the same surrogate gives the wrong sign on 10 of 13 scorable rows at r = 1 and 298.15 K.

What I checked:
- **Surrogate signs, all 14 rows** (from cert_sign.json, at r = 1 and 298.15 K):
  - minus for BEVQID ×2, FASJAL ×3, IFUDAO ×2, MAXHOK ×2, PARFOF, and MAXHEA (unscorable in the producer's coarse slice);
  - plus for VANNIK ×2 and LETQAE01.
- **Full-model slice signs, 3 rows** (FASJAL, BEVQID, VANNIK), with my own code: cold wins at r = 0, 0.5 and 1.
- The counts 11/14, 10/13 and 5/8 match table2_surrogate_check.json. The "scorable" counts rest on the producer's coarse slice grid (every 10th point), which I did not re-derive.
- Fix: add at main.tex:137: "At r = 1 this surrogate predicts the wrong sign for most Table 2 rows (§3.7), so the mechanism is illustrated, not established".
- At main.tex:191-192, note that the slice comparison is lopsided. With T_end held at 308–384 K, the best warm slice point has ξ = 0.01–0.4 µmol/J, against 35–39 µmol/J for cold, so the full-model "cold wins" there is near-trivial.

**N7. Surrogate algebra.** I re-derived it.
- Per mol CO2, the cost is C(T) = a_C + λ (f_N/f_C) a_N + (1−r) γ R s(T)/f_C. Then β = C(T0) − C(Tc) = A + λB + (1−r)γRD, with A_ex = R(T0−Tc) − q_C(T0/Tc − 1) = −(T0−Tc)(q_C/Tc − R), and A_fv = R(T0 − Tc).
- At r = 1, for B > 0: cold wins ⇔ λ > λ* = (T0−Tc)(q_C/Tc − R)/B.
- For (1−r)RD > 0: cold wins ⇔ γ > N/((1−r)RD), with N = −(A + λB).
- The Lean `threshold_iff` and `lambda_threshold_iff` are exactly these rearrangements.

One caveat is missing from main.tex:132. "r = 1 is the worst case" needs γD ≥ 0, and cert_sign.log certifies D_ex > 0 on only 2.9 % of the box (97.1 % undecided). State that D's sign is not certified over the box.

**N8. Lean content (main.tex:60-62, :199, §6).** Honest labelling is needed:
- `benefit_affine_in_r` is a `ring` tautology and has no content.
- `instance_r1` is a `norm_num` numeric check.
- `numerator_factor` is a `ring` identity.
- `lambda_threshold_iff` and `threshold_iff` are one-step linear rearrangements.
- `co2_term_facevalue_favours_cold` is the product of two positives.
- The others are elementary real-analysis facts:
  - Carnot weights in (0,1);
  - the refrigeration weight < 1 for T > T0/2 (hypothesis h0 is redundant, as the linter says);
  - sign of A_ex;
  - monotone in r;
  - log positivity and monotonicity.

All are faithful to their glosses. None touches the model or the data.

Suggested wording: "Tier A: twelve elementary real-algebra lemmas (three of them identities); they certify no number in §3". Also, `carnot_in_mem_unit` "matches" the all-T ≥ T0 positive control (main.tex:213) only as an identity; that control cannot fail.

**N9. Stale status lines.**
- main.tex:41 and :274: "No independent audit of any kind exists" and "producer ≠ verifier recompile is pending". Update both to: audited by an independent AI agent, 2026-10-27; recompile and leanchecker replay rc 0 (data/leanchecker_replay_audit.json).
- main.tex:239: "No leanchecker replay … was run". Same update.
- main.tex:287: HEAD e298698 is stale (see B2).

**N10. Counts (main.tex:179, :227).** My own count over all 11,656 OptIDC files gives:
- 8,769 materials with a stored path that is not null and has the flag "no flags";
- 15,165 such paths;
- **60 materials** with a posterior ξ > 1e-5 mol/J;
- maximum 1.12587e-5 mol/J (VANNIK).

The producer reports 8,765 and 15,161. The difference of 4 is consistent with its loader also dropping paths with fewer than 2 points (stored.py), which mine does not do. The 60 and the maximum agree.

**N11. Positive-control wording (main.tex:212).** Write "Table 2 reproduced to the printed digits *from the stored posterior means*; nominal recomputation within −2.3 % … +1.3 %". The §3.1 text already says this; the Controls list should match it.

**N12. Negative controls.** The four gate plants can fail: each one is a check of a planted ledger against the gate, and each would pass if the gate were broken. None of them is a negative control for the **H1 conclusion**, and the paper has none.

My η and ε variants show that the same scan does return warm optima, T1* = 300 K: FASJAL and BEVQID at η = 0.3 (refrigeration only), r = 1, and at feed-air ε = 0, r = 1. So the H1 machinery is able to fail. Add one such planted accounting as the H1 negative control.

**N13. Exergy legitimacy (summary for §2 Step 3).** The re-accounting is a legitimate second-law bookend, and I found no double counting:
- every step-1, step-2 and step-3 heat appears once;
- the works are kept exactly as published;
- step 3 is a new term, stated as such;
- the published model is not silently changed (my Table 1 numbers reproduce on the stored paths).

Two points worth stating:
- "works at face value" keeps P·ΔV terms (W1 = Δn R T1 and W_des = d R T), which an exergy balance would not count as costs. Dropping them does not change the direction (B3).
- r = 1 at η = 1 is the reversible floor, so internal heat-exchange recovery cannot do better than r = 1. That makes r a correct bookend.

**N14. Bibliography (main.tex:302-305).** I checked:
- `mcd`: authors, title, v1 date (8 Jan 2025) and NIST affiliation, against the PDF and the abs page.
- `zen`: title "Data for Intrinsic DAC calculations", creators McDannald and Siderius, cc-by-4.0, NIST DOI 10.18434/mds2-3687 and Version 1.0 per README.txt. The Zenodo API returns no version field.
- `nist`: v0.0.2 per the tarball name. I did not verify the GitHub URL.
- `mathlib`.

All are correct. Add the arXiv licence (nonexclusive-distrib 1.0) to `mcd`.

The "supplement not obtainable" claim stands. p. 25 announces Supporting Information (IAST derivation, finite-volume correction, H2O/O2); it is not in the Zenodo record files (DAC_data.tar.gz, the code tarball, README.txt). I did not search further.

**N15. Not verified by me.** These are left as the producer's Tier X:
- the 150-material sample (3/150);
- the 8,420/8,765 stored-Pareto re-selection;
- the rows other than the 4 rows (positive control) and 3 rows (scan) I recomputed;
- the 21 violators at 313.15 K outside the five materials.

## Auditor's own deviations

- **Shell discipline.** Early in the audit I used a few `cd X && …` compound commands (read-only listings), one `echo rc=$?` and one `echo exit=$?`. I also used `sed -i` twice on my own /tmp scripts. One compound git command was refused by the guard and re-issued plainly. None touched git state or the repository tree.
- **Shared olean dir.** The pinned wrapper's `--olean` writes into the shared olean dir (`formal_cert/.olean_out` → disk 2 `certified_numerics_olean`). My rebuild overwrote the producer's `Programmes/DacExergy/Core.olean` there, from the same source, so the producer's olean hash could not be compared. The replay is of my own build.
- **Scan grid.** The joint grid is coarse: 10 K in T1 (plus 205–245 K at 5 K), 10 K in ΔT, and 6 values of P_end. There was no refinement. I excluded no-swing paths (T_end = T1, P_end = P1, where Δn_CO2 ≈ 1e-13 is round-off) and paths with Δn_CO2 ≤ 1e-6 mol/kg.
- **Cv off the stored paths.** I interpolated NIST's own GP outputs along all stored paths of the material, with a linear fit to the 7 raw predictions outside that range. This is not a GP re-fit; the H1 direction agrees with the producer's anyway.
- **Density.** As in the producer's work, the density is back-solved from the stored Henry constants (relative spread across all stored points ≤ 2e-15). The saturation cell mass is ρ·V_box, as the producer uses.
