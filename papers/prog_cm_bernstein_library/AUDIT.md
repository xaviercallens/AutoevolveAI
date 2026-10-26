# Independent audit: P3 "Completely monotone and Bernstein functions in Lean 4" (prog_cm_bernstein_library)

- **Auditor.** An AI agent (Claude, Opus-family), separate from the producer and from the paper-stage agent. This is the
  producer≠verifier stage of the Elenchus protocol. It is **not** a human audit. It does **not** close the 20
  `LEDGER_UNAUDITED_TIER_A` flags: those ask a person to certify statement adequacy.
- **Date.** 2026-10-25.
- **What I audited.**
  - `papers/prog_cm_bernstein_library/`: `main.tex`, `main.pdf` (sha256 `491707cd…`, 13 pp.), `ledger/`,
    `publication_meta.json`, `data/`, `gen/`;
  - `results/programmes/2026-10-25/P3/`;
  - `formal_cert/Programmes/CompletelyMonotone/*.lean` (11 files);
  - rusty-SUNDIALS and LeanFlow, checked for any P3 change.
- **Write scope.** I edited nothing except this file. My scratch work is in `/home/callensxavier_gmail_com/programmes-2026-10-25/P3/audit/`:
  - drivers `audit_compile.py` (sha256 `a29cc566…`) and `audit_deep.py` (`a309b78e…`);
  - my Lean files `AuditAxioms.lean`, `AuditPlanted.lean`, `AuditClosure.lean`, `ListExtra.lean`;
  - `compare_logs.py`, `check_listings.py`, the `cite/` folder, the logs in `logs/` and `logs_deep/`, and the reruns.

## Verdict: ACCEPT_WITH_CORRECTIONS

- **The mathematics holds at the tiers it is given.**
  - All 11 Lean files rebuild from source under my own olean directory, with byte-identical compiler output.
  - Every one of the 167 constants in the library has an axiom set within the allowlist.
  - My own planted controls are caught.
  - The Tier X numbers reproduce byte for byte.
  - The four arXiv/Mathlib/policy sources say what the paper says they say.
- **Four corrections are required before publication (R1–R4).** None of them changes a mathematical result:
  - one is an Elenchus bookkeeping violation in the ledger (R1);
  - three are statements that are now false or mislabelled (R2–R4).

---

## 1. Lean: independent recompile, own axiom audit, own planted controls

**Method.**
- **Pass 1** (`audit_compile.py`). I rebuilt all 10 library modules in dependency order into my own olean directory, `audit/olean/`:
  - order: Basic → Bernstein, Laplace, Limits → Examples, Corollaries → NegativeControls, MathlibOnly → MathlibOnlyBridge → Applications;
  - then `Controls.lean` was compiled without writing an olean.
  - `LEAN_PATH` = the pinned stack, then mine, then the shared `formal_cert/.olean_out`. So every `Programmes.CompletelyMonotone.*` import resolves to an auditor-built olean.
- **Pass 2, deep** (`audit_deep.py`).
  - The shared `formal_cert/.olean_out` is **not** on `LEAN_PATH`; the script asserts this.
  - I first rebuilt from source the five repository prerequisites: `Triangular.Riesz`, `Triangular.RieszFinite`, `Autoresearch.Yukawa`, `Autoresearch.KeldyshCM`, `Autoresearch.DipolarExciton`.
  - Then I rebuilt all 11 P3 files and my audit files.
  - Only upstream openai/math (`OAI.*`) and Mathlib oleans came from the pinned `.lake`.
- **Toolchain.** Lean 4.34.1. Mathlib rev `d13f23b723b8a846827a245b89c10fc7d3f11612`, read from the pinned `lake-manifest.json`. Run with `taskset -c 4-7`.

