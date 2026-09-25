---
name: scientific-paper-redactor
description: Decoupled academic paper authoring and LaTeX typesetting agent enforcing Inversion of Control (IoC), zero-hallucination telemetry ingestion, and Unicode/XeLaTeX compilation without code mutation.
---

# Scientific Paper Redactor Skill: Decoupled IoC Academic Typesetting

This skill enforces the strict separation of concerns between code generation (System 1), physical execution telemetry (System 1.5), and academic manuscript typesetting (System 2).

## 1. Architectural Inversion of Control (IoC)

To permanently eradicate **Sycophant Roleplay** and **Context / Mode Bleeding**:
1. **The Redaction Agent NEVER Writes or Mutates Source Code:**
   Code generation is delegated exclusively to the Code Synthesizer (`System 1`). The Redactor only receives paths to verified source files on disk (`.rs`, `.py`, `.lean`).
2. **Zero-Trust Telemetry Ingestion:**
   The Redaction Agent is strictly forbidden from estimating or calculating execution latencies, memory footprints, or invariant errors. All telemetry must be read directly from deterministic benchmark reports (e.g. `results/*_eval_report.json`) minted by `time.perf_counter()` and `resource.getrusage()`.
3. **Code Inclusion via Verbatim Isolation:**
   Code is included in manuscripts either via `\lstinputlisting{...}` or automated verbatim embedding scripts. LaTeX math escapes (`$`, `\mathbb`, `\le`) must never be applied inside code bodies.
4. **Native Unicode Typesetting (XeLaTeX / LuaLaTeX):**
   All documents containing formal mathematical proofs (Lean 4) must compile via `xelatex` using `fontspec`, `DejaVu Serif`, and `DejaVu Sans Mono`, supplemented with `newunicodechar` fallbacks to completely eliminate UTF-8 Mojibake (`âDİ`, `âLÃ`).

## 2. Decoupled Multi-Agent Pipeline

```mermaid
graph LR
    A[Domain Specs / 4 Definitions] --> B[System 1: Code Synthesizer]
    B --> C[Hard-Gate: Compiler & Sandbox]
    C -->|Failure: Stderr Feedback| B
    C -->|Exit Code 0| D[System 1.5: Telemetry Engine]
    D -->|Signed JSON Receipts| E[System 2: Paper Redactor]
    D -->|Raw Code Files| E
    E --> F[XeLaTeX Compiler]
    F --> G[Certified Publication PDF]
```

## 3. Standard Verification Commands

```bash
# 1. Verify and compile code kernels
python3 anse/core/anse_v10_orchestrator.py

# 2. Build compendium using XeLaTeX
python3 scripts/build_200_compendium.py

# 3. Check for Unicode character omissions
grep "Missing character:" papers/200_compendium/main.log
```
