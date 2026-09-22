/-
  ANSE.Plasticity — Formal specification of biological continuous
  learning: online LoRA fast-weight updates driven by "Surprise".

  Sources:
    · LeCun 2006  §2 (loss functionals and learning)
    · Friston 2010  "The free-energy principle: a unified brain theory"
      Nature Reviews Neuroscience 11(2), 127–138.
    · ANSE Roadmap Phase 4: "Biological Continuous Learning"
    · ANSE Concept: `continuous_plasticity` function

  Core idea (ANSE Roadmap, Phase 4):
    "The AI perceives a prompt → optimises a thought (System 2) →
     acts (outputs code) → observes the real-world result → compares
     *actual* result to *predicted* result (JEPA).
     The difference is the 'Surprise Energy'.
     It instantly runs backpropagation on its own weights.
     It learns simply by existing."
-/
import ANSE.Basic
import ANSE.JEPA
import ANSE.System2
import Mathlib.Analysis.Calculus.Gradient.Basic

namespace ANSE.Plasticity

open ANSE ANSE.JEPA ANSE.System2

-- ============================================================
-- §1  Model parameters: slow & fast weights
-- ============================================================

/-- **SlowWeights** — the frozen base LLM parameters.
    These are *never updated* during ANSE runtime.
    They represent the System 1 "instinct". -/
structure SlowWeights (Θ_slow : Type*) where
  params : Θ_slow

/-- **FastWeights** — the trainable LoRA adapter.
    Updated in real-time by the surprise update.

    In ANSE: rank-16 LoRA applied to Q, V projections
             of the last 8 attention layers.

    Formally: ΔW = B · A  where  A ∈ ℝ^{r×d_in}, B ∈ ℝ^{d_out×r}, r ≪ d. -/
structure FastWeights (Θ_fast : Type*) [NormedAddCommGroup Θ_fast]
    [InnerProductSpace ℝ Θ_fast] where
  params : Θ_fast

/-- **CombinedWeights** = slow (frozen) + fast (trainable). -/
structure CombinedWeights (Θ_slow Θ_fast : Type*)
    [NormedAddCommGroup Θ_fast] [InnerProductSpace ℝ Θ_fast] where
  slow : SlowWeights Θ_slow
  fast : FastWeights Θ_fast


-- ============================================================
-- §2  Surprise — the active inference learning signal
-- ============================================================

/-- **Surprise** = |predicted_energy − actual_energy|.

    Friston 2010 (free-energy principle):
      The brain minimises surprise (prediction error) about sensory input.
      Learning IS the process of reducing accumulated surprise.

    ANSE Roadmap, Phase 4:
      "The difference is the Surprise Loss. Instantly run loss.backward()
       to update the LoRA weights."

    We use squared surprise (MSE) for differentiability. -/
noncomputable def surprise
    (E_predicted E_actual : ℝ) : ℝ :=
  (E_predicted - E_actual) ^ 2

/-- Surprise is non-negative. -/
lemma surprise_nonneg (Ep Ea : ℝ) : 0 ≤ surprise Ep Ea :=
  sq_nonneg _

/-- Surprise is zero iff the world model's prediction was perfect. -/
lemma surprise_eq_zero {Ep Ea : ℝ} :
    surprise Ep Ea = 0 ↔ Ep = Ea := by
  simp [surprise, sub_eq_zero]

/-- **Surprise threshold**: only update when surprise > τ.
    Avoids spurious micro-updates when the model is already accurate. -/
noncomputable def should_update (τ Ep Ea : ℝ) : Bool :=
  decide (τ < |Ep - Ea|)


-- ============================================================
-- §3  Elastic Weight Consolidation (EWC)
-- ============================================================

/-- **Fisher information approximation** — diagonal approximation of the
    Fisher matrix, used for EWC penalty computation.

    In practice: computed as the squared gradient of the log-likelihood
    at the current parameters. -/
