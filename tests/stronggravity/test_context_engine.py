from __future__ import annotations

import claude_workflow
import context_manager
from claude_workflow import Subtask, TaskStatus, WorkflowState
from context_manager import (
    HEAD_TAIL_SIZE,
    MAX_INLINE_LINES,
    truncate_and_offload_context,
)


class TestContextEngine:
    """Validates ephemeral context pruning (Lean: ephemeralContext)."""

    def test_short_output_returned_directly(self):
        output = "a\nb\nc"
        result = truncate_and_offload_context("task_1", output)
        assert result == output

    def test_long_output_truncated(self):
        lines = [f"line {i}" for i in range(MAX_INLINE_LINES + 50)]
        output = "\n".join(lines)
        result = truncate_and_offload_context("task_1", output)
        assert "[TOOL OUTPUT TRUNCATED" in result
        assert len(result.splitlines()) < len(lines)

    def test_truncated_output_preserves_head(self):
        lines = [f"line {i}" for i in range(MAX_INLINE_LINES + 50)]
        output = "\n".join(lines)
        result = truncate_and_offload_context("task_1", output)
        for i in range(HEAD_TAIL_SIZE):
            assert lines[i] in result

    def test_truncated_output_preserves_tail(self):
        lines = [f"line {i}" for i in range(MAX_INLINE_LINES + 50)]
        output = "\n".join(lines)
        result = truncate_and_offload_context("task_1", output)
        for i in range(1, HEAD_TAIL_SIZE + 1):
            assert lines[-i] in result

    def test_truncated_output_removes_middle(self):
        lines = [f"line {i}" for i in range(MAX_INLINE_LINES + 50)]
        output = "\n".join(lines)
        result = truncate_and_offload_context("task_1", output)
        middle_idx = len(lines) // 2
        middle_line = lines[middle_idx]
        assert middle_line not in result

    def test_scratchpad_file_created(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            context_manager, "SCRATCHPAD_DIR", tmp_path
        )
        lines = [f"line {i}" for i in range(MAX_INLINE_LINES + 50)]
        output = "\n".join(lines)
        truncate_and_offload_context("task_1", output)
        files = list(tmp_path.glob("*"))
        assert len(files) > 0


class TestWorkflowStateMachine:
    """Validates state transitions (Lean: zeroTrustCompletion)."""

    def test_save_load_roundtrip(self, tmp_path, monkeypatch):
        state_file = tmp_path / ".workflow_state.json"
        monkeypatch.setattr(
            claude_workflow.WorkflowState, "STATE_FILE", state_file
        )
        state = WorkflowState()
        state.subtasks.append(
            Subtask(
                id="1",
                title="Test",
                target_files=[],
                acceptance_command="pytest",
                status=TaskStatus.PENDING,
            )
        )
        state.save()
        new_state = WorkflowState()
        assert len(new_state.subtasks) == 1
        assert new_state.subtasks[0].id == "1"

    def test_get_active_subtask_returns_pending(
        self, tmp_path, monkeypatch
    ):
        state_file = tmp_path / ".workflow_state.json"
        monkeypatch.setattr(
            claude_workflow.WorkflowState, "STATE_FILE", state_file
        )
        state = WorkflowState()
        state.subtasks.append(
            Subtask(
                id="1",
                title="Test",
                target_files=[],
                acceptance_command="pytest",
                status=TaskStatus.PENDING,
            )
        )
        active = state.get_active_subtask()
        assert active is not None
        assert active.id == "1"

    def test_completed_task_skipped(self, tmp_path, monkeypatch):
        state_file = tmp_path / ".workflow_state.json"
        monkeypatch.setattr(
            claude_workflow.WorkflowState, "STATE_FILE", state_file
        )
        state = WorkflowState()
        state.subtasks.append(
            Subtask(
                id="1",
                title="Done",
                target_files=[],
                acceptance_command="pytest",
                status=TaskStatus.COMPLETED,
            )
        )
        state.subtasks.append(
            Subtask(
                id="2",
                title="Next",
                target_files=[],
                acceptance_command="pytest",
                status=TaskStatus.PENDING,
            )
        )
        active = state.get_active_subtask()
        assert active is not None
        assert active.id == "2"

    def test_task_status_enum_values(self):
        assert hasattr(TaskStatus, "PENDING")
        assert hasattr(TaskStatus, "IN_PROGRESS")
        assert hasattr(TaskStatus, "VERIFYING")
        assert hasattr(TaskStatus, "COMPLETED")
        assert hasattr(TaskStatus, "FAILED")
