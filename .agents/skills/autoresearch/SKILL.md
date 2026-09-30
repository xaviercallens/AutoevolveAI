---
name: autoresearch
description: >-
  Autonomous machine learning research paradigm (Karpathy-style).
  Formulates, implements, evaluates, and ratchet-commits ML architectural
  hypotheses. AR-H5 is the canonical example: Qwen2.5-8B Policy + Laya-LoRA
  NAR Value network in MCTS Tree-of-Thoughts. Use this skill when designing
  or running any autoresearch experiment in the ANSE codebase.
---

# Autoresearch Skill

## 1. Paradigm Overview

Autoresearch (inspired by Karpathy) is a self-directed ML experimentation loop:

```
Hypothesis → Implement → Ratchet Gate → Commit (if ΔFitness > 0)
```

Every experiment is:
1. **Numbered** — e.g., AR-H5 (Hypothesis 5)
2. **Falsifiable** — produces a measured fitness score
3. **Ratcheted** — code only commits if it beats the baseline
4. **Provenance-tracked** — JSON receipt with SHA-256

---

## 2. Running AR-H5 (Asymmetric Dual-Process MCTS)

### Quick benchmark (mock, no GPU needed)
```bash
uv run python run_ar_h5_benchmark.py --subset cruxeval --n_problems 10 --dry_run --mock
```

### Full CRUXEval-50 run (requires Qwen + Laya ONNX)
```bash
# Export Laya to ONNX first (if not done)
uv run python scripts/export_laya_onnx.py \
  --checkpoint /mnt/data/home/xavkal/laya_coding_checkpoints/stage3 \
  --output_dir /mnt/data/home/xavkal/laya_onnx

# Run the ratchet benchmark
uv run python run_ar_h5_benchmark.py \
  --subset cruxeval \
  --n_problems 50 \
  --qwen_model Qwen/Qwen2.5-Coder-7B-Instruct \
  --laya_onnx /mnt/data/home/xavkal/laya_onnx/onnx_int8/model_int8.onnx
```

### Ratchet results
```
results/ar_h5/ratchet_results.json   # SHA-256 provenance
results/ar_h5/traces/                # per-problem MCTS traces
```

---

## 3. MCTS Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Policy (Qwen2.5-8B 4-bit, ~5.5 GB VRAM)                   │
│  generate_branches(node, k=3) → list[str]                   │
└──────────────────┬──────────────────────────────────────────┘
                   │ K thought branches
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Value (Laya ONNX INT8, CPU, 0 GB VRAM, ~35ms/call)         │
│  gate_batch(thoughts) → (nouls, passed)                     │
│  score_batch(thoughts) → s_scores                           │
│  Kill if p_noul < τ_noul = 0.3                              │
└──────────────────┬──────────────────────────────────────────┘
                   │ Surviving branches + scores
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Sandbox (subprocess Python REPL / Lean 4)                  │
│  run_auto(code) → SandboxResult                             │
│  Error → score × 0.1 (backpropagation penalty)             │
└──────────────────┬──────────────────────────────────────────┘
                   │
              MCTS backprop → select next node via UCB1-Laya
```

UCB1-Laya formula:
```
UCB(n) = V_laya(n) + C * sqrt(ln(parent.visits) / n.visits)
```
where `C = 1.4` (exploration constant), `V_laya` is Laya's `s_score`.

---

## 4. Fitness Function & Ratchet Gate

```python
Fitness = Pass@1 - λ * VRAM_peak_GB - γ * TTS_s
# λ = 0.02   (penalty per GB VRAM)
# γ = 0.001  (penalty per second time-to-solution)
```

**Ratchet condition:** `Fitness(AR-H5) > Fitness(baseline_qwen_zero_shot)`

Only if this condition holds does `run_ar_h5_benchmark.py` execute `git commit`.
A failing ratchet is reported as REJECTED — never hidden.

---

## 5. VRAM Budget (16 GB consumer GPU)

| Component | VRAM | Notes |
|---|---|---|
| Qwen2.5-Coder-7B 4-bit AWQ | ~5.5 GB | `n_gpu_layers=-1` |
| Laya ONNX INT8 | **0 GB** | CPU only — key architectural insight |
| KV-Cache (Flash Attention) | ~9.5 GB | Enables wide search tree |
| **Total** | **~15.0 GB** | ✅ within 16 GB |

The NAR → CPU offload is the critical architectural innovation: **Laya uses 0 VRAM**,
freeing the entire 9.5 GB headroom for KV-cache and deeper reasoning trees.

---

## 6. Key Files

| File | Purpose |
|---|---|
| `anse/autoresearch/mcts.py` | MCTS engine: MCTSNode, MCTSTree, deep_think() |
| `anse/autoresearch/policy.py` | QwenPolicy + MockQwenPolicy |
| `anse/autoresearch/value.py` | LayaONNXValue + MockLayaValue |
| `anse/autoresearch/sandbox.py` | AR_H5_Sandbox (Python/Lean4) |
| `anse/autoresearch/ar_h5_orchestrator.py` | Top-level AR_H5_Orchestrator |
| `anse/autoresearch/ar_record.py` | ARRecord + ARRecordRegistry |
| `anse/autoresearch/ratchet.py` | RatchetGate + compute_fitness() |
| `run_ar_h5_benchmark.py` | Phase C ratchet benchmark runner |
| `results/ar_h5/ratchet_results.json` | SHA-256 ratchet results |

---

## 7. Adding a New Hypothesis

1. Create `anse/autoresearch/ar_h{N}_{short_name}.py` with the experiment logic
2. Add an `ARRecord(id="AR-H{N}", ...)` entry
3. Implement `train_and_eval()` that produces `BenchmarkResult`
4. Run `RatchetGate.evaluate(baseline, new)` — commit only if ACCEPTED
5. Append result to `results/autoresearch_log.jsonl`

---

## 8. Autoresearch Philosophy

> "An AI Scientist that can autonomously formulate, execute, validate, and commit
>  machine learning hypotheses — each one a falsifiable experiment with a ratchet gate
>  that prevents regression." — inspired by Karpathy's autoresearch vision

Key invariants (enforced by RatchetGate):
- **No regression**: code only commits if ΔFitness > 0
- **No hallucinated results**: all metrics from JSON receipts with SHA-256
- **No silent failures**: a failing gate is logged as REJECTED, never suppressed
- **No stub code**: all implementations pass `verify_ast_and_imports` anti-stub check
