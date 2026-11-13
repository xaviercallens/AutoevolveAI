# Peer Review — Reviewer 2

**Manuscript:** *Laya-LoRA Coding Companion: Curriculum Training on 10 Structured Coding Datasets, GCP-Backed Data Lake Infrastructure, and System 1 Decision Benchmarking Against Autoregressive Baselines*

**Submission Track:** Systems for ML / MLOps (IEEEtran conference)

**Review Date:** 2026-09-30

---

## Overall Recommendation

**Weak Reject**

The manuscript presents a well-structured system paper with an intellectually coherent framing (NAR encoder as System 1 gatekeeper) and commendable transparency around its prototype limitations. However, in its current form it does not constitute a complete empirical contribution: every quantitative result (training, benchmark, latency) is derived from an under-resourced CPU prototype with 120 samples/stage and a single epoch — a sample budget 650× smaller than the claimed corpus. The 33.3% gate accuracy is reported alongside a valid random baseline of 50%, confirming that the deployed checkpoint performs *worse than chance*. Until full-scale Vertex AI training results are available, the manuscript is a well-documented system design proposal rather than an evaluated scientific contribution. Acceptance is contingent on completion of the primary experiment the paper is built around.

---

## Summary

The authors introduce Laya-LoRA Coding Companion, a ModernBERT-base encoder adapted via LoRA (r=8, α=16) and trained through a three-stage curriculum on 10 curated coding datasets (78,503 records total). The model is positioned as a non-autoregressive System 1 pre-filter within the ANSE framework, performing binary gating, 40-class routing, and energy-score regression from a single forward pass. A GCP Socrate AI data lake and Vertex AI training pipeline are specified. Lean 4 compile-time invariants enforce LoRA budget and energy ordering. Empirical results, obtained on 120-sample/stage CPU prototype runs, show 33.3% 12-case benchmark accuracy, 91.7% noul accuracy on a 12-sample validation set, and a P50 latency of 3,911.6 ms.

---

## Strengths

- **Exceptional provenance hygiene.** The paper anchors every numeric claim to SHA-256-verified JSON receipts (`training_summary.json`, `coding_benchmark_and_comparison.json`, `download_receipt.json`). This is a genuine methodological contribution: machine-verified telemetry traceability is rarely achieved in systems-ML papers, and it sets a reproducible standard. The SHA-256 digests embedded in the LaTeX source (lines 7–9) allow independent audit.

- **Honest and clearly-framed prototype disclosure.** Section 5 (Discussion and Limitations) explicitly enumerates the five major limitations, including the prototype scale caveat, the latency warm-up conflation, the Lean 4 `sorry` obligation, the attention FLOP omission, and the cross-environment baseline comparison issue. This level of intellectual honesty about what is and is not demonstrated is commendable and should be preserved verbatim in revision.

- **Architecturally sound System 1 / System 2 decomposition.** The decision to use a NAR encoder for gating and routing rather than invoking an AR model for every classification is well-motivated and grounded in the broader literature (Kahneman, Bengio 2019). The energy function formulation E(x) = 10^6 upon blocking is concrete and integrates cleanly with the ANSE thermodynamic criterion. The 100% precision on the blocking sub-task (4/4 BLOCKED cases correct) is a meaningful early-stage validation of the architectural hypothesis.

- **Reproducible GCP infrastructure specification.** The `gcloud run deploy` snippet (Section 6.1) is complete and immediately executable: region, CPU, memory, concurrency, min-instances, and checkpoint GCS path are all specified. The Vertex AI training job spec (machine type `a2-highgpu-1g`, container registry path, cost estimate at $7.84/run) is actionable. This level of operational specificity is above the norm for MLOps papers.

---

## Weaknesses

### W1 — LoRA Parameter Count Requires Clarification and Arithmetic Verification

Equation (2) computes the LoRA-only parameters as:

    |Θ_LoRA| = 2 × 22 × (768 × 8 + 8 × 768) = 539,136

Several issues arise:

