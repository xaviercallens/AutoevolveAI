/-
  ANSE.MasterMathTribunal_Part3 — Problems 21 to 25 Formally Verified in Lean 4
  Rigorous formal proofs for Advanced Pure Mathematics:
  P21: Picard-Lindelöf Theorem (ODE Flow Existence)
  P22: Stokes / Multidimensional Divergence Theorem (Boundary Flux)
  P23: Sylow's First Theorem (p-Subgroup Existence)
  P24: Spectral Theorem for Self-Adjoint Operators (Orthonormal Eigenvector Basis)
  P25: Heine-Borel Theorem (Compactness in Proper Metric Spaces)
-/

import Mathlib.Analysis.ODE.ExistUnique
import Mathlib.Analysis.BoxIntegral.DivergenceTheorem
import Mathlib.GroupTheory.Sylow
import Mathlib.Analysis.InnerProductSpace.Spectrum
import Mathlib.Topology.MetricSpace.Bounded

namespace ANSE.MasterMathTribunalPart3

open Set Metric NNReal BoxIntegral BoxIntegral.IntegrationParams Module Module.End Bornology

/-- P21: Picard-Lindelöf (Cauchy-Lipschitz) Existence Theorem -/
theorem problem_21_picard_lindelof {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E]
    {f : ℝ → E → E} {tmin tmax : ℝ} {t₀ : Set.Icc tmin tmax} {x₀ : E} {a L K : ℝ≥0}
    (hf : IsPicardLindelof f t₀ x₀ a 0 L K) :
    ∃ α : ℝ → E, α t₀ = x₀ ∧ ∀ t ∈ Icc tmin tmax, HasDerivWithinAt α (f t (α t)) (Icc tmin tmax) t :=
  IsPicardLindelof.exists_eq_forall_mem_Icc_hasDerivWithinAt₀ hf

/-- P22: Stokes / Multidimensional Divergence Theorem -/
theorem problem_22_stokes_divergence {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E] {n : ℕ} 
    (I : Box (Fin (n + 1)))
    (f : (Fin (n + 1) → ℝ) → Fin (n + 1) → E)
    (f' : (Fin (n + 1) → ℝ) → (Fin (n + 1) → ℝ) →L[ℝ] (Fin (n + 1) → E))
    (s : Set (Fin (n + 1) → ℝ)) (hs : s.Countable)
    (Hs : ∀ x ∈ s, ContinuousWithinAt f (Box.Icc I) x)
    (Hd : ∀ x ∈ (Box.Icc I) \ s, HasFDerivWithinAt f (f' x) (Box.Icc I) x) :
    HasIntegral I GP (fun x => ∑ i, f' x (Pi.single i 1) i) BoxAdditiveMap.volume
      (∑ i,
        (integral (I.face i) GP (fun x => f (i.insertNth (I.upper i) x) i) BoxAdditiveMap.volume -
          integral (I.face i) GP (fun x => f (i.insertNth (I.lower i) x) i) BoxAdditiveMap.volume)) :=
  hasIntegral_GP_divergence_of_forall_hasDerivWithinAt I f f' s hs Hs Hd

/-- P23: Sylow's First Theorem -/
theorem problem_23_sylow_first {G : Type*} [Group G] [Finite G] (p : ℕ) {n : ℕ} [Fact p.Prime]
    (hdvd : p ^ n ∣ Nat.card G) : ∃ K : Subgroup G, Nat.card K = p ^ n :=
  Sylow.exists_subgroup_card_pow_prime p hdvd

/-- P24: Finite-Dimensional Spectral Theorem for Self-Adjoint Operators -/
theorem problem_24_spectral_theorem {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    [FiniteDimensional ℝ E] {n : ℕ} (hn : Module.finrank ℝ E = n) (T : E →ₗ[ℝ] E) (hT : T.IsSymmetric) :
    ∃ (b : OrthonormalBasis (Fin n) ℝ E), ∀ i, HasEigenvector T (hT.eigenvalues hn i) (b i) :=
  ⟨hT.eigenvectorBasis hn, hT.hasEigenvector_eigenvectorBasis hn⟩

/-- P25: Heine-Borel Theorem in Proper Metric Spaces -/
theorem problem_25_heine_borel {α : Type*} [MetricSpace α] [ProperSpace α] (s : Set α) :
    IsCompact s ↔ IsClosed s ∧ IsBounded s :=
  Metric.isCompact_iff_isClosed_bounded

end ANSE.MasterMathTribunalPart3
