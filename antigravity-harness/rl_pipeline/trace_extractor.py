"""
Trace Extractor: Extracts and reconstructs agent execution trajectories from Redis or local files.
Aggregates multi-turn reasoning traces, attestation outcomes, energy metrics, and human patches.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from ..storage.redis_bus import RedisBus, TraceRecord


@dataclass
class ExtractedSession:
    """A full development session with prompt, candidate attempts, and outcomes."""

    subtask_id: str
    prompt: str
    traces: list[TraceRecord] = field(default_factory=list)
    human_patch: str | None = None

    @property
    def has_passed_trace(self) -> bool:
        return any(t.verdict == "PASSED" for t in self.traces)

    @property
    def has_failed_trace(self) -> bool:
        return any(t.verdict == "FAILED" for t in self.traces)

    @property
    def is_dpo_ready(self) -> bool:
        """Session has at least one passed (chosen) and one failed (rejected) trace, or a human patch."""
        return (self.has_passed_trace and self.has_failed_trace) or (
            self.human_patch is not None and self.has_failed_trace
        )

    def best_trace(self) -> TraceRecord | None:
        """Returns the passed trace with the lowest physical energy."""
        passed = [t for t in self.traces if t.verdict == "PASSED"]
        if not passed:
            return None
        return min(passed, key=lambda t: t.energy)

    def worst_trace(self) -> TraceRecord | None:
        """Returns the failed trace or the trace with the highest physical energy."""
        failed = [t for t in self.traces if t.verdict == "FAILED"]
        if failed:
            return max(failed, key=lambda t: t.energy)
        if self.traces:
            return max(self.traces, key=lambda t: t.energy)
        return None


class TraceExtractor:
    """Extracts, filters, and groups execution traces from RedisBus or JSONL files."""

    def __init__(self, bus: RedisBus | None = None) -> None:
        self.bus = bus or RedisBus(use_mock=True)

    def extract_from_bus(self) -> list[ExtractedSession]:
        """Queries Redis bus for all stored traces and aggregates them by subtask_id."""
        traces = self.bus.list_all_traces()
        grouped: dict[str, list[TraceRecord]] = {}

        for t in traces:
            grouped.setdefault(t.subtask_id, []).append(t)

        sessions: list[ExtractedSession] = []
        for subtask_id, trace_list in grouped.items():
            # Get common prompt
            prompt = trace_list[0].prompt if trace_list else ""
            # Check for human patch in traces
            patch = next((t.human_patch for t in trace_list if t.human_patch), None)

            # Sort traces chronologically
            sorted_traces = sorted(trace_list, key=lambda t: t.timestamp)
            sessions.append(
                ExtractedSession(
                    subtask_id=subtask_id,
                    prompt=prompt,
                    traces=sorted_traces,
                    human_patch=patch,
                )
            )

        return sessions

    def extract_from_jsonl(self, file_path: str | Path) -> list[ExtractedSession]:
        """Loads offline traces from a .jsonl file (such as evolution traces)."""
        path = Path(file_path)
        if not path.exists():
            return []

        grouped: dict[str, list[TraceRecord]] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                # Map various schema conventions to TraceRecord
                trace = TraceRecord(
                    trace_id=raw.get("trace_id", raw.get("id", "trace_0")),
                    subtask_id=raw.get("subtask_id", raw.get("task_id", "subtask_0")),
                    prompt=raw.get("prompt", raw.get("task", "")),
                    completion=raw.get("completion", raw.get("code", "")),
                    verdict="PASSED"
                    if raw.get("passed", raw.get("converged", False))
                    else "FAILED",
                    energy=float(raw.get("energy", raw.get("final_energy", 1000.0))),
                    reasons=raw.get("reasons", []),
                    human_patch=raw.get("human_patch"),
                )
                grouped.setdefault(trace.subtask_id, []).append(trace)
            except Exception:
                continue

        sessions: list[ExtractedSession] = []
        for subtask_id, trace_list in grouped.items():
            prompt = trace_list[0].prompt if trace_list else ""
            patch = next((t.human_patch for t in trace_list if t.human_patch), None)
            sessions.append(
                ExtractedSession(
                    subtask_id=subtask_id,
                    prompt=prompt,
                    traces=trace_list,
                    human_patch=patch,
                )
            )

        return sessions
