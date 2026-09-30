"""Integration tests for scripts/manage_sub_project.py."""

import subprocess
import sys
from pathlib import Path
import pytest


def test_manage_sub_project_help():
    """Verify that manage_sub_project CLI shows help successfully."""
    cmd = [sys.executable, "scripts/manage_sub_project.py", "--help"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert "AutoevolveAI Sub-Project Manager" in res.stdout
    assert "gitclone" in res.stdout
    assert "audit" in res.stdout


def test_manage_sub_project_audit_path(tmp_path):
    """Verify manage_sub_project audit executes harness on a specific target path."""
    # Create a small valid python file
    sample_file = tmp_path / "valid_sample.py"
    sample_file.write_text(
        "def compute_energy(lat: float, mem: float) -> float:\n"
        "    \"\"\"Calculates physical energy metric.\"\"\"\n"
        "    return 0.5 * lat + 0.5 * mem\n"
    )

    cmd = [
        sys.executable,
        "-m",
        "antigravity_harness",
        "audit",
        str(sample_file),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert "Audit PASSED" in res.stdout
