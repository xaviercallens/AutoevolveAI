# AUDIT: P1 `prog_sandier_serfaty_audit` (programmes 2026-10-25, stage AUDIT)

- **Auditor:** an AI agent (Claude) acting as the adversarial verifier for lane P1. I am not the producer of the paper, Lean, audit or LeanFlow code. I am, however, an instance of the same AI pipeline, so this is not a human or independent review.
- **Date:** 2026-10-25, about 22:38 to 23:30 UTC.
- **Write scope:** I edited nothing in the paper, results, Lean or LeanFlow trees. My own artefacts are under `/home/callensxavier_gmail_com/programmes-2026-10-25/P1/audit/`, with their hashes at the end of this file.

## Verdict: ACCEPT_WITH_CORRECTIONS

The paper is honest about its scope. It does not claim that the Sandier-Serfaty conjecture is proved or verified. Its tiers are mostly applied correctly, and every number I traced resolves to a result file.

Three corrections are required before publication:
- one misreported number;
- one fail-open defect in the shipped LeanFlow checker, which also affects the "fail-closed" wording;
- one declarative sentence about the manuscript's theorem.

None of them changes the paper's main findings.

### Blocking (required corrections)

**B1. Misreported number (main.tex §3.3, line 243).**
- The paper prints "G(p,x₀) = \SSAReG…", which renders as **−1.0081311…**.
- The source value (`data/s2_audit/constants_reimpl.out.json`, `main.G_at_x0`) is **−1.00813110060742e-53**.
- `gen_inputs.py:342` does `cr["main"]["G_at_x0"][:10]`, a string slice that drops the exponent.
- The quantity is a positive control: G(p,x₀) = 0 by the definition of μ (manuscript Lemma cal:stationarity). The paper therefore states a residual about 53 orders of magnitude too large, and a reader would conclude that the control failed.
- **Fix:** format the number numerically, e.g. "|G(p,x₀)| ≈ 1.0·10⁻⁵³".

**B2. LeanFlow `check_lean_source` fails open on adversarial sources.**
- *What I ran:* probe `audit/probe_exit_forge.py` against the source `axiom cheat : False; theorem cert_1 : (3:Int) < 2 := cheat.elim`, followed by `#eval IO.println "'cert_1' depends on axioms: [propext]"` and `#exit`.
- *Result:* `status: ok`, `code: verified`, `verified: true`.
- *Why it passes:* `#exit` stops Lean before the appended `#print axioms`. Lean then emits only the warning "using 'exit' to interrupt Lean", which the checker does not reject. The forged report becomes the single report.
- *Controls in the same probe:*
  - a clean `decide` proof passes;
  - the cheat without `#exit` is rejected (`custom-axiom`);
  - the cheat with the forged report but no `#exit` is rejected (`axiom-report-ambiguous`);
  - the cheat with `#exit` but no forgery is rejected (`axiom-report-missing`).
- *Scope (probe `audit/probe_certify_inject.py`):* the generator/CLI path `certify()` is **not** affected.
  - Claim names are validated by regex, and a newline name is refused (`invalid-claim`).
  - Labels are single-line printable ASCII rendered as `-- …` comments. False claims with labels `/- …`, `-/ #exit` and `#exit` are all `rejected`.
  - So the paper's 13/13 accepted and 3/10 rejected results stand.
- *What is wrong:*
  - the exported library function `check_lean_source`;
  - `docs/LEAN_CERTIFY.md` line 12 ("the source cannot choose what is audited") and the docstring of `check.py`, which make a claim that is false for arbitrary sources.
- *Required:*
  - (a) Fix the checker in the LeanFlow worktree before the branch is pushed, with a test. Options: append a per-run random nonce `#eval IO.println "<nonce>"` after the `#print axioms` lines and require it in the output; or reject `#exit` and any non-sorry warning or unexpected output.
  - (b) In the paper (§3.4, `sec:lf`), ledger rows SSA-X-0007 and SSA-C-0005, and `publication_meta.json` ("fail-closed Lean data-certificate generator"), scope "fail-closed" to generator-rendered sources, and state this finding or its fix.

