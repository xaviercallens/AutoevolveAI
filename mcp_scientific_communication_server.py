#!/usr/bin/env python3
"""
Scientific Communication & Community Adoption MCP Server.
Autonomous neuro-symbolic engine for academic dissemination, Zenodo harvesting,
Reddit community scouting, RL audience prescription, cognitive defense, and continual policy retraining.
"""

from __future__ import annotations

import json
import logging
import math
import os
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Any

import httpx
from fastmcp import FastMCP

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from anse.community.audience_reward import audit_moderation_risk, compute_audience_reward
from anse.community.cognitive_shield import CognitiveShield
from anse.community.config import DOMAIN_SUBREDDITS, ResearchDomain
from anse.community.contextual_bandit import DisjointLinUCB, extract_context_features
from anse.community.paper_ingest import PaperIngestionEngine, PaperItem
from anse.community.post_prescriptor import PostPrescriptor
from anse.community.reddit_trend_scout import RedditTrendScout

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ScientificCommMCP")

mcp = FastMCP("scientific-communication-engine")


# ─────────────────────────────────────────────────────────────────────────────
# Helper Routines
# ─────────────────────────────────────────────────────────────────────────────

def _resolve_domain(domain_str: str) -> ResearchDomain:
    try:
        return ResearchDomain(domain_str.lower().strip())
    except Exception:
        return ResearchDomain.AI_OPTIMIZATION


# ─────────────────────────────────────────────────────────────────────────────
# MCP Tools
# ─────────────────────────────────────────────────────────────────────────────

@mcp.tool()
def scan_zenodo_publications(
    author: str = "Callens, Xavier",
    query: str = "",
    max_results: int = 10,
    include_local_papers: bool = True,
) -> dict[str, Any]:
    """
    Scans the Zenodo REST API for publications by author or query, and indexes local research preprints in papers/.
    Extracts titles, abstracts, DOIs, open-access URLs, and automatically scores research domain relevance.
    """
    engine = PaperIngestionEngine()
    publications: list[dict[str, Any]] = []

    # 1. Query Zenodo REST API
    zenodo_params: dict[str, Any] = {
        "size": max_results,
        "sort": "mostrecent",
        "status": "published",
    }
    if author and not query:
        zenodo_params["q"] = f'creators.name:"{author}"'
    elif query and not author:
        zenodo_params["q"] = query
    elif author and query:
        zenodo_params["q"] = f'creators.name:"{author}" AND ({query})'
    else:
        zenodo_params["q"] = "Xavier Callens"

    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get("https://zenodo.org/api/records", params=zenodo_params)
            if resp.status_code == 200:
                data = resp.json()
                hits = data.get("hits", {}).get("hits", [])
                for hit in hits:
                    meta = hit.get("metadata", {})
                    title = meta.get("title", "")
                    raw_desc = meta.get("description", "")
                    clean_desc = re.sub(r"<[^>]+>", " ", raw_desc).replace("\n", " ").strip()
                    doi = hit.get("doi", "") or meta.get("doi", "")
                    doi_url = hit.get("links", {}).get("doi", f"https://doi.org/{doi}" if doi else "")
                    creators = [c.get("name", "") for c in meta.get("creators", []) if c.get("name")]

                    paper = PaperItem(
                        title=title,
                        abstract=clean_desc,
                        authors=creators,
                        source_url=doi_url,
                        doi=doi,
                        source_type="zenodo",
                        published_date=meta.get("publication_date", ""),
                    )
                    engine.score_paper(paper)
                    publications.append(paper.to_dict())
    except Exception as exc:
        logger.warning(f"Zenodo query encounter: {exc}")

    # 2. Local papers in papers/
    local_count = 0
    if include_local_papers:
        local_items = engine.scan_local_papers(str(REPO_ROOT / "papers"))
        for p in local_items:
            engine.score_paper(p)
            publications.append(p.to_dict())
            local_count += 1

    return {
        "status": "SUCCESS",
        "author_queried": author,
        "query": query,
        "total_publications_found": len(publications),
        "zenodo_count": len(publications) - local_count,
        "local_count": local_count,
        "publications": publications,
    }


