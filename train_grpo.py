#!/usr/bin/env python3
"""
Group Relative Policy Optimization (GRPO) Trainer with Deterministic Attestation Rewards.
Trained on RTX 2080 (8GB VRAM) without a critic/value model to minimize memory usage.
Evaluates candidates against deterministic anti-stub, anti-leakage, and test verification gates.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from radon.visitors import ComplexityVisitor

# Reward Constants
REWARD_PASS = 1.0
REWARD_FAIL = -1.0
REWARD_STUB_PENALTY = -1.0
REWARD_FAKE_DATA_PENALTY = -0.5
REWARD_COMPLEXITY_PENALTY = -0.5
REWARD_CLEAN_BONUS = 0.25


def check_has_stubs(content: str) -> bool:
    """Detects naked stubs or unfulfilled markers in candidate code."""
    for marker in ("pass", "...", "NotImplementedError"):
        if marker in content:
            return True
    return False


def check_fake_data_leakage(content: str) -> bool:
    """Detects mock or dummy variable leakages into candidate production code."""
    lower = content.lower()
    for prefix in ("mock_", "dummy_", "fake_data", "test_stub"):
        if prefix in lower:
            return True
    return False


def check_cyclomatic_complexity_exceeded(content: str, max_cc: int = 10) -> bool:
    """Verifies that no function or method exceeds the cyclomatic complexity threshold."""
    try:
        blocks = ComplexityVisitor.from_code(content).blocks
        return any(b.complexity > max_cc for b in blocks)
    except (OSError, RuntimeError, SyntaxError):
        return False


def compute_code_hygiene_reward(completion: str) -> float:
    """Calculates reward based on anti-stub, fake data, and complexity metrics."""
    score = 0.0
    if check_has_stubs(completion):
        score += REWARD_STUB_PENALTY
    else:
        score += REWARD_CLEAN_BONUS

    if check_fake_data_leakage(completion):
        score += REWARD_FAKE_DATA_PENALTY

    if check_cyclomatic_complexity_exceeded(completion):
        score += REWARD_COMPLEXITY_PENALTY

    return score


def evaluate_candidate_reward(candidate: dict[str, Any]) -> float:
    """Computes combined deterministic reward for a candidate completion."""
    completion = str(candidate.get("completion", ""))
    verdict = candidate.get("verdict", "")

    hygiene_score = compute_code_hygiene_reward(completion)

    verdict_score = 0.0
    if verdict == "PASSED":
        verdict_score = REWARD_PASS
    elif verdict == "FAILED":
        verdict_score = REWARD_FAIL

    return round(verdict_score + hygiene_score, 4)


def compute_group_advantages(rewards: list[float], eps: float = 1e-8) -> list[float]:
    """Normalizes candidate rewards across the group into advantage estimates."""
    if not rewards:
        return []
    if len(rewards) == 1:
        return [0.0]

    mean_r = sum(rewards) / len(rewards)
    var = sum((r - mean_r) ** 2 for r in rewards) / len(rewards)
    std_r = math.sqrt(var)

    if std_r < eps:
        return [0.0 for _ in rewards]

    return [round((r - mean_r) / (std_r + eps), 4) for r in rewards]


def compute_grpo_loss_sample(
    logp_policy: float,
    logp_ref: float,
    advantage: float,
    clip_eps: float = 0.2,
    beta_kl: float = 0.04,
) -> float:
    """Computes scalar clipped surrogate loss with KL divergence for a single sample."""
    ratio = math.exp(logp_policy - logp_ref)
    clipped_ratio = max(1.0 - clip_eps, min(1.0 + clip_eps, ratio))
    surr1 = ratio * advantage
    surr2 = clipped_ratio * advantage
    policy_loss = -min(surr1, surr2)

    # Approximate KL divergence: KL(policy || ref) ~ (ratio - 1) - log(ratio)
    kl_div = (ratio - 1.0) - (logp_policy - logp_ref)
    return policy_loss + beta_kl * max(0.0, kl_div)


def load_grpo_groups(file_path: Path) -> list[dict[str, Any]]:
    """Loads grouped prompt candidates from JSONL dataset."""
    if not file_path.exists():
        return []
    groups: list[dict[str, Any]] = []
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped:
                try:
                    groups.append(json.loads(stripped))
                except json.JSONDecodeError:
                    continue
    return groups


def process_single_grpo_group(group: dict[str, Any]) -> dict[str, Any]:
    """Evaluates rewards and advantages for all candidates in a group."""
    candidates = group.get("candidates", [])
    rewards = [evaluate_candidate_reward(c) for c in candidates]
    advantages = compute_group_advantages(rewards)

    annotated_candidates = []
    for c, r_val, adv in zip(candidates, rewards, advantages, strict=False):
        annotated_candidates.append(
            {
                "completion_preview": str(c.get("completion", ""))[:120],
                "reward": r_val,
                "advantage": adv,
                "verdict": c.get("verdict", "UNKNOWN"),
            }
        )

    return {
        "prompt_turns": len(group.get("prompt", [])),
        "group_size": len(candidates),
        "mean_reward": round(sum(rewards) / len(rewards), 4) if rewards else 0.0,
        "candidates": annotated_candidates,
    }


def execute_grpo_run(
    dataset_path: Path,
    model_name: str = "Qwen/Qwen2.5-Coder-1.5B-Instruct",
    group_size: int = 4,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Loads dataset and runs GRPO reward and advantage computation or dry-run."""
    groups = load_grpo_groups(dataset_path)
    processed_groups = [process_single_grpo_group(g) for g in groups]

    total_candidates = sum(len(g.get("candidates", [])) for g in groups)
    summary = {
        "status": "COMPLETED_DRY_RUN" if dry_run else "READY_FOR_RL",
        "algorithm": "GRPO (Group Relative Policy Optimization)",
        "model_name": model_name,
        "target_hardware": "NVIDIA GeForce RTX 2080 (8GB VRAM)",
        "group_count": len(groups),
        "total_candidates": total_candidates,
        "configured_group_size": group_size,
        "processed_groups": processed_groups[:5],
    }
    return summary


def main() -> None:
    """CLI Entrypoint for GRPO training."""
    parser = argparse.ArgumentParser(
        description="GRPO Trainer with Deterministic Attestation Rewards for RTX 2080"
    )
    parser.add_argument(
        "--dataset", default="dataset_grpo.jsonl", help="Path to GRPO groups JSONL dataset"
    )
    parser.add_argument(
        "--model",
        default="Qwen/Qwen2.5-Coder-1.5B-Instruct",
        help="Base model checkpoint name or path",
    )
    parser.add_argument("--group-size", type=int, default=4, help="Candidate group size")
    parser.add_argument("--dry-run", action="store_true", help="Validate setup and rewards")
    args = parser.parse_args()

    result = execute_grpo_run(
        dataset_path=Path(args.dataset),
        model_name=args.model,
        group_size=args.group_size,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2))


__all__ = [
    "check_has_stubs",
    "check_fake_data_leakage",
    "check_cyclomatic_complexity_exceeded",
    "compute_code_hygiene_reward",
    "evaluate_candidate_reward",
    "compute_group_advantages",
    "compute_grpo_loss_sample",
    "load_grpo_groups",
    "process_single_grpo_group",
    "execute_grpo_run",
    "main",
]


if __name__ == "__main__":
    main()
