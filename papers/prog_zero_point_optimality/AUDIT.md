# AUDIT — P2 `prog_zero_point_optimality` (programmes 2026-10-25)

Auditor: a separate AI agent (Claude), stage AUDIT. I wrote none of the paper, the Lean module, the Rust code or the
analysis, so producer != verifier holds at the agent level. No human has audited this work. This file is the only
thing I edited. My scripts and outputs are in `/home/callensxavier_gmail_com/programmes-2026-10-25/P2/audit/`:

| file | purpose |
|---|---|
| `AuditBasic.lean`, `audit_basic.json` | Lean copy with auditor additions |
| `audit_basic_orig.json`, `audit_controls.json` | recompiles of the original files |
| `audit_realspace.py`, `audit_realspace.json` | independent fifth implementation |
| `audit_map.py` | recount of the map statistics |
| `audit_handnums.py` | traces of hand-typed numbers |
| `human_check_copy.py` | rerun of the paper's Step 9 listing |
| `genrun/` | sandboxed rerun of `gen_inputs.py` |
| `run_cargo.py`, `cargo_{test,fmt,clippy}.txt` | crate checks |
| `audit_elenchus_and_g05.py`, `audit_elenchus_g05.json` | seed-detector run and the independent gauss:0.5 refutation |

## Verdict: ACCEPT_WITH_CORRECTIONS (no blocking findings)

The counterexample to QU-1 holds up:
- My fifth, real-space numpy code shares no code with the producer. It reproduces E_zp at both shapes to about
  1e-12 and confirms the triangular, rhombic and square stability signs.
- E_zp at τ and at −1/τ is identical.
- The sign of c at a = 1 and a = 2 agrees with the paper.

The rest also checks out:
- The Lean module recompiles inside the axiom whitelist, and my own planted `sorry` and axiom are caught.
- Every generated macro and table reproduces bit for bit from `data/`.
- All three citations are real, and the quotations match the arXiv PDFs.
- The crate's tests, fmt and clippy pass.
- The hand derivations are correct.

Five wording and consistency corrections (C1–C5) should be made before Zenodo publication. None changes a result.

**Audit scope.** This says what the audit did and did not check independently.

Recomputed by the auditor's own code:
- gauss:1 E_zp at ρ and at 0.5+0.966025i, and at −1/τ
- grid stability of the triangular, headline and square lattices
- the sign and size of c at a = 1 and a = 2
- the gauss:0.5 refutation at its tab:pot competitor (0.5, 1.016): ΔE = −1.4583e−2 against the paper's
  −1.459e−2. Both lattices are stable on a Γ-centred 400² grid (min λ/|k|² of 0.0118 and 0.0014).
- the gauss:1 map recount
- all generated macros and tables, by rerunning the producer's generator on the producer's data

Checked only by rerunning the producer's tests or reading the producer's data:
- the dipolar, Riesz and Yukawa refutations, which rest entirely on the producer's real-space code
- the exact long-wave elastic tensor
- the Lin/Conc decomposition
- Result 5 (E_static + ΛE_zp)
- the c(a) scan beyond its sign at a = 1 and 2
- `phonon.rs` (691 lines), covered only by its tests, fmt and clippy

**Integrity.** `find -newer` against the auditor's first file lists only `AUDIT.md`. This covers the paper
directory, `formal_cert/Programmes/ZeroPoint`, `formal_cert/.olean_out` and `results/programmes/2026-10-25/P2`. The
rusty worktree's `git status` is clean.

---

## 1. Lean: independent recompile, own `#print axioms`, own planted controls

The sha256 of the files on disk match the paper and publication_meta.json:
- `Basic.lean`: `7d59f181…0d64f0`
- `Controls.lean`: `c725bdcb…acd90`

The Mathlib revision in the pinned `lake-manifest.json` is `d13f23b723b8…`, which matches the paper's `d13f23b7`.

| run (pinned Lean 4.34.1 via `lean_pinned.py`, cores 4–7) | rc | s | result |
|---|---|---|---|
| original `Basic.lean` (no `--olean`, so the shared olean was not touched) | 0 | 7.3 | 19/19 printed declarations `[propext, Classical.choice, Quot.sound]` |
| original `Controls.lean` | 0 | 5.3 | `ctl_sorry`: `sorryAx`; `ctl_axiom`: `ProgZeroPoint.ctl_cheat`; `lap_wrong_false`: whitelist |
| auditor copy `AuditBasic.lean` | 0 | 7.3 | all 19 plus `rho_ne_zero` whitelisted; auditor plants caught (see below) |