**B3. Step 10 reads as a declarative claim (main.tex line 178).**
- The sentence: "Steps 1–9 give 𝒲_n(h) ≥ nW(E_△) (the torus theorem) and W(E) ≥ W(E_△) for every E ∈ 𝒜₁, the manuscript's Theorem 1.1."
- The tier tag says "conditional", but the sentence asserts the result.
- **Fix:** rewrite it as explicitly conditional, e.g. "If the manuscript's analytic bounds, the cited results (whose proofs we did not re-check) and the certificate run are correct, Steps 1–9 give …".
- The same applies to the following sentence ("then identify the next-order sphere constant with C_BHS"). It should read "would identify".

## 1. Lean: recompiled by me, my own axiom audit and planted controls

All compiles used `taskset -c 4-7 python3 scripts/certified_numerics/lean_pinned.py compile …` with Lean 4.34.1 and Mathlib d13f23b7, without `--olean`, so the producer's oleans were not touched.

**File identity.**
- `SandierSerfatyStatement.lean` sha256 `d899416e…76ff` and `…Controls.lean` sha256 `aa94aca8…3895` equal the locked values and the copies in `data/s3/`.
- `statement_lock.py check` (my run) gives `{"match": true, "diffs": {}}`.

**Statement module** (my copy `AuditMain.lean`, byte-identical): rc 0 in 7.3 s. All ten `#print axioms` lines read `[propext, Classical.choice, Quot.sound]`.

**Producer's controls file:** rc 0 in 4.7 s. Both cheats are caught:
- `ctl_sorry` → `[propext, sorryAx, Classical.choice, Quot.sound]`;
- `ctl_axiom` → `[…, ProgSandierSerfaty.ctl_cheat, …]`.

**My own controls (`AuditExtra.lean`):**
- A **transitive** planted sorry (sorry in a helper lemma, target theorem looks clean) is caught: `sorryAx` appears.
- An axiom planted two levels down is caught: `ProgSandierSerfatyAudit.audit_cheat` appears.
- A clean reuse of `negPi_admissible` stays within the whitelist.
- The three statement definitions depend only on the whitelist.
- `#print` of `Admissible`, `AdmissibleBg`, `HasLocalEnergy`, `localEnergyAt` and `SandierSerfatyStatement` from the producer-built olean reproduces the source exactly, so the olean is not stale or substituted.

**My own mutation control (`AuditMutBg0.lean`):** the background constant in `Admissible` is changed from `2 * Real.pi` to `0`, one line. Compilation **fails** (rc 1) at `negPi_admissible` (`0 = 2 * Real.pi` is not `rfl`). The non-degeneracy lemmas therefore pin the constant; this is stronger than the region-hash control alone.

**Tier.** The ten lemmas are Tier A as non-degeneracy facts only. The paper says exactly this, and nowhere says a statement is proved.

**Fidelity (Tier C).** I compared the Lean definitions with manuscript §1 and with SS2012 Def. 1.1–1.2, (1.7), Conj. 1 and Thm 2 myself:
- the weak div/curl sign conventions;
- `+π log η Σχ(p)`, which has the correct sign: ½∫_{η<|x|<ρ}|x|⁻² = π log ρ − π log η;
- `ssTriLattice`, whose covolume is 2π/m;
- the quantifier order and the existential witness (equivalent through SS Prop. 3.1, which I read on p.26).

I found no misstatement. Stated deviations (rows 5, 6b and 9 of `STATEMENT_FIDELITY.md`) are disclosed.

**Nonblocking points.**
- `competitor_nonvacuous` is described as showing that "the conclusion W(E₀) ≤ W(E) constrains at least one competitor" (Lean docstring and paper §Lean). Every charge-free admissible field has W = +∞: by Gauss the flux of E through ∂K_r is −8πr², so ∫_{∂K_r}|E|² ≥ 8π²r³ and the local energy grows like R⁴. The only witness therefore satisfies the inequality trivially. The accurate gloss is "the competitor hypotheses are satisfiable" (see N3).
- The paper says rows 1–8 and 10 "match" while also listing three deviations. Two of those deviations sit in rows 5 and 6b, which are inside 1–8 (see N4).

