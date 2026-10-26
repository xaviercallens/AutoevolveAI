# P6, stage WORK2: the Feynman–Bijl single-mode bound in Lean (pinned openai/math stack)

Status: **KEEP**, first budget. All declarations compile (rc 0) under Lean 4.34.1 + Mathlib as pinned by openai/math:
21 in `Basic.lean`, 4 in `NegativeControls.lean` and 3 in `PositiveControls.lean`. Each one's `#print axioms` stays within
{propext, Classical.choice, Quot.sound}. Both planted controls are caught. The gate is
`scripts/axiom_gate.py`, whose output is `lean/axiom_gate.json`: `"GATE": "PASS"`. That is a gate run by the
producer only. No independent re-verification has been done yet.

Files (sha256 of the final sources):

| file | role | sha256 |
|---|---|---|
| `formal_cert/Programmes/FeynmanBijl/Basic.lean` | theorems (module `Programmes.FeynmanBijl.Basic`) | `a8ed4357bce846e675af161a81dbeddeedcba07c0a2e7f2ae09fce21c5cb6432` |
| `formal_cert/Programmes/FeynmanBijl/NegativeControls.lean` | a genuine counterexample: the symmetry hypothesis cannot be dropped (module `Programmes.FeynmanBijl.NegativeControls`) | `182f8135dd3c778703a8523e46724f600227a3bdcaadc4da5a8bc843373bfc3a` |
| `formal_cert/Programmes/FeynmanBijl/PositiveControls.lean` | witness: all hypotheses of `feynman_bijl_gap` hold together, and the bound is attained | `1555d75cda679a600b667ac0f559b7bd72f9cee3982c644531ee6f81d4bffc05` |
| `formal_cert/Programmes/FeynmanBijl/Controls.lean` | planted `ctl_sorry` / `ctl_axiom` (never import) | `a0f2e8edab9b5aa211fd1a5b39d8836cc22220b483390413edda46135e0c0099` |

Compile records are in `lean/compile_basic.json`, `lean/compile_negctl.json`, `lean/compile_posctl.json` and
`lean/compile_controls.json`. Each holds the full stdout, rc and seconds; the final compiles took 10.5 s, 6.9 s, 6.7 s and 6.2 s.
`lean/attempts/compile_try{1..5}.json` are the logs of the intermediate failing iterations: tactic errors in `rayleigh_expansion` and
one superfluous `ring`. They are kept for the record. They are not gate inputs, and try1 contains `sorryAx` lines from the then-unfinished proof.
Command used: `taskset -c 4-7 python3 scripts/certified_numerics/lean_pinned.py compile FILE [--olean Programmes.FeynmanBijl.Basic] --json-out OUT`.

## Setting (exact Lean definitions)

`E` is a finite-dimensional complex inner product space:
`[NormedAddCommGroup E] [InnerProductSpace ℂ E] [FiniteDimensional ℂ E]`. `H ρ : E →ₗ[ℂ] E`, `ψ : E`, `E0 : ℝ`.
`ρ†` is Mathlib's Hilbert adjoint `LinearMap.adjoint ρ`.

```lean
def comm (A B : E →ₗ[ℂ] E) : E →ₗ[ℂ] E := A ∘ₗ B - B ∘ₗ A

/-- A(X) = ⟪Xψ, (H - E₀) Xψ⟫ -/
noncomputable def excess (H : E →ₗ[ℂ] E) (E0 : ℝ) (ψ : E) (X : E →ₗ[ℂ] E) : ℂ :=
  ⟪X ψ, H (X ψ)⟫_ℂ - (E0 : ℂ) * ⟪X ψ, X ψ⟫_ℂ
```

Dictionary to the physics:
- `ρ` is the density fluctuation ρ_k and `ρ†` is ρ_{-k}.
- `⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫` is the f-sum ⟨ψ₀|[ρ_k†,[H,ρ_k]]|ψ₀⟩.
- N·S(k) = ‖ρψ‖², so `S = ‖ρ ψ‖^2 / N`.

## Exact statements (Tier A, verbatim from Basic.lean)

**Key algebraic step, with no hypotheses beyond symmetric H and an eigenvector ψ.**
```lean
theorem double_comm_expect (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ) (ρ : E →ₗ[ℂ] E) :
    ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = excess H E0 ψ ρ + excess H E0 ψ (adjoint ρ)
```

**Half the f-sum.** This needs the k ↔ −k symmetry hypothesis `hsym`.
```lean
theorem excess_eq_half (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ) (ρ : E →ₗ[ℂ] E) {f : ℂ}
    (hf : ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = f)
    (hsym : excess H E0 ψ (adjoint ρ) = excess H E0 ψ ρ) :
    excess H E0 ψ ρ = f / 2
```

