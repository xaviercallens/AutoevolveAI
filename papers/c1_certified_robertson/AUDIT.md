# Independent audit: "Independent certification of a validated enclosure of Robertson's problem" (C1 preprint v1, 2026-11-25)

Auditor: AI agent (Claude), adversarial reviewer. I did not produce any of the work, and no human was involved.
Inputs: `main.tex`/`main.pdf` in this folder; numerica_repo at commit 34d955d (read-only); `~/c1c_extract/`, `~/c1c_full_logs/`; PH-2 sources.
Scratch reruns: `rerun/` (discrepancy scripts) and `gate/` (Lean gate). No repository was modified.

## VERDICT: ACCEPT_WITH_CORRECTIONS

- No BLOCKER.
- 9 REQUIRED corrections (R1 to R9 below).
- 13 OPTIONAL improvements.

The core claims hold up:
- The headline numbers match their sources.
- The Lean files pass the gate when I rerun it.
- The checker's arithmetic matches the Lean hypotheses on my reading.
- The producer-artefact explanation is confirmed by the producer's source code.

The REQUIRED items fall into four groups:
- one wrong number (R1);
- a description of the checker controls that overstates what was tested in the headline mode (R2);
- missing limitations (R3, R6, R9);
- evidence absent from the evidence repo, or contradicted by it (R4, R5).

Wording fixes R7 and R8 are also REQUIRED.

### REQUIRED corrections

**R1. Wrong number, main.tex:79.**
- Paper: "Mathlib's ready-made lemma bounds ‖A‖ instead, which for Robertson is about 10^8."
- Measured values: `jnorm_all.py` evaluates every record of `data/steps_0_10.jsonl` (2,372 records, t ≤ 10) and both extracts (2,111 + 2,201 records), using Robertson J at the record's q(0) and the record's P.

  | Records | max ‖J‖₂ | max ‖P⁻¹JP‖₂ | max cond(P) | max y2 |
  |---|---|---|---|---|
  | steps_0_10.jsonl (t ≤ 10) | 3.10e3 | 2.56e3 | 17.4 | 3.649e-5 |
  | range1 (steps 287,990 to 290,100) | 6.12e3 | 6.12e3 | 1.03 | — |
  | range2 (steps 423,900 to 426,100) | 6.49e3 | 6.49e3 | 1.02 | — |

- Analytically, ‖J‖ ≲ 1.3e4 on the whole trajectory: |entries| ≤ 0.04 + 1e4·y3 + 6e7·y2, with y3 ≤ 1 and the measured max y2 = 3.65e-5.
- ‖P⁻¹JP‖ also depends on cond(P). I measured it only at the 6,684 records listed above; t > 10 outside the two windows was not checked.
- 1e8 is only the crude global constant 1.3e8 in `robJ_norm_le` (L5Complete.lean:324), i.e. the coefficient scale of the field.
- Fix: write "‖J‖ is of order 10^3 to 10^4 along the trajectory". The argument survives, since e^{Kh} per step is still ruinous over 2.8M steps.
- The same wrong figure is in OneSidedGronwall.lean:12, TubeInvariance.lean:12 and docs/10:73 (comments only, OPTIONAL).

**R2. Checker controls overstated for the headline mode, main.tex:104.**
- Paper: "five corruptions of the records (defect dropped, ν lowered, h doubled, a wrong inverse, the carried error halved) are each rejected at the intended check".
- In the headline configuration (`--mode derive --chain exact`), that is not true. The record shows:
  - **(i) defect dropped:** ACCEPTED 71/71 in derive (RESULTS.md:44); ACCEPTED N/N in exact (RESULTS_C1B.md:55).
  - **(ii) ν lowered:** never run in any derive mode. It ran in CLAIMS mode only (RESULTS.md:45-46, RESULTS_C1B.md:56).
  - **(v) carried error halved:** ACCEPTED 71/71 in derive (RESULTS.md:52). Listed as "not applicable" in exact and never run there (RESULTS_C1B.md:62).
  - **(iv) wrong inverse:** ACCEPTED N/N in exact by design (RESULTS_C1B.md:60). It was rejected only in derive/spec and derive/frob (RESULTS.md:49, RESULTS_C1B.md:59).
  - **(iii) h doubled:** rejected in exact (RESULTS_C1B.md:57; the stream control in RESULTS_C1C.md:42).
  - **(vi) singular P:** rejected in exact (RESULTS_C1B.md:63).
  - PREREG.md:45-46 had already said that (i), (ii) and (v) cannot be tested in derive mode.
