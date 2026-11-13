#!/usr/bin/env python3
"""
Audience Reward Model for Scientific & Open-Source Research Dissemination.
Computes deterministic multi-objective reward scores for candidate posts across:
- Hook & Problem Formulation
- Scientific Grounding & Reproducibility
- Intellectual Modesty & Anti-Hype Constraints
- Community Policy & Submission Statement Compliance
- Technical Readability & Resonance
"""

from __future__ import annotations

import re
from typing import Any

from anse.community.config import BANNED_BUZZWORDS

# Strategic weights for reward components
WEIGHT_HOOK = 0.25
WEIGHT_GROUNDING = 0.25
WEIGHT_MODESTY = 0.20
WEIGHT_COMPLIANCE = 0.20
WEIGHT_RESONANCE = 0.10


def _score_hook(title: str, body: str) -> float:
    """
    Evaluates opening problem formulation and teaser strength.
    Rewards posts that identify concrete technical friction points or shared engineering challenges.
    """
    score = 0.0
    combined = (title + " " + body[:400]).lower()

    # Question or dilemma in title/first paragraph
    if "?" in title or any(q in combined for q in ("why do", "how to", "can we", "the problem with")):
        score += 0.4

    # Technical friction keywords
    friction_keywords = (
        "drift",
        "bottleneck",
        "instability",
        "memory blowup",
        "penalty",
        "hallucinat",
        "overhead",
        "limitation",
        "divergence",
        "tradeoff",
    )
    if any(k in combined for k in friction_keywords):
        score += 0.4

    # Direct teaser without clickbait
    if len(title.split()) >= 6 and len(title.split()) <= 20:
        score += 0.2

    return min(1.0, score)


def _score_grounding(body: str, submission_statement: str, is_comment: bool = False) -> float:
    """
    Rewards rigorous grounding: preprints (Zenodo/ArXiv), DOI links, code repositories,
    and mathematical or empirical telemetry.
    """
    score = 0.0
    combined = body + " " + submission_statement
    combined_l = combined.lower()

    # Preprint / DOI references or links
    if any(k in combined_l for k in ("doi.org", "zenodo", "arxiv", "doi:", "preprint", "paper")):
        score += 0.35

    # Code reproducibility links or open-source references
    if any(k in combined_l for k in ("github", "gitlab", "huggingface", "open-source", "open source", "repository")):
        score += 0.35

    # Empirical or mathematical verification mentions
    verification_terms = (
        "lean 4",
        "proof",
        "formal verification",
        "benchmark",
        "fp64",
        "fp32",
        "test suite",
        "reproducib",
        "theorem",
        "#print axioms",
        "cvode",
        "poisson summation",
        "mach",
        "shear heating",
        "acoustic",
        "jacobian",
        "statement adequacy",
        "exciton",
        "bilayer",
        "monotone",
        "triangular lattice",
        "stiff ode",
        "symplectic",
        "newton-krylov",
    )
    matches = sum(1 for term in verification_terms if term in combined_l)
    if matches >= 1:
        score += 0.30
    if matches >= 3:
        score += 0.15

    # For comments adhering to zero-link karma repair, allow deep mathematical & physical rigor
    # to achieve top grounding without forcing external links
    if is_comment and matches >= 2 and score < 0.90:
        score = min(1.0, score + 0.40)

    return min(1.0, score)


def _score_modesty(title: str, body: str) -> tuple[float, list[str]]:
    """
    Strict anti-hype audit. Penalizes sensationalist buzzwords heavily.
    Rewards explicit, transparent acknowledgment of boundary limitations.
    """
    violations: list[str] = []
    text = (title + " " + body).lower()

    for word in BANNED_BUZZWORDS:
        pattern = r"\b" + re.escape(word.lower()) + r"\b"
        if re.search(pattern, text):
            violations.append(word)

    if violations:
        # Severe penalty for each buzzword
        penalty = min(1.0, len(violations) * 0.4)
        return max(0.0, 1.0 - penalty), violations

    score = 0.7  # Clean baseline
    # Bonus for transparent limitation section
    limitation_markers = (
        "limitation",
        "boundary",
        "where this breaks",
        "does not apply",
        "trade-off",
        "periodic domain",
        "future work",
    )
    if any(m in text for m in limitation_markers):
        score += 0.3

    return min(1.0, score), []



