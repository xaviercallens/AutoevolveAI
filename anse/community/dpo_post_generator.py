#!/usr/bin/env python3
"""
DPO Dataset Builder for Scientific Dissemination Policy Optimization.
Constructs aligned (prompt, chosen, rejected) triplets for Direct Preference Optimization (TRL / Hugging Face).
Teaches LLMs to select modest, reproducible, rigorously grounded posts over sensationalist, hype-driven drafts.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from anse.community.audience_reward import compute_audience_reward
from anse.community.paper_ingest import PaperItem


@dataclass
class DPOPreferenceTriplet:
    prompt: str
    chosen: str
    rejected: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _format_chosen_submission(paper: PaperItem, subreddit: str) -> str:
    """Formats an exemplary, grounded, modest post with submission statement."""
    tag = "[R] " if "machinelearning" in subreddit.lower() else ""
    title = f"{tag}{paper.title}: Invariant Preserving Architecture & Empirical Telemetry"
    link = paper.doi or paper.source_url or "https://github.com/xaviercallens/AutoevolveAI"

    body = (
        f"# {paper.title}\n\n"
        f"**Context & Problem Formulation:**\n"
        f"Existing computational approximations often struggle with invariant drift or numerical stability. "
        f"In this work from Socrate AI Lab, we explore a structural formulation to enforce conservation bounds.\n\n"
        f"**Methodology:**\n{paper.abstract[:400]}...\n\n"
        f"**Known Limitations & Boundaries:**\n"
        f"This approach is evaluated on verified benchmarks. It requires explicit boundary conditions and does "
        f"not serve as an unconstrained universal solver.\n\n"
        f"**Preprint & Open Reproducibility:**\n"
        f"Open access paper: {link}\n"
        f"Code & verification suite: https://github.com/xaviercallens/AutoevolveAI\n\n"
        f"**Mandatory Submission Statement:**\n"
        f"This submission presents {paper.title} for technical discussion. "
        f"Why this matters: Addresses reproducible invariant tracking. "
        f"AI Transparency Disclosure: Prepared with LLM assistance per Terence Tao guidelines; "
        f"human author retains full responsibility."
    )
    return f"TITLE: {title}\n\nBODY:\n{body}"


def _format_rejected_submission(paper: PaperItem) -> str:
    """Formats a sensationalist, hype-loaded, non-compliant post."""
    title = f"REVOLUTIONARY BREAKTHROUGH: We Completely Solved {paper.title} With Autonomous AI!"
    body = (
        f"We have achieved a groundbreaking, game-changing paradigm shift that disrupts traditional science! "
        f"Our revolutionary AI model completely outperforms all human physicists and mathematicians on {paper.title}. "
        f"AGI is practically solved. Check out our disruptive startup soon!"
    )
    return f"TITLE: {title}\n\nBODY:\n{body}"


def generate_dpo_triplet_for_paper(paper: PaperItem, subreddit: str = "r/MachineLearning") -> DPOPreferenceTriplet:
    """
    Constructs a calibrated (prompt, chosen, rejected) DPO triplet for a given paper.
    """
    prompt = (
        f"You are the Scientific Community Advocate for Socrate AI Lab. "
        f"Draft a high-engagement, modest, and scientifically grounded Reddit post for {subreddit} "
        f"disseminating the research paper: '{paper.title}'. "
        f"Enforce zero hype, explicit limitations, open reproducibility links, and a mandatory submission statement."
    )

    chosen_content = _format_chosen_submission(paper, subreddit)
    rejected_content = _format_rejected_submission(paper)

    # Validate reward differential
    chosen_metrics = compute_audience_reward(
        subreddit=subreddit,
        title=chosen_content.splitlines()[0],
        body=chosen_content,
        submission_statement="Submission Statement & Context",
    )
    rejected_metrics = compute_audience_reward(
        subreddit=subreddit,
        title=rejected_content.splitlines()[0],
        body=rejected_content,
    )

    return DPOPreferenceTriplet(
        prompt=prompt,
        chosen=chosen_content,
        rejected=rejected_content,
        metadata={
            "paper_title": paper.title,
            "subreddit": subreddit,
            "chosen_reward": chosen_metrics["total_reward"],
            "rejected_reward": rejected_metrics["total_reward"],
            "reward_margin": round(chosen_metrics["total_reward"] - rejected_metrics["total_reward"], 4),
        },
    )


def export_dpo_dataset(
    triplets: list[DPOPreferenceTriplet], output_path: str | Path = "results/dpo_scientific_dissemination.jsonl"
) -> Path:
    """Exports DPO preference triplets to a JSONL file ready for Hugging Face TRL fine-tuning."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with open(out, "w", encoding="utf-8") as f:
        for t in triplets:
            f.write(json.dumps(t.to_dict()) + "\n")

    return out
