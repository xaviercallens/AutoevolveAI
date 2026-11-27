# K1 (Proposal 4, 2026-10-27): does NIST's "start cold" survive exergy accounting?

**Status (v2, 2026-10-27, revised after the independent AI audit `papers/p4_dac_exergy/AUDIT.md`, verdict
ACCEPT_WITH_CORRECTIONS; item-by-item response in `papers/p4_dac_exergy/REVISION.md`): KEEP, narrowed.**

- "Start cold" survives exergy accounting **of the model's own heats and works** (ideal machines, feed air not
  priced): 14/14 rows in all 9 informative variants. The 9 purity-constrained variants are vacuous for every row.
- **With the chilling of the feed air priced** (2,500 mol air per mol CO2, ε = 0, T0 = 298.15 K):
  - at r = 0, a cold start still wins in 14/14 rows, but at 254–288 K instead of 200–237 K;
  - at r = 1, the optimum moves to ambient (297.25–297.75 K, advantage 0.07–0.35 %) in 11/14 rows.
- H1 as preregistered (T0 = 298.15 K, r = 0) is refuted in both accountings (0/14).
- The size of the cold-start benefit, and at full recovery its existence, depend on the feed-air pricing.
- **Retracted:** the v1 claim that five dataset entries violate the second law. It was a quadrature artefact of our
  own Step 3; 0 violations remain over all 15,161 paths with the published rule.
- The feed-air family is producer-computed. An independent re-check is pending.

Gate (audit item):
- The positive control reproduces Table 2 to the printed digits: 14/14 rows.
- The negative controls are rejected by our own consistency gate: 4/4.
- An independent second implementation agrees.

Kill criteria: neither clause fired.
- The dataset does expose per-path, temperature-resolved energy terms.
- The supplement could not be obtained, so no evidence shows that sub-ambient cooling is already priced. The code
  shows it is not priced: `E3 = 0` in all four evaluators.

All statements are about a **published simplified model**: the McDannald et al. idealised piston, with Henry/IAST
loadings and its own heat and work terms. They are not about real plants, costs or any climate effect. Only
thermodynamic limits are discussed, and only public data are used.

## Source actually read

- McDannald, Siderius, DeCost, Choudhary, Ortiz-Montalvo, *Intrinsic Direct Air Capture*, arXiv 2501.04825v1
  (8 Jan 2025).
  - Read in full via alphaXiv, all 28 pp. A local text copy exists at `data/paper_2501.04825_fulltext.txt`. It is
    **untracked and is not redistributed** (arXiv non-exclusive distribution licence 1.0). It was in the public
    GitHub history (commit e29869853ec8056f6b8aaa1c32e09e018b80ae61) until it was removed from the tracked tree on
    2026-10-27 (b9a226cc1220be4e0006d0ae61ca5dd6b1a748a6).
  - This covers eqs. 1–10, Tables 1–2 and the conclusion.
- The arXiv record has only v1. **The supplement is not in the PDF and was not obtainable**:
  - not on arXiv;
  - not in the Zenodo record;
  - the GitHub repo holds code only.
  - It is therefore **not read**.
- Read as primary evidence of what the published numbers are:
  - **Zenodo 10.5281/zenodo.14452152** (CC-BY-4.0). `DAC_data.tar.gz` has md5 `a2520f52…966c`, which equals the
    Zenodo value; its sha256 is in result.json.
  - Its README.
  - The NIST Julia package **IntrinsicDACCycle v0.0.2** (NIST software licence). The relevant sources were read
    line by line: `Intrinsic_Refresh_Energy_Balance.jl`, `Analyze_GCMC_Results.jl`,
    `Generate_Equilibrium_Sorption.jl`, `MOF_Cv_Extrapolate.jl`, `Path_optimizer.jl`.

## Claims, with tier (A = Lean kernel, L = literature, C = interval/argument, X = floating point)

