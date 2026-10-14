#!/usr/bin/env python3
"""
Comparative RL Diagnostic Across 3 Real Reddit Submissions:
1. r/FluidMechanics (Hit: 160,000 views, 196 upvotes, 46 comments)
2. r/LLMPhysics (Low/Mixed: 13 comments, skepticism/backlash, security suspicion)
3. r/learnmachinelearning (Underperforming: 4 comments, wrong audience)
"""

from anse.community.audience_reward import compute_audience_reward
from anse.community.hf_audience_models import ModernBERTSemanticScorer

posts = [
    {
        "id": "fluid_mechanics",
        "sub": "r/FluidMechanics",
        "title": "The fluid dynamics behind OpenAI’s Navier-Stokes proof: Why the fluid would vaporize before the singularity",
        "body_preview": "Hey everyone, Following OpenAI recently claimed a formal proof demonstrating a finite-time blowup... Mach number easily exceeds 0.3 femtoseconds before blowup... condition number 10^28...",
        "views": "~160,000",
        "upvotes": 196,
        "comments": 46,
        "sentiment": "Strongly positive, highly engaged technical debate, shaped published paper"
    },
    {
        "id": "llm_physics",
        "sub": "r/LLMPhysics",
        "title": "On the recent Lean 4 formalization of the NSE blow-up: a physical and mathematical audit (Gevrey-2 cutoffs, condition numbers, and ESS)",
        "body_preview": "The recent Lean 4 formalization of the forced 3D Navier-Stokes blow-up compiles perfectly... git clone... pip install... python scripts...",
        "views": "~1,500",
        "upvotes": 6,
        "comments": 13,
        "sentiment": "Skeptical, criticized asking users to run scripts ('digital hygiene / malware'), questioned bump function framing"
    },
    {
        "id": "learn_ml",
        "sub": "r/learnmachinelearning",
        "title": "Could LLM-driven formal math lead to 'specification gaming'? A question on the recent Navier-Stokes proof",
        "body_preview": "There's been a lot of interest recently around OpenAI using AI models and Lean 4... specification gaming... non-analytic bump cutoffs...",
        "views": "~800",
        "upvotes": 4,
        "comments": 4,
        "sentiment": "Quiet/low engagement: topic (formal Lean 4 PDE verification) was far too advanced for a beginner tutorial subreddit"
    }
]

print("=" * 90)
print(f"{'Subreddit':<24} | {'Model R':<8} | {'Hook':<6} | {'Modesty':<8} | {'Comp':<6} | {'Res':<6} | {'Outcome':<18}")
print("-" * 90)

for p in posts:
    metrics = compute_audience_reward(p["sub"], p["title"], p["body_preview"])
    print(f"{p['sub']:<24} | {metrics['total_reward']:<8.4f} | {metrics['hook_score']:<6.2f} | {metrics['modesty_score']:<8.2f} | {metrics['compliance_score']:<6.2f} | {metrics['resonance_score']:<6.2f} | {p['upvotes']} up / {p['comments']} comm")

print("=" * 90)
