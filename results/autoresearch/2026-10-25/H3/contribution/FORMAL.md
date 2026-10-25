# H3L: Lean formalisation of the Keldysh / exponential-mixture admissibility (Stage 1, FORMALIZE)

Source: `formal_cert/Autoresearch/KeldyshCM.lean` (419 lines), module `Autoresearch.KeldyshCM`
(olean built into `formal_cert/.olean_out/Autoresearch/`). It imports `Autoresearch.Yukawa` (H2), which gives
`admissible_mul` and `admissible_congr`. The Lean file in this repo is the authority; the statements below are copied from it.

Pinned hashes at build time:
- `KeldyshCM.lean` sha256 `1bac0d410d366614c8d287f7ea95d495aa0ee09c4782cfa0d5b691a3048647f2`
- `KeldyshCMControls.lean` sha256 `d7e5516fe00a6599a181d5a394dde70a66c533d0a2693b78b9035281801f0606`
- dependency `Yukawa.lean` sha256 `a16397de179837dd2119cf09c1b3086db7650b9b8bbaeb322f2d531936c033cf`. Another lane
  edits and rebuilds it. `Yukawa.olean` mtime 2026-10-25 10:45:48 UTC is *older* than `KeldyshCM.olean`
  (10:51:12 UTC), and the controls compile ran after both, so the reported axiom output matches the oleans on disk.
  If Yukawa is rebuilt again, rebuild KeldyshCM.

Toolchain: pinned openai/math stack, Lean 4.34.1 + Mathlib d13f23b7, built with
`taskset -c 4-7 python3 scripts/certified_numerics/lean_pinned.py compile … --olean Autoresearch.KeldyshCM`.
Final compile: rc 0, 23.9 s (`compile_keldysh.json`). The only warning-free state is the final one; earlier
attempts are kept for the record (`compile_try1.json`: 1 error, unknown identifier; `compile_try2.json`: 4 errors;
`compile_try3.json`: rc 0 with one deprecation warning, since removed).

## Tier
- **Tier A** (kernel-checked; axioms limited to `propext, Classical.choice, Quot.sound`; planted controls caught):
  every theorem listed below, **as Lean statements about the Lean definitions**.
- **Tier C/X, not formalised:** that the mixture-defined `keldysh r₀` equals the physical Rytova–Keldysh potential
  `(π/(2r₀))[H₀ − Y₀](r/r₀)` at `t = r²`. That identity is the human proof plus the numerics in `../NOTE.md` and
  `../keldysh_check.py` (max rel. err. 2.1e-21 vs mpmath). Mathlib at this pin has no Struve H₀, Neumann Y₀, or erfc.
- Every triangular-lattice statement depends on upstream `universal_energy_minimum` (openai/math, AI-generated,
  not peer reviewed) and on definition fidelity (`AdmissiblePotential`, `latticeEnergy`, `energy`, `DensityOne`).

## Definitions (verbatim)
```lean
structure MixtureData (μ : Measure α) (k m : α → ℝ) : Prop where
  k_meas : Measurable k
  m_meas : Measurable m
  k_nonneg : ∀ᵐ x ∂μ, 0 ≤ k x
  m_nonneg : ∀ᵐ x ∂μ, 0 ≤ m x
  integrable : ∀ (n : ℕ) (c : ℝ), 0 < c → Integrable (fun x => k x ^ n * Real.exp (-(c * k x)) * m x) μ

noncomputable def erfcx (x : ℝ) : ℝ :=
  2 / Real.sqrt Real.pi * ∫ y in Ioi (0 : ℝ), Real.exp (-(y ^ 2 + 2 * x * y))
noncomputable def w (r0 a : ℝ) : ℝ := 1 / r0 * erfcx (Real.sqrt a / r0)
noncomputable def keldysh (r0 t : ℝ) : ℝ :=
  ∫ a in Ioi (0 : ℝ), w r0 a / (2 * a) * Real.exp (-t / (4 * a))
noncomputable def keldyshReg (r0 ε t : ℝ) : ℝ := keldysh r0 t * Real.exp (-(ε * t))
noncomputable def signedMix (t : ℝ) : ℝ := Real.exp (-t) - 2 * Real.exp (-(2 * t))
```
Fidelity of `erfcx` (Tier X, `fidelity_erfcx.py` → `fidelity_erfcx.json`, mpmath dps 30): the Lean integral form
matches `e^{x²} erfc x` at x ∈ {0, 0.01, 0.3, 1, 2.5, 7, 50} with max rel. err. **1.34e-31**. Negative control:
the perturbed integrand `exp(-(y² + x y))` differs by at least **5.6e-3** (relative) at x > 0.