| # | Statement | Tier |
|---|---|---|
| 1 | Our Python re-implementation of the published energy balance reproduces every stored nominal term of the 14 Table 2 paths. Max normalised deviation is 3.8e-11 across loadings, q, every step-1/step-2 array, E1, E2 and E_total. The stored posterior mean/std of ξ, x_end, Δn_CO2, Δn_N2 and T1/T_end/P1/P_end round to the printed Table 2 strings in 14/14 rows × 8 fields. | X (reproduction) |
| 2 | Exergy re-accounting changes only the convention: each heat is weighted by its Carnot factor relative to an explicit T0; works stay as published; Step 3 is priced explicitly. On the 14 stored Table 2 paths at T0 = 298.15 K this gives:<br>• no-credit ξ_NC (r = 0) = **25.4–36.8 µmol/J**, against face-value ξ = 5.98–11.26 µmol/J (nominal);<br>• reversible floor B_rev = **25.0–27.0 kJ/mol**, against W_min(P0, y) = 18.8–19.4 kJ/mol, so ξ_rev = 37.0–40.0 µmol/J < 1/W_min;<br>• refrigeration (heat removed below T0) makes up **47–80 %** of the no-credit exergy cost. | X |
| 3 | **H1 refuted in the base accounting** (v2 rescan: T1 up to 400 K, 2 K steps over 270–298 K, T_end ≤ 400 K, P_end ∈ [100, P1], step-3 right-point rule):<br>• exergy-optimal T1 is **200–236.75 K in 14/14 rows**, for every T0 ∈ {273.15, 298.15, 313.15} K and r ∈ {0, 0.5, 1};<br>• **vacuity (B4):** for all 14 rows and every T0, no warm path on the grid reaches the stored purity. The 9 constrained variants therefore cannot fail, and **126 of 252 row-variants are informative**, not "18 variants";<br>• face-value control: 14/14 optima have T1 < 273 K. | X |
| 4 | The "start cold" benefit shrinks in the base accounting but remains. The ratio is best ξ with T1 < 298.15 K / best ξ with T1 ≥ 298.15 K, T0 = 298.15 K (v2 grid):<br>• face value: 10–818;<br>• exergy r = 0: **3.5–129**;<br>• r = 0.5: 2.6–79;<br>• r = 1: **1.29–6.6**. | X |
| 4b | **Feed air priced (new in v2).** n_air = Δn_CO2/x, x = 400e-6 (2,500 mol/mol at capture fraction 1, the case most favourable to a cold start); ideal chilling exergy; unrecovered share 1 − ε. At T0 = 298.15 K, ε = 0:<br>• **r = 0:** cold wins in 14/14 rows, at **T1\* = 254–288 K** (ratio 1.46–8.0). 0/14 rows have T1\* ≥ T0, so H1 as preregistered is still refuted;<br>• **r = 0.5:** T1\* = 268–290 K;<br>• **r = 1:** in **11/14 rows the optimum moves to ambient**, at 297.25–297.75 K on a 0.25 K grid. The advantage of the best start below ambient is 0.07–0.35 %, less than each row's printed ξ uncertainty. A start ≥ 10 K below ambient then loses unless **ε > 0.91–0.96** (0.77–0.90 on the auditor's split);<br>• VANNIK ×2 and LETQAE01 stay cold for every ε.<br>Machine sensitivity:<br>• refrigerator-only degradation, no air: r = 1 flips below η_R = 0.10–0.75;<br>• symmetric degradation, no air: the cold start is strengthened in 14/14 rows.<br>Agreement with the auditor on 3 rows: T1\* within one grid cell; η_R\* within 0.015; ε\* higher by 0.04 and 0.09. | X (producer only; independent re-check pending) |
| 4c | **H1 negative control (new in v2).** Refrigeration (sorbent + air) ×M:<br>• M = 1e4: detected (warm optimum) in 14/14 rows at every r;<br>• M = 100: 7/14, 8/14 and 14/14 rows at r = 0, 0.5 and 1. The misses are the 298.0 K cell. | X |
| 5 | Under exergy the optimum moves the **hot end** toward ambient. Unconstrained optimal T_end:<br>• face value: 227–400 K;<br>• exergy r = 0: 301–340 K.<br>T1 stays cold. | X |
| 6 | Slice scan on a seeded random sample of 150 materials (seed 20261027; each represented by its best stored Pareto path; T_end, P1, P_end held): exergy r = 0 at T0 = 298.15 K moves T1* ≥ T0 in **3/150** (unconstrained). Re-selecting among all 15,161 stored Pareto paths of 8,765 materials, the no-credit-exergy-best path starts below 298.15 K for 8,420/8,765 materials (face value: 8,416). | X (conditional, not a re-optimisation) |
| 7 | **H2 answered; v1 violation claim RETRACTED.**<br>• The published face-value ξ never exceeds 1/W_min: dataset max **11.259 µmol/J** (VANNIK), against 1/W_min(P0) ≈ 51.6 µmol/J.<br>• v1 claimed that five entries (CSMNOX, GUSNEN, PACYIE, SABWAU01, UJOKIP05) violate the second law. **That claim is withdrawn.**<br>• `code/rev_h2_rules.py` reruns all 15,161 paths, all three T0 and both floors:<br>&nbsp;&nbsp;– with the v1 step-3 trapezoid: 14/18/21 low-P and 16/22/25 P0 flags, reproducing v1 exactly;<br>&nbsp;&nbsp;– with the right-point rule of the published Step 2: **0 at every T0, against both floors**, and G2 closes to 4.4e-16.<br>• Every flagged path had Δn_CO2 ≤ 3.4e-4 mol/kg. The flags were our quadrature mismatch, amplified by tiny working capacities.<br>• Further v1 errors: SABWAU01's B_rev was −41.9 **kJ**/mol, and SABWAU01 and UJOKIP05 are degenerate in working capacity. | X |
| 8 | Stylised two-component surrogate (van 't Hoff Henry CO₂ + N₂, sensible heat, recovery r; `code/cert_sign.py` docstring). Benefit β = C(T0) − C(Tc) = A + λB + (1−r)γ R D, with closed-form terms:<br>• A_ex = −(T0−Tc)(q_C/Tc − R) is certified < 0 over the whole box Tc ∈ [200, 272] K, T0 ∈ [273, 313] K, T_h ∈ [315, 400] K, q_C ∈ [12, 67] kJ/mol;<br>• the full-recovery N₂ threshold is λ* = (T0−Tc)(q_C/Tc − R)/B when B > 0;<br>• certified signs of β (outward-rounded mpmath intervals, 80-bit) at the surrogate parameters of 164 rows × 3 T0 × 3 r. At T0 = 298.15, r = 0: 151 positive (cold wins), 8 negative, 0 undecided.<br>• An independent plain-float implementation lies inside the enclosures for 2854/2856 points; the other 2 are off by 3e-8 relative from float cancellation, with the same sign.<br>Agreement of the surrogate sign with the full-model scan: **149/150 (r = 0), 146/150 (r = 0.5), 128/150 (r = 1)**. At r = 1 the surrogate disagrees on 11/14 Table 2 rows (it predicts cold loses; the full model says cold wins). **The interval statements are therefore about the surrogate only**, and only r ≤ 0.5 is a fair proxy of the published model. | C (surrogate) |
| 9 | Lean (`formal_cert/Programmes/DacExergy/Core.lean`, pinned Lean 4.34.1 via `scripts/certified_numerics/lean_pinned.py`, rc = 0). 12 theorems, each `#print axioms` = {propext, Classical.choice, Quot.sound}, no `sorry`/`native_decide`:<br>• Carnot weights of heat above ambient lie in (0, 1) (the preregistered all-T ≥ T0 control);<br>• refrigeration weight in (0, 1) for T0/2 < T < T0;<br>• the factorisation of A;<br>• A_ex < 0 for q > R Tc;<br>• β affine in r, so r = 1 is the worst case for cold when γD ≥ 0;<br>• the λ and γ threshold equivalences;<br>• W_min(pure) = R T0 log(1/x) is positive and strictly decreasing in x;<br>• a rational instance.<br>Planted controls in `Controls.lean` compile with rc = 0 and are caught (`sorryAx`, `DacExergy.ctl_cheat`).<br>The independent AI auditor recompiled with rc 0 and replayed `Programmes.DacExergy.Core` with leanchecker: rc 0, 118 s (`papers/p4_dac_exergy/data/leanchecker_replay_audit.json`).<br>Three of the twelve theorems are bare identities (ring, ring, norm_num), and none certifies a number of the paper.<br>**LEDGER_UNAUDITED_TIER_A** stays open: no human has audited the statements. | A (algebra only) |
| 10 | Unit statement in the text (p. 20): "a few sorbents with intrinsic capture efficiencies above 1.0 × 10⁵ mol/J".<br>• Table 2 gives ξ in µmol/J (max 11.259).<br>• The dataset stores `Intrinsic_capture_efficiency` with units string `"mol/J"`; its max posterior value is 1.1259e-5 mol/J.<br>• 60 of the 8,765 materials have at least one path above 1.0e-5 mol/J.<br>• The next sentence compares with 2.46 × 10⁻⁶ mol/J (US grid), which only makes sense at the 10⁻⁵ scale.<br>The printed value is therefore **consistent with 1.0 × 10⁻⁵ mol/J (a dropped minus sign in the exponent)**. This is a typesetting matter in the text; the table and data are self-consistent. (Supplement not read.) | L + X |

## Method (short)

1. **Re-implementation.** `code/dac_model.py` re-implements the Julia functions line by line:
   - T↔β conversion, Kh polynomial extrapolation and q_ads^∞;
   - the monotone truncation (keeps the first k points, as the Julia `cumsum` does);
   - saturation truncation;
   - the analytic-IAST recursion;
   - the step-1 and step-2 terms, including the leading NaN and `nansum`;
   - E3 = 0.
2. **Cv.** `code/cv_gp.py` re-fits the SE + Const GP (fixed heteroscedastic noise, conjugate gradient from the Julia
   initial point). It agrees with the stored Cv to ≤ 4.0e-6 relative on all Table 2 paths.
3. **Exergy ledger.** `code/exergy.py` records each heat once, with its direction and temperature:
   - Step 1: Q_ads removed at T1;
   - Step 2: per-step heat at the mid temperature;
   - Step 3: sensible cooling of the sorbent plus the remaining adsorbed gas from T_end to T1. In v2 this uses the
     same right-point rule as the published Step 2, so the loop closes exactly. v1 used a trapezoid, which caused the
     retracted H2 flags.
   - Not in the base ledger: the contacted feed air. It is priced in the v2 scenario family (`code/rev_scan.py`,
     `code/rev_analyse.py`).

   Costs:
   - no-credit (r = 0): heat supplied below T0 and heat rejected above T0 are free; nothing is recovered;
   - reversible (r = 1): every negative Carnot contribution is credited;
   - B(r) = B_NC − r·credits.

   Works W_ads, W_des and E_P (with its `abs`) are kept at face value.
4. **Second implementation.** `code/fast_costs.py` is vectorised. It agrees with the ledger to 2.3e-15.
5. **Interval certification.** `code/cert_sign.py` uses mpmath `iv` (python-flint is not installed; see Deviations).
6. **Protocols.** H1 protocols were written before the runs: `logs/h1_operational_test_written_before_run.md`
   (slice) and `logs/h1_protocol_amendment_2026-10-27T1300Z.md` (joint; amended after the slice scan, before the
   joint scan).

## Controls and outcomes

| Control | Outcome |
|---|---|
| PC-a: dataset to paper, Table 2 printed digits | 14/14 rows, 8/8 fields each |
| PC-b: raw inputs to stored nominal arrays/E_total | max 3.8e-11 (normalised) |
| PC-c: nominal vs posterior-mean ξ | −2.3 % … +1.3 % (the printed value is the unseeded 100-draw posterior mean) |
| PC-d: GP Cv re-fit vs stored | ≤ 4.0e-6 |
| Positive: real BEVQID ledger passes the gate | pass |
| Positive (preregistered): path entirely at T ≥ T0 (300 K start) | heat-in weights all in (0,1); refrigeration term 0; heat-out free |
| Positive: joint-scan face-value optimum reproduces "start cold" | 14/14 rows have T1 < 273 K |
| Positive: scan self-check (stored path re-evaluated from raw inputs + GP Cv) | ≤ 4.2e-7 relative ξ |
| Negative: double-counted sorbent heating | rejected (G2 sensible closure off by 100 %) |
| Negative: planted ×10⁶ unit error | rejected (G4 value mismatch and above 1/W_min) |
| Negative: the text's 1.0 × 10⁵ mol/J taken literally | rejected (G4) |
| Negative: heats of adsorption removed (W_min violation) | rejected (G3: B_rev 8.7 kJ/mol < W_min 13.5 kJ/mol) |
| Lean planted controls (`sorry`, smuggled axiom) | caught by `#print axioms` |

## Neutral observations on the published code and data (not errors of the method)

- The paper's own scope statement covers our ξ_NC > ξ_fv. The face-value ξ is an accounting-convention quantity,
  not a bound on CO₂ per unit of *work*, and the paper itself says systems with heat recovery "could therefore
  exceed our stated upper limit of capture efficiency" (pp. 14–15). Exergy weighting makes the same point
  quantitatively; it is not a contradiction.
- The paper's mechanism (CO₂ uptake diverges from N₂ at low T, and purity collapses at warm starts: purity 0.98 at
  200 K vs 0.20 at 240 K for LETQAE01 on its slice) is what keeps "start cold" alive. It outweighs the
  refrigeration cost that exergy accounting adds.
