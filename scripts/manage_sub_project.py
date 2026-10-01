#!/usr/bin/env python3
"""
Sub-Project Manager for AutoevolveAI.
Integrates with ANSE and the Antigravity Harness with zero-trust execution attestation.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SUB_PROJECTS_DIR = ROOT_DIR / "sub_projects"
TEMPLATE_DIR = SUB_PROJECTS_DIR / "TEMPLATE"

SAFE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]+$")


def validate_subproject_name(name: str) -> bool:
    """Ensures sub-project name is safe against path traversal and injection."""
    return bool(SAFE_NAME_PATTERN.match(name))


def run_command(cmd: list[str], cwd: Path | None = None) -> int:
    """Executes a sanitized command list."""
    print(f"==> Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd or ROOT_DIR, check=False)
    return result.returncode


def cmd_create(args: argparse.Namespace) -> int:
    name = args.name
    if not validate_subproject_name(name):
        print(f"❌ Invalid sub-project name '{name}'. Must match {SAFE_NAME_PATTERN.pattern}")
        return 1

    target_dir = SUB_PROJECTS_DIR / name

    if target_dir.exists():
        print(f"❌ Sub-project '{name}' already exists at {target_dir}")
        return 1

    print(f"==> Creating sub-project '{name}'...")
    shutil.copytree(TEMPLATE_DIR, target_dir)

    # Initialize basic python module structure
    (target_dir / "__init__.py").touch()

    print(f"✅ Sub-project '{name}' created at {target_dir}")
    print("   Contains 'formal/' directory for Lean 4 specifications.")
    print("   Contains '.pre-commit-config.yaml' for harness auditing.")
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    name = args.name
    if not validate_subproject_name(name):
        print(f"❌ Invalid sub-project name '{name}'.")
        return 1

    target_dir = SUB_PROJECTS_DIR / name
    if not target_dir.exists():
        print(f"❌ Sub-project '{name}' does not exist.")
        return 1

    print(f"==> Auditing sub-project '{name}' via Antigravity Harness...")
    cmd = [
        sys.executable,
        "-m",
        "antigravity_harness",
        "audit",
        str(target_dir),
    ]
    return run_command(cmd)


def cmd_attest(args: argparse.Namespace) -> int:
    name = args.name
    if not validate_subproject_name(name):
        print(f"❌ Invalid sub-project name '{name}'.")
        return 1

    target_dir = SUB_PROJECTS_DIR / name
    if not target_dir.exists():
        print(f"❌ Sub-project '{name}' does not exist.")
        return 1

    print(f"==> Attesting zero-trust execution for sub-project '{name}'...")
    cmd = [
        sys.executable,
        str(ROOT_DIR / "execution_attestation.py"),
    ]
    return run_command(cmd)


def cmd_verify(args: argparse.Namespace) -> int:
    name = args.name
    if not validate_subproject_name(name):
        print(f"❌ Invalid sub-project name '{name}'.")
        return 1

    target_dir = SUB_PROJECTS_DIR / name
    formal_dir = target_dir / "formal"

    if not formal_dir.exists():
        print(f"❌ Formal directory not found at {formal_dir}")
        return 1

    print(f"==> Verifying Lean 4 proofs for sub-project '{name}'...")
    cmd = [
        sys.executable,
        "-m",
        "antigravity_harness",
        "verify",
        "--formal-dir",
        str(formal_dir),
    ]
    return run_command(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="manage_sub_project",
        description="AutoevolveAI Sub-Project Manager integrating ANSE and Harness.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run", required=True)

    # create
    p_create = subparsers.add_parser("create", help="Scaffold a new sub-project")
    p_create.add_argument("name", help="Name of the sub-project")

    # audit
    p_audit = subparsers.add_parser("audit", help="Run harness audit on a sub-project")
    p_audit.add_argument("name", help="Name of the sub-project")

    # attest
    p_attest = subparsers.add_parser("attest", help="Run zero-trust execution attestation")
    p_attest.add_argument("name", help="Name of the sub-project")

    # verify
    p_verify = subparsers.add_parser("verify", help="Run Lean 4 verification on a sub-project")
    p_verify.add_argument("name", help="Name of the sub-project")

    args = parser.parse_args()

    if args.command == "create":
        return cmd_create(args)
    elif args.command == "audit":
        return cmd_audit(args)
    elif args.command == "attest":
        return cmd_attest(args)
    elif args.command == "verify":
        return cmd_verify(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
