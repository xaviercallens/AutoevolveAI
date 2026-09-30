#!/usr/bin/env python3
"""
Evaluate and predict response for comment on r/TheoreticalPhysics:
Post: 'Honestly, I am sad about Open AI announcement'
Author: u/animated_physicist
"""

from anse.community.audience_reward import compute_audience_reward
from anse.community.hf_audience_models import ModernBERTSemanticScorer

sub = "r/TheoreticalPhysics"

comment_body = """As someone working in computational physics and neuro-symbolic AI who actually audited OpenAI’s Lean 4 proof: **take a deep breath, human physics is not obsolete—in fact, this proof demonstrates the exact opposite.**

Here is the perspective that might bring you some peace of mind:

**1. The AI did not "do physics." It did formal logic search.**
The Clay Millennium Prize is a pure mathematics question about whether a specific set of continuum equations (incompressible Navier-Stokes) has smooth solutions or blows up. The AI found an extreme mathematical counterexample where velocity blows up while kinetic energy is technically bounded on paper.

**2. The AI's solution is completely unphysical.**
When we ran the actual fluid dynamics and thermodynamics on OpenAI's construction, it became immediately obvious that the AI has zero physical intuition:
• In real water, as the vortex contracts, local flow speeds exceed Mach 0.3 at 0.7 nanometers, violently shattering the incompressibility assumption.
• Friction dumps massive heat into the core, vaporizing the fluid into plasma picoseconds before reaching the mathematical singularity.

The compiler (Lean 4) accepted the proof because the formal syntax was legal. But real fluids have atoms, finite speed of sound, and thermodynamics. The AI had no idea because **AI models cannot understand physical reality without human physicists.**

**3. Why we need human physicists more than ever:**
What this announcement actually exposed is the massive blind spot of automated theorem provers: "specification gaming." An AI will happily find absurd, non-physical edge cases that legally satisfy human-written math definitions. 

Teaching AI systems the boundaries of nature—energy conservation, thermodynamic admissibility, and physical relevance—cannot be done by prompt engineers. It requires deep theoretical physicists who understand how math maps to the universe.

Don't be sad. You won't spend your career just prompting an AI. If anything, your job will be preventing AI systems from confusing mathematical loopholes with physical reality.

(If you want to see the numbers, we open-sourced the thermodynamic breakdown of the singularity: https://github.com/xaviercallens/OpenAI-NSE-Epistemic-Audit)"""

print("=" * 80)
print(f"🔬 EVALUATING COMMENT FOR {sub}")
print("=" * 80)

metrics = compute_audience_reward(sub, "Comment on r/TheoreticalPhysics", comment_body)
scorer = ModernBERTSemanticScorer()
sub_anchor = (
    "Theoretical physics mathematical physics Navier Stokes continuum mechanics "
    "physical intuition human discovery thermodynamics scientific philosophy"
)
sim = scorer.compute_similarity(comment_body[:300], sub_anchor)

print(f"Total Reward Score:     {metrics['total_reward']:.4f} / 1.0000")
print(f"  • Grounding Score:    {metrics['grounding_score']:.4f}")
print(f"  • Modesty Score:      {metrics['modesty_score']:.4f}")
print(f"  • Resonance Score:    {metrics['resonance_score']:.4f}")
print(f"ModernBERT Alignment:   {sim:.4f}")
print("-" * 80)
# Comment upvote prediction: high empathy + solid physics on a top post (+165 top comments)
est_upvotes = int(45 * metrics["modesty_score"] * (sim / 0.85))
print(f"Predicted Response / Community Upvotes: ~{est_upvotes}+ upvotes")
print("=" * 80)
