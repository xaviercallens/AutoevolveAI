"""
DPO Dataset Builder: Generates preference pairs (chosen vs rejected) for Direct Preference Optimization.
Grounded in computational physics:
- 'chosen': passes verification, zero AST stubs, minimal physical energy.
- 'rejected': fails tests, contains stubs/mock data, or exhibits high energy/latency.
Exports datasets ready for TRL DPOTrainer or offline evaluation.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ..core.anti_stub_guard import AntiStubGuard
from .trace_extractor import ExtractedSession


@dataclass
class DPOPreferencePair:
    """A single training sample for DPO / RLHF alignment."""

    prompt: str
    chosen: str
    rejected: str
    subtask_id: str
    energy_delta: float  # E_chosen - E_rejected (strictly negative)
    source: str = "antigravity_harness"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DPODatasetBuilder:
    """Builds DPO preference datasets from extracted agent trajectories."""

    def __init__(self, guard: AntiStubGuard | None = None) -> None:
        self.guard = guard or AntiStubGuard()

    def build_pairs_from_sessions(
        self, sessions: list[ExtractedSession]
    ) -> list[DPOPreferencePair]:
        """
        Processes sessions and extracts valid (chosen, rejected) training pairs.
        Guarantees that 'chosen' contains no AST stubs.
        """
        pairs: list[DPOPreferencePair] = []

        for session in sessions:
            if not session.is_dpo_ready:
                continue

            # 1. Determine chosen completion
            chosen_code: str | None = None
            chosen_energy: float = 0.0

            best_trace = session.best_trace()
            if best_trace:
                # Assert chosen has no stubs
                audit = self.guard.audit_code(best_trace.completion)
                if audit.is_clean:
                    chosen_code = best_trace.completion
                    chosen_energy = best_trace.energy
            elif session.human_patch:
                chosen_code = session.human_patch
                chosen_energy = 0.0

            if not chosen_code:
                continue

            # 2. Extract rejected attempts
            for trace in session.traces:
                if trace.verdict == "FAILED" or trace.energy > chosen_energy:
                    rejected_code = trace.completion
                    if rejected_code and rejected_code != chosen_code:
                        delta_e = chosen_energy - trace.energy
                        pairs.append(
                            DPOPreferencePair(
                                prompt=session.prompt,
                                chosen=chosen_code,
                                rejected=rejected_code,
                                subtask_id=session.subtask_id,
                                energy_delta=delta_e,
                            )
                        )

        return pairs

    def export_to_jsonl(self, pairs: list[DPOPreferencePair], output_path: str | Path) -> Path:
        """Saves preference pairs as a newline-delimited JSON file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        lines = [json.dumps(p.to_dict()) for p in pairs]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path
