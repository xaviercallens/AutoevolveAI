---
name: scientific-publication
description: >-
  Autonomous scientific paper generation with zero-hallucination telemetry,
  real accuracy metrics, honest Lean 4 invariant framing, arXiv-grounded
  citations, and publication-ready XeLaTeX/PDF compilation. Enforces a
  multi-criterion peer review protocol that has been validated through a
  Strong-Reject → Accept cycle. Use this skill when writing, revising, or
  publishing any scientific paper in the ANSE / AutoevolveAI ecosystem.
---

# Scientific Publication Skill (v2 — Post Strong-Reject Lessons)

This skill governs autonomous authoring, formal verification embedding,
reference grounding, and LaTeX/PDF compilation of papers in the ANSE ecosystem.
It incorporates lessons from a full peer-review cycle that turned a Strong Reject
into an Accept (Systems for ML / MLOps Track).

---

## 0. Pre-Writing Checklist (Run BEFORE Writing Any Paper)

This checklist prevents all 6 fatal flaws from the Strong Reject cycle:

- [ ] **No self-authored peer reviews** will be included in any section of the paper
- [ ] **Affiliation is honest**: Independent/open-source research, not fictional institution
- [ ] **Accuracy metrics collected**: Run evaluation script before writing tables
- [ ] **sorry count committed**: Run `lake build 2>&1 | grep sorry` before writing abstract
- [ ] **FLOP model scoped**: If proving FLOP bounds, document O(L²·d) attention omission
- [ ] **Jargon audit**: Replace "thermodynamically catastrophic", "Weierstrass existence",
      "Banach fixed-point hot-swap" with precise operational language

---

## 1. The Core Scientific Mandate

### 1.1 Zero Hallucination on Numbers
All numeric values — benchmark timings, peak RAM, accuracy scores, parameter counts,
SHA256 hashes — MUST be derived by executing Python code and reading JSON output.
The LLM MUST NEVER estimate or calculate these values freehand.

**Required provenance chain:**
```
Python script → JSON receipt with timestamp → Paper table (with SHA256 citation)
```

### 1.2 Real Accuracy Metrics Required
Any paper comparing model variants MUST include a Table with:
- Task name, dataset ID, number of classes
- Baseline accuracy / F1 (pre-LoRA or zero-shot)  
- Post-adaptation accuracy / F1
- Random baseline (1/num_classes × 100%)
- Honest acknowledgment when scores are at or below random

**Forbidden:** Publishing a latency-only comparison without accuracy. This alone
is grounds for desk rejection at MLSys, ICLR, NeurIPS.

### 1.3 Lean 4 Honest Framing (CRITICAL)
Do NOT frame Lean 4 proofs as "novel theorems" or "fundamental mathematical results"
unless they genuinely are. The correct framing is:

> "These are machine-verified deployment invariants — configuration compliance
> gates verified by the type checker. Unlike Python asserts, they compose formally
> and run before any runtime or cloud resource is initialized."

Justify Lean 4 over Python/Pydantic: compile-time exhaustive checking, formal
composability across codebase, and CI/CD integration with `lake build`.

### 1.4 Grounded Academic Citations Only
Never cite papers from internal LLM memory. Retrieve authentic abstracts, authors,
and DOIs from arXiv API or verified academic sources. Write references to
`papers/references/` before embedding in LaTeX.

---

## 2. 6-Criterion Peer Review Protocol (Internal Gate)

Run this BEFORE finalizing the PDF. Failure in any criterion ⟹ revise before submit.

| # | Criterion | How to Check | Accept Threshold |
|---|---|---|---|
| **R1** | **Academic Integrity** | Search paper for "Reviewer", "Score:", "Accept", "Reject" in Section headings | Zero self-reviews |
| **R2** | **Formal Verification Honesty** | Check that every theorem is scoped and justified; no "computational physics" overclaiming | All invariants have explicit scope statements |
| **R3** | **FLOP Model Correctness** | Verify FLOP definitions include or exclude O(L²·d) explicitly | Docstring names omitted terms |
| **R4** | **Accuracy Completeness** | Table with accuracy + random baseline for every dataset evaluated | Present for all datasets |
| **R5** | **Telemetry Provenance** | Every numeric value traces to a JSON receipt with SHA256 | 100% traceability |
| **R6** | **Language Calibration** | No "thermodynamically catastrophic", no fictitious affiliations, abstract matches sorry count | Zero jargon violations |

