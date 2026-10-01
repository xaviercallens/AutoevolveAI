"""
anse/laya/integration.py
========================
LayaANSEDispatcher — integrates Laya as a System 1 pre-filter for ANSE.

Maps LayaDecision outputs to ANSE actions:
  noul < 0.3  → BLOCK with E=1e6 barrier penalty
  choice       → dispatch to ANSE specialist role
  score        → provide energy estimate to optimizer

Integrates with anse/decision/kev_engine.py via the KevAction protocol.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ANSERole(str, Enum):
    """ANSE specialist roles that Laya can route to."""
    GENERAL = "general"
    ALGORITHMIC_PERFORMANCE = "algorithmic_performance"
    COMPUTATIONAL_PHYSICIST = "computational_physicist"
    LEAN_PROVER = "lean_prover"
    MICRO_ML_ARCHITECT = "micro_ml_architect"
    SECURITY_AUDITOR = "security_auditor"
    REFACTORING_SPECIALIST = "refactoring_specialist"


# Map from Laya choice labels → ANSE roles
CHOICE_TO_ROLE: dict[str, ANSERole] = {
    # Security
    "vulnerable": ANSERole.SECURITY_AUDITOR,
    "safe": ANSERole.GENERAL,
    "security_auditor": ANSERole.SECURITY_AUDITOR,
    # Anti-stub
    "stub_ellipsis": ANSERole.REFACTORING_SPECIALIST,
    "dead_code": ANSERole.REFACTORING_SPECIALIST,
    "smelly": ANSERole.REFACTORING_SPECIALIST,
    "clean": ANSERole.GENERAL,
    "refactoring_specialist": ANSERole.REFACTORING_SPECIALIST,
    # Energy / performance
    "O(N2)": ANSERole.ALGORITHMIC_PERFORMANCE,
    "O(exponential)": ANSERole.ALGORITHMIC_PERFORMANCE,
    "vectorization": ANSERole.ALGORITHMIC_PERFORMANCE,
    "zero_alloc": ANSERole.ALGORITHMIC_PERFORMANCE,
    "algorithmic_performance": ANSERole.ALGORITHMIC_PERFORMANCE,
    "high_energy": ANSERole.ALGORITHMIC_PERFORMANCE,
    # Lean 4
    "omega": ANSERole.LEAN_PROVER,
    "linarith": ANSERole.LEAN_PROVER,
    "ring": ANSERole.LEAN_PROVER,
    "norm_num": ANSERole.LEAN_PROVER,
    "positivity": ANSERole.LEAN_PROVER,
    "simp": ANSERole.LEAN_PROVER,
    "calc": ANSERole.LEAN_PROVER,
    "induction": ANSERole.LEAN_PROVER,
    "lean_prover": ANSERole.LEAN_PROVER,
    # ML
    "micro_ml_architect": ANSERole.MICRO_ML_ARCHITECT,
    # Physics
    "computational_physicist": ANSERole.COMPUTATIONAL_PHYSICIST,
}


@dataclass
class ANSEAction:
    """The action ANSE should take based on Laya's decision."""
    blocked: bool                    # True if noul gate fires (E=1e6)
    role: ANSERole                   # Specialist role to dispatch to
    energy: float                    # ANSE energy E = score + barrier
    lean4_tactic: str | None         # Recommended Lean 4 tactic (if role=lean_prover)
    reasoning: str                   # Human-readable explanation
    raw_decision: Any                # The original LayaDecision


class LayaANSEDispatcher:
    """
    Integrates Laya Coding Companion with the ANSE orchestration pipeline.

    Usage:
        dispatcher = LayaANSEDispatcher(checkpoint_path="...")
        action = dispatcher.dispatch("def foo(): pass")
        if action.blocked:
            raise ANSEBarrierException(E=1e6)
        else:
            route_to_specialist(action.role)
    """

    # Lean 4 tactic choices (from stage 3 training)
    LEAN4_TACTICS = {
        "omega", "linarith", "ring", "norm_num", "positivity",
        "rfl", "simp", "calc", "induction", "intro", "apply",
        "exact", "constructor", "cases", "rcases",
    }

    def __init__(
        self,
        checkpoint_path: str | None = None,
        noul_threshold: float = 0.3,
        energy_weight_t: float = 1.0,
        energy_weight_m: float = 0.01,
    ) -> None:
        from anse.laya.inference import LayaInference
        self.engine = LayaInference(
            checkpoint_path=checkpoint_path,
            device="cpu",
        )
        self.noul_threshold = noul_threshold
        self.energy_weight_t = energy_weight_t
        self.energy_weight_m = energy_weight_m

    def dispatch(self, code_or_prompt: str) -> ANSEAction:
        """
        Evaluate a code snippet/prompt and return the ANSE action.

        Invariant: if noul < threshold, action.energy = 1e6 (barrier penalty).
        """
        decision = self.engine.predict(code_or_prompt)

        blocked = decision.is_blocked(self.noul_threshold)
        energy = 1e6 if blocked else decision.anse_energy(
            self.energy_weight_t, self.energy_weight_m
        )

        # Map choice to ANSE role
        role = CHOICE_TO_ROLE.get(decision.choice, ANSERole.GENERAL)

        # Lean 4 tactic recommendation
        lean4_tactic = decision.choice if decision.choice in self.LEAN4_TACTICS else None

        # Generate reasoning string
        if blocked:
            reasoning = (
                f"BLOCKED: noul={decision.noul:.3f} < {self.noul_threshold} "
                f"(stub/vulnerability/test_fail detected). E=1e6 barrier applied."
            )
        else:
            reasoning = (
                f"PASS: noul={decision.noul:.3f}, "
                f"route={role.value}, "
                f"energy={energy:.3f}, "
                f"latency={decision.latency_ms:.1f}ms"
            )
            if lean4_tactic:
                reasoning += f", lean4_tactic={lean4_tactic}"

        return ANSEAction(
            blocked=blocked,
            role=role,
            energy=energy,
            lean4_tactic=lean4_tactic,
            reasoning=reasoning,
            raw_decision=decision,
        )

    def dispatch_batch(self, inputs: list[str]) -> list[ANSEAction]:
        """Dispatch a batch of code snippets."""
        return [self.dispatch(text) for text in inputs]

    def benchmark(self) -> dict:
        """Run inference benchmark and return latency stats."""
        return self.engine.benchmark()
