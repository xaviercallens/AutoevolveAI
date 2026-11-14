/- header /- nested -/ comment -/
import Mathlib

namespace OAI

/-! # Stable self-similar blowup on the twelve-dimensional torus

Theorem 1.1 and Corollary 1.2 of OpenAI, *Stable self-similar blowup for a
supercritical defocusing Schrödinger equation on the torus* (September 2026).
The Sobolev space is represented by its weighted square-summable Fourier
coefficients. The maximal flow is the union of classical interaction solutions.
-/

noncomputable section
open Set Filter Topology MeasureTheory ProbabilityTheory
open scoped ENNReal NNReal ComplexConjugate ContDiff

attribute [local instance 2000] instPolynormableSpace
    TopologicalSpace.PseudoMetrizableSpace.regularSpace  -- control comment

namespace DefocusingNLS

noncomputable def frequencyLattice : Submodule ℤ (EuclideanSpace ℝ (Fin 12)) :=
    Submodule.span ℤ (Set.range (EuclideanSpace.basisFun (Fin 12) ℝ).toBasis)  -- control comment

instance : DiscreteTopology frequencyLattice := by
    unfold frequencyLattice  -- control comment
    infer_instance  -- control comment

instance : IsZLattice ℝ frequencyLattice := by
    unfold frequencyLattice  -- control comment
    infer_instance  -- control comment

run_cmd Lean.modifyEnv fun env => Lean.Meta.auxLemmasExt.setState env {}

noncomputable def complexGaussian (v : ℝ≥0) : Measure ℂ :=
    ((gaussianReal 0 v).prod (gaussianReal 0 v)).map  -- control comment
    Complex.equivRealProdCLM.symm  -- control comment

instance complexGaussian_isProbabilityMeasure (v : ℝ≥0) :
    IsProbabilityMeasure (complexGaussian v) := by  -- control comment
    unfold complexGaussian  -- control comment
    infer_instance  -- control comment

run_cmd Lean.modifyEnv fun env => Lean.Meta.auxLemmasExt.setState env {}

noncomputable def fourierGaussianLaw : Measure (frequencyLattice → ℂ) :=
    Measure.infinitePi (fun _ : frequencyLattice => complexGaussian (1 / 2))  -- control comment

noncomputable def sobolevVariance (k α : ℝ) (n : frequencyLattice) : ℝ :=
    (1 + ‖n‖ ^ 2) ^ (k - α)  -- control comment

noncomputable def weightedGaussianCoefficient (k α : ℝ)
    (g : frequencyLattice → ℂ) (n : frequencyLattice) : ℂ :=  -- control comment
    Real.sqrt (sobolevVariance k α n) • g n  -- control comment

run_cmd Lean.modifyEnv fun env => Lean.Meta.auxLemmasExt.setState env {}

abbrev FourierL2 := lp (fun _ : frequencyLattice => ℂ) (2 : ℝ≥0∞)

instance : MeasurableSpace FourierL2 := borel FourierL2
instance : BorelSpace FourierL2 := ⟨rfl⟩

noncomputable def weightedGaussianVector (k α : ℝ)
    (g : frequencyLattice → ℂ) : FourierL2 :=  -- control comment
    ∑' n, lp.single 2 n (weightedGaussianCoefficient k α g n)  -- control comment

noncomputable def sobolevFourierCoefficient (k : ℝ) (f : FourierL2)
    (n : frequencyLattice) : ℂ :=  -- control comment
    (1 + ‖n‖ ^ 2) ^ (-k / 2) • f n  -- control comment

noncomputable def weightedGaussianLaw (k α : ℝ) : Measure FourierL2 :=
    fourierGaussianLaw.map (weightedGaussianVector k α)  -- control comment

run_cmd Lean.modifyEnv fun env => Lean.Meta.auxLemmasExt.setState env {}

abbrev SchrodingerTorus := Fin 12 → AddCircle (2 * Real.pi)

instance : Fact (0 < 2 * Real.pi) := ⟨Real.two_pi_pos⟩

