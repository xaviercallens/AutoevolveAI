"""
ANSE Scientific Dissemination and Community Engine
Subproject for literature tracking, Reddit trend scouting, and grounded science advocacy.
"""

from anse.community.audience_reward import compute_audience_reward
from anse.community.cognitive_shield import CognitiveShield, CommentCategory, ShieldAssessment
from anse.community.config import (
    BANNED_BUZZWORDS,
    DOMAIN_KEYWORDS,
    DOMAIN_SUBREDDITS,
    CommunityConfig,
    ResearchDomain,
)
from anse.community.content_generator import ContentGenerator, RedditPostDraft
from anse.community.dpo_post_generator import (
    DPOPreferenceTriplet,
    export_dpo_dataset,
    generate_dpo_triplet_for_paper,
)
from anse.community.contextual_bandit import DisjointLinUCB, extract_context_features
from anse.community.hf_audience_models import ModernBERTSemanticScorer, OllamaQwenGenerator
from anse.community.orchestrator import CommunityOrchestrator
from anse.community.paper_ingest import PaperIngestionEngine, PaperItem
from anse.community.post_prescriptor import PostPrescriptor, PrescribedCandidate, PrescriptionReport
from anse.community.reddit_trend_scout import (
    RedditComment,
    RedditThread,
    RedditTrendScout,
    TrendReport,
)
from anse.community.rl_data_harvester import HarvestedPost, harvest_curated_seed_posts

__all__ = [
    "CommunityConfig",
    "ResearchDomain",
    "DOMAIN_SUBREDDITS",
    "DOMAIN_KEYWORDS",
    "BANNED_BUZZWORDS",
    "PaperItem",
    "PaperIngestionEngine",
    "RedditComment",
    "RedditThread",
    "TrendReport",
    "RedditTrendScout",
    "CommentCategory",
    "ShieldAssessment",
    "CognitiveShield",
    "RedditPostDraft",
    "ContentGenerator",
    "CommunityOrchestrator",
    "compute_audience_reward",
    "DPOPreferenceTriplet",
    "generate_dpo_triplet_for_paper",
    "export_dpo_dataset",
    "PostPrescriptor",
    "PrescribedCandidate",
    "PrescriptionReport",
    "HarvestedPost",
    "harvest_curated_seed_posts",
    "ModernBERTSemanticScorer",
    "OllamaQwenGenerator",
    "DisjointLinUCB",
    "extract_context_features",
]
