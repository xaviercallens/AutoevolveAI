import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.MeasureTheory.Measure.Haar.InnerProductSpace
import Mathlib.MeasureTheory.Function.LocallyIntegrable
import Mathlib.Analysis.Calculus.LineDeriv.IntegrationByParts
import Mathlib.Analysis.Calculus.BumpFunction.Normed
import Mathlib.Analysis.Calculus.BumpFunction.InnerProduct
import Mathlib.Analysis.SpecialFunctions.Gamma.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Topology.Instances.EReal.Lemmas

/-!
# The Sandier–Serfaty conjecture: a Lean *statement* (not a proof)

Programmes 2026-10-25, lane P1, stage S3. This file states, as Lean `Prop`s, the conjecture that the triangular
lattice minimizes the renormalized energy `W` of the planar Coulomb gas with a uniform neutralizing background
(Sandier–Serfaty 2012, arXiv:1011.4617v2, Conjecture 1, p.5), in two normalizations:

* `SandierSerfatyStatement` follows the openai/math manuscript "Triangular minimality for planar Coulomb
  renormalized energy" (2026-09-23), Section 1, eqs. (cutoffs), (admissible), (local-energy), (whole-energy),
  (triangular-lattice) and Theorem 1.1: electric fields `E`, `div E = 2π(ν_Λ − 1)`, `curl E = 0`, square cutoffs
  `K_R = [−R,R]²` of fixed boundary width, triangular lattice of covolume one.
* `SandierSerfatyOriginalStatement` (for every `m > 0`) follows SS2012 Definitions 1.1–1.2 (p.2–3) and Conjecture 1 literally:
  currents `j`, `curl j = 2π Σ δ_p − m`, `div j = 0`, ball cutoffs, `W(j) = limsup W(j, χ_{B_R}) / |B_R|`,
  triangular lattice `Λ_m` of covolume `2π/m`.
* `SandierSerfatyValueStatement` is the manuscript form with the explicit value
  `W(E_△) = π log(2√2 π / (√3 Γ(1/3)³))` (Bétermin–Sandier 2018, p.26 closed form; the identification of this
  number with the manuscript's `W(E_△)` is Tier L + Tier X, NOT formalized here).

NOTHING HERE IS PROVED ABOUT THE CONJECTURE. The proved lemmas only show that the definitions are not degenerate:

* `negPi_admissibleBg_iff` : with no charges, the field `E(x) = −π x` satisfies the weak equations
  `div E = 2π ν − b`, `curl E = 0` **iff** `b = 2π`. So the manuscript's admissible class is non-empty
  (`negPi_admissible`), and the degenerate variants "no background" (`b = 0`) and "wrong-sign background"
  (`b = −2π`) are detectably different (`negPi_not_admissible_noBackground`, `..._wrongSign`). The proof uses a
  bump test function with positive integral, so it also certifies that the class of test functions is not
  collapsed to `0` (a known trap: `ContDiff ℝ ⊤` means analytic in current Mathlib; we use `∞`).
* `negPi_hasLocalEnergy`, `competitor_nonvacuous` : the puncture-limit relation `HasLocalEnergy` is satisfiable
  (for that field and any smooth compactly supported cutoff), so for every cutoff family the competitor clause of
  `SandierSerfatyStatement` constrains at least one competitor. (With `Λ = ∅` the renormalization term
  `π log η Σ χ(p)` is zero, so its sign is checked only by hand: Tier C, see the fidelity note.)
* `exists_squareCutoffFamily`, `exists_ballCutoffFamily` : the manuscript's square cutoff class (eq. (cutoffs))
  and the smooth version of SS2012's ball cutoff class ((1.3)) are non-empty (explicit products / radial profiles
  of `Real.smoothTransition`, gradient bound uniform in `R`), so the `∀ χ` in the statements is not vacuous.
* `triBasis_covolume`, `ssBasis_covolume` : the triangular bases have covolume `1` resp. `2π/m`.

NOT proved (honest gaps of the non-vacuity check): that `triLattice` is locally finite with bounded density, that
any field with charges is admissible (the `∑ᶠ p ∈ Λ, φ p` term is only exercised with `Λ = ∅`), and that a
`Λ_△`-periodic admissible field exists (this needs the torus Green function, absent from Mathlib).
Planted `sorry` / custom-axiom proofs of `SandierSerfatyStatement` live in `SandierSerfatyStatementControls.lean`.

Encoding choices (see `results/programmes/2026-10-25/P1/STATEMENT_FIDELITY.md` for the full Tier C comparison):
distributional equations are written in weak form against all `C_c^∞` test functions; the puncture limit is a
relation (`HasLocalEnergy`, with integrability on the punctured domain), never `limUnder`, so no junk value can
enter; `W` is an `EReal`-valued `limsup`, so `±∞` are allowed as in the manuscript; the triangular minimizer is an
existential witness (a lattice-periodic admissible field with charges exactly on the triangular lattice and finite
energy), because Mathlib has no periodic Green function on a torus with which to define `E_△ = −∇h_△` directly.
-/

namespace ProgSandierSerfaty

open MeasureTheory Filter Topology Set
open scoped ContDiff

/-- The plane `ℝ²` with its Euclidean norm and Lebesgue measure. -/
abbrev Plane := EuclideanSpace ℝ (Fin 2)

/-- Partial derivative `∂ᵢ φ (x)`. -/
noncomputable def pd (i : Fin 2) (φ : Plane → ℝ) (x : Plane) : ℝ :=
  fderiv ℝ φ x (EuclideanSpace.single i 1)

/-- Smooth (`C^∞`, not analytic) compactly supported real test functions. -/
def IsTestFn (φ : Plane → ℝ) : Prop := ContDiff ℝ ∞ φ ∧ HasCompactSupport φ

/-- Locally finite point set (a `Set`, so every point is simple). SS2012 says "discrete"; for the closed-set
conditions used here locally finite is the intended meaning (manuscript: "locally finite and simple"). -/
def LocFinite (Λ : Set Plane) : Prop := ∀ K : Set Plane, IsCompact K → (Λ ∩ K).Finite

