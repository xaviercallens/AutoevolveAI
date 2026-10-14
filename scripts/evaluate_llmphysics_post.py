#!/usr/bin/env python3
"""
Evaluate and Learn from Underperforming Reddit Post:
Subreddit: r/LLMPhysics
Title: 'On the recent Lean 4 formalization of the NSE blow-up: a physical and mathematical audit (Gevrey-2 cutoffs, condition numbers, and ESS)'
"""

from anse.community.audience_reward import compute_audience_reward
from anse.community.hf_audience_models import ModernBERTSemanticScorer

def main():
    print("=" * 80)
    print("📉 EVALUATION OF UNDERPERFORMING POST (r/LLMPhysics)")
    print("=" * 80)

    post_title = (
        "On the recent Lean 4 formalization of the NSE blow-up: a physical and "
        "mathematical audit (Gevrey-2 cutoffs, condition numbers, and ESS)"
    )
    subreddit = "r/LLMPhysics"
    post_body = (
        "The recent Lean 4 formalization of the forced 3D Navier-Stokes blow-up (Alternatives C and D) "
        "compiles perfectly. Zero sorrys, zero custom axioms, force typed as ContDiff ℝ ∞, global L² energy "
        "uniformly bounded. We verified this with an AST crawl. The kernel accepts it. That part is settled.\n\n"
        "However, after running a deep mathematical and physical audit on the construction itself, it is unclear "
        "whether three specific elements of the construction are bugs, features, or simply uncomfortable mathematical "
        "realities of the Millennium Prize framing.\n\n"
        "1. The Gevrey-2 Gap\n"
        "The Clay requirement is C^∞. The proof uses cutoffs of the form χ(q) ~ exp(−1/q²) — which belong to the "
        "Gevrey-2 class. This sits in C^∞ \\ C^ω. They are infinitely differentiable, but non-analytic.\n"
        "The derivative coefficients grow as (N!)^2.2. At order N = 100, the gradient coefficients are above 10^218. "
        "Legally, this is fine because Gevrey-2 ⊂ C^∞. But the entire reason the construction can have a smooth, "
        "compactly supported force is because it is not analytic (an analytic function zero on any open set is zero everywhere). "
        "The proof heavily exploits this gap.\n"
        "Question: Is this a legitimate solution to what the Clay Institute was asking, or did they not intend that "
        "loophole when they wrote 'smooth with compact support'?\n\n"
        "2. The Jacobian Condition Number\n"
        "The inner-outer gluing (Lemma 8.7 / Appendix B.8) matches 5 radial moments. The condition number of that system scales as:\n"
        "> κ(A) ~ λ^{-3} · (X_R)^{7.75}\n"
        "At X_R = 1000, κ ≈ 1.78 × 10^28. That is about 10⁵ times Avogadro's number.\n"
        "Our argument is that this cannot be fixed by preconditioning. The ill-conditioning comes from the physical "
        "separation of inner and outer length scales (the X_R^{7.75} term), not from a bad numerical representation. "
        "A stochastic thermal noise simulation at 300K shows the Reynolds-stress cancellation completely falls apart before X_R = 500.\n"
        "Question: Does structural instability of this magnitude matter for a mathematical existence proof? It feels like the "
        "singularity sits on a measure-zero knife edge that no physical perturbation can stay on.\n\n"
        "3. The L³ Threading\n"
        "Global kinetic energy goes as τ^{+0.485} (bounded, satisfying the Prize). But local enstrophy goes as τ^{-0.515}, "
        "and the L³ norm goes as τ^{-0.020}.\n"
        "The ESS theorem (Escauriaza, Seregin, Šverák, 2003) states you cannot have a singularity if ‖u‖_{L³} stays bounded. "
        "This construction has L³ diverging, but barely — exponent -0.020, which is vanishingly small. The scale parameter used is h = 1/200.\n"
        "Question: Is this chosen to thread the ESS needle on purpose? If yes, what does that say about how non-generic this construction is?\n\n"
        "Everything is fully reproducible. The Python scripts track the exact bounds mentioned above:\n"
        "```bash\n"
        "git clone https://github.com/xaviercallens/OpenAI-NSE-Epistemic-Audit\n"
        "pip install numpy scipy sympy mpmath matplotlib\n"
        "python scripts/directive3_jacobian_instability.py\n"
        "python scripts/directive4_gevrey_regularity.py\n"
        "```\n"
        "Paper and full LaTeX at DOI: 10.5281/zenodo.22727801\n"
        "https://doi.org/10.5281/zenodo.22727801\n\n"
        "(PS: I am a French independent citizen scientist and neuro-symbolic expert. It is too large and Lean 4 based, "
        "making it hard for a human to quickly review the raw code, so we built these diagnostic scripts. The numbers are "
        "what they are—please run the scripts and tell us if they're wrong if you are interested in a deep dive! I am new "
        "to this forum and social networks in general, so apologies if the formatting is off.)"
    )

    metrics = compute_audience_reward(subreddit, post_title, post_body, "")
    print(f"\n[1] AUDIENCE REWARD MODEL EVALUATION:")
    print(f"  • Total Reward Score:   {metrics['total_reward']:.4f}")
    print(f"    - Hook Score:         {metrics['hook_score']:.4f}")
    print(f"    - Grounding Score:    {metrics['grounding_score']:.4f}")
    print(f"    - Modesty Score:      {metrics['modesty_score']:.4f}")
    print(f"    - Compliance Score:   {metrics['compliance_score']:.4f}")
    print(f"    - Resonance Score:    {metrics['resonance_score']:.4f}")
    print(f"    - Hype Violations:    {metrics['hype_violations']}")
    print(f"    - Is Recommended:     {metrics['is_recommended']}")

    scorer = ModernBERTSemanticScorer()
    sub_anchor = "Large language models applied to physics simulations neural reasoning artificial intelligence"
    sim = scorer.compute_similarity(post_title, sub_anchor)
    print(f"\n[2] MODERNBERT SUBREDDIT-TOPIC ALIGNMENT:")
    print(f"  • Alignment with r/LLMPhysics focus: {sim:.4f}")

if __name__ == "__main__":
    main()
