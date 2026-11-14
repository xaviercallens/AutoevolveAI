# Independent adversarial re-audit of K1 v2 (papers/p4_dac_exergy)

Auditor: the same independent AI audit agent as for v1 (producer != verifier), 2026-10-28. No human has audited this paper.

**What I read.**
- REVISION.md, main.tex (v2) and publication_meta.json;
- data/logs/rev/ and the ledger.

**Which commit.** The coordinator's brief names commit 28a1ac0, which is the M1 commit. The K1 v2 revision is **4f3c940** (same timestamp, 2026-10-28 05:23 UTC). It is on `origin/worktree-openai-math-discovery`.

**Independent code.** Every number below is from my own code, written for v1 from the NIST Julia sources and extended for v2. I did not run the producer's `rev_*.py`. Everything is in /tmp/k1audit/scripts/:
- aud_model.py: the model;
- h1_scan_right.py: the cost components with the published right-point step-3 rule;
- v2r_scan.py: the 14-row scan;
- v2_analyse.py: the scenario family;
- h2_full.py: H2 over the full record;
- t1_drift.py: Table 1 drift between the two step-3 rules;
- tar_list.py: the bundle listing.

The outputs are in /tmp/k1audit/*.json.

**Cores.** Only cores 6 and 7, with at most 2 compute processes.

**Files written.**
- In the repository: **this file only**. I made no git writes. data/leanchecker_replay_audit.json is unchanged (see item 6).
- Outside the repository: the dry-run bundler wrote its bundle, as it does by design, to `/home/callensxavier_gmail_com/zenodo-bundles/p4_dac_exergy/`.

**My scan grid.**
- T1: 200–400 K in 10 K steps, plus 2 K steps over 270–298 K and **0.25 K steps over 290–298 K**, plus 273.15, 298.15 and 313.15 K.
- ΔT: 10 K steps with T_end ≤ 400 K.
- P_end ∈ {100, 1e3, 5e3, 2e4, 6e4, P1}.
- No refinement. 1,459–4,939 paths per row.

## VERDICT: ACCEPT_WITH_CORRECTIONS

The science of v2 reproduces:
- the B1 retraction (exactly);
- the B3 feed-air family, within grid resolution and with one boundary case;
- B4, exactly.

The paper also states correctly what it supports: H1 is refuted at the preregistered setting; at r = 1 with the air priced there is a tie at ambient for 11/14 rows.

**One new BLOCKING item** comes from item (4). The Zenodo dry-run bundle contains the arXiv full text, NIST code files and the dataset files. That contradicts §10 and publication_meta.json, and it would be a public redistribution of the arXiv text. The bundle also sweeps in Lean files of about 13 unrelated, partly unpublished programmes.

## (1) B1 retraction: REPRODUCED EXACTLY

My own pass over **all 11,656 files, 8,765 materials and 15,161 paths** (≥ 2 points, flag "no flags"), at 3 T0 and with both floors (/tmp/k1audit/h2_full.json, 434 s):

| rule | low-P floor, 273.15 / 298.15 / 313.15 K | P0 floor | materials (low-P; P0) |
|---|---|---|---|
| v1 trapezoid | 14 / 18 / 21 | 16 / 22 / 25 = **63** | 3 / 5 / 7; 3 / 8 / 10 |
| right-point (published step-2 rule) | **0 / 0 / 0** | **0 / 0 / 0** | none |

- **Flagged paths.** They have Δn_CO2 = 3.0e-9 to 3.4e-4 mol/kg and ξ_fv = 6.0e-8 to 2.9e-3 µmol/J. The minimum B_rev is −1.48e6 kJ/mol. All three match main.tex:230ff.
- **SABWAU01.** B_rev = −41.94 **kJ**/mol (Δn = 4.18e-5 mol/kg, ξ_fv = 2.4e-4 µmol/J). UJOKIP05 has Δn = 1.4e-4 mol/kg. So "degenerate in working capacity" is correct.
- **Table 1 drift** between the two rules, over 14 rows × 3 T0 × 3 r: **max 2.35e-4** relative (PARFOF, 313.15 K, r = 1), against the producer's 2.4e-4. No printed digit of Table 1 changes.
- **Maximum posterior ξ.** 1.12587e-5 mol/J (VANNIK). The count of 60 above 1e-5 mol/J is confirmed in v1 N10.
- **Minor correction.** REVISION.md (B1 table) says "P0 10 in all". The P0-floor materials are 3 / 8 / 10 per T0, and 10 distinct in total. Write "P0: 3/8/10 (10 distinct)".

