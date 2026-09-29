# ⚖️ Kev Decision Engine: Open-Source Jev Architecture Integration for SAAW

## 1. Executive Summary

This document introduces **Kev** ([`vendor/kev`](file:///home/xavkal/xdev/AutoevolveAI/vendor/kev), cloned from [github.com/jaredpalmer/kev](https://github.com/jaredpalmer/kev)), an open-source reconstruction of TypeSafe's **Jev / System One** architecture, and details its integration into **SAAW (SocrateAI Autonomous Agent Workflow)** for automated post-retraining decision-making.

In AutoevolveAI / ANSE, nightly continuous learning cycles retrain multiple neural and symbolic modules (Laya System 1 LoRA, Qwen LTM LoRA, RL EnergyCriticPolicy, EB-JEPA physics world models, and Autopoiesis V2). Rather than relying on uncalibrated heuristic thresholds or manual inspection, **Kev** provides calibrated, probabilistic decision queries (`noul`, `choice`, `score`) with question isolation to determine whether newly retrained models should be promoted to production, quarantined, or deployed to the SocrateAI GCP Data Lake.

---

## 2. Kev Architecture & Decision Primitives

Kev reconstructs the architecture detailed in *Jev's Architecture Unmasked* (Archer Hume) and provides a drop-in replacement for the TypeSafe System One API (`POST /v1/systemone`).

### Key Architectural Pillars
1. **Block-Causal Question Isolation:**
   - Multiple decision questions share a single state text (e.g. multi-page retraining telemetry) but are evaluated in parallel branch masks where questions cannot attend to each other, preventing question contamination.
2. **Pointer Decision Readout:**
   - Delimiter tokens (`<|fim_prefix|>`, `<|fim_middle|>`, `<|box_start|>`, `<|box_end|>`, `<|fim_suffix|>`) enclose the state and candidate options. A terminal `<decide>` token aggregates attention logits over option spans.
3. **Calibrated Probabilistic Output:**
   - Decisions output true probabilities and calibrated confidence bounds fitted against held-out validation distributions.

### Decision Primitives
- **`noul` (Binary Verification):**
  Binary decision answering with a calibrated probability $p \in [0, 1]$ representing $P(\text{true})$.
- **`choice` (Categorical Action Selection):**
  Selects among discrete choices, returning normalized probabilities across all options, argmax label, and normalized confidence:
  $$\text{Confidence}_{\text{choice}} = \frac{\max(P) - 1/K}{1 - 1/K}$$
- **`score` (Continuous Quality Grading):**
  Continuous rating over an ordered scale of criteria, computing expected value $\sum_{i} i \cdot P_i$, legend mappings, and distribution concentration confidence.

---

## 3. SAAW (SocrateAI Autonomous Agent Workflow) Integration

### Core Module: `anse/decision/kev_engine.py`

The integration exposes [`KevDecisionEngine`](file:///home/xavkal/xdev/AutoevolveAI/anse/decision/kev_engine.py) and [`SAAWRetrainDecision`](file:///home/xavkal/xdev/AutoevolveAI/anse/decision/kev_engine.py), providing dual backend execution:
1. **Grounded Calibrated Local Inference Engine:**
   High-performance analytical engine applying fitted temperature scaling over physical conservation invariants, loss reduction percentages, and hippocampal retention fidelities. Operates instantaneously with zero GPU requirements on CPU machines.
2. **Kev Model Server Bridge:**
   Connects via HTTP to a running Kev daemon (`kev.serve` on `http://127.0.0.1:8009`) or TypeSafe endpoint when deployed on GPU clusters.

### The 4 Pivotal SAAW Retraining Questions

Whenever the nightly retraining loop executes, Kev inspects the unified telemetry and answers:

```json
{
  "state": {
    "pipeline_status": "SUCCESS",
    "total_elapsed_sec": 1375.2,
    "dream_phase": { "retention_score": 0.9849, "laya_lora_loss": 1.1145, "latent_mcts_advantage": 2.5868 },
    "qwen_lora": { "loss_reduction_pct": 13.42, "final_loss": 3.3237 },
    "rl_critic": { "margin_gain": 6.842, "loss_reduction_pct": 41.01 },
    "physics_world_model": { "passed_invariants": 10, "total_cases": 10, "loss_reduction": 17.18 }
  },
  "questions": {
    "promote_checkpoint": {
      "type": "noul",
      "instructions": "Should this newly retrained checkpoint set be promoted to active production / default inference?"
    },
    "deployment_strategy": {
      "type": "choice",
      "instructions": "What deployment action should SAAW execute for this retrained state?",
      "criteria": {
        "deploy_full_stack": "Deploy models, vector DBs, Redis snapshot, and cartography to GCP Data Lake",
        "local_staging_only": "Retain weights in local staging directory without overwriting cloud production",
        "rollback_to_parent": "Roll back to parent checkpoint due to invariant degradation or high energy",
        "quarantine_for_investigation": "Quarantine checkpoints into quarantine/ for numerical or safety audit"
      }
    },
    "retraining_quality_score": {
      "type": "score",
      "instructions": "Rate the overall scientific and computational quality of this retraining cycle",
      "criteria": [
        "Critical degradation, invariant violation, or runtime failure",
        "Marginal convergence with weak generalization or borderline retention",
        "Solid improvement satisfying all convergence gates and conservation laws",
        "Exceptional convergence across all multidisciplinary models with high advantage"
      ]
    },
    "next_cycle_adaptation": {
      "type": "choice",
      "instructions": "Which adaptation strategy should be scheduled for the next nightly retraining cycle?",
      "criteria": {
        "standard_schedule": "Proceed with regular balanced overnight schedule",
        "deepen_mcts_exploration": "Increase MCTS dream search thought rollouts and exploration factor",
        "prioritize_physics_invariants": "Expand physics invariant verification cases and symplectic tolerance",
        "scale_lora_learning_rate": "Adjust learning rate and LoRA rank for Qwen/Laya adapters"
      }
    }
  }
}
```

---

## 4. Pipeline Enforcement & Safety Gating

In [`scripts/nightly_retrain_at_5am.py`](file:///home/xavkal/xdev/AutoevolveAI/scripts/nightly_retrain_at_5am.py), Kev acts as the mandatory decision gate prior to Step 8 (GCP Data Lake Deployment):

```text
[Step 1-6: Model Training & Validation]
                  │
                  ▼
[Step 7: Kev SAAW Post-Retrain Decision Gate]
                  │
        ┌─────────┴─────────┐
   Status = APPROVED   Status != APPROVED
        │                   │
        ▼                   ▼
[Step 8: GCP Deploy]   [Abort Cloud Deploy]
(Sync models, DBs,     (Retain parent weights,
cartography to GCS)     log quarantine alert)
```

If Kev detects invariant failure, loss divergence, or catastrophic forgetting, cloud deployment is **automatically halted**, preventing corrupt weights from polluting `gs://socrateai-datalake-gen-lang-client-0625573011/` or `gs://symbrain-v2-models/`.

---

## 5. CLI Usage & Verification

### Running the Decision Gate
```bash
# Evaluate the latest nightly retraining report
uv run python scripts/kev_decision_gate.py

# Enforce strict gate in automated CI/CD or crontab
uv run python scripts/kev_decision_gate.py --gate
```

### Verified Sample Output
```text
2026-09-29 05:48:22,130 [INFO] ⚖️  KEV SAAW POST-RETRAIN CALIBRATED DECISION GATE
2026-09-29 05:48:22,166 [INFO] Saved Kev SAAW Retrain Decision to results/nightly_training/kev_retrain_decision.json
2026-09-29 05:48:22,167 [INFO] Status                      : APPROVED
2026-09-29 05:48:22,168 [INFO] Promote Checkpoint (Noul)   : True (P = 0.9980)
2026-09-29 05:48:22,168 [INFO] Deployment Strategy (Choice): deploy_full_stack (Conf = 0.9952)
2026-09-29 05:48:22,168 [INFO] Quality Score (Score)       : 2.95 / 3.00 (Conf = 0.9502)
2026-09-29 05:48:22,169 [INFO] Next Cycle Adaptation       : standard_schedule (Conf = 0.4317)
2026-09-29 05:48:22,169 [INFO] Summary Reasoning           : Kev Decision APPROVED (Confidence 1.00, Promote Probability 0.9980): All multidisciplinary models converged with quality score 2.95/3.0. Deploying full stack to SocrateAI GCP Data Lake.
2026-09-29 05:48:22,170 [INFO] ✅ Gate passed: Retraining run approved for deployment.
```

---

## 6. Test Suite & Verification

The integration is fully covered by [`tests/test_kev_decision_engine.py`](file:///home/xavkal/xdev/AutoevolveAI/tests/test_kev_decision_engine.py):
- `test_kev_vendor_import`: Asserts direct import of `kev.api` from `vendor/kev`.
- `test_kev_systemone_schemas`: Validates Pydantic serialization of `Noul`, `Choice`, and `Score`.
- `test_kev_decision_evaluation_approved`: Verifies positive approval, high probability ($P \ge 0.95$), and quality score $\ge 2.5$.
- `test_kev_decision_evaluation_rejected_on_failure`: Verifies rejection ($P < 0.15$), rollback routing, and deployment halting when failures occur.
- `test_kev_decision_gate_cli`: Validates process exit codes and CLI arguments.
