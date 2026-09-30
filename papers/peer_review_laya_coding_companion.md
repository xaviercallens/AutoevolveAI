# Peer Review Record: Laya-LoRA Coding Companion Paper
# Recorded verbatim: 2026-09-30T22:26Z
# Paper: laya_coding_companion_paper.tex
# PDF SHA256: 366febbf97614dd2a3cb9420113c4e0e96e2c7f02f65f18a85525728435037c0

---

# Peer Review Report — Reviewer 1
**Track:** Systems for ML / MLOps — IEEEtran Conference Format
**Overall Recommendation:** **Weak Accept**

## Criterion Scores

| Criterion | Score |
|---|---|
| **R1 Academic Integrity** | **Accept** |
| **R2 Formal Verification Honesty** | **Minor Revision** |
| **R3 FLOP Model Correctness** | **Accept** |
| **R4 Accuracy Completeness** | **Minor Revision** |
| **R5 Telemetry Provenance** | **Minor Revision** |
| **R6 Language Calibration** | **Accept** |

## Detailed Criterion Justifications

### R1 — Academic Integrity

**Score: Accept**

The paper passes all academic integrity checks. The sole author is named (Xavier Callens), and the affiliation is explicitly stated as "AutoevolveAI / ANSE Open-Source Research" — a self-identified open-source initiative rather than a fictional university or industry lab. The Acknowledgements section explicitly states: *"No fictitious institutional affiliation is claimed. All experiments were conducted on commodity x86_64 CPU hardware (prototype) with GCP Vertex AI used for production-scale training design."* This is an unusually candid disclosure. The paper self-cites two prior works (`callens2026anse`, `callens2026lean4`), both attributed to the same author and same initiative — acceptable provided neither is presented as independent external validation of the present work's claims, which they are not.

One minor concern: `callens2026lean4` is cited as a published "Systems for ML / MLOps Track" paper but supplies only a SHA-256 hash rather than a DOI, proceedings name, or page range. If this paper has been published in a trackable venue, a proper citation identifier is required. If it is a companion arXiv preprint, it should be cited accordingly.

---

### R2 — Formal Verification Honesty

**Score: Minor Revision**

The treatment of Lean 4 invariants is admirably honest in places but has one structural problem that requires revision.

**Positive:** Invariant I1 (FFN FLOP Monotonicity) is correctly scoped. Invariant I2 (LoRA Parameter Budget) is concrete, numerically verifiable (577,584 ≤ 600,000). Invariant I3 (Energy Cost Ordering) honestly discloses a residual `sorry` obligation.

**Problem:** The paper claims in Section 7 that "these invariants are evaluated at compile time via `lake build`. A failing invariant raises a Lean 4 type error before any Python runtime or cloud resource is initialised." This statement is **partially false** for Invariant I3, which carries an unresolved `sorry`. A `sorry` in Lean 4 does not raise a type error — it suppresses one. A Lean file containing `sorry` will compile successfully (with a warning, not an error). Thus the claim of pre-deployment blocking does not hold for I3. The abstract line "Lean 4 deployment invariants verify at compile time that ... energy cost ordering hold" overclaims.

---

### R3 — FLOP Model Correctness

**Score: Accept**

The abstract explicitly names the O(L²d) omission. Section 7 repeats the scope note within Invariant I1's definition box. Section 8 lists "Attention FLOP omission: Invariant I1 covers FFN layers only." This triple acknowledgement satisfies the transparency requirement. The LoRA parameter count algebra is internally consistent.

---

### R4 — Accuracy Completeness

**Score: Minor Revision**

**Positive:** The paper explicitly computes and reports the random baseline (50.0%). The per-case breakdown (Table 3) shows which 8/12 cases fail. The 91.7% Stage 1 noul accuracy is attributed to a 12-sample validation split.

**Problem 1:** A 12-sample validation split is statistically uninformative. 91.7% on 12 samples = 11/12 correct. A Wilson 95% CI is approximately [61.5%, 99.8%]. Presenting 91.7% without this context misleads readers.

**Problem 2:** The ChoiceHead (40-class routing) and ScoreHead (energy regression) accuracies are not evaluated. Since Laya is presented as a three-headed model, routing and scoring head baselines should be reported.

---

### R5 — Telemetry Provenance

**Score: Minor Revision**

**Issue 1 (Critical):** The data lake is at `gs://socrate-ai-datalake/` — a private GCP bucket with no IAM sharing policy, signed URL, or alternative mirror. A SHA-256 hash is only useful for provenance if reviewers can independently obtain the file to verify the hash. As written, the provenance claim is unverifiable by any external reader.

