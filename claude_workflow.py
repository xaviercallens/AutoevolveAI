#!/usr/bin/env python3
"""
Claude Workflow Engine:
Enforces subtask decomposition, ephemeral context boundaries, and external verification.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import httpx


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Subtask:
    id: str
    title: str
    target_files: list[str]
    acceptance_command: str  # e.g., 'pytest tests/test_auth.py -k test_jwt_validation'
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    last_error: str | None = None


class WorkflowState:
    STATE_FILE = Path(".workflow_state.json")

    def __init__(self, plan_goal: str = ""):
        self.goal = plan_goal
        self.subtasks: list[Subtask] = []
        self._load()

    def _load(self) -> None:
        if not self.STATE_FILE.exists():
            return
        try:
            data = json.loads(self.STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return

        self.goal = data.get("goal", "")
        self.subtasks = [
            Subtask(
                id=t["id"],
                title=t["title"],
                target_files=t.get("target_files", []),
                acceptance_command=t["acceptance_command"],
                status=TaskStatus(t["status"]),
                retry_count=t.get("retry_count", 0),
                max_retries=t.get("max_retries", 3),
                last_error=t.get("last_error"),
            )
            for t in data.get("subtasks", [])
        ]

    def save(self) -> None:
        data = {
            "goal": self.goal,
            "subtasks": [asdict(t) for t in self.subtasks],
        }
        self.STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get_active_subtask(self) -> Subtask | None:
        for t in self.subtasks:
            if t.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.VERIFYING):
                return t
        return None

    def mark_completed(self, subtask_id: str) -> None:
        for t in self.subtasks:
            if t.id == subtask_id:
                t.status = TaskStatus.COMPLETED
                t.last_error = None
                self.save()
                return


def _has_suspicious_stub(content: str) -> bool:
    for marker in ("pass", "...", "NotImplementedError"):
        if marker in content:
            return True
    return False


def _has_naked_stub_lines(content: str) -> bool:
    if "def " not in content:
        return False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped in ("pass", "..."):
            return True
    return False


def _check_file_stubs(filepath: Path) -> tuple[bool, str]:
    """Inspects a Python file for obvious naked stubs."""
    if not filepath.exists() or filepath.suffix != ".py":
        return True, ""

    try:
        content = filepath.read_text(encoding="utf-8")
    except OSError as err:
        return False, f"Failed to read file '{filepath}': {err}"

    if not _has_suspicious_stub(content):
        return True, ""

    if _has_naked_stub_lines(content):
        return False, f"Anti-Stub Gate Failed: '{filepath}' contains naked stubs (pass/...)."

    return True, ""


def verify_subtask(subtask: Subtask) -> tuple[bool, str]:
    """Independent Black-Box Verification Gate."""
    print(f"\n [VERIFICATION GATE] Testing Subtask {subtask.id}: '{subtask.title}'")
    print(f"   Executing: {subtask.acceptance_command}")

    # 1. Audit target files for stubs
    for file_str in subtask.target_files:
        clean_path = Path(file_str)
        passed, err_msg = _check_file_stubs(clean_path)
        if not passed:
            return False, err_msg

    # 2. Run deterministic acceptance test command
    env = dict(os.environ)
    res = subprocess.run(  # nosec B602
        subtask.acceptance_command,
        shell=True,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    if res.returncode == 0:
        return True, "All acceptance checks passed cleanly."

    err_tail = (res.stderr or res.stdout)[-1500:]
    return False, f"Acceptance command failed (exit code {res.returncode}):\n{err_tail}"


def _send_gateway_phase_request(
    endpoint: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    timeout: float,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Helper to dispatch HTTP request to gateway with phase headers."""
    if client is not None:
        resp = client.post(endpoint, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    with httpx.Client(timeout=timeout) as managed_client:
        resp = managed_client.post(endpoint, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()


def run_planning_phase(
    goal: str,
    gateway_url: str = "http://localhost:8080",
    timeout: float = 30.0,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Execute Planning Phase by dispatching to gateway with X-Task-Phase: PLANNING."""
    endpoint = f"{gateway_url.rstrip('/')}/v1beta/models/gemini-3.1-pro:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-Task-Phase": "PLANNING",
    }
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            f"You are the Architecture & Planning Engine (Gemini 3.1 Pro). "
                            f"Decompose the following goal into verified subtasks with concrete "
                            f"acceptance commands:\n\n{goal}"
                        )
                    }
                ],
            }
        ]
    }
    data = _send_gateway_phase_request(endpoint, headers, payload, timeout, client)
    return {
        "phase": "PLANNING",
        "goal": goal,
        "raw_response": data,
        "success": True,
    }


def run_execution_phase(
    subtask_id: str,
    prompt: str,
    gateway_url: str = "http://localhost:8080",
    timeout: float = 60.0,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Execute Implementation Phase by dispatching to gateway with X-Task-Phase: EXECUTION."""
    endpoint = f"{gateway_url.rstrip('/')}/v1beta/models/gemini-3.8-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-Task-Phase": "EXECUTION",
        "X-Subtask-ID": subtask_id,
    }
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ]
    }
    data = _send_gateway_phase_request(endpoint, headers, payload, timeout, client)
    return {
        "phase": "EXECUTION",
        "subtask_id": subtask_id,
        "raw_response": data,
        "success": True,
    }


def run_verification_phase(
    subtask: Subtask,
    gateway_url: str = "http://localhost:8080",
    timeout: float = 30.0,
    client: httpx.Client | None = None,
) -> tuple[bool, str]:
    """Execute Verification Phase by auditing code and executing deterministic acceptance test."""
    passed, message = verify_subtask(subtask)

    endpoint = f"{gateway_url.rstrip('/')}/v1beta/models/gemini-3.1-pro:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-Task-Phase": "VERIFICATION",
        "X-Subtask-ID": subtask.id,
    }
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            f"Audit verification verdict for subtask {subtask.id} "
                            f"('{subtask.title}'):\n"
                            f"Outcome: {'PASSED' if passed else 'FAILED'}\n"
                            f"Diagnostic: {message}"
                        )
                    }
                ],
            }
        ]
    }
    try:
        _send_gateway_phase_request(endpoint, headers, payload, timeout, client)
    except Exception:
        pass

    return passed, message


__all__ = [
    "Subtask",
    "TaskStatus",
    "WorkflowState",
    "verify_subtask",
    "run_planning_phase",
    "run_execution_phase",
    "run_verification_phase",
]
