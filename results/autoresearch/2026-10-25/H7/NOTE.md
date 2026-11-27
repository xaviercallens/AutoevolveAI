# H7: cutoff-uniform enstrophy bound for the σ = 3 regulated shell model (QuantumFluids)

Attempt 1 of 1 this round, started 1792919761 (unix). Toolchain: QuantumFluids lean_src env, Lean v4.34.0-rc2,
qf-lake build, direct `lean` with LEAN_PATH (H8 recipe), cores 6,7.

## Pinned statement (written before any attempt)

Sources: `PLAN.md` l.42 ("σ = 3 regulator ⇒ cutoff-uniform enstrophy bound | open"), `docs/DUAL_SCALE_PROPOSAL.md`
§5 and §7 step 2 ("σ = 3 in Lean: 2DΩ ≤ H + (2E)^{3/2}"), `lean_src/ShellHamiltonian.lean` (docstring of
`dispersive_norm_le`), `exploration/second_invariant/symbolic_check.py` (the model with dispersion).

Model (complexified truncated dyadic shell model, shells 0..N+1, truncation v_{N+2} = 0):

    dv_n/dt = k_{n-1} v_{n-1}^2 - k_n conj(v_n) v_{n+1} - i ω_n v_n,   k_n = 2^n,   ω_n = D k_n^σ,

`σ = 2` is quantum pressure (the owner's symbolic check); H7 is `σ = 3`.

Quantities, with the owner's index ranges (S over `range (N+2)`, cubic over `range (N+1)`):

- `S = Σ_{n<N+2} |v_n|^2`, `E = S/2`
- `Ω = ½ Σ_{n<N+2} k_n^2 |v_n|^2`
- `H₃ = Σ_{n<N+2} 2^{-n} D k_n^3 |v_n|^2 + Σ_{n<N+1} 2^{-n} k_n Im(conj(v_n)^2 v_{n+1})`
  (the §5 formula `H = Σ 2⁻ⁿ[ω_n|v_n|² + k_n Im(conj(v_n)²v_{n+1})]` with ω_n = D k_n³; weight kept as 2^{-n} k_n,
  not simplified to 1, so it matches the proposal literally)

Claim (pointwise, every N, every v : ℕ → ℂ, every real D):

    2 D Ω ≤ H₃ + (2E)^{3/2}         (rpow, exponent 3/2 : ℝ)

Corollary (D > 0): `Ω ≤ (H₃ + (2E)^{3/2}) / (2D)`.

Why this is "cutoff-uniform": the right-hand side depends on N only through H₃ and E. **It is uniform along the
dynamics only on condition that H₃ and E are conserved by the σ = 3 flow.** In Lean the owner has only (i) energy
conservation of the nonlinearity (`shellBc_energy_conservation`) and (ii) the cubic-part algebraic core
(`hamiltonian_rate_zero`). The cross-term cancellation between the dispersive term and the cubic part, and the chain
rule along solutions, are NOT in Lean; this attempt checks them exact-symbolically (numeric_gate.py, part a) and does
not claim them in Lean.

Expected status: a direct specialization of the owner's `dispersive_norm_le` (q_n = 2^{-n} D k_n^3 = D k_n^2,
c_n = 2^{-n} k_n = 1). New here would be only the faithful σ = 3 definitions, the rpow form, the D > 0 Ω bound,
and the controls. No novelty claim.

Kill criterion (preregistered): numeric counterexample, or the attempt fails.

## Planned controls

- Planted `ctl_sorry` (sorryAx) and `ctl_axiom` (user axiom) in a separate file.
- Negative control 1 (Lean + numeric): dropping the (2E)^{3/2} term is false: explicit 2-shell state with H₃ < 2DΩ.
- Negative control 2 (numeric): σ = 2 does not reach enstrophy: 2DΩ / (H₂ + S^{3/2}) grows like 2^N on a top-shell state.
- Negative control 3 (symbolic): perturbed weight on one shell breaks dH₃/dt = 0.

## Outcome (attempt 1, 17 min): KEEP (producer-checked)

- Numeric gate (`numeric_gate.py`, `numeric_gate.json`, gate_pass True): σ = 3 conservation of H₃ and mass exact-symbolic
  (N = 3, 5, both seams, general k_n), perturbed-weight control fails as required; 0 violations / 200000 random states;
  sup (2DΩ − H₃)/S^{3/2} = 0.451 (adversarial) < 1; drop-S^{3/2} control violated (5 > 4); σ = 2 ratio 4095 at N = 11;
  split-step dynamics N = 4, T = 10: Ω stays ≤ the t = 0 bound (156.6 ≤ 175.0), |ΔH₃| ≤ 9e-4 (single dt, not refined; (a) is the conservation evidence), |ΔS| ≤ 4e-12.
- Lean: `Autoresearch_Enstrophy.lean` rc 0 on first compile, no warnings (`compile_main.log`); theorems `enstrophy_bound`,
  `enstrophy_le`, `drop_cubic_term_fails` (+ helpers), all `[propext, Classical.choice, Quot.sound]`.
- Controls: `ctl_sorry` shows sorryAx, `ctl_axiom` shows `ctl_cheat`. Grep for sorry/admit/native_decide/axiom in the
  main file: no matches.
- Scope: a corollary of the owner's `dispersive_norm_le`. Conservation of H₃ along the σ = 3 flow is not in Lean, so
  "uniform in the cutoff along the dynamics" is conditional on it. The O5 trap argument (§7 step 2, second half) was not attempted.
- Infra: page cache warmed (8765 qf-lake oleans) during the gate; no IO starvation this time.
