"""Tests for anse.v2.origin_policy (card N-9) and its wiring in scripts/ltm_learning_mix.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from anse.v2.origin_policy import (
    NO_TRAIN_ORIGINS,
    REASON_MISSING_ORIGIN,
    allowed,
    partition,
    refusal_reason,
)

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "ltm_learning_mix.py"


@pytest.fixture
def gate(tmp_path: Path) -> Path:
    return tmp_path / "gates" / "N8.md"


# ── allowed / refusal_reason ─────────────────────────────────────────────────


@pytest.mark.parametrize("origin", sorted(NO_TRAIN_ORIGINS))
def test_transcript_origins_refused_without_gate_allowed_with_it(gate: Path, origin: str) -> None:
    row = {"origin": origin, "prompt": "p", "completion": "c"}
    assert not allowed(row, gate)
    assert refusal_reason(row, gate) == f"gated_origin:{origin}"
    gate.parent.mkdir(parents=True)
    gate.write_text("# N-8 gate\nverdict: transcript rows admitted\n")
    assert allowed(row, gate)
    assert refusal_reason(row, gate) is None


@pytest.mark.parametrize("row", [{}, {"origin": None}, {"origin": ""}, {"origin": 3}])
def test_missing_origin_refused_even_with_gate(gate: Path, row: dict) -> None:
    assert not allowed(row, gate)
    assert refusal_reason(row, gate) == REASON_MISSING_ORIGIN
    gate.parent.mkdir(parents=True)
    gate.write_text("gate")
    assert not allowed(row, gate)


def test_verified_sandbox_and_call_log_rows_allowed_without_gate(gate: Path) -> None:
    assert allowed({"origin": "sandbox", "verified": True, "verdict": True}, gate)
    assert allowed({"origin": "call_log", "verified": False}, gate)
    assert refusal_reason({"origin": "sandbox"}, gate) is None


def test_gated_set_is_exactly_the_three_transcript_origins() -> None:
    assert NO_TRAIN_ORIGINS == frozenset({"claude_code", "antigravity", "transcript"})
    assert "sandbox" not in NO_TRAIN_ORIGINS


@given(st.text(min_size=1).filter(lambda s: s not in NO_TRAIN_ORIGINS))
def test_any_other_nonempty_origin_is_allowed_regardless_of_gate(origin: str) -> None:
    missing = Path("/nonexistent/N8.md")
    assert allowed({"origin": origin}, missing)
    assert refusal_reason({"origin": origin}, missing) is None


# ── partition ────────────────────────────────────────────────────────────────


def test_partition_counts_by_reason_and_keeps_order(gate: Path) -> None:
    rows = [
        {"origin": "sandbox", "id": 1},
        {"origin": "transcript", "id": 2},
        {"id": 3},
        {"origin": "claude_code", "id": 4},
        {"origin": "call_log", "id": 5},
        {"origin": "transcript", "id": 6},
    ]
    kept, refused = partition(rows, gate)
    assert [r["id"] for r in kept] == [1, 5]
    assert refused == {"gated_origin:claude_code": 1, "gated_origin:transcript": 2,
                       REASON_MISSING_ORIGIN: 1}
    gate.parent.mkdir(parents=True)
    gate.write_text("gate")
    kept2, refused2 = partition(rows, gate)
    assert [r["id"] for r in kept2] == [1, 2, 4, 5, 6]
    assert refused2 == {REASON_MISSING_ORIGIN: 1}


# ── ltm_learning_mix.py wiring ───────────────────────────────────────────────


def _write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return path


def _run_mix(tmp_path: Path, gate: Path, dry_run: bool = False) -> dict:
    episodes = _write_jsonl(tmp_path / "harvest.jsonl", [
        {"task": f"t{i}", "prompt": f"p{i}", "code": f"c{i}", "converged": i % 2 == 0}
        for i in range(3)
    ])
    transcript = _write_jsonl(tmp_path / "redis_ltm_lora_dataset.jsonl", [
        {"prompt": f"q{i}", "response": f"r{i}"} for i in range(4)
    ])
    call_logs = tmp_path / "call_logs"
    call_logs.mkdir()
    out = tmp_path / "mix.jsonl"
    cmd = [sys.executable, str(SCRIPT), "--episodes", str(episodes), "--transcript", str(transcript),
           "--call-logs", str(call_logs), "--gate-file", str(gate), "--out", str(out), "--seed", "1"]
    if dry_run:
        cmd.append("--dry-run")
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    report = json.loads(proc.stdout)
    report["_out"] = out
    return report


def test_mix_refuses_transcript_rows_until_gate_exists(tmp_path: Path, gate: Path) -> None:
    report = _run_mix(tmp_path, gate)
    assert report["refused"]["total"] == 4
    assert report["refused"]["by_reason"] == {"gated_origin:transcript": 4}
    assert report["refused"]["by_pool"] == {"verified": 0, "new": 4}
    assert report["refused"]["gate_present"] is False
    assert report["new_pool_available"] == 0
    assert report["new_rows_taken"] == 0
    assert report["rows"] == 3
    written = [json.loads(line) for line in report["_out"].read_text().splitlines()]
    assert {r["origin"] for r in written} == {"sandbox"}
    assert all(r["verified"] for r in written)


def test_mix_admits_transcript_rows_with_gate_and_keeps_dilution_cap(tmp_path: Path, gate: Path) -> None:
    gate.parent.mkdir(parents=True)
    gate.write_text("# N-8\n")
    report = _run_mix(tmp_path, gate)
    assert report["refused"]["total"] == 0
    assert report["refused"]["gate_present"] is True
    assert report["new_pool_available"] == 4
    # 3 verified rows at a 0.3 cap admit int(3 * 0.3 / 0.7) == 1 new row.
    assert report["new_rows_taken"] == 1
    assert report["effective_dilution"] <= report["dilution_cap"]
    written = [json.loads(line) for line in report["_out"].read_text().splitlines()]
    transcript_rows = [r for r in written if r["origin"] == "transcript"]
    assert len(transcript_rows) == 1
    assert transcript_rows[0]["source"].endswith("redis_ltm_lora_dataset.jsonl")
    assert transcript_rows[0]["verified"] is False


def test_mix_dry_run_reports_but_writes_nothing(tmp_path: Path, gate: Path) -> None:
    report = _run_mix(tmp_path, gate, dry_run=True)
    assert report["written"] is None
    assert report["refused"]["total"] == 4
    assert not report["_out"].exists()