1. **Layer count unverified.** The paper asserts 22 attention layers for ModernBERT-base. ModernBERT-base (answerdotai/ModernBERT-base, arXiv:2412.13663) has 22 encoder layers, which is consistent with a 149M parameter count. However, the paper does not specify whether LoRA is applied to *both* Q and V projections of *all 22 layers*, or to a subset. The factor of 2 in the equation is ambiguous — it could denote {Q, V} or it could denote A and B matrices. In the standard LoRA formula, each adapted weight W ∈ ℝ^{d×k} contributes dr + rk parameters. For Q and V with d=k=768, r=8: 2 × 768 × 8 = 12,288 params per matrix, 2 matrices per layer, 22 layers: 2 × 22 × 12,288 = 540,672, not 539,136. The discrepancy of 1,536 parameters is unresolved and hints at an off-by-one on layer count or projection dimension. The gap to the reported total (577,584 − 539,136 = 38,448) ascribed to "head parameters" is irreconcilable with an independent head count: NoulHead is Linear(768,1) = 769 params; ChoiceHead is Linear(768,256)+ReLU+Linear(256,40) ≈ 207,400; ScoreHead is Linear(768,128)+ReLU+Linear(128,1) ≈ 98,433 — a combined ~306k, which substantially exceeds the stated 38,448 gap. The authors must provide an explicit, itemized parameter count.

2. **Scaling factor α/r = 2 is not discussed.** In deployment, the effective weight perturbation is (α/r)AB = 2AB. This scalar scaling has implications for learning dynamics (effectively doubling the rank-constrained update magnitude) that are not addressed.

### W2 — Training Statistics Are Uninterpretable at Prototype Scale

The `training_summary.json` reveals that each stage used **108 training records and 12 validation records** — not a stratified subsample of 78,503 records, but a 120-example total. The abstract and introduction repeatedly reference the 78,503-record corpus, implying it was used for training, when in fact it was only staged to GCS. Key statistical consequences:

- The 91.7% noul accuracy on Stage 1 corresponds to **11/12 validation samples**. This is not a statistically meaningful accuracy estimate; the 95% Wilson CI is approximately [61.5%, 99.8%]. A single misclassified validation example shifts the metric by 8.3 percentage points.
- The Stage 3 val loss of 8.947 vs. Stage 1 val loss of 2.172 is a 4× degradation, which the paper attributes to "added complexity of 40-class routing" without quantitative analysis. This explanation is plausible but untested; catastrophic forgetting across stages is equally plausible at this sample size.
- The abstract's claim of "91.7% binary gate accuracy" is presented before the prototype-scale disclosure and could mislead readers who do not carefully read Section 5.

### W3 — Baseline Comparison Matrix Is Methodologically Incommensurable

Table III (comparative model matrix) conflates empirically measured Laya values with literature-sourced AR baseline values from unspecified environments, hardware configurations, and tokenisation regimes:

- Qwen2.5-0.5B P50 latency of 385 ms and energy of 4.80 Wh/1k queries: **no citation and no environment specification** is provided. CPU vs. GPU inference, token count per query, quantisation level, and batch size are all latency-determining variables that differ between the Laya measurement (24 tokens, CPU, 4 threads, PyTorch eager) and any published Qwen benchmark.
- The paper correctly flags this in Section 5 ("cross-environment comparison should be interpreted directionally"), but Table III presents both Laya's 3,912 ms and Qwen2.5-0.5B's 385 ms in the same column without visual or typographic differentiation between measured and estimated values. This is potentially misleading: Laya's first-call latency of 3.9 s vs. Qwen's warm-path 385 ms is not a fair operational comparison.
- The energy values for frontier APIs (120 Wh/1k queries) cite no source. Per-query energy for GPT-4o is not publicly disclosed by OpenAI; this figure appears to be an estimate or heuristic.

### W4 — Dataset Selection Has Coverage Gaps and Provenance Concerns for Two Entries

1. **Severe class imbalance across stages.** Stage 2 (1,263 records) is 37× smaller than Stage 1 (46,196) and 25× smaller than Stage 3 (31,044). In a sequential curriculum, the model almost certainly forgets Stage 2 signal before Stage 3 completes — consistent with the Stage 3 val loss of 8.947 observed in the data. No data balancing strategy (oversampling, replay buffer, weighted curriculum) is described.

2. **Magpie-Qwen2.5-20k provenance.** This 20,000-record "instruction-following pairs generated by Qwen2.5-Coder" is a **synthetic dataset** whose quality depends on the generating model. No quality filter, deduplication, or held-out validation against human-labeled data is described. Including synthetic AR-generated data for training a classifier that is then evaluated against AR baseline quality is potentially circular.

3. **CodeRM-UnitTest and SWE-Perf citations are incomplete.** Both are cited as "HuggingFace Dataset Hub, 2024" with no DOI, arXiv ID, or conference affiliation. The Zenodo RAPL Energy dataset is similarly under-cited. Reviewers cannot assess peer-review status or data quality from these entries alone.

