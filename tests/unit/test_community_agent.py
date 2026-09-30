"""
Unit Tests for ANSE Scientific Community Advocate Engine (anse.community)
"""

from anse.community.cognitive_shield import CognitiveShield, CommentCategory
from anse.community.config import (
    DOMAIN_SUBREDDITS,
    ResearchDomain,
)
from anse.community.content_generator import ContentGenerator
from anse.community.paper_ingest import PaperIngestionEngine, PaperItem
from anse.community.reddit_trend_scout import RedditTrendScout


def test_domains_and_subreddits_mapping():
    """Verify that all 7 strategic research domains are defined and have target subreddits."""
    expected_domains = [
        ResearchDomain.RUST_LINUX,
        ResearchDomain.AI_OPTIMIZATION,
        ResearchDomain.OPEN_WEIGHTS,
        ResearchDomain.ASTROPHYSICS,
        ResearchDomain.QUANTUM_COMPUTING,
        ResearchDomain.QUANTUM_PHYSICS,
        ResearchDomain.HPC,
    ]
    for domain in expected_domains:
        assert domain in DOMAIN_SUBREDDITS
        subreddits = DOMAIN_SUBREDDITS[domain]
        assert len(subreddits) >= 2, f"Domain {domain} must have at least 2 target subreddits."


def test_paper_scoring_and_classification():
    """Verify that paper relevance scoring accurately identifies domain keywords."""
    engine = PaperIngestionEngine()

    paper = PaperItem(
        title="Symplectic Integrators and Hamiltonian Mechanics in Lattice Gauge Theory",
        abstract="We implement a symplectic integrator conserving canonical invariants with energy drift bounded by 1e-4.",
        authors=["Alice", "Bob"],
    )
    score = engine.score_paper(paper)
    assert score >= 0.3
    assert ResearchDomain.QUANTUM_PHYSICS in paper.matched_domains

    unrelated_paper = PaperItem(
        title="Baking Sourdough Bread at Room Temperature",
        abstract="A recipe for culinary enthusiasts using natural yeast.",
        authors=["Chef John"],
    )
    unrelated_score = engine.score_paper(unrelated_paper)
    assert unrelated_score < 0.2
    assert len(unrelated_paper.matched_domains) == 0


def test_anti_sensationalism_gate():
    """Verify that banned buzzwords are flagged and clean text passes."""
    gen = ContentGenerator()

    hype_text = "This is a revolutionary, game-changing paradigm shift in AI optimization."
    has_slop, detected = gen.check_sensationalism(hype_text)
    assert has_slop is True
    assert "revolutionary" in detected
    assert "game-changing" in detected
    assert "paradigm shift" in detected

    rigorous_text = "Empirical evaluation shows latency reduced from 14.2ms to 9.8ms with p < 0.01."
    has_slop, detected = gen.check_sensationalism(rigorous_text)
    assert has_slop is False
    assert len(detected) == 0


def test_post_drafting_and_submission_statement():
    """Verify post draft contains necessary structure, links, and submission statement."""
    gen = ContentGenerator()
    paper = PaperItem(
        title="Zero-Allocation SIMD Kernels for Linux io_uring",
        abstract="High-performance systems programming in Rust eliminating heap allocations.",
        authors=["Xavier Callens"],
        source_url="https://doi.org/10.5281/zenodo.12345",
    )

    draft = gen.draft_post_for_paper(
        paper=paper,
        target_subreddit="rust",
        domain=ResearchDomain.RUST_LINUX,
    )

    assert draft.subreddit == "rust"
    assert "Zero-Allocation SIMD Kernels" in draft.title
    assert "Submission Statement & Context:" in draft.submission_statement
    assert "https://doi.org/10.5281/zenodo.12345" in draft.submission_statement
    assert draft.has_banned_buzzwords is False


def test_cognitive_shield_classification():
    """Verify Cognitive Shield classifies incoming comments accurately and determines proper defense action."""
    shield = CognitiveShield()

    # 1. Toxic Ad-Hominem
    res_toxic = shield.classify_comment("You are an idiot and this entire project is complete fraud bullshit.")
    assert res_toxic.category == CommentCategory.TOXIC_AD_HOMINEM
    assert res_toxic.hostility_score >= 0.8
    assert res_toxic.recommended_action == "ignore_starve"
    assert res_toxic.suggested_reply == ""

    # 2. Bad Faith / Cynical Snark
    res_snark = shield.classify_comment("Just another useless hype machine that nobody asked for.")
    assert res_snark.category == CommentCategory.BAD_FAITH_SNARK
    assert res_snark.recommended_action == "de_escalate_once"
    assert "open-source" in res_snark.suggested_reply

    # 3. Technical Critique
    res_tech = shield.classify_comment("What baseline was used for the latency benchmark, and did you measure p-value significance?")
    assert res_tech.category == CommentCategory.TECHNICAL_CRITIQUE
    assert res_tech.recommended_action == "reply_rigorous"

    # 4. Collaboration Interest
    res_collab = shield.classify_comment("Very interesting paper! Can we reproduce this from the github repo and contribute a PR?")
    assert res_collab.category == CommentCategory.COLLABORATION_INTEREST
    assert res_collab.recommended_action == "reply_collaborate"

    # 5. Honest Skepticism
    res_skep = shield.classify_comment("I am skeptical that this generalizes across all hardware. Can you explain why?")
    assert res_skep.category == CommentCategory.HONEST_SKEPTICISM
    assert res_skep.recommended_action == "reply_eli5"


def test_promotional_ratio_enforcement():
    """Verify that the 9:1 community ratio is tracked and flagged if exceeded."""
    scout = RedditTrendScout()

    # Record 1 promo post and 1 comment -> ratio = 50% (> 10%)
    scout.record_action("paper_promotion", {"title": "Paper 1"})
    scout.record_action("comment_response", {"text": "helpful reply"})
    assert scout.get_promotional_ratio() == 0.50

    # Add 9 helpful comments -> 1 promo / 11 total = ~9.1% (< 10%)
    for _ in range(9):
        scout.record_action("comment_response", {"text": "helpful reply"})
    assert scout.get_promotional_ratio() <= 0.10


def test_local_paper_scanning():
    """Verify that scan_local_papers discovers documents in papers/."""
    engine = PaperIngestionEngine()
    papers = engine.scan_local_papers("papers")
    assert len(papers) > 0
    # Check that at least some papers have extracted titles
    titles = [p.title for p in papers]
    assert any("Anse" in t or "Phd" in t or "Cosmo" in t or "Compendium" in t for t in titles)
