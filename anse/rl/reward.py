"""
anse.rl.reward — Differential Multi-Objective Reward Calculator for Kernel Parity.

Implements the ANSE-RL reward functional:
R_diff = (\u03b1 \u22c5 \u03a6_func) + (\u03b2 \u22c5 min(Ops_RunuX / Ops_Linux, 2.0)) - (\u03b3 \u22c5 E_ANSE) + B_target
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class RewardComponents:
    functional_reward: float
    performance_reward: float
    energy_penalty: float
    milestone_bonus: float
    total_reward: float
    phase: int
    passed_iso_80: bool
    passed_degradation_50: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "functional_reward": round(self.functional_reward, 3),
            "performance_reward": round(self.performance_reward, 3),
            "energy_penalty": round(self.energy_penalty, 3),
            "milestone_bonus": round(self.milestone_bonus, 3),
            "total_reward": round(self.total_reward, 3),
            "phase": self.phase,
            "passed_iso_80": self.passed_iso_80,
            "passed_degradation_50": self.passed_degradation_50,
        }


class DifferentialRewardCalculator:
    """
    Computes multi-objective differential reward signals across the 3 curriculum phases:
    - Phase 1: 80% Iso-Functionality Bootstrap (\u03b1 heavy, \u03b2 moderate)
    - Phase 2: 100% Parity Convergence (\u03a6_func hard constraint, \u03b2 heavy)
    - Phase 3: Transcendence (>100% Superhuman Supremacy, \u03b2 uncapped)
    """

    def __init__(self, phase: int = 1) -> None:
        self.phase = phase
        self._configure_weights()

    def _configure_weights(self) -> None:
        if self.phase == 1:
            self.alpha = 100.0
            self.beta = 10.0
            self.gamma = 0.001
            self.cap_ops_ratio = 2.0
            self.bonus_amount = 50.0
        elif self.phase == 2:
            self.alpha = 500.0
            self.beta = 50.0
            self.gamma = 0.001
            self.cap_ops_ratio = 3.0
            self.bonus_amount = 100.0
        else:  # Phase 3
            self.alpha = 500.0
            self.beta = 200.0
            self.gamma = 0.0005
            self.cap_ops_ratio = None  # Uncapped
            self.bonus_amount = 250.0

    def compute_reward(
        self,
        functional_parity: float,  # \u03a6_func in [0.0, 1.0]
        ops_ratio: float,           # Ops_RunuX / Ops_Linux
        energy_anse: float,        # E_ANSE = w_t * dt + w_m * RAM + Pi_penalty * phi
        failed_or_panicked: bool = False,
    ) -> RewardComponents:
        """
        Calculates the differential reward signal.
        """
        if failed_or_panicked:
            # Catastrophic failure penalty (-1000)
            return RewardComponents(
                functional_reward=-100.0,
                performance_reward=0.0,
                energy_penalty=-1000.0,
                milestone_bonus=0.0,
                total_reward=-1100.0,
                phase=self.phase,
                passed_iso_80=False,
                passed_degradation_50=False,
            )

        # 1. Functional component
        func_reward = self.alpha * functional_parity

        # 2. Performance component
        effective_ops = min(ops_ratio, self.cap_ops_ratio) if self.cap_ops_ratio else ops_ratio
        perf_reward = self.beta * effective_ops

        # 3. Energy penalty component
        energy_pen = self.gamma * energy_anse

        # 4. Milestone Gates
        passed_iso_80 = functional_parity >= 0.80
        # Degradation <= +50% is equivalent to ops_ratio >= 0.67
        passed_deg_50 = ops_ratio >= 0.67

        milestone_bonus = 0.0
        if passed_iso_80 and passed_deg_50:
            milestone_bonus = self.bonus_amount

        total_r = func_reward + perf_reward - energy_pen + milestone_bonus

        return RewardComponents(
            functional_reward=func_reward,
            performance_reward=perf_reward,
            energy_penalty=energy_pen,
            milestone_bonus=milestone_bonus,
            total_reward=total_r,
            phase=self.phase,
            passed_iso_80=passed_iso_80,
            passed_degradation_50=passed_deg_50,
        )
