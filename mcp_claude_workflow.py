#!/usr/bin/env python3
"""
FastMCP Server exposing Claude-style Subtask Decomposition and Verification.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from claude_workflow import TaskStatus, WorkflowState, verify_subtask
from context_manager import truncate_and_offload_context

mcp = FastMCP("claude-subtask-workflow")


@mcp.tool()
def plan_decompose_task(goal: str, subtasks: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Decompose the user's high-level request into an ordered sequence of verified subtasks.
    Each subtask MUST have a concrete acceptance command (e.g. pytest command).
    """
    created: list[dict[str, Any]] = []

    for i, item in enumerate(subtasks):
        st = {
            "id": f"TASK-{i + 1:02d}",
            "title": item["title"],
            "target_files": item.get("target_files", []),
            "acceptance_command": item["acceptance_command"],
            "status": TaskStatus.PENDING.value,
        }
        created.append(st)

    # Save to disk
    state_file = Path(".workflow_state.json")
    payload = json.dumps({"goal": goal, "subtasks": created}, indent=2)
    state_file.write_text(payload, encoding="utf-8")

    return {
        "success": True,
        "subtask_count": len(created),
        "tasks": created,
        "message": "Plan registered. Proceed to execute TASK-01 in an isolated subagent context.",
    }


@mcp.tool()
def get_current_subtask_context() -> dict[str, Any]:
    """
    Returns the current active subtask and only the minimal context needed for it.
    Prevents token bloat by excluding unrelated repository history.
    """
    state = WorkflowState()
    active = state.get_active_subtask()

    if not active:
        return {"active": False, "message": "All subtasks completed! Task workflow is finished."}

    # Gather target file contents with truncation
    files_context: dict[str, str] = {}
    for fpath in active.target_files:
        p = Path(fpath)
        if p.exists():
            files_context[fpath] = truncate_and_offload_context(
                p.name, p.read_text(encoding="utf-8")
            )
        else:
            files_context[fpath] = "[File does not exist yet - to be created]"

    return {
        "active": True,
        "subtask_id": active.id,
        "title": active.title,
        "status": active.status.value,
        "acceptance_command": active.acceptance_command,
        "last_error": active.last_error,
        "files": files_context,
    }


@mcp.tool()
def submit_subtask_for_verification(subtask_id: str) -> dict[str, Any]:
    """
    Submits the implementation for verification.
    Executes the deterministic acceptance test. Does NOT allow the model to self-certify.
    """
    state = WorkflowState()
    target = next((t for t in state.subtasks if t.id == subtask_id), None)

    if not target:
        return {"verified": False, "error": f"Subtask {subtask_id} not found."}

    passed, feedback = verify_subtask(target)

    if passed:
        state.mark_completed(subtask_id)
        next_task = state.get_active_subtask()
        return {
            "verified": True,
            "message": f"Subtask {subtask_id} successfully verified and closed.",
            "next_subtask": next_task.id if next_task else "NONE_COMPLETED",
        }

    target.retry_count += 1
    target.last_error = feedback
    if target.retry_count >= target.max_retries:
        target.status = TaskStatus.FAILED
    state.save()

    return {
        "verified": False,
        "error": "ACCEPTANCE_TEST_FAILED",
        "diagnostic": feedback,
        "retries_remaining": target.max_retries - target.retry_count,
        "instruction": (
            "Do not claim completion. Inspect the diagnostic failure above, "
            "adjust the code, and re-submit."
        ),
    }


if __name__ == "__main__":
    mcp.run()
