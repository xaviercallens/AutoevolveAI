# Where the openai/math Lean library can help your Lean work, rusty-SUNDIALS and numerics

Date 2026-10-08. Based on four read-only surveys of this server (all Lean projects outside dependency trees, rusty-SUNDIALS,
the openai/math clone) plus a spot-check of the key declarations quoted below. Nothing here was built except what is marked.

## Bottom line first

1. **openai/math does not touch the core of your theory.** No K3, Mathieu M24 / moonshine, E8 / Leech / Narain lattices,
   Picard-Fuchs operators, Apéry-like sequences or T-duality anywhere in its 121,734 files (the only regex hits were identifiers).
   Its Navier-Stokes work is about universal computation in forced flows, not regularity. So it will not prove, refute or
   strengthen the dual-scale / K3 programme directly.
2. **The overlap is infrastructure**: certified interval / ball arithmetic with soundness theorems, verified matrix inverses,
   the "integer table + `decide +kernel` + soundness lemma" certificate method (zero `native_decide` in the whole library), and a few
   ODE / matrix-analysis lemmas. That is exactly what your numerics are missing: today no project on this server exports a
   numerical result into a Lean proof, and rusty-SUNDIALS has no interval arithmetic at all.
3. **Several of the most valuable targets need only Mathlib, not openai/math** (rusty-SUNDIALS integrator theory, k3 recurrences).
   They are listed separately so openai/math does not get credit it does not deserve.
4. **Hygiene first**: several of your Lean files contain inconsistent or vacuous axioms (appendix). Anything importing them proves nothing.

## What exists today (survey summary)

