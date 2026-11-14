# P1 S3: fidelity of the Lean statement of the Sandier-Serfaty conjecture (Tier C)

Date: 2026-10-25. Lean file: `formal_cert/Programmes/SandierSerfatyStatement.lean`. Planted controls:
`formal_cert/Programmes/SandierSerfatyStatementControls.lean`. Lock: `results/programmes/2026-10-25/P1/STATEMENT_LOCK.json`.
Toolchain: Lean 4.34.1, Mathlib `d13f23b723b8a846827a245b89c10fc7d3f11612` (the pinned openai/math stack).

**What this is.** A Lean *statement* of the conjecture. Nothing here proves it. The definitions are compared below
with the openai/math manuscript (AI-generated, not peer reviewed; build/sections/01-introduction.tex and
02-reduction.tex) and with Sandier-Serfaty 2012 (arXiv:1011.4617v2). I read SS2012 through alphaXiv in this stage:
Def. 1.1 and (1.1)-(1.5) on p.2, Def. 1.2 and (1.6)-(1.8) with Remarks 2, 4 and 7 on pp.2-3, Lemma 1.3 on p.4,
Thm 1, Thm 2, Remark 1.5 and Conjecture 1 on pp.4-5, Prop. 3.1 on pp.26-27. The comparison is my own reading (Tier C).
Only the small lemmas listed under "Proved" are Tier A.

## The three Props

| Lean name | Source | Shape |
|---|---|---|
| `SandierSerfatyStatement` | manuscript Theorem `thm:main` (Sec. 1) | `(∃ χ, cutoff) ∧ ∃ E₀, Admissible Λ_△ E₀ ∧ Λ_△-periodic E₀ ∧ ∀ χ cutoff, ∃ w₀, (∀R>1, W(E₀,χ_R)=w₀ R) ∧ W(E₀) finite ∧ ∀ Λ E w, Admissible Λ E → (∀R>1, W(E,χ_R)=w R) → W(E₀) ≤ W(E)` |
| `SandierSerfatyValueStatement` | the same, with BS2018's value | inf attained by a `Λ_△`-periodic `E₀`, equal to `π log(2√2π/(√3 Γ(1/3)³))` |
| `SandierSerfatyOriginalStatement` | SS2012 Conjecture 1, for every `m > 0` | currents `j ∈ A_m`, ball cutoffs, `Λ_m`; same quantifier shape |

## Definition-by-definition comparison