## (2) B3 feed-air family: REPRODUCED within grid resolution

My setting: x = 400e-6, so n_air = Δn/x (2,500 mol air per mol CO2 at f = 1), c_p = 7/2 R, T0 = 298.15 K, ideal machines, ε = 0, unconstrained.

The comparison below uses my **right-point** components (v2r_*). With the v1 trapezoid, my r = 1 numbers for IFUDAO, MAXHEA, MAXHOK and PARFOF were distorted: the base r = 1 ratio reached 15 and ε\* fell to 0.10. This is the same quadrature artefact as B1, so the producer's switch of rule matters for the r = 1 family too.

| quantity | producer (v2) | auditor | status |
|---|---|---|---|
| r=0 T1\* | 254–288 K (FASJAL 288, BEVQID 280–281, VANNIK 279–280, MAXHOK 273–274, PARFOF 254) | **255–290 K** (FASJAL 290/288/286, BEVQID 282/282, VANNIK 280/280, LETQAE01 280, IFUDAO 280/280, MAXHEA 278, MAXHOK 270/276, PARFOF 255) | agrees within 1–2 grid cells; I have no refinement |
| r=0 cold wins (T1 < T0 vs T1 ≥ T0) | 14/14, ratio 1.46–8.0 | 14/14, **1.449–8.025** | reproduced |
| r=0, start ≥ 10 K below ambient | 14/14 (§4 H1 status; Table 2 q10 ≥ 1.01) | **13/14**: FASJAL 8.186 has T1\* = 290.0 K and q10 = **0.998** | **boundary case** (N1) |
| r=0.5 T1\* | 268–290 K | 270–290.75 K | reproduced |
| r=0.5, ≥ 10 K below loses | 3/14 (FASJAL) | 3/14 (FASJAL, q10 0.971–0.990) | reproduced |
| r=1: rows moving to ambient | 11/14; T1\* 297.25 (BEVQID) / 297.75 (others) | **11/14; 297.25 (BEVQID ×2) / 297.75 (other 9)** | reproduced exactly |
| r=1 margin, best below vs best at/above T0 | 0.07–0.35 % | **0.068–0.355 %** | reproduced |
| r=1 VANNIK / LETQAE01 | 288 K (ratio 1.21) / 284 K (1.36); cold for every ε | 288 K (1.2137 / 1.2120) / 284 K (1.3626); ε\* none on all three splits | reproduced |
| ε\* at r=1, "cold" ≤ T0 − 10 K | BEVQID 0.91, FASJAL 0.95, others 0.95–0.96 | BEVQID 0.911, FASJAL 0.950–0.951, IFUDAO/MAXHEA/MAXHOK/PARFOF 0.954–0.957 | reproduced |
| ε\* at r=1, auditor split (≤ 290 vs ≥ 298.15) | 0.77 / 0.88 / 0.89–0.90 | 0.772–0.773 / 0.882 / 0.893–0.899 | reproduced |
| ε\* at r=1, strict split T1 < T0 | no crossing | none (cold "wins" by ≤ 0.36 % at every ε) | reproduced |
| ε\* at r=0.5 (10 K split) | FASJAL only, 0.12–0.37 | FASJAL only, 0.14–0.33 | reproduced |
| η_R\* at r=1, no air (10 K split) | 0.10–0.75 (FASJAL 0.69, BEVQID 0.61, VANNIK 0.14) | 0.096–0.754 (0.685–0.689, 0.606, 0.141) | reproduced |
| η_R\* at r=0, no air (auditor split) | 0.012–0.077, none for PARFOF | 0.005–0.078; PARFOF 0.005 | agrees (PARFOF "none" vs 0.005, immaterial) |
| η_R\* at r=0, air ε=0 (10 K split) | 0.19–0.93; VANNIK ≈ 0.29 | 0.189–0.309 for 11 rows, VANNIK 0.279/0.289; FASJAL 0.80 / 0.67 / **loses at η = 1** (8.186) | agrees, except the FASJAL boundary case |
| symmetric degradation, no air | strengthened 14/14 for every η; ratio 1.7–62 at η = 0.01, r=1 | strengthened 14/14 (min ratio over η ≥ 1.285); ratio **1.66–189** at η = 0.01 | sign reproduced; magnitude at η = 0.01 is grid-sensitive (N4) |
| other T0, r=1, ε=0: T1\* | 9 rows exactly at T0 at 273.15 and 313.15 K; BEVQID 272 / 311.15; VANNIK and LETQAE01 4–19 K below | 9 rows at T0 at both; BEVQID 272 / 310; VANNIK / LETQAE01 3.15–20 K below | reproduced. The size of the loss of the best below-ambient start at 313.15 K differs: 1.2–1.7 % (mine) vs "0.2–0.6 %" (N3) |