/-- `sup_{R>1} ν_Λ(B_R)/|B_R| < ∞` (manuscript eq. (admissible), SS2012 (1.2) up to the factor `2π`). -/
def DensityBounded (Λ : Set Plane) : Prop :=
  ∃ C : ℝ, ∀ R : ℝ, 1 < R → ((Λ ∩ Metric.ball 0 R).ncard : ℝ) ≤ C * (Real.pi * R ^ 2)

/-! ## Electric-field normalization (the manuscript) -/

/-- Weak form of `div E = 2π ν_Λ − b` (`ν_Λ = Σ_{p∈Λ} δ_p`): for every test function,
`−∫ E·∇φ = 2π Σ_p φ(p) − b ∫ φ`. -/
def WeakDivE (b : ℝ) (Λ : Set Plane) (E : Plane → Plane) : Prop :=
  ∀ φ : Plane → ℝ, IsTestFn φ →
    -(∫ x, (E x 0 * pd 0 φ x + E x 1 * pd 1 φ x)) = 2 * Real.pi * (∑ᶠ p ∈ Λ, φ p) - b * ∫ x, φ x

/-- Weak form of `curl E = ∂₀E₁ − ∂₁E₀ = 0`: `∫ (E₀ ∂₁φ − E₁ ∂₀φ) = 0` for every test function. -/
def WeakCurlFree (E : Plane → Plane) : Prop :=
  ∀ φ : Plane → ℝ, IsTestFn φ → ∫ x, (E x 0 * pd 1 φ x - E x 1 * pd 0 φ x) = 0

