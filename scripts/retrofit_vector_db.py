#!/usr/bin/env python3
"""
scripts/retrofit_vector_db.py
==============================
Retrofits verified positive documents, Lean 4 proofs, and Laya Coding Companion
artifacts into ChromaDB vector database, while indexing negative feedback patterns.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from anse.memory.chroma_rag import ChromaRAG


def retrofit_literature(rag: ChromaRAG) -> None:
    print("1. Retrofitting Scientific Literature & Formal Verification Specs...")

    # 1. Accepted Paper v2
    paper_path = PROJECT_ROOT / "papers" / "laya_lean4_formal_paper_v2.tex"
    if paper_path.exists():
        paper_text = paper_path.read_text(encoding="utf-8")
        rag.index_literature_document(
            doc_id="paper_laya_lean4_v2_accept",
            title="Lean 4 Machine-Verified Deployment Invariants for Non-Autoregressive CPU Inference",
            abstract_or_content=paper_text[:4000],
            authors="AutoevolveAI / ANSE Research Team",
            year="2026",
            arxiv_id="cs.DC/2609.xxxxx",
            key_insights="Deployment invariants verified via Lean 4: LoRA parameter budget (I2 <= 600,000), "
                         "FFN FLOP monotonicity, and CPU latency feasibility (<50ms).",
        )
        print("  ✅ Indexed Accepted Paper v2")

    # 2. Lean 4 Formal Source
    lean_path = PROJECT_ROOT / "formal" / "ANSE" / "LayaDecision.lean"
    if lean_path.exists():
        lean_text = lean_path.read_text(encoding="utf-8")
        rag.index_literature_document(
            doc_id="lean4_layadecision_spec",
            title="Lean 4 Deployment Invariant Verification: LayaDecision",
            abstract_or_content=lean_text,
            authors="ANSE Formal Verification Specialist",
            year="2026",
            arxiv_id="formal-spec",
            key_insights="Machine-verified proofs in Lean 4: lora_param_bound, nar_ffn_single_pass_bound, "
                         "nar_ffn_scaling_advantage, nar_energy_monotonicity, cpu_latency_monotonicity.",
        )
        print("  ✅ Indexed Lean 4 LayaDecision Specification")

    # 3. Laya Coding Companion Architecture Document
    arch_doc = PROJECT_ROOT / "data" / "coding_companion"
    if (PROJECT_ROOT / "artifacts" / "laya_coding_companion" / "training_summary.json").exists():
        summary_text = (PROJECT_ROOT / "artifacts" / "laya_coding_companion" / "training_summary.json").read_text()
        rag.index_literature_document(
            doc_id="laya_coding_companion_training_summary",
            title="Laya Coding Companion: 3-Stage LoRA Training on 10 Coding Datasets",
            abstract_or_content=summary_text,
            authors="ANSE Autopoiesis System",
            year="2026",
            arxiv_id="internal-receipt",
            key_insights="3-Stage multi-task LoRA fine-tuning on 10 datasets across 5 pillars. "
                         "Stage 1 Noul gating accuracy: 91.7%, Stage 3 routing accuracy: 91.7%.",
        )
        print("  ✅ Indexed Laya Coding Companion Training Receipts")

    # 4. Negative Reference (Rejected v1 Pattern) with negative=True metadata
    rag.literature_collection.upsert(
        ids=["paper_laya_v1_rejected_negative"],
        documents=[
            "OVERCLAIMING PATTERN (DO NOT REPLICATE):\n"
            "Claiming that proving hardware FLOP constraints is a novel mathematical breakthrough in DEC or differential geometry. "
            "Calling FFN FLOP count singlePassFLOPs without stating that attention O(L^2 d) was omitted. "
            "Failing to report real zero-shot baseline accuracies alongside LoRA deltas."
        ],
        metadatas=[{
            "title": "Negative Example: Overclaiming in Neuro-Symbolic Literature",
            "negative": True,
            "flaw": "academic_overclaiming",
            "remediation": "frame as compile-time configuration verifiers, scope FLOP definitions explicitly",
        }],
    )
    print("  ✅ Indexed Negative Example with negative=True tag")


def retrofit_code_solutions(rag: ChromaRAG) -> None:
    print("\n2. Retrofitting Verified Code Solutions...")

    # Index Laya model implementation
    model_code = (PROJECT_ROOT / "anse" / "laya" / "model.py").read_text(encoding="utf-8")
    rag.index_code_solution(
        doc_id="laya_model_py",
        code_content=model_code,
        task_prompt="Implement non-autoregressive ModernBERT-base model with LoRA rank 8 and multi-task heads for gating, routing, and energy prediction.",
        language="python",
        energy=0.012,
        metadata={"pillar": "system1_dispatch", "status": "VERIFIED_PASS"},
    )

    # Index Laya ANSE Dispatcher
    dispatcher_code = (PROJECT_ROOT / "anse" / "laya" / "integration.py").read_text(encoding="utf-8")
    rag.index_code_solution(
        doc_id="laya_integration_py",
        code_content=dispatcher_code,
        task_prompt="Implement cognitive dispatcher integrating Laya decisions with ANSE specialist agent roles and barrier energy penalty.",
        language="python",
        energy=0.005,
        metadata={"pillar": "cognitive_dispatcher", "status": "VERIFIED_PASS"},
    )
    print("  ✅ Indexed verified Laya model and integration modules into ltm_code_solutions")


def main() -> None:
    print("=" * 60)
    print("ANSE Vector DB Retrofit (ChromaDB)")
    print("=" * 60)
    rag = ChromaRAG()
    retrofit_literature(rag)
    retrofit_code_solutions(rag)

    print("\n3. Testing Query Retrieval from ChromaDB...")
    hits = rag.query_literature("Lean 4 LoRA parameter budget invariant", n_results=2)
    print(f"  Retrieved {len(hits)} literature hits:")
    for h in hits:
        print(f"    - ID: {h['id']} | Title: {h['metadata'].get('title')}")

    code_hits = rag.query_code("non-autoregressive dispatcher with LoRA", n_results=1)
    print(f"  Retrieved {len(code_hits)} code solution hits:")
    for h in code_hits:
        print(f"    - ID: {h['id']} | Language: {h['metadata'].get('language')}")

    print("\n✅ ChromaDB Vector DB Retrofit completed successfully.")


if __name__ == "__main__":
    main()