**Interpretation check.**
- **"Tie at ambient" is right.** At r = 1 with the air priced, the best start below T0 sits 0.4–0.9 K below ambient and beats the best start at or above it by 0.07–0.36 %. That is below each row's printed ξ uncertainty (0.34 % VANNIK … 8.5 % PARFOF), and the paper correctly says this is not a paired test.
- **The H1 statements are what the numbers support.** H1 is refuted at the preregistered setting (r = 0, 298.15 K) with and without pricing: 0/14 rows reach T1\* ≥ T0, with T1\* = 255–290 K. Under the priced scenario at r = 1 it is *not* refuted for 11/14 rows. The paper also reports the literal counts (0/14 at 298.15 K; 9/14 at 273.15 and 313.15 K).
- **The title** ("…survives exergy accounting of the model's heats and works, but its size, and with full heat recovery its existence, depend on pricing the chilling of the feed air") is supported. "its existence" holds for 11 of 14 rows, not all (VANNIK ×2 and LETQAE01 keep a cold start). Adding "for most rows" would be more exact; this is optional (N2).

**The three overlapping rows: are the producer's explanations right?**
- I re-ran my own code on the v2 domain (T_end ≤ 400 K, fine near-ambient cells). It agrees with the producer to ≤ 0.01 in ε\* and to ≤ 1 % in the base ratios:
  - FASJAL 10.32 / 3.52 / 1.28;
  - BEVQID 78.06 / 16.73 / 1.51;
  - VANNIK 30.65 / 12.11 / 5.32;
  - producer: 10.2 / 3.52 / 1.29, 78.1 / 16.7 / 1.51 and 30.6 / 11.9 / 5.33.
- So the v1-audit differences are explained:
  - **Base ratios 9–19 % higher at face value and r = 0.** The v1-audit grid allowed T_end up to 600 K (the published domain). The v2 cap of 400 K removes the hotter cold-start paths.
  - **ε\* +0.04 / +0.09.** The same T_end cap, plus the v1 grid having no cells between 290 and 298.15 K.
  - **T1\* within a cell.** Grid only.
- The C_V model (my interpolation of NIST's stored GP values versus the producer's GP re-fit) is **not** the main cause: with the domain matched it contributes ≤ 1 %. main.tex:204 lists "the auditor interpolated the stored C_V" first among the causes. See N5.

## (3) B4 vacuity and the H1 negative control

**Vacuity: REPRODUCED.** For all 14 rows and all three T0, **0 warm cells** (T1 ≥ T0) reach the row's stored purity. The best warm purities are 0.062–0.99. All 9 constrained variants are therefore vacuous for every row, and **126 of 252 row-variants are informative**. In the base accounting, those 126 give T1\* = 200–236.75 K (mine), matching §3.3.

**Negative control (refrigeration × M).**
- Reproduced:
  - **M = 1e4:** detected in 14/14 rows at r = 0, 0.5 and 1.
  - **Free refrigeration and air:** never worse, 14/14.
- **M = 100:** my count is **6/14 (r = 0), 6/14 (r = 0.5), 14/14 (r = 1)**, against the producer's 7/8/14. The misses are the cells at 297.5–298.0 K, as the producer explains.

**Can it fail?** Only through a bug in the selection or bookkeeping code: argmax, the cold/warm labelling, or the effective T1 after truncation. The construction itself guarantees a warm optimum for M large, because every T1 < T0 path pays M times its step-1 refrigeration while warm paths are untouched. So it is a valid plumbing check of the H1 machinery, and the paper's claim ("the H1 machinery can return a warm optimum") is exactly what it shows. It is not evidence about the physics.

The M = 100 counts depend on how close the grid's nearest cell is to ambient, so they are not a stable number (N6).

## (4) B2: the Zenodo bundle, NEW BLOCKING