| Project | Lean | Status that matters here |
|---|---|---|
| LeanMaster (`~/SocrateAI-Scientific-Agora-LeanMaster`, v3.45.0+, Lean 4.34.0-rc2) | 252 files, 22.7k lines, 0 sorry, 0 axiom | Strongest asset. Real matrix results (`dualScale_ge`: 2d ≤ tr G + tr G⁻¹, `etaR_genMetric_sq`), lattices, finite moonshine / dyon checks on truncated q-series. Every ODE/PDE-named file (`StiffIntegrators`, `MildPDEs`, `NSMath/OpenAIBridging`) is a placeholder; `OpenAIBridging` cites openai only in docstrings. |
| LeanProposal (Stream 1) | 39 files, 8.7k lines, 2 axioms | Genuine operator / sequence / lattice algebra (`partner_magic`, `sqrtSeq_two_adic`, `s7_complement_is_A2`). Hauptmodul check is numeric only. |
| k3-clean / K3-DarkMatter `lean4_formal_proofs` (4.34.0) | 59 files, 11.7k lines, 5 sorry, 124 axioms | Proved Sym² identities and Wolstenholme; but the s7/s10/S20/T103 recurrences and 108 Fano supercongruences are axioms; 55 `native_decide` uses fail the axiom whitelist. Certified monodromy (Arb balls) exists only outside Lean. |
| AutoevolveAI `formal/` (4.34.0-rc2) | 44 files, 6.6k lines | BAO / DESI lemmas clean (`ANSE.BAOFlatLCDM.E`, `E_pos`, …); Verlet symplectic map over ℚ; BSD / RH / NS / YM / Hodge are statements only. |
| DualScaleSimulator (+13 worktrees) | 26 files | 27 axioms, the Buscher ones inconsistent (own audit F1). Real stiff ODE (modular-curve quintessence) only in Python SciPy Radau, which failed (numerical Jacobian overflow in mpmath). |
| Mensura (NS shell model companion) | 3 files, 0 sorry | Shell-model energy identities; no interval arithmetic (not an interval tool). |
| runux-ai-runtime `spec` (4.30.0) | 16 files, 16 sorry | Only real interval arithmetic on the server, in Rust (`crates/interval_arith`, directed rounding). Lean `LeanFlow.regularity` is tautological; nothing links the Rust certificate JSON to Lean. |
| rusty-SUNDIALS | `proofs/lean4` 74 files, no lakefile, CI checks 1 file | Spec-only; vacuous / inconsistent axioms; no Lean ↔ Rust link. Real numerics: BDF CVODE (Adams stuck at order 1 on main; fix in open PR #63), BAO DESI DR2 fit, ITER 0-D current quench with an exact energy-identity control. |

## Matches, by kind of help

### A. openai/math code worth porting (copy into a pinned project; no clean `import` exists)

**A1. Certified-numerics bridge: from Rust intervals to a kernel-checked enclosure.** *Highest value; the only item that combines all three assets.*
- openai/math asset (checked): `OAI/LinearAlgebra/MatrixFields/Certificates/CertificatesReplay.lean`
  - `structure Ball where center : ℚ; radius : ℚ`, `Ball.Encloses b x := |x - b.center| ≤ b.radius` (line 201, 208)
  - `inductive Certificate : Expression → Ball → Prop` with constructors constant / add / neg / mul / inv / log / widen (line 378)
  - `theorem Certificate.sound (h : Certificate e b) : b.Encloses e.value` (line 389)
  - Missing for our use: `sqrt` and a quadrature remainder. `RI.sqrt` / `RI.mem_sqrt` and `CI.exp` exist in
    `Triangular/Certificate/WaveIntervals.lean` (not checked line by line) and can be ported next to it.
- Your side: `ANSE.BAOFlatLCDM.E (Om z : ℝ) := √(Om (1+z)^3 + (1-Om))` with `E_pos` (formal/ANSE/BAO_FlatLCDM.lean:24, 29, clean);
  rusty-SUNDIALS `qf-bao-distances` (DESI DR2 fit Ωm = 0.29743 ± 0.00861, on origin/main);
  runux `interval_arith` (directed-rounding f64 intervals; doc comments at lib.rs:6, 78, 98).
- What is genuinely new work: (i) a Rust emitter that turns an interval computation of D_M(z)/r_d into an integer / rational
  table; (ii) a Lean quadrature error bound for ∫ dz/E(z) (check Mathlib first); (iii) the soundness chain from table to
  `D_M(z) ∈ [lo, hi]`. Neither repo has an emitter today; openai/math ships re-checkers, not emitters.
- Payoff: the first kernel-checked numerical statement in your programme ("the published DESI fit point gives D_M(z)/r_d in
  [lo, hi] for every DESI redshift"), with the solver suite as the untrusted calculator. The same bridge then applies to the
  ITER energy identity and to any ODE output.

**A2. Verified matrix inverse from a residual.** `Triangular/Certificate/InverseEnclosure.lean` (from the survey, not
line-checked): `isUnit_of_right_residual` (‖1 − AB‖ < 1 ⇒ A invertible), `inverse_bound_of_right_residual`
(‖A⁻¹‖ ≤ k/(1−e)), plus `MatrixInterval.lean` (`matrixMul_mem`, `matrixNorm_bound`).
- Uses: certify the Newton / dense-LU linear solves in a rusty-SUNDIALS step from the computed approximate inverse; certify
  that a numerically computed monodromy or Gram matrix is invertible. Medium value, small port (matrix files are
  self-contained apart from the whole-Mathlib import).

**A3. (Low, speculative) Hermitian functional calculus.** `LiebThirring/ResolventCalculus.lean` (`integral_hermitian_cfc`)
and `MatrixTangent.lean` could help extend LeanMaster's `dualScale_eq_iff` (equality case only for B = 0). Not checked
whether they fit; listed so it is not forgotten.

**A4. (Low) A₂ theta inversion.** `Triangular/Energy/Theta.lean:171` `theta_transform` (θ(c) = 2/(√3 c) θ(4/(3c)), checked
to exist) next to LeanProposal's `s7_complement_is_A2`. Relevance to your modular statements is unverified.

### B. openai/math methodology only (the idea transfers, the code does not)

**B1. Replace `native_decide` by `decide +kernel`.** openai/math uses `decide +kernel` over a million times and
`native_decide` zero times, so every certificate stays inside {propext, Classical.choice, Quot.sound}. Your k3 corpus has 55
`native_decide` (`Structures/S12S21Recurrence.lean` 38, `S12RecurrenceVerification.lean` 13, Cooper s7/s10 2 + 2); these
theorems currently pick up `Lean.ofReduceBool` and fail your own whitelist. Cheapest real upgrade on the server.

**B2. Validated Taylor stepping for ODEs.** Transonic (`Core.lean` Box / `Holds`; `Exterior/Step.lean:52` `stepBox_enclosed`,
checked: it is specific to the transonic recursion `scaledRatioStep`) shows how to carry a power-series ODE solution through
integer boxes with a soundness lemma per step. Template for: kernel-checked Picard-Fuchs continuation (turning the
K3-DarkMatter Arb certified monodromy of L₂ into Lean), and for certified ODE solutions from rusty-SUNDIALS.

**B3. Certificate discipline.** Generated integer tables + soundness theorem + an independent Python / C++ re-checker
(Triangular `verification/check_certificate.py` on the same 10^60 grid). This is what runux `LeanFlow` should become:
today its `regularity` theorem only restates its hypotheses.

### C. Mathlib-only targets (openai/math irrelevant, but high value for rusty-SUNDIALS and k3)

**C1. rusty-SUNDIALS integrator theory.** Replace axioms that certify nothing or certified a real bug:
- `master_spec.lean:145` `axiom bdf_astability_orders_1_2 : ∀ z : ℂ, z.re < 0 → True` (vacuous).
- `roadmap/v2_upgrades.lean:55` `axiom rescale_interpolation_exact` (the repo's own CVODE doc says it "certified" the buggy
  Nordsieck shift behind the tight-tolerance failure).
- Provable over ℚ / ℂ: the `BDF_L` table (`crates/cvode/src/solver.rs:35`) satisfies the BDF order conditions; zero-stability
  (root condition) of BDF1-5 and its failure at BDF6; Nordsieck rescale z_i ← ηⁱ z_i represents the same polynomial while the
  binomial shift used before PR #60 does not; Adams l / tq tables of PR #63.
- Defect-to-global-error: openai's `bounded_ode_perturbation` (`LiebThirring/MatrixFlow.lean:44`) is a thin wrapper of Mathlib's
  `dist_le_of_approx_trajectories_ODE`, so use Mathlib directly.
- Requires a real lake project for `proofs/lean4` (none exists; CI checks one file).

**C2. ITER 0-D current quench.** The exact identity W_mag(0) − W_mag(t) = Q_p + Q_v and dissipativity from
det = L_p L_v − M² > 0 for the two-loop L-R system: a short Mathlib proof that turns the example's numerical control into a theorem.

**C3. k3 recurrences.** Prove `cooper_s7_recurrence` etc. from creative-telescoping certificates checked by `ring`
(LeanProposal already proves operator identities this way; the S20 telescoping `sorry` hit a timeout). openai/math offers nothing here.

### D. No useful match

- K3 / M24 / moonshine / E8 / Narain / T-duality / Picard-Fuchs: nothing in openai/math.
- Navier-Stokes regularity (Mensura, runux LeanFlow, LeanMaster `NSMath`): openai's NS families are about computation, not regularity.
- Vlasov-Maxwell global existence vs the 0-D fusion models: too far apart (its flow lemmas, e.g. `hasFDerivAt_variational_flow`,
  would matter only once rusty-SUNDIALS has forward sensitivities, which it does not).
- DualScaleSimulator stiff quintessence ODE: a numerics task, not a Lean one. Port it to rusty-SUNDIALS BDF with an analytic
  Jacobian to escape the documented Radau / mpmath overflow; the specified `examples/cosmology_quintessence.rs` does not exist yet.

## Constraints for any of this

- Versions differ: openai/math is Lean 4.34.1 + Mathlib d13f23b7; your projects are on 4.34.0-rc2, 4.34.0, 4.33.1 and 4.30.x.
  Reuse means porting files with pinned Mathlib imports (never `import Mathlib`, per CLAUDE.md).
- Recommended host: a new lake project next to the already-built pinned stack on disk 2
  (`/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/openai_math_pinned`), so the 8 GB Mathlib cache is reused.
- Only `sharp_lieb_thirring` and `universal_energy_minimum` have been built and Comparator-checked here. Every other
  openai/math module is an upstream claim until a ported copy builds under the pin.
- `~/rusty-SUNDIALS` is checked out on another session's branch (`merge-mcp-temp`, 4 behind origin/main): any work there
  needs a worktree off origin/main.

## Proposed first pilot (not started)

**P1: certified BAO distance.** Port `Ball` / `Expression` / `Certificate.sound` plus a sqrt enclosure into a pinned project;
add a quadrature remainder lemma; emit a table from Rust (`interval_arith` or exact rationals) for D_M(z)/r_d at the DESI
redshifts and the published best-fit point; close it with `decide +kernel` and `#print axioms` within the whitelist.
Controls: positive, the Einstein-de Sitter closed form must be enclosed; negative, a table for Ωm × 1.01 must fail to
enclose the best-fit value at the stated width. Cost estimate: one to two days of work, small builds (the pinned Mathlib is cached).

## Appendix: axioms that make files unsound or vacuous (fix before importing anything)

| File | Problem |
|---|---|
| DualScaleSimulator `proofs/BuscherRules.lean` | 5 custom axioms; `inv_inv : 1/(1/x) = x` for any F derives False at Nat (own audit F1) |
| rusty-SUNDIALS `proofs/lean4/psc_sop_ph_lyapunov.lean:65` | `psc_telemetry_oracle` proves \|drift\| < 1e-8 for every drift: inconsistent |
| rusty-SUNDIALS `fusion_sop_flagno.lean`, `fusion_sop_monopole.lean` | oracle axioms; the fusion audit kernel-checked False from each |
| rusty-SUNDIALS `jfnk_autodiff.lean:51` | `autodiff_exactness` for arbitrary `f : Dual → Dual`: likely inconsistent (not probed) |
| rusty-SUNDIALS `master_spec.lean:145`, `roadmap/v2_upgrades.lean:55` | vacuous / bug-certifying (C1) |
| runux `spec/LeanFlow/Regularity.lean` | `regularity` restates its hypotheses; interval lemmas left as `sorry` |
| k3 `Agora/Discovery/FanoSupercongruences.lean` | 108 conjectures declared as axioms (not imported by the root, keep it that way) |
| k3 `Structures/*Recurrence.lean` | general recurrences as axioms (C3) |