- Fix: say per control which mode it ran in. State plainly that in the headline mode only these gate a step:
  - continuity and shape (C0);
  - invertibility (C1);
  - the tube condition (C4);
  - finiteness.
- C4 adds little on its own. ρ = 8(ε₀ + d̄h) (lib.rs:523-525) and lhs = (ε₀ + d̄h)·e^{ν₊h} (lib.rs:553), so lhs/ρ = e^{ν₊h}/8 up to rounding, and C4 reduces to ν₊h < ln 8.
  - The "largest tube ratio 0.1314 (a margin of 7.6)" at main.tex:111 therefore says only that ν₊h ≈ 0.05 at step 26. It is not a robustness margin of the enclosure; reword it.
  - The factor 8 matters through U, and hence through ν in C3, not through C4.
- C2, C3, C5 and C7 are derivations that fail only on non-finite values (lib.rs:518, 541, 561, 570).
- Their correctness rests on the code being right, and no negative control exercises them in that mode:
  - no corrupted q coefficient;
  - no mutated field or Jacobian.
  - lib.rs:372 confirms that no internal faults are provided.

**R3. Missing limitation: there is no Lean statement of the multi-step result.**
- Lean proves a one-step theorem (`robertson_onestep_complete`), a chaining inequality (`chain_sigma`) and two-piece gluing (`glue_solutions`/`robertson_glue`).
- No Lean theorem composes N steps. The induction over 2,843,424 steps, the bookkeeping of ε, and the conclusion "the true solution lies in this box at t = 4000" exist only in the Rust loop.
- The Lean files are also standalone and do not import each other. `robF` is defined separately in RobertsonOneStep.lean:143, L5Complete.lean:284 and L6Chaining.lean:163, and `chain_bound` appears in both L6Chaining.lean:11 and SigmaMax2x2.lean:6. Agreement between the copies is textual, not kernel-checked; I checked by eye that the three `robF` copies are identical.
- Fix: say this in the abstract and in §6, so that "Lean-checked … certified" is not read as "formally verified enclosure".

**R4. The headline evidence is missing from the evidence repo.** The bundle itself was not provided to me; this finding is about the repo.
- `git ls-files phase3/c1_checker/full_run` lists only `checker.err`, `hashes.txt` and the three `time_*.txt` files.
- `checker.out`, `producer.log` and `run.log` are excluded by `.gitignore` (numerica_repo/.gitignore:3-4: `*.log`, `*.out`).
- The equivalent files for the t ≤ 40 run are tracked (`out_c1c/run40/checker.out`, `producer.log`, `run.log`), so force-adding them has a precedent.
- In the repo, `checker.err` ends at "progress steps=2840000 … certified=2839999".
- The following exist only in `~/c1c_full_logs/checker.out`:
  - "certified 2843424/2843424", "VERDICT ACCEPTED";
  - max lhs/rho 0.131361 and max ν +244.7;
  - every eps_end and radius ratio in the table.
- The producer ε column and "reproduces the published step counts" rest on `~/c1c_full_logs/producer.log`.
- The paper (main.tex:152) says the run logs are in the bundle. Force-add these three files and list them in the manifest before publishing.
- Their content does match the paper (see N1).

**R5. A failing gate record ships next to the passing ones.**
- `phase1/lean_L6b_2026-11-23/gate_SigmaMax2x2.json` records `chain_initial_bound` and `chain_opNorm_le` as `compiled: false, has_sorry: true` (lines 14-26).
- `gate_main.json` and `gate_main_rerun_by_main_session.json` in the same folder show 16/16. My rerun is also 16/16 (see L1).
- As shipped, the bundle contradicts main.tex:71-72 ("Every theorem named below passed the gate"). Remove the stale file or label it as an earlier failing run.

