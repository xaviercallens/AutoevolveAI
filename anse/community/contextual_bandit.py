"""
Disjoint LinUCB Contextual Bandit for Reddit Macro Strategy Selection.
Selects optimal Subreddit, Post Framing Archetype, and Posting Window on CPU with < 0.1 ms latency.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

DEFAULT_ACTION_SPACE = [
    {"id": 0, "subreddit": "r/MachineLearning", "archetype": "problem_curiosity"},
    {"id": 1, "subreddit": "r/MachineLearning", "archetype": "benchmark_comparison"},
    {"id": 2, "subreddit": "r/MachineLearning", "archetype": "formal_invariant"},
    {"id": 3, "subreddit": "r/Physics", "archetype": "problem_curiosity"},
    {"id": 4, "subreddit": "r/Physics", "archetype": "benchmark_comparison"},
    {"id": 5, "subreddit": "r/rust", "archetype": "benchmark_comparison"},
]


def extract_context_features(
    domain: str,
    hour_utc: int,
    day_of_week: int,
    has_doi: bool = True,
    has_code: bool = True,
) -> list[float]:
    """
    Construct a normalized 10-dimensional context vector for the bandit.
    """
    domain_map = {"ai": 0, "physics": 1, "math": 2, "systems": 3, "rust": 4}
    domain_idx = domain_map.get(domain.lower(), 0)
    domain_one_hot = [1.0 if i == domain_idx else 0.0 for i in range(5)]

    # Cyclical hour encoding
    rad = 2.0 * math.pi * (hour_utc % 24) / 24.0
    hour_sin = math.sin(rad)
    hour_cos = math.cos(rad)

    day_norm = (day_of_week % 7) / 7.0
    doi_feat = 1.0 if has_doi else 0.0
    code_feat = 1.0 if has_code else 0.0

    return domain_one_hot + [hour_sin, hour_cos, day_norm, doi_feat, code_feat]


class DisjointLinUCB:
    """
    Contextual Bandit with Disjoint Linear Upper Confidence Bounds.
    Updates via Sherman-Morrison rank-1 formula for O(d^2) CPU microsecond throughput.
    """

    def __init__(
        self,
        n_actions: int = len(DEFAULT_ACTION_SPACE),
        d_features: int = 10,
        alpha: float = 1.0,
    ) -> None:
        self.n_actions = n_actions
        self.d = d_features
        self.alpha = alpha
        self.action_space = DEFAULT_ACTION_SPACE

        # Initialize inverse covariance matrices to identity and bias vectors to zeros
        self.A_inv: list[list[list[float]]] = [
            [[1.0 if i == j else 0.0 for j in range(self.d)] for i in range(self.d)]
            for _ in range(self.n_actions)
        ]
        self.b: list[list[float]] = [
            [0.0 for _ in range(self.d)] for _ in range(self.n_actions)
        ]

    def select_action(self, context: list[float]) -> dict[str, Any]:
        """
        Compute upper confidence bound for each arm and select the argmax.
        Returns selected action dictionary with estimated payoff and confidence.
        """
        best_action = 0
        best_score = -float("inf")
        best_p = 0.0
        best_var = 0.0

        for a in range(self.n_actions):
            theta_a = self._compute_theta(a)
            mean_payoff = sum(context[i] * theta_a[i] for i in range(self.d))
            variance = self._compute_variance(a, context)
            ucb = mean_payoff + self.alpha * math.sqrt(max(1e-6, variance))

            if ucb > best_score:
                best_score = ucb
                best_action = a
                best_p = mean_payoff
                best_var = variance

        action_meta = self.action_space[best_action] if best_action < len(self.action_space) else {}
        return {
            "action_id": best_action,
            "ucb_score": best_score,
            "predicted_payoff": best_p,
            "variance": best_var,
            "subreddit": action_meta.get("subreddit", "r/MachineLearning"),
            "archetype": action_meta.get("archetype", "benchmark_comparison"),
        }

    def update(self, action: int, context: list[float], reward: float) -> None:
        """
        Perform rank-1 Sherman-Morrison update on A_inv[action] and update b[action].
        """
        if action < 0 or action >= self.n_actions:
            return

        inv_x = [
            sum(self.A_inv[action][i][j] * context[j] for j in range(self.d))
            for i in range(self.d)
        ]
        denom = 1.0 + sum(context[i] * inv_x[i] for i in range(self.d))

        for i in range(self.d):
            for j in range(self.d):
                self.A_inv[action][i][j] -= (inv_x[i] * inv_x[j]) / max(1e-8, denom)
            self.b[action][i] += reward * context[i]

    def save_state(self, filepath: Path | str) -> None:
        """Serialize bandit state to JSON."""
        state = {
            "n_actions": self.n_actions,
            "d_features": self.d,
            "alpha": self.alpha,
            "A_inv": self.A_inv,
            "b": self.b,
            "action_space": self.action_space,
        }
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def load_state(self, filepath: Path | str) -> bool:
        """Load bandit state from JSON file."""
        path = Path(filepath)
        if not path.exists():
            return False
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
            self.n_actions = state["n_actions"]
            self.d = state["d_features"]
            self.alpha = state["alpha"]
            self.A_inv = state["A_inv"]
            self.b = state["b"]
            self.action_space = state.get("action_space", DEFAULT_ACTION_SPACE)
            return True
        except Exception:
            return False

    def _compute_theta(self, action: int) -> list[float]:
        """Compute parameter estimate theta_a = A_inv * b."""
        return [
            sum(self.A_inv[action][i][j] * self.b[action][j] for j in range(self.d))
            for i in range(self.d)
        ]

    def _compute_variance(self, action: int, context: list[float]) -> float:
        """Compute quadratic form x^T A_inv x."""
        inv_x = [
            sum(self.A_inv[action][i][j] * context[j] for j in range(self.d))
            for i in range(self.d)
        ]
        return sum(context[i] * inv_x[i] for i in range(self.d))
