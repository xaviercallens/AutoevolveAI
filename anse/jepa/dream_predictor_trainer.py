"""Gated trainer for the dream-phase verdict predictor, fed only by the verified pool.

The predictor is a logistic probe on episode embeddings: it scores how likely a step is to fail.
Its evidence is measured the way it will be used, on tasks it has never seen:

- Folds are grouped by task, so no task contributes to both training and evaluation.
- Metric is AUROC, never accuracy. Always predicting "held" already scores the pass rate.
- A shuffled-label control is trained on the same folds with the labels permuted across rows.
- The gate passes only when the worst real fold, across every seed, beats the best control fold
  by more than the control's spread. Otherwise the result is BLOCKED and no checkpoint is written.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any

import torch

DEFAULT_SEEDS: tuple[int, ...] = (0, 1, 2)
DEFAULT_FOLDS: int = 5
MIN_POSITIVES: int = 30


def auroc(scores: list[float], labels: list[int]) -> float:
    """Probability that a random failure is scored above a random pass (ties count half)."""
    pos = [s for s, y in zip(scores, labels, strict=True) if y == 1]
    neg = [s for s, y in zip(scores, labels, strict=True) if y == 0]
    if not pos or not neg:
        return float("nan")
    wins = 0.0
    for p in pos:
        for n in neg:
            wins += 1.0 if p > n else (0.5 if p == n else 0.0)
    return wins / (len(pos) * len(neg))


def grouped_folds(tasks: list[str], k: int, seed: int) -> list[set[str]]:
    """Partition the distinct tasks into ``k`` disjoint groups, reproducibly for a seed."""
    uniq = sorted(set(tasks))
    random.Random(seed).shuffle(uniq)
    return [set(uniq[i::k]) for i in range(k)]


def fit_probe_state(
    x_train: torch.Tensor, y_train: torch.Tensor, seed: int
) -> dict[str, torch.Tensor]:
    """Fit a standardised logistic probe with binary cross-entropy, a strictly proper rule.

    Returns the standardisation statistics and the learned weights, so the probe can be saved
    and applied to new embeddings with ``probe_scores``.
    """
    torch.manual_seed(seed)
    mu = x_train.mean(0)
    sd = x_train.std(0) + 1e-6
    xt = (x_train - mu) / sd
    weight = torch.zeros(xt.shape[1], requires_grad=True)
    bias = torch.zeros(1, requires_grad=True)
    opt = torch.optim.Adam([weight, bias], lr=1e-2, weight_decay=1e-2)
    for _ in range(300):
        opt.zero_grad()
        loss = torch.nn.functional.binary_cross_entropy_with_logits(xt @ weight + bias, y_train)
        loss.backward()
        opt.step()
    return {"mu": mu, "sd": sd, "weight": weight.detach(), "bias": bias.detach()}


def probe_scores(state: dict[str, torch.Tensor], x: torch.Tensor) -> torch.Tensor:
    """Failure logits for ``x`` under a fitted probe state."""
    with torch.no_grad():
        return ((x - state["mu"]) / state["sd"]) @ state["weight"] + state["bias"]


def fit_logistic_probe(
    x_train: torch.Tensor, y_train: torch.Tensor, x_test: torch.Tensor, seed: int
) -> torch.Tensor:
    """Fit on the training split and score the held-out split."""
    return probe_scores(fit_probe_state(x_train, y_train, seed), x_test)


def fold_aurocs(rows: list[dict[str, Any]], labels: list[int], seed: int) -> list[float]:
    """AUROC for each task-held-out fold. Folds without both classes are skipped, not guessed."""
    x = torch.tensor([r["hidden_state"] for r in rows], dtype=torch.float32)
    y = torch.tensor(labels, dtype=torch.float32)
    tasks = [r["task"] for r in rows]
    out: list[float] = []
    for held in grouped_folds(tasks, DEFAULT_FOLDS, seed):
        test_idx = [i for i, t in enumerate(tasks) if t in held]
        train_idx = [i for i, t in enumerate(tasks) if t not in held]
        test_labels = [labels[i] for i in test_idx]
        if len(set(test_labels)) < 2 or not train_idx:
            continue
        scores = fit_logistic_probe(x[train_idx], y[train_idx], x[test_idx], seed)
        out.append(auroc(scores.tolist(), test_labels))
    return out


@dataclass
class GateResult:
    status: str
    reasons: list[str] = field(default_factory=list)
    positives: int = 0
    real_folds: dict[int, list[float]] = field(default_factory=dict)
    control_folds: dict[int, list[float]] = field(default_factory=dict)
    worst_real: float = float("nan")
    control_best: float = float("nan")
    control_spread: float = float("nan")


def evaluate_gate(rows: list[dict[str, Any]], seeds: tuple[int, ...] = DEFAULT_SEEDS) -> GateResult:
    """Run real and shuffled-label probes over every seed and decide PASS or BLOCKED."""
    labels = [int(r["energy"]) for r in rows]
    positives = sum(labels)
    result = GateResult(status="BLOCKED", positives=positives)
    if positives < MIN_POSITIVES or len(rows) - positives < MIN_POSITIVES:
        result.reasons.append(
            f"need >= {MIN_POSITIVES} of each class; have {positives} failures, {len(rows) - positives} passes"
        )
        return result

    shuffled_labels = list(labels)
    for seed in seeds:
        result.real_folds[seed] = fold_aurocs(rows, labels, seed)
        permuted = list(shuffled_labels)
        random.Random(seed + 1000).shuffle(permuted)
        result.control_folds[seed] = fold_aurocs(rows, permuted, seed)

    real_all = [a for folds in result.real_folds.values() for a in folds]
    control_all = [a for folds in result.control_folds.values() for a in folds]
    if len(real_all) < DEFAULT_FOLDS * len(seeds) or not control_all:
        result.reasons.append(
            "some task-held-out folds had only one class; the gate cannot be evaluated"
        )
        return result

    result.worst_real = min(real_all)
    result.control_best = max(control_all)
    mean_control = sum(control_all) / len(control_all)
    result.control_spread = math.sqrt(
        sum((a - mean_control) ** 2 for a in control_all) / len(control_all)
    )

    if result.worst_real > result.control_best + result.control_spread:
        result.status = "PASS"
    else:
        result.reasons.append(
            f"worst real fold {result.worst_real:.3f} does not beat best control fold "
            f"{result.control_best:.3f} + spread {result.control_spread:.3f}"
        )
    return result