**R6. The discrepancy claim is too strong in the abstract (main.tex:40-41, "we show that this comes from…").**
- The evidence covers two windows totalling 4,312 records plus a 281-point sample of t ≤ 1000 (main.tex:144).
- Most of the final gap is outside it. The radius ratio falls from 0.1395 at t = 1000 to 0.0565 at t = 4000 (checker.out), a further factor of about 2.5, and that range was not examined.
- `test_dependency_model.py` inverts the producer's ε_end under the assumed model. A constant implied ν_lo is consistency with the model, not an independent test.
- The strongest evidence is the producer source itself, and the paper does not cite it. It is quoted here with that caveat attached:
  - PH2/code/ph2_enclose.py:238-248 computes ν as a ball, stores `nu.upper()`, and evaluates `g = ((nu*Hb).exp() - 1)/nu` with the ball ν whenever `nu.upper() < 0`. That is exactly the stated mechanism.
- Fix: in the abstract, write "we give evidence that … (two windows and a sample, t ≤ 1000)". In §5, cite ph2_enclose.py:244-248.
- Also say explicitly that this analysis explains the producer's looseness. It is not what makes the checker sound; that rests on C3 and C5.

**R7. Two discrepancy numbers are imprecise, main.tex:135-136.**
- "our ν equals the producer's claimed ν at 213 of 281 samples; the other 68 differ by a tiny one-sided 2·10⁻⁸".
- The diagnostic file prints ν to 5 significant digits (diag_every2000_t1000.txt). "Equal" therefore means equal at that printed precision. RESULTS_C1C_FULL.md:44-45 claims "to 1e-9", which the printed data cannot support.
- My parse of that file (`diag_nu.py`) gives 213 equal and 68 unequal, with the first mismatch at 426,000. The differences range from −2.0e-8 to −4.0e-8 (e.g. step 426,000: −3.3328e-4 vs −3.3326e-4).
- Fix: write "differ by 2 to 4·10⁻⁸" and "equal to the printed 5 significant digits".

**R8. The table's step column is ambiguous, main.tex:116-127.**
- The column holds the 0-based index of the last step: 70, 135, …, 2843423.
- The producer and the published record count steps: 71, 136, …, 2,843,424 (producer.log; PH2 logs/robertson_run.log:2-18).
- The text says 2,843,424 steps. Label the column "last step index (0-based)".

**R9. "lies inside the published one" (main.tex:39) is true, but only through an unstated step and only for (y2, y3).**
- The checker compares against `data/stored_enclosure_t*.json`. These were extracted from PH2 `logs/enclosure_ckpt.json` (RESULTS_C1C.md:10), not from the published `enclosures.json`.
- I checked (inline script): the stored boxes have the same midpoints as the published ones and radii smaller by about 1.6e-9 relative, so stored ⊆ published at all 10 times. With "ours ⊆ stored" (checker.out) the claim holds transitively.
- It holds only for the reduced components (y2, y3). The published y1 interval is not compared.
- Also, "t = 0.1" and "t = 0.4" are the doubles 3602879701896397/2^55 and 3602879701896397/2^53 (time_checker.txt command line), not 1/10 and 4/10.
- Fix: state these three points briefly.

### OPTIONAL improvements

