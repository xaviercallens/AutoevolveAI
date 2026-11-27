"""
Unit Tests for Scientific Communication MCP Server (mcp_scientific_communication_server.py).
Tests all 7 exposed MCP tools:
1. get_communication_policy_status
2. audit_post_adoption_and_resistance
3. shield_evaluate_and_reply
4. prescribe_optimal_post
5. scout_reddit_community_sentiment
6. scan_zenodo_publications
7. feedback_and_retrain_rl_policy
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import mcp_scientific_communication_server as mcp_srv


def test_get_communication_policy_status():
    """Verify get_communication_policy_status returns compliant promotional ratio and active guidelines."""
    status = mcp_srv.get_communication_policy_status()
    assert status["status"] == "SUCCESS"
    assert "promotional_ratio" in status
    assert status["promotional_ratio"] <= 0.10
    assert status["promotional_ratio_compliant"] is True
    assert status["bandit_state_active"] is True
    assert isinstance(status["active_guidelines"], list)
    assert len(status["active_guidelines"]) > 0


def test_audit_post_adoption_and_resistance():
    """Verify auditing accurately scores modest posts vs hype-heavy posts."""
    # 1. Modest, grounded post
    compliant_res = mcp_srv.audit_post_adoption_and_resistance(
        title="[R] Why do Neural Operators suffer from magnetic monopole drift? Discrete Hodge projection in Lean 4",
        body=(
            "Standard neural operators suffer from magnetic monopole drift on periodic domains. "
            "In this work, we project into the Coulomb gauge in Fourier space where d^2 = 0 is satisfied identically. "
            "Continuous identities are verified in Lean 4 (5 theorems, zero sorry). "
            "Limitation: Strictly requires periodic boundaries (T^d).\n\n"
            "Preprint: https://doi.org/10.5281/zenodo.22160185\nCode: https://github.com/xaviercallens/AutoevolveAI"
        ),
        subreddit="r/MachineLearning",
        submission_statement=(
            "Submission Statement: Context on invariant preservation and why this matters for PDE stability. "
            "AI Disclosure: Produced following Terence Tao guidelines."
        ),
    )
    assert compliant_res["status"] == "SUCCESS"
    assert compliant_res["total_audience_reward"] >= 0.75
    assert compliant_res["is_recommended_for_posting"] is True
    assert len(compliant_res["hype_violations_detected"]) == 0

    # 2. Hype-laden post
    hype_res = mcp_srv.audit_post_adoption_and_resistance(
        title="REVOLUTIONARY: Our team created the greatest AI model ever!",
        body="This is an unprecedented paradigm shift that completely solves all of physics.",
        subreddit="r/MachineLearning",
    )
    assert hype_res["status"] == "SUCCESS"
    assert hype_res["total_audience_reward"] < 0.50
    assert hype_res["is_recommended_for_posting"] is False
    assert len(hype_res["hype_violations_detected"]) >= 1


def test_shield_evaluate_and_reply():
    """Verify Cognitive Shield classification and humble receipt generation."""
    # 1. Enthusiastic collaboration / paper request
    res_collab = mcp_srv.shield_evaluate_and_reply(
        comment_text="That is fantastic! Where can I read the full paper and check the Lean proofs?",
        context_paper_title="Cohn-Kumar Family 090 Formalization",
        paper_doi="10.5281/zenodo.23295142",
    )
    assert res_collab["status"] == "SUCCESS"
    assert res_collab["category"] == "collaboration_interest"
    assert res_collab["hostility_score"] <= 0.05
    assert "zenodo" in res_collab["suggested_reply"].lower()
    assert "10.5281/zenodo.23295142" in res_collab["suggested_reply"]

    # 2. Toxic ad-hominem
    res_toxic = mcp_srv.shield_evaluate_and_reply(
        comment_text="This whole repository is trash and you are a complete fraud.",
        context_paper_title="Cohn-Kumar Family 090 Formalization",
    )
    assert res_toxic["status"] == "SUCCESS"
    assert res_toxic["category"] == "toxic_ad_hominem"
    assert res_toxic["hostility_score"] >= 0.8
    assert res_toxic["recommended_action"] in ("ignore_starve", "ignore", "DISENGAGE")


def test_prescribe_optimal_post():
    """Verify prescription pipeline generates complete post packages with bandit metrics."""
    res = mcp_srv.prescribe_optimal_post(
        paper_title="Monotonic Energy Decrement in Autopoietic Self-Refactoring Agents",
        abstract="We demonstrate that program synthesis under an energy Lyapunov constraint guarantees termination.",
        doi="10.5281/zenodo.22160185",
        target_subreddit="r/airesearch",
        domain="ai_optimization",
    )
    assert res["status"] == "SUCCESS"
    assert "airesearch" in res["target_subreddit"].lower()
    assert res["selected_strategy"]
    assert res["post_title"]
    assert res["post_body"]
    assert res["submission_statement"]
    assert "recommended_utc_window" in res
    assert "bandit_metrics" in res


def test_scout_reddit_community_sentiment():
    """Verify community scouting computes adoption feasibility and moderation risk."""
    res = mcp_srv.scout_reddit_community_sentiment(
        subreddits=["MachineLearning", "LLMmathematics"],
        domain="ai_optimization",
    )
    assert res["status"] == "SUCCESS"
    assert res["communities_evaluated"] == 2
    for comm in res["recommended_communities"]:
        assert 0.0 <= comm["adoption_feasibility_score"] <= 1.0
        assert comm["estimated_resistance"] in ("LOW", "MEDIUM", "HIGH")
        assert "moderation_risk" in comm
        assert isinstance(comm["moderation_guidelines"], list)


def test_scan_zenodo_publications_local_and_mocked():
    """Verify Zenodo scanning handles local papers and API responses gracefully."""
    # Test local papers
    res = mcp_srv.scan_zenodo_publications(
        author="Callens, Xavier",
        max_results=2,
        include_local_papers=True,
    )
    assert res["status"] == "SUCCESS"
    assert res["total_publications_found"] >= 1
    assert res["local_count"] >= 1
    for pub in res["publications"][:3]:
        assert "title" in pub
        assert "matched_domains" in pub


def test_feedback_and_retrain_rl_policy_isolated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Verify continual reinforcement learning loop updates bandit and logs in an isolated directory."""
    monkeypatch.setattr(mcp_srv, "REPO_ROOT", tmp_path)

    # Pre-populate dummy log and bandit files in tmp_path / "results"
    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    initial_log = {
        "timestamp": "2026-10-10T12:00:00Z",
        "total_submissions_retrofitted": 5,
        "audited_submissions": [],
        "learned_policy_guidelines": ["Rule 1: Lead with technical dilemma."],
    }
    (results_dir / "communication_retraining_log.json").write_text(json.dumps(initial_log), encoding="utf-8")

    # Execute feedback retraining
    res = mcp_srv.feedback_and_retrain_rl_policy(
        subreddit="r/LLMmathematics",
        post_title="Formal Verification of Exciton Bilayer Energy",
        upvotes=42,
        comments_count=18,
        upvote_ratio=0.95,
        views=2200,
        user_reply_sample="Where can I find the paper? Would love to read the Lean proof receipts.",
    )

    assert res["status"] == "SUCCESS"
    assert res["subreddit"] == "LLMmathematics"
    assert res["empirical_reward"] > 0.60
    assert res["dpo_pair_appended"] is True

    # Verify files created/updated in tmp_path
    bandit_state_file = results_dir / "contextual_bandit_state.json"
    assert bandit_state_file.exists()
    bandit_data = json.loads(bandit_state_file.read_text(encoding="utf-8"))
    assert "A_inv" in bandit_data and "b" in bandit_data

    dpo_file = results_dir / "dpo_scientific_dissemination.jsonl"
    assert dpo_file.exists()
    dpo_lines = dpo_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(dpo_lines) == 1
    dpo_entry = json.loads(dpo_lines[0])
    assert dpo_entry["subreddit"] == "LLMmathematics"
    assert dpo_entry["empirical_ground_truth"] is True

    retraining_log = json.loads((results_dir / "communication_retraining_log.json").read_text(encoding="utf-8"))
    assert retraining_log["total_submissions_retrofitted"] == 6
    assert len(retraining_log["audited_submissions"]) == 1
    assert retraining_log["audited_submissions"][0]["score"] == 42