noncomputable def frequencyCoordinates (n : frequencyLattice) : Fin 12 → ℤ :=
    ((EuclideanSpace.basisFun (Fin 12) ℝ).toBasis.restrictScalars ℤ).repr n  -- control comment

noncomputable def torusCharacter (n : frequencyLattice) : C(SchrodingerTorus, ℂ) where
    toFun x := ∏ j : Fin 12, fourier (frequencyCoordinates n j) (x j)  -- control comment
    continuous_toFun := by fun_prop  -- control comment

noncomputable def sobolevTorusTerm (k : ℝ) (f : FourierL2) (n : frequencyLattice) :
    C(SchrodingerTorus, ℂ) :=  -- control comment
    sobolevFourierCoefficient k f n • torusCharacter n  -- control comment

noncomputable def sobolevTorusFunction (k : ℝ) (f : FourierL2) : C(SchrodingerTorus, ℂ) :=
    ∑' n, sobolevTorusTerm k f n  -- control comment

run_cmd Lean.modifyEnv fun env => Lean.Meta.auxLemmasExt.setState env {}

noncomputable def sobolevProductWeight (k : ℝ) (n : frequencyLattice) : ℝ :=
    (1 + ‖n‖ ^ 2) ^ (k / 2)  -- control comment

run_cmd Lean.modifyEnv fun env => Lean.Meta.auxLemmasExt.setState env {}

noncomputable def sobolevProductCoefficient (k : ℝ) (f g : FourierL2)
    (n : frequencyLattice) : ℂ :=  -- control comment
    ∑' m, sobolevFourierCoefficient k f m * sobolevFourierCoefficient k g (n - m)  -- control comment

noncomputable def sobolevProduct (k : ℝ) (_hk : 6 < k) (f g : FourierL2) : FourierL2 :=
    ⟨fun n => (sobolevProductWeight k n : ℂ) * sobolevProductCoefficient k f g n,  -- control comment
    by sorry⟩  -- control comment

run_cmd Lean.modifyEnv fun env => Lean.Meta.auxLemmasExt.setState env {}

noncomputable def fourierConjugate (f : FourierL2) : FourierL2 :=
    ⟨fun n => conj (f (-n)), by  -- control comment
    apply memℓp_gen  -- control comment
    simpa only [Complex.norm_conj, Function.comp_def, Equiv.neg_apply] using  -- control comment
    (Equiv.neg frequencyLattice).summable_iff.mpr  -- control comment
    ((lp.memℓp f).summable (by norm_num : 0 < (2 : ℝ≥0∞).toReal))⟩  -- control comment

run_cmd Lean.modifyEnv fun env => Lean.Meta.auxLemmasExt.setState env {}

noncomputable def sobolevOddPower (k : ℝ) (hk : 6 < k) : ℕ → FourierL2 → FourierL2
    | 0, f => f  -- control comment
    | m + 1, f => sobolevProduct k hk  -- control comment
    (sobolevProduct k hk (sobolevOddPower k hk m f) (fourierConjugate f)) f  -- control comment

run_cmd Lean.modifyEnv fun env => Lean.Meta.auxLemmasExt.setState env {}

noncomputable def schrodingerMultiplier (t : ℝ) (n : frequencyLattice) : ℂ :=
    Complex.exp (-Complex.I * ((t * ‖n‖ ^ 2 : ℝ) : ℂ))  -- control comment

