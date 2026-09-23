# Phase 4: Formal Mathematician (Interactive Theorem Proving)

## Objective
Transition ANSE from a "Zero-Shot Code Generator" to a "Formal Mathematician" capable of interacting continuously with the Lean 4 compiler via REPL, augmented by Mathlib RAG and specialized open-weight models.

## Architectural Pillars

### 1. Interactive REPL (The "Eyes")
- **Mechanism:** Submit single tactics (e.g., `intro x hx`) and receive the exact Tactic State (hypotheses and current `⊢ Goal`) instead of submitting entire `.lean` files blindly.
- **Tools:** Integration of [LeanDojo](https://github.com/lean-dojo/LeanDojo) or [leanprover-community/repl](https://github.com/leanprover-community/repl).
- **Benefit:** Enables immediate error-checking (e.g., "tactic 'ring' failed") and dynamic backtracking (MCTS).

### 2. Mathlib4 RAG (Retrieval-Augmented Formalization)
- **Mechanism:** Vector search on Mathlib4 to retrieve correct import paths and lemma signatures prior to tactic execution.
- **Tools:** Local ChromaDB indexing the Mathlib4 ecosystem.
- **Benefit:** Eliminates hallucinated syntax and pseudo-mathematics by injecting rigorous, contextually relevant theorems (e.g., finding `intermediate_value_Icc` for the IVT).

### 3. "Sorry-Driven" Tree Search
- **Draft:** Gemini 1.5 Pro formulates an informal physics/math proof in LaTeX.
- **Sketch:** Claude 3.5 Sonnet structures the Lean 4 skeleton, replacing complex steps with `sorry`.
- **Prove:** Sub-agents (using Specialized SLMs) tackle each `sorry` individually via the Interactive REPL.
- **Assemble:** The Red Team verifies the aggregated, `sorry`-free `.lean` file.

### 4. Specialized Open-Weight Provers
- **Mechanism:** Deploy specialized SLMs (Small Language Models) trained via RL for Lean 4.
- **Tools:** DeepSeek-Prover-V1.5 (7B) or InternLM-Math-Plus hosted locally (vLLM/Ollama).
- **Benefit:** Highly efficient, high-throughput tactic generation for Monte Carlo Tree Search at zero marginal API cost.

## Immediate Target (Proof of Concept)
Apply the Interactive Agent Loop to solve:
1. **P11 (Intermediate Value Theorem)**
2. **P17 (AM-GM Inequality)**

Goal: Flip their status from `UNVERIFIED_IN_LEAN` to `VERIFIED_SOUND`.