STRICT_LINK_MODERATION_SUBREDDITS = {
    "openai",
    "technology",
    "singularity",
    "science",
    "artificial",
}

STRICT_COMMENT_LINK_SUBREDDITS = {
    "math",
    "physics",
    "claudeai",
    "machinelearning",
    "singularity",
    "askphysics",
    "localllama",
}

SELF_PROMO_TRIGGERS = (
    "our team",
    "our team open-sourced",
    "we wrote",
    "our paper",
    "our audit",
    "our scripts",
    "our repository",
    "we open-sourced",
    "check out our",
    "socrate ai lab",
    "our group",
    "our ai agent swarm",
    "ai agent swarm",
    "i am more an ai person",
    "our framework solves",
)


def audit_moderation_risk(
    subreddit: str,
    title: str,
    body: str,
    is_comment: bool = False,
    karma_repair_mode: bool = False,
) -> dict[str, Any]:
    """
    Evaluates risk of automated removal by Reddit AutoMod and subreddit moderation rules.
    Detects:
    - Rule 3 (Self-Promotion): External links (github, zenodo, doi) in OP body on strict subreddits.
    - Karma Repair Violations: External links in comments when in karma repair mode (karma < +25).
    - Unprompted Link Dumps: External links in comments on academic/technical subreddits.
    - Promotional language heuristics ('our team', 'we open-sourced', 'socrate ai lab', etc.).
    - Title rule violations (excessive length, shoutouts).
    """
    sub_clean = subreddit.lower().replace("r/", "").strip()
    warnings = []
    risk_score = 0.0

    has_raw_links = bool(re.search(r"https?://|doi\.org|github\.com|zenodo\.", body))
    is_strict_post = sub_clean in STRICT_LINK_MODERATION_SUBREDDITS
    is_strict_comment = sub_clean in STRICT_COMMENT_LINK_SUBREDDITS

    if not is_comment and is_strict_post and has_raw_links:
        risk_score += 0.50
        warnings.append(
            f"Rule 3 (Self-Promotion) Risk: External URLs in post body trigger AutoMod on r/{sub_clean}. "
            "Move repository and DOI links to a pinned/top submission comment."
        )

    if is_comment:
        if karma_repair_mode and has_raw_links:
            risk_score += 0.80
            warnings.append(
                "Karma Repair Violation: Active karma repair mode strictly enforces the Zero-Link Rule. "
                "Do not post external links until comment karma > +25."
            )
        elif is_strict_comment and has_raw_links:
            risk_score += 0.40
            warnings.append(
                f"Unprompted Link Dump Risk: Dropping external links in r/{sub_clean} comments triggers cynical "
                "gatekeeping and downvotes. Explain the core mechanism and wait for organic reader demand."
            )

    body_lower = body.lower()
    promo_matches = [phrase for phrase in SELF_PROMO_TRIGGERS if phrase in body_lower]
    if promo_matches:
        risk_score += 0.35
        warnings.append(
            f"Self-referential language detected ({promo_matches}). "
            "Eliminate marketing terms ('our team', 'we open-sourced'). Frame as objective community discussion."
        )

    if title and len(title.split()) > 22:
        risk_score += 0.20
        warnings.append("Title exceeds 22 words; violates concise title rules in general subreddits.")

    return {
        "moderation_risk": min(1.0, round(risk_score, 3)),
        "is_ban_prone": risk_score >= 0.40,
        "moderation_warnings": warnings,
    }

def _score_compliance(subreddit: str, title: str, submission_statement: str) -> float:
    """
    Checks sub-specific formatting rules (e.g. [R] flair for r/MachineLearning)
    and mandatory submission statements.
    """
    sub_clean = subreddit.lower().replace("r/", "").strip()
    score = 0.0

    # Flair compliance
    if sub_clean == "machinelearning":
        if title.startswith("[R]") or title.startswith("[P]"):
            score += 0.4
    else:
        score += 0.4  # Other subreddits don't require title prefixes

    # Mandatory Submission Statement presence
    if submission_statement.strip():
        score += 0.3
        stmt_lower = submission_statement.lower()
        # Quality of submission statement (why it matters + AI disclosure)
        if any(marker in stmt_lower for marker in ("why this matters", "context", "objective")):
            score += 0.15
        if "terence tao" in stmt_lower or "transparency" in stmt_lower or "ai disclosure" in stmt_lower:
            score += 0.15

    return min(1.0, score)