4. **No held-out test split is described.** All reported accuracy figures come from a validation split of 12 examples. A separate test set drawn from the held-out portion of the 78,503-record corpus is required for any publication-quality accuracy claim.

---

## Specific Actionable Suggestions

1. **[Required] Complete the primary experiment.** Run the full 10-epoch Vertex AI A100 training job on the staged 78,503-record corpus. Report noul accuracy, routing F1, and MSE score regression on a held-out test split (≥5,000 examples) before resubmission. Without this, the paper cannot be accepted at a systems ML venue.

2. **[Required] Fix and itemize the LoRA parameter count.** Provide a table: backbone architecture (layer count, hidden dim, projection dims), LoRA target modules, parameter count per module, head parameter counts (NoulHead, ChoiceHead, ScoreHead), and verified total. The arithmetic in Eq. (2) has a discrepancy of ~1,536 that must be resolved, and the stated head-parameter gap (38,448) is arithmetically inconsistent with the described head architectures.

3. **[Required] Separate measured vs. estimated values in Table III.** Add a footnote key: ✓ = empirically measured in this work, ~ = adapted from published benchmark [cite]. Apply it to every cell. Provide exact source citations for each AR baseline row (Qwen benchmarks, energy estimates).

4. **[Required] Expand the validation set before reporting accuracy.** 12 validation examples is not a sample from which any accuracy claim is statistically valid. Use stratified sampling to draw at least 500 examples per stage from the available corpus for validation, and rerun training.

5. **[Recommended] Add a calibration experiment for the noul threshold τ_noul = 0.3.** The paper acknowledges that the conservative threshold causes the 33.3% benchmark result (all PASS cases are wrongly blocked). Include a threshold-vs-F1 curve or a simple Platt scaling step to show the threshold is principled rather than arbitrary.

6. **[Recommended] Address Stage 2 data imbalance.** Either document why 1,263 Stage 2 records are sufficient relative to Stage 1/3, implement a replay buffer, or acknowledge explicitly in limitations that the energy-scoring head may be systematically underfitted relative to the gating and routing heads.

7. **[Recommended] Discharge the Lean 4 `sorry` obligation or downgrade the claim.** Invariant I3 (energy cost ordering) carries an explicit `sorry`. The paper still presents it as a "verified" deployment invariant — this is technically incorrect in Lean 4. A `sorry` is an admitted proof hole, not a verified theorem. Change the invariant label to [Unverified — sorry obligation pending] until discharged.

8. **[Minor] Clarify warm-path latency in the abstract.** The abstract leads with "P50 latency of 3,911.6 ms" — a first-call measurement including JIT warm-up. The operationally relevant figure for a persistent Cloud Run container is the warm-path 35–58 ms, which is only mentioned parenthetically in Section 4.2. The abstract should lead with the warm-path figure and note the first-call overhead separately.

---

## Summary of Scores by Review Criterion

| Criterion | Score (1–5) | Comment |
|---|---|---|
| LoRA parameter correctness | 3/5 | Arithmetic discrepancy of ~1,536 params; head count gap unexplained |
| Curriculum design motivation | 3/5 | Stage weights plausible but not ablated; Stage 2 size disparity unaddressed |
| Comparative matrix fairness | 2/5 | Mixed measured/estimated data without labeling; no common-environment control |
| Honest accuracy presentation | 4/5 | 33.3% honestly disclosed with clear prototype caveats in Section 5 |
| GCP infrastructure reproducibility | 4/5 | Executable gcloud snippet; cost estimate; full Vertex AI spec present |
| Dataset appropriateness | 3/5 | Good coverage but Stage 2 imbalance, synthetic data concerns, incomplete citations |

**Overall Recommendation: Weak Reject**
Conditionally revise and resubmit with full-scale training results, resolved parameter arithmetic, separated baseline provenance, and a statistically adequate evaluation split.

---

## Confidence

**3 — High**

I have read the full LaTeX source, both JSON data files, and verified the arithmetic claims independently. I am familiar with LoRA adaptation, ModernBERT architecture, curriculum training protocols, GCP Vertex AI / Cloud Run infrastructure, and NAR encoder evaluation methodology.

---

*Reviewer 2 | Senior ML Engineer & Applied AI Researcher*  
*Specialisation: LoRA adaptation, BERT-family encoders, coding AI benchmarks, GCP cloud infrastructure*
