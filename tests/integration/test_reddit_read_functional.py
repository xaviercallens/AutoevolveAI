"""
Functional Tests for Reddit Read Model (Live End-to-End Networking)
Tests real HTTP socket communication (local test server) and live public endpoints.
Verifies complete HTTP pipeline, JSON parsing, error tolerance, and domain intelligence.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from anse.community.config import CommunityConfig, ResearchDomain
from anse.community.reddit_trend_scout import RedditComment, RedditThread, RedditTrendScout


class MockRedditHandler(BaseHTTPRequestHandler):
    """Local HTTP Server simulating Reddit's REST API for end-to-end functional testing."""

    def do_GET(self):
        # 1. Thread listing endpoint: /r/{sub}/{listing}.json
        if "/r/rust/hot.json" in self.path or "/r/MachineLearning/hot.json" in self.path:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            payload = {
                "kind": "Listing",
                "data": {
                    "children": [
                        {
                            "kind": "t3",
                            "data": {
                                "id": "t3_live_01",
                                "subreddit": "rust",
                                "title": "Zero-cost abstractions with SIMD in Linux kernels",
                                "selftext": "We achieved 10x throughput with AVX-512 without heap allocation.",
                                "author": "simd_master",
                                "score": 420,
                                "num_comments": 65,
                                "url": "https://github.com/example/simd",
                                "permalink": "/r/rust/comments/t3_live_01/zero_cost/",
                                "created_utc": 1727700000.0,
                            },
                        },
                        {
                            "kind": "t3",
                            "data": {
                                "id": "t3_live_02",
                                "subreddit": "rust",
                                "title": "How to debug memory ordering bugs in io_uring?",
                                "selftext": "Question about acquire-release semantics under heavy load.",
                                "author": "systems_hacker",
                                "score": 95,
                                "num_comments": 18,
                                "url": "https://reddit.com/r/rust/comments/t3_live_02/",
                                "permalink": "/r/rust/comments/t3_live_02/",
                                "created_utc": 1727705000.0,
                            },
                        },
                    ]
                },
            }
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return

        # 2. Thread comments endpoint: /r/{sub}/comments/{id}.json
        if "/comments/t3_live_01.json" in self.path:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            payload = [
                {"kind": "Listing", "data": {"children": []}},
                {
                    "kind": "Listing",
                    "data": {
                        "children": [
                            {
                                "kind": "t1",
                                "data": {
                                    "id": "c_live_101",
                                    "author": "phd_reviewer",
                                    "body": "What were the cache miss ratios and how does it scale to multi-threaded workloads?",
                                    "score": 34,
                                    "created_utc": 1727706000.0,
                                    "parent_id": "t3_live_01",
                                    "permalink": "/r/rust/comments/t3_live_01/comment/c_live_101/",
                                },
                            }
                        ]
                    },
                },
            ]
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return

        # Fallback 404
        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        # Suppress server logging during pytest
        return


@pytest.fixture(scope="module")
def local_reddit_server():
    """Spins up a local HTTP server on a random port for end-to-end socket testing."""
    server = HTTPServer(("127.0.0.1", 0), MockRedditHandler)
    host, port = server.server_address
    base_url = f"http://{host}:{port}"

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    yield base_url

    server.shutdown()
    server.server_close()


def test_e2e_socket_reddit_read_pipeline(local_reddit_server):
    """
    End-to-End Functional Test:
    Executes actual socket connections over TCP localhost using httpx.Client,
    verifying complete HTTP request/response parsing for posts and comments.
    """
    config = CommunityConfig(
        reddit_base_url=local_reddit_server,
        reddit_user_agent="ANSE-Functional-Test/1.0",
    )
    scout = RedditTrendScout(config)

    # 1. Fetch real posts over HTTP socket
    threads = scout.fetch_subreddit_posts("rust", listing="hot", limit=10)
    assert len(threads) == 2

    t1, t2 = threads[0], threads[1]
    assert t1.id == "t3_live_01"
    assert t1.subreddit == "rust"
    assert "Zero-cost abstractions" in t1.title
    assert t1.author == "simd_master"
    assert t1.score == 420
    assert t1.num_comments == 65
    assert t1.permalink.startswith("/r/rust/")

    assert t2.id == "t3_live_02"
    assert "memory ordering bugs" in t2.title

    # 2. Fetch comments over HTTP socket for thread t3_live_01
    comments = scout.fetch_thread_comments("rust", "t3_live_01", limit=10)
    assert len(comments) == 1
    c1 = comments[0]
    assert isinstance(c1, RedditComment)
    assert c1.id == "c_live_101"
    assert c1.author == "phd_reviewer"
    assert "cache miss ratios" in c1.body
    assert c1.score == 34
    assert c1.parent_id == "t3_live_01"

    # 3. Test scout_domain over HTTP socket
    reports = scout.scout_domain(ResearchDomain.RUST_LINUX, limit_per_sub=5)
    assert len(reports) > 0
    rep = reports[0]
    assert rep.domain == ResearchDomain.RUST_LINUX
    assert len(rep.top_topics) > 0
    assert any("simd" in kw or "linux" in kw or "io_uring" in kw for kw in rep.top_topics)
    assert any("How to debug" in q for q in rep.emerging_questions)


def test_live_public_internet_fallback():
    """
    Live Public Network Test:
    Attempts connection to live Reddit. If remote blocks data-center IP (403/429),
    asserts that the client handles it safely without crashing.
    """
    config = CommunityConfig(
        reddit_base_url="https://www.reddit.com",
        reddit_user_agent="ANSE-Scientific-Research-Agent/1.0 (academic validation test suite)",
    )
    scout = RedditTrendScout(config)

    # Attempt fetching from r/rust
    threads = scout.fetch_subreddit_posts("rust", listing="hot", limit=3)
    assert isinstance(threads, list)

    if threads:
        # If public network succeeded, verify integrity
        first = threads[0]
        assert isinstance(first, RedditThread)
        assert len(first.id) > 0
        assert len(first.title) > 0
    else:
        # If blocked by Reddit data-center CDN (403/429), assert graceful degradation
        assert threads == []
