"""
Community Orchestrator for ANSE
Coordinates Paper Ingestion, Reddit Scouting, Content Generation, and Cognitive Shield Defense.
Supports native Agno (agno-agi/agno) multi-tool agent binding with fallback to standalone Python execution.
"""

from typing import Any

from anse.community.cognitive_shield import CognitiveShield, ShieldAssessment
from anse.community.config import CommunityConfig, ResearchDomain
from anse.community.content_generator import ContentGenerator, RedditPostDraft
from anse.community.paper_ingest import PaperIngestionEngine, PaperItem
from anse.community.reddit_trend_scout import RedditTrendScout


class CommunityOrchestrator:
    def __init__(self, config: CommunityConfig | None = None) -> None:
        self.config = config or CommunityConfig()
        self.ingest_engine = PaperIngestionEngine(self.config)
        self.trend_scout = RedditTrendScout(self.config)
        self.content_gen = ContentGenerator(self.config)
        self.shield = CognitiveShield()
        self._agno_agent = None

    def initialize_agno_agent(self):
        """
        Initializes an Agno agent with native ArxivTools and RedditTools if agno is installed.
        """
        try:
            from agno.agent import Agent
            from agno.tools.arxiv import ArxivTools

            tools = [ArxivTools()]
            # If PRAW credentials exist, attach RedditTools if available
            try:
                from agno.tools.reddit import RedditTools
                if self.config.reddit_client_id:
                    tools.append(RedditTools())
            except ImportError as exc:
                logger.debug("agno.tools.reddit not available: %s", exc)

            self._agno_agent = Agent(
                name="ANSE-Community-Advocate",
                description="Autonomous Neuro-Symbolic Scientific Dissemination and Community Engine.",
                tools=tools,
                instructions=[
                    "Analyze frontier papers across Rust, Linux, AI optimization, Astrophysics, Quantum, and HPC.",
                    "Formulate strictly grounded, non-sensational summaries adhering to subreddit rules.",
                    "Enforce the 9:1 non-promotional community rule on Reddit.",
                    "Protect academic integrity by de-escalating cynicism and answering technical inquiries with empirical receipts."
                ],
                markdown=True,
            )
            return True
        except ImportError:
            self._agno_agent = None
            return False

    def run_discovery_cycle(self, domain: ResearchDomain) -> dict[str, Any]:
        """
        Executes a full discovery cycle:
        1. Ingests cutting-edge papers on arXiv & Zenodo
        2. Scans local user preprints in papers/
        3. Scouts Reddit trends in corresponding subreddits
        4. Identifies synergy opportunities between community questions and our research
        """
        domain_name = domain.value.replace("_", " ")

        # 1. External literature search
        arxiv_papers = self.ingest_engine.search_arxiv(domain_name, max_results=3)
        zenodo_papers = self.ingest_engine.search_zenodo(domain_name, max_results=3)

        # 2. Local author papers scan
        local_papers = self.ingest_engine.scan_local_papers()
        domain_local_papers = [
            p for p in local_papers if domain in p.matched_domains or not p.matched_domains
        ]

        # 3. Reddit trend scouting
        trend_reports = self.trend_scout.scout_domain(domain, limit_per_sub=5)

        # 4. Opportunity identification
        keywords = [domain_name] + [kw for rep in trend_reports for kw in rep.top_topics]
        actionable_threads = self.trend_scout.find_opportunities(domain, keywords)

        return {
            "domain": domain.value,
            "external_literature": {
                "arxiv_count": len(arxiv_papers),
                "zenodo_count": len(zenodo_papers),
                "sample": [p.to_dict() for p in (arxiv_papers + zenodo_papers)[:4]],
            },
            "author_papers": {
                "total_local": len(local_papers),
                "domain_relevant": len(domain_local_papers),
                "sample": [p.to_dict() for p in domain_local_papers[:3]],
            },
            "reddit_intelligence": {
                "trends": [tr.to_dict() for tr in trend_reports],
                "actionable_opportunities": [t.to_dict() for t in actionable_threads[:4]],
            },
        }

    def prepare_post(
        self,
        paper: PaperItem,
        target_subreddit: str,
        domain: ResearchDomain,
    ) -> RedditPostDraft:
        """
        Synthesizes a vetted post draft ready for Human-in-the-Loop review.
        """
        draft = self.content_gen.draft_post_for_paper(paper, target_subreddit, domain)

        # Enforce promotional ratio check
        current_ratio = self.trend_scout.get_promotional_ratio()
        if current_ratio > self.config.max_promotional_ratio:
            # Add warning to draft
            draft.submission_statement = (
                f"> [!WARNING] Promotional ratio is currently {current_ratio:.1%} (> 10%). "
                "Engage in more community discussions before posting another promotional thread.\n\n"
                + draft.submission_statement
            )

        return draft

    def evaluate_comment_and_respond(
        self, comment_text: str, context_paper_title: str = ""
    ) -> ShieldAssessment:
        """
        Runs incoming Reddit feedback through the Cognitive Shield.
        """
        assessment = self.shield.classify_comment(comment_text, context_paper_title)
        self.trend_scout.record_action("comment_response", {"category": assessment.category.value})
        return assessment
