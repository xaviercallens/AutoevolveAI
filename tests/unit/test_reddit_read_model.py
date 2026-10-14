"""
Unit Tests for Reddit Read Model (anse.community.reddit_trend_scout)
Tests post fetching, comment ingestion, error resilience, topic clustering, and opportunity ranking.
"""

from unittest.mock import MagicMock, patch

import httpx

from anse.community.config import CommunityConfig, ResearchDomain
from anse.community.reddit_trend_scout import (
    RedditComment,
    RedditThread,
    RedditTrendScout,
    TrendReport,
)


def _create_mock_reddit_posts_json(subreddit: str = "rust") -> dict:
    """Helper creating a simulated Reddit public JSON listing."""
    return {
        "kind": "Listing",
        "data": {
            "children": [
                {
                    "kind": "t3",
                    "data": {
                        "id": "t3_001",
                        "subreddit": subreddit,
                        "title": "Announcing a new zero-allocation SIMD library in Rust",
                        "selftext": "We implemented AVX-512 kernels with zero heap allocations on Linux.",
                        "author": "rustacean_42",
                        "score": 350,
                        "num_comments": 48,
                        "url": "https://github.com/example/simd-rust",
                        "permalink": f"/r/{subreddit}/comments/t3_001/announcing_simd/",
                        "created_utc": 1727680000.0,
                    },
                },
                {
                    "kind": "t3",
                    "data": {
                        "id": "t3_002",
                        "subreddit": subreddit,
                        "title": "How to optimize memory ordering with io_uring in Linux kernel?",
                        "selftext": "I am experiencing subtle latency spikes when submitting ring queues.",
                        "author": "kernel_dev",
                        "score": 120,
                        "num_comments": 25,
                        "url": "https://reddit.com/r/rust/comments/t3_002/io_uring/",
                        "permalink": f"/r/{subreddit}/comments/t3_002/io_uring/",
                        "created_utc": 1727685000.0,
                    },
                },
            ]
        },
    }


def _create_mock_reddit_comments_json(subreddit: str = "rust", thread_id: str = "t3_001") -> list:
    """Helper creating simulated Reddit comments JSON listing ([post_listing, comments_listing])."""
    return [
        {"kind": "Listing", "data": {"children": []}},
        {
            "kind": "Listing",
            "data": {
                "children": [
                    {
                        "kind": "t1",
                        "data": {
                            "id": "c_101",
                            "author": "benchmarker_pro",
                            "body": "What baseline compiler flags did you use, and how does this compare to C++?",
                            "score": 45,
                            "created_utc": 1727686000.0,
                            "parent_id": thread_id,
                            "permalink": f"/r/{subreddit}/comments/{thread_id}/comment/c_101/",
                        },
                    },
                    {
                        "kind": "t1",
                        "data": {
                            "id": "c_102",
                            "author": "[deleted]",
                            "body": "Very impressive zero-allocation numbers.",
                            "score": 12,
                            "created_utc": 1727687000.0,
                            "parent_id": thread_id,
                            "permalink": f"/r/{subreddit}/comments/{thread_id}/comment/c_102/",
                        },
                    },
                ]
            },
        },
    ]


def test_reddit_thread_and_comment_dataclasses():
    """Verify dataclass serialization, formatting, and link rendering."""
    thread = RedditThread(
        id="t3_abc",
        subreddit="MachineLearning",
        title="[R] Autopoietic Neuro-Symbolic Models",
        selftext="A" * 300,  # Long selftext
        author="researcher1",
        score=250,
        num_comments=30,
        url="https://arxiv.org/abs/2312.00000",
        permalink="/r/MachineLearning/comments/t3_abc/paper/",
        created_utc=1727680000.0,
        matched_keywords=["quantization", "jepa"],
        relevance_to_anse=0.85,
    )
    d = thread.to_dict()
    assert d["id"] == "t3_abc"
    assert len(d["selftext"]) < 250  # Must be truncated
    assert d["permalink"] == "https://reddit.com/r/MachineLearning/comments/t3_abc/paper/"
    assert d["relevance_to_anse"] == 0.85

    comment = RedditComment(
        id="c_xyz",
        thread_id="t3_abc",
        subreddit="MachineLearning",
        author="critic",
        body="Detailed inquiry regarding error bounds",
        score=15,
        created_utc=1727681000.0,
        parent_id="t3_abc",
        permalink="/r/MachineLearning/comments/t3_abc/comment/c_xyz/",
    )
    cd = comment.to_dict()
    assert cd["id"] == "c_xyz"
    assert cd["thread_id"] == "t3_abc"
    assert cd["author"] == "critic"
    assert cd["permalink"].startswith("https://reddit.com")