- O1. main.tex:141, "≈ 540". This is the extreme case, step 425,752 (g_claim/h = 336,150, h = 1.608e-3). At the other leap steps, g_claim is about 0.5 to 3.2, i.e. g/h is 318 to 2,000 (dependency_model_test.txt). Write "up to ≈ 540".
- O2. main.tex:138-139, "its ε_end grows by factors 1.04, 1.12, 1.34, 2.04". These numbers are ratios of the claimed ε_end to the Grönwall value of its own ε0, ν, d (growth_range2.txt). They happen to equal step growth because ν ≈ 0, but say which one is meant.
- O3. Title and abstract: "Independent". The paper itself says it is independent code, not an independent method (main.tex:148), and producer and checker come from the same AI agent family. Consider "independent re-check" or "second implementation".
- O4. `robertson_onestep_complete` has no Robertson-specific non-vacuity witness. The witnesses (L5Complete.lean:524-572) are for f = −id on ℝ. Its hypotheses are clearly satisfiable, but a witness would close the question.
- O5. main.tex:85-86: uniqueness also requires `ContinuousOn z'` (L5Complete.lean:479). Also, `hRq` (a bound on q) is a hypothesis the checker does not discharge. It is trivially satisfiable for a polynomial on a compact interval; mention it.
- O6. The L6 negative control "dropped hypothesis" (control2_dropped_hypothesis.lean.txt) fails to compile with `Unknown identifier 'hmatch'` (my rerun, line 184). That is a syntactic failure, not evidence that the hypothesis is mathematically needed. The "minus sqrt" control fails inside the proof of `sigma_sq_pointwise` (line 109, linarith), which is a meaningful rejection.
- O7. RESULTS_C1C_FULL.md:52-53 swaps the hash labels of the two range files. By extract_records.sh:10-11 and my `sha256sum`, e2fb2ee8… is range1.jsonl (steps 287,990 to 290,100) and 7253ec29… is range2.jsonl (423,900 to 426,100).
- O8. main.tex:52-53 says the checker field and Jacobian "have not been compared by a person". You can add that this AI audit compared them and found them identical (see C1), while keeping the human comparison as owed.
- O9. main.tex:96-97, "the basis P with its radii". In the records, P is an exact rational matrix (P_rad all zero in the extracts; lib.rs:176-177 parses P as rationals). Only Pi carries radii, and exact mode does not consume Pi.
- O10. Add a mutation test of the checker: perturb one Jacobian or field coefficient, or one q coefficient, and show that C4 or the comparisons fail. This is the missing control for derive-mode C2 and C3 (see R2).
- O11. The constant implied ν_lo per region (−2.64e-3, −3.52e-3) is not explained. Recomputing the producer's ν ball for one leap step with Sage (ph2_enclose.py:236-238) would turn the consistency check into a direct confirmation.
- O12. main.tex:72, "with exactly {propext, Classical.choice, Quot.sound}". This is true for every theorem the paper names in L5Complete, L6Chaining and SigmaMax2x2 (my rerun). I did not rerun the other files.
- O13. main.tex:154: "it has had one independent AI audit (AUDIT.md in the bundle)" should give that audit's verdict, and should say that it is an AI audit by the same model family.

## Findings by task

### 1. Numbers (all checked against primary files)

| Paper item (main.tex line) | Source | Status |
|---|---|---|
| 2,843,424 of 2,843,424 certified, none rejected (39, 109) | ~/c1c_full_logs/checker.out:2; run.log | OK, but not in repo (R4) |
| ten comparisons hold, ours inside stored (110) | checker.out OUTPUT lines, all `ours_contained_in_stored=true HOLDS=true` | OK |
| wall 22,852 s, 6 h 21 min (39, 110) | run.log `wall_s=22852`; time_checker.txt 6:20:51 | OK |
| producer 214 MB, checker 5.6 MB (110) | time_producer.txt 213,832 kB; time_checker.txt 5,632 kB | OK |
| max tube ratio 0.1314, margin 7.6 (111) | checker.out:3 `max lhs/rho=0.131361 (step 26)` | number OK; meaning is e^{ν₊h}/8, see R2 |
| max ν +244.7 at step 26 (111) | checker.out:3 `+2.447396e2 (step 26)` | OK |
| cumulative sha256 eb8e6e62… (112) | full_run/hashes.txt t=4000 and END lines | OK |
| table producer ε, all 10 rows | producer.log = PH2 robertson_run.log:2-18 | OK |
| table checker eps_end, all 10 rows | checker.out eps_end values | OK |
| table radius ratios 0.941 … 0.057 | checker.out rad_ratio (0.940917 … 0.056534) | OK |
| table step column | 0-based index; counts are +1 | R8 |
| factor 7 at t=1000, 18 at t=4000 (40) | 1/0.139538 = 7.17; 1/0.056534 = 17.7 | OK |
| Frobenius chain fails from step 132 (131) | RESULTS_C1B.md:41 | OK (not rerun) |
| 11,382-record stream, h doubled at middle, first failure at that index (105) | RESULTS_C1C.md:42 (step 5691, C0) | OK (not rerun) |
| 213 of 281, 68 mismatches, first at 426,000 (136) | diag_every2000_t1000.txt; my parse | counts OK; magnitude R7 |
| 4,310 transitions, ≤ 0.1 % (137) | rerun chain_range1/2.txt: 0 of 2110, 0 of 2200 | OK |
| factors 1.04/1.12/1.34/2.04 at 425,749 to 425,752 (138-139) | rerun growth_range2.txt: 1.039103, 1.115085, 1.335125, 2.038674 | OK (O2 wording) |
| 15 leap steps, implied ν_lo −2.636e-3 to −2.645e-3; ν_up −8e-9 to −8e-6 (142-143) | rerun dependency_model_test.txt: min −2.6445e-3, max −2.6362e-3; ν_up −7.86e-9 to −8.294e-6 | OK |
| 3 leap steps, −3.517e-3 to −3.520e-3 (143) | rerun: −3.5165e-3 to −3.5201e-3 | OK (rounding) |
| ≈ 540 (141) | step 425,752 only | O1 |
| ‖A‖ ≈ 10^8 (79) | max measured ‖P⁻¹JP‖ 6.5e3 over 6,684 records | **R1** |
| ν difference 2·10⁻⁸ (136) | −2e-8 to −4e-8 | **R7** |
| 256-bit Arb, flint3-sys 3.6.1 (96) | ball.rs:8 `PREC = 256`; Cargo.toml:8, Cargo.lock:35-36 | OK |