- `Intrinisic_refresh_objectives_posterior_dist` draws 100 samples without a seed.
  - Inside the sample loop it uses `cv_s = cv_s_dist[:,1]`, so every sample reuses one Cv draw.
  - The printed ξ uncertainties therefore do not include Cv variability, and the posterior means cannot be
    regenerated bit-for-bit. They are reproduced here from the stored values.
- In the optimized JSONs, `Captured_CO2` is the posterior mean while `E_Balance` is nominal. They should not be
  divided by each other.
- The single path in Fig. 4/Table 1:
  - the text says 250→350 K, then vacuum to 40,530 Pa;
  - the stored SinglePath files and the README use 250→375 K and 42,844.84 Pa (checked on BEVQID, LETQAE01 and
    VANNIK);
  - the code default `Intrinisic_refresh` uses 300→350 K.
- Eight Table 2 rows have P1 < 101,325 Pa (82,466–101,126 Pa). Both the v0.0.2 optimizer bounds and the eq. 10 prior
  bound P1 to between 101,325 and 111,457.5 Pa. The stored results were therefore probably produced with other
  bounds or another code version.
- With the published evaluator, our joint grid (P_end ≥ 100 Pa, T ≤ 400 K) finds nominal paths that dominate several
  Table 2 rows in both ξ and purity (Tier X, nominal vs nominal):
  - PARFOF: 8.42 µmol/J at purity 0.99999, vs 5.98;
  - MAXHEA: 8.62 vs 6.77;
  - IFUDAO: 8.60 vs 7.27.

  The NSGA-III front in Table 2 may therefore not be fully converged. These face-value optima end below ambient
  (T_end 235–285 K), and their heating would be nearly free under exergy accounting.