**Issue 2 (Moderate):** Table 4's energy figures for AR baselines (GPT-4o: 120 Wh/1k, Qwen2.5-7B: 38.5 Wh/1k) have no citations in the bibliography. For a paper whose central claim is 101× energy advantage, baseline energy figures require citation-level provenance.

**Issue 3 (Minor):** The `callens2026lean4` bibliography entry supplies a SHA-256 hash, not a DOI or arXiv ID.

---

### R6 — Language Calibration

**Score: Accept**

The manuscript is free of pseudo-scientific jargon, fictional affiliations, and overclaiming language. The System 1/System 2 framing is grounded in appropriately cited sources (Kahneman 2011, Bengio 2019). The E(x) = 10⁶ blocking convention is not presented as a physical energy measurement.

One minor note: "demonstrates" in the abstract should be "estimates" or "projects" for the Wh energy figures, as these are derived estimates not direct power-meter measurements.

---

## Top 3 Specific Weaknesses

**W1 — Lean 4 `sorry` and Compile-Time Guarantee Overclaim (R2)**
The abstract and Section 7 must be revised to qualify that I3's compile-time guarantee is pending discharge of the `sorry` obligation. The sentence *"energy cost ordering hold before any cloud resource is initialised"* in the abstract is inaccurate.

**W2 — Inaccessible Data Artifacts and Unverifiable Provenance (R5)**
The three JSON receipt files must be published on a public mirror (Zenodo, HuggingFace, or GitHub release) with direct URLs added to the Data Availability section, or the bucket must be described as private with reviewer access contact information.

**W3 — Statistical Validity of Validation Accuracy on 12 Samples (R4)**
Stage 1's 91.7% accuracy and the 33.3% benchmark accuracy must be accompanied by Wilson or Clopper-Pearson 95% confidence intervals, or explicitly disclaimed as high-variance 12-sample estimates.

## Summary

Laya-LoRA Coding Companion is a disciplined, honest system design paper. Its below-random benchmark accuracy is plainly stated, its Lean 4 `sorry` is disclosed and located, its FLOP omission is triple-acknowledged, and its affiliation is genuine. These qualities are rare. The weaknesses are correctable: the `sorry`/compile-time guarantee language requires tightening (W1), the provenance chain requires a public artifact mirror (W2), and the 12-sample accuracy statistics require confidence intervals (W3). The baseline energy comparison also needs explicit citations. Addressing these four issues would bring this paper to a clean Accept for a systems-for-ML workshop track.

---

---

# Peer Review Report — Reviewer 2
**Track:** ML Engineering / LoRA Adaptation Track
**Overall Recommendation:** **Weak Reject**

The paper presents a coherent, well-documented system design with commendable provenance hygiene (SHA-256 JSON receipts), but in its current form it is a prototype design proposal, not a completed empirical contribution. Every result derives from 120 samples/stage (1 epoch, CPU-only) — 650× smaller than the claimed training corpus. The 33.3% gate accuracy is below the 50% random baseline for the binary task.

## Strengths (4)

- **Exceptional SHA-256 provenance hygiene** — machine-verified telemetry traceability embedded in the LaTeX source is above the norm for systems-ML papers.
- **Honest, exhaustive limitations section** — Section 5 explicitly names prototype scale, JIT warm-up conflation, the Lean 4 `sorry` obligation, attention FLOP omission, and cross-environment baseline caveats.
- **Architecturally sound System 1/2 decomposition** — 100% precision on blocking sub-task (4/4 BLOCKED cases) validates the NAR encoder hypothesis.
- **Reproducible GCP infrastructure spec** — executable `gcloud run deploy` snippet; Vertex AI job spec with machine type, container, and cost estimate (\$7.84/run) is actionable.

## Weaknesses (4)

### W1 — LoRA Parameter Arithmetic Discrepancy
Eq. (2) yields 539,136 for LoRA-only params. Independent calculation gives **540,672** (discrepancy: 1,536 params). Head architecture (ChoiceHead: Linear(768,256)+Linear(256,40)) contributes ~207,400 params alone — far larger than the implied 38,448 "head parameters" gap. An explicit itemized parameter count is required.

### W2 — 12-Sample Validation Is Statistically Indefensible
91.7% noul accuracy = 11/12 examples with 95% Wilson CI [61.5%, 99.8%]. One misclassified example shifts the metric ±8.3%. Not a publishable accuracy figure without confidence intervals.