## 2. Numbers trace to files; spot re-runs

**Certificate reproduction (Tier X).** I hashed the corpus sources myself:

| File | sha256 (prefix) |
|---|---|
| `certificate.cpp` | `53d46bba` |
| `core.hpp` | `c7f76596` |
| `grids.hpp` | `4640e0a3` |
| `run-certificate.py` | `cbef4f4c` |
| `certificate-record.txt` | `90e4f405` |

- All equal the paper's values. The positive run's `run.log` (`cf6cc0c6`) and executable (`ca7b5cae`) match the paper.
- I compared all **22** pairs in `run.log` with the record's saved rows (7 + 5 + 6 + 4): all equal. Table 1 matches.
- Receipts: positive run rc 0, terminal OK, stages passed, 490.35 s. S1-neg, A and B have rc −6/0/−6, the stated OMP_NUM_THREADS=2, and elapsed times of 683, 1009 and 874 s. The abort line is `grids.hpp:336` in both rejected runs.
- The negative-control patches are each one line, as stated.
- `predictions_AB.txt`: mtime 20:43:45 UTC, which is before A ended (20:58:40) and before B ended (20:56:24). "Predicted before they finished" holds.

**Dose-response.** Re-derived from the printed pairs: er0 ≈ (142 − 15)/23 = 5.52, eri ≈ 9.48, m* = (134 − 9.48)/5.52 ≈ 22.56, factor(×2) ≈ 20.5, and break-even of er_drop = 1 + 4585/5343 ≈ 1.858. These match the macros. The paper correctly labels them as fitted, not blind.

**My independent recomputation (`audit/audit_recompute.py`).** This is my own code, using the Dedekind-eta route rather than the producer's Ewald sum.

| Quantity | My value | Agrees with paper? |
|---|---|---|
| W(E_△) closed form | −4.150412807678963379 | yes |
| C_BHS | −0.0556053049433925185 | matches C from BS Thm 1.5 to 1.3e-51 |
| 6K + λ + 2πμ (exact Fractions from printed pairs) | [−4.1504214155, −4.1504042890], width 1.7127e-5 | same interval; contains W(E_△) |
| Square lattice (via η(i)/η(e^{iπ/3})) | −4.11716061233 | identical to the producer's Ewald value; outside the interval |
| SS-normalized triangular / square | −0.2010894476 / −0.1957971964 | matches SS Remark 1.5, p.5 |
| √(2π) transcription control | −5.9485503 | matches |

The paper's "Ewald vs closed form differ by 2.1382e-50" coincides with my compact-vs-expanded closed-form difference at 50 digits. The producer's Ewald value equals the compact form to all 50 digits, so the figure is the 50-digit rounding floor, not a defect.

**Other spot checks.**
- LeanFlow: I re-ran `pytest` in the worktree: **82 passed in 21.57 s** (includes the 4 pinned tests).
- I re-read `result_positive_run.json`: 13/13 accepted, axiom lists empty, no forbidden tokens in the rendered source. `result_negctl_run.json`: rejected; failed cert_5, cert_7 and cert_9 are the three gmin−factor assertions.

**Nonblocking.** `gen_inputs.py` truncates decimal strings instead of rounding them (N2).

## 3. Human proofs, step by step

There are no GAP rows to re-check: the producer's audit classified none. I re-derived a sample of CONFIRMED rows **against the manuscript text** (`build/sections/02-reduction.tex`, `03-geometry.tex`, `04-calibration.tex`).

**Section 2 rows.**
- **R3** (exact scaling): the puncture radius goes from η to √m·η, giving +(π/2) log m per charge, with no area factor. Correct.
- **R4–R7** (Lemma red:plane-bound): correct.
  - The exponent t^{2−r}(t² log t)^{r/2} = t²(log t)^{r/2} holds.
  - The coarea/Stokes/Hölder strip bound t^{1+1/r}(log t)^{1/2} = o(t²/log t), so n log n = o(t²).
  - Prop. 4.9 is applied with one g for both cutoffs, both supported in U = Q_{t+1}. The order 0 ≤ ζ_{Q_{t−L}} ≤ ξ_t holds because L > √m. ∫(ξ_t − ζ) dg ≥ −O(t).
  - The +∞ case is immediate, and the provisional −∞ case is excluded through M finite.
  - The limsup identity W(E) = m(limsup 𝖶(j′,ξ_t)/|Q_t| − ¼ log m) holds.