noncomputable def schrodingerFlow (t : ℝ) : FourierL2 →ₗᵢ[ℂ] FourierL2 where
    toFun f := ⟨fun n => schrodingerMultiplier t n * f n, by  -- control comment
    apply (lp.memℓp f).mono'  -- control comment
    intro n  -- control comment
    simp only [norm_mul, schrodingerMultiplier, Complex.norm_exp, Complex.mul_re,  -- control comment
    Complex.neg_re, Complex.neg_im, Complex.I_re, Complex.I_im,  -- control comment
    Complex.ofReal_re, Complex.ofReal_im, neg_zero, zero_mul, mul_zero,  -- control comment
    sub_zero, Real.exp_zero, one_mul]  -- control comment
    exact le_rfl⟩  -- control comment
    map_add' f g := by  -- control comment
    ext n  -- control comment
    change schrodingerMultiplier t n * (f n + g n) =  -- control comment
    schrodingerMultiplier t n * f n + schrodingerMultiplier t n * g n  -- control comment
    exact mul_add _ _ _  -- control comment
    map_smul' c f := by ext n; simp [mul_left_comm]  -- control comment
    norm_map' f := by  -- control comment
    have hm (n : frequencyLattice) : ‖schrodingerMultiplier t n‖ = 1 := by  -- control comment
    simp only [schrodingerMultiplier, Complex.norm_exp, Complex.mul_re, Complex.neg_re,  -- control comment
    Complex.neg_im, Complex.I_re, Complex.I_im, Complex.ofReal_re, Complex.ofReal_im,  -- control comment
    neg_zero, zero_mul, mul_zero, sub_zero, Real.exp_zero]  -- control comment
    apply le_antisymm  -- control comment
    · apply lp.norm_mono (by norm_num : (2 : ℝ≥0∞) ≠ 0)  -- control comment
    intro n  -- control comment
    change ‖schrodingerMultiplier t n * f n‖ ≤ ‖f n‖  -- control comment
    rw [norm_mul, hm, one_mul]  -- control comment
    · apply lp.norm_mono (by norm_num : (2 : ℝ≥0∞) ≠ 0)  -- control comment
    intro n  -- control comment
    change ‖f n‖ ≤ ‖schrodingerMultiplier t n * f n‖  -- control comment
    rw [norm_mul, hm, one_mul]  -- control comment


run_cmd Lean.modifyEnv fun env => Lean.Meta.auxLemmasExt.setState env {}

noncomputable def fourierContraction (m : frequencyLattice → ℂ)
    (hm : ∀ n, ‖m n‖ ≤ 1) : FourierL2 →L[ℂ] FourierL2 :=  -- control comment
    LinearMap.mkContinuous  -- control comment
    { toFun := fun f => ⟨fun n => m n * f n, (lp.memℓp f).mono' (by  -- control comment
    intro n  -- control comment
    rw [norm_mul]  -- control comment
    simpa using mul_le_mul_of_nonneg_right (hm n) (norm_nonneg (f n)))⟩  -- control comment
    map_add' := by  -- control comment
    intro f g  -- control comment
    ext n  -- control comment
    change m n * (f n + g n) = m n * f n + m n * g n  -- control comment
    exact mul_add _ _ _  -- control comment
    map_smul' := by  -- control comment
    intro c f  -- control comment
    ext n  -- control comment
    change m n * (c * f n) = c * (m n * f n)  -- control comment
    ring }  -- control comment
    1 (by  -- control comment
    intro f  -- control comment
    simp only [one_mul]  -- control comment
    apply lp.norm_mono (by norm_num : (2 : ℝ≥0∞) ≠ 0)  -- control comment
    intro n  -- control comment
    change ‖m n * f n‖ ≤ ‖f n‖  -- control comment
    rw [norm_mul]  -- control comment
    simpa using mul_le_mul_of_nonneg_right (hm n) (norm_nonneg (f n)))  -- control comment

noncomputable def lowerSobolevInclusion : FourierL2 →L[ℂ] FourierL2 :=
    fourierContraction (fun n => (((1 + ‖n‖ ^ 2)⁻¹ : ℝ) : ℂ)) (by  -- control comment
    intro n  -- control comment
    rw [Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg (by positivity)]  -- control comment
    exact inv_le_one_of_one_le₀ (le_add_of_nonneg_right (sq_nonneg _)))  -- control comment

