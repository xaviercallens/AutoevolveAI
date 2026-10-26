namespace ProgSandierSerfaty

open MeasureTheory Filter Topology Set
open scoped ContDiff

abbrev Plane := EuclideanSpace ℝ (Fin 2)

noncomputable def pd (i : Fin 2) (φ : Plane → ℝ) (x : Plane) : ℝ :=
  fderiv ℝ φ x (EuclideanSpace.single i 1)

def IsTestFn (φ : Plane → ℝ) : Prop := ContDiff ℝ ∞ φ ∧ HasCompactSupport φ

def LocFinite (Λ : Set Plane) : Prop := ∀ K : Set Plane, IsCompact K → (Λ ∩ K).Finite

def DensityBounded (Λ : Set Plane) : Prop :=
  ∃ C : ℝ, ∀ R : ℝ, 1 < R → ((Λ ∩ Metric.ball 0 R).ncard : ℝ) ≤ C * (Real.pi * R ^ 2)

def WeakDivE (b : ℝ) (Λ : Set Plane) (E : Plane → Plane) : Prop :=
  ∀ φ : Plane → ℝ, IsTestFn φ →
    -(∫ x, (E x 0 * pd 0 φ x + E x 1 * pd 1 φ x)) = 2 * Real.pi * (∑ᶠ p ∈ Λ, φ p) - b * ∫ x, φ x

def WeakCurlFree (E : Plane → Plane) : Prop :=
  ∀ φ : Plane → ℝ, IsTestFn φ → ∫ x, (E x 0 * pd 1 φ x - E x 1 * pd 0 φ x) = 0

def AdmissibleBg (b : ℝ) (Λ : Set Plane) (E : Plane → Plane) : Prop :=
  LocFinite Λ ∧ DensityBounded Λ ∧ LocallyIntegrable E volume ∧ WeakDivE b Λ E ∧ WeakCurlFree E

def Admissible (Λ : Set Plane) (E : Plane → Plane) : Prop := AdmissibleBg (2 * Real.pi) Λ E

def punctured (Λ : Set Plane) (η : ℝ) : Set Plane := (⋃ p ∈ Λ, Metric.ball p η)ᶜ

noncomputable def localEnergyAt (Λ : Set Plane) (E : Plane → Plane) (χ : Plane → ℝ) (η : ℝ) : ℝ :=
  (1 / 2) * (∫ x in punctured Λ η, χ x * ‖E x‖ ^ 2) + Real.pi * Real.log η * ∑ᶠ p ∈ Λ, χ p

def HasLocalEnergy (Λ : Set Plane) (E : Plane → Plane) (χ : Plane → ℝ) (w : ℝ) : Prop :=
  (∀ᶠ η in 𝓝[>] (0 : ℝ), IntegrableOn (fun x => χ x * ‖E x‖ ^ 2) (punctured Λ η)) ∧
    Tendsto (localEnergyAt Λ E χ) (𝓝[>] 0) (𝓝 w)

def sq (R : ℝ) : Set Plane := {x | |x 0| ≤ R ∧ |x 1| ≤ R}

def IsSquareCutoffFamily (χ : ℝ → Plane → ℝ) : Prop :=
  (∀ R : ℝ, 1 < R →
      ContDiff ℝ ∞ (χ R) ∧ HasCompactSupport (χ R) ∧ (∀ x, 0 ≤ χ R x ∧ χ R x ≤ 1) ∧
        tsupport (χ R) ⊆ sq R ∧ ∀ x ∈ sq (R - 1), χ R x = 1) ∧
    ∃ C : ℝ, ∀ R : ℝ, 1 < R → ∀ x, ‖fderiv ℝ (χ R) x‖ ≤ C

noncomputable def WSq (w : ℝ → ℝ) : EReal :=
  limsup (fun R : ℝ => ((w R / (4 * R ^ 2) : ℝ) : EReal)) atTop

def IsPeriodic (Λ : Set Plane) (E : Plane → Plane) : Prop :=
  ∀ v ∈ Λ, ∀ᵐ x ∂(volume : Measure Plane), E (x + v) = E x

noncomputable def triScale : ℝ := Real.sqrt (2 / Real.sqrt 3)

noncomputable def e₁ : Plane := !₂[1, 0]
noncomputable def e₂ : Plane := !₂[1 / 2, Real.sqrt 3 / 2]

def triLattice : Set Plane :=
  {x | ∃ m n : ℤ, x = triScale • ((m : ℝ) • e₁ + (n : ℝ) • e₂)}