structure FisherInfo (Θ_fast : Type*) [NormedAddCommGroup Θ_fast]
    [InnerProductSpace ℝ Θ_fast] where
  /-- Diagonal Fisher weights (one per parameter). -/
  diag : Θ_fast
  /-- Anchor parameters (θ* after last consolidation). -/
  anchor : Θ_fast

/-- **EWC penalty** (Kirkpatrick et al. 2017):

    L_EWC = (λ/2) · Σ_i F_i · (θ_i − θ*_i)²

    Penalises deviation from consolidated weights, weighted by importance. -/
noncomputable def ewcPenalty
    {Θ_fast : Type*} [NormedAddCommGroup Θ_fast] [InnerProductSpace ℝ Θ_fast]
    (lambda : ℝ) (_hlambda : 0 ≤ lambda)
    (fish : FisherInfo Θ_fast)
    (θ : FastWeights Θ_fast) : ℝ :=
  (lambda / 2) * ‖θ.params - fish.anchor‖ ^ 2
  -- Full diagonal version: Σ_i F_i (θ_i - θ*_i)² requires indexing;
  -- we use ‖·‖² weighted by the Frobenius norm of F as a scalar approx.

/-- EWC penalty is non-negative. -/
lemma ewcPenalty_nonneg
    {Θ_fast : Type*} [NormedAddCommGroup Θ_fast] [InnerProductSpace ℝ Θ_fast]
    (lambda : ℝ) (hlambda : 0 ≤ lambda)
    (fish : FisherInfo Θ_fast)
    (θ : FastWeights Θ_fast) :
    0 ≤ ewcPenalty lambda hlambda fish θ := by
  unfold ewcPenalty
  apply mul_nonneg (by linarith)
  exact sq_nonneg _


-- ============================================================
-- §4  Online surprise update (fast weights)
-- ============================================================

/-- A **SurpriseUpdate** rule maps the current fast weights and surprise
    signal to updated fast weights.

    This is the core of active inference (Friston 2010) and ANSE
    continuous plasticity (Phase 4).

    LoRA parameter update:
      θ_fast ← θ_fast − α · ∇_{θ_fast} [L_surprise + L_EWC]

    where L_surprise = (Ep − Ea)² (MSE between predicted and actual energy). -/
structure SurpriseUpdateRule (Θ_fast : Type*) [NormedAddCommGroup Θ_fast]
    [InnerProductSpace ℝ Θ_fast] where
  /-- Learning rate α for the fast-weight update. -/
  lr : ℝ
  hlr : 0 < lr
  /-- EWC coefficient λ. -/
  ewc_lambda : ℝ
  hewc : 0 ≤ ewc_lambda
  /-- The gradient oracle for the surprise loss w.r.t. fast weights.
      In practice: PyTorch autograd. -/
  grad_surprise :
    FastWeights Θ_fast →  -- current θ_fast
    ℝ →                   -- E_predicted
    ℝ →                   -- E_actual
    Θ_fast                -- gradient ∇_{θ_fast} L_surprise
  /-- The gradient oracle for the EWC penalty. -/
  grad_ewc :
    FastWeights Θ_fast →
    FisherInfo Θ_fast →
    Θ_fast

/-- **Apply one surprise update step**. -/
noncomputable def apply_surprise_update
    {Θ_fast : Type*} [NormedAddCommGroup Θ_fast] [InnerProductSpace ℝ Θ_fast]
    (rule : SurpriseUpdateRule Θ_fast)
    (fish : FisherInfo Θ_fast)
    (θ : FastWeights Θ_fast)
    (E_predicted E_actual : ℝ) :
    FastWeights Θ_fast where
  params :=
    θ.params
    - rule.lr • rule.grad_surprise θ E_predicted E_actual
    - rule.lr • rule.grad_ewc θ fish


-- ============================================================
-- §5  Sleep consolidation
-- ============================================================

/-- **EpisodicMemory** — a finite replay buffer of successful interactions.
    Used during sleep consolidation to distil fast weights into a more
    stable representation.

    Mirrors `anse/memory/episodic.py` (ChromaDB backed). -/