## Deviations (preregistration item K1 is unedited)

1. **Material files missing from the public record.** The CSD material files (`cell_density`, `cell_mass`) are not
   in Zenodo 14452152.
   - PC-b back-solves the density from one stored number (the CO₂ Henry constant at the first path point). Every
     other array is an independent check.
   - Scans use the cell mass for the saturation truncation as ρ·V_box, from the saturation-GCMC box (tilts ≈ 0).
   - The location of the saturation edge, e.g. BEVQID's effective T1 ≈ 209–210 K, depends on this substitute. The
     direction of the H1 result does not.
2. **Table 2 reproduced from stored values.** "Reproduce Table 2 to the printed digits" was met from the stored
   posterior statistics, plus an independent nominal recompute. Regenerating the posterior is impossible because
   the sampling is unseeded.
3. **Search space.** H1 used a 1-D slice scan (per the original protocol), then a joint grid + refinement (dated
   amendment) instead of NSGA-III over 8,759 materials, which was out of budget on 2 cores.
   - The 150-material sample and the stored-Pareto re-selection are Tier X and conditional.
   - The first joint run let the refinement go to P_end = 50 Pa, below the optimizer's 100 Pa bound. It was rerun
     with the bound enforced; the conclusions were identical. v1 is kept as `logs/scan_joint_v1_Pend_unbounded.*`.