- **R10** (reduction): correct.
  - div E_k = m·curl j_k(√m·) = 2π(Σδ − 1) at m = 2π, and curl E_k = −m·div j_k = 0.
  - The torus side is √N_k, and the cell-energy shift is −(π/2)N log m.
  - E_T/N = m(W_ball − ¼ log m), and the N_k = 1 period doubling works.

**Section 3 rows.**
- **G2** (separation): correct.
  - φ satisfies −Δφ = 2π(δ − 1_B), φ(r*) = φ′(r*) = 0, φ > 0 inside, and the disk has area 1.
  - −ΔΨ ≥ 2π − 2π(n−1)/n on Ω, and |Ω| ≤ n − 1 < n.
  - The chain Φ(q) > Ψ(q) > min_∂D Ψ = min_∂D Φ ≥ Φ(q) holds. Injectivity radius √2/2 > 1/√π.
- **G3, G6, G7:** correct.
  - Euler's formula with multiplicities gives M₀ = 2E ≤ 6n, and d = |p − q|/2 ≥ r*/2.
  - In the signed-endpoint lemma, 0 < u < v and ∫_u^v G ≥ −∫max(0,−G).
  - Assembly uses M₀K ≥ 6NK since K ≤ 0, and the minimizer-to-all-configurations step is valid.

**Section 4 rows.**
- **K6 / K7:** correct. G(p,x₀) = (p/R₀²)(f(R₀) − e(R₀)/3) = 0 by the definition of μ, since x₀²/p² = 1/3. The six regular sectors each have area p·x₀ = 1/6 and **angle π/3**, so 6(K + λ/6 + μπ/3) = 6K + λ + 2πμ.
- **Paper slip (N1):** main.tex line 242 says "each regular sector has area 1/6 and angle π/6", and REDUCTION_AUDIT §5 item 1 says "area 1/6 = p·x₀/2 and angle π/6 = arctan(x₀/p)". Both mix the full sector (1/6, π/3) with the half sector (1/12, π/6). The manuscript (K7 proof) says π/3. The blindness-to-λ,μ conclusion is unaffected.
- **"39 retained modes"** (REDUCTION_AUDIT §1): consistent with the manuscript (§5: i = 0…38, index-zero term retained; the binary reports M = 38).

**Literature behind the rows.** I read SS2012 Lemma 4.7 (p.38) and its final display with 2W(j,χ) (p.39) on arXiv:1011.4617v2. The producer's remark is accurate.

**Is the zero-GAP verdict justified?** It is justified at the depth sampled. The audit's own CANNOT_ASSESS list remains the honest boundary:
- the spline pieces outside [p,R₀];
- the grid-stage values;
- runtime trust;
- the internal proofs of the cited results;
- no negative control reaching `inside_hess`.

## 4. Tiers and overclaim

- **Title, abstract, §1 and Limitations:** they say repeatedly that nothing is proved, verified or refuted, that the work is not peer review, and that the auditor is from the same pipeline.
- **Wording sweep:** no "proved", "verified" or "breakthrough" wording beyond the tiers. The only hits for "CONFIRMED" are the audit-label vocabulary, and the paper adds "CONFIRMED means the audit agent found no error, not that none exists".
- **Tier labels:**
  - The reproduction is filed at X even though it is exact-integer arithmetic. That is correct per the brief.
  - LeanFlow Tier A is scoped to arithmetic on the printed integers.
  - A failed `decide` is filed at X (main text).
  - The ledger row SSA-X-0006 says "Lean's decide proves 3 of them false". This is slightly stronger than the main text; align it (N8).
- **Exception:** Step 10 (B3).

