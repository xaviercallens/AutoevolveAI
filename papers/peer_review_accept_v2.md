---
# Peer Review Record: ACCEPT (Systems for ML / MLOps Track)
# Recorded verbatim: 2026-09-30T16:18:46+02:00
# Version reviewed: laya_lean4_formal_paper_v2.tex
# SHA256 of reviewed PDF: 13598542c4ab2c9044c9299b5331979ede51c5639e44396ccc36b5920b43e8fe
---

# Peer Review Report

**Manuscript Title:** Lean 4 Machine-Verified Deployment Invariants for Non-Autoregressive CPU Inference: LoRA Budget Constraints, FFN FLOP Monotonicity, and Energy Ordering

**Recommendation:** Accept (Systems for ML / MLOps Track)

## 1. Summary of the Manuscript

The revised manuscript proposes a framework utilizing the Lean 4 theorem prover as a strongly-typed CI/CD configuration checker for deploying non-autoregressive (NAR) language models (specifically ModernBERT-base with LoRA adaptation) on commodity CPU infrastructure. The goal is to mitigate GPU dependency and reduce computing costs for structural AI decision tasks. The author formalizes five deployment invariants to guarantee FFN FLOP monotonicity, parameter budget compliance, and operational cost ordering. The paper includes an empirical evaluation of latency and 10-shot accuracy across five datasets, demonstrating the economic advantages of CPU-based inference while transparently documenting the model's zero-shot generalization limits.

## 2. Assessment of Revisions (Meta-Review)

The author is to be highly commended for this revision. The manuscript has undergone a profound and rigorous transformation, directly addressing all major flaws from the previous submission with remarkable scientific maturity and intellectual honesty:

* **Academic Integrity:** The self-authored "Peer Review Tribunal" has been removed, restoring the paper to standard academic formatting.
* **Appropriate Framing:** The author successfully reframed the Lean 4 proofs. Rather than claiming them as fundamental mathematical breakthroughs in computational physics, they are accurately presented as machine-verified configuration constraints and CI/CD deployment gates. This is a highly compelling and practical use case for formal methods in ML engineering.
* **Corrected FLOP Modeling & Contradictions:** Equation (2) now accurately reflects the true complexity of the Transformer architecture by explicitly including the O(L²d) attention term. By scoping Invariant I1 strictly to the FFN layers, the author brilliantly resolves the previous latency contradiction—explaining the +14.9% Yelp latency increase via sequence length (L ≈ 430) while maintaining that the FFN FLOPs remain invariant.
* **Inclusion of Accuracy Metrics:** Table 1 introduces the previously missing accuracy metrics. The author honestly acknowledges the poor zero-shot/few-shot generalization on complex domains (e.g., 0% on Banking77) and accurately states that supervised fine-tuning (SFT) is required to make the economic argument viable.
* **Removal of Jargon:** The pseudo-scientific terminology ("thermodynamically catastrophic", "Weierstrass existence") has been appropriately grounded as a "weighted linear cost heuristic."

## 3. Strengths

* **High Practical Value:** The core premise—using NAR encoders on serverless CPUs to bypass the GPU shortage for structured ML tasks—is highly relevant to modern industry architectures. The cost savings ($864–$2,520 down to $15–$40/month) represent a massive operational win.
* **Innovative Application of Formal Methods:** Using Lean 4 not to prove neural network convergence, but rather to rigidly enforce hardware deployment constraints, adapter budgets, and cost ordering at compile-time is a creative and highly pragmatic application of formal verification.
* **Exceptional Transparency:** Section 5 (Discussion and Limitations) is excellent. The explicit marking of the open proof obligation (`sorry` on `cpu_energy_bounded`) and the candid discussion of task-specific accuracy limitations build immense trust with the reader.

## 4. Minor Weaknesses & Constructive Feedback

While the paper is fundamentally sound and ready for publication in an applied systems/MLOps venue, the following minor points could be addressed to further strengthen the final camera-ready version:

### A. Justifying Lean 4 vs. Python Validation (e.g., Pydantic)

A reader might logically ask: *"Why use a complex theorem prover like Lean 4 to verify 16 × 22 × 1536 ≤ 600,000 when a simple Python `assert` or a `Pydantic` schema could do this in the deployment script?"*
**Actionable Feedback:** The paper would benefit from a brief 1–2 sentence discussion in Section 5.1 on the specific advantages of Lean 4. For instance, emphasize that Lean 4 provides *compile-time static checking* before any Python runtime environment or cloud resource is initialized, and allows for the composability of proofs across a wider formally verified codebase.

### B. The Gap in the CPU-Replacement Argument

The economic argument (Table 3) is strong, but Table 1 shows the model currently fails at Banking77 and Yelp. The author rightly notes that SFT will fix this. However, to truly claim that this NAR setup can *replace* an AR LLM, the reader needs to know that the model is actually capable of learning the task.
**Actionable Feedback:** Add a sentence or citation referencing standard ModernBERT (or similar encoder) performance on these datasets post-SFT, just to reassure the reader that the model *is capable* of achieving competitive accuracy once properly trained.

### C. Closing the `sorry` Gap (Technical Suggestion for Future Work)

Section 3.7 acknowledges that `cpu_energy_bounded` relies on a `sorry` because it requires runtime telemetry injection.
**Actionable Feedback:** Lean 4 has excellent metaprogramming and FFI (Foreign Function Interface) capabilities. In Section 5.3 (Future Work), consider mentioning that future iterations could use a Lean macro to read the `results_5_datasets_lora.json` file at compile time, inject the concrete variables (τ, M) into the Abstract Syntax Tree, and automatically discharge the proof (e.g., using `norm_num`). This would completely bridge the gap between empirical telemetry and formal verification.

## 5. Conclusion

This is a textbook example of how to respond to harsh peer review. The manuscript pivoted from over-claiming basic arithmetic as theoretical physics to presenting a highly disciplined, intellectually honest application of formal verification for MLOps. The integration of Lean 4 into an ML deployment pipeline is a novel systems engineering idea that deserves to be shared with the community. I highly recommend this paper for acceptance.
