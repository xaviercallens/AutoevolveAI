"""
Unit tests for Community Dissemination RL Pipeline.
Tests the Audience Reward Model, RL Data Harvester, DPO Dataset Builder, and Post Prescriptor.
"""

from __future__ import annotations

import json
from pathlib import Path

from anse.community.audience_reward import compute_audience_reward
from anse.community.dpo_post_generator import export_dpo_dataset, generate_dpo_triplet_for_paper
from anse.community.paper_ingest import PaperItem
from anse.community.post_prescriptor import PostPrescriptor
from anse.community.rl_data_harvester import harvest_curated_seed_posts


def test_audience_reward_clean_vs_hype():
    """Verify reward model rewards modest grounded posts and heavily penalizes hype."""
    clean_title = "[R] Enforcing div(B)=0 to machine precision in Neural Operators via Hodge projection"
    clean_body = (
        "Why do standard neural operators suffer from magnetic monopole drift? In this work, we project into the "
        "Coulomb gauge in Fourier space. Continuous identities are verified in Lean 4 (5 theorems, zero sorry). "
        "Limitation: Strictly requires periodic boundaries (T^d).\n\n"
        "Preprint: https://doi.org/10.5281/zenodo.22160185\nCode: https://github.com/xaviercallens/AutoevolveAI"
    )
    clean_sub_stmt = (
        "Submission Statement: Context on invariant preservation. "
        "AI Disclosure: Produced following Terence Tao guidelines."
    )

    clean_reward = compute_audience_reward(
        subreddit="r/MachineLearning",
        title=clean_title,
        body=clean_body,
        submission_statement=clean_sub_stmt,
    )
    assert clean_reward["total_reward"] >= 0.75
    assert clean_reward["is_recommended"] is True
    assert len(clean_reward["hype_violations"]) == 0

    # Hype post
    hype_title = "REVOLUTIONARY: We Completely Solved Plasma Physics and AGI with AI!"
    hype_body = "This is a disruptive, game-changing paradigm shift. We outperform all human scientists."
    hype_reward = compute_audience_reward(
        subreddit="r/MachineLearning",
        title=hype_title,
        body=hype_body,
    )
    assert hype_reward["total_reward"] < 0.45
    assert hype_reward["is_recommended"] is False
    assert len(hype_reward["hype_violations"]) >= 2
    assert "revolutionary" in hype_reward["hype_violations"]


def test_rl_data_harvester_seeds():
    """Test seed post harvesting and metric attribution."""
    posts = harvest_curated_seed_posts()
    assert len(posts) >= 3
    for p in posts:
        assert p.title
        assert p.body
        assert p.reward_metrics["total_reward"] > 0.50


def test_dpo_preference_triplet_and_export(tmp_path: Path):
    """Test generating and exporting DPO triplets for Hugging Face TRL fine-tuning."""
    paper = PaperItem(
        title="Structure-Preserving MHD Neural Operators",
        abstract="Exact solenoidal constraints in magnetohydrodynamics via discrete Hodge decomposition.",
        doi="10.5281/zenodo.22160185",
    )
    triplet = generate_dpo_triplet_for_paper(paper, "r/MachineLearning")

    assert triplet.prompt
    assert "TITLE:" in triplet.chosen
    assert "TITLE:" in triplet.rejected
    # The chosen post must have a strictly higher reward than the rejected post
    assert triplet.metadata["reward_margin"] > 0.35

    out_file = tmp_path / "dpo_test.jsonl"
    export_dpo_dataset([triplet], out_file)
    assert out_file.exists()

    with open(out_file, encoding="utf-8") as f:
        data = json.loads(f.readline())
        assert data["chosen"] == triplet.chosen
        assert data["rejected"] == triplet.rejected


def test_post_prescriptor_selection():
    """Test that the prescriptor evaluates candidate strategies and prescribes the best one."""
    paper = PaperItem(
        title="Computational Classification of Ramanujan Eta-Quotients",
        abstract="Formal verification and Newman criteria for Dedekind eta-quotients.",
        doi="10.5281/zenodo.22160184",
    )
    prescriptor = PostPrescriptor(subreddit="r/math")
    report = prescriptor.prescribe_best_post(paper)

    assert report.paper_title == paper.title
    assert report.target_subreddit == "r/math"
    assert report.best_candidate is not None
    assert report.best_candidate.reward_breakdown["total_reward"] >= 0.70
    assert len(report.all_candidates) == 3
    assert len(report.best_candidate.anticipated_qa) >= 1
    assert "Submission Statement" in report.best_candidate.submission_statement
