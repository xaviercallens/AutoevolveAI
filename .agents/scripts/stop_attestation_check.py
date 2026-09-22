#!/usr/bin/env python3
"""
Antigravity IDE v2 Stop Hardening Hook
Guards the completion phase against incomplete background work, active tasks, or unverified stubs.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    # Check 1: Ensure background tasks are idle
    if payload.get("fullyIdle") is False:
        sys.stdout.write(
            json.dumps(
                {
                    "decision": "continue",
                    "reason": "Hardening Gate: Background test or verification tasks are still active. Await completion.",
                }
            )
        )
        return

    # Check 2: Quick git diff audit for anti-simulation markers in modified files
    try:
        proc = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            modified = [f for f in proc.stdout.strip().splitlines() if f.endswith(".py")]
            if modified:
                # Fast audit via execution_attestation if present
                audit_cmd = [
                    sys.executable,
                    str(PROJECT_ROOT / "execution_attestation.py"),
                ]
                audit_run = subprocess.run(
                    audit_cmd,
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if audit_run.returncode != 0:
                    sys.stdout.write(
                        json.dumps(
                            {
                                "decision": "continue",
                                "reason": f"Hardening Gate: Anti-Stub violation detected in modified files:\n{audit_run.stdout[:400]}",
                            }
                        )
                    )
                    return
    except Exception:
        pass

    # All checks passed
    sys.stdout.write(json.dumps({"decision": ""}))


if __name__ == "__main__":
    main()
