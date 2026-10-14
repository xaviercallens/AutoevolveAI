#!/usr/bin/env python3
"""
CLI Runner for ANSE Scientific Community Advocate Agent
Executes literature discovery, Reddit trend scouting, post drafting, and Cognitive Shield evaluation.
"""

import argparse
import sys
from pathlib import Path

# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from anse.community.config import DOMAIN_SUBREDDITS, ResearchDomain
from anse.community.orchestrator import CommunityOrchestrator
from anse.community.paper_ingest import PaperItem

console = Console()


def handle_scout_mode(orchestrator: CommunityOrchestrator, domain: ResearchDomain) -> None:
    console.print(f"\n[bold cyan]=== Scouting Research & Reddit Trends: {domain.value} ===[/bold cyan]\n")
    report = orchestrator.run_discovery_cycle(domain)

    # 1. External Literature
    ext = report["external_literature"]
    console.print(f"[bold yellow]Found {ext['arxiv_count']} arXiv and {ext['zenodo_count']} Zenodo papers.[/bold yellow]")
    for item in ext["sample"]:
        console.print(f"  • [bold]{item['title']}[/bold] ({item['source_type'].upper()})")
        console.print(f"    [dim]{item['source_url']}[/dim]")

    # 2. Local Author Papers
    auth = report["author_papers"]
    console.print(f"\n[bold green]Local ANSE Research Papers in 'papers/': {auth['total_local']} total ({auth['domain_relevant']} matching domain).[/bold green]")
    for item in auth["sample"]:
        console.print(f"  • [bold]{item['title']}[/bold]")
        console.print(f"    [dim]File: {item['local_path']}[/dim]")

    # 3. Reddit Trends & Intelligence
    reddit_info = report["reddit_intelligence"]
    console.print("\n[bold magenta]Reddit Discussion Intelligence & Hot Topics:[/bold magenta]")

    for trend in reddit_info["trends"]:
        table = Table(title=f"Subreddit r/{trend['subreddit']} (Domain: {trend['domain']})", show_lines=True)
        table.add_column("Top Topics", style="cyan")
        table.add_column("Emerging Questions & Pain Points", style="yellow")
        table.add_row(
            "\n".join(f"• {t}" for t in trend["top_topics"]) or "N/A",
            "\n".join(f"• {q}" for q in trend["emerging_questions"]) or "No questions flagged",
        )
        console.print(table)


def handle_draft_mode(
    orchestrator: CommunityOrchestrator,
    domain: ResearchDomain,
    paper_path: str | None,
    subreddit: str | None,
) -> None:
    console.print("\n[bold cyan]=== Drafting Grounded Reddit Submission ===[/bold cyan]\n")

    # Select target paper
    paper: PaperItem
    if paper_path and Path(paper_path).exists():
        extracted_text = orchestrator.ingest_engine.extract_paper_markdown(paper_path)
        title = Path(paper_path).stem.replace("_", " ").title()
        abstract = extracted_text[:500] if extracted_text else "ANSE research publication."
        paper = PaperItem(
            title=title,
            abstract=abstract,
            authors=["Xavier Callens", "ANSE Research Collective"],
            source_url="https://github.com/xaviercallens/AutoevolveAI",
            source_type="local",
            local_path=paper_path,
        )
    else:
        # Search local papers for first matching
        local_papers = orchestrator.ingest_engine.scan_local_papers()
        if local_papers:
            paper = local_papers[0]
        else:
            paper = PaperItem(
                title="Autopoietic Neuro-Symbolic Energy Minimization",
                abstract="A framework enforcing physical conservation laws and deterministic sandbox evaluation.",
                authors=["ANSE Research Collective"],
                source_url="https://github.com/xaviercallens/AutoevolveAI",
                source_type="local",
            )

    target_sub = subreddit or DOMAIN_SUBREDDITS.get(domain, ["MachineLearning"])[0]
    draft = orchestrator.prepare_post(paper, target_subreddit=target_sub, domain=domain)

    # Render Post Panel
    console.print(
        Panel(
            f"[bold]Target Subreddit:[/bold] r/{draft.subreddit}\n"
            f"[bold]Flair Tag:[/bold] {draft.flair}\n"
            f"[bold]Post Title:[/bold] {draft.title}\n"
            f"[bold]Anti-Sensationalism Gate:[/bold] {'[red]FAILED (Buzzwords detected)[/red]' if draft.has_banned_buzzwords else '[green]PASSED (Zero Hype)[/green]'}\n\n"
            f"[bold]Post Body Preview:[/bold]\n{draft.body[:600]}...\n\n"
            f"[bold]Mandatory Submission Statement (Comment 1):[/bold]\n{draft.submission_statement}",
            title="Reddit Submission Draft (Ready for Human Approval)",
            border_style="green",
        )
    )