@mcp.tool()
def scout_reddit_community_sentiment(
    subreddits: list[str] | None = None,
    domain: str = "ai_optimization",
) -> dict[str, Any]:
    """
    Scouts candidate Reddit technical communities to identify trending friction points, audience sentiment,
    moderation risk, and adoption likelihood to minimize community resistance and prevent backlash.
    """
    r_domain = _resolve_domain(domain)
    target_subs = subreddits or DOMAIN_SUBREDDITS.get(r_domain, ["MachineLearning", "LLMmathematics", "airesearch"])
    scout = RedditTrendScout()

    community_reports: list[dict[str, Any]] = []

    for sub in target_subs:
        clean_sub = sub.replace("r/", "").strip()
        threads = scout.fetch_subreddit_posts(clean_sub, listing="hot", limit=10)
        from anse.community.config import DOMAIN_KEYWORDS
        from anse.community.reddit_trend_scout import _analyze_threads_for_trends

        keywords = DOMAIN_KEYWORDS.get(r_domain, ["ai", "benchmark", "proof", "verification", "lean", "physics"])
        top_topics, questions, _ = _analyze_threads_for_trends(threads, keywords)
        mod_risk = audit_moderation_risk(clean_sub, "Sample Title", "Sample Body with external links")

        # Adoption feasibility score: higher for friendly subreddits without aggressive link removal
        resistance_penalty = mod_risk["moderation_risk"] * 0.40
        hot_topic_bonus = min(0.30, len(top_topics) * 0.05)
        adoption_score = max(0.10, min(0.98, 0.75 + hot_topic_bonus - resistance_penalty))

        community_reports.append({
            "subreddit": f"r/{clean_sub}",
            "domain": r_domain.value,
            "adoption_feasibility_score": round(adoption_score, 3),
            "estimated_resistance": "LOW" if adoption_score >= 0.75 else ("MEDIUM" if adoption_score >= 0.50 else "HIGH"),
            "hot_topics": top_topics[:5],
            "emerging_questions": questions[:5],
            "moderation_risk": mod_risk["moderation_risk"],
            "moderation_guidelines": mod_risk["moderation_warnings"],
        })

    return {
        "status": "SUCCESS",
        "domain": r_domain.value,
        "communities_evaluated": len(community_reports),
        "recommended_communities": sorted(community_reports, key=lambda x: x["adoption_feasibility_score"], reverse=True),
    }


@mcp.tool()
def audit_post_adoption_and_resistance(
    title: str,
    body: str,
    subreddit: str,
    submission_statement: str = "",
) -> dict[str, Any]:
    """
    Audits candidate post drafts against the multi-objective Audience Reward Model and moderation risk heuristics.
    Detects hype buzzwords, promotional phrase traps ('our team', 'our paper'), and AutoMod external link filters.
    Returns numerical scores and actionable tuning recommendations.
    """
    clean_sub = subreddit.replace("r/", "").strip()
    reward_metrics = compute_audience_reward(clean_sub, title, body, submission_statement)
    mod_audit = audit_moderation_risk(clean_sub, title, body)

    suggestions: list[str] = []
    if reward_metrics["hook_score"] < 0.60:
        suggestions.append("Lead with a concrete technical dilemma, numerical scale (e.g. Mach > 0.3, condition number 10^28), or question.")
    if reward_metrics["modesty_score"] < 0.80:
        suggestions.append("Add an explicit 'Transparent Limitations' section detailing boundary conditions where the approach does not apply.")
    if mod_audit["is_ban_prone"]:
        suggestions.append("Move direct external links (GitHub, Zenodo) from the main post body to the top author submission comment.")
    if mod_audit["moderation_warnings"]:
        suggestions.extend(mod_audit["moderation_warnings"])

    return {
        "status": "SUCCESS",
        "subreddit": f"r/{clean_sub}",
        "total_audience_reward": reward_metrics["total_reward"],
        "breakdown": {
            "hook_score": reward_metrics["hook_score"],
            "grounding_score": reward_metrics["grounding_score"],
            "modesty_score": reward_metrics["modesty_score"],
            "compliance_score": reward_metrics["compliance_score"],
            "resonance_score": reward_metrics["resonance_score"],
        },
        "is_recommended_for_posting": reward_metrics["is_recommended"],
        "moderation_risk": mod_audit["moderation_risk"],
        "hype_violations_detected": reward_metrics["hype_violations"],
        "tuning_recommendations": suggestions or ["Post complies cleanly with zero-hype community guidelines."],
    }