Discrepancy-script reruns, `.venv` python -I on `~/c1c_extract/`:
- The extract hashes match: range1 e2fb2ee8…, range2 7253ec29….
- `chain_range1.txt`, `chain_range2.txt`, `growth_range1.txt` and `growth_range2.txt` are byte-identical to the committed files.
- `dependency_model_test.txt` differs only in the order of the two blocks; the content is identical.

N1. The content of the uncommitted logs agrees with the paper. Committing them is a matter of record-keeping (R4).

### 2. Lean claims

**Gate rerun.** Command: `lean_runner … --formal-dir …/AutoevolveAI/formal`, on copies in `gate/`.

| File | Exit code | Theorems passing | Note |
|---|---|---|---|
| L5Complete.lean | 0 | 21/21 | |
| L6Chaining.lean | 0 | 18/18 | |
| SigmaMax2x2.lean | 0 | 16/16 | |
| neg_roblip_const (constant 1.3e8 → 1) | 1 | rejected | |
| control1_minus_sqrt_final (F² − √) | 1 | rejected | error L109 in the proof |
| control2_dropped_hypothesis | 1 | rejected | syntactic, unknown identifier (O6) |

- Every named theorem has axioms exactly {propext, Classical.choice, Quot.sound}: `robertson_onestep_complete`, `onesided_norm_le_gronwallBound`, `truncated_error_stays_in_tube`, `robertson_hasFDerivAt`, `chain_sigma`, `sigma_opNorm_le`, `chain_bound`, `glue_solutions`, `robertson_glue`.
- Each file contains its own `#print axioms` lines.
- The committed gate JSONs of the other files pass (`gates.py`). The exception is the stale gate_SigmaMax2x2.json (R5).

**Statement versus description.**
- `onesided_norm_le_gronwallBound` (L5Complete.lean:102-109): the paper's description is correct.
  - The Lean hypotheses are, if anything, weaker than the description: right derivatives, `ContinuousOn`, a time-dependent A, and the one-sided bound only along the trajectory.
  - ν has any sign. The conclusion is `gronwallBound ε₀ ν d (x − a)`.
- `truncated_error_stays_in_tube` (L5Complete.lean:154-186): an abstract form, with a scaling c(x) ∈ [0, 1] of A.
  - The tube condition is `(ε₀ + d(T − a)) e^{max(ν,0)(T − a)} < ρ`, and the conclusion is strict.
  - The paper's phrasing ("field clamped by a retraction … no first-exit argument") is accurate when read together with `onestep_complete_modulo_existence`, where the retraction is applied (L5Complete.lean:243-255).