def handle_shield_mode(orchestrator: CommunityOrchestrator, comment: str) -> None:
    console.print("\n[bold cyan]=== Cognitive Shield: Feedback & Defense Evaluation ===[/bold cyan]\n")
    assessment = orchestrator.evaluate_comment_and_respond(comment, "ANSE Research Paper")

    color_map = {
        "technical_critique": "blue",
        "honest_skepticism": "yellow",
        "bad_faith_snark": "magenta",
        "toxic_ad_hominem": "red",
        "collaboration_interest": "green",
    }
    cat_color = color_map.get(assessment.category.value, "white")

    console.print(
        Panel(
            f"[bold]Incoming Comment:[/bold] \"{comment}\"\n\n"
            f"[bold]Classified Category:[/bold] [{cat_color}]{assessment.category.value.upper()}[/{cat_color}]\n"
            f"[bold]Hostility Score:[/bold] {assessment.hostility_score:.2f} / 1.0\n"
            f"[bold]Recommended Action:[/bold] [bold]{assessment.recommended_action}[/bold]\n"
            f"[bold]Rationale:[/bold] {assessment.rationale}\n\n"
            f"[bold]Suggested Reply / Defense Strategy:[/bold]\n"
            f"\"{assessment.suggested_reply or '[NO REPLY - Starve the Troll]'}\"",
            title="Cognitive Shield Assessment",
            border_style=cat_color,
        )
    )


def _resolve_target_paper(
    orchestrator: CommunityOrchestrator,
    domain: ResearchDomain,
    paper_path: str | None = None,
) -> PaperItem:
    """Resolves paper from path, domain scan, or falls back to default MHD paper."""
    if paper_path and Path(paper_path).exists():
        p = orchestrator.ingest_engine.parse_local_paper(Path(paper_path))
        if p:
            return p

    local_papers = orchestrator.ingest_engine.scan_local_papers()
    relevant = [p for p in local_papers if domain in p.matched_domains]
    if relevant:
        return relevant[0]
    if local_papers:
        return local_papers[0]

    return PaperItem(
        title="Structure-Preserving and Gauge-Invariant Neural Operators for Magnetohydrodynamics",
        abstract="We present the Structure-Preserving Gauge Neural Operator (SP-GNO) enforcing div(B)=0 to machine precision.",
        doi="10.5281/zenodo.22160185",
        matched_domains=[domain],
    )