def _score_resonance(body: str) -> float:
    """
    Evaluates readability, formatting structure, and absence of wall-of-text.
    """
    score = 0.0
    word_count = len(body.split())

    # Sweet spot length for scientific Reddit posts: 200 - 650 words
    if 180 <= word_count <= 700:
        score += 0.4
    elif 100 <= word_count < 180 or 700 < word_count <= 1000:
        score += 0.2

    # Markdown formatting (headers, bullet points, code or math blocks)
    has_headers = bool(re.search(r"^#{1,4}\s", body, re.MULTILINE))
    has_bullets = bool(re.search(r"^\s*[-*]\s", body, re.MULTILINE))
    has_math_or_code = "$" in body or "`" in body

    if has_headers:
        score += 0.2
    if has_bullets:
        score += 0.2
    if has_math_or_code:
        score += 0.2

    return min(1.0, score)


def compute_audience_reward(
    subreddit: str,
    title: str,
    body: str,
    submission_statement: str = "",
    is_comment: bool = False,
    karma_repair_mode: bool = False,
) -> dict[str, Any]:
    """
    Master reward function aggregating all components into a scalar in [0.0, 1.0].
    Enforces minimum grounding score (0.90) and maximum moderation risk (0.10) for recommendations.
    """
    s_hook = _score_hook(title, body)
    s_grounding = _score_grounding(body, submission_statement, is_comment=is_comment)
    s_modesty, violations = _score_modesty(title, body)
    s_compliance = _score_compliance(subreddit, title, submission_statement)
    s_resonance = _score_resonance(body)

    mod_audit = audit_moderation_risk(
        subreddit,
        title,
        body,
        is_comment=is_comment,
        karma_repair_mode=karma_repair_mode,
    )
    if mod_audit["is_ban_prone"]:
        # Severe penalty on compliance for ban-prone submissions
        s_compliance = max(0.0, s_compliance - mod_audit["moderation_risk"])
        violations.extend(mod_audit["moderation_warnings"])

    total_reward = (
        WEIGHT_HOOK * s_hook
        + WEIGHT_GROUNDING * s_grounding
        + WEIGHT_MODESTY * s_modesty
        + WEIGHT_COMPLIANCE * s_compliance
        + WEIGHT_RESONANCE * s_resonance
    )

    is_recommended = (
        total_reward >= 0.75
        and len(violations) == 0
        and not mod_audit["is_ban_prone"]
        and s_grounding >= 0.90
        and mod_audit["moderation_risk"] <= 0.10
    )

    return {
        "total_reward": round(total_reward, 4),
        "hook_score": round(s_hook, 3),
        "grounding_score": round(s_grounding, 3),
        "modesty_score": round(s_modesty, 3),
        "compliance_score": round(s_compliance, 3),
        "resonance_score": round(s_resonance, 3),
        "hype_violations": violations,
        "moderation_risk": mod_audit["moderation_risk"],
        "moderation_warnings": mod_audit["moderation_warnings"],
        "is_recommended": is_recommended,
    }


def audit_comment_reputation(
    comment_text: str,
    karma: int = -8,
    target_sub: str = "",
) -> dict[str, Any]:
    """
    Audits a candidate comment specifically for karma recovery and gatekeeping avoidance.
    Enforces Phase 1 Zero-Link Rule when karma < +25.
    """
    karma_repair_active = karma < 25
    mod = audit_moderation_risk(
        target_sub or "r/askphysics",
        title="",
        body=comment_text,
        is_comment=True,
        karma_repair_mode=karma_repair_active,
    )
    grounding = _score_grounding(comment_text, "", is_comment=True)
    modesty, violations = _score_modesty("", comment_text)

    is_safe = (
        mod["moderation_risk"] <= 0.10
        and len(violations) == 0
        and (not karma_repair_active or ("http" not in comment_text and "doi.org" not in comment_text and "github.com" not in comment_text))
    )

    return {
        "karma_repair_active": karma_repair_active,
        "is_safe_to_post": is_safe,
        "moderation_risk": mod["moderation_risk"],
        "grounding_score": round(grounding, 3),
        "modesty_score": round(modesty, 3),
        "warnings": mod["moderation_warnings"] + violations,
    }
