---
license: apache-2.0
task_categories:
- formal-logic
- text-generation
tags:
- formal-verification
- lean4
- rust
- operating-systems
- neuro-symbolic
- kernel
- proof-engineering
size_categories:
- 1K<n<10K
pretty_name: RunuX Lean 4 Microkernel Formal Verification Telemetry
language:
- en
---

# RunuX Lean 4 Microkernel Formal Verification Dataset

## Dataset Summary
This dataset contains the mechanized formal specifications, theorem statements, proof obligations, and thermodynamic execution telemetry for the **RunuX Minimum Viable Kernel (MVK)**, developed under the **AutoevolveAI / ANSE** research framework.

The dataset accompanies the publication:
> **Autopoietic Neuro-Symbolic Verification of Operating System Kernels: A Thermodynamic Energy Paradigm in Lean 4 and Rust** (October 2026).

## Dataset Structure
The dataset is structured across three primary splits:
1. `data/formal_theorems.jsonl`: **448 theorem and lemma declarations** extracted from 37 Lean 4 formal specification modules (12,164 LOC). Each entry contains:
   - `file`: Path to the Lean 4 source file in `specs/lean4/MVK/`.
   - `theorem_name`: Canonical identifier.
   - `line`: Source line number.
   - `statement`: Pre-proof theorem signature.
   - `statement_hash`: Cryptographic SHA-256 fingerprint enforcing Oracle Invariance.
   - `status`: Verification status (`proven` vs `oracle_invariant_sorry`).
2. `data/verification_telemetry.jsonl`: Multi-tier execution records from the ANSE Master Orchestrator (`workflowrunux_all.py`). Records duration (s), physical action energy ($E$), and 23 cryptographic proof tokens.
3. `data/modules_metadata.jsonl`: Architectural mapping connecting Lean 4 specification modules to the 316 Rust kernel crates.

## Key Verified Baseline Metrics (Wave 16)
- **Lean 4 Proof Completion Rate**: 80.1% (359 / 448 proven with zero sorry).
- **Constant Stub Functions**: 0 (100% eradicated across all 316 crates).
- **Static Safety Comment Ratio**: 0.6098 (+271 comments added, 0 mutable statics).
- **Unit Test Coverage**: 609 tests across 175 crates.
- **Lake Prover Compilation**: 61 / 61 jobs passing clean.

## Usage
To load the theorems split using Python:
```python
import json

theorems = []
with open("data/formal_theorems.jsonl") as f:
    for line in f:
        theorems.append(json.loads(line))

print(f"Loaded {len(theorems)} formal theorem records.")
```

## Citation
```bibtex
@article{callens2026runux,
  author    = {Xavier Callens and the AutoevolveAI Consortium},
  title     = {Autopoietic Neuro-Symbolic Verification of Operating System Kernels: A Thermodynamic Energy Paradigm in Lean 4 and Rust},
  journal   = {Zenodo},
  year      = {2026},
  doi       = {10.5281/zenodo.10000000}
}
```