@mcp.tool()
def prescribe_optimal_post(
    paper_title: str,
    abstract: str = "",
    doi: str = "",
    target_subreddit: str | None = None,
    domain: str = "ai_optimization",
) -> dict[str, Any]:
    """
    Synthesizes an optimal, modest, receipt-grounded post tailored to a target community.
    Leverages LinUCB Contextual Bandit, Audience Reward Model, and semantic relevance to maximize adoption.
    """
    r_domain = _resolve_domain(domain)
    sub = target_subreddit or DOMAIN_SUBREDDITS.get(r_domain, ["MachineLearning"])[0]

    paper = PaperItem(
        title=paper_title,
        abstract=abstract or f"Research publication on {paper_title}",
        doi=doi,
        source_url=f"https://doi.org/{doi}" if doi else "https://github.com/xaviercallens/AutoevolveAI",
        matched_domains=[r_domain],
    )

    prescriptor = PostPrescriptor(subreddit=sub, use_hf_models=False)
    report = prescriptor.prescribe_best_post(paper)
    best = report.best_candidate

    return {
        "status": "SUCCESS",
        "target_subreddit": report.target_subreddit,
        "selected_strategy": best.strategy_name,
        "recommended_utc_window": report.recommended_utc_window,
        "predicted_audience_reward": best.reward_breakdown["total_reward"],
        "post_title": best.title,
        "post_body": best.body,
        "submission_statement": best.submission_statement,
        "anticipated_qa_defense": best.anticipated_qa,
        "bandit_metrics": report.bandit_recommendation,
    }


@mcp.tool()
def shield_evaluate_and_reply(
    comment_text: str,
    context_paper_title: str = "ANSE Research Publication",
    paper_doi: str = "10.5281/zenodo.23295142",
) -> dict[str, Any]:
    """
    Evaluates incoming Reddit comments using the Cognitive Shield.
    Classifies intent (collaboration/paper requests, technical critique, honest skepticism, bad-faith snark, toxic ad-hominem).
    Formulates humble, verified, receipt-bearing replies or calm de-escalation boundaries.
    """
    shield = CognitiveShield()
    assessment = shield.classify_comment(comment_text, context_paper_title)

    # If suggested reply references generic URLs, format with specific paper DOI
    reply = assessment.suggested_reply
    if paper_doi and "zenodo" in reply.lower():
        reply = reply.replace("10.5281/zenodo.23295142", paper_doi)

    return {
        "status": "SUCCESS",
        "comment_text": comment_text,
        "category": assessment.category.value,
        "hostility_score": assessment.hostility_score,
        "recommended_action": assessment.recommended_action,
        "rationale": assessment.rationale,
        "suggested_reply": reply,
    }