**Trial-state energy, the statement the stage asked for.** The normalised trial state ρψ/‖ρψ‖ has energy E₀ + f/(2NS):
```lean
theorem trial_energy_eq (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ) (ρ : E →ₗ[ℂ] E)
    {f N : ℝ} (hN : 0 < N) (hρψ : ρ ψ ≠ 0)
    (hf : ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = (f : ℂ))
    (hsym : excess H E0 ψ (adjoint ρ) = excess H E0 ψ ρ) :
    (⟪((‖ρ ψ‖⁻¹ : ℝ) : ℂ) • ρ ψ, H (((‖ρ ψ‖⁻¹ : ℝ) : ℂ) • ρ ψ)⟫_ℂ).re - E0
      = f / (2 * N * (‖ρ ψ‖ ^ 2 / N))
```

**Symmetry-free variant.** ψ is a ground state, the bound is weaker by a factor 2, and both terms of the identity are ≥ 0:
```lean
theorem trial_energy_le_of_ground (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ)
    (hgs : ∀ x : E, E0 * ‖x‖ ^ 2 ≤ (⟪x, H x⟫_ℂ).re) (ρ : E →ₗ[ℂ] E)
    {f N : ℝ} (hN : 0 < N) (hρψ : ρ ψ ≠ 0)
    (hf : ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = (f : ℂ)) :
    (⟪((‖ρ ψ‖⁻¹ : ℝ) : ℂ) • ρ ψ, H (((‖ρ ψ‖⁻¹ : ℝ) : ℂ) • ρ ψ)⟫_ℂ).re - E0
      ≤ f / (N * (‖ρ ψ‖ ^ 2 / N))
```

**Variational step in the sector excited by φ.** This uses Mathlib's spectral theorem: `eigenvectorBasis`, `eigenvalues`, and Parseval.
```lean
theorem sector_eigenvalue_le (hH : H.IsSymmetric) (φ : E) (hφ : φ ≠ 0) :
    ∃ i, ⟪hH.eigenvectorBasis rfl i, φ⟫_ℂ ≠ 0 ∧
      hH.eigenvalues rfl i ≤ (⟪φ, H φ⟫_ℂ).re / ‖φ‖ ^ 2
```

**Feynman–Bijl bound.** The f-sum rule enters as a hypothesis.
```lean
theorem feynman_bijl_bound (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ) (ρ : E →ₗ[ℂ] E)
    {N m hbar k S : ℝ} (hN : 0 < N) (hm : 0 < m) (hS : 0 < S) (hSdef : S = ‖ρ ψ‖ ^ 2 / N)
    (hf : ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = ((N * hbar ^ 2 * k ^ 2 / m : ℝ) : ℂ))
    (hsym : excess H E0 ψ (adjoint ρ) = excess H E0 ψ ρ) :
    ∃ i, ⟪hH.eigenvectorBasis rfl i, ρ ψ⟫_ℂ ≠ 0 ∧
      hH.eigenvalues rfl i - E0 ≤ hbar ^ 2 * k ^ 2 / (2 * m * S)
```

**Gap form.** This is the non-trivial reading. Taken alone, `feynman_bijl_bound` is satisfied trivially by λᵢ = E₀ whenever ρψ overlaps the E₀-eigenspace. The gap form excludes that case:
```lean
theorem feynman_bijl_gap (hH : H.IsSymmetric) (hψ : H ψ = (E0 : ℂ) • ψ)
    (hgs : ∀ x : E, E0 * ‖x‖ ^ 2 ≤ (⟪x, H x⟫_ℂ).re) (ρ : E →ₗ[ℂ] E)
    (horth : ∀ v : E, H v = (E0 : ℂ) • v → ⟪v, ρ ψ⟫_ℂ = 0)
    {N m hbar k S : ℝ} (hN : 0 < N) (hm : 0 < m) (hS : 0 < S) (hSdef : S = ‖ρ ψ‖ ^ 2 / N)
    (hf : ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ = ((N * hbar ^ 2 * k ^ 2 / m : ℝ) : ℂ))
    (hsym : excess H E0 ψ (adjoint ρ) = excess H E0 ψ ρ) :
    ∃ i, ⟪hH.eigenvectorBasis rfl i, ρ ψ⟫_ℂ ≠ 0 ∧
      0 < hH.eigenvalues rfl i - E0 ∧
      hH.eigenvalues rfl i - E0 ≤ hbar ^ 2 * k ^ 2 / (2 * m * S)
```

`feynman_bijl_bound_ground` has the same hypotheses as `feynman_bijl_bound`, but replaces `hsym` with `hgs`. Its conclusion is
`hH.eigenvalues rfl i - E0 ≤ hbar ^ 2 * k ^ 2 / (m * S)`.