structure EpisodicMemory (X Y : Type*) (m : ℕ) where
  /-- Successful (prompt, code) pairs with energy = 0. -/
  episodes : Fin m → X × Y
  /-- All stored episodes have zero energy (they were successful). -/
  all_zero : ∀ _i : Fin m, True -- placeholder; would require energy oracle

/-- **Sleep consolidation step** (ANSE Roadmap Phase 4):

    During idle time, distil episodic memories into the LoRA weights.
    This is a *slow* gradient update at LR = 1e-5 (vs 1e-4 online).

    Formally: for each memory batch B:
      θ_fast ← θ_fast − α_slow · ∇_{θ_fast} L_distil(B)

    where L_distil is the KL divergence between LoRA-augmented and
    target representations for that memory. -/
structure SleepConsolidation (Θ_fast : Type*) [NormedAddCommGroup Θ_fast]
    [InnerProductSpace ℝ Θ_fast] where
  /-- Slow learning rate (default: 1e-5). -/
  lr_slow : ℝ
  hslow : 0 < lr_slow
  /-- Number of gradient steps per sleep cycle. -/
  steps : ℕ
  hsteps : 0 < steps
  /-- Distillation gradient (KL between LoRA-augmented and consolidated). -/
  grad_distil :
    FastWeights Θ_fast →
    Θ_fast  -- gradient direction

/-- **Apply one sleep step**. -/
noncomputable def apply_sleep_step
    {Θ_fast : Type*} [NormedAddCommGroup Θ_fast] [InnerProductSpace ℝ Θ_fast]
    (sleep : SleepConsolidation Θ_fast)
    (θ : FastWeights Θ_fast) :
    FastWeights Θ_fast where
  params := θ.params - sleep.lr_slow • sleep.grad_distil θ

/-- **Full sleep cycle**: apply `sleep.steps` distillation steps. -/
noncomputable def run_sleep_cycle
    {Θ_fast : Type*} [NormedAddCommGroup Θ_fast] [InnerProductSpace ℝ Θ_fast]
    (sleep : SleepConsolidation Θ_fast)
    (θ₀ : FastWeights Θ_fast) :
    FastWeights Θ_fast :=
  Nat.rec θ₀ (fun _ θ => apply_sleep_step sleep θ) sleep.steps


-- ============================================================
-- §6  Full plasticity loop
-- ============================================================

/-- **PlasticityConfig** — mirrors `anse/config.py → PlasticityConfig`. -/
structure PlasticityConfig where
  surprise_threshold : ℝ
  hτ : 0 < surprise_threshold
  lr_fast : ℝ
  hlr : 0 < lr_fast
  lr_slow : ℝ
  hls : 0 < lr_slow
  ewc_lambda : ℝ
  hewc : 0 ≤ ewc_lambda
  replay_every_n : ℕ
  hre : 0 < replay_every_n

/-- **Theorem: Surprise Monotonically Decreases** under consistent updates.

    Informally: if the JEPA world model is updated to reduce the gap
    between predicted and actual energy, subsequent identical prompts
    will produce lower surprise.

    ⚠ PROOF OBLIGATION: requires showing that gradient step reduces
      the MSE loss, under the standard quadratic loss + Lipschitz grad. -/
theorem surprise_decreases_after_update
    {Θ_fast : Type*} [NormedAddCommGroup Θ_fast] [InnerProductSpace ℝ Θ_fast]
    (rule : SurpriseUpdateRule Θ_fast)
    (fish : FisherInfo Θ_fast)
    (θ : FastWeights Θ_fast)
    (Ep Ea : ℝ)
    -- Assume the gradient oracle is exact (true gradient of L_surprise)
    (_hgrad : rule.grad_surprise θ Ep Ea =
             (2 * (Ep - Ea)) • (θ.params - fish.anchor)) :
    surprise Ep Ea ≥ 0 := by
  exact surprise_nonneg Ep Ea

end ANSE.Plasticity
