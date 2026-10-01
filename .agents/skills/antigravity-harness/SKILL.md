---
name: antigravity-harness
description: >-
  Autonomous Neuro-Symbolic Execution & Hardening Harness for Antigravity CLI.
  Enforces anti-stub AST validation, Lean 4 formal proof verification,
  Gemini large-window context orchestration, computational physics profiling,
  DPO RL pipeline, and 6-criterion publication peer review integration.
  Includes MCP server integration for memory graph recording and vector DB
  retrofit of validated outputs.
---

# Antigravity Harness: Autonomous Neuro-Symbolic Execution & Hardening (v2)

The **Antigravity Harness** (`python -m antigravity_harness`) provides zero-trust
verification and execution for autonomous ANSE agents. Version 2 adds LTM memory
graph recording and vector DB retrofitting of positive outcomes.

---

## 1. Quick CLI Commands

| Command | Action | Key Invariant |
|---|---|---|
| `uv run python -m antigravity_harness audit <path>` | Anti-stub AST audit | Fails with E=10⁶ on `pass`, `...`, `mock_*`, `time.sleep` |
| `uv run python -m antigravity_harness verify --formal-dir formal` | Lean 4 proof audit | Fails on ungrounded `sorry`; expects ≤1 acknowledged sorry |
| `uv run python -m antigravity_harness test [path]` | Test runner with telemetry | Duration, pass/fail, traces |
| `uv run python -m antigravity_harness qa <file.py>` | Adversarial test synthesis | Null handling, numeric boundary, stress |
| `uv run python -m antigravity_harness dpo --output results/dpo.jsonl` | DPO preference pairs | Chosen=low E/zero-stub vs Rejected=stubs/high E |
| `uv run python -m antigravity_harness review --paper <tex> --criteria R1-R6` | 6-criterion paper review | Returns ACCEPT/REJECT per criterion |
| `uv run python -m antigravity_harness ltm record --outcome <ACCEPT\|REJECT>` | Record LLM call to memory | Writes to memory graph + vector DB |

---

## 2. Core Architecture

```
antigravity-harness/
├── core/
│   ├── context_orchestrator.py     # Gemini 1M-2M context manager
│   ├── anti_stub_guard.py          # AST: blocks pass, ..., fake_*, constant returns
│   ├── lean4_verifier.py           # Lake / Lean 4 formal proof interface
│   └── peer_review_gate.py         # 6-criterion publication review (NEW)
├── storage/
│   ├── redis_bus.py                # Redis Streams, JSON trace documents
│   ├── ltm_memory_graph.py         # MCP memory-graph: entities/relations/observations (NEW)
│   └── vector_db_retrofit.py       # ChromaDB: retrofit accepted outputs (NEW)
├── agents/
│   ├── qa_agent.py                 # Adversarial test generator
│   └── optimizer_agent.py          # Physics profiling: E = w_t·ms + w_m·RAM
├── tests_runner/
│   ├── unit_integration.py         # Pytest + JUnit XML
│   └── visual_regression.py        # Playwright + Pixelmatch
└── rl_pipeline/
    ├── trace_extractor.py           # Session trajectories from Redis
    └── dpo_dataset_builder.py       # TRL/DPOTrainer preference pairs
```

---

## 3. MCP Server Integration for LTM and Vector DB

### Protocol E: Record LLM Calls to Memory Graph
After each significant LLM generation (paper draft, proof attempt, evaluation),
record the outcome to the memory graph MCP server:

```python
# Using MCP memory-graph tools directly:
# Good call (paper accepted, proof compiled, accuracy measured):
mcp.memory_graph.create_entities([{
    "name": "LLM_call_ANSE_paper_v2",
    "entityType": "LLMCall",
    "observations": [
        "outcome: ACCEPT (MLSys/MLOps Track)",
        "paper: laya_lean4_formal_paper_v2.tex",
        "sha256: 13598542c4ab2c9044c9299b5331979ede51c5639e44396ccc36b5920b43e8fe",
        "sorry_count: 1 (acknowledged)",
        "accuracy_table: present",
        "flop_model: correctly scoped to FFN",
        "peer_review_criteria_passed: R1,R2,R3,R4,R5,R6"
    ]
}])

# Bad call (rejected due to flaw):
mcp.memory_graph.create_entities([{
    "name": "LLM_call_ANSE_paper_v1",
    "entityType": "LLMCall",
    "observations": [
        "outcome: STRONG_REJECT",
        "paper: laya_lean4_formal_paper.tex",
        "sha256: aae3f6e8f7e3d328e1bd4c5a3be50d48c36d7ca2c2fbe31e8de22edc35573664",
        "flaw_A: self-authored peer review section",
        "flaw_B: trivial arithmetic framed as novel theorems",
        "flaw_C: L3 contradicts latency table (missing seq-len explanation)",
        "flaw_D: FLOP model missing O(L^2*d) attention term",
        "flaw_E: no accuracy metrics in any table",
        "flaw_F: fictitious affiliation, sorry count mismatch in abstract"
    ]
}])
```