4. **No python-flint.** It is not installed in either venv; mpmath `iv` (outward rounding, 80-bit) was used instead.
5. **Lean runner.** Lean was compiled with `scripts/certified_numerics/lean_pinned.py` (pinned Lean 4.34.1), not
   with `anse/formal/lean_runner.py`. The rc and the `#print axioms` output were both checked. No statement lock or
   independent replay yet.
6. **Surrogate scope.** The certified interval part is about a stated two-component surrogate, not about the
   published model; its fidelity is measured in claim 8. The first surrogate run had a bug: the R factor was
   missing on the sensible term. The independent float check caught it (1,904/2,856 mismatches), and the run was
   fixed and repeated.
7. **H2 run.** `h2_all.py` skipped W_min(low P) < 0 cases in its own counter. This is superseded by
   `code/rev_h2_rules.py` (v2), which counts every case under both rules.
9. **v2 revision.**
   - Wider, finer rescan of the 14 rows (`logs/rev/`).
   - Step-3 rule changed to right-point.
   - Feed-air scenario family and H1 negative control added.
   - Shell-discipline lapses during the revision are listed in the paper's Deviations.
8. The preregistration assumed one 11,660-material set. The public record holds 11,656 optimized files, of which
   8,765 have valid paths.

## Limits

- Everything sits inside the published idealised model: Henry/IAST, absolute adsorption, adsorbed-gas heat
  capacities 9/2 R and 7/2 R, GP-extrapolated Cv, a binary CO₂/N₂ "air", no H₂O.