def test_fetch_subreddit_posts_rest_mock():
    """Verify fetch_subreddit_posts properly parses Reddit JSON response in unauthenticated REST mode."""
    config = CommunityConfig(reddit_client_id="")  # Unauthenticated
    scout = RedditTrendScout(config)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = _create_mock_reddit_posts_json("rust")

    with patch("httpx.Client.get", return_value=mock_resp):
        posts = scout.fetch_subreddit_posts("rust", listing="hot", limit=5)

    assert len(posts) == 2
    p1, p2 = posts[0], posts[1]

    assert p1.id == "t3_001"
    assert p1.subreddit == "rust"
    assert "zero-allocation" in p1.title
    assert p1.author == "rustacean_42"
    assert p1.score == 350
    assert p1.num_comments == 48

    assert p2.id == "t3_002"
    assert "io_uring" in p2.title
    assert p2.author == "kernel_dev"


def test_fetch_subreddit_posts_error_resilience():
    """Verify that HTTP 429 rate limit or network exception does not crash and returns empty list."""
    scout = RedditTrendScout(CommunityConfig(reddit_client_id=""))

    # Test HTTP 429 Rate Limit
    mock_resp_429 = MagicMock()
    mock_resp_429.status_code = 429
    with patch("httpx.Client.get", return_value=mock_resp_429):
        posts_429 = scout.fetch_subreddit_posts("rust")
        assert posts_429 == []

    # Test Network Timeout / ConnectError
    with patch("httpx.Client.get", side_effect=httpx.ConnectTimeout("Connection timed out")):
        posts_timeout = scout.fetch_subreddit_posts("rust")
        assert posts_timeout == []


def test_fetch_thread_comments_rest_mock():
    """Verify fetch_thread_comments extracts top-level comments correctly from Reddit JSON."""
    scout = RedditTrendScout(CommunityConfig(reddit_client_id=""))

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = _create_mock_reddit_comments_json("rust", "t3_001")

    with patch("httpx.Client.get", return_value=mock_resp):
        comments = scout.fetch_thread_comments("rust", "t3_001", limit=10)

    assert len(comments) == 2
    c1, c2 = comments[0], comments[1]

    assert c1.id == "c_101"
    assert c1.author == "benchmarker_pro"
    assert "baseline compiler flags" in c1.body
    assert c1.score == 45
    assert c1.parent_id == "t3_001"

    assert c2.id == "c_102"
    assert c2.author == "[deleted]"
    assert c2.score == 12