## Theorems (exact Lean statements)
Generic lemma (any measure space `α`, any measure `μ`, `{k m : α → ℝ}`):
```lean
theorem laplace_admissible (h : MixtureData μ k m) :
    AdmissiblePotential (fun t => ∫ x, Real.exp (-(t * k x)) * m x ∂μ)
theorem laplace_iteratedDeriv (h : MixtureData μ k m) (n : ℕ) {t : ℝ} (ht : 0 < t) :
    iteratedDeriv n (fun t => ∫ x, Real.exp (-(t * k x)) * m x ∂μ) t =
      ∫ x, (-(k x)) ^ n * Real.exp (-(t * k x)) * m x ∂μ
```
How it is proved: induction with `hasDerivAt_integral_of_dominated_loc_of_deriv_le` on `Ioi (t/2)`, dominated by
`k^{n+1} e^{-(t/2)k} m`; `contDiffOn_succ_iff_deriv_of_isOpen` by induction for `ContDiffOn ⊤`; and
`Filter.EventuallyEq.deriv_eq` to move from `deriv` to `iteratedDeriv` on `Ioi 0`.

Instances and controls of the generic lemma:
```lean
theorem expNeg_admissible {ε : ℝ} (hε : 0 ≤ ε) : AdmissiblePotential (fun t => Real.exp (-(ε * t)))   -- Dirac μ
theorem signedMix_not_admissible : ¬ AdmissiblePotential signedMix   -- negative at t = log(3/2): m ≥ 0 is load-bearing
```
The Keldysh instance:
```lean
lemma erfcx_le_one {x : ℝ} (hx : 0 ≤ x) : erfcx x ≤ 1
lemma erfcx_le_inv {x : ℝ} (hx : 0 < x) : erfcx x ≤ 1 / (Real.sqrt Real.pi * x)
lemma keldysh_integrable {r0 : ℝ} (hr0 : 0 < r0) (n : ℕ) {c : ℝ} (hc : 0 < c) :
    IntegrableOn (fun a => (1 / (4 * a)) ^ n * Real.exp (-(c * (1 / (4 * a)))) * (w r0 a / (2 * a))) (Ioi 0)
theorem keldysh_admissible {r0 : ℝ} (hr0 : 0 < r0) : AdmissiblePotential (keldysh r0)
theorem keldysh_pos {r0 t : ℝ} (hr0 : 0 < r0) (ht : 0 < t) : 0 < keldysh r0 t
theorem triangular_keldysh_optimal {r0 : ℝ} (hr0 : 0 < r0) (C : Set Plane) (hC : LocallyFinite C)
    (hdens : DensityOne C) : latticeEnergy (keldysh r0) ≤ energy (keldysh r0) C
theorem keldyshReg_admissible {r0 ε : ℝ} (hr0 : 0 < r0) (hε : 0 ≤ ε) :
    AdmissiblePotential (keldyshReg r0 ε)
theorem triangular_keldyshReg_optimal {r0 ε : ℝ} (hr0 : 0 < r0) (hε : 0 ≤ ε) (C : Set Plane)
    (hC : LocallyFinite C) (hdens : DensityOne C) :
    latticeEnergy (keldyshReg r0 ε) ≤ energy (keldyshReg r0 ε) C
```
`keldysh_pos` is the non-vacuity check. If the defining integral were not integrable, the Bochner integral would be
0 and admissibility would be trivially true. `keldysh_pos` rules that out, and `keldysh_integrable` (n = 0)
shows the integral is a genuine convergent integral.

## `#print axioms` (verbatim, `compile_keldysh.json`)
```
'AutoresearchKeldysh.laplace_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchKeldysh.laplace_iteratedDeriv' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchKeldysh.expNeg_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchKeldysh.signedMix_not_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchKeldysh.erfcx_le_one' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchKeldysh.erfcx_le_inv' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchKeldysh.keldysh_integrable' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchKeldysh.keldysh_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchKeldysh.keldysh_pos' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchKeldysh.triangular_keldysh_optimal' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchKeldysh.keldyshReg_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchKeldysh.triangular_keldyshReg_optimal' depends on axioms: [propext, Classical.choice, Quot.sound]
```
A text search of `KeldyshCM.lean` finds 0 matches for `sorry`/`admit` and no `axiom` declarations.