**Results** (from `audit/logs_deep/*.json` and `audit/compare_logs.py`; pass 1 gives identical results).
- Every one of the 11 source files has a sha256 that appears in `gen/shas.tex` (the paper's §9). The sources have not drifted.

| module | rc | s (deep) | `#print axioms` lines | off allowlist | compiler output identical to producer log |
|---|---|---|---|---|---|
| Basic | 0 | 12.7 | 25 | 0 | yes |
| Bernstein | 0 | 12.9 | 16 | 0 | yes |
| Laplace | 0 | 12.3 | 4 | 0 | yes |
| Limits | 0 | 12.7 | 2 | 0 | yes |
| Examples | 0 | 12.2 | 6 | 0 | yes |
| Corollaries | 0 | 12.4 | 12 | 0 | yes |
| NegativeControls | 0 | 12.1 | 9 | 0 | yes |
| MathlibOnly | 0 | 7.0 | 36 | 0 | yes |
| MathlibOnlyBridge | 0 | 11.8 | 4 | 0 | yes |
| Applications | 0 | 12.6 | 16 | 0 | yes |
| Controls (planted) | 0 | 11.1 | 2 | 2 (expected) | yes |

- **Prerequisites (deep pass).**
  - All rc 0.
  - `Yukawa` printed 8 axiom lines, `KeldyshCM` 12 and `DipolarExciton` 4, all within the allowlist.
  - The only warning is a deprecation (`EuclideanSpace.single_apply`) in `RieszFinite.lean:27`.
- **My own axiom enumeration** (`AuditAxioms.lean`, run on both passes).
  - It iterates over every constant of every `Programmes.CompletelyMonotone.*` module and calls `Lean.collectAxioms`, which is transitive through Autoresearch, Triangular, OAI and Mathlib.
  - Output: `SUMMARY total_consts=167 theorems=150 user_theorems=135 offlist=0 axiom_decls=0`.
  - So no constant in the library (definitions, auxiliary lemmas and structure projections included) depends on `sorryAx` or on any axiom outside {propext, Classical.choice, Quot.sound}. No module declares an `axiom`.
- **130 vs 135.**
  - The paper's "130 theorems" counts `theorem`/`lemma` declarations in the source.
  - My 135 non-internal theorems are those 130 plus 5 auto-generated field projections of the Prop-valued structure `ProgCMCore.LaplaceData` (`k_meas`, `m_meas`, `k_nonneg`, `m_nonneg`, `integrable`), as printed by `ListExtra.lean`.
  - The two counts are consistent, and all 167 constants are covered.
- **Producer's planted controls** (`Controls.lean`, imported by nothing). They reproduce:
  - `ctl_sorry` → `[propext, sorryAx, Classical.choice, Quot.sound]`;
  - `ctl_axiom` → `[propext, Classical.choice, ProgCM.ctl_cheat, Quot.sound]`;
  - rc 0, with the warning "declaration uses `sorry`".
- **My own planted controls** (`AuditPlanted.lean`; the false statement "sin is CM", detected by the same `collectAxioms` code):
  - `planted_sorry` → OFFLIST `[sorryAx]`;
  - `planted_axiom` → OFFLIST `[AuditP3.planted_ax]`;
  - `planted_transitive` (uses the sorry'd lemma only through `comp_sqrt`) → OFFLIST `[sorryAx]`;
  - clean positive control `clean_ctl` (e^{-2√t} via `exp_neg_comp`) → CLEAN.
  - All were caught. The clean control passed, so the detector can say both yes and no.
- **Upstream dependency.**
  - `#print axioms ProgCM.triangular_optimal` gives the allowlist only.
  - So the upstream `universal_energy_minimum` that is used is a proved theorem, not a `sorry` stub.
- **Not verified by me.**
  - The openai/math commit `fd4aeeb…`: the pinned copy has no `.git`, and the id is inherited.
  - The oleans of upstream and Mathlib, which I did not rebuild.
  - The fidelity of upstream's `energy`/`latticeEnergy`/`DensityOne` definitions. The paper correctly marks everything downstream of them as conditional.
- **Statements read against the paper.**
  - `#check` of the bridge and of `sub_comp_add_const` matches Listings 1–2.
  - I read every Lean file in full. The definitions are:
    - `IsCompletelyMonotoneOn`: `ContDiffOn ℝ (⊤:ℕ∞)` on `Ioi 0`, plus sign conditions for every n at every t > 0;
    - `IsBernsteinOn`: C^∞, ≥ 0, and `deriv g` CM.
  - These are the definitions of Salazar Def. 2.1, restricted to (0, ∞) (Section 5).
  - The bridge to `AdmissiblePotential` is a kernel-checked iff, and the Mathlib-only bridge is `Iff.rfl`.
  - Upstream definitions used by the corollaries:
    - `AutoresearchDipolar.g d = 2(t^{-1/2} − (t+d²)^{-1/2})`;
    - `AutoresearchYukawa.g κ = e^{−κ√t}/√t`;
    - `TriangularRiesz.riesz s = t^{−s/2}`.
    - They match the paper's formulas.
- **Listings** (`check_listings.py`). I undid the LaTeX escapes and looked for each listing line in the sources.
  - 215 lines were checked. 189 occur verbatim.
  - 26 are statement lines whose proof was replaced by `:= -- proof elided` (25 lines), or that contain an escaped en-dash in a docstring (1 line). I inspected all 26 by eye: the statements are faithful.
  - 16 lines with unmapped escapes (Σ, ι, ∂, √, superscripts) were skipped.
  - `subord.lst`, which holds the main theorem, has no such lines and is fully verified.
- **Scope of the planted controls.** They are only in `Controls.lean`. `NegativeControls.lean` contains genuine refutations, not planted ones. `grep` finds no `sorry`/`admit`/`axiom`/`native_decide`/`implemented_by` in any library file.

## 2. Numbers trace to files; spot reruns

- **Tier X screen.** I re-ran `cm_numeric_check.py` (mpmath, 60 digits) myself. The output `audit/numeric_rerun.json` is **byte-identical** to `results/.../applications/numeric_check.json`. Table 3 matches it row by row:
  - controls: positive minima 1.06e-27 and 3.84e-62; negative controls −1.0000, −0.4180, −3.34e25 and −0.0048;
  - candidates: only the one-quadrupole field is negative, at −0.0443 (t = 3.16).
- **Proof-length measurement.**
  - I recompiled `Closure.lean` against my own oleans. Its 414 `CLOSURE` lines are identical to the producer's `closure_raw.json`.
  - I re-ran `proof_length.py`. `proof_length.json` and `proof_length_union.json` are byte-identical.
  - The numbers trace: 406/59 → 505/77 → 527/82 → 548/87. The increments 22 and 21 follow from these.
- **Figure numbers** (I recomputed them with numpy on the same grids as `gen_inputs.py`):
  - one-quadrupole minimum −0.04488 at t = 2.791;
  - t^{3/2}F at t = 10³: pair 0.00896, charge −0.99477, wrong weights −0.4951;
  - symbol minima −0.19055 at x = 0.7925 (charge) and −0.04426 at x = 0.9075 (wrong weights).
  - All agree with the macros (−0.0449, 2.79, 0.009, −0.995, −0.5, −0.1905/0.79, −0.0443/0.91).
- **Gate and ledger reruns.**
  - `gate.json` is the same file in `results/` and `data/`. The paper says it re-ran gate.py with identical output; I did not re-run it.
  - My re-run of `tools/ledger.py` reproduces `gate_output.txt` exactly: 0 blocking, 20 flags, rc 1.
- **Copies.** All 9 files under `data/` are byte-identical to their originals in `results/programmes/2026-10-25/P3/`.
- **Hard-coded number.** "872.6 s" (the first cold `Basic` compile) traces only to `LIBRARY.md:253`. Its log was overwritten by the final rebuild. It is an infrastructure remark and supports no claim (non-blocking N9).

## 3. Human proofs, step by step

- **Step 2 (Leibniz).** (uv)^{(n)} = Σ C(n,i) u^{(i)} v^{(n−i)}, and (−1)^n = (−1)^i(−1)^{n−i}, so every term is ≥ 0. Correct.
- **Step 3.**
  - h_n′ = −h_{n+1} ≤ 0, so h_n is antitone.
  - (−f′)^{(n)} carries the sign (−1)^n·(−f^{(n+1)}) = h_{n+1}.
  - The translates have derivatives f^{(n)}(t+c).
  - The difference gives h_n(t) − h_n(t+c) ≥ 0.
  - All correct.
- **Step 4.** d^n t^{−s} = (−s)(−s−1)…(−s−n+1) t^{−s−n}, so h_n = s(s+1)…(s+n−1) t^{−s−n} ≥ 0. Correct.
- **Step 5 (subordination).**
  - I checked (−1)^{n+1}(f∘ψ)^{(n+1)} = (−1)^{n+1}·(−[(F∘ψ)ψ′]^{(n)}) = (−1)^n[(F∘ψ)ψ′]^{(n)}, with F = −f′ CM.
  - The induction hypothesis P(n), applied to F, gives the signs of u = F∘ψ up to order n. The function v = ψ′ is CM.
  - Leibniz closes the step. Quantifying over all CM f is what makes the induction go through.
  - The proof is correct. The Lean `comp_sign` follows it line for line, with `EqOn` used on the open half-line for the derivative identity.
- **Step 6.** (f∘g)′ = (f′∘g)·g′, and f(g(t)) ≥ 0 needs g > 0. Correct.
- **Step 7.**
  - e^{x} ≥ x^n/n! at x = (c/2)u gives u^n ≤ n!(c/2)^{−n} e^{(c/2)u}.
  - Hence k^n e^{−ck} m ≤ n!(c/2)^{−n} e^{−(c/2)k} m. This is integrable, and it dominates the n-th t-derivative for t ≥ c.
  - Correct, and it matches `integrable_pow_mul`.
- **Step 8.** The uniform-convergence-of-derivatives argument is correct. Smoothness of the limit is indeed derived, by induction in `hcont`.
- **Quadrupole (a).**
  - 1/√3 − 2/√4 + 1/√7 = −0.044685 < 0.
  - The bounds √3 > 1.7 and √7 > 2.6 give 10/17 + 10/26 = 0.9729 < 1.
  - Scaling: quadrupoleC(c, cs) = c^{−1/2} · quadrupole(s). Correct.
  - Far field: the shifts 0, c, 4c with weights 1, −2, 1 have first moment 2c, so F ≈ 2c f′(t) = −c t^{−3/2}, i.e. −d²/r³. With c = 1 this gives t^{3/2}F → −1. Correct.
  - Wrong weights 2, −3, 1: first moment 1, so the limit is −1/2. Correct.
  - *Nit:* the paper writes "≈ −0.0446". The value −0.044685 rounds to −0.0447 (N8).
- **Quadrupole (b), pair counting.**
  - Δz = 0: 1+4+1 = 6. |Δz| = d: four ordered pairs with charges 1·(−2), total −8. |Δz| = 2d: two ordered pairs, total 2.
  - So the combination is 6f(t) − 8f(t+c) + 2f(t+4c). Correct.
  - I expanded Δ_c g + Δ_{2c} g + Δ_{3c} g by hand: it gives 3f(t) − 4f(t+c) + f(t+4c). Correct, and Lean checks it by `ring_nf`.
  - Factorisation: (1−x)²(x²+2x+3) = x⁴ − 4x + 3. Correct.
  - Minimum of 1 − 2x + x⁴: at x = 2^{−1/3} = 0.794 the value is −0.1905. Correct.
- **CM-C-0004.** ∫₀^∞ e^{−κ} e^{−κr}/r dκ = 1/(r(1+r)). Correct.
- **Box spectrum (Tier X screen).** ∫₀² e^{−κr}/r dκ = (1 − e^{−2r})/r². Correct.
- **Symbol caption.** ∫₀^∞ e^{−ut} u^{−1/2} du = √π · t^{−1/2}. Correct.

## 4. Tiers and overclaim

- **Tier A tags.** They attach to Lean statements, and the conditional rows (A-0001, A-0012, A-0018) say "CONDITIONAL". I found no "breakthrough" or "novel" claim; the paper explicitly disclaims novelty.
- **"Proved" wording.** It appears only for Tier A statements or for things explicitly marked as not proved. That is acceptable.
- **R1 below (blocking): the tier of CM-C-0007.** It is a tiering defect.
- **R4 below (blocking): Figure 1 is mislabelled.** It says "Tier C" but is filed as X.
- **Overstatement.** "Negative controls show that each hypothesis is needed" (abstract, meta) says more than the file shows. The file shows this for the Bernstein-ness of the inner function, for ψ > 0, for nonnegative weights, and for the distinctness of the two classes. It does not show it for the integrability or measurability hypotheses of `laplace`, or for c ≥ 0 in translation. Say "each of the listed hypotheses" (N3).

## 5. Citations

alphaXiv full-text reads, done by me on 2026-10-25:
- **Petrache–Serfaty, arXiv:1908.09714v3, p. 1.**
  - Conjecture 1 is stated verbatim as quoted.
  - The page says the conjecture was "recently proved in dimensions 8 and 24 — it remains open in dimension 2".
  - It defines p as a CM function of squared distance. Faithful.
- **Cohn–Kumar, arXiv:math/0607446v2 = JAMS 20(1) (2007) 99–148, p. 101.**
  - The definition of completely monotonic cites [Wid, p. 145].
  - The squared-distance paragraph, including "but not vice versa", is verbatim. Faithful.
- **Salazar, arXiv:2607.04467v1.**
  - Def. 2.1 (p. 4) gives CM and BF on (0, ∞) with values in [0, ∞).
  - Thm 2.3 (p. 5) is Bernstein–Widder as quoted.
  - The p. 2 introduction names "Bochner subordination for their composition" and does not number the theorem. Faithful.
- **`tools/citation_check.py`.** Only one L item is a theorem statement: Salazar's Theorem 2.3.
  - I saved the extracted p. 5 text as `audit/cite/salazar_p5.txt` and ran the gate:
    - the faithful quote is **ACCEPTED** (rc 0);
    - a tampered control (positive Radon measure replaced by "positive finite measure") is **REFUSED**, `CITE_QUOTE_ABSENT` (rc 1).
  - The other L rows are outside the gate's scope:
    - L-0001 is Mathlib source;
    - L-0002 is a definition;
    - L-0003 is conjecture prose;
    - L-0005 is a policy page.
  - The producer's `sources/excerpts.json` says this too. Elenchus defines L as a quoted theorem statement, so these rows are L by convention only (N5).
- **Mathlib `AbsolutelyMonotone.lean` at the pin.** Line 57 is the definition, as quoted. The author is M. R. Douglas (2025). It cites Widder 1941.
  - It has **6** theorems: `contDiffOn`, `of_contDiff`, `iteratedDerivWithin_nonneg` (line 80), `iff_iteratedDerivWithin_nonneg`, `add`, `smul`.
  - The paper's "proves only contDiffOn, of_contDiff, iff_…, add and smul" leaves out `iteratedDerivWithin_nonneg`. The list is the module docstring's, not the file's contents (N1).
  - Mathlib contains no `CompletelyMonotone` or Bernstein-function definition (I grepped).
  - `AbsolutelyMonotoneOn` is the sign-free mirror notion: f^{(n)} ≥ 0. Calling it "a different formalisation of the same idea" is loose. CM on (0, ∞) corresponds to absolute monotonicity of x ↦ f(−x) on (−∞, 0) (N2).
- **Lean community "How to contribute", read with WebFetch.** All three quoted sentences are present verbatim, and the page dates the policy to mid-2026. Faithful.
- **Zenodo** (I queried the API for every DOI in `related_identifiers`):
  - 23293429, 23295142 and 23285631 are published, with the cited titles;
  - **23646103, 23646105, 23646107, 23646111 and 23646117 are all published (2026-10-25)**. See R2.
- **Small citation issues.**
  - Salazar's initials are "D. S. P. Salazar" (N6).
  - The bibitem says Salazar is "used only for the definitions … and Thm 2.3", but the paper also cites its p. 2 for the name "Bochner subordination" (N6).
  - The bibitems `widder`, `mlam`, `d2`, `uot` and `txt` are never `\cite`d in the text (N7).

## 6. Data provenance

- **No external data.** All inputs are Lean sources, compile logs and code-generated numerics.
- **Base commit.** `git rev-parse HEAD` = `9d245742c1655852103abb28f585e21af54851e6`, as stated. The P3 files are untracked, as disclosed.
- **rusty-SUNDIALS and LeanFlow.** There is no P3 branch or worktree. Branches exist for ar-h1/h2/h3/h7/h8, p2, p5 and p7 only, and LeanFlow has only `LeanFlow-wt-p1`. So "no change in this lane" is accurate.
  - The user asked to improve rusty-SUNDIALS or LeanFlow "along the way". Whether a lane with no such improvement is acceptable is a scope decision for the parent session, not a defect of the paper (N10).
- **Measurement scope (N4).**
  - `proof_length.py`'s docstring calls `Triangular.*` "upstream openai/math". It is repository code (D1, e.g. `TriangularRiesz.riesz_admissible`); upstream is `OAI.*`.
  - The closure keeps only `Programmes.*` and `Autoresearch.*`, so repository `Triangular.*` lines are excluded on both sides. The paper's "transitive closure of repository declarations (Mathlib and upstream excluded)" should say this.
  - Overlapping structure/field ranges (e.g. `MixtureData` 30–36 and its fields 31–36) are double-counted on both sides.
  - Neither issue changes the direction of the conclusion: the closure is not shorter end to end.
- **`elenchus_check.py` could not run (no result).**
  - On the Lean files it used its default `v4.34.0-rc2` toolchain without the project search path, giving COMPILE_ERROR "unknown module prefix".
  - It skipped the four `.py` files because they declare no `CONTROL_INPUTS`.
  - This is "tool could not run", not a pass and not a fail. The Lean evidence above comes from my own pinned-stack recompiles.

## 7. publication_meta.json

- Title, version, keywords, sha256 values, toolchain, base commit and the counts (130 theorems, 10 modules, 0 blocking, 20 flags) are accurate.
- Inaccurate items:
  - the audit status (R3);
  - the "may not be published records" note on the sibling DOIs (R2);
  - "a different formalisation of the same idea" (N2);
  - "each hypothesis is needed" (N3).
- The "0 blocking findings" is true only after the edge deletion described in R1.
- 23295142, 23285631 and 23293429 are listed as "references" but are not cited in the text (N7).

---

## Required corrections (blocking)

- **R1: CM-C-0007's hidden dependency (Elenchus ledger integrity).**
  - CM-C-0007's statement is, in its own words, a "Reading of the proof-length measurement (CM-X-0002)". It restates the X numbers 23→3, 8→2, 406(59)→505(77), +22 and +21.
  - Yet `depends_on` is `[]`. The paper (§7) says the first gate run found a blocking tier inversion, "repaired by removing the dependency".
  - I restored the edge in a copy (`audit/ledger_c0007_restored.json`). The gate then reports `block LEDGER_TIER_INVERSION CM-C-0007: tier C exceeds effective tier X of its ancestor CM-X-0002` (`audit/ledger_c0007_restored_gate.txt`).
  - Deleting a true provenance edge makes the gate pass without fixing the inversion.
  - **Fix:** refile CM-C-0007 as Tier X (or merge it into CM-X-0002), restore the edge, and re-run the gate. Then replace the §7 sentence with an accurate description.
  - The structural cause, that `Basic.exp_neg_mul` routes through `AutoresearchKeldysh.laplace_admissible`, can be read from the source (`KeldyshCM.lean:160-168`). I confirmed it in my closure output. It may stay as a C observation if it does not cite the X numbers.
  - "We do not claim shorter proofs" is a non-claim and can stay.
- **R2: sibling DOIs are now published.**
  - Zenodo reports all of 10.5281/zenodo.23646103, 23646105, 23646107, 23646111 and 23646117 as **published** on 2026-10-25.
  - Remove the bibitem phrases "DOI reserved at the time of writing" and "DOI reserved" in `dip`, `yuk`, `kel`, `sig` and `bog`.
  - Remove the meta `notes` sentence "reserved … and may not be published records at the time of reading".
- **R3: audit-status language is out of date.**
  - These statements are now false or incomplete:
    - the disclosure: "No independent AI audit … producer≠verifier is still owed";
    - §4: "it is not producer≠verifier";
    - Limitations: "Producer-only. No independent AI audit";
    - meta: "There has been NO independent AI audit"; "Producer-only: no independent audit".
  - Replace them with a description of this audit:
    - an independent AI audit rebuilt all 11 files and the 5 repository prerequisites from source, with the producer olean directory asserted off `LEAN_PATH`;
    - it enumerated `collectAxioms` over all 167 constants (0 off the allowlist);
    - its own planted sorry, axiom and transitive-sorry controls were all caught, and a clean control passed.
  - Keep, and say explicitly, that there is **no human audit**, that the 20 `LEDGER_UNAUDITED_TIER_A` flags remain open, and that an AI audit does not close them.
- **R4: Figure 1 caption tier.**
  - The `fig_symbols` caption says "Tier C illustration". The ledger files the figure as **CM-X-0004 (Tier X)**.
  - The plotted minima (−0.1905 at 0.79, −0.0443 at 0.91) are floating-point grid values.
  - Change the caption to Tier X. The factorisation itself is already C, under CM-C-0002.

## Non-blocking notes

- **N1.** Mathlib `AbsolutelyMonotone.lean` proves 6 theorems. `iteratedDerivWithin_nonneg` (line 80) is missing from the list in §2 and in CM-L-0001.
- **N2.** `AbsolutelyMonotoneOn` is the mirror notion (f^{(n)} ≥ 0), not "the same idea". Say so, and say how CM corresponds to it under x ↦ −x.
- **N3.** Change "each hypothesis is needed" to "each of the listed hypotheses is needed". The controls do not cover the integrability or measurability hypotheses of `laplace`, or c ≥ 0.
- **N4.** In the proof-length method, say that repository `Triangular.*` is excluded, and fix "upstream" in the `proof_length.py` docstring. Mention that overlapping structure/field ranges are double-counted on both sides.
- **N5.** L-0001/0002/0003/0005 are definitions, prose or policy, not theorem statements. citation_check only applies to Salazar Thm 2.3, which I accepted with a tampered control refused. Say in §7 that these rows are L by convention and were not run through `citation_check.py`.
- **N6.** Write "D. S. P. Salazar". The bibitem's "used only for …" should also mention the p. 2 "Bochner subordination" naming.
- **N7.** The bibitems `widder`, `mlam`, `d2`, `uot` and `txt` (and the related identifiers 23285631, 23293429 and 23295142) are never cited in the text. Cite them where relevant or drop them.
- **N8.** "1/√3 − 1 + 1/√7 ≈ −0.0446": the value −0.044685 rounds to −0.0447.
- **N9.** The 872.6 s cold-compile figure traces only to `LIBRARY.md`, because its log was overwritten. Mark it as an infrastructure anecdote, or drop it.
- **N10.** Add an explicit preregistration-vs-outcome line:
  - core closure (prior 0.8): done;
  - composition with Bernstein (prior 0.5): done;
  - Fourier criterion (prior 0.3): not attempted;
  - Stieltjes mixtures: not done;
  - "Mathlib-PR-ready branch": **not met**, as the paper says;
  - the "two budgets per lemma" kill rule: not reported.
  - The rusty-SUNDIALS/LeanFlow non-contribution is accurately disclosed. Whether it is acceptable is the parent session's scope call.
- **N11.** `laplace_measure`'s hypothesis is that ∫e^{−cx}dμ is finite for every c > 0. "finite exponential moments" (§3, Step 7) usually means ∫e^{cx} < ∞, so say "finite Laplace transform for every c > 0".
- **N12.** "field of one quadrupole on a test charge" means a potential energy, not a field. Consider "potential".
- **N13.** `elenchus_check.py` could not examine the Lean files (wrong toolchain and search path) and skipped the `.py` files (no `CONTROL_INPUTS`). It gave no verdict either way.
