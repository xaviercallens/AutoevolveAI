"""
Cognitive Shield: Anti-Toxicity, Bad-Faith Defense, and Scientific Engagement Engine
Protects scientific reputation from bad-faith attacks, cynical snark, and toxic comments.
Classifies incoming feedback and synthesizes grounded, mathematically rigorous, de-escalating replies.
"""

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class CommentCategory(StrEnum):
    TECHNICAL_CRITIQUE = "technical_critique"
    HONEST_SKEPTICISM = "honest_skepticism"
    BAD_FAITH_SNARK = "bad_faith_snark"
    TOXIC_AD_HOMINEM = "toxic_ad_hominem"
    COLLABORATION_INTEREST = "collaboration_interest"


@dataclass
class ShieldAssessment:
    category: CommentCategory
    hostility_score: float  # 0.0 (cordial) to 1.0 (toxic)
    recommended_action: str  # 'reply_rigorous', 'reply_eli5', 'de_escalate_once', 'ignore_starve', 'reply_collaborate'
    rationale: str
    suggested_reply: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category.value,
            "hostility_score": round(self.hostility_score, 2),
            "recommended_action": self.recommended_action,
            "rationale": self.rationale,
            "suggested_reply": self.suggested_reply,
        }


class CognitiveShield:
    def __init__(self) -> None:
        self._toxic_markers = [
            "bs", "bullshit", "scam", "trash", "garbage", "idiot", "fraud",
            "snake oil", "clown", "stupid", "worthless", "grifter", "liar"
        ]
        self._bad_faith_markers = [
            "another useless", "just another", "waste of time", "delusional",
            "buzzword salad", "hype machine", "nobody cares", "who asked",
            "fake science", "pretentious"
        ]
        self._collab_markers = [
            "github", "reproduce", "try this", "collab", "contribute",
            "interesting paper", "great work", "extend this", "citation", "benchmark code",
            "read that paper", "read the paper", "read your paper", "kill to read", "love to read",
            "where can i read", "paper link", "link to paper", "link to the paper", "drop the link",
            "fantastic", "awesome work", "super interesting", "where is the paper", "is there a paper",
            "preprint link", "paper please", "share the paper", "link please",
        ]
        self._technical_markers = [
            "baseline", "proof", "theorem", "complexity", "ablation", "dataset",
            "hyperparameter", "latency", "benchmark", "error bars", "variance",
            "hardware", "p-value", "significance", "memory", "simd", "flcdm"
        ]
        self._skepticism_markers = [
            "skeptical", "skeptic", "doubt", "hard to believe", "not convinced",
            "unlikely to work", "sounds too good", "questionable"
        ]

    def _check_toxic(self, text: str) -> ShieldAssessment | None:
        toxic_hits = [m for m in self._toxic_markers if re.search(r"\b" + re.escape(m) + r"\b", text)]
        if not toxic_hits:
            return None
        return ShieldAssessment(
            category=CommentCategory.TOXIC_AD_HOMINEM,
            hostility_score=0.95,
            recommended_action="ignore_starve",
            rationale=f"Direct ad-hominem insult detected ({', '.join(toxic_hits)}). Never feed bad spirits on public forums.",
            suggested_reply="",
        )

    def _check_bad_faith(self, text: str) -> ShieldAssessment | None:
        snark_hits = [m for m in self._bad_faith_markers if m in text]
        if not snark_hits:
            return None
        de_escalation = (
            "We appreciate the critical eye. The complete experimental setup, raw telemetry, "
            "and mathematical proofs are fully open-source in the linked repository so anyone can independently "
            "verify or refute the results on their own hardware."
        )
        return ShieldAssessment(
            category=CommentCategory.BAD_FAITH_SNARK,
            hostility_score=0.70,
            recommended_action="de_escalate_once",
            rationale=f"Cynical or bad-faith dismissal detected ({', '.join(snark_hits)}). Calm, factual 1-sentence boundary.",
            suggested_reply=de_escalation,
        )

    def _check_collab(self, text: str) -> ShieldAssessment | None:
        collab_hits = [m for m in self._collab_markers if m in text]
        if not collab_hits:
            return None
        paper_request_markers = [
            "read that paper", "read the paper", "read your paper", "kill to read", "love to read",
            "where can i read", "paper link", "link to paper", "link to the paper", "drop the link",
            "where is the paper", "is there a paper", "preprint link", "paper please", "share the paper", "link please",
        ]
        is_paper_req = any(m in text for m in paper_request_markers)
        if is_paper_req:
            reply = (
                "Thank you so much for your interest! The preprint and reproduction code (including the Lean 4 formalization, "
                "Rust CVODE relaxation solvers, and Poisson summation derivations) are open-source: "
                "Preprint DOI: 10.5281/zenodo.23295142 | Repo: https://github.com/xaviercallens/SocrateAI-Scientific-MechanicaFluidorum. "
                "We would love to hear your thoughts, and especially welcome critical feedback on where our analysis might be challenged!"
            )
        else:
            reply = (
                "Thank you for your interest! We are actively welcoming open collaboration and independent reproductions. "
                "The codebase, benchmarks, and issue trackers are available on GitHub and Zenodo. Feel free to open an issue or PR "
                "if you'd like to test on different hardware or explore an extension."
            )
        return ShieldAssessment(
            category=CommentCategory.COLLABORATION_INTEREST,
            hostility_score=0.02 if is_paper_req else 0.05,
            recommended_action="reply_collaborate",
            rationale="Constructive researcher seeking paper access, collaboration, or code reproduction.",
            suggested_reply=reply,
        )

    def _check_skepticism(self, text: str) -> ShieldAssessment | None:
        skep_hits = [m for m in self._skepticism_markers if m in text]
        if not skep_hits:
            return None
        return ShieldAssessment(
            category=CommentCategory.HONEST_SKEPTICISM,
            hostility_score=0.20,
            recommended_action="reply_eli5",
            rationale=f"Honest skepticism detected ({', '.join(skep_hits)}). Provide intuitive ELI5 explanation with transparent limitations.",
            suggested_reply="Good question! In brief: rather than relying on heuristic approximations, the approach enforces strict invariant bounds. The main limitation is that it requires verifiable boundary conditions, so it is not a drop-in silver bullet for unstructured problems.",
        )

    def _check_technical(self, text: str) -> ShieldAssessment | None:
        tech_hits = [m for m in self._technical_markers if m in text]
        if not tech_hits:
            return None
        return ShieldAssessment(
            category=CommentCategory.TECHNICAL_CRITIQUE,
            hostility_score=0.25,
            recommended_action="reply_rigorous",
            rationale=f"Legitimate technical inquiry regarding: {', '.join(tech_hits)}. Requires rigorous receipts.",
            suggested_reply=f"Fair question regarding {', '.join(tech_hits)}. In our evaluation (detailed in Section 4 of the paper), we specifically isolated this variable. The raw execution logs and reproduction scripts are in the repository for full auditability.",
        )

    def _default_skepticism(self) -> ShieldAssessment:
        return ShieldAssessment(
            category=CommentCategory.HONEST_SKEPTICISM,
            hostility_score=0.20,
            recommended_action="reply_eli5",
            rationale="General community inquiry or healthy skepticism. Provide intuitive ELI5 explanation with transparent limitations.",
            suggested_reply="Good question! In brief: rather than relying on heuristic approximations, the approach enforces strict invariant bounds. The main limitation is that it requires verifiable boundary conditions, so it is not a drop-in silver bullet for unstructured problems.",
        )

    def classify_comment(self, comment_text: str, context_paper_title: str = "") -> ShieldAssessment:
        """
        Classifies incoming Reddit comment and determines optimal de-escalation or engagement response.
        """
        text = comment_text.lower()
        res = (
            self._check_toxic(text)
            or self._check_bad_faith(text)
            or self._check_collab(text)
            or self._check_skepticism(text)
            or self._check_technical(text)
        )
        return res or self._default_skepticism()

    def formulate_grounded_response(
        self,
        comment_text: str,
        paper_title: str,
        verified_data_point: str,
        limitations: str = "",
    ) -> str:
        """
        Synthesizes a response strictly adhering to zero-drama, verified science communication rules.
        """
        assessment = self.classify_comment(comment_text, paper_title)

        if assessment.recommended_action == "ignore_starve":
            return ""

        if assessment.recommended_action == "de_escalate_once":
            return assessment.suggested_reply

        # Construct high-rigor reply
        response = (
            f"Thanks for raising this point regarding '{paper_title}'.\n\n"
            f"**Empirical Verification:** {verified_data_point}\n\n"
        )
        if limitations:
            response += f"**Transparent Limitations:** To be completely clear, {limitations}\n\n"

        response += "All scripts, test suites, and raw data are open-source for full independent reproduction."
        return response

    def audit_draft_tone(self, text: str) -> dict[str, Any]:
        """
        Audits candidate post/comment text for academic credibility gatekeeping hazards
        and self-defeating framing traps (e.g. 'I am more an AI person', 'AI agent swarm').
        """
        text_l = text.lower()
        warnings: list[str] = []
        suggestions: list[str] = []

        gatekeeping_traps = {
            "i am more an ai person": "Disclaims domain authority and prompts gatekeeping from theorists on r/math / r/Physics.",
            "our ai agent swarm": "Triggers immediate anti-AI skepticism; frame around objective theorem syntax and solver quenches.",
            "ai agent swarm": "Triggers immediate anti-AI skepticism; frame around objective theorem syntax and solver quenches.",
            "our team discovered a loophole": "Sounds combative; frame as 'auditing boundary terms and statement adequacy in Lean 4'.",
            "our team audited this and found": "Without tenure/paper, claims of team audits prompt downvotes; state the formal verification steps directly.",
            "we completely solved": "Absolute claims trigger instant backlash; frame as bounded empirical observations.",
        }

        for trap, warning in gatekeeping_traps.items():
            if trap in text_l:
                warnings.append(f"Gatekeeping Trigger: '{trap}' — {warning}")

        is_safe = len(warnings) == 0
        if not is_safe:
            suggestions.append(
                "Recommendation: Rewrite from the perspective of an objective technical investigator. "
                "Cite concrete axioms (#print axioms), specific numerical solvers (CVODE), and exact physical scales (Mach > 0.3)."
            )

        return {
            "is_safe_tone": is_safe,
            "tone_warnings": warnings,
            "suggestions": suggestions,
        }

    def audit_link_policy(
        self,
        text: str,
        is_comment: bool = True,
        comment_karma: int = -8,
        is_reply_to_request: bool = False,
    ) -> dict[str, Any]:
        """
        Enforces Phase 1 Karma Repair (Zero-Link Rule) and Organic Pull protocol.
        """
        has_links = bool(re.search(r"https?://|doi\.org|github\.com|zenodo\.", text))
        karma_repair_active = comment_karma < 25

        if is_comment:
            if karma_repair_active and has_links:
                return {
                    "is_compliant": False,
                    "phase": "Phase 1: Karma Repair (-8 to +25)",
                    "rule": "Strict Zero-Link Rule",
                    "reason": f"Active comment karma is {comment_karma} (< +25). Any external link risks AutoMod filtering or cynical downvotes. Remove all links.",
                }
            if not is_reply_to_request and has_links:
                return {
                    "is_compliant": False,
                    "phase": "Phase 2: Organic Pull Protocol",
                    "rule": "Wait for Demand Rule",
                    "reason": "External links dropped unprompted in comments trigger marketing cynicism. Explain the math/physics and provide links only when requested.",
                }

        return {
            "is_compliant": True,
            "phase": "Compliant",
            "rule": "Zero-Link or Authorized Organic Delivery",
            "reason": "No unprompted links detected or user explicitly requested paper/code.",
        }
