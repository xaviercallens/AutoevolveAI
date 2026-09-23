# Phase 4: Formal Mathematician (Interactive Theorem Proving & SOTA RAG)

## Objective
Transform the ANSE reasoning engine from a fragile Zero-Shot code generator into an autonomous **Formal Mathematician** capable of:
1. Grounded **Premise Selection** across Mathlib4's 130,000+ declarations.
2. Step-by-step interactive tactic progression via the **Lean 4 Compiler REPL / LeanDojo**.
3. **MCTS Backtracking** and Red Team auditing to block Epistemic Cheating (e.g. replacing manifolds with algebraic fractions).
4. Converting `UNVERIFIED_IN_LEAN` failures into `VERIFIED_SOUND` mathematical certificates.

---

## 1. SOTA Ecosystem & Repository Alignment

The ANSE framework formally aligns with the leading 2024–2025 AI-for-Mathematics architectures:

| Project | Source / Reference | Role in ANSE Architecture |
|---|---|---|
| **LeanDojo** | [lean-dojo/LeanDojo](https://github.com/lean-dojo/LeanDojo) (NeurIPS 2023) | Programmatic REPL for Lean 4, environment interaction, and AST extraction (`vendor/LeanDojo`). |
| **Lean Finder** | [delta-lab-ai/lean-finder](https://github.com/delta-lab-ai/lean-finder) (ICLR 2025) | FAISS-based semantic vector search engine custom-trained on Mathlib4 formal syntax. |
| **Mathlib4 AST & Docs** | [leanprover/lean4-api-docs](https://github.com/leanprover/lean4-api-docs) / `doc-gen4` | Structured declaration extraction (theorems, types, docstrings, module paths) across `formal/.lake/packages/mathlib/Mathlib`. |
| **Goedel's Poetry / ImProver** | [KellyJDavis/goedels-poetry](https://github.com/KellyJDavis/goedels-poetry), [riyazahuja/improver](https://github.com/riyazahuja/improver) | Multi-turn LangGraph agentic loop with MCTS tactic rollback on compiler failure. |
| **LeanSearchClient & Loogle** | `formal/.lake/packages/LeanSearchClient` / [Loogle API](https://loogle.lean-lang.org/json) | Online semantic premise search integrated directly into the Lean 4 environment. |

---

## 2. Core Implementation: `anse/symbolic/lean_rag_dojo.py`

The ANSE engine provides two decoupled, high-performance components:

### A. `MathlibPremiseRetriever`
- **Storage:** ChromaDB persistent collection at `./mathlib_rag_db` (or Milvus).
- **Extraction:** Recursively parses `.lean` files in `formal/.lake/packages/mathlib/Mathlib/` to extract module paths, signatures, and docstrings.
- **Premise Injection:** Formats retrieved theorems into exact import directives:
  ```lean
  USEFUL MATHLIB PREMISES:
  import Mathlib.Topology.Order.IntermediateValue
  theorem intermediate_value_Icc {a b : α} (hab : a ≤ b) (hf : ContinuousOn f (Icc a b)) : Icc (f a) (f b) ⊆ f '' Icc a b
  ```

### B. `LeanCompilerREPL` & `InteractiveFormalProver`
- Direct execution via `lake env lean` within the verified Lake environment.
- Captures compiler diagnostics, unsolved tactic states (`⊢ Goal`), and error traces.
- MCTS backpropagation: on `TacticError` or typeclass failure, records the failure mode to prune dead tactic branches.
- **Anti-Cheat Radar:** Explicitly checks that tactics do not rely on `sorry`, `admit`, or degenerate real-arithmetic reductions for topological tasks.

---

## 3. Milestones Achieved: P11 to P20 Formally Verified

Using this RAG & compiler-grounded pipeline, problems **P11 through P20** have been formally verified in Lean 4 with **0 errors, 0 warnings, and 0 sorry**:

| Problem ID | Title | Key Mathlib Premise Retrieved | Verification File | Status |
|---|---|---|---|---|
| **P11** | Intermediate Value Theorem (IVT) | `intermediate_value_Icc`, `ContinuousOn` | `ANSE.MasterMathTribunal_Part2` | **VERIFIED_SOUND** |
| **P12** | Cayley-Hamilton Theorem | `Matrix.aeval_self_charpoly`, `Polynomial` | `ANSE.MasterMathTribunal_Part2` | **VERIFIED_SOUND** |
| **P13** | Zorn's Lemma | `zorn_le`, `IsMax` | `ANSE.MasterMathTribunal_Part2` | **VERIFIED_SOUND** |
| **P14** | Baire Category Theorem | `BaireSpace.baire_property` | `ANSE.MasterMathTribunal_Part2` | **VERIFIED_SOUND** |
| **P15** | Cantor's Theorem | Constructive diagonalisation (`¬ Surjective f`) | `ANSE.MasterMathTribunal_Part2` | **VERIFIED_SOUND** |
| **P16** | Infinitude of Primes | `Nat.exists_infinite_primes` | `ANSE.MasterMathTribunal_Part2` | **VERIFIED_SOUND** |
| **P17** | AM-GM Inequality ($n=2$) | `sq_nonneg`, `Real.sq_sqrt`, `Real.sqrt_mul` | `ANSE.MasterMathTribunal_Part2` | **VERIFIED_SOUND** |
| **P18** | Irrationality of $\sqrt{2}$ | `irrational_sqrt_two` | `ANSE.MasterMathTribunal_Part2` | **VERIFIED_SOUND** |
| **P19** | 2 is Prime | `Nat.prime_two` | `ANSE.MasterMathTribunal_Part2` | **VERIFIED_SOUND** |
| **P20** | Metric Space Triangle Inequality | `dist_triangle` | `ANSE.MasterMathTribunal_Part2` | **VERIFIED_SOUND** |

All 2,605 jobs in `cd formal && lake build` build and compile successfully.

---

## 4. Next Frontier: P21-P25 & Theoretical Physics

1. **P21 (Picard-Lindelöf):** Leverage `Mathlib.Analysis.ODE.PicardLindelof` for existence and uniqueness of ODE flows.
2. **P22 (Stokes' Theorem):** Utilize `Mathlib.Analysis.Calculus.DifferentialForms.Basic` and manifold boundary integration.
3. **P23 (Sylow's First Theorem):** Retrieve `Sylow.exists_subgroup_card_pow_prime` from `Mathlib.GroupTheory.Sylow`.
4. **P24 (Spectral Theorem):** Retrieve `Matrix.IsSymm.has_eigenvector` and orthogonal diagonalization.
5. **P25 (Heine-Borel):** Retrieve `isCompact_iff_isClosed_bounded` from `Mathlib.Topology.MetricSpace.ProperSpace.Real`.
6. **Physics P26-P50:** Shift from ASCII pseudocode to formal bundles (Symplectic Manifolds, Hilbert Spaces, Bundle Connections).