def handle_prescribe_mode(
    orchestrator: CommunityOrchestrator,
    domain: ResearchDomain,
    paper_path: str | None = None,
    subreddit: str | None = None,
    use_hf_models: bool = False,
) -> None:
    from anse.community.dpo_post_generator import export_dpo_dataset, generate_dpo_triplet_for_paper
    from anse.community.post_prescriptor import PostPrescriptor

    console.print("\n[bold cyan]=== RL Post Prescriptor & Audience Optimization ===[/bold cyan]\n")
    sub = subreddit or DOMAIN_SUBREDDITS.get(domain, ["r/MachineLearning"])[0]
    paper = _resolve_target_paper(orchestrator, domain, paper_path)

    prescriptor = PostPrescriptor(subreddit=sub, use_hf_models=use_hf_models)
    report = prescriptor.prescribe_best_post(paper)
    best = report.best_candidate

    panel_text = (
        f"[bold]Target Subreddit:[/bold] {report.target_subreddit}\n"
        f"[bold]Recommended Window:[/bold] {report.recommended_utc_window}\n"
        f"[bold]Selected Strategy:[/bold] [bold green]{best.strategy_name}[/bold green]\n"
        f"[bold]Overall Audience Reward:[/bold] [bold cyan]{best.reward_breakdown['total_reward'] * 100:.1f}%[/bold cyan]\n"
    )
    if "semantic_relevance_score" in best.reward_breakdown:
        panel_text += f"[bold]ModernBERT Semantic Match:[/bold] [bold magenta]{best.reward_breakdown['semantic_relevance_score'] * 100:.1f}%[/bold magenta]\n"
    if report.bandit_recommendation:
        b_rec = report.bandit_recommendation
        panel_text += (
            f"[bold]LinUCB Bandit Payoff:[/bold] {b_rec.get('predicted_payoff', 0):.3f} "
            f"(UCB: {b_rec.get('ucb_score', 0):.3f}, Sub: {b_rec.get('subreddit')})\n"
        )

    panel_text += (
        f"\n[bold]Optimal Post Title:[/bold]\n{best.title}\n\n"
        f"[bold]Teaser / Problem Hook:[/bold]\n\"{best.teaser_hook}\"\n\n"
        f"[bold]Post Body Preview:[/bold]\n{best.body[:500]}...\n\n"
        f"[bold]Mandatory Submission Statement (Comment 1):[/bold]\n{best.submission_statement}\n\n"
        f"[bold]Anticipated Defense (Cognitive Shield):[/bold]\n"
        + "\n".join(f"  • Q: {qa['q']}\n    A: {qa['a']}" for qa in best.anticipated_qa)
    )

    console.print(
        Panel(
            panel_text,
            title="🎯 Prescribed Optimal Scientific Post (RL Policy Output)",
            border_style="green",
        )
    )

    # Export DPO preference dataset
    triplet = generate_dpo_triplet_for_paper(paper, sub)
    dpo_path = export_dpo_dataset([triplet])
    console.print(f"\n[dim green]✓ DPO Preference Triplet exported to {dpo_path} for Hugging Face TRL fine-tuning.[/dim green]\n")


def main():
    parser = argparse.ArgumentParser(description="ANSE Scientific Community Advocate Agent")
    parser.add_argument(
        "--mode",
        choices=["scout", "draft", "shield", "prescribe", "full_audit"],
        default="prescribe",
        help="Operating mode: scout (trends), draft (post), shield (defense), prescribe (RL optimal post), full_audit (all)",
    )
    parser.add_argument(
        "--domain",
        choices=[d.value for d in ResearchDomain],
        default=ResearchDomain.AI_OPTIMIZATION.value,
        help="Strategic domain to operate on",
    )
    parser.add_argument("--paper", type=str, default=None, help="Path to local paper file (PDF, TeX, MD)")
    parser.add_argument("--subreddit", type=str, default=None, help="Target subreddit name")
    parser.add_argument("--comment", type=str, default=None, help="Comment text to test with Cognitive Shield")
    parser.add_argument(
        "--use-hf-models",
        action="store_true",
        help="Enable locally cached Hugging Face models (ModernBERT & Qwen2.5-0.5B)",
    )

    args = parser.parse_args()
    domain = ResearchDomain(args.domain)
    orchestrator = CommunityOrchestrator()

    if args.mode == "scout":
        handle_scout_mode(orchestrator, domain)
    elif args.mode == "draft":
        handle_draft_mode(orchestrator, domain, args.paper, args.subreddit)
    elif args.mode == "shield":
        comment = args.comment or "This looks completely fake. Just another useless AI paper with zero real math."
        handle_shield_mode(orchestrator, comment)
    elif args.mode == "prescribe":
        handle_prescribe_mode(
            orchestrator, domain, args.paper, args.subreddit, use_hf_models=args.use_hf_models
        )
    elif args.mode == "full_audit":
        console.print("[bold green]=== Full Cross-Domain Strategic Intelligence Sweep ===[/bold green]")
        for d in ResearchDomain:
            console.print(f"\n[bold cyan]>>> Auditing Domain: {d.value}[/bold cyan]")

            handle_scout_mode(orchestrator, d)


if __name__ == "__main__":
    main()