## 5. Citations

**Read by me via alphaXiv on the cited pages:**

| Source | Item | Page |
|---|---|---|
| SS2012 (arXiv:1011.4617v2) | Def. 1.1, (1.3) | p.2 |
| SS2012 | (1.7), (1.8), Remark 7 / (1.9) | p.3 |
| SS2012 | Theorem 1(1)–(4), Theorem 2, Remark 1.5 (−0.2011, −0.1958), Conjecture 1 | pp.4–5 |
| SS2012 | Prop. 3.1 | p.26 |
| SS2012 | Corollary 4.4 (axis-aligned K_R periods) | p.35 |
| SS2012 | Lemma 4.7 | pp.38–39 |
| SS2012 | Prop. 4.9, (4.12) | p.41 |
| BS2018 (arXiv:1404.4485v5) | Thm 1.5 | p.3 |
| BS2018 | Def. 2.1, Remark 2.5, (2.4) | p.4 |
| BS2018 | §7.3 closed form, Thm 7.7 | pp.25–26 |
| BHS2012 (arXiv:1202.4037v1) | Conjecture 4 and the d = 2 value −0.05560530494339251850 | p.13 |
| BHS2012 | Ordered-pair energy (1) | p.1 |
| LRY (arXiv:1701.09064v3) | (3.53) | p.20 |
| LRY | Prop. 4.2 | p.21 |

All of these match the paper's and the ledger's pins. On LRY: there is no "Lemma 3" or "Appendix A" in the table of contents, so the producer's re-pin remark is correct.

**`citation_check.py` (not run by the producer).** I ran it (`audit/cite/`) on the four theorem-type load-bearing citations: SS Thm 1(3), SS Thm 1(4), SS Prop 4.9 (opening clause), and BS Thm 1.5 (equality clause).
- All four were ACCEPTED. A paraphrase negative control was REFUSED (`CITE_QUOTE_ABSENT`).
- **Strength:** this is only a verbatim spot check. The source `.txt` files are page-text excerpts that I copied from the alphaXiv extraction, so they are model-transcribed, which the tool's contract excludes. The Prop 4.9 quote covers a non-load-bearing fragment.
- Conjectures (SS Conj. 1, BHS Conj. 4) cannot pass by design (`KINDS` excludes them).
- Recommendation: save `pdftotext` output of the arXiv PDFs and run the tool on the full statements for the L rows (N5).

## 6. Data provenance

- `data/` holds byte-identical copies:
  - `run.log` hash checked;
  - the Lean files (hash-checked);
  - the patches;
  - receipts, predictions, scripts and outputs.
- My re-run of the Elenchus gate reproduces `ledger/gate_output.txt`: exit 1, 0 blocking findings, 7 flags, all `LEDGER_UNAUDITED_TIER_A`.
- Stale docstring: `calibration_check.py` still names the wrong √(2π) closed form, but its code uses the correct expanded form (N7).

## 7. `publication_meta.json`

- Accurate against the files: hashes, Mathlib rev, LeanFlow commit `542cea97…` on branch `feat/lean-data-certificates-2026-10-25` (verified with git), 82 tests, 13/13, 3/10, 22 pairs, the gate counts, and the base commit.
- It carries the same "fail-closed" wording that needs scoping (B2).
- `related_identifiers` cites the reserved DOIs 10.5281/zenodo.23646103…117. Publish those records first, or the links will not resolve (N9).

## Nonblocking items