| # | Object | Manuscript | SS2012 | Lean | Verdict |
|---|---|---|---|---|---|
| 1 | Plane, area | R², Lebesgue | R², `\|·\|` area | `EuclideanSpace ℝ (Fin 2)` with `volume`: Euclidean norm and balls, product Lebesgue measure (Mathlib `EuclideanSpace.volume_preserving_symm_measurableEquiv_toLp`). `ℝ × ℝ` was avoided because Mathlib gives it the sup norm. | exact |
| 2 | Point set | "locally finite and simple" (eq. admissible) | "discrete set Λ" (Def. 1.1) | `Λ : Set Plane` (so points are simple) with `LocFinite Λ`: `Λ ∩ K` is finite for every compact `K` | exact for the manuscript. For SS, "discrete" is read as locally finite, which is what ν being a locally finite measure and (1.2) need. |
| 3 | Density bound | `sup_{R>1} ν_Λ(B_R)/\|B_R\| < ∞` | (1.2), ν = 2πΣδ | `∃ C, ∀ R>1, ncard(Λ ∩ ball 0 R) ≤ C·πR²` | exact. `ncard` is honest because `LocFinite` makes the set finite. Open vs closed `B_R` only changes C. |
| 4 | Field equations | `div E = 2π(ν_Λ−1)`, `curl E = 0` in D', E ∈ L¹_loc (L^q_loc, q<2, gives the same class: Lemma red:local) | `curl j = ν − m`, `div j = 0` (1.1) | `LocallyIntegrable E` plus the weak forms against every real `C_c^∞` φ (`ContDiff ℝ ∞`, which is not analytic `⊤`): `−∫E·∇φ = 2πΣ_{p∈Λ}φ(p) − b∫φ` with `b = 2π`, and `∫(E₀∂₁φ − E₁∂₀φ) = 0`. SS: `∫ j·∇φ = 0` and `∫(j₀∂₁φ − j₁∂₀φ) = 2πΣφ(p) − m∫φ`. | exact: this is the definition of equality in D'. Mathlib now has `Distribution`, but the classical weak form was chosen for transparency. Signs were checked by `negPi_admissibleBg_iff` (div(−πx) = −2π forces b = 2π). |
| 5 | Local energy `W(E,χ)` | eq. local-energy: `lim_{η↓0}[½∫_{R²∖∪B(p,η)} χ\|E\|² + π log η Σ χ(p)]` | (1.7), identical | `HasLocalEnergy Λ E χ w`: eventually in η, `χ‖E‖²` is integrable on `(⋃_{p∈Λ} ball p η)ᶜ`, and the bracket tends to `w` along `𝓝[>] 0`. The finite sum is `∑ᶠ p ∈ Λ, χ p`, which is a true finite sum because Λ∩supp χ is finite. | exact as a relation. No `limUnder`, and the Bochner integral cannot return its junk value 0. Removing open rather than closed disks changes only null circles. **Conditional:** the existence of the limit for every admissible E (manuscript Lemma red:local; SS Remark 2) is *not* formalized. If it failed for some E, that E would drop out of the competitor class, which would make the Lean statement weaker, not stronger. |
| 6a | Square cutoffs | eq. cutoffs: `χ_R ∈ C_c^∞`, `0≤χ_R≤1`, supp ⊂ K_R, `χ_R = 1` on K_{R−1}, `sup_R ‖∇χ_R‖_∞ < ∞` | (1.3) for U_R = K_R | `IsSquareCutoffFamily`: the same five clauses for R > 1, with `tsupport` as the closed support and `‖fderiv‖` (operator norm = Euclidean \|∇χ\|) uniformly bounded | exact. Non-empty: `exists_squareCutoffFamily` (Tier A). |
| 6b | Ball cutoffs | — | (1.3): `\|∇χ\| ≤ C`, Supp ⊂ B_R, `χ = 1` where `d(x,B_Rᶜ) ≥ 1` (equivalently ‖x‖ ≤ R−1), "positive" | `IsBallCutoffFamily`: those clauses plus `C^∞` and `χ ≤ 1` | **deviation:** a smaller class. SS Thm 1(1) (p.4) says `W_U(j)` does not depend on the choice of cutoff satisfying (1.3), for families with (1.4)-(1.5), which balls satisfy, so the values are unchanged (Tier L). Non-empty: `exists_ballCutoffFamily` (Tier A). |
| 7 | `W(E)` | eq. whole-energy: `limsup_R W(E,χ_R)/\|K_R\|`, \|K_R\| = 4R², both infinite values allowed | (1.6): balls, \|B_R\| = πR² | `WSq w = limsup_{R→∞} ((w R/(4R²) : ℝ) : EReal)` and `WBall w = limsup(w R/(πR²))` | exact. ±∞ are allowed, as in the manuscript ("initially allowed to take either infinite value"). |
| 8 | Triangular lattice | eq. triangular-lattice: `√(2/√3)(ℤ(1,0)+ℤ(1/2,√3/2))` | Thm 2: `Λ_m = √(4π/(m√3))((1,0)ℤ⊕(1/2,√3/2)ℤ)` | `triLattice` and `ssTriLattice m`, written out literally | exact. Covolumes 1 and 2π/m are proved (`triBasis_covolume`, `ssBasis_covolume`, Tier A). |
| 9 | `E_△` / `j_Λ` | the mean-zero Λ_△-periodic solution of `−Δh_△ = 2π(δ_0−1)` on R²/Λ_△, with `E_△ = −∇h_△` | `j_Λ = −∇^⊥H_Λ`, mean-zero periodic solution (Lemma 1.3, Prop. 3.1); `W(Λ) := W_U(j_Λ)` | an existential witness `E₀` that is admissible for Λ_△ and a.e. Λ_△-periodic | **equivalent given SS Prop. 3.1** (Tier L, pp.26-27): every periodic admissible field with charges Λ is `j_Λ + c` and has `W ≥ W(j_Λ)`, with equality iff c = 0. If the conjecture holds, E₀ := E_△ is a witness. Conversely, a witness E₀ = E_△ + c gives `W(E_△) ≤ W(E₀) ≤ W(E)` for all E, so E_△ is a minimizer. Mathlib has no torus Green function, which is why E_△ is not defined directly. |
| 10 | Minimum statement | Thm `thm:main`: `W(E) ≥ W(E_△)` for every cutoff family and every E ∈ 𝒜₁ (including W(E) = +∞); triangular value finite; `inf = W(E_△)` | Conj. 1: `W(Λ_m) = min_{A_m} W` | ∀ competitors (Λ, E, w) with the puncture relation for all R > 1: `WSq w₀ ≤ WSq w`; plus `WSq w₀ ≠ ⊤, ⊥`. The infimum statement follows because E₀ is itself admissible. | exact (modulo rows 5 and 9). Quantifier order: E₀ comes before ∀χ, as E_△ does not depend on χ; w₀ is chosen per χ. |
| 11 | Value | `W(E_△) = 6K+λ+2πμ`, identified numerically with BS2018 | — | `wTriClosedForm = π·log(2√2π/(√3·Γ(1/3)³))` | the Lean expression evaluates (mpmath, 30 digits, this stage) to −4.15041280767896337944. That matches S2's BS2018 closed form −4.1504128076789633794 and S2's Ewald sum, and lies inside the certificate's printed interval (S2 calibration check). The wrong transcription with √(2π) (negative control) gives −5.94855. The identification `W(E_△) = wTriClosedForm` is Tier L (BS2018 p.26) + Tier X, and is not formalized. |
| 12 | E-form vs SS j-form | Sec. 2, Lemma red:plane-bound: `j = (−E₂,E₁)`, scaling (1.9) with m = 2π, square vs ball | (1.9), (1.12), Thm 1(3) (the min and minimizers are independent of U, although `W_U(j)` of a fixed non-minimizer can depend on U: Remark 4) | two separate Props | the equivalence of `SandierSerfatyStatement` and `SandierSerfatyOriginalStatement` is Tier L/C (S2 audit rows R1-R10) and is not formalized. |