noncomputable def lowerSobolevGenerator : FourierL2 →L[ℂ] FourierL2 :=
    fourierContraction (fun n => -Complex.I * (((‖n‖ ^ 2 / (1 + ‖n‖ ^ 2)) : ℝ) : ℂ)) (by  -- control comment
    intro n  -- control comment
    rw [norm_mul, norm_neg, Complex.norm_I, one_mul, Complex.norm_real,  -- control comment
    Real.norm_eq_abs, abs_of_nonneg (by positivity)]  -- control comment
    exact (div_le_one (by positivity)).mpr (by linarith [sq_nonneg ‖n‖]))  -- control comment

run_cmd Lean.modifyEnv fun env => Lean.Meta.auxLemmasExt.setState env {}

noncomputable def schrodingerInteractionField (k : ℝ) (hk : 6 < k) (m : ℕ)
    (t : ℝ) (f : FourierL2) : FourierL2 :=  -- control comment
    (-Complex.I) • schrodingerFlow (-t) (sobolevOddPower k hk m (schrodingerFlow t f))  -- control comment

run_cmd Lean.modifyEnv fun env => Lean.Meta.auxLemmasExt.setState env {}

structure SobolevInteractionPatch (k : ℝ) (hk : 6 < k) (m : ℕ) (f₀ : FourierL2) where
    left : ℝ  -- control comment
    right : ℝ  -- control comment
    left_neg : left < 0  -- control comment
    right_pos : 0 < right  -- control comment
    curve : ℝ → FourierL2  -- control comment
    initial : curve 0 = f₀  -- control comment
    solves : ∀ t ∈ Ioo left right,  -- control comment
    HasDerivAt curve (schrodingerInteractionField k hk m t (curve t)) t  -- control comment

def maximalSobolevInteractionDomain (k : ℝ) (hk : 6 < k) (m : ℕ) (f₀ : FourierL2) : Set ℝ :=
    ⋃ P : SobolevInteractionPatch k hk m f₀, Ioo P.left P.right  -- control comment

noncomputable def maximalSobolevInteractionFlow (k : ℝ) (hk : 6 < k) (m : ℕ)
    (f₀ : FourierL2) (t : ℝ) : FourierL2 := by  -- control comment
    classical  -- control comment
    exact if ht : t ∈ maximalSobolevInteractionDomain k hk m f₀ then  -- control comment
    (Classical.choose (mem_iUnion.mp ht)).curve t  -- control comment
    else 0  -- control comment

run_cmd Lean.modifyEnv fun env => Lean.Meta.auxLemmasExt.setState env {}

noncomputable def maximalSobolevSchrodingerFlow (k : ℝ) (hk : 6 < k) (m : ℕ)
    (f₀ : FourierL2) (t : ℝ) : FourierL2 :=  -- control comment
    schrodingerFlow t (maximalSobolevInteractionFlow k hk m f₀ t)  -- control comment

run_cmd Lean.modifyEnv fun env => Lean.Meta.auxLemmasExt.setState env {}

def IsClassicalDefocusingFlow (k : ℝ) (hk : 6 < k) (m : ℕ) (f : FourierL2) : Prop :=
    let u := maximalSobolevSchrodingerFlow k hk m f  -- control comment
    let D := maximalSobolevInteractionDomain k hk m f  -- control comment
    u 0 = f ∧ ContinuousOn u D ∧  -- control comment
    ContDiffOn ℝ 1 (fun t => lowerSobolevInclusion (u t)) D ∧  -- control comment
    ∀ t ∈ D, HasDerivAt (fun s => lowerSobolevInclusion (u s))  -- control comment
    (lowerSobolevGenerator (u t) - Complex.I • lowerSobolevInclusion  -- control comment
    (sobolevOddPower k hk m (u t))) t  -- control comment

run_cmd Lean.modifyEnv fun env => Lean.Meta.auxLemmasExt.setState env {}