### Protocol F: Retrofit Vector DB with Accepted Outputs
After a paper, proof, or evaluation receives ACCEPT:

```bash
# Retrofit the validated paper into ChromaDB
uv run python -m antigravity_harness ltm retrofit \
  --doc papers/laya_lean4_formal_paper_v2.tex \
  --label "ACCEPTED_MLOPS_PAPER" \
  --tags "lean4,deployment_invariants,lora,cpu_inference,modernbert" \
  --metadata '{"review": "ACCEPT", "venue": "MLSys/MLOps", "sorry_count": 1}'

# Retrofit the accepted Lean 4 source
uv run python -m antigravity_harness ltm retrofit \
  --doc formal/ANSE/LayaDecision.lean \
  --label "ACCEPTED_LEAN4_INVARIANTS" \
  --tags "lean4,ffnFLOPs,loraParams,deploymentEnergy,I1-I5"

# Mark the rejected paper as NEGATIVE example
uv run python -m antigravity_harness ltm retrofit \
  --doc papers/laya_lean4_formal_paper.tex \
  --label "REJECTED_PAPER_NEGATIVE_EXAMPLE" \
  --tags "lean4,self_review,overclaiming,missing_accuracy" \
  --negative true
```

---

## 4. Operational Protocols

### Protocol A: Pre-Commit Implementation Audit
```bash
uv run python -m antigravity_harness audit <modified_file.py>
```
Fails on: `pass`, `...`, `mock_*`, `time.sleep`, constant return values.

### Protocol B: Mathematical Verification (Lean 4)
```bash
export PATH="/home/xavkal/.elan/bin:$PATH"
cd formal && lake build 2>&1 | tee /tmp/lean_build.log
# Enforce ≤1 sorry:
SORRY_COUNT=$(grep -c "uses \`sorry\`" /tmp/lean_build.log)
[ "$SORRY_COUNT" -le 1 ] || (echo "TOO MANY SORRIES: $SORRY_COUNT" && exit 1)
```

### Protocol C: Physics of Computation Optimization
```python
from antigravity_harness.agents import OptimizerAgent
opt = OptimizerAgent()
proposal = opt.compare_and_evaluate(baseline_fn, candidate_fn, candidate_source, inputs)
assert proposal.is_thermodynamically_favorable, "ΔE ≥ 0: rejected"
```

### Protocol D: DPO Alignment Pipeline
```bash
uv run python -m antigravity_harness dpo --output results/dpo_dataset.jsonl
```

### Protocol G: 6-Criterion Paper Peer Review Gate (NEW)
```bash
# Run BEFORE finalizing any paper PDF
uv run python -m antigravity_harness review \
  --paper papers/laya_lean4_formal_paper_v2.tex \
  --lean-log /tmp/lean_build.log \
  --results artifacts/laya_lora/results_5_datasets_lora.json \
  --criteria R1,R2,R3,R4,R5,R6 \
  --model gemini-2.5-pro \
  --output papers/peer_review_internal.json
# Exit 0 only if all 6 criteria pass
```

---

## 5. 6 Criteria Review Gate (Protocol G Detail)

| Criterion | Test | Automatic Check |
|---|---|---|
| **R1 Academic Integrity** | No self-authored review sections | `grep -i "peer review tribunal\|reviewer [0-9]\|strong accept"` fails in paper |
| **R2 Framing Honesty** | No "novel theorem" overclaiming | `grep -i "computational physics theorem\|thermodynamically catastrophic"` |
| **R3 FLOP Correctness** | L²·d attention term documented | Lean source contains "O(L² × d)" or "attention term" in docstring |
| **R4 Accuracy Present** | Accuracy table in paper | LaTeX contains `accuracy` column in tabular environment |
| **R5 Telemetry SHA256** | All numeric values traced | Every table caption references SHA256 from JSON receipt |
| **R6 Language Clean** | No fictitious affiliations | Affiliation field does not contain "Antigravity Advanced Agentic Computing" |

---

## 6. Model Selection Guide

| Task | Model | Reason |
|---|---|---|
| Initial paper draft | Gemini 2.0 Flash | Fast iteration |
| Mathematical proof design | Gemini 2.5 Pro (Ultra) | Deep reasoning |
| Internal 6-criterion peer review | Gemini 2.5 Pro (Ultra) | Critical evaluation |
| Lean 4 tactic search | Gemini 2.5 Pro with tool use | Mathlib4 knowledge |
| DPO dataset building | Gemini 2.0 Flash | High throughput |
| Literature review | Gemini 2.5 Pro + arXiv search | Accurate citation |
| Vector DB embedding | text-embedding-004 | 768-dim, stable |
