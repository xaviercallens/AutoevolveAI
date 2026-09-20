"""
Tests for Claude Workflow Engine and Context Pruner.
Enforces subtask state machine transitions, context offloading, and anti-stub verification.
"""

from __future__ import annotations

import json
from pathlib import Path

from claude_workflow import Subtask, WorkflowState, verify_subtask
from context_manager import SCRATCHPAD_DIR, truncate_and_offload_context


def test_context_manager_small_payload():
    small_text = "line 1\nline 2\nline 3"
    result = truncate_and_offload_context("unit_test", small_text)
    assert result == small_text
    assert "TOOL OUTPUT TRUNCATED" not in result


def test_context_manager_large_payload_offload(tmp_path: Path):
    lines = [f"Trace statement line {i}" for i in range(100)]
    large_text = "\n".join(lines)
    result = truncate_and_offload_context("heavy_tool", large_text)

    assert "TOOL OUTPUT TRUNCATED - 100 lines total" in result
    assert "--- HEAD (First 25 lines) ---" in result
    assert "--- TAIL (Last 25 lines) ---" in result
    assert "Trace statement line 0" in result
    assert "Trace statement line 99" in result

    # Verify scratchpad log was generated
    scratch_files = list(SCRATCHPAD_DIR.glob("heavy_tool_*.log"))
    assert len(scratch_files) > 0
    assert any(f.read_text(encoding="utf-8") == large_text for f in scratch_files)


def test_workflow_state_lifecycle(tmp_path: Path, monkeypatch):
    test_state_file = tmp_path / ".test_workflow_state.json"
    monkeypatch.setattr(WorkflowState, "STATE_FILE", test_state_file)

    state = WorkflowState(plan_goal="Test Goal")
    subtask1 = Subtask(
        id="TASK-01",
        title="First Step",
        target_files=[],
        acceptance_command='python -c "import sys; sys.exit(0)"',
    )
    subtask2 = Subtask(
        id="TASK-02",
        title="Second Step",
        target_files=[],
        acceptance_command='python -c "import sys; sys.exit(0)"',
    )
    state.subtasks = [subtask1, subtask2]
    state.save()

    # Verify persistence
    assert test_state_file.exists()
    saved_data = json.loads(test_state_file.read_text(encoding="utf-8"))
    assert saved_data["goal"] == "Test Goal"
    assert len(saved_data["subtasks"]) == 2

    # Verify state transitions
    active = state.get_active_subtask()
    assert active is not None
    assert active.id == "TASK-01"

    state.mark_completed("TASK-01")
    next_active = state.get_active_subtask()
    assert next_active is not None
    assert next_active.id == "TASK-02"

    state.mark_completed("TASK-02")
    assert state.get_active_subtask() is None


def test_verify_subtask_detects_naked_stubs(tmp_path: Path):
    stub_file = tmp_path / "stubbed_module.py"
    stub_file.write_text("def hollow_func():\n    pass\n", encoding="utf-8")

    subtask = Subtask(
        id="TASK-STUB",
        title="Stubbed Task",
        target_files=[str(stub_file)],
        acceptance_command='python -c "import sys; sys.exit(0)"',
    )

    passed, error_msg = verify_subtask(subtask)
    assert not passed
    assert "Anti-Stub Gate Failed" in error_msg
    assert "contains naked stubs" in error_msg


def test_verify_subtask_clean_execution(tmp_path: Path):
    clean_file = tmp_path / "clean_module.py"
    clean_file.write_text("def real_func() -> int:\n    return 42\n", encoding="utf-8")

    subtask = Subtask(
        id="TASK-CLEAN",
        title="Clean Task",
        target_files=[str(clean_file)],
        acceptance_command='python -c "import sys; sys.exit(0)"',
    )

    passed, message = verify_subtask(subtask)
    assert passed
    assert "All acceptance checks passed cleanly" in message
