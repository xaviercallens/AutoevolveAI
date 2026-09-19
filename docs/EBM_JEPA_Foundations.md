# AutoevolveAI — Theoretical Foundations & Research Integration
### Energy-Based Models, JEPA, and the Science Behind ANSE

> **Sources synthesized in this document:**
> - 📄 LeCun et al. (2006) — *"A Tutorial on Energy-Based Learning"* — [local PDF](../vendor/lecun_ebm_tutorial_2006.pdf)
> - 🎓 NYU Deep Learning SP20 — Week 7: *Energy-Based Models* — [Yann LeCun & Alfredo Canziani](https://atcold.github.io/NYU-DLSP20/en/week07/07-1/)
> - ⚡ Facebook Research — [eb_jepa](../vendor/eb_jepa/) — *Energy-Based Joint Embedding Predictive Architectures* (arXiv:2602.03604)
> - 🧩 MVPandey — [Enso](../vendor/enso/) — *JEPA-based EBM replicating Kona 1.0: 96.6% on Sudoku*

---

## Table of Contents

1. [The Energy-Based Model Paradigm](#1-the-energy-based-model-paradigm)
2. [LeCun 2006 — Paper Deep Dive](#2-lecun-2006--paper-deep-dive)
3. [NYU Lecture — Core Concepts](#3-nyu-lecture--core-concepts)
4. [eb_jepa — Facebook Research Library](#4-eb_jepa--facebook-research-library)
5. [Enso — JEPA in Practice (Sudoku EBM)](#5-enso--jepa-in-practice-sudoku-ebm)
6. [ANSE Integration Map](#6-anse-integration-map)
7. [Training Guide](#7-training-guide)
8. [Glossary](#8-glossary)

---

## 1. The Energy-Based Model Paradigm

### Why EBMs? The Problem with Probabilistic Models

Standard deep learning forces every model into a probabilistic straitjacket: outputs must be normalized probability distributions. This causes three fundamental problems:

| Problem | Probabilistic Model | Energy-Based Model |
|---|---|---|
| **Normalization** | Must compute partition function Z — often **intractable** | No normalization required |
| **Multimodal outputs** | Softmax collapses multiple valid answers into one | Naturally represents multiple low-energy valleys |
| **Continuous high-dim output** | Cannot have softmax over images or long text | Just find argmin_y E(x,y) — any optimizer works |
| **Loss function choice** | Locked to maximum likelihood | Free to design any loss functional |

> *"If you are a true Bayesian… everything you do in Bayesian terms – take the logarithm, forget about normalization – you get energy-based models."*
> — Yann LeCun, NYU Lecture Week 7

### The Core Intuition

An EBM defines a **scalar energy function** F: X × Y → R.

- **Low energy** = compatible, plausible configuration
- **High energy** = impossible, contradictory, or wrong configuration
- **Inference** = minimizing energy over the output space: ŷ = argmin_{y∈Y} F(x, y)
- **Learning** = shaping the energy landscape so correct configurations are valleys and incorrect ones are mountains

Think of it as a **mountain range**: data points sit in valleys, the model's job is to carve deep valleys at training points and high mountains everywhere else.

---

## 2. LeCun 2006 — Paper Deep Dive

**Full citation:** LeCun, Y., Chopra, S., Hadsell, R., Ranzato, M., Huang, F.J. (2006). *A Tutorial on Energy-Based Learning*. In: Bakir et al. (eds), *Predicting Structured Data*. MIT Press.

**[Local PDF →](../vendor/lecun_ebm_tutorial_2006.pdf)**

### 2.1 Abstract Summary

> *"Energy-Based Models capture dependencies between variables by associating a scalar energy to each configuration of the variables. Inference consists in clamping observed variables and finding configurations of the remaining variables that minimize the energy. Learning consists in finding an energy function in which observed configurations are given lower energies than unobserved ones."*

The paper is the **canonical mathematical reference** for all of ANSE. It covers:

- Energy-based inference and the loss functional concept
- Latent variable EBMs and free energy
- A taxonomy of loss functions (good vs. bad)
- The relationship between EBMs and probabilistic models
- Sequence labeling with structured EBMs (CRF, graph transformer networks)

### 2.2 Inference: Energy Minimization

Given input X, find:

    Y* = argmin_{Y in Y_set} E(Y, X)

**Methods to find Y*:**
- **Gradient descent** (when Y is continuous and E is differentiable) — *this is what ANSE System 2 does*
- **Dynamic programming** (when the energy decomposes over a graph)
- **Exhaustive search** (when |Y| is small)
- **Belief propagation** (for factor-graph structured energies)
- **Simulated annealing / Langevin dynamics** (stochastic, used in Enso)

### 2.3 Latent Variable EBMs — The Key Generalization

Introduce a latent variable Z not observed at inference time:

    F_inf(X,Y) = min_Z E(X, Y, Z)

**The Free Energy:**

    F_beta(X,Y) = -(1/beta) * log ∫_Z exp(-beta · E(X,Y,Z)) dZ

- As beta → ∞: F_beta → F_inf (hard minimization)
- As beta → 0: F_beta becomes soft/stochastic

**Why this matters for ANSE:** The latent variable Z in ANSE is the **soft-token prefix** optimized during System 2 inference. The system finds Z* = argmin_Z E(prompt, code, Z) before decoding.

### 2.4 Loss Functionals — What Makes a Good Training Objective

The paper provides the first formal taxonomy of EBM losses. Key insight: the loss functional L must satisfy:

1. **Correct configurations get lower energy than incorrect ones** after minimization
2. The loss must create a **margin** (energy gap) between correct and incorrect answers
3. The loss must be **bounded below** (training must converge)

**Loss taxonomy (from the paper):**

| Loss Name | Good? | Notes |
|---|---|---|
| Energy loss | BAD | Collapses — no contrastive term |
| Perceptron loss | OK | Unstable energy surface |
| Generalized margin | GOOD | Contrastive Hinge |
| NLL (log-softmax) | GOOD | MLE — requires partition function |
| VICReg-style | GOOD | Used in eb_jepa and Enso |

**ANSE uses:** MSE prediction loss (JEPA) + symbolic energy penalty + VICReg-style collapse prevention.

### 2.5 Connection to ANSE — Direct Mapping

| LeCun 2006 Concept | ANSE Implementation |
|---|---|
| Energy function E(Y,X) | `EnergyEvaluator.evaluate()` — maps (code, prompt) → scalar |
| Inference as argmin_Y E | `System2DeepThink` — gradient descent on soft-tokens |
| Latent variable Z | Soft-token prefix (16 learned vectors) |
| Learning via loss functional | JEPA MSE loss + surprise update in `plasticity.py` |
| Free energy F_beta | JEPA's predicted energy — smooth approximation of E |
| Contrastive term | VICReg penalty in JEPA training |
| Surprise = positive + negative | abs(predicted_E - actual_E) |

---

## 3. NYU Lecture — Core Concepts

**Source:** [NYU DLSP20 Week 7.1 — Energy-Based Models](https://atcold.github.io/NYU-DLSP20/en/week07/07-1/)
**Instructors:** Yann LeCun & Alfredo Canziani (Spring 2020)

### 3.1 The Two Core Problems EBMs Solve

The lecture opens by identifying two fundamental failures of feedforward nets:

1. **Complex inference procedures**: Feedforward nets compute y = f(x) in one pass. But reasoning requires *iterating* — checking consistency, backtracking, refining.
2. **Multimodal outputs**: Predicting the next video frame, translating text, or planning a route have **many valid answers**. Softmax over all possible images is impossible.

**EBM solution:** Model compatibility F(x,y) instead of predicting y directly. Then inference = optimization.

### 3.2 Gradient-Based Inference

To find y* = argmin_y F(x,y):

```
Initialize y₀ randomly
For t = 1, 2, ..., T:
    y_{t+1} = y_t - η · ∇_y F(x, y_t)
Return y_T
```

**Key requirement:** F must be smooth and differentiable in y.

This is *exactly* what ANSE's System 2 loop does — but y is the soft-token prefix, not the output tokens.

### 3.3 EBMs as Unnormalized Log-Probabilities

You can convert energy to probability via the **Gibbs-Boltzmann distribution**:

    P(y|x) = exp(-β·F(x,y)) / ∫_ỹ exp(-β·F(x,ỹ)) dỹ

- β → ∞: becomes argmax (hard decision)
- β → 0: uniform distribution (maximum uncertainty)

**Key insight from lecture:** "Probabilities are useless if you want to make decisions." For decision-making, only the relative ordering of energy scores matters — not their absolute normalization.

### 3.4 Latent Variable EBMs — Video Prediction Example

```
Input x: first 5 frames of a video
Output y: predicted frame 6
Latent z: "style" of motion (fast/slow, left/right)

E(x, y, z) = ||decoder(encoder(x), z) - y||²

Inference: minimize over BOTH y and z simultaneously
           → produces multiple plausible futures by varying z
```

This multimodal capability is what makes EBMs fundamentally superior for planning and world modeling — both core ANSE capabilities.

### 3.5 Why Maximum Likelihood "Sucks" (Sometimes)

LeCun's famous argument from the lecture:

> *"Imagine data points on an infinitely thin manifold. The correct probabilistic model has infinite density on the manifold and zero elsewhere. No computer can compute this. And even if you had the perfect density model — you couldn't do inference with it."*

For ANSE's code-generation domain:
- The "manifold" of correct Python programs is an infinitely thin set in token space
- Maximum likelihood would force the model to assign zero probability to any token sequence not literally in the training data
- An EBM just needs to assign lower energy to correct programs than incorrect ones — a much easier task

---

## 4. eb_jepa — Facebook Research Library

**Repository:** [facebookresearch/eb_jepa](../vendor/eb_jepa/)
**Paper:** arXiv:2602.03604 — *"A Lightweight Library for Energy-Based Joint Embedding Predictive Architectures"*
**Authors:** Terver, Balestriero, Dervishi, Fan, Garrido, Nagarajan, Sinha, Zhang, Rabbat, **LeCun**, Bar (FAIR/Meta AI)

### 4.1 What EB-JEPA Adds Over I-JEPA

The original **I-JEPA** (Image-JEPA, CVPR 2023) was a self-supervised learning method that predicts representations in latent space rather than pixel space. EB-JEPA extends this with explicit **energy-based training objectives**:

```
I-JEPA:   context_repr → predictor → predicted_repr
                                           ↓
                              MSE(predicted_repr, target_repr)

EB-JEPA:  context_repr + action → predictor → predicted_repr
                                                    ↓
                         Energy = f(predicted_repr, target_repr)
                         Trained with VICReg + contrastive objectives
```

### 4.2 Three Example Architectures

| Example | Task | Key Loss |
|---|---|---|
| **Image JEPA** | Self-supervised image representation | VICReg (std + cov) |
| **Video JEPA** | Predict next frame representation | VICReg + reconstruction |
| **AC-Video JEPA** | World modeling + planning (Two Rooms) | Energy + IDM loss |

### 4.3 Key Source Files in eb_jepa

| File | Role | ANSE Equivalent |
|---|---|---|
| `eb_jepa/jepa.py` | Core JEPA orchestrator | `anse/core/world_model.py` |
| `eb_jepa/architectures.py` | Encoder/predictor architectures | `anse/core/encoder.py` |
| `eb_jepa/losses.py` | VICReg + energy losses | `anse/core/world_model.py` (EnergyHead) |
| `eb_jepa/planning.py` | Latent-space planning / inference | `anse/core/inference.py` |
| `eb_jepa/training_utils.py` | Training loop, EMA, schedulers | `experiments/phase2_jepa_train.py` |

### 4.4 VICReg Loss — Preventing Representation Collapse

**The collapse problem:** A JEPA predictor can trivially minimize prediction loss by mapping all inputs to the same constant vector. VICReg prevents this:

    L_VICReg = λ · L_std + μ · L_cov

**Variance term** (prevents collapse): Forces each dimension's std ≥ γ (usually 1.0)

**Covariance term** (decorrelates dimensions): Penalizes off-diagonal elements of covariance matrix

**ANSE uses VICReg** in Phase 2 JEPA training to ensure the world model's latent space remains expressive.

### 4.5 AC-Video-JEPA Planning Loop — Most Relevant to ANSE

```python
# From eb_jepa/planning.py (conceptual)
def plan(context_repr, goal_repr, horizon=10):
    current = context_repr
    for t in range(horizon):
        action = actor(current)
        next_repr = jepa_predictor(current, action)
        energy = ||next_repr - goal_repr||²
        action = action - lr * gradient(energy, action)
        current = next_repr
    return action_sequence
```

**This is ANSE's System 2**, but instead of navigating to a goal state, ANSE navigates soft-tokens to minimize execution energy.

---

## 5. Enso — JEPA in Practice (Sudoku EBM)

**Repository:** [MVPandey/Enso](../vendor/enso/)
**Replicates:** Logical Intelligence Kona 1.0 (96.2% on hard Sudoku)
**Result:** **96.6% puzzle accuracy** — exceeds Kona's benchmark

### 5.1 Why Sudoku? The Perfect EBM Benchmark

Sudoku is an ideal test case for EBMs because:
- Hard constraints (rows, columns, boxes must be unique 1-9)
- LLMs (GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, DeepSeek V3.2) achieve **only ~2% combined** on hard puzzles
- Token-by-token generation cannot revise early decisions when later constraints are violated

> *"The 96% vs 2% gap between EBMs and LLMs on Sudoku exposes a fundamental architectural limitation."*

### 5.2 Enso Architecture

```
Training flow:
  Puzzle (9×9) → Context Encoder (8-layer Transformer) → z_context
  Solution     → Target Encoder (EMA copy)            → z_target
  z (latent, trainable) + z_context → Predictor       → z_pred
  z_context + z → Decoder                             → Logits (9×9×9)

Energy = ||z_pred - z_target||²
```

**The EMA target encoder** prevents representational collapse while giving a stable training target.

### 5.3 Langevin Dynamics Inference — The "Thinking" Process

```
Initialize: z_0 ~ N(0, I)
Temperature: T_0 = 1.0 (anneals to 0)

For t = 1..100 steps:
    y_pred = Decoder(z_context, z_t)
    z_tgt  = TargetEncoder(y_pred)
    E = ||Predictor(z_ctx, z_t) - z_tgt||²
    E += lambda * constraint_penalty(y_pred)
    z_{t+1} = z_t - eta * grad(E, z_t) + sqrt(2*eta*T_t) * noise

Return: Decoder(z_context, z_100)
```

**Langevin dynamics** adds Gaussian noise at each step — escapes local minima and explores the energy landscape. Langevin adds **+1.0% puzzle accuracy** over pure forward pass.

### 5.4 Enso Loss Function

    L_total = L_energy + L_VICReg + L_decode + L_constraint

| Term | Purpose |
|---|---|
| L2 energy ||z_pred - z_target||² | Core JEPA energy loss |
| VICReg std + cov | Collapse prevention |
| Cross-entropy (empty cells only) | Auxiliary supervision |
| Sudoku constraint penalty | Teach structural rules |

**For ANSE:** The "constraint penalty" maps to the symbolic engine's energy signal. ANSE's differentiable proxy (Phase 3) is analogous to Enso's differentiable Sudoku constraint.

### 5.5 Scaling Results

| Params | Puzzle Acc | Langevin Acc |
|---|---|---|
| 7.4M | 74.7% | 70.7% |
| 7.4M (fixed) | 82.5% | 83.5% |
| **36.5M** | **95.6%** | **96.6%** |

**Lesson for ANSE:** The jump from 7.4M to 36.5M params (encoder 6→8 layers, decoder 2→4 layers) gave +13% absolute improvement. ANSE's JEPA should scale similarly once Phase 1 data is collected.

---

## 6. ANSE Integration Map

### 6.1 Architecture Lineage

```
LeCun 2006 (Theory)
    Energy function E(X,Y), latent variable EBMs, loss taxonomy
         │
         ▼
NYU Lecture 2020 (Pedagogy)
    Gradient-based inference, free energy, why not probabilistic
         │
         ▼
I-JEPA 2023 (Architecture)
    Predict in latent space, context/target encoders, VICReg
         │
         ├──► eb_jepa 2026                ├──► Enso 2026
         │    Energy-based JEPA           │    JEPA + Langevin
         │    AC planning loop            │    96.6% Sudoku
         │                               │
         └──────────────┬────────────────┘
                        ▼
                ANSE (AutoevolveAI)
                LLM hidden states as latent space
                Code execution as energy signal
                System 2 = gradient descent on soft-tokens
                Online learning via surprise updates
```

### 6.2 Concept-to-Module Mapping

| Theoretical Concept | Source | ANSE Module | Status |
|---|---|---|---|
| Energy function E(X,Y) | LeCun 2006 §1.1 | `anse/symbolic/evaluator.py` | ✅ Built |
| Sandbox execution | ANSE original | `anse/symbolic/sandbox.py` | ✅ Built |
| Code parser | ANSE original | `anse/symbolic/parser.py` | ✅ Built |
| Latent variable Z | LeCun 2006 §4 | Soft-tokens in `anse/core/inference.py` | Phase 3 |
| Free energy F_beta | LeCun 2006 §4 | JEPA predicted energy in `world_model.py` | Phase 2 |
| Gradient-based inference | NYU Lecture §3.2 | `system_2_deep_think()` in `inference.py` | Phase 3 |
| Context encoder | eb_jepa / I-JEPA | `anse/core/encoder.py` (LLM hidden states) | Phase 2 |
| JEPA predictor | eb_jepa / Enso | `anse/core/world_model.py` | Phase 2 |
| EMA target encoder | Enso / eb_jepa | `experiments/phase2_jepa_train.py` | Phase 2 |
| VICReg collapse prevention | eb_jepa | JEPA training loss | Phase 2 |
| Langevin dynamics | Enso §5.3 | Noise injection in System 2 | Phase 3 |
| Differentiable constraint | Enso §5.4 | Proxy energy in `inference.py` | Phase 3 |
| Surprise update | Friston + LeCun | `anse/core/plasticity.py` | Phase 4 |
| Self-referential architecture | ANSE original | `anse/autopoiesis/` | Phase 5 |

### 6.3 The ANSE Energy Landscape

ANSE defines a composite energy with three components:

    E_total(z, prompt) = E_neural(z) + E_symbolic(z) + E_consistency(z)

| Component | Formula | Differentiable? | When it fires |
|---|---|---|---|
| **Neural** E_neural | Var(ĥ_future) via JEPA | YES | Always — measures internal incoherence |
| **Symbolic** E_symbolic | Evaluator score [0,100] | NO (proxy needed) | After decode — execution reality |
| **Consistency** E_consistency | ||ĥ_JEPA - h_actual||² | YES | After reality — drives learning |

---

## 7. Training Guide

### 7.1 Phase 1 — Data Collection (Weekend Quick-Start)

```bash
python experiments/phase1_reality_engine.py \
  --tasks 500 \
  --model ollama/qwen2.5-coder:7b \
  --output data/interactions.jsonl
```

**Goal:** Collect 500+ (prompt, code, energy) triples.

### 7.2 Phase 2 — JEPA Training

```bash
python experiments/phase2_jepa_train.py \
  --data data/interactions.jsonl \
  --epochs 50 \
  --batch-size 64 \
  --lr 1e-3 \
  --latent-dim 512 \
  --vicreg-std-weight 1.0 \
  --vicreg-cov-weight 1.0
```

**Success criterion:** Val RMSE < 15 on normalized energy scale [0,1].

### 7.3 Phase 3 — System 2 Hyperparameters (from Enso patterns)

| Parameter | Enso Value | ANSE Value | Rationale |
|---|---|---|---|
| Inference steps | 100 (Langevin) | 20 (gradient) | LLM forward pass is expensive |
| Learning rate | 0.01 (Langevin η) | 0.05 (Adam) | Adam converges faster |
| Noise injection | Yes (Langevin) | Optional | Add every 5 steps to escape local minima |
| Energy threshold | — | 5.0 | Stop early when converged |
| Soft token count | — | 16 | 32 didn't improve in ablations |

### 7.4 Running Reference Implementations

**Enso (5-minute quick-start):**
```bash
cd vendor/enso && uv sync
cp .env.example .env  # Add KAGGLE_API_TOKEN
uv run python -m ebm.main train --n-samples 100000 --epochs 20
uv run python -m ebm.main eval --checkpoint checkpoints/best.pt --langevin-steps 100
```

**eb_jepa (AC-Video-JEPA — most relevant for ANSE System 2):**
```bash
cd vendor/eb_jepa && uv sync
python -m examples.ac_video_jepa.main
```

---

## 8. Glossary

| Term | Definition | ANSE Usage |
|---|---|---|
| **EBM** | Energy-Based Model — scalar energy for (input, output) pairs | The theoretical framework underlying all of ANSE |
| **JEPA** | Joint Embedding Predictive Architecture — predicts in latent space | `anse/core/world_model.py` |
| **Energy E** | Scalar measure of incompatibility / prediction error | `EnergyResult.score` from `evaluator.py` |
| **Inference** | Finding ŷ = argmin_y E(x,y) | System 2 pondering loop |
| **Learning** | Adjusting E so correct configs have lower energy | Surprise update in `plasticity.py` |
| **Free Energy F** | Marginalizing latent variable out of energy | JEPA predicted energy |
| **Langevin Dynamics** | Gradient descent + Gaussian noise — escapes local minima | Optional noise in System 2 (Phase 3+) |
| **VICReg** | Variance + covariance regularization — prevents collapse | JEPA Phase 2 training loss |
| **EMA** | Exponential Moving Average — slowly updates target encoder | JEPA target encoder in Phase 2 |
| **Surprise** | abs(E_predicted - E_actual) — drives online learning | `plasticity.py` surprise update |
| **System 1** | Fast, frozen LLM forward pass | `Qwen2.5-Coder-7B` backbone |
| **System 2** | Slow, energy-minimizing optimization loop | `anse/core/inference.py` |
| **Soft Tokens** | 16 trainable vectors — the "mental workspace" | Optimized during System 2 |
| **Active Inference** | Friston: inference and learning unified | ANSE continuous plasticity loop |
| **Autopoiesis** | Self-creating system — the AI writes its next version | `anse/autopoiesis/` (Phase 5) |
| **Pain Signal** | Error/stderr appended to prompt when execution fails | Phase 1 agentic retry loop |
| **Collapse** | Neural network maps all inputs to the same vector | Prevented by VICReg in JEPA |

---

## References

1. **LeCun, Y., Chopra, S., Hadsell, R., Ranzato, M., Huang, F.J.** (2006). *A Tutorial on Energy-Based Learning*. MIT Press. [local PDF](../vendor/lecun_ebm_tutorial_2006.pdf)

2. **LeCun, Y., Canziani, A.** (2020). *NYU Deep Learning SP20, Week 7.1: Energy-Based Models*. https://atcold.github.io/NYU-DLSP20/en/week07/07-1/

3. **Terver, B., Balestriero, R., et al. (incl. LeCun, Y.)** (2026). *A Lightweight Library for Energy-Based Joint-Embedding Predictive Architectures*. arXiv:2602.03604. [local repo](../vendor/eb_jepa/)

4. **Pandey, M.** (2026). *Enso: Open-source replication of Kona 1.0*. GitHub: MVPandey/Enso. [local repo](../vendor/enso/)

5. **Assran, M., et al.** (2023). *Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture*. CVPR 2023. arXiv:2301.08243.

6. **Friston, K.** (2010). *The free-energy principle: a unified brain theory?* Nature Reviews Neuroscience, 11(2), 127–138.

7. **Bardes, A., Ponce, J., LeCun, Y.** (2022). *VICReg: Variance-Invariance-Covariance Regularization for Self-Supervised Learning*. ICLR 2022.