### W3 — Baseline Comparison Matrix Is Incommensurable
Laya's 3,912 ms first-call latency vs. Qwen's warm-path 385 ms is not a fair comparison. No citations for Qwen2.5-7B energy (38.5 Wh/1k) or frontier API energy (120 Wh/1k). No visual distinction between measured vs. estimated values.

### W4 — Stage 2 Data Imbalance, Synthetic Data, Incomplete Citations
- Stage 2 (1,263 records) is 37× smaller than Stage 1 — catastrophic forgetting not investigated.
- Magpie-Qwen2.5-20k is synthetic AR data; no quality filter; potentially circular.
- CodeRM-UnitTest, SWE-Perf, Zenodo RAPL citations lack DOI/arXiv IDs.
- No held-out test split — accuracy from 12-example validation set only.

## Required Actions Before Accept

1. Complete full 10-epoch Vertex AI A100 training; report on ≥5,000-example held-out test split.
2. Provide itemized LoRA + head parameter count table.
3. Mark non-measured Table III values as [estimated] with primary source citations.
4. Lead abstract with warm-path latency (35–58 ms), not first-call (3,912 ms).
5. Add threshold-vs-F1 curve for τ_noul = 0.3.

**Confidence: 3 — High**

---

---

# Peer Review Report — Reviewer 3
**Track:** Code Intelligence Track
**Overall Recommendation:** **Weak Accept**

## Summary

The manuscript for the Laya-LoRA Coding Companion presents a disciplined and candid system design suitable for a Systems for ML/MLOps track. The paper outlines a 149M parameter non-autoregressive encoder adapted via LoRA to route code based on quality and security, demonstrating a substantial energy advantage over autoregressive baselines. The work stands out for its transparency regarding its limitations and open-source origins, though it requires specific revisions regarding its formal verification claims, data accessibility, and statistical reporting before final acceptance.

## Strengths & Academic Integrity

* **Radical Transparency:** The paper honestly reports a prototype gate accuracy of 33.3% on its 12-case benchmark, acknowledging this is below the 50.0% random baseline due to conservative blocking bias.

* **Scoped Formal Constraints:** The authors explicitly and repeatedly acknowledge the omission of the O(L²d) attention FLOP bound in their Lean 4 invariants, satisfying FLOP model correctness transparency.

* **Authentic Affiliation:** The manuscript is free of fictional institutional affiliations, clearly attributing the work to the AutoevolveAI open-source initiative and noting the use of commodity CPU hardware for prototype experiments.

## Key Weaknesses & Required Revisions

* **Lean 4 Compile-Time Guarantee Overclaim:** The abstract and Section VII claim that Lean 4 deployment invariants verify energy cost ordering at compile time, raising a type error if failing. However, Invariant 3 carries a `sorry` obligation. Because a `sorry` in Lean 4 suppresses type errors rather than raising them, the claim of pre-deployment blocking is partially false and must be qualified.

* **Inaccessible Data Artifacts:** The paper relies on SHA-256 hashes for dataset and telemetry provenance, but the artifacts are hosted on a private GCP bucket (`gs://socrate-ai-datalake/`). These JSON receipts must be published on a public mirror (e.g., Zenodo, Hugging Face, or GitHub) to make the provenance claims verifiable. Additionally, baseline energy figures for models like GPT-4o and Qwen2.5-7B (120.00 Wh/1k and 38.50 Wh/1k, respectively) require citation-level provenance.

* **Statistical Validity on Small Samples:** The reported 91.7% Stage 1 accuracy is derived from a 12-sample validation split. This estimate is statistically uninformative without a Wilson or Clopper-Pearson 95% confidence interval. Furthermore, the paper fails to report baseline accuracies for the 40-class routing (ChoiceHead) and energy regression (ScoreHead) tasks.


---

# Peer Review Report — Reviewer 3 (Full Extended Version from Code Intelligence Track)
**Track:** Applied AI Scientist — Code Intelligence, Software Quality Metrics, Energy-Aware Computing, Formal Methods
**Review Date:** 2026-09-30
**Overall Recommendation:** **Weak Accept** — Accept with mandatory minor revisions

## Key Innovation Assessment

The core innovation is the explicit framing of an encoder-only (NAR) model as a **System 1 pre-filter gatekeeper** within a broader two-system coding agent architecture, trained via three-stage curriculum learning with stage-specific multi-objective loss weighting across three concurrent task heads (binary gate, 40-class routing, energy regression). The most technically differentiated contribution is the use of Lean 4 compile-time deployment invariants as configuration compliance gates — verified before any Python runtime or cloud resource is initialized — a novel application of formal methods to MLOps infrastructure that the literature has not previously demonstrated.