What I added in the auditor copy:
- **A planted `sorry`.** `audit_planted_sorry` "proves" `y²(Qxx+Qyy) = 3Q`. It compiles with rc 0, and
  `#print axioms` shows `sorryAx`.
- **A planted axiom.** `audit_cheat : ∀ p, p` is used to prove `1 = 2`. It compiles with rc 0, and
  `AuditZP.audit_cheat` is exposed.
- **Statement-adequacy checks** (whitelisted):
  - `audit_deriv_Qx` shows that the stated `Q_x` is Mathlib's `deriv`.
  - `audit_deriv2_Qx` shows that `deriv (deriv Q) = 2n²/y`, so the explicit second-derivative expressions used in
    `lap_Q` are the real second derivatives.
  - `audit_inversion_nonvacuous` shows that the hypothesis of `deriv_at_one_of_inversion` is satisfiable
    (f(α) = α^(−1/2)).

Conclusion: the exit code is not the gate; the axiom list is. `grep -c sorry Basic.lean` gives 0, and
`Basic.lean` contains no `axiom`, `admit`, `native_decide`, `implemented_by` or `extern`.

Statement adequacy, by eye:
- **Q and its derivatives.** I re-derived the four partials of Q, `lap_Q` and `grad_Q`. With u = m+nx,
  y²(4n²u²/y² + (n² − u²/y²)²) = (n²y + u²/y)² = Q².
- **`gauss_h`, `m2_f'`, `m2_h`.** I re-derived these by hand, collecting
  2u·(8π²a² − 4π³a³u) − 4π³a³u² − πa·u²·(8π²a² − 4π³a³u) = 16π²a²u − 20π³a³u² + 4π⁴a⁴u³.
- **`rot120_comm_symm`.** The hypotheses `h11` and `h12` are exactly the (1,1) and (1,2) entries of RH = HR for
  R = [[−1/2, −s], [s, −1/2]].
- **`rot120_fixed_vec`.** This is Rg = g. Because `s² = 3/4` admits both signs, the lemma covers the ±120°
  rotations.
- **Rho lemmas.** `rho_sq`, `gamma_fixes_rho`, `rho_sq_mul_rot` and `hasDerivAt_gamma` are correct. (1 −1; 1 0) has
  determinant 1, and γ'(ρ) = ρ⁻² = e^{−2πi/3}.
- **Scope.** `lap_comp` is pure algebra, and the paper says so (Tier C for the chain rule). The paper does not
  overstate what Tier A covers.

