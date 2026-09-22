---
name: scientific-publication
description: Autonomous scientific paper generation, formal mathematical proof embedding, arXiv reference grounding, anti-hallucination code execution, and publication-ready LaTeX/PDF compilation.
---

# Scientific Publication Skill: Autonomous Zero-Hallucination Academic Pipeline

This skill governs the autonomous authoring, formal mathematical verification, reference grounding, and LaTeX/PDF compilation of scientific papers in the ANSE / Antigravity ecosystem.

---

## 1. The Core Scientific Mandate

When generating scientific papers, articles, and technical reports:
1. **The LLM Must NEVER Perform Freehand Numeric Calculation:**
   All numeric values, invariant errors, benchmark timings, peak RAM metrics, and physical parameters must be derived by executing Python code in the sandbox. The resulting stdout/receipt must be programmatically injected into tables and text.
2. **The 4 Definitions Contract:**
   Every physical phenomenon and world model presented in an ANSE paper must be articulated through four formal definitions:
   - **Definition A: Physical & Mathematical Formulation:** Differential equations, Hamiltonian $\mathcal{H}$, Lagrangian $\mathcal{L}$, or governing partial differential equations (PDEs).
   - **Definition B: Conservation Laws & Invariant Functional:** Exact algebraic invariant $\mathcal{I}(s) = 0$ (e.g. Peters-Mathews energy balance, canonical momentum $P_\phi$, Chern topological number $\mathcal{C}$, entropy production non-negativity $\partial_\mu S^\mu \ge 0$).
   - **Definition C: Algorithmic Discretization & Solver Scheme:** Exact numerical integration scheme (e.g. 4th-Order Runge-Kutta, Symplectic Velocity-Verlet, Heun predictor-corrector, 2D Riemannian quadrature).
   - **Definition D: Quantitative Acceptance Threshold & Gate:** Mathematical tolerance $\epsilon_{\text{tol}}$ and failure penalty functional $\Pi_{\text{penalty}} = 10^6$.
3. **Grounded Academic Citations Only:**
   Never cite papers from internal LLM memory. The skill queries arXiv over HTTPS, retrieves authentic abstracts, authors, and DOIs, and writes verified references to `papers/references/`.
4. **Publication-Grade LaTeX & Vector Diagrams:**
   All mathematical equations must be formatted in standard AMS-LaTeX (`align*`, `equation`). Diagrams and visualizations must be generated as high-resolution vector PDF/PNG figures using Python (`matplotlib`) and embedded in the LaTeX document.

---

## 2. Standard Workflow Commands

```bash
# 1. Fetch grounded citations from arXiv
uv run python scripts/generate_scientific_paper.py

# 2. Generate publication figures via Python
python3 scripts/generate_paper_figures.py

# 3. Generate LaTeX source and compile to PDF
python3 scripts/build_latex_paper.py

# 4. Review paper via Gemini 3.1 Pro protocol
python3 scripts/review_paper_gemini_pro.py

# 5. Verify zero stubs and mint attestation proof
uv run python execution_attestation.py antigravity_harness.core.paper_harness tests/test_paper_harness.py
```

---

## 3. Gemini 3.1 Pro Scientific Review Protocol

The peer review rubric evaluates papers across five physical criteria:
1. **Mathematical Rigor & Notation:** Correct tensor indices, operator dimensions, and PDE formulation.
2. **Physical Conservation Law Validity:** Zero ungrounded or violated invariants ($\Delta E < 0$).
3. **Anti-Hallucination Integrity:** 100% of numeric table rows correspond to verified execution receipts.
4. **Literature Grounding:** Citations resolve to authenticated preprints or journal publications.
5. **Autopoietic Rebuild Feasibility:** Clear description of context management, review loops, and live hot-swapping.
