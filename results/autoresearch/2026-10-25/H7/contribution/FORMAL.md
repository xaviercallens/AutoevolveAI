# H7 stage 1 (FORMALIZE): conservation of H₃ along the σ = 3 shell flow, and the enstrophy bound along solutions

Status: **producer-checked only** (producer = this lane; an independent verifier has not run yet). Tier A candidate,
QuantumFluids environment (Lean v4.34.0-rc2, qf-lake Mathlib build, importing the owner's compiled `ShellHamiltonian`).

## 1. Fresh-eyes recheck of the prior round

| file | sha256 | rc | result |
|---|---|---|---|
| `H7/Autoresearch_Enstrophy.lean` (copied to `contribution/recheck_Autoresearch_Enstrophy.lean`) | `c7c9f24cfe2e623f36600d11e11841e7cbd75f4b3801fa602681980735c97f03` (both copies identical) | 0 | 6 theorems, all `[propext, Classical.choice, Quot.sound]` |
| `H7/Autoresearch_EnstrophyControls.lean` (copied to `contribution/recheck_Autoresearch_EnstrophyControls.lean`) | `0c722d5f73d0c4b375b06df6735c364f160c9a199b7d0c36fab7506094444588` (both identical) | 0 | `ctl_sorry` shows `sorryAx`, `ctl_axiom` shows `ctl_cheat` |

The recompile of the main file took 2163.9 s wall (`recheck_prior.json`). The cause was disk-2 page-cache thrash,
not proof cost. After the closure (rc2 core + qf-lake, about 6.1 GB) was re-warmed, the same environment compiles a file in 10–16 s.

Verbatim `#print axioms` (recheck):
```
'QuantumFluids.AutoresearchEnstrophy.weight_eq_one' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.disp_weight' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.sqrt_mul_self_eq_rpow' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.enstrophy_bound' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.enstrophy_le' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.drop_cubic_term_fails' depends on axioms: [propext, Classical.choice, Quot.sound]
```
I also re-read the prior statement against the model. `ham3` is the §5 formula with ω_n = D k_n³ and the weight kept as 2⁻ⁿk_n.
The prior proof is a direct specialisation of the owner's `dispersive_norm_le`, which is what the prior NOTE says.
I found nothing to correct.

## 2. New file: `contribution/Autoresearch_EnstrophyFlow.lean`

sha256 `4cd746897f58f7a18eb27e95f703b43d49ec0eb5c5f38753cd5f0bc1a99a8dd4`, **rc 0**, 15.5 s (`compile_flow_final.json`).
The only output is linter warnings (unused simp args, `<;>` style): no errors and no `sorry` warning.
The hole grep `grep -n "sorry\|admit\|native_decide\|^axiom"`, re-run on the final file (sha `4cd74689…8dd4`) after the last edit, gives no match (rc 1).
Earlier attempts: try 1 rc 1 with 5 errors, all fixed in try 2 (rc 0). Try 1's JSON records a sha taken after the
file was edited, so it is diagnostic only.

Section 1 of the file repeats the prior definitions (`kk`, `energy`, `enstrophy`, `ham3`), helper lemmas and `enstrophy_bound`
with identical statements and proof bodies. `diff` of that block against the prior file shows only that the docstring of
`enstrophy_bound` was shortened. `enstrophy_le` and `drop_cubic_term_fails` are not repeated.

### Model as formalised
`F k ω v n := shellBc k n v - I * ω n * v n`. This is the owner's conjugated complexified Katz–Pavlović nonlinearity
`shellBc` plus the dispersive rotation `-i ω_n v_n`. Truncation: shells `0..N+1` with `v (N+2) = 0`.
σ = 3 is `k = kk` (`kk n = 2ⁿ`) and `ω n = D * kk n ^ 3`. The general functional is

    hamG q g N v = Σ_{n<N+2} q n * normSq (v n) + Σ_{n<N+1} g n * (conj(v n) * conj(v n) * v (n+1)).im

with first variation `dHam q g N v w`, the product rule written out. `ham3 D N v = hamG (fun n => (1/2)^n * (D * kk n ^ 3)) (fun n => (1/2)^n * kk n) N v`
holds by `rfl` (`ham3_eq_hamG`).

### Theorem list (exact Lean statements)

```lean
theorem re_conj_mul_F (k ω : ℕ → ℝ) (v : ℕ → ℂ) (n : ℕ) :
    ((starRingEnd ℂ) (v n) * F k ω v n).re = ((starRingEnd ℂ) (v n) * shellBc k n v).re

theorem dT_F (k ω : ℕ → ℝ) (v : ℕ → ℂ) (n : ℕ) :
    (2 * (starRingEnd ℂ) (v n) * (starRingEnd ℂ) (F k ω v n) * v (n + 1)
        + (starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * F k ω v (n + 1)).im
      = dT k v n + (2 * ω n - ω (n + 1)) * R v n
    -- R v n = (conj(v n) * conj(v n) * v (n+1)).re ; dT is the owner's ShellHamiltonian.dT

theorem quad_tel (k ω q g : ℕ → ℝ) (v : ℕ → ℂ)
    (hw : ∀ n, 2 * q (n + 1) * k n + g n * (2 * ω n - ω (n + 1)) = 2 * q n * k n) :
    ∀ M : ℕ, ∑ n ∈ Finset.range (M + 1), q n * (2 * ((starRingEnd ℂ) (v n) * shellBc k n v).re)
        + ∑ n ∈ Finset.range M, g n * ((2 * ω n - ω (n + 1)) * R v n)
      = -(2 * q M * k M * R v M)

theorem rate_zero (k ω q g : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ)
    (hg : ∀ n, g (n + 1) * (2 * k n) = g n * k (n + 1))
    (hw : ∀ n, 2 * q (n + 1) * k n + g n * (2 * ω n - ω (n + 1)) = 2 * q n * k n)
    (hbc : v (N + 2) = 0) :
    dHam q g N v (F k ω v) = 0

theorem ham_rate_zero (k ω : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (hbc : v (N + 2) = 0) :
    dHam (fun n => (1 / 2 : ℝ) ^ n * ω n) (fun n => (1 / 2 : ℝ) ^ n * k n) N v (F k ω v) = 0

theorem energy_rate_zero (k ω : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (hbc : v (N + 2) = 0) :
    ∑ n ∈ Finset.range (N + 2), 2 * ((starRingEnd ℂ) (v n) * F k ω v n).re = 0

theorem hasDerivAt_hamG (q g : ℕ → ℝ) (N : ℕ) (u : ℝ → ℕ → ℂ) (u' : ℕ → ℂ) (t : ℝ)
    (hu : ∀ n, n < N + 2 → HasDerivAt (fun s => u s n) (u' n) t) :
    HasDerivAt (fun s => hamG q g N (u s)) (dHam q g N (u t) u') t

theorem const_on_Icc (Φ : (ℕ → ℂ) → ℝ) (Φ' : (ℕ → ℂ) → ℝ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hd : ∀ t ∈ Set.Icc (0 : ℝ) T, HasDerivAt (fun s => Φ (u s)) (Φ' (u t)) t)
    (hz : ∀ t ∈ Set.Icc (0 : ℝ) T, Φ' (u t) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T, Φ (u t) = Φ (u 0)

theorem ham_conserved (k ω : ℕ → ℝ) (N : ℕ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hsol : ∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => u s n) (F k ω (u t) n) t)
    (hbc : ∀ t ∈ Set.Icc (0 : ℝ) T, u t (N + 2) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T,
      hamG (fun n => (1 / 2 : ℝ) ^ n * ω n) (fun n => (1 / 2 : ℝ) ^ n * k n) N (u t)
        = hamG (fun n => (1 / 2 : ℝ) ^ n * ω n) (fun n => (1 / 2 : ℝ) ^ n * k n) N (u 0)

theorem cross_weights_ok (k ω : ℕ → ℝ) (n : ℕ) :
    2 * ((1 / 2 : ℝ) ^ (n + 1) * ω (n + 1)) * k n + ((1 / 2 : ℝ) ^ n * k n) * (2 * ω n - ω (n + 1))
      = 2 * ((1 / 2 : ℝ) ^ n * ω n) * k n
    -- no separate #print axioms line; ham_rate_zero depends on it and is audited

theorem energy_conserved (k ω : ℕ → ℝ) (N : ℕ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hsol : ∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => u s n) (F k ω (u t) n) t)
    (hbc : ∀ t ∈ Set.Icc (0 : ℝ) T, u t (N + 2) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T, energy N (u t) = energy N (u 0)

theorem enstrophy_bound_along_flow (D : ℝ) (N : ℕ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hsol : ∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => u s n) (F kk (fun m => D * kk m ^ 3) (u t) n) t)
    (hbc : ∀ t ∈ Set.Icc (0 : ℝ) T, u t (N + 2) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T,
      2 * D * enstrophy N (u t) ≤ ham3 D N (u 0) + (2 * energy N (u 0)) ^ (3 / 2 : ℝ)

theorem enstrophy_le_along_flow (D : ℝ) (hD : 0 < D) (N : ℕ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hsol : ∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => u s n) (F kk (fun m => D * kk m ^ 3) (u t) n) t)
    (hbc : ∀ t ∈ Set.Icc (0 : ℝ) T, u t (N + 2) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T,
      enstrophy N (u t) ≤ (ham3 D N (u 0) + (2 * energy N (u 0)) ^ (3 / 2 : ℝ)) / (2 * D)

theorem zero_trajectory_is_solution (D : ℝ) (N : ℕ) (T : ℝ) :
    (∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => (fun (_ : ℝ) (_ : ℕ) => (0 : ℂ)) s n)
        (F kk (fun m => D * kk m ^ 3) ((fun (_ : ℝ) (_ : ℕ) => (0 : ℂ)) t) n) t)
    ∧ (∀ t ∈ Set.Icc (0 : ℝ) T, (fun (_ : ℝ) (_ : ℕ) => (0 : ℂ)) t (N + 2) = 0)

-- sensitivity controls (N = 0, D = 1, v11 = (1,1,0,…), v111 = (1,1,1,0,…)), proved by direct computation
theorem rate_v11_correct :
    dHam (fun n => (1 / 2 : ℝ) ^ n * (1 * kk n ^ 3)) (fun n => (1 / 2 : ℝ) ^ n * kk n) 0 v11
      (F kk (fun m => 1 * kk m ^ 3) v11) = 0
theorem rate_v11_wrong_weight :
    dHam (fun n => 1 * kk n ^ 3) (fun n => (1 / 2 : ℝ) ^ n * kk n) 0 v11
      (F kk (fun m => 1 * kk m ^ 3) v11) = 8
theorem rate_v111_no_truncation :
    dHam (fun n => (1 / 2 : ℝ) ^ n * (1 * kk n ^ 3)) (fun n => (1 / 2 : ℝ) ^ n * kk n) 0 v111
      (F kk (fun m => 1 * kk m ^ 3) v111) ≠ 0
```

### `#print axioms` (verbatim, final compile)
```
'QuantumFluids.AutoresearchEnstrophy.enstrophy_bound' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.re_conj_mul_F' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.dT_F' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.quad_tel' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.rate_zero' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.ham_rate_zero' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.energy_rate_zero' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.hasDerivAt_hamG' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.const_on_Icc' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.ham_conserved' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.energy_conserved' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.enstrophy_bound_along_flow' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.enstrophy_le_along_flow' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.zero_trajectory_is_solution' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.rate_v11_correct' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.rate_v11_wrong_weight' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchEnstrophy.rate_v111_no_truncation' depends on axioms: [propext, Classical.choice, Quot.sound]
```

## 3. Planted controls (separate file, never in the claimed module)

`contribution/Autoresearch_EnstrophyFlowControls.lean`, sha256 `7a3904240f4734df1360471af1bce7fb420ff279298298da6effc9f5c9e065ce`,
rc 0 (`compile_flow_controls.json`). Both controls state a false rate identity (energy rate = 1). Verbatim:
```
...Autoresearch_EnstrophyFlowControls.lean:13:8: warning: declaration uses `sorry`
'QuantumFluids.AutoresearchEnstrophyFlowControls.ctl_sorry' depends on axioms: [propext,
 sorryAx,
 Classical.choice,
 Quot.sound]
'QuantumFluids.AutoresearchEnstrophyFlowControls.ctl_axiom' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 QuantumFluids.AutoresearchEnstrophyFlowControls.ctl_flow_cheat]
```
The controls file exits with rc 0 even though it contains both holes. The axiom audit is the gate, not the exit code.

Sensitivity controls inside the claimed file. These check the algebraic rate identity, not the chain-rule layer:
- positive: `rate_v11_correct`. At (1,1,0,…) with the dyadic weights the rate is 0. This is computed directly by
  `simp`/`norm_num`, independently of `rate_zero`.
- negative 1: `rate_v11_wrong_weight`. Dropping the 2⁻ⁿ factor on the dispersive weight gives rate 8 ≠ 0, which matches
  the hand value −2 + 16 − 6 = 8.
- negative 2: `rate_v111_no_truncation`. Without the truncation (v₂ ≠ 0) the correct-weight rate is ≠ 0.

## 4. What is new compared with the prior round

The prior round had only the pointwise inequality. Conservation of H₃ was then checked exact-symbolically in Python and
was not in Lean. This round adds the following in Lean:
1. **The full rate identity along the dispersive vector field** (`rate_zero`, `ham_rate_zero`). This covers the
   nonlinear/cubic part (via the owner's `sum_dT`), the nonlinear/quadratic part and the dispersion/cubic cross terms.
   Those last two parts were not in Lean before. The owner's own `lean_src/ShellHamiltonian.lean` docstring lists,
   under "WHAT IS NOT PROVED", "the dispersive (`D`) and GPE-seam (`μ`) extensions (checked as exact polynomial
   identities in exploration/second_invariant/symbolic_check.py, not in Lean)". This file closes the dispersive (D) part
   of that gap. The μ (GPE-seam) part is still open.
   A finding from the proof: the identity holds for the dyadic weights q_n = 2⁻ⁿω_n, g_n = 2⁻ⁿk_n with **any** real
   sequences k and ω. The cross-term condition `2q_{n+1}k_n + g_n(2ω_n − ω_{n+1}) = 2q_n k_n` reduces to an identity
   (`cross_weights_ok`), so σ = 3 plays no role in conservation. It matters only in `enstrophy_bound`, because
   q_n = 2⁻ⁿ D k_n³ = D k_n² is the weight that turns the quadratic part into 2DΩ.
2. **Energy rate along F** (`energy_rate_zero`). This reuses the owner's `shellBc_energy_conservation` at cutoff N+1,
   and adds the fact that the dispersive rotation does no work.
3. **The chain rule** (`hasDerivAt_hamG`, `energy_conserved`) and constancy on [0,T] (`const_on_Icc`, from Mathlib's
   `constant_of_has_deriv_right_zero`).
4. **The bound along solutions** (`enstrophy_bound_along_flow`, `enstrophy_le_along_flow`): for every t ∈ [0,T],
   2DΩ(t) ≤ H₃(0) + (2E(0))^{3/2}.

## 5. Honest scope

- **The solution is a hypothesis.** No existence theorem, local or global, is proved. The solution hypotheses are
  consistent, because `zero_trajectory_is_solution` shows u ≡ 0 satisfies them, but that is all this shows. Global
  existence at fixed N should follow from conservation of E in finite dimensions (Tier C remark, not formalised).
- `HasDerivAt` is two-sided at every t ∈ [0,T], including the endpoints. The trajectory must therefore be
  differentiable on a neighbourhood of [0,T]; a one-sided endpoint hypothesis would be weaker and is not what is stated.
- **Everything is at a fixed finite cutoff N.** No N → ∞ limit or infinite-shell statement is made.
- **"Uniform in the cutoff" is conditional.** The right-hand side depends on N only through the initial data. H₃(0)
  contains 2DΩ(0), so the bound is uniform in N only for families of initial data with N-uniform Ω(0) and E(0), i.e. data
  in an H¹-type class. For such data it gives a uniform-in-N, uniform-in-time enstrophy bound at each fixed D > 0.
  The D-dependence (1/(2D)) is not uniform as D → 0.
- The model is the owner's conjugated complexification `shellBc` plus a dispersive term. The physical meaning and the
  fidelity of that model are the owner's design choices (QuantumFluids memo), not certified here. Tier A certifies the
  Lean statement only.
- The O5 trap (§7 step 2, second half) was not attempted.
- No breakthrough claim: this is a finite-dimensional conservation law plus an elementary inequality, and the
  formalisation closes the Lean gap the prior round recorded.

## 6. Reproduce

From the repo worktree root:

    taskset -c 4-7 /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I results/autoresearch/2026-10-25/H7/contribution/run_lean.py results/autoresearch/2026-10-25/H7/contribution/Autoresearch_EnstrophyFlow.lean OUT.json

`run_lean.py` sets LEAN_PATH to the qf-lake build, the package libs (mathlib, batteries, Qq, aesop, proofwidgets,
importGraph, LeanSearchClient, plausible, Cli) and the rc2 core lib, then runs
`~/.elan/toolchains/leanprover--lean4---v4.34.0-rc2/bin/lean`. If a compile sits at about 1% CPU, warm the closure first:
the `.olean` paths from `/proc/PID/maps` go into `warm_siblings.py`. `residency.py` reports page-cache residency.
