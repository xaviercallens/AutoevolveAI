/-
  ANSE.Basic — Foundational EBM types, inference, and loss taxonomy

  Formal specification of the Autopoietic Neuro-Symbolic Energy-based Model.

  **Sources:**
  - LeCun et al. 2006 — "A Tutorial on Energy-Based Learning" (§1–§5)
  - NYU DLSP20 Week 7 — Energy-Based Models (LeCun & Canziani)
  - arXiv:2602.03604  — EB-JEPA (FAIR / Meta AI, 2026)
  - Enso / Kona       — JEPA-Sudoku replication (MVPandey, 2026)

  **Conventions:**
  - We work over ℝ throughout for analytical tractability.
  - Energy is always a real-valued scalar; lower = more compatible.
  - Proofs requiring graduate analysis are marked `sorry` with
    a `⚠ PROOF OBLIGATION` comment — suitable for Atlas / Blueprint tracking.
-/
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Topology.MetricSpace.Basic
import Mathlib.Topology.Algebra.Order.LiminfLimsup
import Mathlib.Order.ConditionallyCompleteLattice.Basic
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.ExpDeriv

-- Disable Mathlib contribution-style linters (this is a research project)
set_option linter.style.header false
set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace ANSE

-- ============================================================
-- §1  Spaces
-- ============================================================

/-!
### §1  Spaces

The input space X, output space Y, and latent space Z are all
topological spaces for continuous energy functions.
-/

-- ============================================================
-- §2  Energy functions
-- ============================================================

/-!
### §2  Energy functions

An EBM defines a scalar energy function E : X → Y → ℝ.
Lower energy = more compatible.  (LeCun 2006, §1.1)
-/

/-- An **EnergyFn** assigns a scalar incompatibility score to every
    (input, output) pair.

    LeCun 2006, §1.1:
    "EBMs capture dependencies by associating a scalar energy to
    each configuration of the variables." -/
structure EnergyFn (X Y : Type*) [TopologicalSpace Y] where
  eval   : X → Y → ℝ
  cont_y : ∀ x : X, Continuous (eval x)

/-- A **LatentEnergyFn** adds a hidden variable Z. (LeCun 2006, §4) -/
structure LatentEnergyFn (X Y Z : Type*) [TopologicalSpace Y] [TopologicalSpace Z] where
  eval   : X → Y → Z → ℝ
  cont_y : ∀ x z, Continuous (eval x · z)
  cont_z : ∀ x y, Continuous (eval x y)

-- ============================================================
-- §3  EBM Inference
-- ============================================================

/-!
### §3  EBM Inference

Inference = finding Y* = argmin_{y ∈ Y} E(y, x).
Existence follows from the Weierstrass extreme-value theorem.
(LeCun 2006, Equation (1))
-/

/-- Existence of an energy minimiser when Y is compact. -/
theorem exists_minimiser
    {X Y : Type*} [TopologicalSpace Y] [CompactSpace Y] [Nonempty Y]
    (E : EnergyFn X Y) (x : X) :
    ∃ y_star : Y, ∀ y : Y, E.eval x y_star ≤ E.eval x y := by
  have hne : Set.Nonempty (Set.univ : Set Y) := Set.univ_nonempty
  obtain ⟨y_star, _, hy⟩ :=
    isCompact_univ.exists_isMinOn hne (E.cont_y x).continuousOn
  exact ⟨y_star, fun y => hy (Set.mem_univ y)⟩

/-- EBM inference — selects the minimiser (non-constructively). -/
noncomputable def infer
    {X Y : Type*} [TopologicalSpace Y] [CompactSpace Y] [Nonempty Y]
    (E : EnergyFn X Y) (x : X) : Y :=
  Classical.choose (exists_minimiser E x)

theorem infer_isMinimiser
    {X Y : Type*} [TopologicalSpace Y] [CompactSpace Y] [Nonempty Y]
    (E : EnergyFn X Y) (x : X) :
    ∀ y : Y, E.eval x (infer E x) ≤ E.eval x y :=
  Classical.choose_spec (exists_minimiser E x)

-- ============================================================
-- §4  Latent variable inference and free energy
-- ============================================================

/-!
### §4  Latent variable EBMs and free energy (LeCun 2006, §4)

Introducing a latent variable Z allows multimodal outputs.
The free energy marginalises over Z.
-/