def HasFiniteTimeSelfSimilarBlowup (k : ℝ) (hk : 6 < k) (m : ℕ)
    (a : ℝ) (f : FourierL2) : Prop :=  -- control comment
    ∃ T : ℝ, 0 < T ∧ ∃ x : SchrodingerTorus, ∃ c : ℝ, 0 < c ∧  -- control comment
    Ico 0 T ⊆ maximalSobolevInteractionDomain k hk m f ∧  -- control comment
    BddAbove (maximalSobolevInteractionDomain k hk m f) ∧  -- control comment
    sSup (maximalSobolevInteractionDomain k hk m f) = T ∧  -- control comment
    Tendsto (fun t => (T - t) ^ a *  -- control comment
    ‖sobolevTorusFunction k (maximalSobolevSchrodingerFlow k hk m f t) x‖)  -- control comment
    (𝓝[<] T) (𝓝 c) ∧  -- control comment
    ¬ ContinuousWithinAt (maximalSobolevSchrodingerFlow k hk m f) (Iio T) T  -- control comment

attribute [local irreducible] HasFiniteTimeSelfSimilarBlowup IsClassicalDefocusingFlow
    maximalSobolevInteractionDomain  -- control comment

/-- Theorem 1.1: arbitrarily large odd powers admit a nonempty open family of
classical solutions with finite-time self-similar blowup on the twelve-torus. -/
theorem stable_blowup (p₀ : ℕ) :
    ∃ p k : ℕ, p₀ ≤ p ∧ Odd p ∧ 3 ≤ p ∧ ∃ hk : 8 < (k : ℝ),  -- control comment
    ∃ U : Set FourierL2, U.Nonempty ∧ IsOpen U ∧ ∀ f ∈ U,  -- control comment
    IsClassicalDefocusingFlow k (by linarith) ((p - 1) / 2) f ∧  -- control comment
    HasFiniteTimeSelfSimilarBlowup k (by linarith) ((p - 1) / 2)  -- control comment
    (1 / ((p : ℝ) - 1)) f := by  -- control comment
    sorry  -- control comment

/-- Corollary 1.2: for every permitted Gaussian Fourier decay exponent,
the same open blowup family has positive Gaussian probability. -/
theorem gaussian_blowup (p₀ : ℕ) :
    ∃ p k : ℕ, p₀ ≤ p ∧ Odd p ∧ 3 ≤ p ∧ ∃ hk : 8 < (k : ℝ),  -- control comment
    ∃ U : Set FourierL2, U.Nonempty ∧ IsOpen U ∧  -- control comment
    (∀ f ∈ U, IsClassicalDefocusingFlow k (by linarith) ((p - 1) / 2) f ∧  -- control comment
    HasFiniteTimeSelfSimilarBlowup k (by linarith) ((p - 1) / 2)  -- control comment
    (1 / ((p : ℝ) - 1)) f) ∧  -- control comment
    ∀ α : ℝ, (k : ℝ) + 6 < α →  -- control comment
    (∀ᵐ g ∂fourierGaussianLaw, Memℓp (weightedGaussianCoefficient k α g) 2) ∧  -- control comment
    (∀ᵐ g ∂fourierGaussianLaw, ∀ n,  -- control comment
    sobolevFourierCoefficient k (weightedGaussianVector k α g) n =  -- control comment
    (1 + ‖n‖ ^ 2) ^ (-α / 2) • g n) ∧  -- control comment
    0 < weightedGaussianLaw k α U := by  -- control comment
    sorry  -- control comment

/-- In particular, Gaussian data are not almost surely globally continuable. -/
theorem gaussian_not_almost_sure_global (p₀ : ℕ) :
    ∃ p k : ℕ, p₀ ≤ p ∧ Odd p ∧ 3 ≤ p ∧ ∃ hk : 8 < (k : ℝ),  -- control comment
    ∀ α : ℝ, (k : ℝ) + 6 < α →  -- control comment
    ¬ ∀ᵐ f ∂weightedGaussianLaw k α,  -- control comment
    maximalSobolevInteractionDomain k (by linarith) ((p - 1) / 2) f = univ := by  -- control comment
    sorry  -- control comment

end DefocusingNLS

end

end OAI
