#!/usr/bin/env python3
"""
Fine-tune and predict performance of the r/OpenSourceeAI submission proposal.
Computes reward metrics, ModernBERT semantic resonance, and logs pre-flight
predictions to results/reddit_prediction_opensourceeai.json for retrofitting.
"""

import json
from pathlib import Path
from anse.community.audience_reward import compute_audience_reward
from anse.community.hf_audience_models import ModernBERTSemanticScorer

sub = "r/OpenSourceeAI"
sub_size = 33290

# Candidate 1: Initial Proposal
c1_title = "OpenAI formalized a Navier-Stokes singularity in Lean 4, but left the physics closed. We open-sourced the thermodynamic audit."
c1_body = """Hey everyone,

Thanks to the mods for the invite to the community. 

Like many of you, I followed the news about OpenAI using AI models and Lean 4 to formalize a finite-time blow-up for the 3D Navier-Stokes equations (one of the Millennium Prize problems). 

While the formal proof compiles with zero errors, closed-frontier labs rarely explore the messy physical implications of their mathematical constructions. As an independent researcher working on neuro-symbolic AI, our team wanted to see what their solution actually looks like in real-world fluid dynamics.

What we found when we simulated the construction in Python and mpmath:
• The math is legally sound within the abstract rules of the Clay problem.
• But physically, in liquid water, the fluid vaporizes from shear friction at 0.7 nanometers, picoseconds before the mathematical singularity. 
• Local flow speeds exceed Mach 0.3, breaking the incompressibility assumptions long before reaching infinity.

In AI, this is classic "specification gaming": the model found an extreme, unnatural edge case that legally satisfies the formal mathematical target, even though physical reality breaks down.

We believe scientific AI verification should be open, transparent, and reproducible, so we open-sourced the entire epistemic audit, simulation scripts, and Lean 4 reflection code:

• GitHub: https://github.com/xaviercallens/OpenAI-NSE-Epistemic-Audit
• Zenodo Preprint: https://doi.org/10.5281/zenodo.22838708

Since this community is focused on open-source AI, I'd love to hear your thoughts: As frontier labs push automated theorem proving, how can the open-source community build physical guardrails to keep AI models grounded in reality?"""

# Candidate 2: Optimized for Higher Hook & Open-Source Ethos
c2_title = "Why did OpenAI’s Lean 4 Navier-Stokes proof break physics? The open-source audit on specification gaming"
c2_body = """Hey everyone,

Thanks to the mods for the invite to r/OpenSourceeAI!

Like many of you, I followed OpenAI's formalization of the 3D Navier-Stokes blowup in Lean 4. Having frontier models generate a complete formal proof that compiles with zero errors is a major milestone for automated reasoning.

The math compiles with zero logic errors. But closed-frontier labs rarely explore the physical limits of their models. Coming from open-source neuro-symbolic research, I wanted to see what happens when you map this mathematical singularity to real-world physics.

When we simulated the solution in open-source Python (mpmath):
• The mathematics strictly satisfies the formal Millennium Prize definition.
• But physically, in liquid water, the fluid vaporizes from localized viscous friction at 0.7 nanometers, picoseconds before the singularity.
• Flow velocities exceed Mach 0.3, violently breaking the incompressibility assumption long before reaching infinity.

In machine learning, this is classic specification gaming: the AI exploited an unconstrained degree of freedom in the mathematical rules to find an extreme edge case. The code passes the compiler, but the physics melts.

We believe scientific AI verification should belong to the open-source community, not behind proprietary walls. We open-sourced the entire audit and verification scripts:

• GitHub repository: https://github.com/xaviercallens/OpenAI-NSE-Epistemic-Audit
• Zenodo preprint: https://doi.org/10.5281/zenodo.22838708

For folks working on open-weight models and scientific AI: As frontier labs advance automated theorem proving, how can the open-source community build physical boundary guardrails so models learn reality, not just formal syntax?"""

scorer = ModernBERTSemanticScorer()
sub_anchor = "Open source artificial intelligence open weights reproducible benchmarks community models datasets"

candidates = [("Candidate 1 (Initial)", c1_title, c1_body), ("Candidate 2 (Fine-Tuned)", c2_title, c2_body)]

print("=" * 80)
print(f"🔬 COMPARATIVE AUDIENCE REWARD EVALUATION FOR {sub}")
print("=" * 80)

results = []
for name, title, body in candidates:
    metrics = compute_audience_reward(sub, title, body)
    sim = scorer.compute_similarity(title + " " + body[:300], sub_anchor)
    
    # Expected metrics for r/OpenSourceeAI (33.3k members)
    # Baseline expected upvotes: 25 - 80; views: 3,000 - 12,000
    r_val = metrics["total_reward"]
    est_views = int(sub_size * 0.12 * (r_val / 0.65)**2.2)
    est_upvotes = int(est_views * 0.008 * (metrics["modesty_score"]))
    est_comments = int(est_upvotes * 0.28)

    print(f"\n[{name}]")
    print(f"  • Title:              {title}")
    print(f"  • Total Reward Score: {metrics['total_reward']:.4f} / 1.0000")
    print(f"    - Hook Score:       {metrics['hook_score']:.4f}")
    print(f"    - Grounding Score:  {metrics['grounding_score']:.4f}")
    print(f"    - Modesty Score:    {metrics['modesty_score']:.4f}")
    print(f"    - Compliance Score: {metrics['compliance_score']:.4f}")
    print(f"    - Resonance Score:  {metrics['resonance_score']:.4f}")
    print(f"    - Moderation Risk:  {metrics['moderation_risk']:.4f} (Safe)")
    print(f"  • Semantic Alignment: {sim:.4f}")
    print(f"  • Predicted Telemetry:")
    print(f"    - Estimated Views:    ~{est_views:,} views")
    print(f"    - Estimated Upvotes:  ~{est_upvotes} upvotes")
    print(f"    - Estimated Comments: ~{est_comments} comments")
    
    results.append({
        "name": name,
        "title": title,
        "body": body,
        "reward_score": metrics["total_reward"],
        "semantic_fit": sim,
        "metrics": metrics,
        "predicted_telemetry": {
            "est_views": est_views,
            "est_upvotes": est_upvotes,
            "est_comments": est_comments
        }
    })

# Save pre-flight prediction for retrofitting
out_file = Path("results/reddit_prediction_opensourceeai.json")
out_file.parent.mkdir(parents=True, exist_ok=True)
with open(out_file, "w") as f:
    json.dump({
        "subreddit": sub,
        "sub_size": sub_size,
        "timestamp": "2026-09-30T20:32:00",
        "best_candidate": results[1] if results[1]["reward_score"] > results[0]["reward_score"] else results[0],
        "all_candidates": results
    }, f, indent=2)

print("\n" + "=" * 80)
print(f"💾 Pre-flight predictions successfully saved to {out_file} for future retrofitting!")
print("=" * 80)