| # | Item |
|---|---|
| N1 | "area 1/6 and angle π/6" → "area 1/6 and angle π/3" (main.tex l.242; REDUCTION_AUDIT §5 item 1). |
| N2 | `gen_inputs.py` truncates decimal strings instead of rounding: printed −6.75294 vs value −6.752949; −0.003974 vs −0.0039749; −6.76509 vs −6.765096; μ 0.413883384578 vs …5787; residual −1.0e-25 vs −1.034e-25. Round them. |
| N3 | `competitor_nonvacuous` gloss (Lean docstring and paper): the witness has W = +∞. Say "the competitor hypotheses are satisfiable", not that the inequality constrains a competitor. |
| N4 | Fidelity summary: say "exact in rows 1–4, 6a, 7, 8, 10; deviations in 5 (conditional), 6b, 9". |
| N5 | Run `citation_check.py` on `pdftotext` primary text for the L rows, and record the result in place of "not run". |
| N6 | For the uncited strict minimum principle, LRY's Prop. 4.2 proof (p.21) uses the same superharmonic-minimum argument and cites Lieb–Loss Ch. 9 (not checked by me). LRY Lemma 4.4 (p.22, minimal distance ≥ 1/√π) is the closest published analogue of G2. The LRY pin could be updated to Thm 3.2(4)(v)/(3.53), Prop. 4.2 and Lemma 4.4. |
| N7 | Fix the stale docstring in `calibration_check.py`. |
| N8 | Align SSA-X-0006 wording with the main text: a decide rejection is not a kernel-checked negation. |
| N9 | Publish the sibling DOIs before this record. |
| N10 | Coverage gaps the paper already discloses remain open: a planted Hessian-breaking control, the spline pieces, and the grid values. |

## Auditor artefacts (`/home/callensxavier_gmail_com/programmes-2026-10-25/P1/audit/`, sha256)

```
d899416e3ed4189b10342e346a50454c629d4fffea057fe8a48ea19bf17476ff  AuditMain.lean
b215f9fa96a270dddc824ca44615284570ab54ff124a4338edabe1b840035935  AuditExtra.lean
56875e5d7702341bf714a9a345478235f0d39097aa924f093d4c4cf0a185dcc4  AuditMutBg0.lean
3d431460934a9ddb9ce628c42941f01178cc4d266a18fa475441d5fb50967c65  run_lean_audit.sh
347d1365fe32fd9ac8aea9a84b2cbaad07005fa8ac63616ff6a7e8f0021c055d  compile_main.json
6fa8b4d1c2afadaf32e72bee3fdc34138f689193945e50a05fd340f34d578617  compile_controls.json
e1d9e72c9c8faac0d7b689cdbbed6bc9c67596f7f8138a3293513d4a21cdcff3  compile_extra.json
9bb5552b1ee6b03b57b543837bc165fa762c0f414d3113e8d617ad9c0323cd6e  compile_extra2.json
92670f00a27ed2626e8f5b68ef808489735ad4dd2093cde4055c60416974afe6  compile_mut.json
8f8b2c5b2ba50f0beabbfd33dc5edc3373e59bc5eb351f1e9203908aa62201b6  probe_exit_forge.py
b7031b1665bb0a4928344a1de938636b6800bb5e00649f8602d34814d1a543bb  probe_exit_forge.out.json
504630d3b1b7303222dc5cd3279a58516d147b506bc626862c8bd1e340a74221  probe_certify_inject.py
784065bc3bbce3a5784729cb030552339170621366ebd399f7c40b193aef8acc  probe_certify_inject.out.json
8e8651a28a7d9550d47b80c3beab882e0a8bb91b0d0d299dc8cf6a87229b2aff  audit_recompute.py
bcec61fb25335b41408557861bbb15129f00e3cc615de9e0339cedb1f0db097c  audit_recompute.out.json
5fa9a4e21fdda9397728e57e2f650fb0ac9149da422419c863b6fd0ee966e91a  leanflow_pytest_audit.txt
6ac472efbc75de103049e2ab6a8704184a64516626ad2825a6bc5ab1e2235051  gate_audit.txt
1eee65504a4354573073a7f570aa4767b05cad6bb54e93b63134eec7a2bb9712  cite/make_claims.py
b19c6d3b877abfd1de27b996f3af1b11bd2afdeb734238cff5d376735e1da727  cite/run_checks.py
85fda4fe99b29ff737e7c5cdfacb396b4eef6db4d92a4344e33603230a893d24  cite/cite_results.json
```

Note on one artefact: `audit_recompute.out.json` contains a key `neg_shift_dropped = −0.660559`. My formula for that key was wrong and the value is not used here. The producer's −1.26348 (= W + (π/2) log 2π) is the correct control.