Helper lemmas, all Tier A and all printed:
- `inner_eig_H`, `excess_re`, `rayleigh_normalised`
- `exists_le_weighted_mean`: some index with positive weight is ≤ the weighted mean
- `rayleigh_expansion`: re⟪x,Hx⟫ = Σᵢ ‖⟪eᵢ,x⟫‖² λᵢ

### Connection to H8 (Bogoliubov), Tier A

The variables are those of H8:
- hc = ħc and ks = k* = 2mc/ħ;
- ε₀ = hc·k²/ks;
- ε_B = √((hc k)² + (hc k²/ks)²);
- S_B = ε₀/ε_B.

H8 itself was checked on another stack (`import DualLength`, LeanMaster rc2). The definitions are restated here and re-proved on the pinned stack.
The signatures below omit the implicit binders `{hc ks k : ℝ}`, `{hc ks k S : ℝ}` and `{hbar m c k : ℝ}`; see Basic.lean for the verbatim
text.
```lean
theorem epsFree_units (hh : 0 < hbar) (hm : 0 < m) (hc : 0 < c) :
    epsFree (hbar * c) (2 * m * c / hbar) k = hbar ^ 2 * k ^ 2 / (2 * m)
theorem feynman_sBog_eq (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    epsFree hc ks k / sBog hc ks k = epsBog hc ks k
theorem feynman_sBog_units (hh : 0 < hbar) (hm : 0 < m) (hc : 0 < c) (hk : 0 < k) :
    hbar ^ 2 * k ^ 2 / (2 * m * sBog (hbar * c) (2 * m * c / hbar) k)
      = epsBog (hbar * c) (2 * m * c / hbar) k
theorem feynman_le_epsBog_iff (hhc : 0 < hc) (hk : 0 < k) (hS : 0 < S) :
    epsFree hc ks k / S ≤ epsBog hc ks k ↔ sBog hc ks k ≤ S
theorem sBog_sq (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ^ 2 = k ^ 2 / (ks ^ 2 + k ^ 2)
theorem sBog_le_sqrt (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ≤ Real.sqrt (k / (2 * ks))
```

What these lines show at Tier A:
- The Feynman energy ħ²k²/(2m S), computed from S_B, equals ε_B exactly.
- The Feynman energy computed from a measured S is ≤ ε_B iff S ≥ S_B.

What they do **not** show:
- That the Bogoliubov ground state saturates the operator bound in `feynman_bijl_bound`. The abstract `H` is not the Bogoliubov Hamiltonian, so that claim is Tier C/L: textbook, Bogoliubov theory with a single-mode excitation spectrum.

## `#print axioms` (verbatim, lean/compile_basic.json, rc 0)

```
'ProgFeynmanBijl.inner_eig_H' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.epsBog_pos' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.sBog_pos' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.double_comm_expect' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.excess_eq_half' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.excess_re' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.rayleigh_normalised' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.trial_energy_eq' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.trial_energy_le_of_ground' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.exists_le_weighted_mean' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.rayleigh_expansion' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.sector_eigenvalue_le' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.feynman_bijl_bound' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.feynman_bijl_bound_ground' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.feynman_bijl_gap' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.epsFree_units' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.feynman_sBog_eq' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.feynman_le_epsBog_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.sBog_sq' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.sBog_le_sqrt' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.feynman_sBog_units' depends on axioms: [propext, Classical.choice, Quot.sound]
```

## Controls

**Genuine negative control.** `NegativeControls.lean` is Tier A, rc 0, whitelist axioms only.

`symmetry_needed` takes orthonormal e₀, e₁ with:
- H = |e₁⟩⟨e₁|;
- ψ = e₀, so E₀ = 0;
- the one-sided operator ρ = |e₁⟩⟨e₀|.

Then the double commutator equals 1 and A(ρ) = 1 ≠ 1/2, because ρ†ψ = 0. `symmetry_needed_fin2` instantiates this on
`EuclideanSpace ℂ (Fin 2)`. So `hsym` in `excess_eq_half`, `trial_energy_eq` and `feynman_bijl_bound` is load-bearing.
```
'ProgFeynmanBijl.ketBra_apply' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.ketBra_self_symm' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.symmetry_needed' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.symmetry_needed_fin2' depends on axioms: [propext, Classical.choice, Quot.sound]
```

**Positive control, showing the gap theorem is not vacuous.** `PositiveControls.lean` is Tier A, rc 0, whitelist axioms only.

`gap_witness` takes orthonormal e₀, e₁ with:
- H = |e₁⟩⟨e₁|;
- ψ = e₀, so E₀ = 0;
- the Hermitian ρ = |e₁⟩⟨e₀| + |e₀⟩⟨e₁|.

It proves every hypothesis of `feynman_bijl_gap` with N = ħ = k = 1 and m = 1/2:
- `IsSymmetric`;
- the eigen-equation;
- the ground-state inequality;
- ρψ ⊥ ker H;
- S = 1;
- f-sum = 2;
- `hsym`, which holds via `adjoint ρ = ρ`.

