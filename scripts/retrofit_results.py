#!/usr/bin/env python3
"""
Retrofit Real Reddit Telemetry against Pre-Flight Predictions.
Calculates calibration gap, applies Sherman-Morrison rank-1 update to Disjoint LinUCB,
and augments the DPO preference dataset with empirical ground truth.
Usage:
    python scripts/retrofit_results.py --target localllama --upvotes 350 --comments 95 --views 45000
"""

import argparse
import json
from pathlib import Path
from anse.community.contextual_bandit import DisjointLinUCB, extract_context_features

def main():
    parser = argparse.ArgumentParser(description="Retrofit Reddit results into RL models")
    parser.add_argument("--target", choices=["localllama", "opensourceeai"], required=True)
    parser.add_argument("--upvotes", type=int, required=True)
    parser.add_argument("--comments", type=int, required=True)
    parser.add_argument("--views", type=int, required=True)
    args = parser.parse_args()

    pred_file = Path(f"results/reddit_prediction_{args.target}.json")
    if not pred_file.exists():
        print(f"Error: {pred_file} not found.")
        return

    with open(pred_file, "r") as f:
        pred_data = json.load(f)

    pred_views = pred_data["predicted_telemetry"]["est_views"]
    pred_upvotes = pred_data["predicted_telemetry"]["est_upvotes"]
    pred_comments = pred_data["predicted_telemetry"]["est_comments"]
    model_r = pred_data["reward_score"]

    # Compute empirical ground truth reward (normalized [0, 1])
    real_r = min(1.0, (args.upvotes / (args.upvotes + 30)) + min(0.08, args.comments * 0.002))
    delta_r = real_r - model_r
    views_ratio = args.views / max(1, pred_views)

    print("=" * 80)
    print(f"📊 RETROFITTING TELEMETRY FOR r/{args.target.upper()}")
    print("=" * 80)
    print(f"  • Model Pre-Flight Reward:  {model_r:.4f}")
    print(f"  • Empirical Real Reward:    {real_r:.4f}")
    print(f"  • Calibration Gap (ΔR):     {delta_r:+.4f}")
    print("-" * 80)
    print(f"  • Views:    Predicted ~{pred_views:,}  vs  Real {args.views:,}  ({views_ratio:.2f}x)")
    print(f"  • Upvotes:  Predicted ~{pred_upvotes}   vs  Real {args.upvotes}")
    print(f"  • Comments: Predicted ~{pred_comments}    vs  Real {args.comments}")
    print("-" * 80)

    # 1. Update Contextual Bandit
    bandit = DisjointLinUCB()
    bandit_state = Path("results/contextual_bandit_state.json")
    if bandit_state.exists():
        bandit.load_state(bandit_state)
    
    # Context: systems/open-source AI domain (idx 3), hour=20 UTC, day=2, has_doi=True, has_code=True
    context = extract_context_features(domain="systems", hour_utc=20, day_of_week=2, has_doi=True, has_code=True)
    arm = 1  # benchmark / audit comparison arm
    bandit.update(action=arm, context=context, reward=real_r)
    bandit.save_state(bandit_state)
    print(f"✅ Successfully updated Disjoint LinUCB Bandit weights in {bandit_state}")

    # 2. Augment DPO preference dataset
    dpo_file = Path("results/dpo_scientific_dissemination.jsonl")
    golden_entry = {
        "prompt": f"Write an engaging open-source audit post for r/{args.target} on frontier AI formal proofs.",
        "chosen": f"Title: {pred_data['title']}\n\n{pred_data['body']}",
        "rejected": "Title: OpenAI proof is completely fake! Don't trust closed AI models.",
        "subreddit": args.target,
        "real_upvotes": args.upvotes,
        "real_views": args.views,
        "empirical_ground_truth": True
    }
    with open(dpo_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(golden_entry) + "\n")
    print(f"✅ Injected empirical golden pair into DPO dataset ({dpo_file})")
    print("=" * 80)

if __name__ == "__main__":
    main()