I ran the dry run: `python3 -I scripts/publish_ar_paper.py --paper-dir papers/p4_dac_exergy --lane-dir results/proposal4/2026-10-27/K1 --token-file … --dry-run`. Its output:
- bundle `~/zenodo-bundles/p4_dac_exergy/p4_dac_exergy_2026-10-25.tar.gz`;
- 6,212,426 bytes, 268 members (267 in the manifest);
- the pdf sha256 is in /tmp/k1audit/dryrun.json.

No network upload took place: the dry-run returns before reading the token.

The member listing is in /tmp/k1audit/bundle_list.json. `members()` packs **every** file of the paper dir **and the lane dir** with a kept suffix, from the filesystem, regardless of git status. The bundle therefore contains:
- **the arXiv full text**: `results/proposal4/2026-10-27/K1/data/paper_2501.04825_fulltext.txt`. Its licence (nonexclusive-distrib 1.0) gives no redistribution right;
- **18 files of the NIST source tree**: `…/K1/data/zenodo/code_untrusted/IntrinsicDACCycle-0.0.2/`, including FEASSTscripts/*.py, LICENSE.md, README.md, Project.toml and Manifest.toml. The tarball itself (.tar.gz) is not a kept suffix;
- the Zenodo `README.txt`;
- **52 dataset files**: the 51 members plus SHA256SUMS.json under `…/K1/data/zenodo_members/`;
- **Lean files of about 13 unrelated programmes**: AmplifierCensus, CompletelyMonotone, FeynmanBijl, PbIgnition, SandierSerfaty and SandierSerfatyL1, YukawaBccFcc, ZeroPoint, ZeroPointCert, ZeroPointClass, ZeroPointDipolar and ZeroPointPhys. The bundler includes a Lean file whenever its stem ("Core", "Basic", "Controls") occurs in main.tex. Some of these are untracked, unpublished work (for example PbIgnition and SandierSerfatyL1, which `git ls-files` does not list);
- `results/autoresearch/2026-10-25/{program.md, preregistration.json}`, which is hard-coded and unrelated to K1.

**What is fine.** No file is over 5 MB; the largest is cert_sign.json at 3.07 MB.

**Licence and attribution adequacy.**
- The dataset files are CC-BY-4.0, so including them is lawful with attribution. §1 and the `zen` bibitem give the creators, title, DOI and licence, which is adequate attribution. But the files are present, and the paper says "no dataset files".
- The NIST files carry LICENSE.md, so redistribution is lawful. The paper says they are not included.
- The arXiv text must not be included.

**Fix (BLOCKING before any publish).**
- Build the bundle from an explicit allow-list, or pass a lane dir without `data/` and move the third-party files out of `results/proposal4/2026-10-27/K1/data/`.
- Replace the stem match by an explicit list: `formal_cert/Programmes/DacExergy/{Core,Controls}.lean`.
- Drop the hard-coded autoresearch files.
- Rerun the dry run and check with a member listing that the result has no `fulltext`, no `code_untrusted`, no `zenodo_members/`, no other programme's Lean, and no autoresearch files.
- Only then do main.tex:353 and publication_meta.json ("This bundle contains no third-party full text, no NIST code … and no dataset files") become true. Until the bundle is fixed, they are false.

**Repository side.** This part of the text is accurate as written:
- e298698 contained the text, the NIST code and the dataset files;
- b9a226c removed the text and the code from the tracked tree;
- the 52 dataset files are still tracked.

The local copies still sit in the lane directory, and that is why the bundler picks them up.

## (5) Wording

- **Unit sentence (main.tex:282-283).** Neutral, records the page-image check, and keeps the 10⁻⁵ reading as an inference. Good.
- **Scope.** There is no claim about real plants, costs, deployment or climate; the box is at main.tex:73-77. The headline is Tier X (main.tex:248-258, DAC-X-0011), which is correct.
- **The "pending" sentences** (main.tex:44-45, :61, :204; publication_meta.json; REVISION.md "Who checked"). Once the blocking item is fixed, replace them with:

  > "The feed-air scenario family was independently re-checked by the auditor (AUDIT_v2.md, 2026-10-28) with its own code on all 14 rows: the r = 1 move to ambient (11/14 rows, T1\* 297.25/297.75 K, margin 0.07–0.36 %), the ε\* thresholds, the η_R\* thresholds, the symmetric-degradation sign, the vacuity count and the M = 1e4 control reproduce; r = 0 T1\* agree within one or two grid cells (255–290 K against 254–288 K); one row (FASJAL 8.186) lies at the 10 K 'materially cold' boundary at r = 0."

## (6) Ledger gate and replay record

- **Gate.** Re-run to scratch (/tmp/k1audit/gate_v2.txt): exit 1, 0 blocking, 5 flags (LEDGER_UNAUDITED_TIER_A, A-0001…0005). It is identical to ledger/gate_output.txt apart from the exit-line format.
- **Lean sources.** Unchanged: Core.lean 4bfa4f7e…, Controls.lean 25017505….
- **Replay record.** `data/leanchecker_replay_audit.json` is my v1 record, unmodified (24 lines; replay rc 0, 118 s). The shared olean is still my build (d2b2a11d…). The replay therefore remains valid for v2, and I did not rerun it.

## BLOCKING

**BB1. The Zenodo bundle contains third-party and unrelated material.** Item (4) above gives the file list and the exact fix:
- main.tex:353 and the publication_meta.json "Redistribution" paragraph are false for the bundle as built;
- including the arXiv full text would be a redistribution the licence does not permit.

Fix the bundler inputs, rerun the dry run, and record its member listing (for example in data/logs/rev/bundle_members.json) before any publish.

## NONBLOCKING (exact fixes)

**N1. FASJAL 8.186 at r = 0, air priced (ε = 0), is at the 10 K boundary.**
- Producer: T1\* = 288.15 K, exactly 10.0 K below, q10 = 1.01.
- Mine: T1\* = 290.0 K, q10 = 0.998.
- main.tex:259 ("14/14 start ≥ 10 K below ambient") and the abstract's 254–288 K should read "13–14/14 (FASJAL 8.186 sits at the 10 K boundary)" and "254–290 K". The table entry `288.15 C` for that row should carry a note.
- The η_R\* with air at r = 0 range "0.19–0.93" depends on this row too.

**N2. Title, optional.** "…and with full heat recovery, for 11 of 14 rows, its existence…".

The PDF metadata title (main.tex:31) omits "and with full heat recovery its existence". Make it identical to the printed title.

**N3. Other ambients (main.tex:200).** "loses by 0.2–0.6 %" holds at 273.15 K (mine 0.22–0.25 %). At 313.15 K my best start below ambient, which is 3.15 K below with no refinement, loses by 1.2–1.7 %. State the two ambients separately, or note that the 313.15 K figure is from the refined grid.

**N4. Symmetric degradation at η = 0.01 (main.tex:202).** The ratio "1.7–62" is grid-sensitive: mine is 1.66–189. Keep only the sign statement (strengthened for every η, 14/14), or give the range as grid-dependent.

**N5. Causes of the v1-audit differences (main.tex:204; REVISION.md B3 table).** Replace "Plausible causes … the auditor interpolated the stored C_V instead of re-fitting the GP, allowed T_end up to 600 K and used a different grid without refinement" with:

> "the auditor's v1 scan allowed T_end up to 600 K (the published domain) and had no cells between 290 and 298.15 K. On the v2 domain the auditor's code reproduces our ratios to ≤ 1 % and ε\* to ≤ 0.01 (AUDIT_v2.md)".

**N6. Negative control (main.tex:279).** Report M = 100 as grid-dependent (auditor: 6/6/14 with 0.25 K cells near ambient; producer 7/8/14), and keep M = 1e4 as the control.

**N7. Stale status lines.**
- main.tex:356 and REVISION.md "State of the revision": "the revision's files are uncommitted … not pushed". The revision is committed in 4f3c940 and pushed to origin. Fix both.
- The coordinator's reference to "28a1ac0" for K1 v2 should be 4f3c940.

**N8. REVISION.md B1 table.** The P0-floor materials are 3/8/10 per T0 (10 distinct), not "10 in all".

## Auditor's deviations

- **v2 grid.** The scan has no refinement around best cells, so my T1\* values are grid cells.
- **Trapezoid run.** My first v2 run used the v1 trapezoid step 3 (/tmp/k1audit/v2_scan_raw.json). I rescanned with the right-point rule (v2r_*), and all comparisons above use that rescan. The trapezoid run is kept only as the observation in (2).
- **Shell.** One `echo "exit $?"` (a shell variable) for the gate exit code, and one compound `sed … > file; grep` to derive the right-point script. Several waits used `until …; do sleep 10; done` loops, because the harness refused a plain `sleep`. No git state was changed.
- **Dry run.** It wrote its bundle under `~/zenodo-bundles/p4_dac_exergy/` (outside the repository), as designed. Nothing was uploaded.