I ran the Elenchus seed detector myself (`audit_elenchus_g05.json`) on both original files and on `AuditBasic.lean`,
with the pinned LEAN_PATH. It skipped all three with rc 2 ("toolchain mismatch: lean-toolchain pins 4.34.0-rc2, lean
reports 4.34.1"). This reproduces the paper's disclosure. The auditor's planted controls above stand in for it.

## 2. Numbers trace to result files; independent re-runs

- **Generated numbers.** I copied `gen_inputs.py` to `audit/genrun/`, with `data/` and `ledger/` symlinked
  read-only and only the Lean path fixed. It runs with rc 0 and emits 163 macros. `gen_numbers.tex` and all of
  `gen/*` are **identical** to the paper's. So every `\ZP…` macro and every generated table is a deterministic
  function of `data/`.
- **Data copies.** The `data/` copies are byte-identical to `results/programmes/2026-10-25/P2/{,g2/}` (14 files
  compared with `cmp`). `controls.json` and `edge_check.json` are also identical to the rusty branch's
  `results/phonon_gate/`.
- **Headline in the data.** In `poisson_check.json`, Duffy N=128 gives 1.5033523522073637 for the triangular
  lattice and 1.4902783182796493 for the rhombic one. The uniform-grid Richardson values agree to about 1e-14.
- **Step 9 listing.** I re-ran `human_check.py` (copy) and reproduced `data/human_check.json` exactly: Richardson
  values 1.503352352205 and 1.490278318273, so ΔE = −1.30740e−2.
- **Fifth implementation (`audit_realspace.py`).** It sums D(k) in real space directly (no folding, no Poisson) on a
  half-shifted grid and extrapolates n = 160, 320 with Richardson:

  | quantity | auditor | paper |
  |---|---|---|
  | E_zp(ρ), a = 1 | 1.5033523522067 | 1.5033523522 |
  | E_zp(0.5+0.966025i) | 1.4902783182775 | 1.4902783183 |
  | ΔE | −1.30740e−2 | −1.3074e−2 |
  | E_zp at −1/τ = −0.4226+0.8164i | 1.4902783182775 (modular invariance) | — |
  | min λ/\|k\|² on a Γ-centred 400² grid: tri / head / square | 0.03239 / 0.03510 / −0.1475 | 0.03222 / 0.03493 / −0.1475 |
  | c estimate at r = 0.02, a = 1 (θ = 0, π/2) | −0.962, −0.963 | c(1) = −0.962 |
  | c estimate at r = 0.02, a = 2 | 0.47–0.49 | c(2) = +0.495 |

  The auditor's stability values are grid values, so they bound the zone minimum from above, consistent with the
  paper's Nelder–Mead minimum. The 45° directions give −0.932, which is the O(r³) term at r = 0.02 and is
  consistent with an isotropic Hessian.
- **Map statistics (`audit_map.py`).** The gauss:1 n=96 recount gives 625 shapes, 65 stable and 64/64
  competitors lower, with weakest margin −1.26e−4. All of these match the paper.
- **Hand-typed numbers in `main.tex`** (`audit_handnums.py`):

  | claim in main.tex | value in the data | source |
  |---|---|---|
  | stencil vs exact lattice sum ≤ 2.5e−10 for a ≥ 0.5 | max 2.42e−10 | `mechanism.json` |
  | ∂xx = ∂yy to 1e−6 | 1.33e−6 relative | `mechanism.json` |
  | ∂xy ≈ 1e−9 | 1.7e−10 at a = 1 (1.8e−9 at a = 0.5) | `mechanism.json` |
  | "3600 directions" | `linspace(0, π, 3600)` | `phonon_elastic_check.py` |
  | shear ≤ 1.5e−9 for a ≤ 0.123 | 1.44e−9 | `smalla_check.json` |
  | shear 3.3e−12 at a = 0.1 | 3.28e−12 | `smalla_check.json` |
  | roots | 0.12269, 0.37668, 1.58148, 1.09361 | `mechanism.json` |
  | MaxStableDist "0.23" (hard-coded) | 0.2274, the max over 12 potentials (gauss:0.25) | rusty scan CSVs |

- **Crate checks (`run_cargo.py`, cores 4,5).**
  - `cargo test --release -p qf-yukawa-crystal`: 59 passed, 0 failed, 1 ignored.
  - `cargo fmt --all --check`: exit 0.
  - `cargo clippy --workspace --features experimental -- -D warnings`: exit 0.
  - `git status --short` in the rusty worktree is empty afterwards, so the runs touched no files.
  - The commit hashes in the paper (`a961a714…`, `5f2f73b8…`, `6ad3cf7e…`) match `git rev-parse`.
  - There are 12 `#[test]` in `phonon.rs` and 5 in `phonon_spectral.rs`, as stated.

## 3. Human proofs, re-derived step by step

- **Step 3, chain rule.** Δf(Q) = y²[f''·|∇Q|² + f'·ΔQ] = Q²f'' + 2Qf' = (u²f')'(Q). This is correct and is tagged C
  where it is not formalised.
- **Step 6.** For orthogonal J, JᵀHJ = H is equivalent to HJ = JH, which is what the Lean hypotheses encode. If
  H = κI, then E − E(ρ) ≈ ½κ|τ−ρ|². With ΔE = y²·2κ this gives c|τ−ρ|²/y² with c = ΔE/4. Correct.
- **Step 7, the sum rule.** I re-derived it:
  - ⟨1 − cos k·R⟩_BZ = 1 for R ≠ 0, so ⟨tr D⟩ = Σ_{R≠0} ΔV(R).
  - ΔV(0) = m₂(0) = −4πa, so Σ_{R≠0} = Σ_R ΔV(R) + 4πa.
  - Poisson summation for the unit covolume, with V̂(ξ) = a⁻¹e^{−π|ξ|²/a} and the factor −4π²|ξ|², gives
    −(4π²/a)S(1/a; L*). L* is a rotation of L.
  - So ⟨tr D⟩ = 4πa − (4π²/a)S(1/a). Correct.
  - (i) Luo–Wei Cor. 1.1 applies with α = 1/a ≥ 1, that is a ≤ 1, and minimising S maximises ⟨tr D⟩. Correct.
  - (ii) θ(1/α) = αθ(α), from Poisson and L* ≅ L. The inversion lemma gives θ'(1) = −θ(1)/2, and S = −θ'/π, so
    S(1) = θ(1)/2π. This is the same as Luo–Wei Lemma 3.5, W_{1/2π}(1; z) = 0, which I checked in the PDF. So
    ⟨tr D⟩ = 4π − 2πθ(1). Correct.
- **Step 8, Einstein bound.** ½(ω₁+ω₂) ≤ √((ω₁²+ω₂²)/2), followed by Jensen (concave √), gives
  E_zp ≤ √(⟨tr D⟩/2). Correct.
- **Step 8, concavity.** The second derivative of tr f(D(τ)) splits into a linear part Φ'(D)[∂²D] and a quadratic
  part Φ''[∂D, ∂D] ≤ 0 for concave f. This is standard. The table checks: Lin + Conc = −0.799 − 3.048 = −3.847
  against −3.848, and Conc_diag + Conc_cross = −3.048.
- **Bernstein remark.** The Bernstein-mixture argument is linear in V and E_zp is not. Correct.
- **Duffy rule** (Rust, read-only). The Jacobian of (s,t) → (s/2, s(t − 1/2)) is s/2, and the four triangles have
  total weight 1. The integrand √(tr D + 2√det D) is smooth away from Γ for a stable lattice.

## 4. Tiers and overclaim

The tiering is careful overall:
- Everything about E_zp is X or C.
- Tier A is limited to the algebraic statements, and the paper says what Tier A does not certify.
- The ledger gate is reproduced: 0 blocking, 8 `LEDGER_UNAUDITED_TIER_A` flags, exit 1. Ledger counts are
  A 8 / L 3 / C 13 / X 12, total 36.
- Post-hoc analysis and deviations from the preregistration are disclosed. The preregistration asked for G1 "over
  the fundamental domain" with a non-CM negative control, and both were done.
- The marginal 0.295+0.9555i point is corrected openly.

The exceptions are corrections C1, C2, C4 and C5 below.

## 5. Citations

I checked these against the arXiv PDFs through alphaXiv, and I re-ran `citation_check.py` on all three claim JSONs:
each returned ACCEPTED (rc 0) with tier ceiling L. The source-text sha256 match the claims.

- **arXiv:2302.05042v1, Luo & Wei, "On lattice hexagonal crystallization for non-monotone potentials".**
  - Cor. 1.1 on p. 3: for α ≥ 1, min Σ|P|²e^{−πα|P|²} is attained at the hexagonal lattice. Verified.
  - Lemma 3.5 on p. 12: W_{1/2π}(1; z) = 0. Verified.
  - Bétermin's assertion that (1.6) cannot hold for all α > 0: Luo–Wei pp. 2–3. Verified.
- **arXiv:2411.17199v1, Deng & Luo, "Minimizing lattice energy and hexagonal crystallization".** Theorem A
  (Montgomery 1988) on p. 3, with reference [28] = Glasgow Math. J. 30 (1988) 75–85. Verified.
- **Bétermin.** SIAM J. Math. Anal. 48(5) (2016), with first page 3236. Verified second-hand, as the paper says.
- **Zenodo DOIs.** The five ar_* DOIs and the textbook DOI are the user's own records (not re-resolved here).

## 6. Data provenance

- The scan CSVs, the G1 JSONs and the gate files are committed in the rusty branch (not pushed).
- The G2 JSONs (`poisson_check`, `mechanism`, `elastic_check`, `smalla_check`, `sumrule_identity`) exist only as
  uncommitted files in AutoevolveAI. Their generating scripts are committed in the rusty branch.
- The fetched arXiv texts behind the Tier-L hashes are in `/home/callensxavier_gmail_com/programmes-2026-10-25/P2/g2/src_*`.
  `ledger/sources/` is empty (see N5).
- No external data set is used. All numbers are computed.

## 7. publication_meta.json

These items are accurate: the title, version, Lean sha256, base commit `9d245742…`, rusty commits, test counts,
the list of refuted potentials, the riesz:4 caveat, the seed-detector skip, and the arXiv related identifiers.
Required updates are in C1, C2 and C3.

---

## Corrections required before publication (no result changes)

- **C1 — "false as stated".** The abstract of main.tex and the meta description say "We tested it … and it is false
  as stated". That is a Tier-X result stated as a bare fact.
  - Reword, for example: "… and it fails numerically (Tier X): …".
  - Keep "numerically refuted" as elsewhere in the paper.
  - The logical statement in ZP-C-0011 can stay as written.
- **C2 — "four narrower ones" is wrong.** It appears in the main.tex abstract, and the meta says "four narrower
  potentials (Gaussian a = 0.25, 2, 4, Riesz s = 6)".
  - For e^{−πar²}, a = 0.25 is the *widest* Gaussian tested.
  - The survivors are one wide Gaussian, two narrow ones and the shortest-range Riesz.
  - Replace "narrower" with a neutral description.
- **C3 — stale verification-status statements.** These statements will be false once this audit exists:
  - main.tex AI disclosure: "No separate AI audit of this preprint has been done either".
  - Limitations bullet: "No independent AI or human audit of this preprint, of the Lean module, or of the Rust
    code".
  - publication_meta description: "No human audit and no independent AI audit of this preprint, its Lean module or
    its Rust code has been done".

  Update them to say that a separate AI agent audited the work, and keep within the audit-scope paragraph above:
  - it recompiled the Lean with its own planted controls
  - it reproduced the gauss:1 and gauss:0.5 refutations with an independent real-space code
  - it regenerated all macros and re-checked the citations
  - it reran the crate tests

  **Keep** the caveats that describe the *paper-stage rerun*, because they stay true: "not a producer ≠ verifier
  check" and "a rerun by the same AI pipeline, not a separate verifier". Still say that no human audit exists. The
  8 `LEDGER_UNAUDITED_TIER_A` flags must stay open, because an AI adequacy review is not a person's certification.
- **C4 — riesz:4 caveat missing from the main.tex abstract.**
  - The abstract says "refuted for 8 of 12" without the caveat that the meta description carries.
  - riesz:4 rests on one competitor (0.3+0.954i) with a long-wave margin of 0.08 % of the triangular value. That is
    the same regime as the demoted gauss:1 point. Its finite-k stability rests only on G1 grids, and its triangular
    point is a local minimum (c > 0).
  - Add one clause to the abstract.
- **C5 — the competitor tables disagree.**
  - tab:pot lists the gauss:1 "robust min" at 0.295+0.9555i (LW 0.06 %). The text explicitly demotes that point as
    marginal and "not the headline".
  - tab:elastic, whose caption says "competitor used in each refutation", uses 0.5+0.966i for gauss:1 and for
    gauss:0.5. tab:pot uses (0.5, 1.016) for gauss:0.5.
  - Mark the gauss:1 row of tab:pot with † (marginal; the refutation uses 0.5+0.966i), or use one competitor choice
    consistently across both tables.

## Non-blocking notes

- **N1 — two conventions for min λ/|k|².**
  - The Rust `ezp_gauss_duffy` and the Table 2 Nelder–Mead values use κ reduced to the parallelogram
    [−½, ½]²: 0.03222 (tri), 0.03493 (head).
  - The Step 9 listing reduces κ to the Wigner–Seitz cell: 0.097 (tri), 0.068 (head). This reverses the order of
    the two lattices.
  - The sign, and so the stability verdict, is unaffected. State the convention.
- **N2 — QU-1′ endpoints and "exactly".** QU-1′ states an "iff" with a ∉ [a₁, a₂], a closed interval whose
  endpoints are bisected numerical roots. At c = 0 the second-order test is inconclusive, so the endpoint behaviour
  is unsupported. "negative exactly for a ∈ (…)" is also strong for a 21-point scan plus bisection. Write
  "numerically, c < 0 on (a₁, a₂)".
- **N3 — isotropy holds for a ≥ 0.5 only.** "∂xx = ∂yy to 1e−6 relative" holds for a ≥ 0.5 (1.3–1.5e−6). At
  a = 0.25 the relative difference is 4.3e−4 and the gradient is about 1e−5, near the soft-shear region.
- **N4 — bibliography details.**
  - The Bétermin bibitem gives pp. 3236–3269 "as listed in" Luo–Wei, whose reference [7] actually reads "3236-269".
  - The assertion is on Luo–Wei pp. 2–3, not p. 3 only.
  - Deng–Luo ref. [27] gives the Luo–Wei journal version, J. Math. Phys. 65 (2024) 071901. It can be cited
    second-hand.
- **N5 — Tier-L source texts not bundled.** `ledger/sources/` is empty. Bundle the two pdftotext source files, or
  record their paths, so that a reader of the Zenodo bundle can re-check the Tier-L hashes.
- **N6 — hand-coded macro.** `MaxStableDist` is hard-coded ("0.23") rather than generated. The value is correct
  (0.2274).
- **N7 — hardening point.** `omega_sum` and `ezp_gauss_duffy` return a clipped E_zp for unstable shapes, so callers
  must check `min_ratio`. The current tests and scripts do.
- **N8 — unpushed and uncommitted artefacts.** The rusty branch is not pushed, and the G2 JSONs and paper files are
  uncommitted in AutoevolveAI. Commit and push them before publication so that the hashes cited in the paper
  resolve.
- **N9 — the non-CM controls show detection power only.** They show the search *can* find a lower-E_zp stable
  lattice. They are not a false-positive control; gauss:2 and the frozen-phonon checks play that role. Morse:3 also
  shows a stable lower-E_zp competitor at 0.5+0.966i (in tab:neg), which the text does not mention.