/-- Admissible fields with background `b` (the manuscript's class `𝒜₁` is `b = 2π`). -/
def AdmissibleBg (b : ℝ) (Λ : Set Plane) (E : Plane → Plane) : Prop :=
  LocFinite Λ ∧ DensityBounded Λ ∧ LocallyIntegrable E volume ∧ WeakDivE b Λ E ∧ WeakCurlFree E

/-- The manuscript's admissible class `𝒜₁`: `div E = 2π(ν_Λ − 1)`, `curl E = 0`, bounded density. -/
def Admissible (Λ : Set Plane) (E : Plane → Plane) : Prop := AdmissibleBg (2 * Real.pi) Λ E

/-- `ℝ² ∖ ⋃_{p∈Λ} B(p, η)`. -/
def punctured (Λ : Set Plane) (η : ℝ) : Set Plane := (⋃ p ∈ Λ, Metric.ball p η)ᶜ

/-- The bracket in manuscript eq. (local-energy) / SS2012 (1.7):
`½ ∫_{ℝ² ∖ ⋃ B(p,η)} χ |E|² + π log η Σ_p χ(p)`. -/
noncomputable def localEnergyAt (Λ : Set Plane) (E : Plane → Plane) (χ : Plane → ℝ) (η : ℝ) : ℝ :=
  (1 / 2) * (∫ x in punctured Λ η, χ x * ‖E x‖ ^ 2) + Real.pi * Real.log η * ∑ᶠ p ∈ Λ, χ p

/-- `W(E, χ) = w`: the puncture limit `η ↓ 0` exists and equals `w`, with the integral genuinely convergent on the
punctured domain for small `η` (so the Bochner integral never returns its junk value `0`). -/
def HasLocalEnergy (Λ : Set Plane) (E : Plane → Plane) (χ : Plane → ℝ) (w : ℝ) : Prop :=
  (∀ᶠ η in 𝓝[>] (0 : ℝ), IntegrableOn (fun x => χ x * ‖E x‖ ^ 2) (punctured Λ η)) ∧
    Tendsto (localEnergyAt Λ E χ) (𝓝[>] 0) (𝓝 w)

/-- The closed square `K_R = [−R, R]²`. -/
def sq (R : ℝ) : Set Plane := {x | |x 0| ≤ R ∧ |x 1| ≤ R}

/-- Manuscript eq. (cutoffs): `χ_R ∈ C_c^∞`, `0 ≤ χ_R ≤ 1`, `supp χ_R ⊂ K_R`, `χ_R = 1` on `K_{R−1}`,
`sup_{R>1} ‖∇χ_R‖_∞ < ∞`. -/
def IsSquareCutoffFamily (χ : ℝ → Plane → ℝ) : Prop :=
  (∀ R : ℝ, 1 < R →
      ContDiff ℝ ∞ (χ R) ∧ HasCompactSupport (χ R) ∧ (∀ x, 0 ≤ χ R x ∧ χ R x ≤ 1) ∧
        tsupport (χ R) ⊆ sq R ∧ ∀ x ∈ sq (R - 1), χ R x = 1) ∧
    ∃ C : ℝ, ∀ R : ℝ, 1 < R → ∀ x, ‖fderiv ℝ (χ R) x‖ ≤ C

/-- Manuscript eq. (whole-energy): `W(E) = limsup_{R→∞} W(E, χ_R) / |K_R|`, `|K_R| = 4R²`, in `EReal`
(both infinite values allowed). `w R` is the value of `W(E, χ_R)`. -/
noncomputable def WSq (w : ℝ → ℝ) : EReal :=
  limsup (fun R : ℝ => ((w R / (4 * R ^ 2) : ℝ) : EReal)) atTop

/-- `Λ`-periodicity (almost everywhere) of a field. -/
def IsPeriodic (Λ : Set Plane) (E : Plane → Plane) : Prop :=
  ∀ v ∈ Λ, ∀ᵐ x ∂(volume : Measure Plane), E (x + v) = E x

/-- Scale `√(2/√3)` of the covolume-one triangular lattice. -/
noncomputable def triScale : ℝ := Real.sqrt (2 / Real.sqrt 3)

/-- Basis vectors `(1, 0)` and `(1/2, √3/2)`. -/
noncomputable def e₁ : Plane := !₂[1, 0]
noncomputable def e₂ : Plane := !₂[1 / 2, Real.sqrt 3 / 2]

/-- Manuscript eq. (triangular-lattice): `Λ_△ = √(2/√3) (ℤ(1,0) + ℤ(1/2, √3/2))`. -/
def triLattice : Set Plane :=
  {x | ∃ m n : ℤ, x = triScale • ((m : ℝ) • e₁ + (n : ℝ) • e₂)}

/-- **The Sandier–Serfaty conjecture, manuscript normalization (Theorem 1.1 of the openai/math manuscript).**
The cutoff class is non-empty, and there is one `Λ_△`-periodic admissible field `E₀` with charges exactly at
`Λ_△` (the role of `E_△ = −∇h_△`) such that, for every admissible cutoff family, `W(E₀)` is finite and
`W(E) ≥ W(E₀)` for every admissible `E` (every point set `Λ`). Not proved here. -/
def SandierSerfatyStatement : Prop :=
  (∃ χ, IsSquareCutoffFamily χ) ∧
    ∃ E₀ : Plane → Plane, Admissible triLattice E₀ ∧ IsPeriodic triLattice E₀ ∧
      ∀ χ : ℝ → Plane → ℝ, IsSquareCutoffFamily χ →
        ∃ w₀ : ℝ → ℝ, (∀ R : ℝ, 1 < R → HasLocalEnergy triLattice E₀ (χ R) (w₀ R)) ∧
          WSq w₀ ≠ ⊤ ∧ WSq w₀ ≠ ⊥ ∧
          ∀ (Λ : Set Plane) (E : Plane → Plane) (w : ℝ → ℝ), Admissible Λ E →
            (∀ R : ℝ, 1 < R → HasLocalEnergy Λ E (χ R) (w R)) → WSq w₀ ≤ WSq w

/-- `π log(2√2 π / (√3 Γ(1/3)³)) ≈ −4.1504128` (Bétermin–Sandier 2018, p.26, transcribed in the manuscript
normalization; numerical identification with `W(E_△)` checked in S2, Tier L + X). -/
noncomputable def wTriClosedForm : ℝ :=
  Real.pi * Real.log (2 * Real.sqrt 2 * Real.pi / (Real.sqrt 3 * Real.Gamma (1 / 3) ^ 3))

/-- **Explicit-value form.** `inf_{𝒜₁} W = π log(2√2 π / (√3 Γ(1/3)³))`, the infimum attained by a
`Λ_△`-periodic field with charges at `Λ_△`. Not proved here. -/
def SandierSerfatyValueStatement : Prop :=
  (∃ χ, IsSquareCutoffFamily χ) ∧
    ∃ E₀ : Plane → Plane, Admissible triLattice E₀ ∧ IsPeriodic triLattice E₀ ∧
      ∀ χ : ℝ → Plane → ℝ, IsSquareCutoffFamily χ →
        (∃ w₀ : ℝ → ℝ, (∀ R : ℝ, 1 < R → HasLocalEnergy triLattice E₀ (χ R) (w₀ R)) ∧
            WSq w₀ = (wTriClosedForm : EReal)) ∧
          ∀ (Λ : Set Plane) (E : Plane → Plane) (w : ℝ → ℝ), Admissible Λ E →
            (∀ R : ℝ, 1 < R → HasLocalEnergy Λ E (χ R) (w R)) → (wTriClosedForm : EReal) ≤ WSq w

/-! ## Current normalization (Sandier–Serfaty 2012, Definitions 1.1–1.2, Conjecture 1) -/

/-- SS2012 (1.1): `div j = 0` weakly, i.e. `∫ j·∇φ = 0`. -/
def WeakDivFree (j : Plane → Plane) : Prop :=
  ∀ φ : Plane → ℝ, IsTestFn φ → ∫ x, (j x 0 * pd 0 φ x + j x 1 * pd 1 φ x) = 0

/-- SS2012 (1.1): `curl j = ∂₀j₁ − ∂₁j₀ = ν − m` with `ν = 2π Σ_{p∈Λ} δ_p`, weakly:
`∫ (j₀ ∂₁φ − j₁ ∂₀φ) = 2π Σ_p φ(p) − m ∫ φ`. -/
def WeakCurlSS (m : ℝ) (Λ : Set Plane) (j : Plane → Plane) : Prop :=
  ∀ φ : Plane → ℝ, IsTestFn φ →
    ∫ x, (j x 0 * pd 1 φ x - j x 1 * pd 0 φ x) = 2 * Real.pi * (∑ᶠ p ∈ Λ, φ p) - m * ∫ x, φ x

/-- SS2012 Definition 1.1, the class `A_m`. -/
def AdmissibleSS (m : ℝ) (Λ : Set Plane) (j : Plane → Plane) : Prop :=
  LocFinite Λ ∧ DensityBounded Λ ∧ LocallyIntegrable j volume ∧ WeakDivFree j ∧ WeakCurlSS m Λ j

/-- SS2012 (1.3) for balls: `|∇χ| ≤ C`, `Supp χ ⊂ B_R`, `χ = 1` where `d(x, B_Rᶜ) ≥ 1` (i.e. on `B̄_{R−1}`),
`0 ≤ χ ≤ 1`; we additionally take `χ` smooth (SS Theorem 1(1): the value does not depend on the admissible
cutoff, so restricting to smooth cutoffs does not change `W`; Tier L). -/
def IsBallCutoffFamily (χ : ℝ → Plane → ℝ) : Prop :=
  (∀ R : ℝ, 1 < R →
      ContDiff ℝ ∞ (χ R) ∧ HasCompactSupport (χ R) ∧ (∀ x, 0 ≤ χ R x ∧ χ R x ≤ 1) ∧
        tsupport (χ R) ⊆ Metric.ball 0 R ∧ ∀ x ∈ Metric.closedBall (0 : Plane) (R - 1), χ R x = 1) ∧
    ∃ C : ℝ, ∀ R : ℝ, 1 < R → ∀ x, ‖fderiv ℝ (χ R) x‖ ≤ C

/-- SS2012 (1.6): `W(j) = limsup_{R→∞} W(j, χ_{B_R}) / |B_R|`, `|B_R| = π R²`. -/
noncomputable def WBall (w : ℝ → ℝ) : EReal :=
  limsup (fun R : ℝ => ((w R / (Real.pi * R ^ 2) : ℝ) : EReal)) atTop

/-- SS2012 Theorem 2: `Λ_m = √(4π/(m√3)) ((1,0)ℤ ⊕ (1/2, √3/2)ℤ)`, covolume `2π/m`. -/
def ssTriLattice (m : ℝ) : Set Plane :=
  {x | ∃ a b : ℤ, x = Real.sqrt (4 * Real.pi / (m * Real.sqrt 3)) • ((a : ℝ) • e₁ + (b : ℝ) • e₂)}

/-- **SS2012 Conjecture 1** (`W(Λ_m) = min_{A_m} W`), with `W(Λ_m)` realised by a `Λ_m`-periodic field in
`A_m` with charges at `Λ_m` (SS2012 Lemma 1.3 / Prop. 3.1: the mean-zero periodic `j_Λ` minimises among periodic
fields, so a periodic minimiser exists iff `j_Λ` is one; Tier L), for every background `m > 0`.
Not proved here. -/
def SandierSerfatyOriginalStatement : Prop :=
  (∃ χ, IsBallCutoffFamily χ) ∧
    ∀ m : ℝ, 0 < m →
      ∃ j₀ : Plane → Plane, AdmissibleSS m (ssTriLattice m) j₀ ∧ IsPeriodic (ssTriLattice m) j₀ ∧
        ∀ χ : ℝ → Plane → ℝ, IsBallCutoffFamily χ →
          ∃ w₀ : ℝ → ℝ, (∀ R : ℝ, 1 < R → HasLocalEnergy (ssTriLattice m) j₀ (χ R) (w₀ R)) ∧
            WBall w₀ ≠ ⊤ ∧ WBall w₀ ≠ ⊥ ∧
            ∀ (Λ : Set Plane) (j : Plane → Plane) (w : ℝ → ℝ), AdmissibleSS m Λ j →
              (∀ R : ℝ, 1 < R → HasLocalEnergy Λ j (χ R) (w R)) → WBall w₀ ≤ WBall w

/-! ## Proved non-degeneracy lemmas (these do NOT bear on the truth of the conjecture) -/

section NonDegeneracy

/-- The field `x ↦ −π x` (no charges): `div = −2π`, `curl = 0`. -/
noncomputable def negPi : Plane → Plane := fun x => (-Real.pi) • x

lemma negPi_apply (x : Plane) (i : Fin 2) : negPi x i = -Real.pi * x i := by
  simp [negPi]

lemma continuous_negPi : Continuous negPi := by
  unfold negPi; fun_prop

lemma continuous_coord (i : Fin 2) : Continuous (fun x : Plane => x i) :=
  PiLp.continuous_apply 2 _ i

lemma contDiff_coord (i : Fin 2) : ContDiff ℝ ∞ (fun x : Plane => x i) :=
  (EuclideanSpace.proj (𝕜 := ℝ) i).contDiff

lemma fderiv_coord (i : Fin 2) (x : Plane) :
    fderiv ℝ (fun y : Plane => y i) x = EuclideanSpace.proj (𝕜 := ℝ) i :=
  (EuclideanSpace.proj (𝕜 := ℝ) i).fderiv

lemma hcs_mul_left {f g : Plane → ℝ} (hg : HasCompactSupport g) :
    HasCompactSupport (fun x => f x * g x) :=
  hg.mul_left (f := f)

lemma hcs_mul_right {f g : Plane → ℝ} (hf : HasCompactSupport f) :
    HasCompactSupport (fun x => f x * g x) :=
  hf.mul_right (f' := g)

lemma IsTestFn.continuous_pd {φ : Plane → ℝ} (hφ : IsTestFn φ) (k : Fin 2) :
    Continuous (pd k φ) :=
  (hφ.1.continuous_fderiv (by simp)).clm_apply continuous_const

lemma IsTestFn.hasCompactSupport_pd {φ : Plane → ℝ} (hφ : IsTestFn φ) (k : Fin 2) :
    HasCompactSupport (pd k φ) := by
  unfold pd
  exact hφ.2.fderiv_apply (𝕜 := ℝ) _

lemma integrable_coord_pd {φ : Plane → ℝ} (hφ : IsTestFn φ) (i k : Fin 2) :
    Integrable (fun x : Plane => x i * pd k φ x) :=
  ((continuous_coord i).mul (hφ.continuous_pd k)).integrable_of_hasCompactSupport
    (hcs_mul_left (hφ.hasCompactSupport_pd k))

/-- Integration by parts against a coordinate: `∫ xᵢ ∂ₖφ = −δᵢₖ ∫ φ`. -/
lemma ibp_coord {φ : Plane → ℝ} (hφ : IsTestFn φ) (i k : Fin 2) :
    ∫ x : Plane, x i * pd k φ x =
      -∫ x : Plane, (EuclideanSpace.single k (1 : ℝ) : Plane) i * φ x := by
  have hφc : Continuous φ := hφ.1.continuous
  have key := integral_mul_fderiv_eq_neg_fderiv_mul_of_integrable (μ := (volume : Measure Plane))
    (f := fun y : Plane => y i) (g := φ) (v := EuclideanSpace.single k (1 : ℝ)) ?_ ?_ ?_ ?_ ?_
  · simpa only [pd, fderiv_coord, EuclideanSpace.coe_proj] using key
  · simp only [fderiv_coord, EuclideanSpace.coe_proj]
    exact (continuous_const.mul hφc).integrable_of_hasCompactSupport (hcs_mul_left hφ.2)
  · exact integrable_coord_pd hφ i k
  · exact ((continuous_coord i).mul hφc).integrable_of_hasCompactSupport (hcs_mul_left hφ.2)
  · intro x _
    exact (contDiff_coord i).differentiable (by simp) x
  · intro x _
    exact hφ.1.differentiable (by simp) x

/-- For every test function, `−∫ (−π x)·∇φ = −2π ∫ φ`, i.e. `div(−π x) = −2π` weakly. -/
lemma negPi_div_pairing {φ : Plane → ℝ} (hφ : IsTestFn φ) :
    -(∫ x, (negPi x 0 * pd 0 φ x + negPi x 1 * pd 1 φ x)) = -(2 * Real.pi * ∫ x, φ x) := by
  have h0 := ibp_coord hφ 0 0
  have h1 := ibp_coord hφ 1 1
  simp only [negPi_apply, mul_assoc]
  rw [integral_add ((integrable_coord_pd hφ 0 0).const_mul _) ((integrable_coord_pd hφ 1 1).const_mul _),
    integral_const_mul, integral_const_mul, h0, h1]
  simp
  ring

/-- A fixed bump test function (radii 1 < 2 about the origin). -/
noncomputable def bump : ContDiffBump (0 : Plane) := ⟨1, 2, one_pos, one_lt_two⟩

lemma bump_isTestFn : IsTestFn (bump : Plane → ℝ) := ⟨bump.contDiff, bump.hasCompactSupport⟩

/-- The bump has positive integral, so test functions are not collapsed to `0`. -/
lemma bump_integral_pos : 0 < ∫ x, (bump : Plane → ℝ) x := bump.integral_pos

theorem negPi_weakDivE_iff (b : ℝ) : WeakDivE b ∅ negPi ↔ b = 2 * Real.pi := by
  constructor
  · intro h
    have hb := h _ bump_isTestFn
    rw [negPi_div_pairing bump_isTestFn] at hb
    simp only [finsum_mem_empty, mul_zero, zero_sub] at hb
    have hpos := bump_integral_pos
    have hz : (b - 2 * Real.pi) * ∫ x, (bump : Plane → ℝ) x = 0 := by linarith
    rcases mul_eq_zero.1 hz with h' | h'
    · linarith
    · linarith
  · rintro rfl φ hφ
    rw [negPi_div_pairing hφ]
    simp

theorem negPi_weakCurlFree : WeakCurlFree negPi := by
  intro φ hφ
  have h01 := ibp_coord hφ 0 1
  have h10 := ibp_coord hφ 1 0
  simp only [negPi_apply, mul_assoc]
  rw [integral_sub ((integrable_coord_pd hφ 0 1).const_mul _) ((integrable_coord_pd hφ 1 0).const_mul _),
    integral_const_mul, integral_const_mul, h01, h10]
  simp

/-- **Positive control / non-vacuity.** With no charges, `−π x` is admissible with background `b` iff
`b = 2π`. -/
theorem negPi_admissibleBg_iff (b : ℝ) : AdmissibleBg b ∅ negPi ↔ b = 2 * Real.pi := by
  constructor
  · intro h
    exact (negPi_weakDivE_iff b).1 h.2.2.2.1
  · intro hb
    refine ⟨fun K _ => by simp, ⟨0, fun R _ => by simp⟩, continuous_negPi.locallyIntegrable,
      (negPi_weakDivE_iff b).2 hb, negPi_weakCurlFree⟩

/-- The manuscript's class `𝒜₁` is non-empty. -/
theorem negPi_admissible : Admissible ∅ negPi := (negPi_admissibleBg_iff _).2 rfl

/-- **Negative control.** Dropping the neutralizing background (`div E = 2π ν`) is detectably different. -/
theorem negPi_not_admissible_noBackground : ¬ AdmissibleBg 0 ∅ negPi := by
  rw [negPi_admissibleBg_iff]
  have := Real.pi_pos
  intro h
  linarith

/-- **Negative control.** A wrong-sign background (`div E = 2π(ν + 1)`) is detectably different. -/
theorem negPi_not_admissible_wrongSign : ¬ AdmissibleBg (-(2 * Real.pi)) ∅ negPi := by
  rw [negPi_admissibleBg_iff]
  have := Real.pi_pos
  intro h
  linarith

/-- The puncture-limit relation is satisfiable: for `Λ = ∅` there is nothing to puncture. -/
theorem negPi_hasLocalEnergy {χ : Plane → ℝ} (hχ : Continuous χ) (hs : HasCompactSupport χ) :
    HasLocalEnergy ∅ negPi χ ((1 / 2) * ∫ x, χ x * ‖negPi x‖ ^ 2) := by
  have hp : ∀ η : ℝ, punctured (∅ : Set Plane) η = univ := by
    intro η
    simp [punctured]
  refine ⟨Filter.Eventually.of_forall fun η => ?_, ?_⟩
  · rw [hp]
    have hc : Continuous fun x => χ x * ‖negPi x‖ ^ 2 := hχ.mul (continuous_negPi.norm.pow 2)
    exact (hc.integrable_of_hasCompactSupport (hcs_mul_right hs)).integrableOn
  · have h : localEnergyAt ∅ negPi χ = fun _ => (1 / 2) * ∫ x, χ x * ‖negPi x‖ ^ 2 := by
      funext η
      simp [localEnergyAt, hp]
    rw [h]
    exact tendsto_const_nhds

/-- **Non-vacuity of the competitor quantifier.** For every manuscript cutoff family, the competitor hypotheses
of `SandierSerfatyStatement` (`Admissible Λ E` and `HasLocalEnergy` for all `R > 1`) are met by `(∅, −π x, w)`
for some `w`, so the conclusion `W(E₀) ≤ W(E)` constrains at least one competitor. -/
theorem competitor_nonvacuous {χ : ℝ → Plane → ℝ} (hχ : IsSquareCutoffFamily χ) :
    ∃ (Λ : Set Plane) (E : Plane → Plane) (w : ℝ → ℝ), Admissible Λ E ∧
      ∀ R : ℝ, 1 < R → HasLocalEnergy Λ E (χ R) (w R) :=
  ⟨∅, negPi, fun R => (1 / 2) * ∫ x, χ R x * ‖negPi x‖ ^ 2, negPi_admissible, fun R hR =>
    negPi_hasLocalEnergy ((hχ.1 R hR).1.continuous) (hχ.1 R hR).2.1⟩

lemma e₁_zero : e₁ 0 = 1 := by simp [e₁]
lemma e₁_one : e₁ 1 = 0 := by simp [e₁]
lemma e₂_zero : e₂ 0 = 1 / 2 := by simp [e₂]
lemma e₂_one : e₂ 1 = Real.sqrt 3 / 2 := by simp [e₂]

/-- The manuscript's triangular basis has covolume one. -/
theorem triBasis_covolume : triScale ^ 2 * (e₁ 0 * e₂ 1 - e₁ 1 * e₂ 0) = 1 := by
  have h3 : 0 < Real.sqrt 3 := Real.sqrt_pos.2 (by norm_num)
  have hs : triScale ^ 2 = 2 / Real.sqrt 3 := Real.sq_sqrt (by positivity)
  rw [hs, e₁_zero, e₁_one, e₂_zero, e₂_one]
  field_simp
  ring

/-- SS2012's `Λ_m` has covolume `2π/m`. -/
theorem ssBasis_covolume {m : ℝ} (hm : 0 < m) :
    Real.sqrt (4 * Real.pi / (m * Real.sqrt 3)) ^ 2 * (e₁ 0 * e₂ 1 - e₁ 1 * e₂ 0) = 2 * Real.pi / m := by
  have h3 : 0 < Real.sqrt 3 := Real.sqrt_pos.2 (by norm_num)
  have hs : Real.sqrt (4 * Real.pi / (m * Real.sqrt 3)) ^ 2 = 4 * Real.pi / (m * Real.sqrt 3) :=
    Real.sq_sqrt (by positivity)
  rw [hs, e₁_zero, e₁_one, e₂_zero, e₂_one]
  field_simp
  ring

/-! ### The manuscript's cutoff class (eq. (cutoffs)) is non-empty -/

/-- `s(t) = s(clamp₀₁ t)` for the smooth transition `s`. -/
lemma st_clamp (t : ℝ) : Real.smoothTransition t = Real.smoothTransition (max (min t 1) 0) := by
  rcases le_total t 0 with h | h
  · rw [Real.smoothTransition.zero_of_nonpos h, Real.smoothTransition.zero_of_nonpos]
    exact max_le (min_le_of_left_le h) le_rfl
  · rcases le_total t 1 with h' | h'
    · rw [min_eq_left h', max_eq_left h]
    · rw [Real.smoothTransition.one_of_one_le h', min_eq_right h', max_eq_left zero_le_one,
        Real.smoothTransition.one_of_one_le le_rfl]

/-- The smooth transition is globally Lipschitz. -/
lemma st_lipschitz : ∃ K : NNReal, LipschitzWith K Real.smoothTransition := by
  obtain ⟨K, hK⟩ := (Real.smoothTransition.contDiff (n := 1)).contDiffOn.exists_lipschitzOnWith
    (s := Icc (0 : ℝ) 1) (by simp) (convex_Icc 0 1) isCompact_Icc
  refine ⟨K, LipschitzWith.of_dist_le_mul fun t u => ?_⟩
  rw [st_clamp t, st_clamp u]
  have hc : ∀ v : ℝ, max (min v 1) 0 ∈ Icc (0 : ℝ) 1 :=
    fun v => ⟨le_max_right _ _, max_le (min_le_right _ _) zero_le_one⟩
  calc dist (Real.smoothTransition (max (min t 1) 0)) (Real.smoothTransition (max (min u 1) 0))
      ≤ K * dist (max (min t 1) 0) (max (min u 1) 0) := hK.dist_le_mul _ (hc t) _ (hc u)
    _ ≤ K * dist t u := by
        gcongr
        rw [Real.dist_eq, Real.dist_eq]
        calc |max (min t 1) 0 - max (min u 1) 0| ≤ |min t 1 - min u 1| := abs_max_sub_max_le_abs _ _ _
          _ ≤ max |t - u| |1 - 1| := abs_min_sub_min_le_max _ _ _ _
          _ = |t - u| := by simp

lemma st_abs_le_one (t : ℝ) : |Real.smoothTransition t| ≤ 1 :=
  abs_le.2 ⟨by linarith [Real.smoothTransition.nonneg t], Real.smoothTransition.le_one t⟩

/-- One factor `x ↦ s(R + σ xᵢ)`, `|σ| = 1`, is `K`-Lipschitz. -/
lemma factor_lipschitz {K : NNReal} (hK : LipschitzWith K Real.smoothTransition) (R σ : ℝ) (hσ : |σ| = 1)
    (i : Fin 2) : LipschitzWith K (fun x : Plane => Real.smoothTransition (R + σ * x i)) := by
  refine LipschitzWith.of_dist_le_mul fun x y => ?_
  calc dist (Real.smoothTransition (R + σ * x i)) (Real.smoothTransition (R + σ * y i))
      ≤ K * dist (R + σ * x i) (R + σ * y i) := hK.dist_le_mul _ _
    _ ≤ K * dist x y := by
        gcongr
        rw [Real.dist_eq, show R + σ * x i - (R + σ * y i) = σ * (x i - y i) by ring, abs_mul, hσ,
          one_mul, ← Real.dist_eq]
        exact PiLp.dist_apply_le x y i

/-- Product of two Lipschitz functions with values in `[−1, 1]`. -/
lemma lipschitz_mul_of_abs_le_one {f g : Plane → ℝ} {Kf Kg : NNReal} (hf : LipschitzWith Kf f)
    (hg : LipschitzWith Kg g) (hf1 : ∀ x, |f x| ≤ 1) (hg1 : ∀ x, |g x| ≤ 1) :
    LipschitzWith (Kf + Kg) (fun x => f x * g x) := by
  refine LipschitzWith.of_dist_le_mul fun x y => ?_
  have h1 := hf.dist_le_mul x y
  have h2 := hg.dist_le_mul x y
  rw [Real.dist_eq] at h1 h2 ⊢
  have e : f x * g x - f y * g y = f x * (g x - g y) + g y * (f x - f y) := by ring
  rw [e]
  calc |f x * (g x - g y) + g y * (f x - f y)| ≤ |f x| * |g x - g y| + |g y| * |f x - f y| := by
        rw [← abs_mul, ← abs_mul]
        exact abs_add_le _ _
    _ ≤ 1 * (Kg * dist x y) + 1 * (Kf * dist x y) :=
        add_le_add (mul_le_mul (hf1 x) h2 (abs_nonneg _) zero_le_one)
          (mul_le_mul (hg1 y) h1 (abs_nonneg _) zero_le_one)
    _ = ((Kf + Kg : NNReal) : ℝ) * dist x y := by push_cast; ring

/-- `χ_R(x) = s(R − x₀) s(R + x₀) s(R − x₁) s(R + x₁)`. -/
noncomputable def sqCutoff (R : ℝ) (x : Plane) : ℝ :=
  Real.smoothTransition (R + (-1) * x 0) * Real.smoothTransition (R + 1 * x 0) *
    Real.smoothTransition (R + (-1) * x 1) * Real.smoothTransition (R + 1 * x 1)

lemma isClosed_sq (R : ℝ) : IsClosed (sq R) :=
  (isClosed_le (continuous_abs.comp (continuous_coord 0)) continuous_const).inter
    (isClosed_le (continuous_abs.comp (continuous_coord 1)) continuous_const)

lemma isCompact_sq {R : ℝ} (hR : 0 ≤ R) : IsCompact (sq R) := by
  have hsub : sq R ⊆ Metric.closedBall (0 : Plane) (2 * R) := by
    intro x hx
    obtain ⟨h0, h1⟩ := hx
    rw [mem_closedBall_zero_iff, EuclideanSpace.norm_eq, Fin.sum_univ_two, Real.norm_eq_abs,
      Real.norm_eq_abs]
    calc Real.sqrt (|x 0| ^ 2 + |x 1| ^ 2) ≤ Real.sqrt ((2 * R) ^ 2) := by
          apply Real.sqrt_le_sqrt
          nlinarith [abs_nonneg (x 0), abs_nonneg (x 1)]
      _ = 2 * R := Real.sqrt_sq (by linarith)
  exact Metric.isCompact_of_isClosed_isBounded (isClosed_sq R) (Metric.isBounded_closedBall.subset hsub)

lemma mul_le_one_aux {a b : ℝ} (ha : a ≤ 1) (hb : 0 ≤ b) (hb1 : b ≤ 1) : a * b ≤ 1 := by
  nlinarith

lemma sqCutoff_eq_zero {R : ℝ} {x : Plane} (hx : x ∉ sq R) : sqCutoff R x = 0 := by
  simp only [sq, Set.mem_ofPred_eq, not_and_or, not_le] at hx
  unfold sqCutoff
  rcases hx with h | h
  · rcases lt_abs.1 h with h' | h'
    · rw [Real.smoothTransition.zero_of_nonpos (x := R + (-1) * x 0) (by linarith)]; ring
    · rw [Real.smoothTransition.zero_of_nonpos (x := R + 1 * x 0) (by linarith)]; ring
  · rcases lt_abs.1 h with h' | h'
    · rw [Real.smoothTransition.zero_of_nonpos (x := R + (-1) * x 1) (by linarith)]; ring
    · rw [Real.smoothTransition.zero_of_nonpos (x := R + 1 * x 1) (by linarith)]; ring

/-- **Non-vacuity of `∀ χ`.** The manuscript's cutoff class (eq. (cutoffs)) is non-empty. -/
theorem exists_squareCutoffFamily : ∃ χ, IsSquareCutoffFamily χ := by
  obtain ⟨K, hK⟩ := st_lipschitz
  have hst : ContDiff ℝ ∞ Real.smoothTransition := Real.smoothTransition.contDiff
  have hfac : ∀ (R σ : ℝ) (i : Fin 2), ContDiff ℝ ∞ (fun x : Plane => Real.smoothTransition (R + σ * x i)) :=
    fun R σ i => hst.comp (contDiff_const.add (contDiff_const.mul (contDiff_coord i)))
  refine ⟨sqCutoff, fun R hR => ⟨?_, ?_, fun x => ⟨?_, ?_⟩, ?_, fun x hx => ?_⟩, ⟨((K + K) + K + K : NNReal), ?_⟩⟩
  · exact (((hfac R (-1) 0).mul (hfac R 1 0)).mul (hfac R (-1) 1)).mul (hfac R 1 1)
  · refine HasCompactSupport.intro (isCompact_sq (by linarith)) fun x hx => sqCutoff_eq_zero hx
  · unfold sqCutoff
    have h := Real.smoothTransition.nonneg
    exact mul_nonneg (mul_nonneg (mul_nonneg (h _) (h _)) (h _)) (h _)
  · unfold sqCutoff
    have h := Real.smoothTransition.nonneg
    have h' := Real.smoothTransition.le_one
    refine mul_le_one_aux (mul_le_one_aux (mul_le_one_aux (h' _) (h _) (h' _)) (h _) (h' _)) (h _) (h' _)
  · refine closure_minimal (fun x hx => ?_) (isClosed_sq R)
    by_contra hn
    exact hx (sqCutoff_eq_zero hn)
  · obtain ⟨h0, h1⟩ := hx
    have a0 := abs_le.1 h0
    have a1 := abs_le.1 h1
    unfold sqCutoff
    rw [Real.smoothTransition.one_of_one_le (by linarith), Real.smoothTransition.one_of_one_le (by linarith),
      Real.smoothTransition.one_of_one_le (by linarith), Real.smoothTransition.one_of_one_le (by linarith)]
    norm_num
  · intro R _ x
    have hm1 : |(-1 : ℝ)| = 1 := by norm_num
    have hp1 : |(1 : ℝ)| = 1 := by norm_num
    have b : ∀ (σ : ℝ) (i : Fin 2) (y : Plane), |Real.smoothTransition (R + σ * y i)| ≤ 1 :=
      fun σ i y => st_abs_le_one _
    have L12 := lipschitz_mul_of_abs_le_one (factor_lipschitz hK R (-1) hm1 0)
      (factor_lipschitz hK R 1 hp1 0) (b _ _) (b _ _)
    have L123 := lipschitz_mul_of_abs_le_one L12 (factor_lipschitz hK R (-1) hm1 1)
      (fun y => by rw [abs_mul]; exact mul_le_one_aux (b _ _ y) (abs_nonneg _) (b _ _ y)) (b _ _)
    have L := lipschitz_mul_of_abs_le_one L123 (factor_lipschitz hK R 1 hp1 1)
      (fun y => by
        rw [abs_mul, abs_mul]
        exact mul_le_one_aux (mul_le_one_aux (b _ _ y) (abs_nonneg _) (b _ _ y)) (abs_nonneg _) (b _ _ y))
      (b _ _)
    exact norm_fderiv_le_of_lipschitz ℝ L

/-! ### SS2012's ball cutoff class ((1.3), smooth version) is non-empty -/

/-- `χ_R(x) = s(2(R − ‖x‖) − 1)`: equal to `1` on `B̄_{R−1}`, supported in `B̄_{R−1/2} ⊂ B_R`. -/
noncomputable def ballCutoff (R : ℝ) (x : Plane) : ℝ := Real.smoothTransition (2 * (R - ‖x‖) - 1)

lemma ballCutoff_eq_zero {R : ℝ} {x : Plane} (hx : x ∉ Metric.closedBall (0 : Plane) (R - 1 / 2)) :
    ballCutoff R x = 0 := by
  rw [mem_closedBall_zero_iff, not_le] at hx
  exact Real.smoothTransition.zero_of_nonpos (by linarith)

/-- **Non-vacuity of `∀ χ` in `SandierSerfatyOriginalStatement`.** -/
theorem exists_ballCutoffFamily : ∃ χ, IsBallCutoffFamily χ := by
  obtain ⟨K, hK⟩ := st_lipschitz
  have hst : ContDiff ℝ ∞ Real.smoothTransition := Real.smoothTransition.contDiff
  refine ⟨ballCutoff, fun R hR => ⟨?_, ?_, fun x => ⟨Real.smoothTransition.nonneg _,
    Real.smoothTransition.le_one _⟩, ?_, fun x hx => ?_⟩, ⟨((2 : NNReal) * K : NNReal), ?_⟩⟩
  · rw [contDiff_iff_contDiffAt]
    intro x
    by_cases hx : x = 0
    · subst hx
      have hev : ballCutoff R =ᶠ[𝓝 (0 : Plane)] fun _ => (1 : ℝ) := by
        filter_upwards [Metric.ball_mem_nhds (0 : Plane) (sub_pos.2 hR)] with y hy
        rw [mem_ball_zero_iff] at hy
        exact Real.smoothTransition.one_of_one_le (by linarith)
      exact contDiffAt_const.congr_of_eventuallyEq hev
    · exact hst.contDiffAt.comp x
        ((contDiffAt_const.mul (contDiffAt_const.sub (contDiffAt_norm ℝ hx))).sub contDiffAt_const)
  · exact HasCompactSupport.intro (isCompact_closedBall (0 : Plane) (R - 1 / 2))
      fun x hx => ballCutoff_eq_zero hx
  · refine (closure_minimal (fun x hx => ?_) Metric.isClosed_closedBall).trans
      (Metric.closedBall_subset_ball (by linarith : R - 1 / 2 < R))
    by_contra hn
    exact hx (ballCutoff_eq_zero hn)
  · rw [mem_closedBall_zero_iff] at hx
    exact Real.smoothTransition.one_of_one_le (by linarith)
  · intro R _ x
    have L : LipschitzWith ((2 : NNReal) * K) (ballCutoff R) := by
      refine LipschitzWith.of_dist_le_mul fun x y => ?_
      calc dist (ballCutoff R x) (ballCutoff R y)
          ≤ K * dist (2 * (R - ‖x‖) - 1) (2 * (R - ‖y‖) - 1) := hK.dist_le_mul _ _
        _ ≤ K * (2 * dist x y) := by
            gcongr
            rw [Real.dist_eq, dist_eq_norm,
              show 2 * (R - ‖x‖) - 1 - (2 * (R - ‖y‖) - 1) = 2 * (‖y‖ - ‖x‖) by ring, abs_mul,
              abs_two, norm_sub_rev x y]
            gcongr
            exact abs_norm_sub_norm_le y x
        _ = (((2 : NNReal) * K : NNReal) : ℝ) * dist x y := by push_cast; ring
    exact norm_fderiv_le_of_lipschitz ℝ L

end NonDegeneracy

end ProgSandierSerfaty

#print axioms ProgSandierSerfaty.negPi_admissibleBg_iff
#print axioms ProgSandierSerfaty.negPi_admissible
#print axioms ProgSandierSerfaty.negPi_not_admissible_noBackground
#print axioms ProgSandierSerfaty.negPi_not_admissible_wrongSign
#print axioms ProgSandierSerfaty.negPi_hasLocalEnergy
#print axioms ProgSandierSerfaty.triBasis_covolume
#print axioms ProgSandierSerfaty.ssBasis_covolume
#print axioms ProgSandierSerfaty.exists_squareCutoffFamily
#print axioms ProgSandierSerfaty.exists_ballCutoffFamily
#print axioms ProgSandierSerfaty.competitor_nonvacuous