def test_fetch_subreddit_posts_and_comments_praw_mock():
    """Verify that when PRAW is configured, the read engine uses PRAW submission/comment objects."""
    scout = RedditTrendScout(CommunityConfig(reddit_client_id="dummy_id", reddit_client_secret="dummy_secret"))

    # Mock PRAW client
    mock_praw = MagicMock()
    mock_sub = MagicMock()

    mock_submission = MagicMock()
    mock_submission.id = "praw_t3_01"
    mock_submission.title = "PRAW Fetched Post: Kernel SIMD"
    mock_submission.selftext = "Body text from PRAW"
    mock_submission.author = "praw_user"
    mock_submission.score = 500
    mock_submission.num_comments = 80
    mock_submission.url = "https://reddit.com/r/linux/praw_t3_01"
    mock_submission.permalink = "/r/linux/praw_t3_01/"
    mock_submission.created_utc = 1727690000.0

    # Mock PRAW comments
    mock_comment = MagicMock()
    mock_comment.id = "praw_c_01"
    mock_comment.author = "praw_commenter"
    mock_comment.body = "Excellent SIMD results."
    mock_comment.score = 50
    mock_comment.created_utc = 1727691000.0
    mock_comment.parent_id = "praw_t3_01"
    mock_comment.permalink = "/r/linux/praw_t3_01/comment/01"

    mock_submission.comments = [mock_comment]
    mock_sub.hot.return_value = [mock_submission]
    mock_praw.subreddit.return_value = mock_sub
    mock_praw.submission.return_value = mock_submission

    with patch.object(scout, "_get_praw", return_value=mock_praw):
        posts = scout.fetch_subreddit_posts("linux", listing="hot", limit=1)
        assert len(posts) == 1
        assert posts[0].id == "praw_t3_01"
        assert posts[0].author == "praw_user"

        comments = scout.fetch_thread_comments("linux", "praw_t3_01", limit=1)
        assert len(comments) == 1
        assert comments[0].id == "praw_c_01"
        assert comments[0].author == "praw_commenter"


def test_scout_domain_topic_clustering_and_questions():
    """Verify that scout_domain correctly aggregates keywords and identifies community questions."""
    scout = RedditTrendScout(CommunityConfig(reddit_client_id=""))

    mock_threads = [
        RedditThread(
            id="t1",
            subreddit="rust",
            title="How to optimize io_uring ring buffer in Linux kernel?",
            selftext="Looking for benchmarks and zero-allocation techniques.",
            author="dev_a",
            score=100,
            num_comments=30,
            url="url1",
            permalink="/p1",
            created_utc=100.0,
        ),
        RedditThread(
            id="t2",
            subreddit="rust",
            title="SIMD memory safety zero-cost abstractions",
            selftext="Exploring AVX-512 in Rust.",
            author="dev_b",
            score=200,
            num_comments=50,
            url="url2",
            permalink="/p2",
            created_utc=200.0,
        ),
    ]

    with patch.object(scout, "fetch_subreddit_posts", return_value=mock_threads):
        reports = scout.scout_domain(ResearchDomain.RUST_LINUX, limit_per_sub=5)

    assert len(reports) > 0
    first_report = reports[0]
    assert isinstance(first_report, TrendReport)
    assert first_report.domain == ResearchDomain.RUST_LINUX

    # Verify keywords were extracted
    assert any(kw in ["rust", "linux", "kernel", "io_uring", "simd"] for kw in first_report.top_topics)

    # Verify question was extracted
    assert any("How to optimize" in q for q in first_report.emerging_questions)


def test_find_opportunities_matching():
    """Verify that find_opportunities scores relevance based on keyword hits and engagement."""
    scout = RedditTrendScout(CommunityConfig(reddit_client_id=""))

    mock_threads = [
        RedditThread(
            id="t_match",
            subreddit="MachineLearning",
            title="Discussion on parameter budget and quantization in local models",
            selftext="What techniques exist for energy minimization and strict parameter budget?",
            author="ai_dev",
            score=150,
            num_comments=40,
            url="url1",
            permalink="/p1",
            created_utc=100.0,
        ),
        RedditThread(
            id="t_unrelated",
            subreddit="MachineLearning",
            title="Which laptop should I buy for university?",
            selftext="Looking for recommendation under $1000.",
            author="student",
            score=10,
            num_comments=5,
            url="url2",
            permalink="/p2",
            created_utc=200.0,
        ),
    ]

    with patch.object(scout, "fetch_subreddit_posts", return_value=mock_threads):
        opportunities = scout.find_opportunities(
            domain=ResearchDomain.AI_OPTIMIZATION,
            paper_keywords=["quantization", "parameter budget", "energy minimization"],
        )

    assert len(opportunities) == 1
    assert opportunities[0].id == "t_match"
    assert opportunities[0].relevance_to_anse >= 0.5
    assert "quantization" in opportunities[0].matched_keywords