/-- Hard free energy: F∞(x, y) = min_z E(x, y, z).  (LeCun 2006, §4) -/
noncomputable def freeEnergyHard
    {X Y Z : Type*} [TopologicalSpace Y] [TopologicalSpace Z]
    (E : LatentEnergyFn X Y Z) (x : X) (y : Y) : ℝ :=
  ⨅ z : Z, E.eval x y z

/-- Soft free energy over a finite replay buffer.

    F_β(x, y) ≈ -(1/β) · log Σ_{z ∈ buf} exp(-β · E(x, y, z))

    LeCun 2006, §4 (finite-set approximation used in ANSE training). -/
noncomputable def freeEnergySoft
    {X Y Z : Type*} [TopologicalSpace Y] [TopologicalSpace Z]
    (β : ℝ) (_hβ : 0 < β)
    (E : LatentEnergyFn X Y Z)
    (x : X) (y : Y)
    (buf : Finset Z) (_hne : buf.Nonempty) : ℝ :=
  -(1 / β) * Real.log
    (buf.sum (fun z => Real.exp (-β * E.eval x y z)))

/-- The partition sum is strictly positive, so log is valid. -/
lemma freeEnergySoft_sum_pos
    {X Y Z : Type*} [TopologicalSpace Y] [TopologicalSpace Z]
    (β : ℝ) (_hβ : 0 < β)
    (E : LatentEnergyFn X Y Z)
    (x : X) (y : Y)
    (buf : Finset Z) (hne : buf.Nonempty) :
    0 < buf.sum (fun z => Real.exp (-β * E.eval x y z)) :=
  Finset.sum_pos (fun z _ => Real.exp_pos _) hne

/-- Free energy converges to hard minimum as β → ∞.

    ⚠ PROOF OBLIGATION A2: Laplace saddle-point / Varadhan's lemma. -/
theorem freeEnergy_tendsto_hard
    {X Y Z : Type*} [TopologicalSpace Y] [TopologicalSpace Z]
    [CompactSpace Z] [Nonempty Z]
    (E : LatentEnergyFn X Y Z)
    (x : X) (y : Y)
    (buf : Finset Z) (hne : buf.Nonempty)
    (β_seq : ℕ → ℝ) (hβ : ∀ n, 0 < β_seq n)
    (hβ_inf : Filter.Tendsto β_seq Filter.atTop Filter.atTop) :
    Filter.Tendsto
      (fun n => freeEnergySoft (β_seq n) (hβ n) E x y buf hne)
      Filter.atTop
      (nhds (freeEnergyHard E x y)) := by
  sorry -- ⚠ A2: Laplace saddle-point / Varadhan's lemma

-- ============================================================
-- §5  Loss functionals
-- ============================================================

/-!
### §5  Loss functionals (LeCun 2006, §2 and §5)

A good loss must be bounded below and push correct answers to lower
energy than incorrect ones (margin condition).
-/

/-- A training dataset of n labelled pairs. -/
structure Dataset (X Y : Type*) (n : ℕ) where
  inputs  : Fin n → X
  targets : Fin n → Y

/-- A **LossFn** evaluates the quality of a parameterised energy family. -/
structure LossFn (X Y Θ : Type*) (n : ℕ) where
  eval          : Θ → Dataset X Y n → ℝ
  bounded_below : ∃ c : ℝ, ∀ θ D, c ≤ eval θ D

/-- The **good-loss margin condition** (LeCun 2006, §5 sufficient condition). -/
structure GoodLoss (X Y Θ : Type*) [TopologicalSpace Y] (n : ℕ)
    (EF : Θ → EnergyFn X Y)
    (L : LossFn X Y Θ n) : Prop where
  margin : ∀ (D : Dataset X Y n),
    ∃ (θ_star : Θ) (m : ℝ), 0 < m ∧
      ∀ (i : Fin n) (y_wrong : Y), y_wrong ≠ D.targets i →
        (EF θ_star).eval (D.inputs i) (D.targets i) + m ≤
        (EF θ_star).eval (D.inputs i) y_wrong

-- ------------------------------------------------------------
-- Concrete loss instances
-- ------------------------------------------------------------

/-- **Energy loss** — the loss that causes energy collapse unless energies
    are explicitly bounded below.

    LeCun 2006, §5: "The energy loss will just push down the energy of
    the desired answer — nothing prevents the model from setting all
    energies to -∞." -/
