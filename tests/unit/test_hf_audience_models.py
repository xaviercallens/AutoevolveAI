"""
Unit tests for Hugging Face Pretrained Models Integration.
Tests ModernBERT semantic relevance scoring and Qwen2.5-0.5B CPU generation.
"""

from __future__ import annotations

from anse.community.hf_audience_models import ModernBERTSemanticScorer, QwenCPUGenerator
from anse.community.paper_ingest import PaperItem
from anse.community.post_prescriptor import PostPrescriptor


def test_modernbert_semantic_scorer():
    """Verify ModernBERT or fallback computes similarity within [0, 1]."""
    scorer = ModernBERTSemanticScorer()
    text_a = "Solenoidal constraints in Magnetohydrodynamics neural operators"
    text_b = "Exact divergence-free magnetic field projections in plasma physics"
    text_c = "Recipe for baking sourdough bread in high temperature oven"

    sim_ab = scorer.compute_similarity(text_a, text_b)
    sim_ac = scorer.compute_similarity(text_a, text_c)

    assert 0.0 <= sim_ab <= 1.0
    assert 0.0 <= sim_ac <= 1.0
    # Technical match should score higher than unrelated sourdough bread
    assert sim_ab > sim_ac


def test_qwen_cpu_generator():
    """Verify Qwen2.5-0.5B or heuristic generates non-empty titles and de-escalating replies."""
    generator = QwenCPUGenerator()
    title = generator.generate_candidate_title(
        "Structure-Preserving Neural Operators", "problem_curiosity"
    )
    assert title
    assert len(title) > 10

    reply = generator.generate_comment_reply(
        user_comment="Why not just add a soft penalty term?",
        paper_summary="Enforcing solenoidal bounds via discrete Hodge projection",
    )
    assert reply
    assert len(reply) > 20


def test_post_prescriptor_with_hf_models():
    """Verify PostPrescriptor integrates HF models and contextual bandit."""
    paper = PaperItem(
        title="Structure-Preserving MHD Neural Operators",
        abstract="Exact solenoidal constraints in magnetohydrodynamics via discrete Hodge projection.",
        doi="10.5281/zenodo.22160185",
    )
    prescriptor = PostPrescriptor(subreddit="r/MachineLearning", use_hf_models=True)
    report = prescriptor.prescribe_best_post(paper)

    assert report.paper_title == paper.title
    assert report.target_subreddit == "r/MachineLearning"
    assert report.best_candidate is not None
    assert report.best_candidate.reward_breakdown["total_reward"] >= 0.70
    assert report.bandit_recommendation
    assert "action_id" in report.bandit_recommendation