## 4 Specific Strengths

**S1 — Radical Transparency on Training Scale:** The paper explicitly reports that prototype training used only 120 samples/stage for 1 epoch on CPU — approximately 0.15% of the full corpus. This level of honesty about prototype constraints is rare and should be held as a model for the field.

**S2 — SHA-256 Provenance Chain:** Machine-derived JSON receipts with SHA-256 hashes for training, benchmark, and download artifacts represent a serious, principled commitment to reproducible telemetry. The statement "all numeric values are machine-derived from JSON receipts and are not estimated by the language model" directly addresses a well-documented failure mode of AI-assisted research writing.

**S3 — Lean 4 Compile-Time MLOps Invariants with Honest Scoping:** Invariant I2 (LoRA budget ≤ 600,000 parameters, verified at `lake build` time) is a genuinely innovative use of a proof assistant for MLOps configuration governance. The explicit scoping of I1 to FFN layers only (with a documented `sorry` obligation) demonstrates methodological maturity.

**S4 — Coherent System Architecture with Production-Realistic Deployment Design:** The three-head architecture with E(x) → 10⁶ for blocked patterns is well-defined. The Cloud Run scale-to-zero inference design is appropriate for bursty coding-companion workloads. The cost comparison ($0.40–$1.20/month vs. $360–$864/month) is directionally compelling.

## 4 Specific Weaknesses with Actionable Suggestions

### W1 — N=12 Validation Set Renders Core Accuracy Claims Statistically Invalid

At N=12, Wilson score 95% CI for 91.7% is approximately [59%, 99%] — statistically uninformative. Both Stage 1 (91.7%) and Stage 3 (91.7%) being identical on such a small set suggests a potential label imbalance artifact (11/12) rather than genuine convergence to different equilibria.

**Action:** Run the Stage 3 checkpoint in inference mode against a stratified 10% hold-out (~7,850 records). Report accuracy, F1-macro, precision/recall per class, and a confusion matrix for the noul gate. Retain the 12-case benchmark as a qualitative illustration only.

### W2 — Energy Measurement Methodology Missing for the Headline Claim

"0.38 Wh per 1,000 queries" and "101× less than Qwen2.5-Coder-7B" are the primary differentiators in the abstract, yet nowhere is the energy measurement methodology described: no measurement instrument (Intel RAPL? CodeCarbon?), no CPU hardware model, no sequence length confirmation, no warm/cold path clarification. This is inconsistent with the paper's stated SHA-256 provenance commitments.

**Action:** Add ≤6-line "Energy Measurement Protocol" subsection to §4 and qualify the 0.38 Wh figure with hardware and methodology context. For the Qwen-7B 38.5 Wh baseline, cite the specific benchmark paper or add "Directional comparison only; not re-measured under matched conditions."

### W3 — ChoiceHead Taxonomy and Dataset-to-Class Supervision Mapping Is Missing

The 40-class routing head is architecturally defined but its class taxonomy is never enumerated anywhere in the paper. No routing accuracy or macro-F1 is reported for any training stage. With 10 training datasets covering ~6–8 task categories, how 40 routing classes receive meaningful training signal is completely unexplained.

**Action:** Provide a table enumerating all 40 routing classes with class label, assigned specialist role, primary training dataset(s), and record count. Report per-class macro-F1 in Table 2, or add a routing evaluation table. Routing is one of three claimed contributions; it currently has zero quantitative evaluation.

### W4 — SmellBench Citation Error and Zenodo RAPL Dataset Missing DOI

The `tambon2024smellbench` citation attributes SmellBench to Tambon (2024) but Tambon's 2024 work focuses on HuggingFace model reuse, not code smell benchmarking. The Zenodo RAPL Energy dataset has no authors, no DOI, no dataset version — yet it provides the primary ground-truth energy signal for the `s_score` regression head.

**Action:** Verify SmellBench authorship at its HuggingFace URL and correct the bibitem. Provide the full Zenodo DOI, author list, version number, and add two sentences describing what hardware generated the RAPL measurements and how raw energy values were normalized into regression targets.

## Final Recommendation Rationale

This paper occupies a valuable and underserved niche: honest about its prototype status while making substantive architectural and formal methods contributions. With all four weaknesses addressed in a revision, this would be a solid, honest, and methodologically interesting contribution to the Systems for ML / MLOps track.

**Overall Score: 3.5/5 — Weak Accept pending mandatory minor revisions**