- `robertson_onestep_complete` (L5Complete.lean:463-481): the existence claim is genuine.
  - z is obtained from Picard–Lindelöf on the clamped field (`truncated_exists`, L5Complete.lean:393-453). It is not assumed.
  - The one-sided bound is required for all y ∈ U and all v (L5Complete.lean:470), with U ⊇ {q(t) + Pu : ‖u‖ ≤ ρ} (L5Complete.lean:469). It is not assumed along the trajectory: the along-trajectory form is derived via the midpoint lemma (L5Complete.lean:238-242, 275-280).
  - D is defined by `HasDerivAt q (robF (q t) − D t)` (L5Complete.lean:467), i.e. D = f(q) − q′.
  - The defect bound is `‖P⁻¹ D t‖ ≤ d` on Ico.
  - The conclusion covers: strict tube, ODE solution on Icc, the sharp Grönwall bound with the scalar ν, and uniqueness among continuous, right-differentiable solutions.
  - I found no vacuous or unused hypothesis. `hRq` is used to build the Lipschitz ball (L5Complete.lean:484-508).
  - Caveats O4 and O5.
- `robertson_hasFDerivAt` (L5Complete.lean:304) and robJ (L5Complete.lean:288-297) match the paper's claim.
- `chain_bound` (SigmaMax2x2.lean:6-16) and `chain_sigma` (SigmaMax2x2.lean:164-177) match main.tex:87-88.
  - The hypothesis `∀ v, P'.symm (P v) = mat2 a b c d v` is the "P′⁻¹P = C" of the paper.
  - The mat2 convention is row-major (SigmaMax2x2.lean:35-45), as in `rat_mm` (lib.rs:97-100). Since F² and det are invariant under transposition, the convention would not matter anyway.
- `sigma_opNorm_le` (SigmaMax2x2.lean:111-114) is the exact 2×2 formula.
- `glue_solutions` / `robertson_glue` (L6Chaining.lean:169-217) cover two pieces only (R3).

**Lean hypotheses versus Rust checks, exact/derive mode.** This is my correspondence check by reading, not a proof.

| Lean hypothesis | Rust check | Match |
|---|---|---|
| P is a ContinuousLinearEquiv | C1: exact rational det ≠ 0, exact rational inverse (lib.rs:85-94, 417-432) | yes |
| hD: ‖P⁻¹D(t)‖ ≤ d on [0, h) | C2: d = Σ_k ‖P⁻¹ D_k‖ h^k, D_k = [t^k] g(q) − (k+1) q_{k+1}, k = 0..2p−2 (lib.rs:301-323, 509-516), complete for a quadratic field and degree p−1; triangle inequality on [0, h] | yes, sign D = f(q) − q′ matches |
| hU: U ⊇ {q(t) + Pu : ‖u‖ ≤ ρ} | box: Horner(q, [0, h]) + ‖row_c(P)‖₂ ρ [−1, 1] (lib.rs:529-536); \|(Pu)_c\| ≤ ‖row_c‖‖u‖ | yes |
| hν: ⟪v, P⁻¹J(y)Pv⟫ ≤ ν‖v‖² for all y ∈ U | C3: λ_max of the symmetric part of Pi·J(U)·P via the closed form in ball arithmetic, upper end (lib.rs:326-343, 537-539); an interval extension encloses the range over U | yes |
| htube: (ε₀ + d h) e^{max(ν,0) h} < ρ | C4: lhs = (ε₀ + d h)·exp(ν₊ h), upper end, strict `lt` (lib.rs:523-555) | yes |
| conclusion gronwallBound ε₀ ν d h | C5 at the scalar upper end of ν: (e^{νh} − 1)/ν for ν < 0, h e^{νh} (≥ the exact value) for ν ≥ 0 (lib.rs:557-559); monotone in ν | yes |
| chain_sigma with C exact | C6: `rat_mm(inv, prev.p_rat)`, exact F² and D, only the sqrt is a ball, upper end (lib.rs:110-124, 482-488); jump = Horner(q_prev, h) − q(0) | yes |
| output | C7: q(h) ± ‖row_c‖ ε_end (lib.rs:564-569) | yes |
| initial value | step 0 requires t0 = 0 and q(0) = 0 exactly (lib.rs:402-405); ε₀ = 0 | yes |

**C1. Field and Jacobian.**
- Rust `defect_coeffs` (lib.rs:300-322) and `jacobian` (lib.rs:326-332) match Lean `robF`/`robJ` (L5Complete.lean:284-297) coefficient by coefficient:
  - g2 = (4/100)(1 − y2 − y3) − 10000 y2 y3 − 30000000 y2²;
  - g3 = 30000000 y2²;
  - J = [[−0.04 − 1e4 y3 − 6e7 y2, −0.04 − 1e4 y2], [6e7 y2, 0]].