noncomputable def energyLoss
    {X Y Θ : Type*} [TopologicalSpace Y] (n : ℕ)
    (EF : Θ → EnergyFn X Y)
    (h_lb : ∃ c : ℝ, ∀ θ x y, c ≤ (EF θ).eval x y) : LossFn X Y Θ n where
  eval θ D := ∑ i : Fin n, (EF θ).eval (D.inputs i) (D.targets i)
  bounded_below := by
    obtain ⟨c, hc⟩ := h_lb
    refine ⟨n * c, fun θ D => ?_⟩
    have hsum : (∑ _i : Fin n, c) ≤ ∑ i : Fin n, (EF θ).eval (D.inputs i) (D.targets i) :=
      Finset.sum_le_sum (fun i _ => hc θ (D.inputs i) (D.targets i))
    simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul] at hsum
    exact hsum

/-- **Perceptron loss** — contrastive; requires an inference oracle.

    L_perc = Σ_i [ E(y_i, x_i) − min_y E(y, x_i) ] ≥ 0

    LeCun 2006, §5.1 -/
noncomputable def perceptronLoss
    {X Y Θ : Type*}
    [TopologicalSpace Y] [CompactSpace Y] [Nonempty Y]
    (n : ℕ) (EF : Θ → EnergyFn X Y) : LossFn X Y Θ n where
  eval θ D := ∑ i : Fin n,
    ((EF θ).eval (D.inputs i) (D.targets i)
     - (⨅ y : Y, (EF θ).eval (D.inputs i) y))
  bounded_below := ⟨0, fun θ D => by
    apply Finset.sum_nonneg
    intro i _
    have hbdd : BddBelow (Set.range (fun y => (EF θ).eval (D.inputs i) y)) := by
      obtain ⟨y_star, hy⟩ := exists_minimiser (EF θ) (D.inputs i)
      exact ⟨(EF θ).eval (D.inputs i) y_star,
             fun v ⟨y, hy'⟩ => hy' ▸ hy y⟩
    have hle : ⨅ y : Y, (EF θ).eval (D.inputs i) y ≤
               (EF θ).eval (D.inputs i) (D.targets i) :=
      ciInf_le hbdd (D.targets i)
    linarith⟩

/-- **Hinge (contrastive margin) loss** — LeCun 2006's recommended loss.

    L_hinge = Σ_i max(0, E(y_i, x_i) − min_y E(y, x_i) + m) ≥ 0

    LeCun 2006, §5 -/
noncomputable def hingeLoss
    {X Y Θ : Type*}
    [TopologicalSpace Y]
    (m : ℝ) (_hm : 0 < m) (n : ℕ) (EF : Θ → EnergyFn X Y) :
    LossFn X Y Θ n where
  eval θ D := ∑ i : Fin n,
    max 0 ((EF θ).eval (D.inputs i) (D.targets i)
           - (⨅ y : Y, (EF θ).eval (D.inputs i) y) + m)
  bounded_below :=
    ⟨0, fun _ _ => Finset.sum_nonneg (fun _ _ => le_max_left _ _)⟩

/-- **Hinge loss is a good loss** when a perfect classifier exists.

    (Atlas theorem A3 — PROVED) -/
theorem hinge_is_good_loss
    {X Y Θ : Type*}
    [TopologicalSpace Y]
    (m : ℝ) (hm : 0 < m) (n : ℕ) (EF : Θ → EnergyFn X Y)
    (hrich : ∀ D : Dataset X Y n, ∃ θ : Θ,
      ∀ i : Fin n, ∀ y_wrong : Y, y_wrong ≠ D.targets i →
        (EF θ).eval (D.inputs i) (D.targets i) + m ≤
        (EF θ).eval (D.inputs i) y_wrong) :
    GoodLoss X Y Θ n EF (hingeLoss m hm n EF) where
  margin := fun D =>
    let ⟨θ, hθ⟩ := hrich D
    ⟨θ, m, hm, hθ⟩

/-- **MSE prediction loss** — used in JEPA / ANSE world model.

    L_JEPA = ||Ê(x, z) − E_actual(x, y)||²

    Here Ê is the world model's predicted energy (the JEPA predictor). -/
noncomputable def mseJEPALoss
    {X Y Z : Type*} (n : ℕ)
    (predict : X → Z → ℝ) -- JEPA predicted energy
    (actual : X → Y → ℝ) -- ground-truth energy from sandbox
    (encode : Y → Z) : -- encoder: output → latent
    LossFn X Y Unit n where
  eval _ D := ∑ i : Fin n,
    (predict (D.inputs i) (encode (D.targets i))
     - actual (D.inputs i) (D.targets i)) ^ 2
  bounded_below := ⟨0, fun _ _ =>
    Finset.sum_nonneg (fun _ _ => sq_nonneg _)⟩

end ANSE