- Exergy weighting uses ideal reversible machines against a single ambient T0; works are kept at face value.
- The base accounting omits the feed air. With the feed air priced, the result depends on ε, r and how "cold" is
  defined; see claim 4b.
- The grid caps T_end at 400 K, a restriction of the published 600 K domain.
- The joint search is a grid with refinement, not a proof of global optimality.
- Saturation edges use the box-mass substitute.
- The interval results are about the surrogate (Tier C); the Lean results certify algebra only.

## What is NOT claimed

- Nothing about real DAC plants, costs, deployment, or tonnes of CO₂ removed or climate effect.
- No claim that the NIST metric or its authors are wrong. Face value and exergy are two accounting conventions, and
  the paper states its own scope (no heat recovery, intrinsic comparison).
- No claim about the unread supplement.
- No claim that the Table 2 front is non-optimal beyond the stated Tier X grid observation.
- No claim that any dataset entry violates the second law. The v1 claim to that effect is retracted.
- No unconditional "cold start survives": the result depends on the feed-air pricing, ε, r and the machine
  efficiencies.

## Files

- **code/**
  - `dac_model.py`, `cv_gp.py`, `exergy.py`, `fast_costs.py`, `stored.py`, `load_data.py`, `table2.py`
  - `run_pc.py`, `run_exergy_table2.py`, `run_scan.py`, `run_joint.py`, `run_warm_best.py`
  - `h2_all.py`, `h2_violators.py`
  - `surrogate_params.py`, `cert_sign.py`, `surrogate_agreement.py`
  - `extract_dataset.py`, `copy_members.py`, `singlepath_check.py`, `summarize_scan.py`
  - `inspect_opt.py`, `debug_float.py` (diagnostics)
- **data/**: local copies, not in the paper's Zenodo bundle.
  - The paper text and the NIST tarball and tree were removed from the tracked tree of the public repository on
    2026-10-27 (b9a226cc1220be4e0006d0ae61ca5dd6b1a748a6).
  - **The 51 dataset files in `zenodo_members/` (CC-BY-4.0) are still tracked at HEAD.** Untracking them is the
    owner's decision.

  It holds:
  - the paper text;
  - the Zenodo README;
  - the IntrinsicDACCycle-0.0.2 tarball and its extracted source (`zenodo/code_untrusted/`);
  - `zenodo_members/`: the 51 members used for the Table 2 materials.

  The names and sha256 of the members are in `papers/p4_dac_exergy/data/zenodo_members_SHA256SUMS.json`. The full
  3.4 GB tarball stays on disk 2 at `/mnt/disks/disk-socrateai-local-1/k1_dac_zenodo/`.
- **logs/rev/** (v2):
  - `h2_rules.json`, `exergy_table2_right.json`, `table1_compare.json`;
  - `scan_raw.json` (49 MB), `analysis.json`;
  - copies and summaries in `papers/p4_dac_exergy/data/logs/rev/`.
- **code/** (v2 additions):
  - `rev_h2_rules.py`, `rev_table1_compare.py`;
  - `rev_scan.py`, `rev_analyse.py`, `rev_refine_ambient.py`;
  - `rev_summary.py`, `rev_tables.py`, `inline_tables.py`;
  - `sha_files.py`, `wait_for_text.py`.
- **logs/**
  - `positive_control.json`, `exergy_table2.json`
  - `scan_T1.json`/`.log`, `scan_T1_summary.txt`
  - `scan_joint.json`/`.log`, `warm_best.json`
  - `h2_all.json`, `h2_violators.json`
  - `surrogate_params.json`, `cert_sign.json`/`.log`, `surrogate_agreement.json`
  - `lean_core.json`/`.log`, `lean_controls.json`/`.log`
  - the two H1 protocol files
- **Lean:** `formal_cert/Programmes/DacExergy/Core.lean`, `formal_cert/Programmes/DacExergy/Controls.lean`