- This is an AI comparison, not the human one the paper says is owed.

**Producer claims in derive mode.** No producer claim reaches a gating decision:
- ε₀, d and ν used downstream are the checker's own values (lib.rs:498-499, 517-518, 540-541).
- In exact mode the claimed Pi is used only for a non-gating note (lib.rs:419-431).
- `eps_end_claim` is used only for the displayed ratio (lib.rs:560).

### 3. Checker soundness

- Exact rationals are used where the paper says they are: P⁻¹ and C = P′⁻¹P (lib.rs:85-100). Pi then enters the ball computations as an enclosure of the exact rational (ball.rs:136-141).
- Rounding: every quantity that feeds a decision is taken at its rigorous upper end (`arb_get_ubound_arf`, ball.rs:246-257). Comparisons are certified:
  - `lt` means the difference is certainly positive;
  - `le` means no negative element (ball.rs:322-330).
- I found no use of a midpoint where an upper bound is needed.
- `sqrt_nn` clamps negatives before the square root (ball.rs:224-237). In exact mode, F⁴ − 4D² < 0 returns an error instead (lib.rs:119-121). In `nu_of` the argument is nonnegative.
- Continuity: t0 + h must equal the next t0 exactly, and the last step must equal t_end (stream.rs `push`/`finish`). The q mismatch at step boundaries is absorbed by the jump term.
- I found no way for a false step to be accepted, assuming Arb/FLINT and the FFI wrapper are correct. That assumption remains the trust base; 38 `unsafe` blocks are in src/.
- Weaknesses:
  - In derive mode, C2, C3, C5 and C7 are derivations that gate only on finiteness, and the headline mode has no mutation or negative control for them (R2, O10).
  - There is no automated cross-check of the hard-coded field against Lean (C1 is by reading).

**Discrepancy explanation.**
- The mechanism is confirmed in the producer source (ph2_enclose.py:236-248): ν is a ball, `nu.upper()` is recorded, and g is computed by ball division when `nu.upper() < 0`.
- The checker evaluates g at a point ν (lib.rs:557-558), so it cannot have this artefact.
- I see no alternative explanation that fits better. Everywhere else the chain values agree to within 0.1 % (4,310 transitions). The ν agreement at 213 of 281 samples also rules out a systematically optimistic ν in the checker.
- The limit at main.tex:144 is stated honestly in the body but omitted from the abstract (R6).

### 4. Overclaims, tiers, disclosure

- The tier labelling is honest throughout (main.tex:42-43, 47-49, 52-55, 93, 147-149). Nothing claims Tier A, and "Tier A candidate" is defined.
- The AI disclosure (main.tex:153-155) is present and specific. "No human has reviewed the Lean statements" appears at main.tex:43, 93 and 149.
- Overclaims and gaps, each covered by a REQUIRED item:
  - abstract "we show" (R6);
  - checker controls (R2);
  - no Lean multi-step statement (R3);
  - "published" containment (R9).
- The title's "Independent" is softened in the body (O3).
- "Lean-checked one-step theorem" in the title is accurate.
- A reader could still take "the checker certifies every step under the hypotheses of those theorems" (main.tex:50-51) as machine-checked. The next sentence (52-55) correctly disclaims it.

### 5. What I did NOT check

- I did not rerun the producer or the checker (6.5 h), so the stream hashes, `cargo test` and the C1b/C1c controls were not reproduced. All of those are taken from the committed or uncommitted logs.
- I did not rerun the gate on RobertsonMidpoint, OneSidedGronwall, OneStepModuloTube, RobertsonOneStep or TubeInvariance; I relied on the committed gate JSONs. I reran only 3 of about 16 negative controls.
- I did not read docs/10, 11, 16, 17 and 18 beyond grepping them, and did not review json.rs/main.rs or the FFI declarations in detail.
- I did not see the evidence-bundle manifest, so I could not check its sha256 list.
- I checked the PDF against the tex only by spot greps (the 10^8, 540, 2·10⁻⁸, hash and step-count lines match).
- I did not verify the PH-2 claim that its run was interrupted and resumed beyond the existence of launch2/launch3 and the resume script.