## Planted controls (`formal_cert/Autoresearch/KeldyshCMControls.lean`, separate file; `compile_controls.json`, rc 0)
The controls file imports the built `Autoresearch.KeldyshCM` olean. Both planted false claims
(`AdmissiblePotential signedMix`) are caught. The compile exits 0 regardless: a successful compile is not a gate,
the axiom list is.
```
KeldyshCMControls.lean:11:8: warning: declaration uses `sorry`
'AutoresearchKeldyshControls.ctl_sorry' depends on axioms: [propext, sorryAx, Classical.choice, Quot.sound]
'AutoresearchKeldyshControls.ctl_axiom' depends on axioms: [propext,
 AutoresearchKeldyshControls.ctl_cheat,
 Classical.choice,
 Quot.sound]
```
The same run re-printed the claimed theorems from the imported olean, each with `[propext, Classical.choice, Quot.sound]`.

## New compared with the prior round
- The prior round (`../NOTE.md`) had **no Lean** for H3: Tier C proof plus Tier X numerics, H3L "not attempted" (prior 0.30).
- New, Tier A:
  1. the generic positive-exponential-mixture lemma, with the derivative formula. It covers Laplace transforms
     (`k = id`), Gaussian mixtures in `t = r²` (`k a = 1/(4a)`) and finite or Dirac mixtures.
  2. admissibility, strict positivity and the (conditional) triangular-optimality corollary for the mixture-defined
     Keldysh potential.
  3. the same for the Gaussian-regularised `keldysh · e^{-εt}`, for every ε ≥ 0 and r₀ > 0.
- The generic lemma is reusable for any interaction with a known positive Laplace or Gaussian-mixture
  representation. It is a standard fact (one direction of Bernstein's theorem, under a moment hypothesis); what is
  new here is only the machine-checked form against upstream's `AdmissiblePotential`.

## Scope and what is NOT shown
- **Definition fidelity gap:** `keldysh` is *defined* by the mixture. The equality with the Struve/Neumann form stays
  Tier C/X. A reader must trust NOTE.md's Hankel/Laplace/Fubini argument (or Route B, DLMF 11.5.2) for that step.
- **`triangular_keldysh_optimal` is expected to be `⊤ ≤ ⊤`.** The 1/r tail makes the 2D lattice sum diverge, so
  the raw-energy statement says nothing about which configuration wins. This is Tier C: `latticeEnergy (keldysh r0) = ⊤`
  is **not** proved in Lean, and neither is its negation.
- **`triangular_keldyshReg_optimal`:** whether `latticeEnergy (keldyshReg r0 ε) < ⊤` for ε > 0 was **not attempted**
  in Lean. It is expected to be true (e^{-εt} decay; Tier C), and it is needed before the corollary can be called
  non-trivial in Lean. A route: monotonicity from `laplace_iteratedDeriv` (n = 1), the lattice minimum distance,
  e^{-εt} ≤ 2/(ε t)², and comparison with `riesz 3` as in `latticeEnergy_yukawa_lt_top`.
- The physically relevant jellium (neutralised) energy of a TMD Wigner crystal is **not** covered. The limit ε → 0
  is not addressed.
- No breakthrough is claimed. Complete monotonicity of the Keldysh potential follows directly from a textbook formula
  (NOTE.md, Route B). The contribution is the kernel-checked admissibility against upstream's definition, plus the
  generic lemma.

## Reproduce
```
taskset -c 4-7 python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Autoresearch/KeldyshCM.lean --olean Autoresearch.KeldyshCM --json-out results/autoresearch/2026-10-25/H3/contribution/compile_keldysh.json
taskset -c 4-7 python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Autoresearch/KeldyshCMControls.lean --json-out results/autoresearch/2026-10-25/H3/contribution/compile_controls.json
/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I results/autoresearch/2026-10-25/H3/contribution/fidelity_erfcx.py
```
When disk 2 is IO-starved, the first compile may sit at about 2% CPU for over 10 minutes. Warming the import
closure (`olean_list_from_maps.py PID out.txt`, then the shared `warm_siblings.py out.txt`) brought it back to about 20 s.
Producer ≠ verifier: this compile is the producer's own. An independent recompile and review are still owed.
