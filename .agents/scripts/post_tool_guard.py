#!/usr/bin/env python3
"""
Antigravity IDE v2 Post-Tool Hardening Hook
Runs AST anti-stub analysis on newly written or edited Python files.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from execution_attestation import ImplementationAuditor
except ImportError:
    ImplementationAuditor = None


def main() -> None:
    # Read payload from stdin as JSON
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    tool_call = payload.get("toolCall", {})
    args = tool_call.get("args", {})

    target_file = (
        args.get("TargetFile")
        or args.get("target_file")
        or args.get("path")
        or args.get("file_path")
    )

    if target_file and target_file.endswith(".py") and ImplementationAuditor:
        p = Path(target_file)
        if not p.is_absolute():
            p = PROJECT_ROOT / p

        if p.exists():
            try:
                tree = ast.parse(p.read_text(encoding="utf-8"), filename=p.name)
                auditor = ImplementationAuditor(p.name)
                auditor.visit(tree)
                if auditor.violations:
                    sys.stderr.write(
                        f"\n⚠️ [HARDENING GUARD VIOLATION] {p.name} contains forbidden stubs/mocks:\n"
                    )
                    for v in auditor.violations:
                        sys.stderr.write(f"   - {v}\n")
                    sys.stderr.write("   Refactor code to provide concrete production logic.\n")
            except Exception as e:
                sys.stderr.write(f"⚠️ [HARDENING GUARD] Parse check error: {e}\n")

    # PostToolUse contract requires JSON object on stdout
    sys.stdout.write(json.dumps({}))


if __name__ == "__main__":
    main()