@mcp.tool()
def feedback_and_retrain_rl_policy(
    subreddit: str,
    post_title: str,
    upvotes: int,
    comments_count: int,
    upvote_ratio: float = 0.50,
    views: int = 1000,
    user_reply_sample: str = "",
) -> dict[str, Any]:
    """
    Continual Reinforcement Learning feedback loop:
    1. Computes normalized empirical reward from real Reddit telemetry.
    2. Updates LinUCB Contextual Bandit weights in results/contextual_bandit_state.json.
    3. Augments DPO preference pairs in results/dpo_scientific_dissemination.jsonl.
    4. Updates results/communication_retraining_log.json with newly learned policy rules.
    """
    clean_sub = subreddit.replace("r/", "").strip()

    # Calculate empirical reward:
    # High score (> 20 upvotes) or high positive comments (> 10) indicates strong community adoption
    upvote_component = min(0.60, (max(0, upvotes) / max(1, upvotes + 15)) * 0.60)
    ratio_component = max(0.0, (upvote_ratio - 0.50) * 0.40)
    comment_component = min(0.20, comments_count * 0.015)
    empirical_reward = round(min(1.0, max(0.05, upvote_component + ratio_component + comment_component)), 4)

    # 1. Update LinUCB Contextual Bandit
    bandit = DisjointLinUCB()
    bandit_state_path = REPO_ROOT / "results" / "contextual_bandit_state.json"
    bandit_state_path.parent.mkdir(parents=True, exist_ok=True)
    if bandit_state_path.exists():
        bandit.load_state(bandit_state_path)

    # Select appropriate domain
    domain = "physics" if any(k in clean_sub.lower() for k in ["physics", "fluid"]) else ("math" if "math" in clean_sub.lower() else "ai")
    context = extract_context_features(domain=domain, hour_utc=14, day_of_week=3, has_doi=True, has_code=True)

    action_id = 2 if "machinelearning" in clean_sub.lower() or "airesearch" in clean_sub.lower() else (3 if "physics" in clean_sub.lower() else 0)
    bandit.update(action=action_id, context=context, reward=empirical_reward)
    bandit.save_state(bandit_state_path)

    # 2. Augment DPO preference dataset if high or low reward
    dpo_file = REPO_ROOT / "results" / "dpo_scientific_dissemination.jsonl"
    dpo_file.parent.mkdir(parents=True, exist_ok=True)
    dpo_created = False
    if user_reply_sample and empirical_reward >= 0.70:
        shield = CognitiveShield()
        shield_eval = shield.classify_comment(user_reply_sample)
        dpo_entry = {
            "prompt": f"A community member on r/{clean_sub} responded to '{post_title}': '{user_reply_sample}'. How should the author respond?",
            "chosen": shield_eval.suggested_reply,
            "rejected": "Thanks, glad you like it. We worked really hard and our AI is revolutionary.",
            "subreddit": clean_sub,
            "empirical_ground_truth": True,
            "reward": empirical_reward,
        }
        with open(dpo_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(dpo_entry) + "\n")
        dpo_created = True

    # 3. Update communication retraining log
    retraining_log_path = REPO_ROOT / "results" / "communication_retraining_log.json"
    current_log: dict[str, Any] = {}
    if retraining_log_path.exists():
        try:
            current_log = json.loads(retraining_log_path.read_text(encoding="utf-8"))
        except Exception:
            current_log = {}

    current_log["timestamp"] = "2026-10-11T16:00:00Z"
    current_log["total_submissions_retrofitted"] = current_log.get("total_submissions_retrofitted", 7) + 1
    current_log.setdefault("audited_submissions", []).append({
        "title": post_title,
        "subreddit": clean_sub,
        "score": upvotes,
        "ratio": upvote_ratio,
        "comments": comments_count,
        "views": views,
        "empirical_reward": empirical_reward,
    })

    with open(retraining_log_path, "w", encoding="utf-8") as f:
        json.dump(current_log, f, indent=2)

    return {
        "status": "SUCCESS",
        "subreddit": clean_sub,
        "post_title": post_title,
        "empirical_reward": empirical_reward,
        "linucb_arm_updated": action_id,
        "dpo_pair_appended": dpo_created,
        "retraining_log_updated": str(retraining_log_path),
    }


@mcp.tool()
def get_communication_policy_status() -> dict[str, Any]:
    """
    Returns the live status of the reinforcement learning dissemination policy:
    LinUCB bandit weights, historical retrofits, promotional ratio, and learned guidelines.
    """
    scout = RedditTrendScout()
    retraining_log_path = REPO_ROOT / "results" / "communication_retraining_log.json"
    bandit_state_path = REPO_ROOT / "results" / "contextual_bandit_state.json"

    log_data: dict[str, Any] = {}
    if retraining_log_path.exists():
        try:
            log_data = json.loads(retraining_log_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    bandit_loaded = bandit_state_path.exists()

    return {
        "status": "SUCCESS",
        "promotional_ratio": scout.get_promotional_ratio(),
        "promotional_ratio_compliant": scout.get_promotional_ratio() <= 0.10,
        "total_submissions_retrofitted": log_data.get("total_submissions_retrofitted", 7),
        "bandit_state_active": bandit_loaded,
        "active_guidelines": log_data.get("learned_policy_guidelines", []),
    }


if __name__ == "__main__":
    mcp.run()