## Proved non-degeneracy lemmas (Tier A, axioms ⊆ {propext, Classical.choice, Quot.sound}; see STATEMENT_LOCK.json)

- `negPi_admissibleBg_iff`: with Λ = ∅, the field E(x) = −πx satisfies the weak equations with background b iff b = 2π.
  - Positive control `negPi_admissible`: 𝒜₁ ≠ ∅.
  - Negative controls `negPi_not_admissible_noBackground` (b = 0) and `negPi_not_admissible_wrongSign` (b = −2π): those degenerate variants are detectably different.
  - The proof tests against a bump with positive integral (`bump_integral_pos`), which also certifies that the test-function class is not collapsed to 0.
- `negPi_hasLocalEnergy` and `competitor_nonvacuous`: for every manuscript cutoff family, some competitor meets all hypotheses of the ∀-clause, so `W(E₀) ≤ W(E)` is a real constraint.
- `exists_squareCutoffFamily` and `exists_ballCutoffFamily`: both cutoff classes are non-empty, so `∀ χ` is not vacuous.
  - Square: χ_R(x) = s(R−x₀)s(R+x₀)s(R−x₁)s(R+x₁). Ball: χ_R(x) = s(2(R−‖x‖)−1). Here s = `Real.smoothTransition`.
  - The gradient bound is uniform in R, via a global Lipschitz bound for s.
- `triBasis_covolume`, `ssBasis_covolume`.
- Planted controls: `ctl_sorry` and `ctl_axiom` "prove" `SandierSerfatyStatement`. The file compiles with rc 0, but `#print axioms` shows `sorryAx` and `ProgSandierSerfaty.ctl_cheat` respectively, so both are caught.
- Lock control: changing the background in `Admissible` from `2 * Real.pi` to `0` changes the statement-region sha256 from 38974cc1… (locked) to ed68e1c8…. `statement_lock.py check` gives `match: true` on the files as they stand.

## Honest gaps of the non-vacuity check (not proved here)

1. That `triLattice` is locally finite with bounded density. This is doable with Mathlib's `ZLattice` and lattice-point counting; it was not done in this budget.
2. That any field *with charges* is admissible. The `∑ᶠ p ∈ Λ, φ p` term in `WeakDivE` is exercised only with Λ = ∅. The same goes for the renormalization term `π log η · ∑ᶠ p ∈ Λ, χ p` in `localEnergyAt`: no proof exercises it, so a sign or factor slip there would not be caught by any Lean check. A single-charge example, `(x−p)/|x−p|² − π(x−p)`, would need a weak Gauss law with a singularity.
   - Tier C sign check of the energy term. Near a charge, E = (x−p)/|x−p|² + smooth (manuscript Lemma red:local; SS Remark 2), so ½∫_{η<|x−p|<ρ} |x−p|⁻² dx = ½·2π·log(ρ/η) = π log ρ − π log η.
   - The Lean term `+ Real.pi * Real.log η * χ(p)` cancels the −π log η·χ(p) divergence, matching manuscript eq. local-energy and SS (1.7).
   - With `−π log η` the bracket would diverge like 2π log(1/η)·χ(p), and with `2π log η` like −π log(1/η)·χ(p). Then `HasLocalEnergy` would be unsatisfiable for every admissible field with a charge where χ(p) ≠ 0.
3. That a Λ_△-periodic admissible field exists (that is, the triangular side is inhabited). This needs the periodic Green function.

## Missing Mathlib infrastructure (pinned rev; grep found none of these)

- Green function / periodic Poisson solution on a flat torus. This is needed to define h_△, E_△ and j_Λ intrinsically and to inhabit the triangular side.
- Weyl's lemma / elliptic regularity for distributional div-curl systems. This is needed to prove that the puncture limit exists for every admissible field (manuscript Lemma red:local).
- A packaged weak Gauss law for the 2D Coulomb kernel (`div(x/|x|²) = 2πδ_0`).

## Bottom line

The Lean Props match the manuscript's definitions clause by clause (rows 1-8, 10). The exceptions are: (i) the existence of the puncture limit is assumed, not proved (row 5); (ii) E_△ is replaced by an existential periodic witness, equivalent by SS Prop. 3.1 (row 9, Tier L); (iii) the SS ball-cutoff class is restricted to smooth cutoffs, harmless by SS Thm 1(1) (row 6b, Tier L). The statement is locked by sha256 and is not proved.