It also proves that H(ρψ) = 1·ρψ with 1 = ħ²k²/(2mS), so the bound is **attained** (sharp) on this instance.

`gap_witness_applies` feeds these hypotheses to `feynman_bijl_gap`. `orthonormal_pair_fin2` shows the orthonormal pair exists in ℂ².
```
'ProgFeynmanBijl.gap_witness' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.gap_witness_applies' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgFeynmanBijl.orthonormal_pair_fin2' depends on axioms: [propext, Classical.choice, Quot.sound]
```

**Planted controls.** `Controls.lean` has rc 0, and both cheats are caught by `#print axioms`. Each one claims the false strengthening
A(ρ) = f, which lacks the 1/2 factor and the symmetry hypothesis.
```
'ProgFeynmanBijl.ctl_sorry' depends on axioms: [propext, sorryAx, Classical.choice, Quot.sound]
'ProgFeynmanBijl.ctl_axiom' depends on axioms: [propext, Classical.choice, ProgFeynmanBijl.ctl_cheat, Quot.sound]
```

**Gate self-test.** On the first gate run, `axiom_gate.py` reported FAIL because 4 helper lemmas had no `#print axioms` line, so it does
flag gaps. After the prints were added it reported PASS.

**Float cross-check, Tier X, supports no claim.** Script: `scripts/feynman_bijl_numeric.py`; output: `lean/feynman_bijl_numeric.json`. Seed
20261025, 200 random 12×12 instances, ψ = ground state.

| check | result |
|---|---|
| POS-1: double-commutator identity, random ρ | max relative residual 1.7e-15 |
| POS-2: Hermitian ρ (so the symmetry holds), A(ρ) = f/2 | max relative residual 6.7e-16 |
| POS-2: trial excess = f/(2NS) | max relative residual 1.1e-16 |
| POS-2: sector bound holds | 200/200 |
| POS-3: Bogoliubov ħ²k²/(2mS_B) = ε_B | max relative residual 1.8e-16 |
| POS-3: H8 bound | holds at 2000/2000 grid points |
| NEG-1: the 2×2 counterexample | A(ρ) = 1, A(ρ†) = 0, f = 1 |
| NEG-2: random non-symmetric ρ, \|A(ρ) − f/2\|/\|f\| | min 0.0019, median 0.079 |
| NEG-3: planted claim A = f | caught 200/200 |

POS-2 uses a random Hermitian ρ. That generically gives ⟪ψ,ρψ⟫ ≠ 0, so the POS-2 instances satisfy the hypotheses of `feynman_bijl_bound`
but **not** the orthogonality hypothesis of `feynman_bijl_gap`. The gap theorem's non-vacuity rests on the Tier A `gap_witness` above.

## Tiers and caveats (Elenchus)

- **Tier A.** These are statements about an abstract finite-dimensional Hermitian `H`, an eigenvector `ψ` and an arbitrary operator `ρ`. Tier A certifies
  exactly the Lean statements above and nothing about their physical reading.
- **The f-sum rule `hf` is a hypothesis.**
  - It follows from the canonical commutation relations, which have no finite-dimensional representation, so it cannot be derived inside this setting.
  - No literature source was verified or pinned in this stage. Before the paper stage, the f-sum rule and the original Feynman (1954) and
    Bijl (1940) papers must be pinned to page and equation (Tier L). Until then the physics reading has no Tier L support from this stage.
- **The symmetry `hsym`.** A(ρ_{-k}) = A(ρ_k) is the inversion or time-reversal symmetry of the fluid. Here it is a hypothesis, and the counterexample above shows it is needed.
- **"Sector" means an eigenvector with nonzero overlap with ρψ.**
  - `feynman_bijl_bound` alone can be satisfied by λ = E₀.
  - The meaningful statement is `feynman_bijl_gap`. It needs ρψ ⊥ the E₀-eigenspace.
  - For k ≠ 0 that orthogonality comes from momentum conservation, which is Tier C here and not formalised.
- **Applying this to measured S(k) is Tier C.** It reads "measured S(k) gives the upper bound ε(k) ≤ ħ²k²/(2mS(k))" and is conditional on all of the following:
  - the exact f-sum rule;
  - the symmetry;
  - S being the T = 0 ground-state structure factor.
  - The stage-1 He-4 data are at 1.4–4 K and contain thermal S. Two X-ray points at Q = 0.213 and 0.267 Å⁻¹ already exceed the Feynman self-check, as recorded in DATA.md/results.json.
  - The BEC values are Tier X, from digitised figures.
- **Novelty is not claimed.** This is the textbook Feynman–Bijl argument, formalised. The result does not depend on openai/math theorems; it only uses the pinned openai/math Lean/Mathlib toolchain.
