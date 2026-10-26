import Triangular.AnyDensity
import Programmes.PopGen.Absorption
import Programmes.EvoGraph.BirthDeath
import Autoresearch.KeldyshCM
import Programmes.PopGen.Price

/-!
# Acronymes : cinq ré-exportations sous des noms courts

Each theorem below is a **re-export** of a result that is already kernel-checked elsewhere in
`formal_cert/`. The statement is copied verbatim from the source theorem and the proof is the source
theorem applied to its arguments; nothing new is proved here. The `example`s after each theorem check,
by `rfl`, that the re-exported constant has exactly the type of its source (same statement, not a
weaker or stronger one).

Each name is an acronym; its docstring gives the backronym.

| name      | source                                                     |
|-----------|------------------------------------------------------------|
| `ALIX`    | `TriangularDensity.triangular_optimal_any_density`         |
| `KAL`     | `ProgPopGen.fixation_limit`                                |
| `ILENE`   | `EvoGraph.isothermal_fixation_single`                      |
| `ALEXIS`  | `AutoresearchKeldysh.laplace_admissible`                   |
| `AURELIA` | `ProgPopGen.Price.fisher_haploid_nondecreasing`            |

`ALIX` rests on upstream openai/math `universal_energy_minimum` (AI-generated, not peer reviewed);
everything is conditional on the fidelity of the definitions it uses.
-/

namespace Acronymes

section Lattice

open OAI.AtomicTriangular TriangularDensity Filter Topology Set
open scoped Pointwise

/-- **A** **L**attice **I**s e**X**tremal.

At every density `ρ > 0` the rescaled triangular lattice `ρ^{-1/2} A` is locally finite, has density
`ρ`, and its lower energy is `≤` that of every locally finite density-`ρ` configuration, for every
admissible (completely monotone in `r²`) potential `h`. Re-export of
`TriangularDensity.triangular_optimal_any_density` (conditional on upstream). -/
theorem ALIX (h : ℝ → ℝ) (hh : AdmissiblePotential h) {ρ : ℝ} (hρ : 0 < ρ) :
    LocallyFinite ((Real.sqrt ρ)⁻¹ • A) ∧ DensityRho ρ ((Real.sqrt ρ)⁻¹ • A) ∧
      ∀ C : Set Plane, LocallyFinite C → DensityRho ρ C → energy h ((Real.sqrt ρ)⁻¹ • A) ≤ energy h C :=
  triangular_optimal_any_density h hh hρ

example : @ALIX = @triangular_optimal_any_density := rfl

end Lattice

section Absorption

open Filter Topology ProgPopGen

/-- **K**olmogorov **A**bsorption **L**imit.

For a stochastic kernel on `{0,...,N}` with absorbing ends, whose `n`-step kernel is the
Chapman–Kolmogorov power `kPow P n`: if `h` is interior-harmonic with `h 0 = 0`, `h N = 1` and the
one-step variance of `h` is positive at every interior state, then `P^n(i,N) → h i` and
`P^n(i,0) → 1 - h i`. Re-export of `ProgPopGen.fixation_limit`. -/
theorem KAL {N : ℕ} {P : Fin (N + 1) → Fin (N + 1) → ℝ} (hP : AbsorbingChain P) (hN : 0 < N)
    {h : Fin (N + 1) → ℝ} (hh : InteriorHarmonic P h) (h0 : h 0 = 0) (h1 : h (Fin.last N) = 1)
    (hvar : ∀ k : Fin (N + 1), 0 < (k : ℕ) → (k : ℕ) < N → 0 < ∑ j, P k j * (h j - h k) ^ 2)
    (i : Fin (N + 1)) :
    Tendsto (fun n => kPow P n i (Fin.last N)) atTop (𝓝 (h i)) ∧
    Tendsto (fun n => kPow P n i 0) atTop (𝓝 (1 - h i)) :=
  fixation_limit hP hN hh h0 h1 hvar i

example : @KAL = @fixation_limit := rfl

end Absorption

section Isothermal

open Finset Filter Topology EvoGraph

/-- **I**sothermal **L**aw: **E**very **N**ode **E**quivalent.

Birth–death updating with uniform selection on a strongly connected isothermal graph (`W` doubly
stochastic): a single mutant of fitness `r ≠ 1` placed at *any* node `v` fixes with limiting
probability `(1 - r⁻¹)/(1 - r^(-n))`, the same for every node and equal to Moran's value.
Re-export of `EvoGraph.isothermal_fixation_single`. -/
theorem ILENE {n : ℕ} {W : Fin n → Fin n → ℝ} {r : ℝ} (hn : 0 < n) (hr : 0 < r)
    (hr1 : r ≠ 1) (hW : Isothermal W) (hsc : StronglyConnected W) (v : Fin n) :
    Tendsto (fun t => sPow (bdK (fun _ => 1) W r) t {v} univ) atTop
      (𝓝 ((1 - r⁻¹) / (1 - r⁻¹ ^ n))) :=
  isothermal_fixation_single hn hr hr1 hW hsc v

example : @ILENE = @isothermal_fixation_single := rfl

end Isothermal

section Laplace

open MeasureTheory OAI.AtomicTriangular AutoresearchKeldysh

/-- **A**veraged **L**aplace **EX**ponentials **I**nherit **S**igns.

A positive mixture of decaying exponentials `fun t => ∫ e^{-t k(x)} m(x) dμ(x)` (with `k, m ≥ 0` and all
moments `∫ k^n e^{-c k} m dμ` finite for `c > 0`) is `AdmissiblePotential`: `C^∞` on `(0, ∞)`,
nonnegative, with alternating signs `(-1)^r g^{(r)} ≥ 0`, each exponential's signs passing to the
average. Re-export of `AutoresearchKeldysh.laplace_admissible`. -/
theorem ALEXIS {α : Type*} [MeasurableSpace α] {μ : Measure α} {k m : α → ℝ}
    (h : MixtureData μ k m) :
    AdmissiblePotential (fun t => ∫ x, Real.exp (-(t * k x)) * m x ∂μ) :=
  laplace_admissible h

example : @ALEXIS.{0} = @laplace_admissible.{0} := rfl

end Laplace

section Fisher

open ProgPopGen.Price

/-- **A**verage **U**nder **R**eplication: **E**volution **L**ifts **I**t, **A**lways.

Haploid selection with constant type fitnesses and no transmission bias, nonnegative abundances,
positive total abundance and positive mean fitness: the mean fitness does not decrease,
`wbar ≤ wbar'`. This is a special case of Fisher's fundamental theorem (haploid types, constant
fitnesses, no transmission bias), obtained from the exact identity `wbar' - wbar = Var(w)/wbar`
derived from the Price equation. Re-export of `ProgPopGen.Price.fisher_haploid_nondecreasing`. -/
theorem AURELIA {ι : Type*} (s : Finset ι) (n w : ι → ℝ)
    (hn : ∀ i ∈ s, 0 ≤ n i) (hN : 0 < ∑ i ∈ s, n i) (hW : 0 < ∑ i ∈ s, n i * w i) :
    wmean s n w ≤ wbarNext s n w :=
  fisher_haploid_nondecreasing s n w hn hN hW

example : @AURELIA.{0} = @fisher_haploid_nondecreasing.{0} := rfl

end Fisher

end Acronymes

#print axioms Acronymes.ALIX
#print axioms Acronymes.KAL
#print axioms Acronymes.ILENE
#print axioms Acronymes.ALEXIS
#print axioms Acronymes.AURELIA