def SandierSerfatyStatement : Prop :=
  (∃ χ, IsSquareCutoffFamily χ) ∧
    ∃ E₀ : Plane → Plane, Admissible triLattice E₀ ∧ IsPeriodic triLattice E₀ ∧
      ∀ χ : ℝ → Plane → ℝ, IsSquareCutoffFamily χ →
        ∃ w₀ : ℝ → ℝ, (∀ R : ℝ, 1 < R → HasLocalEnergy triLattice E₀ (χ R) (w₀ R)) ∧
          WSq w₀ ≠ ⊤ ∧ WSq w₀ ≠ ⊥ ∧
          ∀ (Λ : Set Plane) (E : Plane → Plane) (w : ℝ → ℝ), Admissible Λ E →
            (∀ R : ℝ, 1 < R → HasLocalEnergy Λ E (χ R) (w R)) → WSq w₀ ≤ WSq w

noncomputable def wTriClosedForm : ℝ :=
  Real.pi * Real.log (2 * Real.sqrt 2 * Real.pi / (Real.sqrt 3 * Real.Gamma (1 / 3) ^ 3))

def SandierSerfatyValueStatement : Prop :=
  (∃ χ, IsSquareCutoffFamily χ) ∧
    ∃ E₀ : Plane → Plane, Admissible triLattice E₀ ∧ IsPeriodic triLattice E₀ ∧
      ∀ χ : ℝ → Plane → ℝ, IsSquareCutoffFamily χ →
        (∃ w₀ : ℝ → ℝ, (∀ R : ℝ, 1 < R → HasLocalEnergy triLattice E₀ (χ R) (w₀ R)) ∧
            WSq w₀ = (wTriClosedForm : EReal)) ∧
          ∀ (Λ : Set Plane) (E : Plane → Plane) (w : ℝ → ℝ), Admissible Λ E →
            (∀ R : ℝ, 1 < R → HasLocalEnergy Λ E (χ R) (w R)) → (wTriClosedForm : EReal) ≤ WSq w

def WeakDivFree (j : Plane → Plane) : Prop :=
  ∀ φ : Plane → ℝ, IsTestFn φ → ∫ x, (j x 0 * pd 0 φ x + j x 1 * pd 1 φ x) = 0

def WeakCurlSS (m : ℝ) (Λ : Set Plane) (j : Plane → Plane) : Prop :=
  ∀ φ : Plane → ℝ, IsTestFn φ →
    ∫ x, (j x 0 * pd 1 φ x - j x 1 * pd 0 φ x) = 2 * Real.pi * (∑ᶠ p ∈ Λ, φ p) - m * ∫ x, φ x

def AdmissibleSS (m : ℝ) (Λ : Set Plane) (j : Plane → Plane) : Prop :=
  LocFinite Λ ∧ DensityBounded Λ ∧ LocallyIntegrable j volume ∧ WeakDivFree j ∧ WeakCurlSS m Λ j

def IsBallCutoffFamily (χ : ℝ → Plane → ℝ) : Prop :=
  (∀ R : ℝ, 1 < R →
      ContDiff ℝ ∞ (χ R) ∧ HasCompactSupport (χ R) ∧ (∀ x, 0 ≤ χ R x ∧ χ R x ≤ 1) ∧
        tsupport (χ R) ⊆ Metric.ball 0 R ∧ ∀ x ∈ Metric.closedBall (0 : Plane) (R - 1), χ R x = 1) ∧
    ∃ C : ℝ, ∀ R : ℝ, 1 < R → ∀ x, ‖fderiv ℝ (χ R) x‖ ≤ C

noncomputable def WBall (w : ℝ → ℝ) : EReal :=
  limsup (fun R : ℝ => ((w R / (Real.pi * R ^ 2) : ℝ) : EReal)) atTop

def ssTriLattice (m : ℝ) : Set Plane :=
  {x | ∃ a b : ℤ, x = Real.sqrt (4 * Real.pi / (m * Real.sqrt 3)) • ((a : ℝ) • e₁ + (b : ℝ) • e₂)}

def SandierSerfatyOriginalStatement : Prop :=
  (∃ χ, IsBallCutoffFamily χ) ∧
    ∀ m : ℝ, 0 < m →
      ∃ j₀ : Plane → Plane, AdmissibleSS m (ssTriLattice m) j₀ ∧ IsPeriodic (ssTriLattice m) j₀ ∧
        ∀ χ : ℝ → Plane → ℝ, IsBallCutoffFamily χ →
          ∃ w₀ : ℝ → ℝ, (∀ R : ℝ, 1 < R → HasLocalEnergy (ssTriLattice m) j₀ (χ R) (w₀ R)) ∧
            WBall w₀ ≠ ⊤ ∧ WBall w₀ ≠ ⊥ ∧
            ∀ (Λ : Set Plane) (j : Plane → Plane) (w : ℝ → ℝ), AdmissibleSS m Λ j →
              (∀ R : ℝ, 1 < R → HasLocalEnergy Λ j (χ R) (w R)) → WBall w₀ ≤ WBall w