**Model to use for internal review:** Gemini 2.5 Pro (Ultra subscription) with the
above 6 criteria as the evaluation rubric. Record result to `papers/peer_review_*.json`.

---

## 3. Standard Single-Run Pipeline

The pipeline MUST produce a publication-ready PDF in one uninterrupted run:

```bash
# Step 1: Collect real telemetry (accuracy + latency)
uv run python scripts/evaluate_5_datasets.py \
  --output artifacts/laya_lora/results_5_datasets_lora.json

# Step 2: Build Lean 4 invariants and count sorries
export PATH="/home/xavkal/.elan/bin:$PATH"
cd formal && lake build ANSE.LayaDecision 2>&1 | tee /tmp/lean_build.log
SORRY_COUNT=$(grep -c "uses \`sorry\`" /tmp/lean_build.log)
echo "Sorry count: $SORRY_COUNT"  # Must be ≤ 1
cd ..

# Step 3: Run anti-stub audit
uv run python -m antigravity_harness audit papers/

# Step 4: Compile XeLaTeX (2 passes for cross-references)
xelatex -interaction=nonstopmode -output-directory=papers papers/laya_*.tex
xelatex -interaction=nonstopmode -output-directory=papers papers/laya_*.tex

# Step 5: Compute SHA256 for provenance
sha256sum papers/laya_*.pdf

# Step 6: Internal 6-criterion peer review via Gemini Pro
uv run python scripts/review_paper_gemini_pro.py \
  --paper papers/laya_lean4_formal_paper_v2.tex \
  --criteria R1,R2,R3,R4,R5,R6 \
  --output papers/peer_review_internal.json

# Step 7: Record LTM memory
uv run python scripts/record_ltm_memory.py \
  --paper papers/laya_lean4_formal_paper_v2.pdf \
  --review papers/peer_review_internal.json \
  --outcome ACCEPT
```

---

## 4. LaTeX Publication Standards

- **Engine:** XeLaTeX (required for Lean 4 Unicode: ∀ ∃ ≤ ≥ ℕ ℝ)
- **Fonts:** `\setmainfont{DejaVu Serif}`, `\setmonofont{DejaVu Sans Mono}`
- **Document class:** `IEEEtran` (for systems/MLOps venues)
- **Two-pass compilation:** Required for cross-references (`\ref`, `\cite`)
- **Tables:** All latency tables MUST include `Avg Tokens` column

---

## 5. Limitations Section Template

Every paper MUST include a Limitations section. Minimum content:

```latex
\subsection{Limitations of the Evaluation}
\begin{itemize}
\item \textbf{N-shot only}: [N]-shot evaluation performed; full supervised
  fine-tuning was not conducted. [Dataset] accuracy at [X]\% reflects
  zero-shot generalization, not optimal task performance.
\item \textbf{Attention FLOP omission}: Invariant I1 covers FFN layers only.
  Full formal verification including O(L²·d) attention is future work.
\item \textbf{Open proof obligation}: \texttt{[theorem\_name]} is marked
  \texttt{sorry}; discharge requires [specific action].
\end{itemize}
```

---

## 6. The 4 Definitions Contract (for Physics/Theory Papers)

When generating ANSE physics papers (NOT MLOps/deployment papers):

- **Definition A:** Physical / Mathematical Formulation (PDEs, Hamiltonian)
- **Definition B:** Conservation Laws & Invariant Functional (exact algebraic invariant)
- **Definition C:** Algorithmic Discretization & Solver Scheme (RK4, Verlet, etc.)
- **Definition D:** Quantitative Acceptance Threshold & Gate (ε_tol, Π_penalty = 10⁶)

For MLOps/deployment papers, replace with:
- **Definition A:** Deployment Cost Heuristic (linear weighted functional)
- **Definition B:** Hardware Acceptance Gates (latency ≤ τ_max, RAM ≤ M_max)
- **Definition C:** Evaluation Protocol (N-shot, dataset splits, metric definitions)
- **Definition D:** Budget Compliance Constraint (LoRA params ≤ D_budget)
