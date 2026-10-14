"""
Reddit Trend Scout and Discussion Intelligence for ANSE Community Engine
Monitors target subreddits, extracts trends, detects community pain points,
and identifies active threads where ANSE research provides grounded solutions.
Inspired by ScrapeCreators/social-media-research-skills and donebyai-team/RedoraAI.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any

import httpx

logger = logging.getLogger(__name__)

from anse.community.config import (
    DOMAIN_KEYWORDS,
    DOMAIN_SUBREDDITS,
    CommunityConfig,
    ResearchDomain,
)


@dataclass
class RedditThread:
    id: str
    subreddit: str
    title: str
    selftext: str
    author: str
    score: int
    num_comments: int
    url: str
    permalink: str
    created_utc: float
    matched_keywords: list[str] = field(default_factory=list)
    relevance_to_anse: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "subreddit": self.subreddit,
            "title": self.title,
            "selftext": self.selftext[:200] + "..." if len(self.selftext) > 200 else self.selftext,
            "author": self.author,
            "score": self.score,
            "num_comments": self.num_comments,
            "url": self.url,
            "permalink": f"https://reddit.com{self.permalink}",
            "matched_keywords": self.matched_keywords,
            "relevance_to_anse": round(self.relevance_to_anse, 3),
        }


@dataclass
class RedditComment:
    id: str
    thread_id: str
    subreddit: str
    author: str
    body: str
    score: int
    created_utc: float
    parent_id: str = ""
    permalink: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "subreddit": self.subreddit,
            "author": self.author,
            "body": self.body[:200] + "..." if len(self.body) > 200 else self.body,
            "score": self.score,
            "created_utc": self.created_utc,
            "parent_id": self.parent_id,
            "permalink": f"https://reddit.com{self.permalink}" if self.permalink.startswith("/") else self.permalink,
        }


@dataclass
class TrendReport:
    domain: ResearchDomain
    subreddit: str
    top_topics: list[str]
    emerging_questions: list[str]
    high_engagement_threads: list[RedditThread]

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain.value,
            "subreddit": self.subreddit,
            "top_topics": self.top_topics,
            "emerging_questions": self.emerging_questions,
            "threads_count": len(self.high_engagement_threads),
            "threads": [t.to_dict() for t in self.high_engagement_threads[:5]],
        }


def _parse_praw_comments(praw_client, subreddit: str, thread_id: str, limit: int) -> list[RedditComment]:
    """Helper to parse comments from a PRAW submission."""
    try:
        submission = praw_client.submission(id=thread_id)
        if hasattr(submission.comments, "replace_more"):
            submission.comments.replace_more(limit=0)
        comments: list[RedditComment] = []
        for c in list(submission.comments)[:limit]:
            comments.append(
                RedditComment(
                    id=getattr(c, "id", ""),
                    thread_id=thread_id,
                    subreddit=subreddit,
                    author=str(getattr(c, "author", "[deleted]")),
                    body=getattr(c, "body", "") or "",
                    score=getattr(c, "score", 0),
                    created_utc=getattr(c, "created_utc", 0.0),
                    parent_id=getattr(c, "parent_id", ""),
                    permalink=getattr(c, "permalink", ""),
                )
            )
        return comments
    except Exception:
        return []


def _parse_json_comments(data: Any, subreddit: str, thread_id: str) -> list[RedditComment]:
    """Helper to parse comments from Reddit JSON listing."""
    if not isinstance(data, list) or len(data) <= 1:
        return []
    comments: list[RedditComment] = []
    children = data[1].get("data", {}).get("children", [])
    for child in children:
        if child.get("kind") == "t1":
            cd = child.get("data", {})
            comments.append(
                RedditComment(
                    id=cd.get("id", ""),
                    thread_id=thread_id,
                    subreddit=subreddit,
                    author=cd.get("author", "[deleted]"),
                    body=cd.get("body", ""),
                    score=cd.get("score", 0),
                    created_utc=cd.get("created_utc", 0.0),
                    parent_id=cd.get("parent_id", ""),
                    permalink=cd.get("permalink", ""),
                )
            )
    return comments


def _analyze_threads_for_trends(
    threads: list[RedditThread], keywords: list[str]
) -> tuple[list[str], list[str], list[RedditThread]]:
    """Analyzes threads, scores matches, clusters topics, and extracts inquiry questions."""
    topic_counts: dict[str, int] = {}
    questions: list[str] = []

    for t in threads:
        text = f"{t.title} {t.selftext}".lower()
        matches = [kw for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", text)]
        t.matched_keywords = matches
        t.relevance_to_anse = min(1.0, len(matches) * 0.25)

        for kw in matches:
            topic_counts[kw] = topic_counts.get(kw, 0) + 1

        if "?" in t.title or any(w in t.title.lower() for w in ["how to", "why does", "what is", "benchmark", "comparison"]):
            questions.append(t.title)

    sorted_topics = [k for k, _ in sorted(topic_counts.items(), key=lambda item: item[1], reverse=True)]
    high_eng = sorted(threads, key=lambda x: (x.score + x.num_comments * 2), reverse=True)
    return sorted_topics, questions, high_eng


class RedditTrendScout:
    def __init__(
        self,
        config: CommunityConfig | None = None,
        use_hf_semantic: bool = False,
    ) -> None:
        self.config = config or CommunityConfig()
        self._praw_instance = None
        self._action_history: list[dict[str, Any]] = []
        self._semantic_scorer = None
        if use_hf_semantic:
            self._init_semantic_scorer()

    def _init_semantic_scorer(self) -> None:
        try:
            from anse.community.hf_audience_models import ModernBERTSemanticScorer
            self._semantic_scorer = ModernBERTSemanticScorer()
        except Exception as exc:
            logger.debug("Failed to init ModernBERTSemanticScorer in scout: %s", exc)

    def _get_praw(self):
        """Lazy initialization of PRAW client if credentials exist."""
        if self._praw_instance is None and self.config.reddit_client_id:
            try:
                import praw
                self._praw_instance = praw.Reddit(
                    client_id=self.config.reddit_client_id,
                    client_secret=self.config.reddit_client_secret,
                    user_agent=self.config.reddit_user_agent,
                    username=self.config.reddit_username or None,
                    password=self.config.reddit_password or None,
                )
            except Exception:
                self._praw_instance = None
        return self._praw_instance

    def fetch_subreddit_posts(
        self, subreddit: str, listing: str = "hot", limit: int = 15
    ) -> list[RedditThread]:
        """
        Fetch threads from subreddit via PRAW or public JSON API fallback.
        """
        praw_client = self._get_praw()
        threads: list[RedditThread] = []

        if praw_client is not None:
            try:
                sub = praw_client.subreddit(subreddit)
                posts = getattr(sub, listing)(limit=limit)
                for p in posts:
                    threads.append(
                        RedditThread(
                            id=p.id,
                            subreddit=subreddit,
                            title=p.title,
                            selftext=p.selftext or "",
                            author=str(p.author),
                            score=p.score,
                            num_comments=p.num_comments,
                            url=p.url,
                            permalink=p.permalink,
                            created_utc=p.created_utc,
                        )
                    )
                return threads
            except Exception as exc:
                logger.debug("PRAW thread fetch failed, falling back to public JSON: %s", exc)

        # Unauthenticated JSON API fallback
        url = f"{self.config.reddit_base_url}/r/{subreddit}/{listing}.json?limit={limit}"
        headers = {"User-Agent": self.config.reddit_user_agent}

        try:
            with httpx.Client(timeout=10.0, headers=headers) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    children = data.get("data", {}).get("children", [])
                    for child in children:
                        d = child.get("data", {})
                        threads.append(
                            RedditThread(
                                id=d.get("id", ""),
                                subreddit=subreddit,
                                title=d.get("title", ""),
                                selftext=d.get("selftext", ""),
                                author=d.get("author", "[deleted]"),
                                score=d.get("score", 0),
                                num_comments=d.get("num_comments", 0),
                                url=d.get("url", ""),
                                permalink=d.get("permalink", ""),
                                created_utc=d.get("created_utc", 0.0),
                            )
                        )
        except Exception as exc:
            logger.debug("Public JSON API thread fetch failed: %s", exc)

        return threads

    def fetch_thread_comments(
        self, subreddit: str, thread_id: str, limit: int = 25
    ) -> list[RedditComment]:
        """
        Fetch top comments for a specific thread via PRAW or public JSON fallback.
        """
        praw_client = self._get_praw()
        if praw_client is not None:
            comments = _parse_praw_comments(praw_client, subreddit, thread_id, limit)
            if comments:
                return comments

        # Unauthenticated JSON API fallback
        url = f"{self.config.reddit_base_url}/r/{subreddit}/comments/{thread_id}.json?limit={limit}"
        headers = {"User-Agent": self.config.reddit_user_agent}

        try:
            with httpx.Client(timeout=10.0, headers=headers) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    return _parse_json_comments(resp.json(), subreddit, thread_id)
        except Exception as exc:
            logger.debug("Public JSON API comments fetch failed: %s", exc)

        return []

    def scout_domain(self, domain: ResearchDomain, limit_per_sub: int = 10) -> list[TrendReport]:
        """
        Scout all primary subreddits for a given domain and assemble trend intelligence.
        """
        subreddits = DOMAIN_SUBREDDITS.get(domain, [])
        keywords = DOMAIN_KEYWORDS.get(domain, [])
        reports: list[TrendReport] = []

        for sub in subreddits:
            threads = self.fetch_subreddit_posts(sub, listing="hot", limit=limit_per_sub)
            if not threads:
                continue

            top_topics, questions, high_eng = _analyze_threads_for_trends(threads, keywords)

            report = TrendReport(
                domain=domain,
                subreddit=sub,
                top_topics=top_topics[:5],
                emerging_questions=questions[:5],
                high_engagement_threads=high_eng,
            )
            reports.append(report)

        return reports

    def find_opportunities(
        self,
        domain: ResearchDomain,
        paper_keywords: list[str],
        paper_text: str = "",
    ) -> list[RedditThread]:
        """
        Finds active Reddit threads where presenting our paper results directly
        addresses the community's questions or bottlenecks.
        Optionally scores semantic similarity using ModernBERT.
        """
        subreddits = DOMAIN_SUBREDDITS.get(domain, [])
        candidate_threads: list[RedditThread] = []
        seen_ids: set[str] = set()

        for sub in subreddits:
            threads = self.fetch_subreddit_posts(sub, listing="hot", limit=15)
            for t in threads:
                if t.id in seen_ids:
                    continue
                text = f"{t.title} {t.selftext}".lower()
                hits = [kw for kw in paper_keywords if re.search(r"\b" + re.escape(kw) + r"\b", text)]
                if hits:
                    seen_ids.add(t.id)
                    t.matched_keywords = hits
                    base_rel = min(1.0, 0.3 * len(hits) + 0.1 * min(10, t.num_comments))
                    if self._semantic_scorer is not None and getattr(self._semantic_scorer, "is_available", False) and paper_text:
                        sem_sim = self._semantic_scorer.compute_similarity(paper_text, f"{t.title} {t.selftext}")
                        t.relevance_to_anse = 0.5 * base_rel + 0.5 * sem_sim
                    else:
                        t.relevance_to_anse = base_rel
                    candidate_threads.append(t)

        return sorted(candidate_threads, key=lambda x: x.relevance_to_anse, reverse=True)

    def record_action(self, action_type: str, details: dict[str, Any]) -> None:
        """Tracks actions to enforce the 9:1 community non-promotional ratio."""
        self._action_history.append({"type": action_type, "details": details})

    def get_promotional_ratio(self) -> float:
        """Returns the ratio of promotional posts to total community interactions."""
        if not self._action_history:
            return 0.0
        promotional = sum(1 for a in self._action_history if a.get("type") == "paper_promotion")
        return promotional / len(self._action_history)
